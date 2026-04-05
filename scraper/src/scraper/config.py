"""Configuración y utilidades para el scraper de Mercado Público."""

import os
from pathlib import Path
from typing import Optional

# URLs del portal de Mercado Público
BASE_URL = "https://www.mercadopublico.cl"
BUSQUEDA_URL = f"{BASE_URL}/BuscarLicitacion/Home/Buscar"

# Directorios por defecto
DEFAULT_DOWNLOAD_DIR = Path("./ofertas")
DEFAULT_TIMEOUT = 30_000  # 30 segundos

# Rate limiting (segundos entre requests)
MIN_DELAY_BETWEEN_REQUESTS = 2.0
MAX_DELAY_BETWEEN_REQUESTS = 5.0


def get_download_dir() -> Path:
    """Obtiene el directorio de descarga configurado."""
    download_dir = os.getenv("MP_SCRAPER_DOWNLOAD_DIR")
    if download_dir:
        return Path(download_dir)
    return DEFAULT_DOWNLOAD_DIR


def ensure_dir(path: Path) -> Path:
    """Asegura que un directorio exista, creándolo si es necesario."""
    path.mkdir(parents=True, exist_ok=True)
    return path
