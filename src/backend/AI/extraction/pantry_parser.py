"""Pantry entity resolution and enrichment parser using Catalog master index.

Re-exports and wraps the canonical AI.smart_parser.PantryParser for backwards compatibility.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Protocol

from AI.smart_parser.parser import PantryParser


class PantryItemMatcher(Protocol):
    """Protocol for resolving and enriching extracted items against master catalog."""

    def resolve_master_ingredient(
        self, query: str
    ) -> dict[str, Any] | None:
        """Resolve a free-text name to master catalog details."""
        ...

    def enrich_item(self, raw_item: dict[str, Any]) -> dict[str, Any]:
        """Enrich extracted entity with master code, category, nutrition, and staple flags."""
        ...


class CatalogPantryParser(PantryParser):
    """Matches raw food names to master ingredients and enriches pantry items.

    Inherits from the canonical AI.smart_parser.PantryParser.
    """

    def __init__(
        self,
        master_alias_index: (
            Mapping[str, tuple[str, ...] | list[str] | set[str]] | None
        ) = None,
        master_by_code: Mapping[str, dict[str, Any]] | None = None,
    ) -> None:
        super().__init__(
            master_alias_index=master_alias_index,
            master_by_code=master_by_code,
        )
