import json
from typing import Optional
from interfaces.mcp.server import mcp
from infrastructure.licitacion_repository import MercadoPublicoLicitacionRepository
from infrastructure.orden_compra_repository import MercadoPublicoOrdenCompraRepository
from application.licitacion.use_cases import (
    ObtenerLicitacion,
    ListarLicitacionesHoy,
    ListarLicitacionesActivas,
    ListarLicitacionesPorFecha,
    ListarLicitacionesPorEstado,
    ListarLicitacionesPorOrganismo,
    ListarLicitacionesPorProveedor,
    BuscarLicitacionesPorNombre,
    BuscarLicitacionesSoftware,
)
from domain.licitacion.categories import PERFILES
from application.orden_compra.use_cases import (
    ObtenerOrdenCompra,
    ListarOrdenesHoy,
    ListarOrdenesPorFecha,
    ListarOrdenesPorEstado,
    ListarOrdenesPorOrganismo,
    ListarOrdenesPorProveedor,
)

_lic_repo = MercadoPublicoLicitacionRepository()
_oc_repo = MercadoPublicoOrdenCompraRepository()

# ─── Licitaciones ────────────────────────────────────────────────────────────


@mcp.tool()
async def obtener_licitacion(codigo: str) -> dict:
    """Obtiene el detalle completo de una licitación de Mercado Público por su código.
    Ejemplo de código: '1509-5-L114'. Retorna todos los campos incluyendo comprador,
    fechas, ítems y adjudicación."""
    try:
        lic = await ObtenerLicitacion(_lic_repo).execute(codigo)
        return lic.model_dump(mode="json")
    except Exception as e:
        return {"error": str(e)}


@mcp.tool()
async def listar_licitaciones_hoy() -> dict:
    """Lista todas las licitaciones publicadas en el día actual en todos sus estados."""
    try:
        lics = await ListarLicitacionesHoy(_lic_repo).execute()
        return {
            "cantidad": len(lics),
            "licitaciones": [l.model_dump(mode="json") for l in lics],
        }
    except Exception as e:
        return {"error": str(e)}


@mcp.tool()
async def listar_licitaciones_activas() -> dict:
    """Lista únicamente las licitaciones activas/publicadas al día de hoy en Mercado Público."""
    try:
        lics = await ListarLicitacionesActivas(_lic_repo).execute()
        return {
            "cantidad": len(lics),
            "licitaciones": [l.model_dump(mode="json") for l in lics],
        }
    except Exception as e:
        return {"error": str(e)}


@mcp.tool()
async def listar_licitaciones_por_fecha(fecha: str) -> dict:
    """Lista todas las licitaciones de una fecha específica.
    El parámetro 'fecha' debe estar en formato ddmmaaaa (ejemplo: '02022014' para el 2 de febrero de 2014)."""
    try:
        lics = await ListarLicitacionesPorFecha(_lic_repo).execute(fecha)
        return {
            "cantidad": len(lics),
            "licitaciones": [l.model_dump(mode="json") for l in lics],
        }
    except Exception as e:
        return {"error": str(e)}


@mcp.tool()
async def listar_licitaciones_por_estado(
    estado: str, fecha: Optional[str] = None
) -> dict:
    """Lista licitaciones filtradas por estado. Si no se especifica fecha, usa el día actual.
    Estados válidos: Publicada, Cerrada, Desierta, Adjudicada, Revocada, Suspendida, Todos.
    Fecha en formato ddmmaaaa (opcional)."""
    try:
        lics = await ListarLicitacionesPorEstado(_lic_repo).execute(estado, fecha)
        return {
            "cantidad": len(lics),
            "licitaciones": [l.model_dump(mode="json") for l in lics],
        }
    except Exception as e:
        return {"error": str(e)}


