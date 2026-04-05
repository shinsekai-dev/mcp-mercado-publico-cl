import pytest
from infrastructure.mercado_publico_client import (
    validate_fecha,
    validate_estado_licitacion,
    validate_estado_oc,
)


def test_fecha_valida():
    assert validate_fecha("02022014") == "02022014"


def test_fecha_formato_incorrecto_guiones():
    with pytest.raises(ValueError, match="ddmmaaaa"):
        validate_fecha("2014-02-02")


def test_fecha_formato_incorrecto_longitud():
    with pytest.raises(ValueError, match="ddmmaaaa"):
        validate_fecha("0202")


def test_estado_licitacion_valido():
    assert validate_estado_licitacion("Adjudicada") == "adjudicada"
    assert validate_estado_licitacion("TODOS") == "todos"


def test_estado_licitacion_invalido():
    with pytest.raises(ValueError, match="Estado inválido"):
        validate_estado_licitacion("inexistente")


def test_estado_oc_valido():
    assert validate_estado_oc("aceptada") == "aceptada"
    assert validate_estado_oc("TODOS") == "todos"


def test_estado_oc_invalido():
    with pytest.raises(ValueError, match="Estado inválido"):
        validate_estado_oc("inexistente")
