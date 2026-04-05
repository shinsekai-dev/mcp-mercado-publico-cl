"""CLI para el scraper de Mercado Público."""

import asyncio
import sys
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from .browser import MPBrowser
from .parser import DocumentParser
from .storage import LicitacionStorage
from .config import get_download_dir

app = typer.Typer(help="Scraper de documentos de licitaciones de Mercado Público Chile")
console = Console()


@app.command()
def login(
    url: str = typer.Option("https://www.mercadopublico.cl", help="URL inicial del portal"),
):
    """
    Abre el portal en modo visible para hacer login manual y guardar las cookies.

    Después de este comando, el scraper puede correr en modo headless
    sin necesidad de login interactivo.
    """
    import asyncio
    from .auth import save_cookies, get_cookies_path

    async def _login():
        from playwright.async_api import async_playwright

        cookies_path = get_cookies_path()

        console.print("\n[bold blue]MODO LOGIN - Guardando sesión[/bold blue]")
        console.print("=" * 60)
        console.print(f"[yellow]1. Se abrirá el navegador en: {url}[/yellow]")
        console.print(f"[yellow]2. Hacé login con tu usuario y contraseña[/yellow]")
        console.print(f"[yellow]3. Presioná ENTER en esta terminal cuando estés logueado[/yellow]")
        console.print("=" * 60 + "\n")

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=False)
            context = await browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                viewport={"width": 1920, "height": 1080},
            )
            page = await context.new_page()
            await page.goto(url, wait_until="networkidle")

            import concurrent.futures
            loop = asyncio.get_event_loop()
            def wait_enter():
                input("\n[Presioná ENTER cuando hayas hecho login...] ")
                return True
            with concurrent.futures.ThreadPoolExecutor() as pool:
                await loop.run_in_executor(pool, wait_enter)

            saved_path = await save_cookies(context, cookies_path)
            await browser.close()

        console.print(f"\n[green][OK] Cookies guardadas en: {saved_path}[/green]")
        console.print(f"[dim]El scraper usará esta sesión automáticamente.[/dim]")

    asyncio.run(_login())


@app.command()
def descargar(
    codigo: str = typer.Argument(
        ..., help="Código de la licitación (ej: 1005498-5-LE26)"
    ),
    output: Optional[Path] = typer.Option(
        None, "--output", "-o", help="Directorio de salida"
    ),
    headless: bool = typer.Option(
        True, "--headless/--no-headless", help="Ejecutar navegador en modo headless"
    ),
    max_concurrent: int = typer.Option(
        3, "--max-concurrent", "-c", help="Máximo de descargas simultáneas"
    ),
):
    """
    Descarga todos los documentos anexos de una licitación.
    """

    async def _descargar():
        console.print(
            Panel.fit(
                f"[bold blue]Scraper Mercado Público[/bold blue]\n[cyan]Código: {codigo}[/cyan]"
            )
        )

        # Inicializar componentes
        storage = LicitacionStorage(output)

        async with MPBrowser(headless=headless) as browser:
            # Buscar licitación
            ficha_url = await browser.buscar_licitacion(codigo)

            if not ficha_url:
                console.print("[red][ERROR] No se pudo encontrar la licitación[/red]")
                raise typer.Exit(1)

            # Extraer links de documentos
            documentos = await browser.extraer_links_documentos()

            if not documentos:
                console.print(
                    "[yellow][WARN] No se encontraron documentos anexos[/yellow]"
                )
                raise typer.Exit(0)

            # Guardar metadata
            storage.save_metadata(
                codigo,
                {
                    "ficha_url": ficha_url,
                    "total_documentos": len(documentos),
                    "documentos": documentos,
                },
            )

            # Descargar documentos usando la sesion del browser (preserva cookies ASP.NET)
            doc_dir = storage.get_documentos_dir(codigo)
            descargados = await browser.descargar_documentos_con_sesion(
                documentos, doc_dir, max_concurrent
            )

            # Mostrar resumen
            table = Table(title="Resumen de Descarga")
            table.add_column("Métrica", style="cyan")
            table.add_column("Valor", style="green")
            table.add_row("Documentos encontrados", str(len(documentos)))
            table.add_row("Documentos descargados", str(len(descargados)))
            table.add_row("Directorio", str(storage.get_licitacion_dir(codigo)))
            console.print(table)

            # Parsear documentos
            console.print("\n[blue][DOC] Extrayendo texto de documentos...[/blue]")
            texto_completo = DocumentParser.parse_directory(doc_dir)

            # Guardar resumen
            storage.save_resumen(codigo, texto_completo)

            # Crear template de oferta
            storage.create_template_oferta(codigo)

            console.print(f"\n[green][OK] Proceso completado exitosamente![/green]")
            console.print(
                f"[dim]Archivos guardados en: {storage.get_licitacion_dir(codigo)}[/dim]"
            )

    asyncio.run(_descargar())


