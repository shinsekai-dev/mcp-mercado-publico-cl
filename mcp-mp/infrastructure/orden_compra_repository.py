from typing import Optional
from domain.orden_compra.entities import OrdenCompra
from domain.orden_compra.repository import OrdenCompraRepository
from infrastructure.mercado_publico_client import (
    fetch_json,
    validate_fecha,
    validate_estado_oc,
)

ENDPOINT = "ordenesdecompra.json"


def _parse_listado(data: dict) -> list[OrdenCompra]:
    listado = data.get("Listado") or []
    return [OrdenCompra.model_validate(item) for item in listado]


class MercadoPublicoOrdenCompraRepository(OrdenCompraRepository):

    async def get_by_codigo(self, codigo: str) -> Optional[OrdenCompra]:
        data = await fetch_json(ENDPOINT, {"codigo": codigo})
        listado = _parse_listado(data)
        return listado[0] if listado else None

    async def list_hoy(self) -> list[OrdenCompra]:
        data = await fetch_json(ENDPOINT, {"estado": "todos"})
        return _parse_listado(data)

    async def list_by_fecha(self, fecha: str) -> list[OrdenCompra]:
        validate_fecha(fecha)
        data = await fetch_json(ENDPOINT, {"fecha": fecha})
        return _parse_listado(data)

    async def list_by_estado(self, estado: str, fecha: Optional[str] = None) -> list[OrdenCompra]:
        estado_norm = validate_estado_oc(estado)
        params: dict = {"estado": estado_norm}
        if fecha:
            validate_fecha(fecha)
            params["fecha"] = fecha
        data = await fetch_json(ENDPOINT, params)
        return _parse_listado(data)

    async def list_by_organismo(self, codigo_organismo: str, fecha: Optional[str] = None) -> list[OrdenCompra]:
        params: dict = {"CodigoOrganismo": codigo_organismo}
        if fecha:
            validate_fecha(fecha)
            params["fecha"] = fecha
        data = await fetch_json(ENDPOINT, params)
        return _parse_listado(data)

    async def list_by_proveedor(self, codigo_proveedor: str, fecha: Optional[str] = None) -> list[OrdenCompra]:
        params: dict = {"CodigoProveedor": codigo_proveedor}
        if fecha:
            validate_fecha(fecha)
            params["fecha"] = fecha
        data = await fetch_json(ENDPOINT, params)
        return _parse_listado(data)
