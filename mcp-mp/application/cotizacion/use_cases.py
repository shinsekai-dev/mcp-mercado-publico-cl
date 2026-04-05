"""Use cases para generación de cotizaciones."""

import json
from datetime import date
from pathlib import Path
from typing import Optional

from domain.cotizacion.entities import Cotizacion, DatosProveedor, ItemCotizacion
from domain.licitacion.repository import LicitacionRepository
from infrastructure.excel_generator import CotizacionExcelGenerator


class GenerarCotizacionExcel:
    def __init__(self, repo: LicitacionRepository):
        self._repo = repo

    async def execute(
        self,
        codigo: str,
        items_precios: list[dict],
        datos_proveedor: dict,
        output_dir: Optional[str] = None,
    ) -> Path:
        """
        Genera un Excel de cotización para una licitación.

        Args:
            codigo: Código de la licitación
            items_precios: Lista de dicts con correlativo y precio_unitario_neto.
                           Ejemplo: [{"correlativo": 1, "precio_unitario_neto": 150000}]
            datos_proveedor: Dict con empresa, rut, representante_legal, direccion, telefono, email
            output_dir: Directorio de salida (default: ./ofertas/<codigo>/)

        Returns:
            Path al archivo .xlsx generado
        """
        licitacion = await self._repo.get_by_codigo(codigo)
        if licitacion is None:
            raise ValueError(f"No se encontró la licitación '{codigo}'.")

        proveedor = DatosProveedor(**datos_proveedor)

        # Construir mapa de precios por correlativo
        precios_map = {
            int(p["correlativo"]): float(p["precio_unitario_neto"])
            for p in items_precios
        }

        # Construir ítems desde la licitación + precios proporcionados
        items_cotizacion: list[ItemCotizacion] = []
        if licitacion.Items and licitacion.Items.Listado:
            for item in licitacion.Items.Listado:
                correlativo = item.Correlativo or (len(items_cotizacion) + 1)
                precio = precios_map.get(correlativo, 0.0)
                items_cotizacion.append(
                    ItemCotizacion(
                        correlativo=correlativo,
                        descripcion=item.NombreProducto or item.Descripcion or f"Ítem {correlativo}",
                        cantidad=item.Cantidad or 1.0,
                        unidad_medida=item.UnidadMedida or "unidad",
                        precio_unitario_neto=precio,
                    )
                )
        else:
            # Sin ítems en la API, usar los proporcionados directamente
            for p in items_precios:
                items_cotizacion.append(
                    ItemCotizacion(
                        correlativo=int(p["correlativo"]),
                        descripcion=p.get("descripcion", f"Ítem {p['correlativo']}"),
                        cantidad=float(p.get("cantidad", 1)),
                        unidad_medida=p.get("unidad_medida", "unidad"),
                        precio_unitario_neto=float(p["precio_unitario_neto"]),
                    )
                )

        cotizacion = Cotizacion(
            codigo_licitacion=codigo,
            nombre_licitacion=licitacion.Nombre or codigo,
            organismo=(
                licitacion.Comprador.NombreOrganismo
                if licitacion.Comprador else "Organismo no especificado"
            ),
            proveedor=proveedor,
            fecha=date.today(),
            moneda=licitacion.Moneda or "CLP",
            items=items_cotizacion,
            validez_oferta_dias=30,
        )

        # Determinar path de salida
        if output_dir:
            out_path = Path(output_dir) / f"cotizacion_{codigo}.xlsx"
        else:
            out_path = Path("ofertas") / codigo / f"cotizacion_{codigo}.xlsx"

        return CotizacionExcelGenerator.generate(cotizacion, out_path)