@mcp.tool()
async def listar_licitaciones_por_organismo(
    codigo_organismo: str, fecha: Optional[str] = None
) -> dict:
    """Lista las licitaciones publicadas por un organismo público específico.
    El 'codigo_organismo' es el código numérico del organismo (ejemplo: '6945').
    Fecha en formato ddmmaaaa (opcional, por defecto día actual)."""
    try:
        lics = await ListarLicitacionesPorOrganismo(_lic_repo).execute(
            codigo_organismo, fecha
        )
        return {
            "cantidad": len(lics),
            "licitaciones": [l.model_dump(mode="json") for l in lics],
        }
    except Exception as e:
        return {"error": str(e)}


@mcp.tool()
async def listar_licitaciones_por_proveedor(
    codigo_proveedor: str, fecha: Optional[str] = None
) -> dict:
    """Lista las licitaciones asociadas a un proveedor específico.
    El 'codigo_proveedor' es el código numérico del proveedor (ejemplo: '17793').
    Fecha en formato ddmmaaaa (opcional, por defecto día actual)."""
    try:
        lics = await ListarLicitacionesPorProveedor(_lic_repo).execute(
            codigo_proveedor, fecha
        )
        return {
            "cantidad": len(lics),
            "licitaciones": [l.model_dump(mode="json") for l in lics],
        }
    except Exception as e:
        return {"error": str(e)}


@mcp.tool()
async def buscar_licitaciones_por_nombre(
    query: str,
    fecha_inicio: Optional[str] = None,
    fecha_fin: Optional[str] = None,
) -> dict:
    """Busca licitaciones cuyo nombre o descripción contengan el texto indicado.
    Si no se especifican fechas, busca entre las licitaciones activas del día.
    Si se especifican, consulta la API día a día en el rango y filtra en memoria.
    Fechas en formato ddmmaaaa. Rango máximo: 30 días.
    Ejemplo: query='equipos computacionales', fecha_inicio='01032024', fecha_fin='07032024'."""
    try:
        lics = await BuscarLicitacionesPorNombre(_lic_repo).execute(
            query, fecha_inicio, fecha_fin
        )
        if not lics:
            return {
                "cantidad": 0,
                "licitaciones": [],
                "mensaje": f"No se encontraron licitaciones con '{query}'.",
            }
        return {
            "cantidad": len(lics),
            "licitaciones": [l.model_dump(mode="json") for l in lics],
        }
    except Exception as e:
        return {"error": str(e)}


@mcp.tool()
async def buscar_licitaciones_software(
    query: Optional[str] = None,
    fecha_inicio: Optional[str] = None,
    fecha_fin: Optional[str] = None,
) -> dict:
    """Busca licitaciones relacionadas con desarrollo de software y servicios TI.

    Filtra por códigos UNSPSC de tecnología (prefijos 43, 4323, 81111, 81112)
    y por palabras clave en nombre, descripción y categorías de ítems.
    Retorna resultados ordenados por score de relevancia (0-3).

    Si no se especifican fechas, busca entre las licitaciones activas del día.
    Fechas en formato ddmmaaaa. Rango máximo: 30 días.

    Parámetro 'query' opcional para refinar la búsqueda por texto adicional."""
    try:
        resultados = await BuscarLicitacionesSoftware(_lic_repo).execute(
            query=query,
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin,
        )
        if not resultados:
            return {
                "cantidad": 0,
                "licitaciones": [],
                "mensaje": "No se encontraron licitaciones de software/TI activas hoy.",
            }
        return {
            "cantidad": len(resultados),
            "licitaciones": [
                {
                    "score_relevancia": r["score"],
                    **r["licitacion"].model_dump(mode="json"),
                }
                for r in resultados
            ],
        }
    except Exception as e:
        return {"error": str(e)}


