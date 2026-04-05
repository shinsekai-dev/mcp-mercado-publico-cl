## 1. Configuración del proyecto

- [x] 1.1 Crear `pyproject.toml` con dependencias: `mcp`, `fastapi`, `uvicorn`, `httpx`, `pydantic>=2`
- [x] 1.2 Crear estructura de directorios DDD: `domain/licitacion/`, `domain/orden_compra/`, `application/licitacion/`, `application/orden_compra/`, `infrastructure/`, `interfaces/mcp/`
- [x] 1.3 Crear archivos `__init__.py` en cada módulo
- [x] 1.4 Crear `README.md` con instrucciones de instalación y configuración de variables de entorno

## 2. Capa de dominio - Licitacion

- [x] 2.1 Crear entidad `Licitacion` en `domain/licitacion/entities.py` con todos los campos del diccionario de datos (Pydantic v2, campos opcionales para listados básicos)
- [x] 2.2 Crear value objects: `Comprador`, `FechasLicitacion`, `ItemLicitacion`, `AdjudicacionItem`, `AdjudicacionGlobal`
- [x] 2.3 Crear interfaz `LicitacionRepository` en `domain/licitacion/repository.py` con métodos: `get_by_codigo`, `list_by_fecha`, `list_activas`, `list_hoy`, `list_by_estado`, `list_by_organismo`, `list_by_proveedor`
- [x] 2.4 Crear servicio de dominio `LicitacionSearchService` en `domain/licitacion/services.py` con método `search_by_nombre(licitaciones: list[Licitacion], query: str) -> list[Licitacion]` que filtre en memoria (case-insensitive) sobre `Nombre` y `Descripcion`

## 3. Capa de dominio - OrdenCompra

- [x] 3.1 Crear entidad `OrdenCompra` en `domain/orden_compra/entities.py` con todos los campos del diccionario de datos (Pydantic v2, campos opcionales para listados básicos)
- [x] 3.2 Crear value objects: `CompradorOC`, `ProveedorOC`, `FechasOrdenCompra`, `ItemOrdenCompra`
- [x] 3.3 Crear interfaz `OrdenCompraRepository` en `domain/orden_compra/repository.py` con métodos: `get_by_codigo`, `list_hoy`, `list_by_fecha`, `list_by_estado`, `list_by_organismo`, `list_by_proveedor`

## 4. Capa de infraestructura

- [x] 4.1 Crear `infrastructure/mercado_publico_client.py` con cliente `httpx` async que lee `MERCADO_PUBLICO_TICKET` y `MERCADO_PUBLICO_BASE_URL`; incluir helper para validar y construir parámetro `fecha` en formato `ddmmaaaa`
- [x] 4.2 Implementar `infrastructure/licitacion_repository.py` con los 7 métodos del repositorio: detalle por código, listado hoy, activas, por fecha, por estado, por organismo y por proveedor
- [x] 4.3 Implementar `infrastructure/orden_compra_repository.py` con los 6 métodos del repositorio: detalle por código, listado hoy, por fecha, por estado, por organismo y por proveedor
- [x] 4.4 Agregar manejo de errores HTTP (404, 500, timeout) con mensajes descriptivos en ambos repositorios
- [x] 4.5 Agregar validación de parámetro `estado` en ambos repositorios con lista de valores permitidos

## 5. Capa de aplicación

- [x] 5.1 Crear casos de uso de licitaciones en `application/licitacion/use_cases.py`: `ObtenerLicitacion`, `ListarLicitacionesHoy`, `ListarLicitacionesActivas`, `ListarLicitacionesPorFecha`, `ListarLicitacionesPorEstado`, `ListarLicitacionesPorOrganismo`, `ListarLicitacionesPorProveedor`
- [x] 5.3 Crear caso de uso `BuscarLicitacionesPorNombre` en `application/licitacion/use_cases.py` que: valide que el rango no supere 30 días, itere cada día del rango llamando al repositorio, acumule resultados y llame a `LicitacionSearchService.search_by_nombre`; si no hay fechas use `list_activas`
- [x] 5.2 Crear casos de uso de OC en `application/orden_compra/use_cases.py`: `ObtenerOrdenCompra`, `ListarOrdenesHoy`, `ListarOrdenesPorFecha`, `ListarOrdenesPorEstado`, `ListarOrdenesPorOrganismo`, `ListarOrdenesPorProveedor`

## 6. Capa de interfaces MCP

- [x] 6.1 Crear `interfaces/mcp/server.py` con app FastAPI, FastMCP `mercado-publico` montado en `/mcp` y endpoint `GET /health`
- [x] 6.2 Implementar las 8 tools de licitaciones en `interfaces/mcp/tools.py` con descripciones semánticas en español: `obtener_licitacion`, `listar_licitaciones_hoy`, `listar_licitaciones_activas`, `listar_licitaciones_por_fecha`, `listar_licitaciones_por_estado`, `listar_licitaciones_por_organismo`, `listar_licitaciones_por_proveedor`, `buscar_licitaciones_por_nombre`
- [x] 6.3 Implementar las 6 tools de OC en `interfaces/mcp/tools.py` con descripciones semánticas en español: `obtener_orden_compra`, `listar_ordenes_hoy`, `listar_ordenes_por_fecha`, `listar_ordenes_por_estado`, `listar_ordenes_por_organismo`, `listar_ordenes_por_proveedor`
- [x] 6.4 Validar presencia de `MERCADO_PUBLICO_TICKET` al iniciar el servidor y lanzar error descriptivo si no está definido
- [x] 6.5 Crear `__main__.py` que inicie `uvicorn` con la app FastAPI, leyendo el puerto de la variable `PORT` (default 8000)

## 7. Tests

- [x] 7.1 Crear tests unitarios para entidad `Licitacion`: deserialización detallada, deserialización de listado (campos básicos) y tolerancia a campos extra
- [x] 7.2 Crear tests unitarios para entidad `OrdenCompra`: deserialización detallada, listado y caso sin ítems
- [x] 7.3 Crear tests unitarios para los casos de uso de licitaciones con mocks de repositorio (los 7 casos)
- [x] 7.4 Crear tests unitarios para los casos de uso de OC con mocks de repositorio (los 6 casos)
- [x] 7.5 Crear tests de integración para `LicitacionRepository` con respuestas HTTP mockeadas (httpx mock): detalle, listado por fecha, por estado, por organismo y por proveedor
- [x] 7.6 Crear tests de integración para `OrdenCompraRepository` con respuestas HTTP mockeadas: detalle, listado por fecha, por estado, por organismo y por proveedor
- [x] 7.7 Crear tests de validación de parámetros: fecha en formato incorrecto, estado inválido en ambos recursos
- [x] 7.8 Crear tests unitarios para `LicitacionSearchService`: coincidencia en nombre, coincidencia en descripción, sin coincidencias, case-insensitive
- [x] 7.9 Crear tests unitarios para `BuscarLicitacionesPorNombre`: rango válido, rango > 30 días, fecha_inicio > fecha_fin, sin fechas (usa activas)
