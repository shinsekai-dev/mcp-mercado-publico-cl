"""Tool MCP para integrar el scraper de documentos."""

from typing import Optional
from pathlib import Path
import asyncio

from interfaces.mcp.server import mcp
from infrastructure.licitacion_repository import MercadoPublicoLicitacionRepository
from application.licitacion.use_cases import ObtenerLicitacion

try:
    from scraper.browser import MPBrowser
    from scraper.parser import DocumentParser
    from scraper.storage import LicitacionStorage
    from scraper.auth import cookies_exist, get_cookies_path

    SCRAPER_AVAILABLE = True
except ImportError as e:
    print(f"[WARNING] Scraper no disponible: {e}")
    SCRAPER_AVAILABLE = False


_lic_repo = MercadoPublicoLicitacionRepository()


@mcp.tool()
async def descargar_documentacion_licitacion(
    codigo: str,
    output_dir: Optional[str] = None,
) -> dict:
    """
    Descarga todos los documentos anexos de una licitación desde el portal web de Mercado Público.

    Esta herramienta navega el portal web, extrae los links de documentos anexos (bases, especificaciones,
    anexos), los descarga y genera un resumen en texto para su análisis.

    Args:
        codigo: Código de la licitación (ej: "1005498-5-LE26")
        output_dir: Directorio opcional donde guardar los archivos (default: ./ofertas)

    Returns:
        Dict con información de la descarga:
        - codigo: Código de la licitación
        - ficha_url: URL de la ficha en el portal
        - documentos_descargados: Lista de archivos descargados
        - directorio_salida: Path al directorio con los archivos
        - resumen_path: Path al archivo de resumen en markdown
        - template_path: Path al template de oferta

    Nota: Esta operación puede tardar varios minutos dependiendo de la cantidad de documentos.
    """
    if not SCRAPER_AVAILABLE:
        return {
            "error": "Scraper no disponible. Asegúrate de haber instalado las dependencias del scraper: cd scraper && pip install -e .",
            "codigo": codigo,
        }

    try:
        # Verificar que hay sesión activa
        if not cookies_exist():
            return {
                "error": "Sin sesión autenticada. Ejecutá 'mp-scraper login' en la terminal para guardar las cookies de sesión.",
                "codigo": codigo,
                "ayuda": "El portal requiere autenticación para descargar documentos. Corré 'mp-scraper login', hacé login en el navegador que se abre, y presioná ENTER.",
            }

        from rich.console import Console

        console = Console()

        output_path = Path(output_dir) if output_dir else None
        storage = LicitacionStorage(output_path)

        console.print(f"[blue]Procesando licitación: {codigo}[/blue]")

        async with MPBrowser(headless=True) as browser:
            # Buscar licitación en el portal
            ficha_url = await browser.buscar_licitacion(codigo)

            if not ficha_url:
                return {
                    "error": f"No se pudo encontrar la licitación {codigo} en el portal",
                    "codigo": codigo,
                }

            # Extraer links de documentos
            documentos = await browser.extraer_links_documentos()

            if not documentos:
                return {
                    "warning": "No se encontraron documentos anexos en la ficha",
                    "codigo": codigo,
                    "ficha_url": ficha_url,
                }

            # Guardar metadata
            storage.save_metadata(
                codigo,
                {
                    "ficha_url": ficha_url,
                    "total_documentos": len(documentos),
                    "documentos": documentos,
                },
            )

            # Descargar documentos usando la sesion del browser (requiere cookies ASP.NET)
            doc_dir = storage.get_documentos_dir(codigo)
            descargados = await browser.descargar_documentos_con_sesion(
                documentos, doc_dir
            )

            # Parsear documentos y generar resumen
            console.print("[blue]Generando resumen de documentos...[/blue]")
            texto_completo = DocumentParser.parse_directory(doc_dir)
            storage.save_resumen(codigo, texto_completo)

            # Crear template de oferta
            template_file = storage.create_template_oferta(codigo)

            # Preparar respuesta
            licitacion_dir = storage.get_licitacion_dir(codigo)

            return {
                "success": True,
                "codigo": codigo,
                "ficha_url": ficha_url,
                "total_documentos_encontrados": len(documentos),
                "documentos_descargados": [str(d.name) for d in descargados],
                "directorio_salida": str(licitacion_dir.absolute()),
                "resumen_path": str(
                    (licitacion_dir / "resumen_licitacion.md").absolute()
                ),
                "template_path": str(template_file.absolute()),
                "estructura_archivos": {
                    "metadata.json": "Información de la licitación y documentos",
                    "documentos/": f"{len(descargados)} archivos descargados",
                    "resumen_licitacion.md": "Texto extraído de todos los documentos",
                    "template_oferta.md": "Template para preparar la oferta",
                },
            }

    except Exception as e:
        return {
            "error": f"Error procesando licitación: {str(e)}",
            "codigo": codigo,
            "tipo_error": type(e).__name__,
        }


