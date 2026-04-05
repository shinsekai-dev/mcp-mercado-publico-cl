from datetime import datetime, timedelta
from typing import Optional
from domain.licitacion.entities import Licitacion
from domain.licitacion.repository import LicitacionRepository
from domain.licitacion.services import LicitacionSearchService
from domain.licitacion.categories import CategoryFilter, SOFTWARE_UNSPSC_PREFIXES, PERFILES
from infrastructure.mercado_publico_client import validate_fecha

MAX_RANGO_DIAS = 30


class ObtenerLicitacion:
    def __init__(self, repo: LicitacionRepository):
        self._repo = repo

    async def execute(self, codigo: str) -> Licitacion:
        result = await self._repo.get_by_codigo(codigo)
        if result is None:
            raise ValueError(f"No se encontró ninguna licitación con el código '{codigo}'.")
        return result


class ListarLicitacionesHoy:
    def __init__(self, repo: LicitacionRepository):
        self._repo = repo

    async def execute(self) -> list[Licitacion]:
        return await self._repo.list_hoy()


class ListarLicitacionesActivas:
    def __init__(self, repo: LicitacionRepository):
        self._repo = repo

    async def execute(self) -> list[Licitacion]:
        return await self._repo.list_activas()


class ListarLicitacionesPorFecha:
    def __init__(self, repo: LicitacionRepository):
        self._repo = repo

    async def execute(self, fecha: str) -> list[Licitacion]:
        validate_fecha(fecha)
        return await self._repo.list_by_fecha(fecha)


class ListarLicitacionesPorEstado:
    def __init__(self, repo: LicitacionRepository):
        self._repo = repo

    async def execute(self, estado: str, fecha: Optional[str] = None) -> list[Licitacion]:
        return await self._repo.list_by_estado(estado, fecha)


class ListarLicitacionesPorOrganismo:
    def __init__(self, repo: LicitacionRepository):
        self._repo = repo

    async def execute(self, codigo_organismo: str, fecha: Optional[str] = None) -> list[Licitacion]:
        return await self._repo.list_by_organismo(codigo_organismo, fecha)


class ListarLicitacionesPorProveedor:
    def __init__(self, repo: LicitacionRepository):
        self._repo = repo

    async def execute(self, codigo_proveedor: str, fecha: Optional[str] = None) -> list[Licitacion]:
        return await self._repo.list_by_proveedor(codigo_proveedor, fecha)


class BuscarLicitacionesPorNombre:
    def __init__(self, repo: LicitacionRepository):
        self._repo = repo

    async def execute(
        self,
        query: str,
        fecha_inicio: Optional[str] = None,
        fecha_fin: Optional[str] = None,
    ) -> list[Licitacion]:
        if fecha_inicio is None and fecha_fin is None:
            licitaciones = await self._repo.list_activas()
            return LicitacionSearchService.search_by_nombre(licitaciones, query)

        if fecha_inicio is None or fecha_fin is None:
            raise ValueError("Debes proporcionar ambas fechas: fecha_inicio y fecha_fin.")

        validate_fecha(fecha_inicio)
        validate_fecha(fecha_fin)

        inicio = datetime.strptime(fecha_inicio, "%d%m%Y")
        fin = datetime.strptime(fecha_fin, "%d%m%Y")

        if inicio > fin:
            raise ValueError(
                f"fecha_inicio ({fecha_inicio}) no puede ser posterior a fecha_fin ({fecha_fin})."
            )

        delta = (fin - inicio).days + 1
        if delta > MAX_RANGO_DIAS:
            raise ValueError(
                f"El rango de fechas no puede superar {MAX_RANGO_DIAS} días "
                f"(se solicitaron {delta} días). Reduce el rango para evitar exceso de llamadas a la API."
            )

        acumuladas: list[Licitacion] = []
        current = inicio
        while current <= fin:
            fecha_str = current.strftime("%d%m%Y")
            resultados = await self._repo.list_by_fecha(fecha_str)
            acumuladas.extend(resultados)
            current += timedelta(days=1)

        return LicitacionSearchService.search_by_nombre(acumuladas, query)


class BuscarLicitacionesSoftware:
    def __init__(self, repo: LicitacionRepository):
        self._repo = repo

    async def execute(
        self,
        query: Optional[str] = None,
        fecha_inicio: Optional[str] = None,
        fecha_fin: Optional[str] = None,
        perfil: str = "software",
    ) -> list[dict]:
        """
        Busca licitaciones del rubro software/TI.

        Estrategia en dos pasos:
        1. Filtro rápido por nombre/descripción en el listado (sin detalle)
        2. Para las candidatas, aplica filtro por UNSPSC y keywords de categoría

        Retorna lista de dicts con la licitación + score de relevancia.
        """
        prefixes = PERFILES.get(perfil, SOFTWARE_UNSPSC_PREFIXES)

        # Obtener el universo de licitaciones
        if fecha_inicio is None and fecha_fin is None:
            licitaciones = await self._repo.list_activas()
        else:
            if fecha_inicio is None or fecha_fin is None:
                raise ValueError("Debes proporcionar ambas fechas: fecha_inicio y fecha_fin.")
            validate_fecha(fecha_inicio)
            validate_fecha(fecha_fin)
            inicio = datetime.strptime(fecha_inicio, "%d%m%Y")
            fin = datetime.strptime(fecha_fin, "%d%m%Y")
            if inicio > fin:
                raise ValueError("fecha_inicio no puede ser posterior a fecha_fin.")
            delta = (fin - inicio).days + 1
            if delta > MAX_RANGO_DIAS:
                raise ValueError(
                    f"El rango no puede superar {MAX_RANGO_DIAS} días (se solicitaron {delta})."
                )
            licitaciones = []
            current = inicio
            while current <= fin:
                resultados = await self._repo.list_by_fecha(current.strftime("%d%m%Y"))
                licitaciones.extend(resultados)
                current += timedelta(days=1)

        # Primer filtro: keyword en nombre/descripción (siempre útil)
        candidatas = LicitacionSearchService.search_by_nombre(
            licitaciones, query or "software"
        ) if query else licitaciones

        # Segundo filtro: UNSPSC + keywords de categoría + score
        resultados = []
        for lic in candidatas:
            score = CategoryFilter.score_software(lic)
            # Incluir si tiene score > 0 o si pasó el filtro de nombre con query explícito
            if score > 0 or query:
                resultados.append({
                    "score": score,
                    "licitacion": lic,
                })

        # Ordenar por score descendente
        resultados.sort(key=lambda x: x["score"], reverse=True)

        return resultados
