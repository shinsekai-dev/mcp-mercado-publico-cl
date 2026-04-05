"""Entidades del dominio de cotización."""

from __future__ import annotations
from datetime import date
from typing import Optional
from pydantic import BaseModel, field_validator


class DatosProveedor(BaseModel):
    empresa: str
    rut: str
    representante_legal: str
    direccion: str
    telefono: str
    email: str
    giro: Optional[str] = None


class ItemCotizacion(BaseModel):
    correlativo: int
    descripcion: str
    cantidad: float
    unidad_medida: str
    precio_unitario_neto: float

    @property
    def precio_total_neto(self) -> float:
        return round(self.cantidad * self.precio_unitario_neto, 2)


class Cotizacion(BaseModel):
    codigo_licitacion: str
    nombre_licitacion: str
    organismo: str
    proveedor: DatosProveedor
    fecha: date
    moneda: str = "CLP"
    items: list[ItemCotizacion]
    validez_oferta_dias: int = 30
    observaciones: Optional[str] = None

    @property
    def subtotal_neto(self) -> float:
        return round(sum(i.precio_total_neto for i in self.items), 2)

    @property
    def iva(self) -> float:
        return round(self.subtotal_neto * 0.19, 2)

    @property
    def total(self) -> float:
        return round(self.subtotal_neto + self.iva, 2)
