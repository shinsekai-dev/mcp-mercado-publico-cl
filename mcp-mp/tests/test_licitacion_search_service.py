import pytest
from domain.licitacion.entities import Licitacion
from domain.licitacion.services import LicitacionSearchService


def _lic(nombre: str, descripcion: str = "") -> Licitacion:
    return Licitacion.model_validate({"Nombre": nombre, "Descripcion": descripcion})


def test_coincidencia_en_nombre():
    lics = [_lic("Adquisición de notebooks"), _lic("Servicio de aseo")]
    result = LicitacionSearchService.search_by_nombre(lics, "notebooks")
    assert len(result) == 1
    assert result[0].Nombre == "Adquisición de notebooks"


def test_coincidencia_en_descripcion():
    lics = [_lic("Licitación general", "Incluye equipos computacionales"), _lic("Otra licitación")]
    result = LicitacionSearchService.search_by_nombre(lics, "computacionales")
    assert len(result) == 1


def test_sin_coincidencias():
    lics = [_lic("Servicio de limpieza"), _lic("Reparación de vehículos")]
    result = LicitacionSearchService.search_by_nombre(lics, "notebook")
    assert result == []


def test_case_insensitive():
    lics = [_lic("ADQUISICIÓN DE NOTEBOOKS")]
    result = LicitacionSearchService.search_by_nombre(lics, "notebooks")
    assert len(result) == 1


def test_multiple_coincidencias():
    lics = [_lic("Compra de papel"), _lic("Papel higiénico"), _lic("Otro servicio")]
    result = LicitacionSearchService.search_by_nombre(lics, "papel")
    assert len(result) == 2
