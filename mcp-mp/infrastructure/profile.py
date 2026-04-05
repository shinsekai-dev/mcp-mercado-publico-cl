"""Gestión del perfil de proveedor persistente en ~/.mp-mcp/provider.json."""

import json
import os
from pathlib import Path
from typing import Optional

DEFAULT_PROFILE_PATH = Path.home() / ".mp-mcp" / "provider.json"

CAMPOS_REQUERIDOS = ["empresa", "rut", "representante_legal", "direccion", "telefono", "email"]
CAMPOS_OPCIONALES = ["giro", "banco", "tipo_cuenta", "numero_cuenta", "email_transferencia"]


def get_profile_path() -> Path:
    env = os.environ.get("MP_PROFILE_PATH")
    return Path(env) if env else DEFAULT_PROFILE_PATH


def save_profile(datos: dict) -> Path:
    path = get_profile_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(datos, f, indent=2, ensure_ascii=False)
    return path


def load_profile() -> Optional[dict]:
    path = get_profile_path()
    if not path.exists():
        return None
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def profile_exists() -> bool:
    path = get_profile_path()
    return path.exists() and path.stat().st_size > 10


def merge_with_profile(datos_proveedor: dict) -> dict:
    """Combina datos del perfil guardado con los datos proporcionados.
    Los datos proporcionados tienen prioridad sobre el perfil."""
    perfil = load_profile() or {}
    return {**perfil, **datos_proveedor}


def validate_profile(datos: dict) -> list[str]:
    """Retorna lista de campos requeridos faltantes."""
    return [c for c in CAMPOS_REQUERIDOS if not datos.get(c)]
