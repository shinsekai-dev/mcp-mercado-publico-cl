"""
MCP Mercado Público — Instalador automático.

Uso: python install.py
"""

import json
import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path


# -- Colores ANSI --------------------------------------------------------------

class C:
    RESET  = "\033[0m"
    BOLD   = "\033[1m"
    RED    = "\033[91m"
    GREEN  = "\033[92m"
    YELLOW = "\033[93m"
    CYAN   = "\033[96m"


def ok(msg):   print(f"  {C.GREEN}[OK]{C.RESET}  {msg}")
def err(msg):  print(f"  {C.RED}[X]{C.RESET}  {C.RED}{msg}{C.RESET}")
def warn(msg): print(f"  {C.YELLOW}!{C.RESET}  {C.YELLOW}{msg}{C.RESET}")
def info(msg): print(f"  {C.CYAN}->{C.RESET}  {msg}")


def header(title: str):
    print(f"\n{C.BOLD}{C.CYAN}{'-' * 58}{C.RESET}")
    print(f"{C.BOLD}{C.CYAN}  {title}{C.RESET}")
    print(f"{C.BOLD}{C.CYAN}{'-' * 58}{C.RESET}\n")


def fatal(message: str, hint: str = ""):
    err(message)
    if hint:
        warn(f"Fix: {hint}")
    sys.exit(1)


# ── Subprocess helper ─────────────────────────────────────────────────────────

def run(cmd: list, *, cwd=None, capture=False) -> subprocess.CompletedProcess:
    # If using 'uv' and it's not in PATH, use 'python -m uv'
    if cmd and cmd[0] == "uv" and not shutil.which("uv"):
        cmd = [sys.executable, "-m", "uv"] + cmd[1:]
        
    result = subprocess.run(cmd, cwd=cwd, capture_output=capture, text=True)
    if result.returncode != 0:
        if capture and (result.stderr or result.stdout):
            print(result.stderr or result.stdout)
        raise subprocess.CalledProcessError(result.returncode, cmd)
    return result


# ── Step 1: Python version ────────────────────────────────────────────────────

def check_python():
    header("Paso 2 / 6 — Versión de Python")
    major, minor = sys.version_info[:2]
    if (major, minor) >= (3, 11):
        ok(f"Python {major}.{minor} — OK")
        return

    warn(f"Python {major}.{minor} detectado — se requiere 3.11+.")
    info("Instalando Python 3.11 via uv (sin tocar tu Python del sistema)...")
    try:
        run(["uv", "python", "install", "3.11"])
    except subprocess.CalledProcessError:
        fatal(
            "No se pudo instalar Python 3.11 automáticamente.",
            "Instalalo manualmente: https://python.org"
        )
    ok("Python 3.11 instalado via uv — OK")


# ── Step 2: uv ───────────────────────────────────────────────────────────────

def _patch_uv_path():
    home = Path.home()
    candidates = [
        home / ".cargo" / "bin",
        home / ".local" / "bin",
    ]
    exe = "uv.exe" if sys.platform == "win32" else "uv"
    for p in candidates:
        if (p / exe).exists():
            os.environ["PATH"] = str(p) + os.pathsep + os.environ["PATH"]
            return


def ensure_uv():
    header("Paso 1 / 6 — Gestor de paquetes uv")

    if shutil.which("uv"):
        ok("uv ya está instalado — saltando")
        return

    # Check if uv is available via python -m uv
    try:
        run([sys.executable, "-m", "uv", "--version"], capture=True)
        ok("uv ya está disponible via 'python -m uv' — saltando")
        return
    except (subprocess.CalledProcessError, FileNotFoundError):
        pass

    info("Instalando uv...")
    try:
        if sys.platform == "win32":
            # Intentar primero con pip (más robusto en Windows con PowerShell roto)
            try:
                info("Intentando instalar uv via pip...")
                run([sys.executable, "-m", "pip", "install", "uv"])
                ok("uv instalado via pip")
                return
            except subprocess.CalledProcessError:
                info("Pip falló, intentando instalador oficial de PowerShell...")
                run([
                    "powershell", "-ExecutionPolicy", "Bypass", "-Command",
                    "irm https://astral.sh/uv/install.ps1 | iex"
                ])
        else:
            run(["sh", "-c", "curl -LsSf https://astral.sh/uv/install.sh | sh"])
    except subprocess.CalledProcessError:
        fatal(
            "No se pudo instalar uv automáticamente.",
            "Instalalo manualmente: https://docs.astral.sh/uv/getting-started/installation/ o 'pip install uv'"
        )

    _patch_uv_path()

    if not shutil.which("uv"):
        # Verificamos si al menos funciona via python -m uv después de instalar
        try:
            run([sys.executable, "-m", "uv", "--version"], capture=True)
            ok("uv instalado (disponible via 'python -m uv')")
            return
        except:
            fatal(
                "uv se instaló pero no se encuentra en el PATH ni via 'python -m uv'.",
                "Abrí una nueva terminal y volvé a ejecutar install.py."
            )

    ok("uv instalado correctamente")


