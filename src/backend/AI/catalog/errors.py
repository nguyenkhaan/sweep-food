"""Exceptions for the AI catalog boundary."""


class CatalogNotLoadedError(Exception):
    """Raised when the catalog database is empty or uninitialized."""

    def __init__(
        self,
        message: str = "Catalog is not loaded in the database. Run 'python -m AI.catalog.importer' to populate it.",
    ) -> None:
        super().__init__(message)
