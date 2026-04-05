from __future__ import annotations
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict


class CompradorOC(BaseModel):
    model_config = ConfigDict(extra="allow")

    CodigoOrganismo: Optional[str] = None
    NombreOrganismo: Optional[str] = None
    RutUnidad: Optional[str] = None
    CodigoUnidad: Optional[str] = None
    NombreUnidad: Optional[str] = None
    Actividad: Optional[str] = None
    DireccionUnidad: Optional[str] = None
    ComunaUnidad: Optional[str] = None
    RegionUnidad: Optional[str] = None
    Pais: Optional[str] = None
    NombreContacto: Optional[str] = None
    CargoContacto: Optional[str] = None
    FonoContacto: Optional[str] = None
    MailContacto: Optional[str] = None


class ProveedorOC(BaseModel):
    model_config = ConfigDict(extra="allow")

    Codigo: Optional[str] = None
    Nombre: Optional[str] = None
    Actividad: Optional[str] = None
    CodigoSucursal: Optional[str] = None
    NombreSucursal: Optional[str] = None
    RutSucursal: Optional[str] = None
    Direccion: Optional[str] = None
    Comuna: Optional[str] = None
    Region: Optional[str] = None
    Pais: Optional[str] = None
    NombreContacto: Optional[str] = None
    CargoContacto: Optional[str] = None
    FonoContacto: Optional[str] = None
    MailContacto: Optional[str] = None


class FechasOrdenCompra(BaseModel):
    model_config = ConfigDict(extra="allow")

    FechaCreacion: Optional[datetime] = None
    FechaEnvio: Optional[datetime] = None
    FechaAceptacion: Optional[datetime] = None
    FechaCancelacion: Optional[datetime] = None
    FechaUltimaModificacion: Optional[datetime] = None


class ItemOrdenCompra(BaseModel):
    model_config = ConfigDict(extra="allow")

    Correlativo: Optional[int] = None
    CodigoCategoria: Optional[int] = None
    Categoria: Optional[str] = None
    CodigoProducto: Optional[int] = None
    EspecificacionComprador: Optional[str] = None
    EspecificacionProveedor: Optional[str] = None
    Cantidad: Optional[float] = None
    Moneda: Optional[str] = None
    PrecioNeto: Optional[float] = None
    TotalCargos: Optional[float] = None
    TotalDescuentos: Optional[float] = None
    TotalImpuestos: Optional[float] = None
    Total: Optional[float] = None


class ItemsOrdenCompra(BaseModel):
    model_config = ConfigDict(extra="allow")

    Cantidad: Optional[int] = None
    Listado: Optional[list[ItemOrdenCompra]] = None


class OrdenCompra(BaseModel):
    model_config = ConfigDict(extra="allow")

    Codigo: Optional[str] = None
    Nombre: Optional[str] = None
    CodigoEstado: Optional[int] = None
    CodigoLicitacion: Optional[str] = None
    Descripcion: Optional[str] = None
    CodigoTipo: Optional[str] = None
    Tipo: Optional[str] = None
    TipoMoneda: Optional[str] = None
    CodigoEstadoProveedor: Optional[int] = None
    EstadoProveedor: Optional[str] = None
    Fechas: Optional[FechasOrdenCompra] = None
    TieneItems: Optional[str] = None
    PromedioCalificacion: Optional[float] = None
    CantidadEvaluacion: Optional[int] = None
    Descuentos: Optional[float] = None
    Cargos: Optional[float] = None
    TotalNeto: Optional[float] = None
    PorcentajeIva: Optional[float] = None
    Impuestos: Optional[float] = None
    Total: Optional[float] = None
    Financiamiento: Optional[str] = None
    Pais: Optional[str] = None
    TipoDespacho: Optional[str] = None
    FormaPago: Optional[str] = None
    Comprador: Optional[CompradorOC] = None
    Proveedor: Optional[ProveedorOC] = None
    Items: Optional[ItemsOrdenCompra] = None


# Necesario para resolver forward references cuando los campos tienen
# el mismo nombre que sus tipos (e.g. Comprador, Proveedor, Fechas, Items)
OrdenCompra.model_rebuild()