@mcp.tool()
async def filtrar_licitaciones_por_categoria(
    codigos_unspsc: list[str],
    fecha_inicio: Optional[str] = None,
    fecha_fin: Optional[str] = None,
) -> dict:
    """Filtra licitaciones por prefijos de código UNSPSC en sus ítems.

    Útil para buscar licitaciones de cualquier rubro por categoría de producto.
    Perfiles predefinidos disponibles:
    - software: ['43', '4323', '81111', '81112']
    - construccion: ['72', '73', '7210', '7211']
    - salud: ['42', '85', '8510', '8511']
    - consultoria: ['80', '8010', '8011']
    - educacion: ['86', '8610']

    Fechas en formato ddmmaaaa. Sin fechas, usa las licitaciones activas del día."""
    try:
        resultados = await BuscarLicitacionesSoftware(_lic_repo).execute(
            query=None,
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin,
            perfil="software",
        )
        # Aplicar filtro manual por los prefijos indicados
        from domain.licitacion.categories import CategoryFilter
        filtradas = [
            r for r in resultados
            if CategoryFilter.matches_unspsc(r["licitacion"], codigos_unspsc)
        ]
        return {
            "cantidad": len(filtradas),
            "prefijos_buscados": codigos_unspsc,
            "licitaciones": [r["licitacion"].model_dump(mode="json") for r in filtradas],
        }
    except Exception as e:
        return {"error": str(e)}


# ─── Órdenes de Compra ───────────────────────────────────────────────────────


@mcp.tool()
async def obtener_orden_compra(codigo: str) -> dict:
    """Obtiene el detalle completo de una orden de compra de Mercado Público por su código.
    Ejemplo de código: '2097-241-SE14'. Retorna todos los campos incluyendo comprador,
    proveedor, ítems con precios y totales."""
    try:
        oc = await ObtenerOrdenCompra(_oc_repo).execute(codigo)
        return oc.model_dump(mode="json")
    except Exception as e:
        return {"error": str(e)}


@mcp.tool()
async def listar_ordenes_hoy() -> dict:
    """Lista todas las órdenes de compra emitidas en el día actual en todos sus estados."""
    try:
        ocs = await ListarOrdenesHoy(_oc_repo).execute()
        return {
            "cantidad": len(ocs),
            "ordenes": [o.model_dump(mode="json") for o in ocs],
        }
    except Exception as e:
        return {"error": str(e)}


@mcp.tool()
async def listar_ordenes_por_fecha(fecha: str) -> dict:
    """Lista las órdenes de compra emitidas en una fecha específica.
    El parámetro 'fecha' debe estar en formato ddmmaaaa (ejemplo: '02022014')."""
    try:
        ocs = await ListarOrdenesPorFecha(_oc_repo).execute(fecha)
        return {
            "cantidad": len(ocs),
            "ordenes": [o.model_dump(mode="json") for o in ocs],
        }
    except Exception as e:
        return {"error": str(e)}


@mcp.tool()
async def listar_ordenes_por_estado(estado: str, fecha: Optional[str] = None) -> dict:
    """Lista órdenes de compra filtradas por estado. Si no se especifica fecha, usa el día actual.
    Estados válidos: enviadaproveedor, aceptada, cancelada, recepcionconforme,
    pendienterecepcion, recepcionaceptadacialmente, recepecionconformeincompleta, todos.
    Fecha en formato ddmmaaaa (opcional)."""
    try:
        ocs = await ListarOrdenesPorEstado(_oc_repo).execute(estado, fecha)
        return {
            "cantidad": len(ocs),
            "ordenes": [o.model_dump(mode="json") for o in ocs],
        }
    except Exception as e:
        return {"error": str(e)}


@mcp.tool()
async def listar_ordenes_por_organismo(
    codigo_organismo: str, fecha: Optional[str] = None
) -> dict:
    """Lista las órdenes de compra emitidas por un organismo público específico.
    El 'codigo_organismo' es el código numérico del organismo (ejemplo: '6945').
    Fecha en formato ddmmaaaa (opcional, por defecto día actual)."""
    try:
        ocs = await ListarOrdenesPorOrganismo(_oc_repo).execute(codigo_organismo, fecha)
        return {
            "cantidad": len(ocs),
            "ordenes": [o.model_dump(mode="json") for o in ocs],
        }
    except Exception as e:
        return {"error": str(e)}


