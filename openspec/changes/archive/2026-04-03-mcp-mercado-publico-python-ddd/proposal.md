## Why

La API pública de Mercado Público (api.mercadopublico.cl) expone información de licitaciones y órdenes de compra del sistema de compras públicas de Chile, pero no existe una interfaz MCP que permita a agentes de IA consumir esta información de forma estructurada. Se necesita un servidor MCP en Python con arquitectura DDD para exponer estas capacidades a modelos de lenguaje.

## What Changes

- Crear un servidor MCP en Python que exponga **13 herramientas** para consultar y listar licitaciones y órdenes de compra de la API de Mercado Público.
- Implementar arquitectura DDD (Domain-Driven Design) con capas: dominio, aplicación, infraestructura e interfaces.
- Exponer tools MCP para obtener detalle de licitación/OC por código, listar por fecha, por estado, por organismo y por proveedor.
- Gestionar autenticación mediante ticket de acceso configurable.
- Exponer el servidor MCP via HTTP/SSE montado sobre FastAPI.
- Modelar entidades de dominio ricas: `Licitacion`, `OrdenCompra`, `Comprador`, `Proveedor`, `Item`, `Adjudicacion`.

## Capabilities

### New Capabilities
- `consultar-licitaciones`: 8 tools para licitaciones — obtener por código, listar hoy, listar activas, listar por fecha, por estado, por organismo, por proveedor y buscar por nombre con rango de fechas (filtro en memoria).
- `consultar-ordenes-compra`: 6 tools para órdenes de compra — obtener por código, listar hoy, listar por fecha, por estado, por organismo y por proveedor.
- `configuracion-mcp`: Gestión de configuración del servidor MCP (ticket de acceso, URL base, puerto, transporte FastAPI).

### Modified Capabilities
<!-- No hay capacidades existentes que cambien -->

## Impact

- **Nuevo proyecto Python**: estructura de directorios con DDD (`domain/`, `application/`, `infrastructure/`, `interfaces/`).
- **Dependencias**: `mcp`, `fastapi`, `uvicorn`, `httpx`, `pydantic>=2`.
- **Configuración**: variables de entorno `MERCADO_PUBLICO_TICKET`, `MERCADO_PUBLICO_BASE_URL`, `PORT`.
- **API externa**: `api.mercadopublico.cl/servicios/v1/publico/licitaciones.json` y `api.mercadopublico.cl/servicios/v1/publico/ordenesdecompra.json`.
