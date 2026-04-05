"""Cliente de navegador Playwright para scraping de Mercado Público."""

import asyncio
import random
from pathlib import Path
from typing import Optional
from urllib.parse import urlencode, urljoin

from playwright.async_api import async_playwright, Page, Browser, BrowserContext
from rich.console import Console

from .config import (
    BASE_URL,
    BUSQUEDA_URL,
    MIN_DELAY_BETWEEN_REQUESTS,
    MAX_DELAY_BETWEEN_REQUESTS,
)

console = Console()

# Iconos compatibles con Windows
ICON_OK = "[OK]"
ICON_ERROR = "[ERROR]"
ICON_WARNING = "[WARN]"
ICON_SEARCH = "[BUSCAR]"
ICON_DOC = "[DOC]"


class MPBrowser:
    """Navegador para interactuar con el portal de Mercado Público."""

    def __init__(self, headless: bool = True, cookies_path: Optional[Path] = None):
        self.headless = headless
        self.cookies_path = cookies_path
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None

    async def __aenter__(self):
        """Inicializa el navegador."""
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(headless=self.headless)
        self.context = await self.browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={"width": 1920, "height": 1080},
        )
        self.page = await self.context.new_page()
        from .auth import load_cookies
        if self.cookies_path or (Path.home() / ".mp-mcp" / "cookies.json").exists():
            from .auth import get_cookies_path
            loaded = await load_cookies(self.context, self.cookies_path)
            if loaded:
                console.print(f"[green]{ICON_OK}[/green] Cookies de sesión cargadas")
            else:
                console.print(f"[yellow]{ICON_WARNING}[/yellow] No se encontraron cookies guardadas")
        console.print(f"[green]{ICON_OK}[/green] Navegador inicializado")
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Cierra el navegador."""
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()
        console.print(f"[green]{ICON_OK}[/green] Navegador cerrado")

    async def _random_delay(self):
        """Espera un tiempo aleatorio entre requests para no sobrecargar el servidor."""
        delay = random.uniform(MIN_DELAY_BETWEEN_REQUESTS, MAX_DELAY_BETWEEN_REQUESTS)
        await asyncio.sleep(delay)

    async def buscar_licitacion(self, codigo: str) -> Optional[str]:
        """
        Busca una licitación por código en el portal.
        Intenta primero acceder directamente usando el patrón de URL conocido.

        Args:
            codigo: Código de licitación (ej: "1005498-5-LE26")

        Returns:
            URL de la ficha de licitación o None si no se encuentra
        """
        if not self.page:
            raise RuntimeError("Navegador no inicializado")

        console.print(f"[blue]{ICON_SEARCH} Buscando licitacion: {codigo}[/blue]")

        try:
            # METODO 1: Intentar acceder directamente a la ficha
            # URL descubierta: /Procurement/Modules/RFB/DetailsAcquisition.aspx?idlicitacion=XXXX
            direct_url = f"{BASE_URL}/Procurement/Modules/RFB/DetailsAcquisition.aspx?idlicitacion={codigo}"
            console.print(f"[dim]Intentando acceso directo: {direct_url}[/dim]")

            await self.page.goto(direct_url, wait_until="networkidle")
            await self._random_delay()

            # Verificar si cargó correctamente (no es página de error)
            current_url = self.page.url
            page_title = await self.page.title()

            # Si no es un error y contiene el código, probablemente es la ficha
            if (
                "DetailsAcquisition" in current_url
                and "error" not in page_title.lower()
            ):
                # Verificar que el código esté en la página
                page_content = await self.page.content()
                if codigo in page_content:
                    console.print(
                        f"[green]{ICON_OK}[/green] Encontrada ficha (acceso directo): {current_url}"
                    )
                    return current_url

            # METODO 2: Buscar usando el buscador oficial
            console.print(
                f"[yellow]{ICON_WARNING} Acceso directo fallo, usando buscador...[/yellow]"
            )

            # Nueva URL de búsqueda basada en el HTML proporcionado
            search_url = f"{BASE_URL}/BuscarLicitacion/Home/Buscar"
            await self.page.goto(search_url, wait_until="networkidle")
            await self._random_delay()

            # Buscar el campo de búsqueda (basado en la estructura HTML real)
            # El buscador usa un input específico
            search_selectors = [
                'input[name="search"]',
                "input#search",
                ".search-input input",
                'input[placeholder*="buscar" i]',
            ]

            search_input = None
            for selector in search_selectors:
                try:
                    search_input = await self.page.wait_for_selector(
                        selector, timeout=3000
                    )
                    if search_input:
                        break
                except:
                    continue

            if search_input:
                await search_input.fill(codigo)
                await self._random_delay()

                # Buscar botón de búsqueda o presionar Enter
                await search_input.press("Enter")
                await self.page.wait_for_load_state("networkidle")
                await self._random_delay()

            # METODO 3: Buscar enlaces en resultados
            # Buscar enlaces que contengan el código o llamen a verFicha
            link_selectors = [
                f'a:has-text("{codigo}")',
                'a[onclick*="verFicha"]',
                'a[onclick*="DetailsAcquisition"]',
                'a[href*="DetailsAcquisition"]',
                ".lic-bloq-wrap a",
                "h2 a",
            ]

            for selector in link_selectors:
                try:
                    links = await self.page.query_selector_all(selector)
                    for link in links:
                        onclick = await link.get_attribute("onclick")
                        href = await link.get_attribute("href")

                        # Si tiene onclick con verFicha, extraer la URL
                        if onclick and "verFicha" in onclick:
                            # Extraer URL de onclick="$.Busqueda.verFicha('URL')"
                            import re

                            url_match = re.search(
                                r"verFicha\(['\"](.+?)['\"]\)", onclick
                            )
                            if url_match:
                                ficha_url = url_match.group(1)
                                # Convertir a URL absoluta si es relativa
                                if ficha_url.startswith("http"):
                                    full_url = ficha_url
                                else:
                                    full_url = urljoin(BASE_URL, ficha_url)

                                await self.page.goto(full_url, wait_until="networkidle")
                                await self._random_delay()

                                console.print(
                                    f"[green]{ICON_OK}[/green] Encontrada ficha de licitacion: {self.page.url}"
                                )
                                return self.page.url

                        # Si tiene href directo
                        elif href and ("DetailsAcquisition" in href or codigo in href):
                            full_url = urljoin(BASE_URL, href)
                            await link.click()
                            await self.page.wait_for_load_state("networkidle")
                            await self._random_delay()

                            console.print(
                                f"[green]{ICON_OK}[/green] Encontrada ficha de licitacion: {self.page.url}"
                            )
                            return self.page.url

                except Exception as e:
                    console.print(f"[dim]Error con selector {selector}: {e}[/dim]")
                    continue

            console.print(
                f"[red]{ICON_ERROR}[/red] No se encontro la licitacion {codigo}"
            )
            return None

        except Exception as e:
            console.print(f"[red]{ICON_ERROR}[/red] Error buscando licitacion: {e}")
            import traceback

            traceback.print_exc()
            return None

    async def extraer_links_documentos(self) -> list[dict]:
        """
        Extrae los links de documentos anexos de la ficha actual.

        El portal estructura los documentos en 3 tablas inline:
        - #grvAdministrativo — Documentos Administrativos
        - #grvTecnico        — Documentos Tecnicos
        - #grvEconomico      — Documentos Economicos

        Cada fila tiene:
        - span[id*="lblDescripcion"] con el nombre del documento
        - input.fancyAdjunto[href*="VerAntecedentes"] con la URL de descarga
          (2 botones por fila con el mismo href — se deduplica)

        Returns:
            Lista de dicts con: nombre, url, seccion, index
        """
        if not self.page:
            raise RuntimeError("Navegador no inicializado")

        console.print(f"[blue]{ICON_DOC} Extrayendo links de documentos...[/blue]")

        documentos = []
        urls_vistas = set()

        sections = [
            ("grvAdministrativo", "Administrativo"),
            ("grvTecnico", "Tecnico"),
            ("grvEconomico", "Economico"),
        ]

        try:
            for section_id, section_label in sections:
                section_el = await self.page.query_selector(f"#{section_id}")
                if not section_el:
                    console.print(f"[dim]  Seccion #{section_id} no encontrada[/dim]")
                    continue

                # Buscar todos los spans de descripcion en esta seccion
                desc_spans = await section_el.query_selector_all(
                    "span[id*='lblDescripcion']"
                )
                console.print(
                    f"[dim]  {section_label}: {len(desc_spans)} descripciones encontradas[/dim]"
                )

                for span in desc_spans:
                    nombre = (await span.inner_text()).strip()
                    if not nombre:
                        nombre = f"Documento_{section_label}_{len(documentos) + 1}"

                    # Derivar el prefijo de fila desde el ID del span
                    # Ej: "grvAdministrativo_ctl02_lblDescripcion" -> "grvAdministrativo_ctl02"
                    span_id = await span.get_attribute("id") or ""
                    row_prefix = span_id.replace("_lblDescripcion", "")

                    if not row_prefix:
                        continue

                    # Buscar boton de descarga por ID derivado del prefijo de fila
                    download_input = await section_el.query_selector(
                        f"input[id^='{row_prefix}_grvDescargar'][href*='VerAntecedentes']"
                    )
                    if not download_input:
                        # Fallback: variante del link
                        download_input = await section_el.query_selector(
                            f"input[id^='{row_prefix}_grvDescargarLink'][href*='VerAntecedentes']"
                        )
                    if not download_input:
                        # Sin archivo descargable en esta fila (ej: "Entregar via sistema")
                        console.print(
                            f"[dim]    Sin descarga: {nombre[:60]}[/dim]"
                        )
                        continue

                    href = await download_input.get_attribute("href")
                    if not href:
                        continue

                    # Resolver URL relativa contra la URL actual de la pagina
                    full_url = urljoin(self.page.url, href)

                    if full_url in urls_vistas:
                        continue
                    urls_vistas.add(full_url)

                    documentos.append(
                        {
                            "nombre": nombre,
                            "url": full_url,
                            "seccion": section_label,
                            "index": len(documentos),
                        }
                    )

            console.print(
                f"[green]{ICON_OK}[/green] Encontrados {len(documentos)} documentos unicos"
            )
            return documentos

        except Exception as e:
            console.print(f"[red]{ICON_ERROR}[/red] Error extrayendo links: {e}")
            import traceback

            traceback.print_exc()
            return []

    async def descargar_documento_con_sesion(
        self, url: str, nombre: str, output_dir: Path
    ) -> Optional[Path]:
        """
        Descarga un documento usando la sesión activa del navegador.

        Navega a VerAntecedentes.aspx dentro del mismo contexto (preservando cookies).
        La pagina puede disparar la descarga directamente al cargar, o puede mostrar
        un boton que hay que clickear.

        Args:
            url: URL de VerAntecedentes.aspx con enc= encriptado
            nombre: Nombre descriptivo del documento
            output_dir: Directorio de salida

        Returns:
            Path al archivo descargado o None
        """
        if not self.context:
            raise RuntimeError("Contexto del navegador no inicializado")

        popup_page = None
        try:
            console.print(f"[dim]  [DOWN] Procesando: {nombre[:50]}...[/dim]")

            popup_page = await self.context.new_page()

            # Registrar handler ANTES de navegar — la descarga puede dispararse
            # al cargar la pagina (si el servidor responde con Content-Disposition: attachment)
            download_future: asyncio.Future = asyncio.get_event_loop().create_future()

            def on_download(download):
                if not download_future.done():
                    download_future.set_result(download)

            popup_page.on("download", on_download)

            # Navegar a la URL de descarga — puede lanzar la descarga directamente
            try:
                await popup_page.goto(url, wait_until="networkidle", timeout=30000)
            except Exception:
                # Si la navegacion falla porque el servidor envia el archivo directamente,
                # el evento download ya fue capturado — continuamos
                pass

            # Si la descarga no se disparó sola, buscar boton en la pagina
            if not download_future.done():
                await asyncio.sleep(1)

                boton_selectores = [
                    'input[title="Ver Anexo"]',
                    'input[src*="ver.gif"]',
                    'input[src*="descargar"]',
                    'input[src*="bajar"]',
                    'input[name*="search"]',
                    'input[type="image"]',
                    'a[href*="download" i]',
                ]

                boton_descarga = None
                for selector in boton_selectores:
                    try:
                        boton = await popup_page.query_selector(selector)
                        if boton:
                            boton_descarga = boton
                            break
                    except:
                        continue

                if boton_descarga:
                    await boton_descarga.click()
                else:
                    console.print(
                        f"[yellow]  [WARN][/yellow] No se encontro boton de descarga para: {nombre}"
                    )
                    await popup_page.close()
                    return None

            # Esperar la descarga con timeout
            try:
                download_obj = await asyncio.wait_for(
                    asyncio.shield(download_future), timeout=15
                )
            except asyncio.TimeoutError:
                console.print(
                    f"[yellow]  [WARN][/yellow] Timeout esperando descarga para: {nombre}"
                )
                await popup_page.close()
                return None

            # Generar nombre de archivo seguro conservando la extension sugerida
            safe_name = "".join(
                c if c.isalnum() or c in "._-" else "_" for c in nombre[:50]
            )
            suggested = download_obj.suggested_filename
            if suggested:
                ext = Path(suggested).suffix
                if ext and not safe_name.endswith(ext):
                    safe_name = f"{safe_name}{ext}"
            if not safe_name.endswith((".pdf", ".doc", ".docx", ".xls", ".xlsx")):
                safe_name = f"{safe_name}.pdf"

            download_path = output_dir / safe_name
            await download_obj.save_as(download_path)

            await popup_page.close()

            if download_path.exists():
                size = download_path.stat().st_size
                console.print(
                    f"[green]  [OK][/green] {download_path.name} ({size} bytes)"
                )
                return download_path
            else:
                console.print(
                    f"[yellow]  [WARN][/yellow] Archivo no guardado: {nombre}"
                )
                return None

        except Exception as e:
            console.print(f"[red]  [ERROR][/red] Error descargando {nombre}: {e}")
            if popup_page:
                try:
                    await popup_page.close()
                except:
                    pass
            return None

    async def descargar_documentos_con_sesion(
        self, documentos: list[dict], output_dir: Path, max_concurrent: int = 2
    ) -> list[Path]:
        """
        Descarga múltiples documentos usando la sesión del navegador.

        Args:
            documentos: Lista de dicts con 'nombre' y 'url'
            output_dir: Directorio de salida
            max_concurrent: Máximo de descargas simultáneas

        Returns:
            Lista de paths a archivos descargados
        """
        from .config import ensure_dir

        ensure_dir(output_dir)

        console.print(
            f"\n[blue][DOC] Descargando {len(documentos)} documentos con sesión activa...[/blue]"
        )

        descargados = []

        # Descargar uno por uno para evitar problemas con sesión
        for doc in documentos:
            resultado = await self.descargar_documento_con_sesion(
                doc["url"], doc["nombre"], output_dir
            )
            if resultado:
                descargados.append(resultado)

            # Pequeña pausa entre descargas
            await asyncio.sleep(1)

        console.print(
            f"[green][OK][/green] Descargados {len(descargados)}/{len(documentos)} documentos"
        )
        return descargados

    async def obtener_html_ficha(self) -> str:
        """Obtiene el HTML de la ficha actual para análisis."""
        if not self.page:
            raise RuntimeError("Navegador no inicializado")
        return await self.page.content()

    async def cargar_ficha_por_url(self, ficha_url: str) -> bool:
        """
        Carga una ficha de licitación directamente desde su URL.

        Args:
            ficha_url: URL completa de la ficha (ej: https://www.mercadopublico.cl/Procurement/Modules/RFB/DetailsAcquisition.aspx?qs=...)

        Returns:
            True si se cargó correctamente
        """
        if not self.page:
            raise RuntimeError("Navegador no inicializado")

        console.print(f"[blue]{ICON_SEARCH} Cargando ficha desde URL...[/blue]")

        try:
            await self.page.goto(ficha_url, wait_until="networkidle")
            await self._random_delay()

            # Verificar que estamos en una ficha válida
            current_url = self.page.url
            if "DetailsAcquisition" in current_url:
                console.print(f"[green]{ICON_OK}[/green] Ficha cargada: {current_url}")
                return True
            else:
                console.print(
                    f"[yellow]{ICON_WARNING}[/yellow] La URL no parece ser una ficha de licitación"
                )
                return False

        except Exception as e:
            console.print(f"[red]{ICON_ERROR}[/red] Error cargando ficha: {e}")
            return False

    async def esperar_login_manual(
        self,
        url: str = "https://www.mercadopublico.cl/Home",
        codigo: Optional[str] = None,
    ) -> bool:
        """
        Abre el portal en modo visible y espera a que el usuario haga login manualmente.
        Puede buscar la licitación automáticamente si se proporciona el código.

        Args:
            url: URL inicial para abrir (default: home del portal)
            codigo: Código de licitación para buscar automáticamente (opcional)

        Returns:
            True si el usuario confirmó que está logueado y en ficha
        """
        if not self.page:
            raise RuntimeError("Navegador no inicializado")

        console.print(f"\n[bold yellow]MODO LOGIN MANUAL[/bold yellow]")
        console.print("=" * 70)
        console.print(f"[blue]Abriendo portal: {url}[/blue]")
        console.print(f"[yellow]Instrucciones:[/yellow]")
        console.print(f"  1. [bold]Haz login[/bold] con tu usuario y contraseña")
        if codigo:
            console.print(
                f"  2. [Opcional] Busca la licitación [cyan]{codigo}[/cyan] o navega a su ficha"
            )
        else:
            console.print(f"  2. Navega a la ficha de la licitación")
        console.print(
            f"  3. Presiona [bold green]ENTER[/bold green] en esta terminal cuando estés listo"
        )
        console.print("=" * 70 + "\n")

        try:
            # Abrir el portal en el navegador visible
            await self.page.goto(url, wait_until="networkidle")

            # Esperar a que el usuario presione ENTER
            console.print("[dim]Esperando que completes el login...[/dim]")

            # Usar input() bloqueante (en un thread separado para no bloquear el event loop)
            import concurrent.futures

            def wait_for_enter():
                input(
                    "\n[Presiona ENTER cuando hayas hecho login (no importa en qué página estés)...]"
                )
                return True

            loop = asyncio.get_event_loop()
            with concurrent.futures.ThreadPoolExecutor() as pool:
                result = await loop.run_in_executor(pool, wait_for_enter)

            if result:
                console.print(f"\n[green]{ICON_OK}[/green] Login confirmado")

                # Verificar si estamos en una ficha de licitación
                current_url = self.page.url
                if "DetailsAcquisition" in current_url:
                    console.print(
                        f"[green]{ICON_OK}[/green] Perfecto! Ya estás en una ficha de licitación"
                    )
                    return True
                elif codigo:
                    # Intentar buscar la licitación automáticamente
                    console.print(
                        f"[blue]{ICON_SEARCH}[/blue] No estás en una ficha. Intentando buscar [cyan]{codigo}[/cyan] automáticamente..."
                    )
                    ficha_url = await self.buscar_licitacion(codigo)
                    if ficha_url:
                        return True
                    else:
                        # Si no se encuentra, pedir al usuario que navegue manualmente
                        console.print(
                            f"[yellow]{ICON_WARNING}[/yellow] No se pudo encontrar automáticamente."
                        )
                        console.print(
                            f"[yellow]Por favor navega manualmente a la ficha y presiona ENTER...[/yellow]"
                        )

                        def wait_for_enter_again():
                            input(
                                "\n[Cuando estés en la ficha de la licitación, presiona ENTER...]"
                            )
                            return True

                        with concurrent.futures.ThreadPoolExecutor() as pool:
                            await loop.run_in_executor(pool, wait_for_enter_again)

                        # Verificar nuevamente
                        current_url = self.page.url
                        if "DetailsAcquisition" in current_url:
                            console.print(
                                f"[green]{ICON_OK}[/green] Ahora sí estás en la ficha!"
                            )
                            return True
                        else:
                            console.print(
                                f"[yellow]{ICON_WARNING}[/yellow] Aún no estás en una ficha. URL: {current_url}"
                            )
                            return False
                else:
                    console.print(
                        f"[yellow]{ICON_WARNING}[/yellow] No estás en una ficha de licitación."
                    )
                    console.print(f"[dim]URL actual: {current_url}[/dim]")
                    console.print(
                        f"[yellow]Navega a la ficha e intenta nuevamente.[/yellow]"
                    )
                    return False

            return False

        except Exception as e:
            console.print(f"[red]{ICON_ERROR}[/red] Error en login manual: {e}")
            return False
