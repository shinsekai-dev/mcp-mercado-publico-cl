import pytest
import respx
import httpx
from infrastructure.licitacion_repository import MercadoPublicoLicitacionRepository
from infrastructure.orden_compra_repository import MercadoPublicoOrdenCompraRepository

BASE = "https://api.mercadopublico.cl/servicios/v1/publico"

LIC_DETALLE = {
    "Cantidad": 1,
    "Listado": [{"CodigoExterno": "1509-5-L114", "Nombre": "Adquisición equipos", "CodigoEstado": 5}],
}

OC_DETALLE = {
    "Cantidad": 1,
    "Listado": [{"Codigo": "2097-241-SE14", "Nombre": "OC insumos", "CodigoEstado": 6}],
}

LISTADO_VACIO = {"Cantidad": 0, "Listado": []}


@pytest.fixture(autouse=True)
def set_ticket(monkeypatch):
    monkeypatch.setenv("MERCADO_PUBLICO_TICKET", "ticket-test")


# ─── Licitaciones ─────────────────────────────────────────────────────────────

@respx.mock
async def test_get_licitacion_by_codigo():
    respx.get(f"{BASE}/licitaciones.json").mock(return_value=httpx.Response(200, json=LIC_DETALLE))
    repo = MercadoPublicoLicitacionRepository()
    result = await repo.get_by_codigo("1509-5-L114")
    assert result.CodigoExterno == "1509-5-L114"


@respx.mock
async def test_list_licitaciones_by_fecha():
    respx.get(f"{BASE}/licitaciones.json").mock(return_value=httpx.Response(200, json=LIC_DETALLE))
    repo = MercadoPublicoLicitacionRepository()
    result = await repo.list_by_fecha("01012024")
    assert len(result) == 1


@respx.mock
async def test_list_licitaciones_by_estado():
    respx.get(f"{BASE}/licitaciones.json").mock(return_value=httpx.Response(200, json=LIC_DETALLE))
    repo = MercadoPublicoLicitacionRepository()
    result = await repo.list_by_estado("adjudicada", "01012024")
    assert len(result) == 1


@respx.mock
async def test_list_licitaciones_by_organismo():
    respx.get(f"{BASE}/licitaciones.json").mock(return_value=httpx.Response(200, json=LISTADO_VACIO))
    repo = MercadoPublicoLicitacionRepository()
    result = await repo.list_by_organismo("6945", "01012024")
    assert result == []


@respx.mock
async def test_list_licitaciones_by_proveedor():
    respx.get(f"{BASE}/licitaciones.json").mock(return_value=httpx.Response(200, json=LISTADO_VACIO))
    repo = MercadoPublicoLicitacionRepository()
    result = await repo.list_by_proveedor("17793")
    assert result == []


# ─── Órdenes de Compra ────────────────────────────────────────────────────────

@respx.mock
async def test_get_oc_by_codigo():
    respx.get(f"{BASE}/ordenesdecompra.json").mock(return_value=httpx.Response(200, json=OC_DETALLE))
    repo = MercadoPublicoOrdenCompraRepository()
    result = await repo.get_by_codigo("2097-241-SE14")
    assert result.Codigo == "2097-241-SE14"


@respx.mock
async def test_list_oc_by_fecha():
    respx.get(f"{BASE}/ordenesdecompra.json").mock(return_value=httpx.Response(200, json=OC_DETALLE))
    repo = MercadoPublicoOrdenCompraRepository()
    result = await repo.list_by_fecha("01012024")
    assert len(result) == 1


@respx.mock
async def test_list_oc_by_estado():
    respx.get(f"{BASE}/ordenesdecompra.json").mock(return_value=httpx.Response(200, json=OC_DETALLE))
    repo = MercadoPublicoOrdenCompraRepository()
    result = await repo.list_by_estado("aceptada", "01012024")
    assert len(result) == 1


@respx.mock
async def test_list_oc_by_organismo():
    respx.get(f"{BASE}/ordenesdecompra.json").mock(return_value=httpx.Response(200, json=LISTADO_VACIO))
    repo = MercadoPublicoOrdenCompraRepository()
    result = await repo.list_by_organismo("6945")
    assert result == []


@respx.mock
async def test_list_oc_by_proveedor():
    respx.get(f"{BASE}/ordenesdecompra.json").mock(return_value=httpx.Response(200, json=LISTADO_VACIO))
    repo = MercadoPublicoOrdenCompraRepository()
    result = await repo.list_by_proveedor("17793", "01012024")
    assert result == []
