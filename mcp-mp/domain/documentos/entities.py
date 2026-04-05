"""Entidades del dominio de documentos de postulación."""

from __future__ import annotations
from enum import Enum
from typing import Optional
from pydantic import BaseModel


class TipoDocumento(str, Enum):
    CARTA_PRESENTACION = "carta_presentacion"
    ANEXO_2_ACEPTACION_BASES = "anexo_2_aceptacion_bases"
    ANEXO_3_CONFLICTO_INTERESES = "anexo_3_conflicto_intereses"
    ANEXO_4_DECLARACION_PROBIDAD = "anexo_4_declaracion_probidad"
    ANEXO_5_DATOS_TRANSFERENCIA = "anexo_5_datos_transferencia"
    ANEXO_7_PACTO_INTEGRIDAD = "anexo_7_pacto_integridad"


CATALOGO_DOCUMENTOS = {
    TipoDocumento.CARTA_PRESENTACION: {
        "nombre": "Carta de Presentación",
        "descripcion": "Carta formal presentando la oferta de la empresa.",
        "campos_requeridos": ["empresa", "rut", "representante_legal", "direccion", "telefono", "email"],
    },
    TipoDocumento.ANEXO_2_ACEPTACION_BASES: {
        "nombre": "Anexo N°2 — Declaración de Aceptación de Bases",
        "descripcion": "Declaración jurada de aceptación de las bases administrativas.",
        "campos_requeridos": ["empresa", "rut", "representante_legal"],
    },
    TipoDocumento.ANEXO_3_CONFLICTO_INTERESES: {
        "nombre": "Anexo N°3 — Declaración de Conflicto de Intereses",
        "descripcion": "Declaración de ausencia de conflicto de intereses con el organismo.",
        "campos_requeridos": ["empresa", "rut", "representante_legal"],
    },
    TipoDocumento.ANEXO_4_DECLARACION_PROBIDAD: {
        "nombre": "Anexo N°4 — Declaración Jurada de Probidad",
        "descripcion": "Declaración jurada simple de probidad y ausencia de inhabilidades.",
        "campos_requeridos": ["empresa", "rut", "representante_legal"],
    },
    TipoDocumento.ANEXO_5_DATOS_TRANSFERENCIA: {
        "nombre": "Anexo N°5 — Datos para Transferencia Electrónica",
        "descripcion": "Datos bancarios para pago de la orden de compra.",
        "campos_requeridos": ["empresa", "rut", "banco", "tipo_cuenta", "numero_cuenta", "email_transferencia"],
    },
    TipoDocumento.ANEXO_7_PACTO_INTEGRIDAD: {
        "nombre": "Anexo N°7 — Pacto de Integridad",
        "descripcion": "Compromiso de no incurrir en actos de cohecho o corrupción.",
        "campos_requeridos": ["empresa", "rut", "representante_legal"],
    },
}
