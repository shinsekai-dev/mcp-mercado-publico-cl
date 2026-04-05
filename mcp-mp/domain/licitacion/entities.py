from __future__ import annotations
from datetime import datetime
from typing import Any, Optional
from pydantic import BaseModel, ConfigDict


class DetallesComprador(BaseModel):
    model_config = ConfigDict(extra="allow")

    CodigoOrganismo: Optional[str] = None
    NombreOrganismo: Optional[str] = None
    RutUnidad: Optional[str] = None
    CodigoUnidad: Optional[str] = None
    NombreUnidad: Optional[str] = None
    DireccionUnidad: Optional[str] = None
    ComunaUnidad: Optional[str] = None
    RegionUnidad: Optional[str] = None
    RutUsuario: Optional[str] = None
    CodigoUsuario: Optional[str] = None
    NombreUsuario: Optional[str] = None
    CargoUsuario: Optional[str] = None


class FechasLicitacion(BaseModel):
    model_config = ConfigDict(extra="allow")

    FechaCreacion: Optional[datetime] = None
    FechaCierre: Optional[datetime] = None
    FechaInicio: Optional[datetime] = None
    FechaFinal: Optional[datetime] = None
    FechaPubRespuestas: Optional[datetime] = None
    FechaActoAperturaTecnica: Optional[datetime] = None
    FechaActoAperturaEconomica: Optional[datetime] = None
    FechaPublicacion: Optional[datetime] = None
    FechaAdjudicacion: Optional[datetime] = None
    FechaEstimadaAdjudicacion: Optional[datetime] = None
    FechaSoporteFisico: Optional[datetime] = None
    FechaTiempoEvaluacion: Optional[datetime] = None
    FechaEstimadaFirma: Optional[datetime] = None
    FechasUsuario: Optional[datetime] = None
    FechaVisitaTerreno: Optional[datetime] = None
    FechaEntregaAntecedentes: Optional[datetime] = None


class AdjudicacionItem(BaseModel):
    model_config = ConfigDict(extra="allow")

    RutProveedor: Optional[str] = None
    NombreProveedor: Optional[str] = None
    CantidadAdjudicada: Optional[str] = None
    MontoUnitario: Optional[float] = None


class ItemLicitacion(BaseModel):
    model_config = ConfigDict(extra="allow")

    CodigoEstadoLicitacion: Optional[int] = None
    Correlativo: Optional[int] = None
    CodigoProducto: Optional[int] = None
    CodigoCategoria: Optional[str] = None
    Categoria: Optional[str] = None
    NombreProducto: Optional[str] = None
    Descripcion: Optional[str] = None
    UnidadMedida: Optional[str] = None
    Cantidad: Optional[float] = None
    Adjudicacion: Optional[AdjudicacionItem] = None


class AdjudicacionGlobal(BaseModel):
    model_config = ConfigDict(extra="allow")

    Tipo: Optional[int] = None
    Fecha: Optional[datetime] = None
    Numero: Optional[str] = None
    NumeroOferentes: Optional[int] = None
    UrlActa: Optional[str] = None


class ItemsLicitacion(BaseModel):
    model_config = ConfigDict(extra="allow")

    Cantidad: Optional[int] = None
    Listado: Optional[list[ItemLicitacion]] = None


class Licitacion(BaseModel):
    model_config = ConfigDict(extra="allow")

    CodigoExterno: Optional[str] = None
    Nombre: Optional[str] = None
    CodigoEstado: Optional[int] = None
    FechaCierre: Optional[datetime] = None
    Descripcion: Optional[str] = None
    Estado: Optional[str] = None
    Comprador: Optional[DetallesComprador] = None
    DiasCierreLicitacion: Optional[int] = None
    Informada: Optional[int] = None
    CodigoTipo: Optional[int] = None
    Tipo: Optional[str] = None
    TipoConvocatoria: Optional[int] = None
    Moneda: Optional[str] = None
    Etapas: Optional[int] = None
    EstadoEtapas: Optional[int] = None
    TomaRazon: Optional[int] = None
    EstadoPublicidadOfertas: Optional[int] = None
    JustificacionPublicidad: Optional[str] = None
    Contrato: Optional[int] = None
    Obras: Optional[int] = None
    CantidadReclamos: Optional[int] = None
    Fechas: Optional[FechasLicitacion] = None
    UnidadTiempoEvaluacion: Optional[int] = None
    DireccionVisita: Optional[str] = None
    DireccionEntrega: Optional[str] = None
    Estimacion: Optional[Any] = None
    FuenteFinanciamiento: Optional[Any] = None
    VisibilidadMonto: Optional[int] = None
    MontoEstimado: Optional[float] = None
    UnidadTiempo: Optional[int] = None
    Modalidad: Optional[int] = None
    TipoPago: Optional[int] = None
    NombreResponsablePago: Optional[str] = None
    EmailResponsablePago: Optional[str] = None
    NombreResponsableContrato: Optional[str] = None
    EmailResponsableContrato: Optional[str] = None
    FonoResponsableContrato: Optional[str] = None
    ProhibicionContratacion: Optional[str] = None
    SubContratacion: Optional[int] = None
    UnidadTiempoDuracionContrato: Optional[int] = None
    TiempoDuracionContrato: Optional[int] = None
    TipoDuracionContrato: Optional[str] = None
    JustificacionMontoEstimado: Optional[str] = None
    ExtensionPlazo: Optional[int] = None
    EsBaseTipo: Optional[int] = None
    UnidadTiempoContratoLicitacion: Optional[int] = None
    ValorTiempoRenovacion: Optional[int] = None
    PeriodoTiempoRenovacion: Optional[str] = None
    EsRenovable: Optional[int] = None
    Adjudicacion: Optional[AdjudicacionGlobal] = None
    Items: Optional[ItemsLicitacion] = None


# Necesario para resolver forward references cuando los campos tienen
# el mismo nombre que sus tipos (e.g. Comprador, Fechas, Items, Adjudicacion)
Licitacion.model_rebuild()
