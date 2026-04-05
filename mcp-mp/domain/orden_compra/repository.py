from abc import ABC, abstractmethod
from typing import Optional
from domain.orden_compra.entities import OrdenCompra


class OrdenCompraRepository(ABC):

    @abstractmethod
    async def get_by_codigo(self, codigo: str) -> Optional[OrdenCompra]:
        ...

    @abstractmethod
    async def list_hoy(self) -> list[OrdenCompra]:
        ...

    @abstractmethod
    async def list_by_fecha(self, fecha: str) -> list[OrdenCompra]:
        ...

    @abstractmethod
    async def list_by_estado(self, estado: str, fecha: Optional[str] = None) -> list[OrdenCompra]:
        ...

    @abstractmethod
    async def list_by_organismo(self, codigo_organismo: str, fecha: Optional[str] = None) -> list[OrdenCompra]:
        ...

    @abstractmethod
    async def list_by_proveedor(self, codigo_proveedor: str, fecha: Optional[str] = None) -> list[OrdenCompra]:
        ...