@mcp.tool()
async def listar_ordenes_por_proveedor(
    codigo_proveedor: str, fecha: Optional[str] = None
) -> dict:
    """Lista las órdenes de compra enviadas a un proveedor específico.
    El 'codigo_proveedor' es el código numérico del proveedor (ejemplo: '17793').
    Fecha en formato ddmmaaaa (opcional, por defecto día actual)."""
    try:
        ocs = await ListarOrdenesPorProveedor(_oc_repo).execute(codigo_proveedor, fecha)
        return {
            "cantidad": len(ocs),
            "ordenes": [o.model_dump(mode="json") for o in ocs],
        }
    except Exception as e:
        return {"error": str(e)}


# ─── Cotización ──────────────────────────────────────────────────────────────


@mcp.tool()
async def generar_cotizacion_excel(
    codigo: str,
    items_precios: list[dict],
    datos_proveedor: dict,
    output_dir: Optional[str] = None,
) -> dict:
    """Genera un archivo Excel de cotización para una licitación de Mercado Público.

    Combina los ítems de la licitación (obtenidos de la API) con los precios
    proporcionados y genera un .xlsx formateado con encabezado, tabla de precios,
    subtotal, IVA, total y bloque de firma.

    Args:
        codigo: Código de la licitación (ej: '1005498-5-LE26')
        items_precios: Lista de dicts con los precios por correlativo.
            Ejemplo: [{"correlativo": 1, "precio_unitario_neto": 150000}, ...]
            Si la licitación no tiene ítems en la API, incluir también
            'descripcion', 'cantidad' y 'unidad_medida' en cada dict.
        datos_proveedor: Dict con datos de la empresa:
            {"empresa": "Mi Empresa SpA", "rut": "76.123.456-7",
             "representante_legal": "Juan Pérez", "direccion": "Av. X 123",
             "telefono": "+56 9 1234 5678", "email": "contacto@empresa.cl",
             "giro": "Desarrollo de software"}
        output_dir: Directorio de salida (default: ./ofertas/<codigo>/)

    Returns:
        Dict con:
        - archivo: path al .xlsx generado
        - total: monto total de la cotización
        - items_count: número de ítems incluidos
    """
    try:
        from application.cotizacion.use_cases import GenerarCotizacionExcel
        path = await GenerarCotizacionExcel(_lic_repo).execute(
            codigo=codigo,
            items_precios=items_precios,
            datos_proveedor=datos_proveedor,
            output_dir=output_dir,
        )
        # Calcular total para el resumen
        from domain.cotizacion.entities import DatosProveedor, ItemCotizacion, Cotizacion
        return {
            "success": True,
            "archivo": str(path.absolute()),
            "mensaje": f"Excel generado correctamente en {path}",
        }
    except Exception as e:
        return {"error": str(e)}


# ─── Documentos de postulación ───────────────────────────────────────────────


@mcp.tool()
async def listar_tipos_documentos() -> dict:
    """Lista todos los tipos de documentos de postulación disponibles para generar.

    Retorna el catálogo completo con nombre, descripción y campos requeridos
    para cada tipo de documento estándar de licitaciones chilenas."""
    from application.documentos.use_cases import ListarTiposDocumentos
    return {"documentos": ListarTiposDocumentos().execute()}


