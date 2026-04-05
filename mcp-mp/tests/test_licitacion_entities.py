import pytest
from domain.licitacion.entities import Licitacion


def test_deserializacion_detallada():
    data = {
        "CodigoExterno": "1509-5-L114",
        "Nombre": "Adquisición de equipos",
        "CodigoEstado": 5,
        "Estado": "Publicada",
        "Descripcion": "Descripción del proceso",
        "Comprador": {
            "CodigoOrganismo": "6945",
            "NombreOrganismo": "Ministerio de Salud",
        },
        "Items": {
            "Cantidad": 1,
            "Listado": [
                {"Correlativo": 1, "NombreProducto": "Notebook", "Cantidad": 10.0}
            ],
        },
    }
    lic = Licitacion.model_validate(data)
    assert lic.CodigoExterno == "1509-5-L114"
    assert lic.Comprador.NombreOrganismo == "Ministerio de Salud"
    assert len(lic.Items.Listado) == 1
    assert lic.Items.Listado[0].NombreProducto == "Notebook"


def test_deserializacion_listado_basico():
    data = {"CodigoExterno": "1234-1-L122", "Nombre": "Servicio de limpieza", "CodigoEstado": 5}
    lic = Licitacion.model_validate(data)
    assert lic.CodigoExterno == "1234-1-L122"
    assert lic.Items is None
    assert lic.Comprador is None


def test_tolerancia_campos_extra():
    data = {
        "CodigoExterno": "9999-1-L122",
        "Nombre": "Test",
        "CampoNuevoDesconocido": "valor_extra",
    }
    lic = Licitacion.model_validate(data)
    assert lic.CodigoExterno == "9999-1-L122"