# ── Venv helper ──────────────────────────────────────────────────────────────

def get_venv_python(repo_root: Path) -> Path:
    """Retorna la ruta al ejecutable Python dentro del virtualenv."""
    venv = repo_root / "mcp-mp" / ".venv"
    if sys.platform == "win32":
        return venv / "Scripts" / "python.exe"
    return venv / "bin" / "python"


def ensure_venv(repo_root: Path):
    """Crea el virtualenv con Python 3.11 si no existe."""
    venv_path = repo_root / "mcp-mp" / ".venv"
    venv_py = get_venv_python(repo_root)
    if venv_py.exists():
        ok("Virtualenv ya existe — saltando")
        return
    info(f"uv venv --python 3.11 mcp-mp/.venv")
    try:
        run(["uv", "venv", "--python", "3.11", str(venv_path)])
    except subprocess.CalledProcessError:
        fatal(
            "No se pudo crear el virtualenv.",
            "Ejecutá manualmente: uv venv --python 3.11 mcp-mp/.venv"
        )
    ok("Virtualenv Python 3.11 creado en mcp-mp/.venv")


# ── Step 3: Scraper ───────────────────────────────────────────────────────────

def install_scraper(repo_root: Path):
    header("Paso 3 / 6 — Instalar paquete scraper")
    ensure_venv(repo_root)
    venv_py = str(get_venv_python(repo_root))
    info(f"uv pip install --python .venv -e ./scraper")
    try:
        run(["uv", "pip", "install", "--python", venv_py, "-e", str(repo_root / "scraper")])
    except subprocess.CalledProcessError:
        fatal(
            "No se pudo instalar el paquete scraper.",
            "Ejecutá manualmente: uv pip install --python mcp-mp/.venv/Scripts/python.exe -e ./scraper"
        )
    ok("mp-scraper instalado")


# ── Step 4: Playwright ────────────────────────────────────────────────────────

def install_playwright(repo_root: Path):
    header("Paso 4 / 6 — Instalar Playwright Chromium")
    warn("Esto descarga ~130 MB. Puede tardar un minuto...")
    venv_py = str(get_venv_python(repo_root))
    info(f"playwright install chromium")
    try:
        run([venv_py, "-m", "playwright", "install", "chromium"])
    except subprocess.CalledProcessError:
        fatal(
            "No se pudo instalar Playwright Chromium.",
            f"Ejecutá manualmente: {venv_py} -m playwright install chromium"
        )
    ok("Playwright Chromium instalado")


# ── Step 5: mcp-mp ────────────────────────────────────────────────────────────

def install_mcp_mp(repo_root: Path):
    header("Paso 5 / 6 — Instalar servidor MCP")
    venv_py = str(get_venv_python(repo_root))
    info('uv pip install --python .venv -e "./mcp-mp[scraper]"')
    try:
        run(["uv", "pip", "install", "--python", venv_py, "-e", str(repo_root / "mcp-mp")])
    except subprocess.CalledProcessError:
        fatal(
            "No se pudo instalar mcp-mercado-publico.",
            "Ejecutá manualmente: uv pip install --python mcp-mp/.venv/Scripts/python.exe -e ./mcp-mp"
        )
    ok("mcp-mercado-publico instalado con soporte de scraper")


# ── Step 6: Claude Desktop config ─────────────────────────────────────────────

