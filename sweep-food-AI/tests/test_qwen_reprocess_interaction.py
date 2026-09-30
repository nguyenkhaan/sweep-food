"""Documents the interaction between the Qwen Class-A fix and main's
scripts/reprocess_recipe_weights_and_nutrition.py.

This is NOT a test of the Qwen fix itself (see test_qwen_matching.py /
test_matching_integrity.py / test_qwen_safe_fix_apply.py for that).

Historical note: this file previously pinned a known bug where the reprocessing
script collapsed missing (blank/null) nutrition on UNMATCHED rows into a
literal measured zero, which meant the Qwen fix was idempotent for MATCHING
fields but not for the missing-vs-zero nutrition distinction. That bug is now
fixed (see scripts/reprocess_recipe_weights_and_nutrition.py's UNMATCHED
branch and tests/test_unmatched_nutrition_semantics.py for the fix's own
regression coverage) -- the Qwen fix's output is now fully idempotent under
this pipeline, for both matching fields and nutrition representation.
"""

import csv
import json

import pytest

import scripts.reprocess_recipe_weights_and_nutrition as reprocess_mod


def _write_csv(path, rows, fieldnames):
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


@pytest.fixture
def qwen_fixed_row_paths(tmp_path, monkeypatch):
    """A tiny fixture shaped like the real dataset immediately after the Qwen
    Class-A fix: one row cleared to UNMATCHED with blank match fields and
    blank (not zero) nutrition."""
    ing_fields = ["id", "recipe_id", "master_ingredient_code", "master_ingredient_name",
                  "raw_text", "cleaned_name", "required_quantity", "estimated_weight_g",
                  "match_confidence", "match_method", "calories", "protein_g", "fat_g", "carbs_g"]
    ing_rows = [
        {"id": "row-a", "recipe_id": "r1", "master_ingredient_code": "", "master_ingredient_name": "",
         "raw_text": "hành lá", "cleaned_name": "hành lá", "required_quantity": "1",
         "estimated_weight_g": "10.0", "match_confidence": "", "match_method": "UNMATCHED",
         "calories": "", "protein_g": "", "fat_g": "", "carbs_g": ""},
    ]
    ing_csv = tmp_path / "data" / "processed" / "recipes" / "recipe_ingredients.csv"
    ing_json = tmp_path / "data" / "processed" / "recipes" / "recipe_ingredients.json"
    recipes_csv = tmp_path / "data" / "processed" / "recipes" / "recipes.csv"
    recipes_json = tmp_path / "data" / "processed" / "recipes" / "recipes.json"
    master_csv = tmp_path / "data" / "processed" / "viendinhduong" / "master_ingredients_nutrition.csv"
    for p in (ing_csv, recipes_csv, master_csv):
        p.parent.mkdir(parents=True, exist_ok=True)

    _write_csv(ing_csv, ing_rows, ing_fields)
    ing_json.write_text(json.dumps(ing_rows, ensure_ascii=False), encoding="utf-8")

    recipe_fields = ["id", "total_calories", "total_protein_g", "total_fat_g", "total_carbs_g", "ingredients_count"]
    recipes = [{"id": "r1", "total_calories": "0", "total_protein_g": "0", "total_fat_g": "0",
                "total_carbs_g": "0", "ingredients_count": "1"}]
    _write_csv(recipes_csv, recipes, recipe_fields)
    recipes_json.write_text(json.dumps(recipes, ensure_ascii=False), encoding="utf-8")

    _write_csv(master_csv, [{"code": "4019", "name_vi": "Chuối xanh", "category_vi": "Trái cây",
                              "energy_kcal": "90", "protein_g": "1.0", "fat_g": "0.2", "carbs_g": "22"}],
               ["code", "name_vi", "category_vi", "energy_kcal", "protein_g", "fat_g", "carbs_g"])

    monkeypatch.setattr(reprocess_mod, "ROOT", tmp_path)
    return ing_csv


def test_reprocess_keeps_matching_fields_stable_for_unmatched_rows(qwen_fixed_row_paths):
    """A3/A4/A5 outcome (match identity) IS stable across this pipeline."""
    reprocess_mod.reprocess()
    with qwen_fixed_row_paths.open(encoding="utf-8-sig", newline="") as f:
        row = next(csv.DictReader(f))
    assert row["match_method"] == "UNMATCHED"
    assert row["master_ingredient_code"] == ""
    assert row["master_ingredient_name"] == ""
    assert row["match_confidence"] == ""


def test_reprocess_now_keeps_unmatched_nutrition_blank_not_zero(qwen_fixed_row_paths):
    """Fixed: nutrition on an UNMATCHED row (including a Qwen Class-A row
    cleared by scripts/eda/apply_qwen_safe_fix.py) stays blank/missing across
    this pipeline instead of being collapsed into a literal measured zero.
    The Qwen fix's output is therefore now fully idempotent under this
    pipeline, for both matching fields and nutrition representation."""
    reprocess_mod.reprocess()
    with qwen_fixed_row_paths.open(encoding="utf-8-sig", newline="") as f:
        row = next(csv.DictReader(f))
    assert row["calories"] == ""
    assert row["protein_g"] == ""
    assert row["fat_g"] == ""
    assert row["carbs_g"] == ""
