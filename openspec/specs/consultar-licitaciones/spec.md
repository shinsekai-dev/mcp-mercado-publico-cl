## ADDED Requirements

### Requirement: Obtener licitación por código
El sistema SHALL exponer una tool MCP `obtener_licitacion(codigo: str)` que retorne el detalle completo de una licitación específica. La búsqueda por código no requiere fecha y siempre retorna información detallada.

#### Scenario: Consulta exitosa por código
- **WHEN** el agente invoca `obtener_licitacion` con un código válido (e.g., `"1509-5-L114"`)
- **THEN** el servidor retorna un objeto `Licitacion` con todos los campos del diccionario de datos: código externo, nombre, estado, comprador, fechas, ítems con adjudicación por línea y adjudicación global

#### Scenario: Código inexistente
- **WHEN** el agente invoca `obtener_licitacion` con un código que no existe
- **THEN** el servidor retorna un mensaje de error descriptivo indicando que no se encontró la licitación

#### Scenario: Error de conectividad
- **WHEN** la API no está disponible
- **THEN** el servidor retorna un mensaje de error con el detalle del problema de conexión

---

### Requirement: Listar licitaciones del día actual
El sistema SHALL exponer una tool MCP `listar_licitaciones_hoy()` que retorne todas las licitaciones publicadas en el día actual en todos sus estados, usando el endpoint sin parámetro de fecha.

#### Scenario: Listado exitoso del día
- **WHEN** el agente invoca `listar_licitaciones_hoy`
- **THEN** el servidor retorna una lista de licitaciones del día con información básica de cada una (código, nombre, estado, organismo, fecha cierre)

#### Scenario: Sin licitaciones en el día
- **WHEN** la API responde con cantidad cero para el día actual
- **THEN** el servidor retorna una lista vacía con un mensaje indicando que no hay licitaciones para hoy

---

### Requirement: Listar licitaciones activas
El sistema SHALL exponer una tool MCP `listar_licitaciones_activas()` que retorne únicamente las licitaciones en estado publicado/activo al momento de la consulta, usando `estado=activas`.

#### Scenario: Listado de activas exitoso
- **WHEN** el agente invoca `listar_licitaciones_activas`
- **THEN** el servidor retorna la lista de licitaciones actualmente publicadas con código, nombre, fecha de cierre y organismo comprador

---

### Requirement: Listar licitaciones por fecha
El sistema SHALL exponer una tool MCP `listar_licitaciones_por_fecha(fecha: str)` que retorne todas las licitaciones de un día específico. El parámetro `fecha` debe estar en formato `ddmmaaaa`.

#### Scenario: Consulta exitosa por fecha válida
- **WHEN** el agente invoca `listar_licitaciones_por_fecha` con fecha `"02022014"`
- **THEN** el servidor retorna la lista de licitaciones publicadas ese día con información básica

#### Scenario: Formato de fecha inválido
- **WHEN** el agente pasa una fecha en formato incorrecto (e.g., `"2014-02-02"`)
- **THEN** el servidor retorna un error descriptivo indicando que el formato debe ser `ddmmaaaa`

---

### Requirement: Listar licitaciones por estado
El sistema SHALL exponer una tool MCP `listar_licitaciones_por_estado(estado: str, fecha: str | None)` que filtre licitaciones por estado. Estados válidos: `Publicada`, `Cerrada`, `Desierta`, `Adjudicada`, `Revocada`, `Suspendida`, `Todos`. Si no se provee `fecha`, se usa el día actual.

#### Scenario: Filtro por estado con fecha
- **WHEN** el agente invoca `listar_licitaciones_por_estado` con `estado="adjudicada"` y `fecha="02022014"`
- **THEN** el servidor retorna solo las licitaciones adjudicadas en esa fecha

#### Scenario: Filtro por estado sin fecha (día actual)
- **WHEN** el agente invoca `listar_licitaciones_por_estado` con `estado="publicada"` sin especificar fecha
- **THEN** el servidor retorna las licitaciones publicadas hoy

#### Scenario: Estado inválido
- **WHEN** el agente pasa un estado que no existe en la lista de valores válidos
- **THEN** el servidor retorna un error descriptivo con los estados permitidos

---

### Requirement: Listar licitaciones por organismo público
El sistema SHALL exponer una tool MCP `listar_licitaciones_por_organismo(codigo_organismo: str, fecha: str | None)` que retorne las licitaciones del organismo indicado. Si no se provee `fecha`, se usa el día actual.

#### Scenario: Consulta exitosa por organismo
- **WHEN** el agente invoca `listar_licitaciones_por_organismo` con `codigo_organismo="6945"` y una fecha
- **THEN** el servidor retorna las licitaciones publicadas por ese organismo en la fecha indicada

