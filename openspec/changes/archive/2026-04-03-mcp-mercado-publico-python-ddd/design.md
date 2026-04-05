## Context

La API de Mercado Público (api.mercadopublico.cl) es una API REST pública de ChileCompra que expone información de licitaciones y órdenes de compra del sistema de compras públicas chileno. No existe actualmente un servidor MCP que permita a agentes de IA consumir esta información de forma nativa.

El proyecto se construye desde cero en Python, aplicando Domain-Driven Design para mantener la lógica de negocio aislada de los detalles de infraestructura (HTTP, serialización) y de la capa MCP.

## Goals / Non-Goals

**Goals:**
- Implementar un servidor MCP en Python con herramientas para consultar licitaciones y órdenes de compra.
- Exponer el servidor MCP mediante transporte HTTP/SSE montado sobre una app FastAPI.
- Aplicar DDD con las capas: `domain`, `application`, `infrastructure`, `interfaces/mcp`.
- Modelar entidades ricas de dominio con Pydantic v2.
- Soportar autenticación mediante ticket de acceso (variable de entorno).
- Cubrir con tests unitarios la capa de dominio y aplicación.

**Non-Goals:**
- Soporte para formatos XML o JSONP (solo JSON).
- Autenticación OAuth o gestión de sesiones.
- Persistencia o caché de datos.
- Endpoints de escritura (la API es solo lectura).
- Búsqueda por criterios distintos al código (la API pública solo soporta código).

## Decisions

### 1. Estructura de directorios DDD

```
mcp-mp/
├── domain/
│   ├── licitacion/
│   │   ├── entities.py        # Licitacion, Item, Adjudicacion, Comprador
│   │   └── repository.py      # LicitacionRepository (interfaz)
│   └── orden_compra/
│       ├── entities.py        # OrdenCompra, Item, Comprador, Proveedor
│       └── repository.py      # OrdenCompraRepository (interfaz)
├── application/
│   ├── licitacion/
│   │   └── use_cases.py       # ConsultarLicitacion
│   └── orden_compra/
│       └── use_cases.py       # ConsultarOrdenCompra
├── infrastructure/
│   ├── mercado_publico_client.py   # Cliente HTTP para la API
│   ├── licitacion_repository.py    # Implementación con API
│   └── orden_compra_repository.py  # Implementación con API
└── interfaces/
    └── mcp/
        ├── server.py          # FastMCP + FastAPI app (mount en /mcp)
        └── tools.py           # Definición de tools MCP
```

**Alternativa considerada**: arquitectura en capas planas (sin DDD). Descartada porque el dominio es rico (múltiples entidades relacionadas) y la separación facilita testing y futuros cambios de infraestructura.

### 2. Transporte MCP: FastMCP montado sobre FastAPI

Se usa `FastMCP` (SDK oficial `mcp` de Anthropic) montado sobre una app `FastAPI` como transporte HTTP/SSE. El servidor MCP queda accesible en `http://localhost:8000/mcp` permitiendo conexiones desde clientes remotos, no solo stdio.

```python
app = FastAPI()
mcp = FastMCP("mercado-publico")
app.mount("/mcp", mcp.get_asgi_app())
```

Se levanta con `uvicorn` como servidor ASGI.

**Alternativa**: transporte stdio puro. Descartada porque la arquitectura HTTP permite conectar múltiples agentes simultáneamente y facilita el despliegue en servidores.

### 3. HTTP Client: `httpx` con async

Se usa `httpx` asíncrono para llamadas a la API, compatible con el loop de eventos de FastMCP.

**Alternativa**: `requests` (síncrono). Descartada para mantener coherencia con el modelo async de MCP.

### 4. Modelos de dominio: Pydantic v2

Las entidades de dominio se modelan con Pydantic v2 para validación y serialización automática. Se usan como Value Objects inmutables.

**Alternativa**: dataclasses puras. Descartada porque Pydantic facilita la deserialización desde JSON de la API y la serialización para respuestas MCP.

### 5. Configuración: variables de entorno

El ticket de acceso se lee de `MERCADO_PUBLICO_TICKET`. Opcional: `MERCADO_PUBLICO_BASE_URL` para sobreescribir la URL base y `PORT` para el puerto HTTP (default `8000`).

## Risks / Trade-offs

- **Disponibilidad de la API** → La API de Mercado Público puede tener downtime o rate limiting no documentado. Mitigación: manejo de errores HTTP con mensajes descriptivos en las tools MCP.
- **Cambios en la API** → La estructura de la respuesta puede cambiar sin aviso. Mitigación: modelos Pydantic con `model_config = ConfigDict(extra='allow')` para no fallar ante campos nuevos.
- **Ticket de acceso requerido** → Sin ticket, las herramientas no funcionan. Mitigación: validar la presencia del ticket al iniciar el servidor y lanzar error descriptivo si no está configurado.
- **API solo soporta búsqueda por código** → No es posible buscar por nombre, estado, etc. con la API pública. Trade-off aceptado: el MCP refleja fielmente las capacidades de la API.
