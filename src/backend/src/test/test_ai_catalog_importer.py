"""Focused tests for Slice A: AI catalog database schema, importer pure logic, and migration."""

from __future__ import annotations

import importlib.util
from decimal import Decimal
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import UUID

import pytest

from AI.catalog.importer import (
    DEFAULT_BUNDLE_DIR,
    ImportReport,
    _classify_and_upsert_table,
    load_catalog_bundle,
    load_recipe_media,
    parse_args,
    resolve_ingredient_id,
    run_importer,
    transform_catalog_bundle,
    transform_recipe_ingredients,
    values_differ,
)
from src.model.enum_model import MeasurementUnit
from src.model.recipe_model import RecipeModel

BACKEND_ROOT = Path(__file__).resolve().parents[2]
MIGRATION_PATH = BACKEND_ROOT / "alembic" / "versions" / "e2b4f68a10cd_add_ai_catalog_columns.py"


def test_load_catalog_bundle_row_counts() -> None:
    """Bundle loader reads exact byte-exact counts of all catalog files."""
    bundle = load_catalog_bundle(DEFAULT_BUNDLE_DIR)
    assert len(bundle.recipes) == 1075
    assert len(bundle.recipe_ingredients) == 10406
    assert len(bundle.master_nutrition) == 1399
    assert len(bundle.redirects) == 213


def test_pure_transformation_recipe_contract_and_constraints() -> None:
    """Every transformed recipe satisfies the shared data contract and DB constraints."""
    bundle = load_catalog_bundle(DEFAULT_BUNDLE_DIR)
    data, _report = transform_catalog_bundle(bundle)

    assert len(data.recipes) == 1075
    expected_recipe_contract_keys = {
        "id",
        "name",
        "description",
        "instructions",
        "media_url",
        "source_platform",
        "source_url",
        "default_servings",
        "estimated_cooking_minutes",
        "estimated_cost",
        "total_calories",
        "total_protein_g",
        "total_fat_g",
        "total_carbs_g",
        "total_sugar_g",
        "other_nutrients",
        "nutrition_status",
        "tags",
        "ai_features",
    }

    raw_recipe_keys = set(bundle.recipes[0].keys()) - {"id"}
    seen_ids: set[UUID] = set()
    seen_names: set[str] = set()
    seen_urls: set[str] = set()

    for recipe in data.recipes:
        assert set(recipe.keys()) == expected_recipe_contract_keys
        assert isinstance(recipe["id"], UUID)
        assert recipe["id"] not in seen_ids
        seen_ids.add(recipe["id"])

        name_lower = str(recipe["name"]).casefold()
        assert name_lower not in seen_names
        seen_names.add(name_lower)

        source_url = str(recipe["source_url"])
        assert source_url not in seen_urls
        seen_urls.add(source_url)

        # DB check constraints
        assert isinstance(recipe["default_servings"], Decimal)
        assert recipe["default_servings"] > 0
        assert recipe["nutrition_status"] in ("COMPLETE", "PARTIAL", "INCOMPLETE")
        assert recipe["estimated_cooking_minutes"] > 0
        assert isinstance(recipe["instructions"], dict)
        assert isinstance(recipe["tags"], dict)

        # ai_features contract: every column of recipes.csv except id verbatim
        ai_features = recipe["ai_features"]
        assert isinstance(ai_features, dict)
        assert set(ai_features.keys()) == raw_recipe_keys


