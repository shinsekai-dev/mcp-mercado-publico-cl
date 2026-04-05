"""Configuración de marca — personalizar con los datos reales de tu empresa.

Editá este archivo con los datos de tu empresa antes de generar documentos.
También podés sobreescribir estos valores desde el perfil de proveedor:
    guardar_perfil_proveedor({...})  → se guarda en ~/.mp-mcp/provider.json
"""

from pathlib import Path

# ── Identidad ────────────────────────────────────────────────────────────────
EMPRESA = "Tu Empresa SpA"                # Nombre legal de tu empresa
RUT = ""                                  # RUT empresa (ej: 76.XXX.XXX-X)
GIRO = "Desarrollo de software y servicios TI"
DIRECCION = ""                            # Dirección comercial
TELEFONO = ""                             # +56 9 XXXX XXXX
EMAIL = ""                                # contacto@tuempresa.cl
REPRESENTANTE_LEGAL = ""                  # Nombre completo del representante
SITIO_WEB = ""                            # www.tuempresa.cl

# ── Logo ─────────────────────────────────────────────────────────────────────
# Poner el .png del logo en assets/logo.png
LOGO_PATH = Path(__file__).parent.parent / "assets" / "logo.png"

# ── Paleta de colores (hex sin #) ────────────────────────────────────────────
COLOR_PRIMARY = "1A1A2E"        # Color principal
COLOR_SECONDARY = "16213E"      # Secundario
COLOR_ACCENT = "0F3460"         # Acento
COLOR_LIGHT = "E94560"          # Contraste/highlight
COLOR_BG_ALT = "F0F4F8"         # fondo alternado filas
COLOR_WHITE = "FFFFFF"
COLOR_TEXT_LIGHT = "FFFFFF"
COLOR_BORDER = "CBD5E0"

# ── Tipografía ────────────────────────────────────────────────────────────────
FONT_PRIMARY = "Calibri"        # TODO: reemplazar con fuente de marca si aplica
FONT_SIZE_TITLE = 16
FONT_SIZE_SUBTITLE = 12
FONT_SIZE_BODY = 10
FONT_SIZE_SMALL = 9

# ── Datos como dict (para usar en use cases sin importar todo) ────────────────
def get_datos_proveedor() -> dict:
    return {
        "empresa": EMPRESA,
        "rut": RUT,
        "representante_legal": REPRESENTANTE_LEGAL,
        "direccion": DIRECCION,
        "telefono": TELEFONO,
        "email": EMAIL,
        "giro": GIRO,
    }