@mcp.tool()
async def generar_documento_licitacion(
    tipo: str,
    codigo: str,
    datos_proveedor: dict,
    output_dir: Optional[str] = None,
) -> dict:
    """Genera un documento DOCX de postulación para una licitación específica.

    Args:
        tipo: Tipo de documento. Valores válidos:
            - carta_presentacion
            - anexo_2_aceptacion_bases
            - anexo_3_conflicto_intereses
            - anexo_4_declaracion_probidad
            - anexo_5_datos_transferencia
            - anexo_7_pacto_integridad
        codigo: Código de la licitación (ej: '1005498-5-LE26')
        datos_proveedor: Dict con datos de la empresa. Campos opcionales
            (se completan con el perfil configurado si no se proveen):
            empresa, rut, representante_legal, direccion, telefono, email, giro.
            Para anexo_5, agregar: banco, tipo_cuenta, numero_cuenta, email_transferencia.
        output_dir: Directorio de salida (default: ./ofertas/<codigo>/documentos_postulacion/)

    Returns:
        Dict con 'archivo' (path al .docx generado)."""
    try:
        from application.documentos.use_cases import GenerarDocumento
        path = await GenerarDocumento(_lic_repo).execute(
            tipo=tipo,
            codigo=codigo,
            datos_proveedor=datos_proveedor,
            output_dir=output_dir,
        )
        return {"success": True, "archivo": str(path.absolute()), "tipo": tipo}
    except Exception as e:
        return {"error": str(e)}


@mcp.tool()
async def generar_documentos_licitacion(
    codigo: str,
    datos_proveedor: dict,
    output_dir: Optional[str] = None,
) -> dict:
    """Genera todos los documentos estándar de postulación para una licitación.

    Genera en un solo paso: carta de presentación + los 5 anexos estándar
    (aceptación de bases, conflicto de intereses, probidad, transferencia, pacto).

    Args:
        codigo: Código de la licitación (ej: '1005498-5-LE26')
        datos_proveedor: Dict con datos de la empresa (se mezcla con el perfil configurado).
            Para datos bancarios en Anexo 5: incluir banco, tipo_cuenta, numero_cuenta.
        output_dir: Directorio de salida (default: ./ofertas/<codigo>/documentos_postulacion/)

    Returns:
        Dict con lista de archivos generados."""
    try:
        from application.documentos.use_cases import GenerarTodosDocumentos
        paths = await GenerarTodosDocumentos(_lic_repo).execute(
            codigo=codigo,
            datos_proveedor=datos_proveedor,
            output_dir=output_dir,
        )
        return {
            "success": True,
            "cantidad": len(paths),
            "archivos": [str(p.absolute()) for p in paths],
            "directorio": str(paths[0].parent.absolute()) if paths else None,
        }
    except Exception as e:
        return {"error": str(e)}


# ─── Perfil de proveedor ─────────────────────────────────────────────────────


@mcp.tool()
async def guardar_perfil_proveedor(datos: dict) -> dict:
    """Guarda el perfil de la empresa en ~/.mp-mcp/provider.json para reutilizarlo.

    Una vez guardado, todas las tools de generación usarán estos datos
    automáticamente sin necesidad de pasarlos en cada llamada.

    Campos requeridos: empresa, rut, representante_legal, direccion, telefono, email.
    Campos opcionales: giro, banco, tipo_cuenta, numero_cuenta, email_transferencia.

    Ejemplo:
        {"empresa": "Tu Empresa SpA", "rut": "76.123.456-7",
         "representante_legal": "Juan Pérez", "direccion": "Av. X 123, Santiago",
         "telefono": "+56 9 1234 5678", "email": "contacto@tuempresa.cl",
         "giro": "Desarrollo de software", "banco": "Banco Estado",
         "tipo_cuenta": "Cuenta Corriente", "numero_cuenta": "123456789"}"""
    try:
        from infrastructure.profile import save_profile, validate_profile
        faltantes = validate_profile(datos)
        if faltantes:
            return {
                "error": f"Campos requeridos faltantes: {', '.join(faltantes)}",
                "campos_requeridos": ["empresa", "rut", "representante_legal", "direccion", "telefono", "email"],
            }
        path = save_profile(datos)
        return {"success": True, "guardado_en": str(path), "campos": list(datos.keys())}
    except Exception as e:
        return {"error": str(e)}


