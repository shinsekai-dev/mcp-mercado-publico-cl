import os
from dotenv import load_dotenv

# Load .env file before importing our app code
load_dotenv()

from infrastructure.mercado_publico_client import get_ticket
from interfaces.mcp.server import mcp
from interfaces.mcp import tools  # noqa: F401 — registra los tools en mcp

if __name__ == "__main__":
    get_ticket()  # falla rápido si no está configurado el ticket
    mcp.run(transport="stdio")
