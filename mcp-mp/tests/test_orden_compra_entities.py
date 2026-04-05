import pytest
from domain.orden_compra.entities import OrdenCompra


def test_deserializacion_detallada():
    data = {
        "Codigo": "2097-241-SE14",
        "Nombre": "Compra de insumos",
        "CodigoEstado": 6,
        "Comprador": {"CodigoOrganismo": "6945", "NombreOrganismo": "Ministerio de Educación"},
        "Proveedor": {"Codigo": "17793", "Nombre": "Proveedor SA", "RutSucursal": "12345678-9"},
        "Items": {
            "Cantidad": 2,
            "Listado": [
                {"Correlativo": 1, "PrecioNeto": 1000.0, "Cantidad": 5.0, "Total": 5000.0},
                {"Correlativo": 2, "PrecioNeto": 2000.0, "Cantidad": 3.0, "Total": 6000.0},
            ],
        },
        "Total": 11000.0,
    }
    oc = OrdenCompra.model_validate(data)
    assert oc.Codigo == "2097-241-SE14"
    assert oc.Proveedor.Nombre == "Proveedor SA"
    assert len(oc.Items.Listado) == 2
    assert oc.Total == 11000.0


def test_deserializacion_listado_basico():
    data = {"Codigo": "111-1-SE14", "Nombre": "OC simple", "CodigoEstado": 4}
    oc = OrdenCompra.model_validate(data)
    assert oc.Codigo == "111-1-SE14"
    assert oc.Items is None


def test_orden_sin_items():
    data = {"Codigo": "222-1-SE14", "Nombre": "Sin items", "TieneItems": "0"}
    oc = OrdenCompra.model_validate(data)
    assert oc.TieneItems == "0"
    assert oc.Items is None
