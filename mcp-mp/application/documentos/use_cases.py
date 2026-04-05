"""Use cases para generación de documentos de postulación."""

from pathlib import Path
from typing import Optional

from domain.documentos.entities import TipoDocumento, CATALOGO_DOCUMENTOS
from domain.licitacion.repository import LicitacionRepository
from infrastructure.docx_generator import DocumentoGenerator
from infrastructure import brand


class ListarTiposDocumentos:
    def execute(self) -> list[dict]:
        return [
            {
                "tipo": tipo.value,
                "nombre": info["nombre"],
                "descripcion": info["descripcion"],
                "campos_requeridos": info["campos_requeridos"],
            }
            for tipo, info in CATALOGO_DOCUMENTOS.items()
        ]


class GenerarDocumento:
    def __init__(self, repo: LicitacionRepository):
        self._repo = repo

    async def execute(
        self,
        tipo: str,
        codigo: str,
        datos_proveedor: dict,
        output_dir: Optional[str] = None,
    ) -> Path:
        tipo_enum = TipoDocumento(tipo)

        licitacion = await self._repo.get_by_codigo(codigo)
        if licitacion is None:
            raise ValueError(f"No se encontró la licitación '{codigo}'.")

        nombre_lic = licitacion.Nombre or codigo
        organismo = (
            licitacion.Comprador.NombreOrganismo
            if licitacion.Comprador else "Organismo no especificado"
        )

        # Completar con defaults de marca si faltan campos
        datos = {**brand.get_datos_proveedor(), **datos_proveedor}

        out_dir = Path(output_dir) if output_dir else Path("ofertas") / codigo / "documentos_postulacion"
        filename = f"{tipo_enum.value}.docx"

        return DocumentoGenerator.generar(
            tipo=tipo_enum,
            datos=datos,
            codigo=codigo,
            nombre_licitacion=nombre_lic,
            organismo=organismo,
            output_path=out_dir / filename,
        )


class GenerarTodosDocumentos:
    def __init__(self, repo: LicitacionRepository):
        self._repo = repo

    async def execute(
        self,
        codigo: str,
        datos_proveedor: dict,
        output_dir: Optional[str] = None,
    ) -> list[Path]:
        licitacion = await self._repo.get_by_codigo(codigo)
        if licitacion is None:
            raise ValueError(f"No se encontró la licitación '{codigo}'.")

        nombre_lic = licitacion.Nombre or codigo
        organismo = (
            licitacion.Comprador.NombreOrganismo
            if licitacion.Comprador else "Organismo no especificado"
        )

        datos = {**brand.get_datos_proveedor(), **datos_proveedor}

        out_dir = Path(output_dir) if output_dir else Path("ofertas") / codigo / "documentos_postulacion"

        return DocumentoGenerator.generar_todos(
            datos=datos,
            codigo=codigo,
            nombre_licitacion=nombre_lic,
            organismo=organismo,
            output_dir=out_dir,
        )