def detect_config_paths() -> list[Path]:
    """
    Retorna todas las rutas donde Claude Desktop puede leer su config.

    En Windows hay dos instalaciones posibles:
      - Instalador clásico (.exe): %APPDATA%\\Claude\\
      - Microsoft Store (UWP):    %LOCALAPPDATA%\\Packages\\Claude_*\\LocalCache\\Roaming\\Claude\\

    Escribimos en todas las que encontremos para cubrir ambos casos.
    Si ninguna existe, devolvemos la ruta estándar para crearla.
    """
    if sys.platform == "darwin":
        return [Path.home() / "Library" / "Application Support" / "Claude" / "claude_desktop_config.json"]

    if sys.platform != "win32":
        return [Path.home() / ".config" / "Claude" / "claude_desktop_config.json"]

    paths: list[Path] = []

    # Versión clásica (.exe installer)
    appdata = os.environ.get("APPDATA", "")
    if appdata:
        classic = Path(appdata) / "Claude" / "claude_desktop_config.json"
        if classic.parent.exists():
            paths.append(classic)

    # Versión Microsoft Store (UWP) — el sufijo del paquete puede variar
    localappdata = os.environ.get("LOCALAPPDATA", "")
    if localappdata:
        packages = Path(localappdata) / "Packages"
        if packages.exists():
            for pkg in packages.iterdir():
                if pkg.name.startswith("Claude_"):
                    store_config = pkg / "LocalCache" / "Roaming" / "Claude" / "claude_desktop_config.json"
                    paths.append(store_config)

    # Si no encontramos ninguna instalación existente, usamos la ruta clásica
    if not paths:
        if not appdata:
            fatal(
                "Variable de entorno APPDATA no encontrada.",
                "Definila manualmente antes de ejecutar este script."
            )
        paths.append(Path(appdata) / "Claude" / "claude_desktop_config.json")

    return paths


def ask_ticket() -> str:
    print()
    print(f"  {C.BOLD}Se requiere tu MERCADO_PUBLICO_TICKET.{C.RESET}")
    print(f"  Obtenelo en: {C.CYAN}https://www.mercadopublico.cl{C.RESET} -> Perfil -> API Key")
    while True:
        ticket = input(f"\n  {C.BOLD}Ingresá el MERCADO_PUBLICO_TICKET:{C.RESET} ").strip()
        if ticket:
            return ticket
        warn("El ticket no puede estar vacío. Intentá de nuevo.")


def build_server_entry(repo_root: Path, ticket: str) -> dict:
    venv_py = str(get_venv_python(repo_root).resolve())
    run_script = str((repo_root / "mcp-mp" / "run_stdio.py").resolve())
    return {
        "command": venv_py,
        "args": [run_script],
        "env": {"MERCADO_PUBLICO_TICKET": ticket},
    }


def load_config(path: Path) -> dict:
    if path.exists():
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError:
            backup = path.with_suffix(".json.bak")
            shutil.copy2(path, backup)
            warn(f"Config existente con JSON inválido — backup guardado en {backup.name}")
            return {}
    return {}


def write_config(path: Path, config: dict):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2, ensure_ascii=False)


def configure_claude(repo_root: Path) -> list[Path]:
    header("Paso 6 / 6 — Configurar Claude Desktop")

    config_paths = detect_config_paths()

    if len(config_paths) > 1:
        info(f"Detectadas {len(config_paths)} instalaciones de Claude Desktop:")
        for p in config_paths:
            label = "Store" if "Packages" in str(p) else "Clásico"
            info(f"  [{label}] {p}")
    else:
        info(f"Ruta del config: {config_paths[0]}")
        if not config_paths[0].parent.exists():
            warn("Claude Desktop no parece estar instalado en esta máquina.")
            warn("El config se creará igual — instalá Claude Desktop y reinicialo.")

    ticket = ask_ticket()
    server_entry = build_server_entry(repo_root, ticket)

    print(f"\n  Se agregará/actualizará en {C.CYAN}mcpServers{C.RESET}:\n")
    preview = {"mercado-publico": server_entry}
    for line in json.dumps(preview, indent=4).splitlines():
        print(f"    {line}")

    print()
    confirm = input(f"  {C.BOLD}¿Escribir esto en el config de Claude Desktop? [Y/n]:{C.RESET} ").strip().lower()
    if confirm not in ("", "y", "yes", "s", "si", "sí"):
        warn("Config omitido. Podés configurarlo manualmente luego.")
        return config_paths

    written: list[Path] = []
    for config_path in config_paths:
        config = load_config(config_path)
        config.setdefault("mcpServers", {})

        if "mercado-publico" in config["mcpServers"]:
            warn(f"Ya existe 'mercado-publico' en {config_path.name} — será sobreescrita.")

        otros = [k for k in config["mcpServers"] if k != "mercado-publico"]
        config["mcpServers"]["mercado-publico"] = server_entry

        try:
            write_config(config_path, config)
            label = " (Store)" if "Packages" in str(config_path) else ""
            ok(f"Config escrito{label}: {config_path}")
            if otros:
                ok(f"  Servidores existentes preservados: {otros}")
            written.append(config_path)
        except OSError as e:
            err(f"No se pudo escribir {config_path}: {e}")

    if not written:
        fatal(
            "No se pudo escribir ningún config.",
            "Agregá la entrada manualmente en el config de Claude Desktop."
        )

    return written


