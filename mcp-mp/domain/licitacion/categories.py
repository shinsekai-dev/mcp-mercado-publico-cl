"""Categorías UNSPSC para filtrado de licitaciones por rubro."""

from domain.licitacion.entities import Licitacion

# Prefijos UNSPSC relevantes para software y servicios TI
# https://www.ungm.org/Public/UNSPSC
SOFTWARE_UNSPSC_PREFIXES = [
    "43",       # Tecnología de la información, transmisión, telecomunicaciones
    "4323",     # Software
    "432300",   # Software (variante de 6 dígitos)
    "81111",    # Servicios de tecnología de la información
    "81112",    # Desarrollo de software
    "811118",   # Desarrollo de aplicaciones
    "8111",     # Servicios informáticos
    "8112",     # Servicios de gestión de sistemas de información
]

# Palabras clave en Categoria/NombreProducto para reforzar el filtro
SOFTWARE_KEYWORDS = [
    "software",
    "desarrollo",
    "aplicaci",     # aplicación / aplicaciones
    "sistema inform",
    "plataforma",
    "tecnolog",
    "informátic",
    "informatica",
    "programaci",
    "base de dato",
    "web",
    "digital",
    "ti ",
    "tic",
]

# Perfiles predefinidos para otros rubros
PERFILES = {
    "software": SOFTWARE_UNSPSC_PREFIXES,
    "construccion": ["72", "73", "7210", "7211"],
    "salud": ["42", "85", "8510", "8511"],
    "consultoria": ["80", "8010", "8011"],
    "educacion": ["86", "8610"],
}


class CategoryFilter:

    @staticmethod
    def matches_unspsc(licitacion: Licitacion, prefixes: list[str]) -> bool:
        """Retorna True si algún item tiene CodigoProducto con prefijo en la lista."""
        if not licitacion.Items or not licitacion.Items.Listado:
            return False
        for item in licitacion.Items.Listado:
            if item.CodigoProducto is not None:
                codigo_str = str(item.CodigoProducto)
                for prefix in prefixes:
                    if codigo_str.startswith(prefix):
                        return True
        return False

    @staticmethod
    def matches_keywords_categoria(licitacion: Licitacion, keywords: list[str]) -> bool:
        """Retorna True si algún item tiene Categoria o NombreProducto con keyword."""
        if not licitacion.Items or not licitacion.Items.Listado:
            return False
        for item in licitacion.Items.Listado:
            texto = " ".join(filter(None, [
                item.Categoria or "",
                item.NombreProducto or "",
                item.Descripcion or "",
            ])).lower()
            for kw in keywords:
                if kw.lower() in texto:
                    return True
        return False

    @staticmethod
    def matches_software(licitacion: Licitacion) -> bool:
        """Retorna True si la licitación parece ser de software/TI."""
        return (
            CategoryFilter.matches_unspsc(licitacion, SOFTWARE_UNSPSC_PREFIXES)
            or CategoryFilter.matches_keywords_categoria(licitacion, SOFTWARE_KEYWORDS)
        )

    @staticmethod
    def score_software(licitacion: Licitacion) -> int:
        """Retorna score de relevancia (0-3) para licitaciones de software."""
        score = 0
        nombre = (licitacion.Nombre or "").lower()
        descripcion = (licitacion.Descripcion or "").lower()

        # +1 si el nombre/descripción contiene keywords
        for kw in SOFTWARE_KEYWORDS:
            if kw in nombre or kw in descripcion:
                score += 1
                break

        # +1 si los items matchean UNSPSC
        if CategoryFilter.matches_unspsc(licitacion, SOFTWARE_UNSPSC_PREFIXES):
            score += 1

        # +1 si los items matchean keywords de categoría
        if CategoryFilter.matches_keywords_categoria(licitacion, SOFTWARE_KEYWORDS):
            score += 1

        return score