@mcp.tool()
async def obtener_perfil_proveedor() -> dict:
    """Obtiene el perfil de proveedor guardado en ~/.mp-mcp/provider.json.

    Retorna los datos guardados o un mensaje indicando que no hay perfil."""
    try:
        from infrastructure.profile import load_profile, get_profile_path
        perfil = load_profile()
        if perfil is None:
            return {
                "perfil": None,
                "mensaje": "No hay perfil guardado. Usá guardar_perfil_proveedor() para configurarlo.",
                "path": str(get_profile_path()),
            }
        return {"perfil": perfil, "path": str(get_profile_path())}
    except Exception as e:
        return {"error": str(e)}


# ─── Orquestación ─────────────────────────────────────────────────────────────


@mcp.tool()
async def analizar_licitacion_completa(codigo: str) -> dict:
    """Obtiene un análisis completo de una licitación combinando API + documentos.

    Ejecuta en secuencia:
    1. Datos estructurados de la API (nombre, organismo, fechas, ítems, monto)
    2. Score de relevancia para software/TI
    3. Si hay sesión activa del scraper: descarga y extrae texto de todos los documentos
    4. Resumen ejecutivo del contenido de las bases (si se pudieron descargar)

    Útil para que el agente evalúe si vale la pena postular antes de generar documentos.

    Args:
        codigo: Código de la licitación (ej: '1005498-5-LE26')"""
    resultado: dict = {"codigo": codigo}

    # 1. Datos de la API
    try:
        lic = await ObtenerLicitacion(_lic_repo).execute(codigo)
        resultado["licitacion"] = lic.model_dump(mode="json")

        # Score software
        from domain.licitacion.categories import CategoryFilter
        resultado["score_software"] = CategoryFilter.score_software(lic)

        # Fechas clave
        if lic.Fechas:
            resultado["fecha_cierre"] = (
                lic.Fechas.FechaCierre.isoformat() if lic.Fechas.FechaCierre else None
            )
        resultado["monto_estimado"] = lic.MontoEstimado
        resultado["organismo"] = (
            lic.Comprador.NombreOrganismo if lic.Comprador else None
        )
    except Exception as e:
        resultado["error_api"] = str(e)
        return resultado

    # 2. Documentos (si hay scraper disponible y sesión activa)
    try:
        from scraper.auth import cookies_exist
        from scraper.browser import MPBrowser
        from scraper.parser import DocumentParser
        from scraper.storage import LicitacionStorage
        import asyncio

        if not cookies_exist():
            resultado["documentos"] = {
                "disponible": False,
                "mensaje": "Sin sesión del scraper. Ejecutá 'mp-scraper login' para habilitar descarga de docs.",
            }
        else:
            storage = LicitacionStorage()
            doc_dir = storage.get_documentos_dir(codigo)

            # Si ya están descargados, reusar
            if doc_dir.exists() and any(doc_dir.iterdir()):
                texto = DocumentParser.parse_directory(doc_dir)
                archivos = [f.name for f in doc_dir.iterdir() if f.is_file()]
                resultado["documentos"] = {
                    "disponible": True,
                    "fuente": "cache",
                    "cantidad": len(archivos),
                    "archivos": archivos,
                    "resumen_preview": texto[:2000] + "..." if len(texto) > 2000 else texto,
                }
            else:
                async with MPBrowser(headless=True) as browser:
                    ficha_url = await browser.buscar_licitacion(codigo)
                    if not ficha_url:
                        resultado["documentos"] = {
                            "disponible": False,
                            "mensaje": "No se encontró la ficha en el portal web.",
                        }
                    else:
                        docs = await browser.extraer_links_documentos()
                        if not docs:
                            resultado["documentos"] = {
                                "disponible": True,
                                "cantidad": 0,
                                "mensaje": "La ficha existe pero no tiene documentos anexos.",
                            }
                        else:
                            descargados = await browser.descargar_documentos_con_sesion(
                                docs, doc_dir
                            )
                            texto = DocumentParser.parse_directory(doc_dir)
                            storage.save_resumen(codigo, texto)
                            resultado["documentos"] = {
                                "disponible": True,
                                "fuente": "descargado",
                                "cantidad": len(descargados),
                                "archivos": [d.name for d in descargados],
                                "resumen_preview": texto[:2000] + "..." if len(texto) > 2000 else texto,
                            }
    except ImportError:
        resultado["documentos"] = {
            "disponible": False,
            "mensaje": "Scraper no instalado. Instalá con: cd scraper && pip install -e .",
        }
    except Exception as e:
        resultado["documentos"] = {"disponible": False, "error": str(e)}

    return resultado