# ── Optional: scraper login ───────────────────────────────────────────────────

def offer_login(repo_root: Path):
    header("Opcional — Login del scraper (sesión de navegador)")
    print("  El scraper necesita una sesión guardada para descargar")
    print("  documentos del portal de Mercado Público.")
    print()
    print(f"  {C.CYAN}Se abrirá Chrome -> hacés login -> presionás ENTER{C.RESET}")
    print()
    answer = input(f"  {C.BOLD}¿Ejecutar mp-scraper login ahora? [y/N]:{C.RESET} ").strip().lower()
    if answer not in ("y", "yes", "s", "si", "sí"):
        info("Saltado. Para ejecutarlo luego:")
        info(f"  cd {repo_root / 'scraper'} && uv run mp-scraper login")
        return

    info("Abriendo navegador para login...")
    venv_py = str(get_venv_python(repo_root))
    try:
        subprocess.run([venv_py, "-m", "scraper.cli", "login"], check=True)
        ok("Sesión guardada en ~/.mp-mcp/cookies.json")
    except subprocess.CalledProcessError:
        warn("El login falló o fue cancelado.")
        info(f"Intentalo manualmente: {venv_py} -m scraper.cli login")


# ── Summary ───────────────────────────────────────────────────────────────────

def print_summary(repo_root: Path, config_paths: list[Path]):
    print(f"\n{C.BOLD}{C.GREEN}{'=' * 58}{C.RESET}")
    print(f"{C.BOLD}{C.GREEN}  ¡Instalación completa!{C.RESET}")
    print(f"{C.BOLD}{C.GREEN}{'=' * 58}{C.RESET}\n")

    print("  Qué se hizo:")
    ok("Python 3.11+ verificado")
    ok("uv listo")
    ok("mp-scraper instalado")
    ok("Playwright Chromium instalado")
    ok("mcp-mercado-publico[scraper] instalado")
    ok(f"Claude Desktop configurado")

    print(f"\n  {C.BOLD}Próximos pasos:{C.RESET}")
    info("1. Reiniciá Claude Desktop completamente (cerralo y volvé a abrirlo).")
    info("2. En Claude deberías ver 'mercado-publico' en tus servidores MCP.")
    info("3. La primera vez, configurá el perfil de tu empresa desde Claude:")
    print(f"\n     {C.CYAN}guardar_perfil_proveedor({{\"empresa\": \"...\", \"rut\": \"...\", ...}}){C.RESET}\n")
    info("4. Si saltaste el login del scraper, ejecutalo cuando quieras descargar docs:")
    scraper_dir = (repo_root / "scraper").resolve()
    print(f"\n     {C.CYAN}cd {scraper_dir} && uv run mp-scraper login{C.RESET}\n")


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    if sys.platform == "win32":
        os.system("color")  # habilitar ANSI en cmd.exe de Windows

    print(f"\n{C.BOLD}{C.CYAN}  MCP Mercado Público - Instalador{C.RESET}")
    print(f"  {C.CYAN}Configura tu integración con Claude Desktop{C.RESET}\n")

    repo_root = Path(__file__).resolve().parent

    ensure_uv()
    check_python()
    install_scraper(repo_root)
    install_playwright(repo_root)
    install_mcp_mp(repo_root)
    config_paths = configure_claude(repo_root)
    offer_login(repo_root)
    print_summary(repo_root, config_paths)


if __name__ == "__main__":
    main()