def test_pure_transformation_ingredient_contract_and_quantities() -> None:
    """Ingredient rows satisfy schema constraints, quantity rules, and foreign keys."""
    bundle = load_catalog_bundle(DEFAULT_BUNDLE_DIR)
    data, _report = transform_catalog_bundle(bundle)

    # All 10406 rows retained: 10381 canonical + 25 linked to 21 placeholder masters
    assert len(data.recipe_ingredients) == 10406
    assert len(data.placeholder_ids) == 21
    # Check that canonical masters + placeholder masters match
    assert len(data.masters) == 1399 + 21

    expected_ingredient_contract_keys = {
        "id",
        "recipe_id",
        "master_ingredient_id",
        "required_quantity",
        "unit",
        "display_quantity",
        "display_unit",
        "is_optional",
        "preparation_note",
        "ai_attributes",
    }

    raw_ingredient_keys = set(bundle.recipe_ingredients[0].keys()) - {"id", "recipe_id"}
    valid_recipe_ids = {r["id"] for r in data.recipes}
    valid_master_ids = {m["id"] for m in data.masters}

    for ing in data.recipe_ingredients:
        assert set(ing.keys()) == expected_ingredient_contract_keys
        assert isinstance(ing["id"], UUID)
        assert ing["recipe_id"] in valid_recipe_ids
        assert ing["master_ingredient_id"] in valid_master_ids

        # DB check constraints
        assert isinstance(ing["required_quantity"], Decimal)
        assert ing["required_quantity"] > 0
        assert ing["display_quantity"] is None or (
            isinstance(ing["display_quantity"], Decimal) and ing["display_quantity"] > 0
        )
        assert isinstance(ing["unit"], MeasurementUnit)
        role = str(ing["ai_attributes"].get("ingredient_role", "")).strip().lower()
        assert ing["is_optional"] is (role == "seasoning")

        # ai_attributes contract: every column of recipe_ingredients.csv except id, recipe_id
        ai_attrs = ing["ai_attributes"]
        assert isinstance(ai_attrs, dict)
        assert set(ai_attrs.keys()) == raw_ingredient_keys

        # Deterministic quantity rule:
        # If original required_quantity was empty, fallback uses estimated_weight_g or 1.000
        orig_qty = str(ai_attrs.get("required_quantity", "")).strip()
        orig_weight = str(ai_attrs.get("estimated_weight_g", "")).strip()
        if not orig_qty:
            if orig_weight and float(orig_weight) > 0:
                assert ing["unit"] == MeasurementUnit.GRAM
                assert ing["required_quantity"] == Decimal(orig_weight).quantize(Decimal("0.001"))
            else:
                assert ing["unit"] in (MeasurementUnit.OTHER, MeasurementUnit.GRAM)
                assert ing["required_quantity"] == Decimal("1.000")
        # A count in an unmeasurable unit ("1 trái") must be stored by weight in grams.
        elif ing["unit"] == MeasurementUnit.OTHER:
            assert not (orig_weight and float(orig_weight) > 0)

        # For placeholder-linked rows, master_ingredient_code is empty and master is unverified
        if not ai_attrs.get("master_ingredient_code"):
            master_row = next(m for m in data.masters if m["id"] == ing["master_ingredient_id"])
            assert master_row["source_code"] is None
            assert master_row["is_verified"] is False
            assert master_row["canonical_unit"] == MeasurementUnit.GRAM


def test_redirect_handling_synthetic() -> None:
    """Ingredient pointing to a redirected old code resolves to canonical master."""
    bundle = load_catalog_bundle(DEFAULT_BUNDLE_DIR)
    master_code_to_id = {
        row["code"].strip(): resolve_ingredient_id(f"master:{row['code'].strip()}")
        for row in bundle.master_nutrition
    }
    redirect_map = {
        row["old_code"].strip(): row["canonical_code"].strip()
        for row in bundle.redirects
        if row.get("old_code") and row.get("canonical_code")
    }

    sample_recipe_id = UUID(bundle.recipes[0]["id"].strip())
    valid_recipe_ids = {sample_recipe_id}

    # Old code 20430 redirects to canonical 14004
    synthetic_rows = [
        {
            "id": "e0000000-0000-0000-0000-000000000001",
            "recipe_id": str(sample_recipe_id),
            "master_ingredient_code": "20430",
            "required_quantity": "100.0",
            "unit": "GRAM",
            "unit_vi": "g",
            "estimated_weight_g": "100.0",
        },
        {
            "id": "e0000000-0000-0000-0000-000000000002",
            "recipe_id": str(sample_recipe_id),
            "master_ingredient_code": "NON_EXISTENT_CODE_99999",
            "required_quantity": "100.0",
            "unit": "GRAM",
        },
    ]

    report = ImportReport()
    unclass_cat_uuid = UUID("00000000-0000-0000-0000-000000000099")
    placeholder_masters: dict[UUID, dict[str, object]] = {}
    transformed = transform_recipe_ingredients(
        synthetic_rows,
        valid_recipe_ids,
        master_code_to_id,
        redirect_map,
        unclass_cat_uuid,
        placeholder_masters,
        report,
    )
    assert len(transformed) == 1
    assert transformed[0]["master_ingredient_id"] == master_code_to_id["14004"]
    assert len(report.redirected) == 1
    assert "20430 -> 14004" in report.redirected[0]

    assert len(report.rejected) == 1
    assert "NON_EXISTENT_CODE_99999" in report.rejected[0]


