"""Gestión de cookies de autenticación persistentes."""

import json
from pathlib import Path
from typing import Optional
from playwright.async_api import BrowserContext

DEFAULT_COOKIES_PATH = Path.home() / ".mp-mcp" / "cookies.json"


def get_cookies_path() -> Path:
    """Obtiene el path de cookies desde env var o default."""
    import os
    env_path = os.environ.get("MP_SCRAPER_COOKIES_PATH")
    return Path(env_path) if env_path else DEFAULT_COOKIES_PATH


async def save_cookies(context: BrowserContext, path: Optional[Path] = None) -> Path:
    """Guarda cookies del BrowserContext a un archivo JSON."""
    cookies_path = path or get_cookies_path()
    cookies_path.parent.mkdir(parents=True, exist_ok=True)
    cookies = await context.cookies()
    with open(cookies_path, "w", encoding="utf-8") as f:
        json.dump(cookies, f, indent=2, ensure_ascii=False)
    return cookies_path


async def load_cookies(context: BrowserContext, path: Optional[Path] = None) -> bool:
    """Carga cookies desde archivo al BrowserContext. Retorna True si se cargaron."""
    cookies_path = path or get_cookies_path()
    if not cookies_path.exists():
        return False
    with open(cookies_path, "r", encoding="utf-8") as f:
        cookies = json.load(f)
    if not cookies:
        return False
    await context.add_cookies(cookies)
    return True


def cookies_exist(path: Optional[Path] = None) -> bool:
    """Verifica si existe el archivo de cookies."""
    cookies_path = path or get_cookies_path()
    return cookies_path.exists() and cookies_path.stat().st_size > 10


def delete_cookies(path: Optional[Path] = None) -> bool:
    """Elimina el archivo de cookies. Retorna True si existía."""
    cookies_path = path or get_cookies_path()
    if cookies_path.exists():
        cookies_path.unlink()
        return True
    return False