#### Scenario: Sin resultados para el organismo en la fecha
- **WHEN** el organismo no publicó licitaciones en la fecha indicada
- **THEN** el servidor retorna lista vacía con mensaje descriptivo

---

### Requirement: Listar licitaciones por proveedor
El sistema SHALL exponer una tool MCP `listar_licitaciones_por_proveedor(codigo_proveedor: str, fecha: str | None)` que retorne las licitaciones en que participó el proveedor indicado. Si no se provee `fecha`, se usa el día actual.

#### Scenario: Consulta exitosa por proveedor
- **WHEN** el agente invoca `listar_licitaciones_por_proveedor` con `codigo_proveedor="17793"` y una fecha
- **THEN** el servidor retorna las licitaciones asociadas a ese proveedor en la fecha indicada

---

### Requirement: Entidad de dominio Licitacion
El sistema SHALL modelar la entidad `Licitacion` con todos los campos del diccionario de datos (Pydantic v2), incluyendo comprador, fechas, ítems, adjudicación por línea y adjudicación global. Debe tolerar campos extras sin fallar.

#### Scenario: Deserialización desde respuesta JSON detallada (por código)
- **WHEN** la infraestructura recibe la respuesta JSON del endpoint de detalle
- **THEN** se construye una entidad `Licitacion` válida con todos los campos mapeados correctamente

#### Scenario: Deserialización desde respuesta JSON de listado (por fecha/estado/etc.)
- **WHEN** la infraestructura recibe una respuesta de listado con información básica
- **THEN** se construyen entidades `Licitacion` con los campos disponibles, dejando en `None` los campos no presentes en listados

#### Scenario: Tolerancia a campos desconocidos
- **WHEN** la API retorna campos adicionales no documentados
- **THEN** la entidad se construye sin error

---

### Requirement: Buscar licitaciones por nombre con rango de fechas
El sistema SHALL exponer una tool MCP `buscar_licitaciones_por_nombre(query: str, fecha_inicio: str | None, fecha_fin: str | None)` que:
1. Llame a la API para obtener todas las licitaciones del rango de fechas indicado (una llamada por día del rango).
2. Si no se proveen fechas, use `estado=activas` para obtener las licitaciones activas del día actual.
3. Filtre en memoria los resultados, retornando solo las licitaciones cuyo `Nombre` o `Descripcion` contengan el texto `query` (búsqueda case-insensitive).

La API no soporta búsqueda por texto, por lo que el filtrado es responsabilidad del servidor MCP.

#### Scenario: Búsqueda con rango de fechas
- **WHEN** el agente invoca `buscar_licitaciones_por_nombre` con `query="equipos computacionales"`, `fecha_inicio="01032024"` y `fecha_fin="07032024"`
- **THEN** el servidor llama a la API una vez por cada día del rango (7 llamadas), acumula los resultados y retorna solo las licitaciones cuyo nombre o descripción contienen `"equipos computacionales"` (sin distinguir mayúsculas)

#### Scenario: Búsqueda sin fechas — usa activas del día
- **WHEN** el agente invoca `buscar_licitaciones_por_nombre` con `query="servicios de limpieza"` sin fechas
- **THEN** el servidor obtiene las licitaciones activas del día actual (`estado=activas`) y retorna las que coinciden con el texto

#### Scenario: Sin resultados que coincidan
- **WHEN** ninguna licitación en el rango/activas contiene el texto buscado
- **THEN** el servidor retorna lista vacía con mensaje indicando que no se encontraron licitaciones con ese nombre

#### Scenario: Rango de fechas con fecha_inicio posterior a fecha_fin
- **WHEN** el agente pasa `fecha_inicio` posterior a `fecha_fin`
- **THEN** el servidor retorna un error descriptivo indicando que el rango de fechas es inválido

#### Scenario: Rango de fechas mayor a 30 días
- **WHEN** el rango entre `fecha_inicio` y `fecha_fin` supera los 30 días
- **THEN** el servidor retorna un error indicando que el rango máximo permitido es 30 días, para evitar exceso de llamadas a la API

---

### Requirement: Descriptions semánticas de todas las tools de licitaciones
Cada tool de licitaciones SHALL tener nombre y descripción en español que indique claramente su propósito, parámetros y el formato esperado.

#### Scenario: Tools visibles y comprensibles para el agente
- **WHEN** un agente lista las herramientas disponibles del servidor MCP
- **THEN** las 8 tools de licitaciones aparecen con descripciones en español, indicando formatos de parámetros (e.g., fecha en `ddmmaaaa`, estados válidos, límite de rango de fechas)
