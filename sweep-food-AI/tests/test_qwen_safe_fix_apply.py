"""Tests for scripts/eda/apply_qwen_safe_fix.py against small CSV fixtures.

Never touches the real ~64k-row processed dataset: all paths are monkeypatched
to a tmp_path fixture so this is safe to run anywhere, anytime.
"""

import csv
import json

import pytest

import scripts.eda.apply_qwen_safe_fix as apply_fix
import scripts.eda.audit_qwen_matching as audit_mod


def _write_csv(path, rows, fieldnames):
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


@pytest.fixture
def fixture_paths(tmp_path, monkeypatch):
    master_csv = tmp_path / "master.csv"
    ing_csv = tmp_path / "recipe_ingredients.csv"
    ing_json = tmp_path / "recipe_ingredients.json"
    recipes_csv = tmp_path / "recipes.csv"
    recipes_json = tmp_path / "recipes.json"
    out_dir = tmp_path / "reports"

    _write_csv(master_csv, [
        {"code": "4019", "name_vi": "Chuối xanh"},
        {"code": "4007", "name_vi": "Cà rốt"},
    ], ["code", "name_vi"])

    ing_fields = ["id", "recipe_id", "master_ingredient_code", "master_ingredient_name",
                  "raw_text", "cleaned_name", "match_confidence", "match_method",
                  "calories", "protein_g", "fat_g", "carbs_g"]
    ing_rows = [
        # Class A: reviewed false positive (hanh la -> "Chuoi xanh"), simple raw text.
        {"id": "row-a", "recipe_id": "r1", "master_ingredient_code": "4019",
         "master_ingredient_name": "Hành hoa, tươi", "raw_text": "hành lá",
         "cleaned_name": "hành lá", "match_confidence": "0.98", "match_method": "QWEN_LLM_MATCH",
         "calories": "90", "protein_g": "1.0", "fat_g": "0.2", "carbs_g": "22"},
        # Class C-shaped but not in the VALID table here -> stays B; included to
        # prove non-A rows are never touched regardless of class.
        {"id": "row-b", "recipe_id": "r1", "master_ingredient_code": "4007",
         "master_ingredient_name": "Cà rốt", "raw_text": "2 củ cà rốt to",
         "cleaned_name": "cà rốt", "match_confidence": "0.98", "match_method": "QWEN_LLM_MATCH",
         "calories": "41", "protein_g": "0.9", "fat_g": "0.2", "carbs_g": "9.6"},
        # Unrelated non-Qwen row: must never be touched.
        {"id": "row-c", "recipe_id": "r1", "master_ingredient_code": "4007",
         "master_ingredient_name": "Cà rốt", "raw_text": "cà rốt",
         "cleaned_name": "cà rốt", "match_confidence": "1.00", "match_method": "EXACT_CATALOG_MATCH",
         "calories": "41", "protein_g": "0.9", "fat_g": "0.2", "carbs_g": "9.6"},
    ]
    _write_csv(ing_csv, ing_rows, ing_fields)
    ing_json.write_text(json.dumps(ing_rows, ensure_ascii=False), encoding="utf-8")

    recipe_fields = ["id", "total_calories", "total_protein_g", "total_fat_g", "total_carbs_g"]
    recipes = [{"id": "r1", "total_calories": "172", "total_protein_g": "2.8",
                "total_fat_g": "0.6", "total_carbs_g": "41.6"}]
    _write_csv(recipes_csv, recipes, recipe_fields)
    recipes_json.write_text(json.dumps(recipes, ensure_ascii=False), encoding="utf-8")

    monkeypatch.setattr(audit_mod, "ING", ing_csv)
    monkeypatch.setattr(audit_mod, "MASTER", master_csv)
    monkeypatch.setattr(apply_fix, "ING", ing_csv)
    monkeypatch.setattr(apply_fix, "ING_JSON", ing_json)
    monkeypatch.setattr(apply_fix, "RECIPES_CSV", recipes_csv)
    monkeypatch.setattr(apply_fix, "RECIPES_JSON", recipes_json)
    monkeypatch.setattr(apply_fix, "OUT", out_dir)
    return {"ing_csv": ing_csv, "ing_json": ing_json, "recipes_csv": recipes_csv, "recipes_json": recipes_json}


def test_preview_does_not_write_any_file(fixture_paths):
    before = fixture_paths["ing_csv"].read_bytes()
    report = apply_fix.run(apply=False)
    assert report["status"] == "preview"
    assert report["corrected_A"] == 1
    assert fixture_paths["ing_csv"].read_bytes() == before


def test_apply_clears_only_class_a_row(fixture_paths):
    report = apply_fix.run(apply=True)
    assert report["status"] == "applied"
    assert report["corrected_A"] == 1

    with fixture_paths["ing_csv"].open(encoding="utf-8-sig", newline="") as f:
        rows = {r["id"]: r for r in csv.DictReader(f)}

    cleared = rows["row-a"]
    assert cleared["master_ingredient_code"] in (None, "")
    assert cleared["master_ingredient_name"] in (None, "")
    assert cleared["match_method"] == "UNMATCHED"
    assert cleared["match_confidence"] in (None, "")
    assert cleared["calories"] in (None, "")

    untouched_b = rows["row-b"]
    assert untouched_b["master_ingredient_code"] == "4007"
    assert untouched_b["calories"] == "41"

    untouched_c = rows["row-c"]
    assert untouched_c["match_method"] == "EXACT_CATALOG_MATCH"
    assert untouched_c["calories"] == "41"


def test_apply_recomputes_recipe_rollup_totals(fixture_paths):
    apply_fix.run(apply=True)
    with fixture_paths["recipes_csv"].open(encoding="utf-8-sig", newline="") as f:
        recipe = next(csv.DictReader(f))
    # Only row-b (41 kcal) and row-c (41 kcal) remain after row-a (90 kcal) is cleared.
    assert recipe["total_calories"] == "82.0"


def test_apply_writes_json_mirrors_csv(fixture_paths):
    apply_fix.run(apply=True)
    ing_json_rows = {r["id"]: r for r in json.loads(fixture_paths["ing_json"].read_text(encoding="utf-8"))}
    assert ing_json_rows["row-a"]["master_ingredient_code"] is None
    assert ing_json_rows["row-a"]["match_method"] == "UNMATCHED"


def test_run_is_deterministic(fixture_paths):
    report1 = apply_fix.run(apply=False)
    report2 = apply_fix.run(apply=False)
    assert report1 == report2