@app.command()
def descargar_url(
    url: str = typer.Argument(..., help="URL directa de la ficha de licitación"),
    codigo: str = typer.Argument(
        ..., help="Código de la licitación para nombrar archivos"
    ),
    output: Optional[Path] = typer.Option(
        None, "--output", "-o", help="Directorio de salida"
    ),
    headless: bool = typer.Option(
        True, "--headless/--no-headless", help="Ejecutar navegador en modo headless"
    ),
    max_concurrent: int = typer.Option(
        3, "--max-concurrent", "-c", help="Máximo de descargas simultáneas"
    ),
):
    """
    Descarga documentos usando URL directa de la ficha.

    Útil cuando el portal tiene protección anti-bot.
    Obtén la URL manualmente desde el navegador y pásala aquí.
    """

    async def _descargar_url():
        console.print(
            Panel.fit(
                f"[bold blue]Scraper Mercado Público[/bold blue]\n[cyan]URL: {url[:60]}...[/cyan]\n[cyan]Código: {codigo}[/cyan]"
            )
        )

        # Inicializar componentes
        storage = LicitacionStorage(output)

        async with MPBrowser(headless=headless) as browser:
            # Cargar ficha directamente desde URL
            success = await browser.cargar_ficha_por_url(url)

            if not success:
                console.print(
                    "[red][ERROR] No se pudo cargar la ficha desde la URL[/red]"
                )
                raise typer.Exit(1)

            # Extraer links de documentos
            documentos = await browser.extraer_links_documentos()

            if not documentos:
                console.print(
                    "[yellow][WARN] No se encontraron documentos anexos[/yellow]"
                )
                raise typer.Exit(0)

            # Guardar metadata
            storage.save_metadata(
                codigo,
                {
                    "ficha_url": url,
                    "total_documentos": len(documentos),
                    "documentos": documentos,
                },
            )

            # Descargar documentos usando la sesion del browser (preserva cookies ASP.NET)
            doc_dir = storage.get_documentos_dir(codigo)
            descargados = await browser.descargar_documentos_con_sesion(
                documentos, doc_dir, max_concurrent
            )

            # Mostrar resumen
            table = Table(title="Resumen de Descarga")
            table.add_column("Métrica", style="cyan")
            table.add_column("Valor", style="green")
            table.add_row("Documentos encontrados", str(len(documentos)))
            table.add_row("Documentos descargados", str(len(descargados)))
            table.add_row("Directorio", str(storage.get_licitacion_dir(codigo)))
            console.print(table)

            # Parsear documentos
            console.print("\n[blue][DOC] Extrayendo texto de documentos...[/blue]")
            texto_completo = DocumentParser.parse_directory(doc_dir)

            # Guardar resumen
            storage.save_resumen(codigo, texto_completo)

            # Crear template de oferta
            storage.create_template_oferta(codigo)

            console.print(f"\n[green][OK] Proceso completado exitosamente![/green]")
            console.print(
                f"[dim]Archivos guardados en: {storage.get_licitacion_dir(codigo)}[/dim]"
            )

    asyncio.run(_descargar_url())


@app.command()
def descargar_con_login(
    codigo: str = typer.Argument(
        ..., help="Código de la licitación para nombrar archivos"
    ),
    output: Optional[Path] = typer.Option(
        None, "--output", "-o", help="Directorio de salida"
    ),
    max_concurrent: int = typer.Option(
        3, "--max-concurrent", "-c", help="Máximo de descargas simultáneas"
    ),
):
    """
    Descarga documentos con login manual interactivo.

    Abre el navegador visible para que hagas login manualmente,
    luego descarga automáticamente todos los documentos de la ficha.
    """

    async def _descargar_con_login():
        console.print(
            Panel.fit(
                f"[bold blue]Scraper Mercado Público - Login Manual[/bold blue]\n[cyan]Código: {codigo}[/cyan]"
            )
        )

        # Inicializar componentes
        storage = LicitacionStorage(output)

        # IMPORTANTE: headless=False para ver el navegador
        async with MPBrowser(headless=False) as browser:
            # Paso 1: Esperar login manual (pasa el código para búsqueda automática)
            login_ok = await browser.esperar_login_manual(codigo=codigo)

            if not login_ok:
                console.print("[red][ERROR] Login no completado correctamente[/red]")
                raise typer.Exit(1)

            # Paso 2: Extraer links de documentos de la página actual
            documentos = await browser.extraer_links_documentos()

            if not documentos:
                console.print(
                    "[yellow][WARN] No se encontraron documentos anexos en la página actual[/yellow]"
                )
                console.print(
                    "[dim]Asegúrate de estar en la ficha de la licitación[/dim]"
                )
                raise typer.Exit(0)

            # Obtener URL actual
            current_url = browser.page.url if browser.page else "unknown"

            # Guardar metadata
            storage.save_metadata(
                codigo,
                {
                    "ficha_url": current_url,
                    "origen": "login_manual",
                    "total_documentos": len(documentos),
                    "documentos": documentos,
                },
            )

            # Descargar documentos usando la sesión del navegador
            doc_dir = storage.get_documentos_dir(codigo)
            descargados = await browser.descargar_documentos_con_sesion(
                documentos, doc_dir, max_concurrent
            )

            # Mostrar resumen
            table = Table(title="Resumen de Descarga")
            table.add_column("Métrica", style="cyan")
            table.add_column("Valor", style="green")
            table.add_row("Documentos encontrados", str(len(documentos)))
            table.add_row("Documentos descargados", str(len(descargados)))
            table.add_row("Directorio", str(storage.get_licitacion_dir(codigo)))
            console.print(table)

            # Parsear documentos
            console.print("\n[blue][DOC] Extrayendo texto de documentos...[/blue]")
            texto_completo = DocumentParser.parse_directory(doc_dir)

            # Guardar resumen
            storage.save_resumen(codigo, texto_completo)

            # Crear template de oferta
            storage.create_template_oferta(codigo)

            console.print(f"\n[green][OK] Proceso completado exitosamente![/green]")
            console.print(
                f"[dim]Archivos guardados en: {storage.get_licitacion_dir(codigo)}[/dim]"
            )

    asyncio.run(_descargar_con_login())


