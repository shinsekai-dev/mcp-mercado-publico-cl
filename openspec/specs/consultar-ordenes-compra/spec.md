## ADDED Requirements

### Requirement: Obtener orden de compra por código
El sistema SHALL exponer una tool MCP `obtener_orden_compra(codigo: str)` que retorne el detalle completo de una orden de compra específica. La búsqueda por código no requiere fecha y siempre retorna información detallada.

#### Scenario: Consulta exitosa por código
- **WHEN** el agente invoca `obtener_orden_compra` con un código válido (e.g., `"2097-241-SE14"`)
- **THEN** el servidor retorna un objeto `OrdenCompra` con todos los campos: código, nombre, estado, comprador, proveedor con sucursal, fechas, ítems con precios, descuentos, IVA y total

#### Scenario: Código inexistente
- **WHEN** el agente invoca `obtener_orden_compra` con un código que no existe
- **THEN** el servidor retorna un mensaje de error descriptivo indicando que no se encontró la orden

#### Scenario: Error de conectividad
- **WHEN** la API no está disponible
- **THEN** el servidor retorna un mensaje de error con el detalle del problema de conexión

---

### Requirement: Listar órdenes de compra del día actual
El sistema SHALL exponer una tool MCP `listar_ordenes_hoy()` que retorne todas las órdenes de compra enviadas en el día actual en todos los estados, usando `estado=todos`.

#### Scenario: Listado exitoso del día
- **WHEN** el agente invoca `listar_ordenes_hoy`
- **THEN** el servidor retorna la lista de órdenes del día con información básica (código, nombre, estado, organismo, proveedor, total)

#### Scenario: Sin órdenes en el día
- **WHEN** la API responde con cantidad cero
- **THEN** el servidor retorna lista vacía con mensaje indicando que no hay órdenes para hoy

---

### Requirement: Listar órdenes de compra por fecha
El sistema SHALL exponer una tool MCP `listar_ordenes_por_fecha(fecha: str)` que retorne las órdenes emitidas en un día específico. El parámetro `fecha` debe estar en formato `ddmmaaaa`.

#### Scenario: Consulta exitosa por fecha válida
- **WHEN** el agente invoca `listar_ordenes_por_fecha` con fecha `"02022014"`
- **THEN** el servidor retorna la lista de órdenes emitidas ese día

#### Scenario: Formato de fecha inválido
- **WHEN** el agente pasa una fecha en formato incorrecto
- **THEN** el servidor retorna un error descriptivo indicando que el formato debe ser `ddmmaaaa`

---

### Requirement: Listar órdenes de compra por estado
El sistema SHALL exponer una tool MCP `listar_ordenes_por_estado(estado: str, fecha: str | None)` que filtre órdenes por estado. Estados válidos: `enviadaproveedor`, `aceptada`, `cancelada`, `recepcionconforme`, `pendienterecepcion`, `recepcionaceptadacialmente`, `recepecionconformeincompleta`, `todos`. Si no se provee `fecha`, se usa el día actual.

#### Scenario: Filtro por estado con fecha
- **WHEN** el agente invoca `listar_ordenes_por_estado` con `estado="aceptada"` y `fecha="02022014"`
- **THEN** el servidor retorna solo las órdenes aceptadas en esa fecha

#### Scenario: Filtro por estado sin fecha
- **WHEN** el agente invoca `listar_ordenes_por_estado` con `estado="cancelada"` sin fecha
- **THEN** el servidor retorna las órdenes canceladas del día actual

#### Scenario: Estado inválido
- **WHEN** el agente pasa un estado no reconocido
- **THEN** el servidor retorna un error descriptivo con los estados válidos listados

---

### Requirement: Listar órdenes de compra por organismo público
El sistema SHALL exponer una tool MCP `listar_ordenes_por_organismo(codigo_organismo: str, fecha: str | None)` que retorne las órdenes emitidas por el organismo indicado. Si no se provee `fecha`, se usa el día actual.

#### Scenario: Consulta exitosa por organismo
- **WHEN** el agente invoca `listar_ordenes_por_organismo` con `codigo_organismo="6945"` y una fecha
- **THEN** el servidor retorna las órdenes emitidas por ese organismo en la fecha indicada

#### Scenario: Sin resultados
- **WHEN** el organismo no emitió órdenes en la fecha indicada
- **THEN** el servidor retorna lista vacía con mensaje descriptivo

---

### Requirement: Listar órdenes de compra por proveedor
El sistema SHALL exponer una tool MCP `listar_ordenes_por_proveedor(codigo_proveedor: str, fecha: str | None)` que retorne las órdenes enviadas al proveedor indicado. Si no se provee `fecha`, se usa el día actual.

#### Scenario: Consulta exitosa por proveedor
- **WHEN** el agente invoca `listar_ordenes_por_proveedor` con `codigo_proveedor="17793"` y una fecha
- **THEN** el servidor retorna las órdenes enviadas a ese proveedor en la fecha indicada

---

### Requirement: Entidad de dominio OrdenCompra
El sistema SHALL modelar la entidad `OrdenCompra` con todos los campos del diccionario de datos (Pydantic v2), incluyendo comprador, proveedor con sucursal, fechas, ítems con precios unitarios, descuentos, cargos, IVA y total. Debe tolerar campos extras sin fallar.

#### Scenario: Deserialización desde respuesta JSON detallada (por código)
- **WHEN** la infraestructura recibe la respuesta JSON del endpoint de detalle
- **THEN** se construye una entidad `OrdenCompra` válida con comprador, proveedor e ítems correctamente mapeados

#### Scenario: Deserialización desde respuesta JSON de listado
- **WHEN** la infraestructura recibe una respuesta de listado con información básica
- **THEN** se construyen entidades `OrdenCompra` con los campos disponibles, dejando en `None` los campos no presentes en listados

#### Scenario: Orden sin ítems
- **WHEN** la API retorna una orden con `TieneItems = 0`
- **THEN** la entidad `OrdenCompra` se construye con lista de ítems vacía sin error

---

### Requirement: Descriptions semánticas de todas las tools de órdenes de compra
Cada tool de órdenes de compra SHALL tener nombre y descripción en español que indique claramente su propósito, parámetros y el formato esperado.

#### Scenario: Tools visibles y comprensibles para el agente
- **WHEN** un agente lista las herramientas disponibles del servidor MCP
- **THEN** las 6 tools de órdenes de compra aparecen con descripciones en español, indicando formatos de parámetros y estados válidos
