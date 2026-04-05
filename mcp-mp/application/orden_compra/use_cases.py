from typing import Optional
from domain.orden_compra.entities import OrdenCompra
from domain.orden_compra.repository import OrdenCompraRepository
from infrastructure.mercado_publico_client import validate_fecha


class ObtenerOrdenCompra:
    def __init__(self, repo: OrdenCompraRepository):
        self._repo = repo

    async def execute(self, codigo: str) -> OrdenCompra:
        result = await self._repo.get_by_codigo(codigo)
        if result is None:
            raise ValueError(f"No se encontró ninguna orden de compra con el código '{codigo}'.")
        return result


class ListarOrdenesHoy:
    def __init__(self, repo: OrdenCompraRepository):
        self._repo = repo

    async def execute(self) -> list[OrdenCompra]:
        return await self._repo.list_hoy()


class ListarOrdenesPorFecha:
    def __init__(self, repo: OrdenCompraRepository):
        self._repo = repo

    async def execute(self, fecha: str) -> list[OrdenCompra]:
        validate_fecha(fecha)
        return await self._repo.list_by_fecha(fecha)


class ListarOrdenesPorEstado:
    def __init__(self, repo: OrdenCompraRepository):
        self._repo = repo

    async def execute(self, estado: str, fecha: Optional[str] = None) -> list[OrdenCompra]:
        return await self._repo.list_by_estado(estado, fecha)


class ListarOrdenesPorOrganismo:
    def __init__(self, repo: OrdenCompraRepository):
        self._repo = repo

    async def execute(self, codigo_organismo: str, fecha: Optional[str] = None) -> list[OrdenCompra]:
        return await self._repo.list_by_organismo(codigo_organismo, fecha)


class ListarOrdenesPorProveedor:
    def __init__(self, repo: OrdenCompraRepository):
        self._repo = repo

    async def execute(self, codigo_proveedor: str, fecha: Optional[str] = None) -> list[OrdenCompra]:
        return await self._repo.list_by_proveedor(codigo_proveedor, fecha)
