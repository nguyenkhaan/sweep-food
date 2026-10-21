"""AI Catalog package providing snapshots, master ingredient indexing, and DB loading."""
# ruff: noqa: N999

from AI.catalog.errors import CatalogNotLoadedError
from AI.catalog.master_index import (
    build_master_alias_index,
    get_effective_codes,
    normalize,
    resolve_pantry_items,
)
from AI.catalog.snapshot import (
    CatalogSnapshot,
    get_catalog_snapshot,
    invalidate_catalog_snapshot,
    load_snapshot,
    load_snapshot_from_bundle,
    warm_up,
)

__all__ = [
    "CatalogNotLoadedError",
    "CatalogSnapshot",
    "build_master_alias_index",
    "get_catalog_snapshot",
    "get_effective_codes",
    "invalidate_catalog_snapshot",
    "load_snapshot",
    "load_snapshot_from_bundle",
    "normalize",
    "resolve_pantry_items",
    "warm_up",
]
