# mp-mcp — MCP Server para Mercado Público Chile

## Estructura del proyecto

Dos paquetes Python independientes en el mismo repo:

```
mp-mcp/
├── mcp-mp/          ← MCP server (FastMCP + DDD)
└── scraper/         ← Playwright scraper (descarga documentos)
```

---

## Instalación (primera vez)

### Requisitos previos
- Python 3.11+
- [uv](https://docs.astral.sh/uv/getting-started/installation/) — gestor de paquetes Python

### 1. Instalar el scraper
```bash
cd scraper
uv pip install -e .
uv run playwright install chromium
```

### 2. Instalar el servidor MCP con soporte de scraper
```bash
cd mcp-mp
uv pip install -e ".[scraper]"
```

### 3. Obtener el ticket de la API
Registrarse en https://www.mercadopublico.cl y obtener el ticket de API desde el perfil.

---

## Configuración en Claude Desktop

Ubicación del archivo de configuración:
- **Windows:** `%APPDATA%\Claude\claude_desktop_config.json`
- **Mac:** `~/Library/Application Support/Claude/claude_desktop_config.json`

Agregar esto (reemplazá `RUTA_AL_REPO` con el path donde clonaste el repo):

```json
{
  "mcpServers": {
    "mercado-publico": {
      "command": "uv",
      "args": [
        "--directory", "RUTA_AL_REPO/mcp-mp",
        "run", "python", "run_stdio.py"
      ],
      "env": {
        "MERCADO_PUBLICO_TICKET": "tu-ticket-aqui"
      }
    }
  }
}
```

**Ejemplo Windows:** `RUTA_AL_REPO` = `D:/trabajo/mp-mcp`  
**Ejemplo Mac/Linux:** `RUTA_AL_REPO` = `/home/usuario/mp-mcp`

Reiniciar Claude Desktop después de guardar.

---

## Primera vez con el scraper (una sola vez por máquina)

El scraper necesita cookies de sesión para descargar documentos del portal.

```bash
cd scraper
uv run mp-scraper login
# Se abre Chrome → hacé login en mercadopublico.cl → presioná ENTER
```

Las cookies se guardan en `~/.mp-mcp/cookies.json` y se reusan automáticamente.

Para verificar desde Claude: usar la tool `verificar_sesion_scraper()`.

---

## Configurar perfil de empresa (una sola vez desde Claude)

Una vez que Claude Desktop tiene el servidor conectado, ejecutar:

```
guardar_perfil_proveedor({
  "empresa": "Nombre de tu empresa",
  "rut": "76.XXX.XXX-X",
  "representante_legal": "Nombre Apellido",
  "direccion": "Dirección completa",
  "telefono": "+56 9 XXXX XXXX",
  "email": "contacto@empresa.cl",
  "giro": "Desarrollo de software",
  "banco": "Banco Estado",
  "tipo_cuenta": "Cuenta Corriente",
  "numero_cuenta": "123456789"
})
```

Se guarda en `~/.mp-mcp/provider.json` y todas las tools lo usan automáticamente.

---

## Flujo de uso típico

```
1. buscar_licitaciones_software()
   → lista licitaciones TI activas ordenadas por relevancia

2. analizar_licitacion_completa("CODIGO")
   → datos completos + descarga automática de documentos

3. preparar_oferta("CODIGO", [{"correlativo": 1, "precio_unitario_neto": 500000}])
   → genera Excel de cotización + 6 documentos DOCX listos para subir
```

---

## Variables de entorno

| Variable | Requerida | Default | Descripción |
|---|---|---|---|
| `MERCADO_PUBLICO_TICKET` | Sí | — | API key de ChileCompra |
| `MERCADO_PUBLICO_BASE_URL` | No | `https://api.mercadopublico.cl/servicios/v1/publico` | Base URL |
| `MP_SCRAPER_COOKIES_PATH` | No | `~/.mp-mcp/cookies.json` | Cookies del scraper |
| `MP_PROFILE_PATH` | No | `~/.mp-mcp/provider.json` | Perfil de proveedor |

---

## Arquitectura — capas DDD

```
domain/          ← entidades Pydantic, repositorios abstractos, servicios de dominio
application/     ← use cases (orquestación + validación)
infrastructure/  ← repositorios, HTTP client, generadores Excel/DOCX, brand, profile
interfaces/mcp/  ← MCP tools (@mcp.tool())
```

**Regla:** las importaciones van hacia adentro únicamente.  
`interfaces` → `application` → `domain`. Nunca al revés.

---

## Marca / Branding

Editar `mcp-mp/infrastructure/brand.py` con los colores y datos reales de la empresa.  
Se aplica automáticamente a todos los Excel y DOCX generados.

---

## Tests

```bash
cd mcp-mp
uv run pytest
```
