from domain.licitacion.entities import Licitacion
from domain.licitacion.categories import CategoryFilter


class LicitacionSearchService:

    @staticmethod
    def search_by_nombre(licitaciones: list[Licitacion], query: str) -> list[Licitacion]:
        query_lower = query.lower()
        return [
            l for l in licitaciones
            if (l.Nombre and query_lower in l.Nombre.lower())
            or (l.Descripcion and query_lower in l.Descripcion.lower())
        ]

    @staticmethod
    def search_by_categories(licitaciones: list[Licitacion], prefixes: list[str]) -> list[Licitacion]:
        return [l for l in licitaciones if CategoryFilter.matches_unspsc(l, prefixes)]

    @staticmethod
    def search_software(licitaciones: list[Licitacion]) -> list[Licitacion]:
        return [l for l in licitaciones if CategoryFilter.matches_software(l)]

    @staticmethod
    def search_combined(
        licitaciones: list[Licitacion],
        query: str | None = None,
        prefixes: list[str] | None = None,
    ) -> list[Licitacion]:
        """Filtra por nombre/descripción OR por categorías UNSPSC."""
        result = set()
        if query:
            for l in LicitacionSearchService.search_by_nombre(licitaciones, query):
                result.add(id(l))
        if prefixes:
            for l in LicitacionSearchService.search_by_categories(licitaciones, prefixes):
                result.add(id(l))
        return [l for l in licitaciones if id(l) in result]
