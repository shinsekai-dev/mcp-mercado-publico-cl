from abc import ABC, abstractmethod
from typing import Optional
from domain.licitacion.entities import Licitacion


class LicitacionRepository(ABC):

    @abstractmethod
    async def get_by_codigo(self, codigo: str) -> Optional[Licitacion]:
        ...

    @abstractmethod
    async def list_hoy(self) -> list[Licitacion]:
        ...

    @abstractmethod
    async def list_activas(self) -> list[Licitacion]:
        ...

    @abstractmethod
    async def list_by_fecha(self, fecha: str) -> list[Licitacion]:
        ...

    @abstractmethod
    async def list_by_estado(self, estado: str, fecha: Optional[str] = None) -> list[Licitacion]:
        ...

    @abstractmethod
    async def list_by_organismo(self, codigo_organismo: str, fecha: Optional[str] = None) -> list[Licitacion]:
        ...

    @abstractmethod
    async def list_by_proveedor(self, codigo_proveedor: str, fecha: Optional[str] = None) -> list[Licitacion]:
        ...
