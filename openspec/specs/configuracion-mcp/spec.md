## ADDED Requirements

### Requirement: Configuración del ticket de acceso via variable de entorno
El sistema SHALL leer el ticket de acceso a la API de Mercado Público desde la variable de entorno `MERCADO_PUBLICO_TICKET` al iniciar el servidor MCP.

#### Scenario: Servidor inicia con ticket configurado
- **WHEN** la variable de entorno `MERCADO_PUBLICO_TICKET` está definida con un valor no vacío al iniciar el servidor
- **THEN** el servidor inicia correctamente y todas las tools pueden usar el ticket para autenticarse con la API

#### Scenario: Servidor inicia sin ticket configurado
- **WHEN** la variable de entorno `MERCADO_PUBLICO_TICKET` no está definida o está vacía al iniciar el servidor
- **THEN** el servidor lanza un error descriptivo indicando que se requiere configurar `MERCADO_PUBLICO_TICKET`

### Requirement: URL base de la API configurable
El sistema SHALL usar `http://api.mercadopublico.cl/servicios/v1/publico` como URL base por defecto, con posibilidad de sobreescribirla mediante la variable de entorno `MERCADO_PUBLICO_BASE_URL`.

#### Scenario: Uso de URL base por defecto
- **WHEN** la variable `MERCADO_PUBLICO_BASE_URL` no está definida
- **THEN** el servidor usa `http://api.mercadopublico.cl/servicios/v1/publico` como URL base para todas las llamadas a la API

#### Scenario: Sobreescritura de URL base
- **WHEN** la variable `MERCADO_PUBLICO_BASE_URL` está definida con una URL alternativa
- **THEN** el servidor usa esa URL para todas las llamadas, permitiendo apuntar a entornos de prueba

### Requirement: Nombre e identificador del servidor MCP
El sistema SHALL registrar el servidor MCP con el nombre `mercado-publico` y una descripción en español que indique su propósito.

#### Scenario: Servidor identificable por agentes
- **WHEN** un cliente MCP se conecta al servidor
- **THEN** el servidor se identifica con nombre `mercado-publico` y descripción `"Servidor MCP para consultar licitaciones y órdenes de compra de la API de Mercado Público de ChileCompra"`

### Requirement: Transporte HTTP/SSE via FastAPI
El sistema SHALL exponer el servidor MCP mediante una app FastAPI con FastMCP montado en la ruta `/mcp`, accesible por HTTP/SSE. El servidor ASGI SHALL iniciarse con `uvicorn`.

#### Scenario: Cliente conecta al servidor MCP por HTTP
- **WHEN** un cliente MCP se conecta a `http://localhost:<PORT>/mcp`
- **THEN** el cliente puede listar las tools disponibles y ejecutarlas usando el protocolo MCP sobre HTTP/SSE

#### Scenario: Puerto configurable
- **WHEN** la variable de entorno `PORT` está definida
- **THEN** el servidor escucha en ese puerto; si no está definida, usa el puerto `8000` por defecto

#### Scenario: Ruta de salud del servidor FastAPI
- **WHEN** un cliente HTTP hace GET a `http://localhost:<PORT>/health`
- **THEN** el servidor retorna `{"status": "ok"}` con código HTTP 200
