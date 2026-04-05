from fastapi import FastAPI
from mcp.server.fastmcp import FastMCP
from infrastructure.mercado_publico_client import get_ticket

mcp = FastMCP(
    "mercado-publico",
    instructions="Servidor MCP para consultar licitaciones y órdenes de compra de la API de Mercado Público de ChileCompra.",
)

app = FastAPI(title="MCP Mercado Público")


@app.get("/health")
async def health():
    return {"status": "ok"}


def create_app() -> FastAPI:
    # Valida el ticket al arrancar (lanza RuntimeError si no está configurado)
    get_ticket()

    from interfaces.mcp import tools  # noqa: F401 — registra los tools en mcp

    app.mount("/mcp", mcp.get_asgi_app())
    return app
