"""Unit tests for the all-in-one FreshCheck seed entrypoint."""

from uuid import UUID

from src.seed_freshness import build_mapping_plan
from src.service.freshcheck_mapping_service import (
    CatalogIngredient,
    FreshCheckIngredientReference,
)


def test_build_mapping_plan_only_accepts_unique_exact_names() -> None:
    """Ambiguous and unmatched catalog names remain out of automatic seed data."""
    catalog_ingredients = (
        CatalogIngredient(UUID("00000000-0000-0000-0000-000000000001"), "Cá hồi"),
        CatalogIngredient(UUID("00000000-0000-0000-0000-000000000002"), "Nấm"),
        CatalogIngredient(UUID("00000000-0000-0000-0000-000000000003"), "Không rõ"),
    )
    freshcheck_ingredients = (
        FreshCheckIngredientReference("FC-SALMON", ("Cá hồi",)),
        FreshCheckIngredientReference("FC-MUSHROOM-A", ("Nấm",)),
        FreshCheckIngredientReference("FC-MUSHROOM-B", ("Nấm",)),
    )

    plan = build_mapping_plan(
        "1.2.3",
        catalog_ingredients,
        freshcheck_ingredients,
    )

    assert plan.mapping_manifest.kb_version == "1.2.3"
    assert [
        (mapping.master_ingredient_id, mapping.freshcheck_ingredient_id)
        for mapping in plan.mapping_manifest.mappings
    ] == [(UUID("00000000-0000-0000-0000-000000000001"), "FC-SALMON")]
    assert plan.ambiguous_count == 1
    assert plan.unmapped_count == 1
