"""Unit tests for the all-in-one FreshCheck seed entrypoint."""

from types import SimpleNamespace
from uuid import UUID

import pytest

from src.seed_freshness import FreshnessSeedError, build_mapping_plan
from src.service.freshcheck_mapping_service import (
    CatalogIngredient,
    FreshCheckIngredientReference,
    MappingManifest,
    ReviewedMapping,
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


def test_build_mapping_plan_incorporates_reviewed_manifest_mappings() -> None:
    """Reviewed mappings take precedence and preserve coverage across releases."""
    catalog_ingredients = (
        CatalogIngredient(UUID("00000000-0000-0000-0000-000000000001"), "Thịt ba chỉ (ba rọi) heo"),
        CatalogIngredient(UUID("00000000-0000-0000-0000-000000000002"), "Cá hồi"),
    )
    freshcheck_ingredients = (
        FreshCheckIngredientReference("thit_ba_chi_heo", ("thịt ba chỉ heo", "ba rọi")),
        FreshCheckIngredientReference("ca_hoi", ("Cá hồi",)),
    )
    reviewed_manifest = MappingManifest(
        "0.4.0",
        (
            ReviewedMapping(
                UUID("00000000-0000-0000-0000-000000000001"),
                "thit_ba_chi_heo",
                "EXACT_CODE",
                "reviewer",
                "Pork belly mapping",
            ),
        ),
    )

    plan = build_mapping_plan(
        "0.4.0",
        catalog_ingredients,
        freshcheck_ingredients,
        reviewed_manifest=reviewed_manifest,
    )

    assert plan.mapping_manifest.kb_version == "0.4.0"
    assert [
        (mapping.master_ingredient_id, mapping.freshcheck_ingredient_id, mapping.match_method)
        for mapping in plan.mapping_manifest.mappings
    ] == [
        (UUID("00000000-0000-0000-0000-000000000001"), "thit_ba_chi_heo", "EXACT_CODE"),
        (UUID("00000000-0000-0000-0000-000000000002"), "ca_hoi", "EXACT_NAME"),
    ]
    assert plan.unmapped_count == 0
    assert plan.ambiguous_count == 0


def test_build_mapping_plan_preserves_active_mappings_from_prior_release() -> None:
    """Active mappings from the prior release are carried forward to preserve coverage."""
    catalog_ingredients = (
        CatalogIngredient(UUID("00000000-0000-0000-0000-000000000001"), "Thịt bò"),
        CatalogIngredient(UUID("00000000-0000-0000-0000-000000000002"), "Cá hồi"),
    )
    freshcheck_ingredients = (
        FreshCheckIngredientReference("thit_bo_than", ("thịt bò tươi",)),
        FreshCheckIngredientReference("ca_hoi", ("Cá hồi",)),
    )
    # Active mapping from 0.3.0 for beef
    active_mapping = SimpleNamespace(
        master_ingredient_id=UUID("00000000-0000-0000-0000-000000000001"),
        kb_version="0.3.0",
        freshcheck_ingredient_id="thit_bo_than",
        match_method="MANUAL_REVIEW",
        reviewed_by="legacy_reviewer",
        note="Legacy active mapping",
        catalog_code=None,
    )

    plan = build_mapping_plan(
        "0.4.0",
        catalog_ingredients,
        freshcheck_ingredients,
        active_mappings=[active_mapping],  # type: ignore[arg-type]
        prior_active_kb_version="0.3.0",
    )

    assert plan.mapping_manifest.kb_version == "0.4.0"
    mappings_dict = {m.master_ingredient_id: m for m in plan.mapping_manifest.mappings}
    assert UUID("00000000-0000-0000-0000-000000000001") in mappings_dict
    assert mappings_dict[UUID("00000000-0000-0000-0000-000000000001")].freshcheck_ingredient_id == "thit_bo_than"
    assert mappings_dict[UUID("00000000-0000-0000-0000-000000000001")].match_method == "MANUAL_REVIEW"
    # And cá hồi matched by exact name
    assert UUID("00000000-0000-0000-0000-000000000002") in mappings_dict
    assert mappings_dict[UUID("00000000-0000-0000-0000-000000000002")].freshcheck_ingredient_id == "ca_hoi"


def test_build_mapping_plan_allows_reviewed_manifest_to_override_active_mapping() -> None:
    """Explicit reviewed manifest overrides prior active mapping."""
    catalog_ingredients = (
        CatalogIngredient(UUID("00000000-0000-0000-0000-000000000001"), "Cá quả"),
    )
    freshcheck_ingredients = (
        FreshCheckIngredientReference("ca_loc", ("cá quả",)),
    )
    active_mapping = SimpleNamespace(
        master_ingredient_id=UUID("00000000-0000-0000-0000-000000000001"),
        kb_version="0.3.0",
        freshcheck_ingredient_id="ca_loc_cu",
        match_method="EXACT_NAME",
        reviewed_by="old",
        note="Old",
        catalog_code=None,
    )
    manifest = MappingManifest(
        "0.4.0",
        (
            ReviewedMapping(
                UUID("00000000-0000-0000-0000-000000000001"),
                "ca_loc",
                "EXACT_CODE",
                "new_reviewer",
                "Updated whole fish mapping",
            ),
        ),
    )

    plan = build_mapping_plan(
        "0.4.0",
        catalog_ingredients,
        freshcheck_ingredients,
        reviewed_manifest=manifest,
        active_mappings=[active_mapping],  # type: ignore[arg-type]
        prior_active_kb_version="0.3.0",
    )

    assert len(plan.mapping_manifest.mappings) == 1
    mapping = plan.mapping_manifest.mappings[0]
    assert mapping.freshcheck_ingredient_id == "ca_loc"
    assert mapping.reviewed_by == "new_reviewer"


def test_build_mapping_plan_fails_closed_on_dangling_active_reference() -> None:
    """Fails closed when active mapping references an ingredient removed in new release without override."""
    catalog_ingredients = (
        CatalogIngredient(UUID("00000000-0000-0000-0000-000000000001"), "Món cũ"),
    )
    freshcheck_ingredients = (
        FreshCheckIngredientReference("mon_moi", ("món mới",)),
    )
    active_mapping = SimpleNamespace(
        master_ingredient_id=UUID("00000000-0000-0000-0000-000000000001"),
        kb_version="0.3.0",
        freshcheck_ingredient_id="mon_cu_da_xoa",
        match_method="MANUAL_REVIEW",
        reviewed_by="old",
        note="Old",
        catalog_code=None,
    )

    with pytest.raises(FreshnessSeedError, match="removed ingredient"):
        build_mapping_plan(
            "0.4.0",
            catalog_ingredients,
            freshcheck_ingredients,
            active_mappings=[active_mapping],  # type: ignore[arg-type]
            prior_active_kb_version="0.3.0",
        )