def test_determinism_across_runs() -> None:
    """Running the transformation pipeline twice yields identical deterministic IDs."""
    bundle = load_catalog_bundle(DEFAULT_BUNDLE_DIR)

    data1, report1 = transform_catalog_bundle(bundle)
    data2, report2 = transform_catalog_bundle(bundle)

    assert [c["id"] for c in data1.categories] == [c["id"] for c in data2.categories]
    assert [m["id"] for m in data1.masters] == [m["id"] for m in data2.masters]
    assert [a["id"] for a in data1.aliases] == [a["id"] for a in data2.aliases]
    assert [r["id"] for r in data1.recipes] == [r["id"] for r in data2.recipes]
    assert [i["id"] for i in data1.recipe_ingredients] == [i["id"] for i in data2.recipe_ingredients]

    assert report1.summary() == report2.summary()


def test_alembic_migration_schema_and_operations() -> None:
    """Migration revision matches chain and exercises upgrade/downgrade operations."""
    assert MIGRATION_PATH.exists(), f"Migration file missing: {MIGRATION_PATH}"

    spec = importlib.util.spec_from_file_location("ai_migration", str(MIGRATION_PATH))
    assert spec is not None and spec.loader is not None
    migration = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(migration)

    assert migration.revision == "e2b4f68a10cd"
    assert migration.down_revision == "98d6d2fdff50"

    mock_op = MagicMock()
    with patch("alembic.op.add_column", mock_op.add_column), \
         patch("alembic.op.create_index", mock_op.create_index), \
         patch("alembic.op.drop_index", mock_op.drop_index), \
         patch("alembic.op.drop_column", mock_op.drop_column):

        # Exercise upgrade
        migration.upgrade()
        assert mock_op.add_column.call_count == 3
        assert mock_op.create_index.call_count == 1

        added_columns = [(call.args[0], call.args[1].name) for call in mock_op.add_column.mock_calls]
        assert ("recipes", "ai_features") in added_columns
        assert ("recipe_ingredients", "ai_attributes") in added_columns
        assert ("master_ingredients", "source_code") in added_columns

        created_indexes = [call.args[0] for call in mock_op.create_index.mock_calls]
        assert "uq_master_ingredients_source_code" in created_indexes

        # Exercise downgrade
        mock_op.reset_mock()
        migration.downgrade()
        assert mock_op.drop_index.call_count == 1
        assert mock_op.drop_column.call_count == 3

        dropped_indexes = [call.args[0] for call in mock_op.drop_index.mock_calls]
        assert "uq_master_ingredients_source_code" in dropped_indexes

        dropped_columns = [(call.args[0], call.args[1]) for call in mock_op.drop_column.mock_calls]
        assert ("master_ingredients", "source_code") in dropped_columns
        assert ("recipe_ingredients", "ai_attributes") in dropped_columns
        assert ("recipes", "ai_features") in dropped_columns


@pytest.mark.anyio
async def test_importer_cli_parsing_and_dry_run(monkeypatch: pytest.MonkeyPatch) -> None:
    """CLI argument parsing and dry-run execution run end-to-end without crashing."""
    # Never reach a real database: an unreachable URL forces the offline dry-run path.
    monkeypatch.setenv("DATABASE_URL", "postgresql+asyncpg://test:test@127.0.0.1:1/test")
    parsed = parse_args(["--dry-run", "--bundle-dir", str(DEFAULT_BUNDLE_DIR)])
    assert parsed.dry_run is True
    assert parsed.bundle_dir == DEFAULT_BUNDLE_DIR

    report = await run_importer(bundle_dir=DEFAULT_BUNDLE_DIR, dry_run=True)
    assert len(report.created) == 27385
    assert len(report.created_placeholders) == 21
    assert len(report.rejected) == 301
    assert len(report.redirected) == 0

    breakdown = report.rejection_breakdown()
    assert breakdown["alias_duplicates"] == 301
    assert breakdown["duplicate_recipe_names"] == 0
    assert breakdown["duplicate_recipe_urls"] == 0
    assert breakdown["unknown_master_codes"] == 0

    assert "created=27385" in report.summary()
    assert "[placeholders=21]" in report.summary()
    assert "rejected=301" in report.summary()
    assert "alias_duplicates=301" in report.summary()

def test_values_differ_classification_without_postgres() -> None:
    """Classification comparison handles numeric tolerances, enums, JSONB dicts, and None."""
    assert not values_differ(Decimal("4.000"), 4.0)
    assert not values_differ(Decimal("4.0000001"), 4.0)
    assert values_differ(Decimal("4.001"), 4.0)
    assert not values_differ(MeasurementUnit.GRAM, "GRAM")
    assert not values_differ("GRAM", MeasurementUnit.GRAM)
    assert values_differ(MeasurementUnit.GRAM, MeasurementUnit.KG)
    assert not values_differ(None, None)
    assert values_differ(None, 0.0)
    assert values_differ("hello", "world")
    assert not values_differ("  hello  ", "hello")
    assert not values_differ({"steps": []}, {"steps": []})
    assert values_differ({"steps": [{"step": 1}]}, {"steps": []})


