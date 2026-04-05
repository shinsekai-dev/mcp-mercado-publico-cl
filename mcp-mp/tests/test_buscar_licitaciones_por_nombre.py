import pytest
from unittest.mock import AsyncMock
from domain.licitacion.entities import Licitacion
from application.licitacion.use_cases import BuscarLicitacionesPorNombre


def _lic(nombre: str) -> Licitacion:
    return Licitacion.model_validate({"Nombre": nombre})


@pytest.fixture
def repo():
    return AsyncMock()


async def test_sin_fechas_usa_activas(repo):
    repo.list_activas.return_value = [_lic("Notebook HP"), _lic("Silla ergonómica")]
    result = await BuscarLicitacionesPorNombre(repo).execute("notebook")
    repo.list_activas.assert_called_once()
    assert len(result) == 1


async def test_con_rango_valido(repo):
    repo.list_by_fecha.return_value = [_lic("Papel A4")]
    result = await BuscarLicitacionesPorNombre(repo).execute("papel", "01032024", "03032024")
    assert repo.list_by_fecha.call_count == 3
    assert len(result) == 3


async def test_rango_mayor_30_dias(repo):
    with pytest.raises(ValueError, match="30 días"):
        await BuscarLicitacionesPorNombre(repo).execute("x", "01012024", "15022024")


async def test_fecha_inicio_posterior_a_fin(repo):
    with pytest.raises(ValueError, match="posterior"):
        await BuscarLicitacionesPorNombre(repo).execute("x", "10032024", "01032024")


async def test_solo_una_fecha_lanza_error(repo):
    with pytest.raises(ValueError, match="ambas fechas"):
        await BuscarLicitacionesPorNombre(repo).execute("x", fecha_inicio="01032024")