@mcp.tool()
async def obtener_info_licitacion_con_documentos(codigo: str) -> dict:
    """
    Obtiene información completa de una licitación incluyendo datos de la API y disponibilidad de documentos.

    Esta herramienta combina:
    1. Datos estructurados de la API de Mercado Público
    2. Verificación de disponibilidad de documentos anexos en el portal web

    Args:
        codigo: Código de la licitación (ej: "1005498-5-LE26")

    Returns:
        Dict con:
        - info_api: Datos estructurados de la licitación (nombre, organismo, fechas, etc.)
        - documentos_disponibles: Bool indicando si hay documentos anexos disponibles
        - ficha_url: URL de la ficha en el portal web
    """
    if not SCRAPER_AVAILABLE:
        # Si no hay scraper, al menos devolvemos info de la API
        try:
            licitacion = await ObtenerLicitacion(_lic_repo).execute(codigo)
            return {
                "codigo": codigo,
                "info_api": licitacion.model_dump(mode="json"),
                "documentos_disponibles": False,
                "nota": "Scraper no disponible. Instala las dependencias del scraper para descargar documentos.",
            }
        except Exception as e:
            return {"error": str(e), "codigo": codigo}

    try:
        # Verificar que hay sesión activa
        if not cookies_exist():
            return {
                "error": "Sin sesión autenticada. Ejecutá 'mp-scraper login' en la terminal para guardar las cookies de sesión.",
                "codigo": codigo,
                "ayuda": "El portal requiere autenticación para descargar documentos. Corré 'mp-scraper login', hacé login en el navegador que se abre, y presioná ENTER.",
            }

        # Obtener datos de la API
        licitacion = await ObtenerLicitacion(_lic_repo).execute(codigo)

        async with MPBrowser(headless=True) as browser:
            # Verificar si existe en el portal
            ficha_url = await browser.buscar_licitacion(codigo)

            if not ficha_url:
                return {
                    "codigo": codigo,
                    "info_api": licitacion.model_dump(mode="json"),
                    "documentos_disponibles": False,
                    "ficha_url": None,
                    "nota": "Licitación encontrada en API pero no en portal web",
                }

            # Contar documentos disponibles
            documentos = await browser.extraer_links_documentos()

            return {
                "codigo": codigo,
                "info_api": licitacion.model_dump(mode="json"),
                "documentos_disponibles": len(documentos) > 0,
                "cantidad_documentos": len(documentos),
                "ficha_url": ficha_url,
                "puede_descargarse": True,
            }

    except Exception as e:
        return {
            "error": str(e),
            "codigo": codigo,
            "tipo_error": type(e).__name__,
        }


@mcp.tool()
async def verificar_sesion_scraper() -> dict:
    """
    Verifica si hay una sesión autenticada guardada para el portal de Mercado Público.

    El scraper necesita cookies de sesión para descargar documentos adjuntos.
    Si no hay sesión, ejecutá 'mp-scraper login' en la terminal.

    Returns:
        Dict con:
        - autenticado: bool indicando si hay cookies guardadas
        - cookies_path: path donde se guardan las cookies
        - mensaje: instrucción para el usuario si no hay sesión
    """
    if not SCRAPER_AVAILABLE:
        return {
            "error": "Scraper no disponible. Instalá las dependencias: cd D:/work/mp-mcp/scraper && pip install -e .",
            "autenticado": False,
        }

    existe = cookies_exist()
    cookies_path = str(get_cookies_path())

    return {
        "autenticado": existe,
        "cookies_path": cookies_path,
        "mensaje": (
            "Sesión activa. Podés descargar documentos."
            if existe
            else "Sin sesión. Ejecutá 'mp-scraper login' en la terminal para autenticarte."
        ),
    }