def test_recipe_media_transformed_counts_match_artifact() -> None:
    """Transformed recipe counts with media and steps exactly match recipe_media.json."""
    bundle = load_catalog_bundle(DEFAULT_BUNDLE_DIR)
    report = ImportReport()
    data, _ = transform_catalog_bundle(bundle, report)

    assert len(data.recipes) == 1075

    recipes_with_media = [r for r in data.recipes if r["media_url"] is not None]
    artifact_with_media = [m for m in bundle.recipe_media if m.get("media_url") is not None]
    assert len(recipes_with_media) == len(artifact_with_media) == 1075

    recipes_with_steps = [r for r in data.recipes if bool(r["instructions"].get("steps"))]
    artifact_with_steps = [m for m in bundle.recipe_media if bool(m.get("steps"))]
    assert len(recipes_with_steps) == len(artifact_with_steps) == 1075

    # Check that the 7 overridden recipes carry 4-6 steps each
    overridden_ids = {
        "05dae86b-448a-514e-a4dc-2a81394b5dbd",
        "2316d42e-fbe6-5443-98e4-81cf0c34a145",
        "4b767868-aae2-5b64-b459-fce529d7e0c9",
        "4d7a2558-9c7b-5750-844c-f0ca902223a0",
        "c5270778-4e98-584b-8b9f-4b8eb39b9afd",
        "de9e2f72-4152-56c5-ad24-b2d11d232d67",
        "e4792ee5-a1be-52be-99ff-0264e7e19dc5",
    }
    for r in data.recipes:
        if str(r["id"]) in overridden_ids:
            step_count = len(r["instructions"]["steps"])
            assert 4 <= step_count <= 6, f"Overridden recipe {r['id']} has {step_count} steps"

    # Validate step structure contract (order and text only, no redundant duplicate keys)
    for r in recipes_with_steps:
        steps = r["instructions"]["steps"]
        assert isinstance(steps, list) and len(steps) > 0
        for idx, step in enumerate(steps, start=1):
            assert isinstance(step, dict)
            assert step["order"] == idx
            assert isinstance(step["text"], str) and step["text"].strip()
            assert "title" not in step
            assert "content" not in step


def test_missing_recipe_media_raises_clean_error(tmp_path: Path) -> None:
    """Missing recipe_media.json raises a clean FileNotFoundError referencing media_builder."""
    missing_path = tmp_path / "catalog" / "recipe_media.json"
    with pytest.raises(FileNotFoundError, match="media_builder"):
        load_recipe_media(missing_path)


@pytest.mark.anyio
async def test_classification_unchanged_rerun_and_changed_media_url() -> None:
    """Unchanged rerun reports all records unchanged; modified media_url reports exactly 1 updated."""
    bundle = load_catalog_bundle(DEFAULT_BUNDLE_DIR)
    data, _ = transform_catalog_bundle(bundle, ImportReport())

    recipes_sample = data.recipes[:10]
    existing_rows = [dict(r) for r in recipes_sample]

    session = AsyncMock()
    result_mock = MagicMock()
    result_mock.mappings.return_value = existing_rows
    session.execute.return_value = result_mock

    # Unchanged rerun
    report_unchanged = ImportReport()
    await _classify_and_upsert_table(
        session,
        RecipeModel.__table__,
        recipes_sample,
        "recipe",
        report_unchanged,
        dry_run=True,
        batch_size=500,
    )
    assert len(report_unchanged.created) == 0
    assert len(report_unchanged.updated) == 0
    assert len(report_unchanged.unchanged) == len(recipes_sample)

    # Mutate media_url of exactly 1 recipe
    mutated_sample = [dict(r) for r in recipes_sample]
    mutated_sample[0]["media_url"] = "https://example.com/new-image-for-test.jpg"

    report_updated = ImportReport()
    await _classify_and_upsert_table(
        session,
        RecipeModel.__table__,
        mutated_sample,
        "recipe",
        report_updated,
        dry_run=True,
        batch_size=500,
    )
    assert len(report_updated.created) == 0
    assert len(report_updated.updated) == 1
    assert len(report_updated.unchanged) == len(recipes_sample) - 1