@mcp.tool()
async def preparar_oferta(
    codigo: str,
    items_precios: list[dict],
    datos_proveedor: Optional[dict] = None,
    output_dir: Optional[str] = None,
) -> dict:
    """Genera el paquete completo de postulación para una licitación.

    En una sola llamada genera:
    - cotizacion_<codigo>.xlsx — planilla de precios formateada
    - carta_presentacion.docx
    - anexo_2_aceptacion_bases.docx
    - anexo_3_conflicto_intereses.docx
    - anexo_4_declaracion_probidad.docx
    - anexo_5_datos_transferencia.docx
    - anexo_7_pacto_integridad.docx

    Usa el perfil guardado con guardar_perfil_proveedor() si datos_proveedor
    no se especifica (o lo combina con los datos adicionales proporcionados).

    Args:
        codigo: Código de la licitación (ej: '1005498-5-LE26')
        items_precios: Lista de precios por correlativo.
            Ejemplo: [{"correlativo": 1, "precio_unitario_neto": 500000}]
        datos_proveedor: Dict con datos de la empresa (opcional si hay perfil guardado).
            Para datos bancarios del Anexo 5 incluir banco, tipo_cuenta, numero_cuenta.
        output_dir: Directorio raíz de salida (default: ./ofertas/<codigo>/)

    Returns:
        Dict con paths a todos los archivos generados y totales."""
    try:
        from infrastructure.profile import merge_with_profile, profile_exists
        from application.cotizacion.use_cases import GenerarCotizacionExcel
        from application.documentos.use_cases import GenerarTodosDocumentos
        from pathlib import Path

        # Resolver datos de proveedor
        datos = merge_with_profile(datos_proveedor or {})
        if not datos.get("empresa"):
            return {
                "error": "No hay perfil de proveedor. Usá guardar_perfil_proveedor() primero o pasá datos_proveedor.",
            }

        base_dir = Path(output_dir) if output_dir else Path("ofertas") / codigo

        # Generar Excel
        excel_path = await GenerarCotizacionExcel(_lic_repo).execute(
            codigo=codigo,
            items_precios=items_precios,
            datos_proveedor=datos,
            output_dir=str(base_dir),
        )

        # Generar todos los DOCX
        docs_dir = base_dir / "documentos_postulacion"
        docx_paths = await GenerarTodosDocumentos(_lic_repo).execute(
            codigo=codigo,
            datos_proveedor=datos,
            output_dir=str(docs_dir),
        )

        todos_archivos = [str(excel_path.absolute())] + [str(p.absolute()) for p in docx_paths]

        return {
            "success": True,
            "codigo": codigo,
            "directorio_base": str(base_dir.absolute()),
            "cotizacion_excel": str(excel_path.absolute()),
            "documentos_docx": [str(p.absolute()) for p in docx_paths],
            "total_archivos": len(todos_archivos),
            "archivos": todos_archivos,
            "siguiente_paso": "Revisá los documentos, completá los campos marcados con ___ y cargalos al portal de Mercado Público.",
        }
    except Exception as e:
        return {"error": str(e)}


# ─── Importar tools del scraper de documentos (opcional) ─────────────────────
# Estas tools permiten descargar documentos anexos desde el portal web
try:
    from interfaces.mcp.scraper_tools import (
        descargar_documentacion_licitacion,
        obtener_info_licitacion_con_documentos,
        verificar_sesion_scraper,
    )
except ImportError as e:
    # Scraper no instalado o no disponible
    pass