@app.command()
def parsear(
    codigo: str = typer.Argument(..., help="Código de la licitación"),
    output: Optional[Path] = typer.Option(
        None, "--output", "-o", help="Archivo de salida"
    ),
):
    """
    Parsea los documentos descargados y genera un resumen.
    """
    storage = LicitacionStorage()
    doc_dir = storage.get_documentos_dir(codigo)

    if not doc_dir.exists():
        console.print(f"[red][ERROR] No se encontraron documentos para {codigo}[/red]")
        console.print("[dim]Ejecuta primero: mp-scraper descargar {codigo}[/dim]")
        raise typer.Exit(1)

    output_file = output or storage.get_licitacion_dir(codigo) / "resumen_licitacion.md"

    console.print(f"[blue][DOC] Parseando documentos en {doc_dir}...[/blue]")
    DocumentParser.parse_directory(doc_dir, output_file)

    console.print(f"[green][OK] Resumen guardado en {output_file}[/green]")


@app.command()
def template(
    codigo: str = typer.Argument(..., help="Código de la licitación"),
    output: Optional[Path] = typer.Option(
        None, "--output", "-o", help="Archivo de salida"
    ),
):
    """
    Genera un template para preparar la oferta.
    """
    storage = LicitacionStorage()

    # Cargar metadata si existe
    metadata = storage.load_metadata(codigo)
    info_licitacion = metadata.get("info_api") if metadata else None

    template_file = storage.create_template_oferta(codigo, info_licitacion)

    console.print(f"[green][OK] Template generado: {template_file}[/green]")


@app.command()
def listar(
    output_dir: Optional[Path] = typer.Option(
        None, "--output", "-o", help="Directorio base"
    ),
):
    """
    Lista todas las licitaciones descargadas.
    """
    storage = LicitacionStorage(output_dir)
    base_dir = storage.base_dir

    if not base_dir.exists():
        console.print(f"[red][ERROR] Directorio no encontrado: {base_dir}[/red]")
        raise typer.Exit(1)

    table = Table(title=f"Licitaciones en {base_dir}")
    table.add_column("Código", style="cyan")
    table.add_column("Documentos", style="green", justify="right")
    table.add_column("Estado", style="yellow")

    for item in sorted(base_dir.iterdir()):
        if item.is_dir():
            doc_dir = item / "documentos"
            num_docs = len(list(doc_dir.glob("*"))) if doc_dir.exists() else 0

            has_template = (item / "template_oferta.md").exists()
            has_resumen = (item / "resumen_licitacion.md").exists()

            estado_parts = []
            if has_resumen:
                estado_parts.append("[DOC]")
            if has_template:
                estado_parts.append("[EDIT]")

            table.add_row(
                item.name,
                str(num_docs),
                " ".join(estado_parts) if estado_parts else "-",
            )

    console.print(table)


@app.command()
def info(
    codigo: str = typer.Argument(..., help="Código de la licitación"),
):
    """
    Muestra información de una licitación descargada.
    """
    storage = LicitacionStorage()

    metadata = storage.load_metadata(codigo)
    if not metadata:
        console.print(f"[red][ERROR] No se encontró metadata para {codigo}[/red]")
        raise typer.Exit(1)

    stats = storage.get_estadisticas(codigo)

    console.print(Panel.fit(f"[bold]{codigo}[/bold]"))

    table = Table(show_header=False)
    table.add_column("Campo", style="cyan")
    table.add_column("Valor", style="white")

    table.add_row("Ficha URL", metadata.get("ficha_url", "N/A"))
    table.add_row("Fecha de scraping", metadata.get("scraped_at", "N/A"))
    table.add_row("Total documentos", str(stats["total_documentos"]))
    table.add_row("Tamaño total", f"{stats['total_bytes'] / 1024:.1f} KB")

    if stats["tipos_archivo"]:
        tipos = ", ".join(
            [f"{ext}({count})" for ext, count in stats["tipos_archivo"].items()]
        )
        table.add_row("Tipos de archivo", tipos)

    console.print(table)


def main():
    """Punto de entrada principal."""
    app()


if __name__ == "__main__":
    main()
