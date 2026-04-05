"""Gestión de almacenamiento y organización de archivos."""

import json
from datetime import datetime
from pathlib import Path
from typing import Optional, Any

from rich.console import Console

from .config import get_download_dir, ensure_dir

console = Console()


class LicitacionStorage:
    """Organiza los archivos de una licitación en estructura estándar."""

    def __init__(self, base_dir: Optional[Path] = None):
        self.base_dir = base_dir or get_download_dir()
        ensure_dir(self.base_dir)

    def get_licitacion_dir(self, codigo: str) -> Path:
        """Obtiene el directorio base para una licitación."""
        # Limpiar código para usar como nombre de directorio
        safe_codigo = codigo.replace("/", "-").replace("\\", "-")
        lic_dir = self.base_dir / safe_codigo
        return ensure_dir(lic_dir)

    def get_documentos_dir(self, codigo: str) -> Path:
        """Obtiene el subdirectorio para documentos."""
        doc_dir = self.get_licitacion_dir(codigo) / "documentos"
        return ensure_dir(doc_dir)

    def save_metadata(self, codigo: str, metadata: dict[str, Any]):
        """Guarda metadata de la licitación en JSON."""
        lic_dir = self.get_licitacion_dir(codigo)
        metadata_file = lic_dir / "metadata.json"

        # Agregar timestamp
        metadata["scraped_at"] = datetime.now().isoformat()
        metadata["codigo"] = codigo

        with open(metadata_file, "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)

        console.print(f"[dim][SAVE] Metadata guardada en {metadata_file}[/dim]")

    def load_metadata(self, codigo: str) -> Optional[dict]:
        """Carga metadata de una licitación."""
        metadata_file = self.get_licitacion_dir(codigo) / "metadata.json"
        if metadata_file.exists():
            with open(metadata_file, "r", encoding="utf-8") as f:
                return json.load(f)
        return None

    def save_resumen(self, codigo: str, texto: str):
        """Guarda el resumen de documentos en markdown."""
        lic_dir = self.get_licitacion_dir(codigo)
        resumen_file = lic_dir / "resumen_licitacion.md"

        header = f"""# Resumen de Licitación: {codigo}

**Fecha de extracción:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

---

"""

        resumen_file.write_text(header + texto, encoding="utf-8")
        console.print(f"[green][OK][/green] Resumen guardado en {resumen_file}")

    def create_template_oferta(
        self, codigo: str, info_licitacion: Optional[dict] = None
    ):
        """Crea un template para preparar la oferta."""
        lic_dir = self.get_licitacion_dir(codigo)
        template_file = lic_dir / "template_oferta.md"

        # Obtener información básica si está disponible
        nombre = (
            info_licitacion.get("Nombre", "[Nombre de la licitación]")
            if info_licitacion
            else "[Nombre de la licitación]"
        )
        organismo = (
            info_licitacion.get("Comprador", {}).get("NombreOrganismo", "[Organismo]")
            if info_licitacion
            else "[Organismo]"
        )

        template = f"""# Propuesta de Oferta: {codigo}

## Información General

- **Código:** {codigo}
- **Nombre:** {nombre}
- **Organismo:** {organismo}
- **Fecha de preparación:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

## Documentos Consultados

- [ ] Bases Administrativas
- [ ] Especificaciones Técnicas
- [ ] Anexos requeridos
- [ ] Condiciones comerciales

## Análisis de Requerimientos

### 1. Alcance del Servicio/Producto
_Describir aquí el alcance según las bases..._

### 2. Requisitos Técnicos
_Listar requisitos técnicos encontrados en documentos..._

### 3. Requisitos Administrativos
- [ ] Anexo N° 1: Identificación del Proponente
- [ ] Anexo N° 2: Declaración de Aceptación de Bases
- [ ] Anexo N° 3: Declaración Conflicto de Intereses
- [ ] Anexo N° 4: Declaración Jurada de Probidad
- [ ] Anexo N° 5: Datos para Transferencia Electrónica
- [ ] Anexo N° 6: Trazabilidad (si aplica)
- [ ] Anexo N° 7: Pacto de Integridad
- [ ] Carta de Presentación

### 4. Criterios de Evaluación
_Describir ponderación y criterios..._

### 5. Plazos Importantes
- Fecha de cierre:
- Plazo de entrega:
- Vigencia de oferta:

## Propuesta Técnica

### Descripción de la Solución
_Describir la solución propuesta..._

### Ventajas Competitivas
- Ventaja 1
- Ventaja 2
- Ventaja 3

### Experiencia Relevante
_Listar proyectos similares realizados..._

## Propuesta Económica

| Ítem | Descripción | Cantidad | Precio Unitario | Total |
|------|-------------|----------|-----------------|-------|
| 1 | | | | |
| 2 | | | | |
| **TOTAL** | | | | |

## Documentos a Adjuntar

- [ ] Carta de presentación
- [ ] Anexos firmados digitalmente
- [ ] Certificaciones requeridas
- [ ] Fichas técnicas de productos
- [ ] Cotización detallada

## Notas y Observaciones

_Agregar cualquier nota importante, preguntas pendientes, o consideraciones especiales..._

---

**Estado:** [ ] Borrador | [ ] En revisión | [ ] Listo para enviar

**Responsable:** _________________

**Fecha límite de envío:** _________________
"""

        template_file.write_text(template, encoding="utf-8")
        console.print(f"[green][OK][/green] Template de oferta creado en {template_file}")
        return template_file

    def get_estadisticas(self, codigo: str) -> dict:
        """Obtiene estadísticas de archivos descargados."""
        lic_dir = self.get_licitacion_dir(codigo)
        doc_dir = lic_dir / "documentos"

        stats = {
            "codigo": codigo,
            "directorio": str(lic_dir),
            "total_documentos": 0,
            "tipos_archivo": {},
            "total_bytes": 0,
        }

        if doc_dir.exists():
            for f in doc_dir.iterdir():
                if f.is_file():
                    stats["total_documentos"] += 1
                    stats["total_bytes"] += f.stat().st_size
                    ext = f.suffix.lower()
                    stats["tipos_archivo"][ext] = stats["tipos_archivo"].get(ext, 0) + 1

        return stats
