# MP Scraper - Documentos de Licitaciones

Sistema de scraping para descargar documentos anexos de licitaciones de Mercado Público Chile.

## ¿Qué hace?

Este módulo permite:
1. **Navegar el portal web** de Mercado Público
2. **Extraer links** de documentos anexos (bases, especificaciones, anexos)
3. **Descargar** todos los documentos automáticamente
4. **Parsear** PDFs y DOCs para extraer texto
5. **Generar** resúmenes y templates para preparar ofertas

## Instalación

### 1. Instalar dependencias del scraper

```bash
cd scraper
pip install -e ".[dev]"
```

### 2. Instalar Playwright browsers

```bash
playwright install chromium
```

## Uso

### CLI (Línea de comandos)

```bash
# Descargar documentos de una licitación
mp-scraper descargar 1005498-5-LE26

# Especificar directorio de salida
mp-scraper descargar 1005498-5-LE26 --output ./mis-ofertas

# Ver licitaciones descargadas
mp-scraper listar

# Generar template de oferta
mp-scraper template 1005498-5-LE26

# Ver información de una licitación
mp-scraper info 1005498-5-LE26
```

### Integración con MCP

El scraper se integra automáticamente con el servidor MCP. Nuevas herramientas disponibles:

- `descargar_documentacion_licitacion(codigo)` - Descarga todos los documentos
- `obtener_info_licitacion_con_documentos(codigo)` - Verifica disponibilidad de documentos

## Estructura de archivos generada

```
ofertas/
├── 1005498-5-LE26/
│   ├── metadata.json              # Info de la licitación y documentos
│   ├── documentos/
│   │   ├── bases_administrativas.pdf
│   │   ├── anexo_1.docx
│   │   ├── especificaciones_tecnicas.pdf
│   │   └── ...
│   ├── resumen_licitacion.md      # Texto extraído de todos los documentos
│   └── template_oferta.md         # Template para completar
```

## Componentes

- **browser.py**: Navegación con Playwright
- **downloader.py**: Descarga concurrente de documentos
- **parser.py**: Extracción de texto de PDFs y DOCs
- **storage.py**: Organización de archivos
- **cli.py**: Interfaz de línea de comandos

## Limitaciones

- El portal web de Mercado Público puede cambiar (requiere mantenimiento)
- Formatos .doc (antiguos) requieren conversión manual
- Algunos documentos pueden estar protegidos o requerir autenticación adicional

## Rate Limiting

El scraper incluye delays automáticos entre requests (2-5 segundos) para no sobrecargar los servidores de Mercado Público.

## Licencia

Mismo proyecto principal - Uso para preparación de ofertas legítimas.
