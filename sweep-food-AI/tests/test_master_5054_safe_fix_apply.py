"""Tests for scripts/eda/apply_master_5054_safe_fix.py against small CSV
fixtures.

Never touches the real ~64k-row processed dataset: all paths are
monkeypatched to a tmp_path fixture so this is safe to run anywhere, anytime.
"""

import csv
import json

import pytest

import scripts.eda.apply_master_5054_safe_fix as apply_fix
import scripts.eda.audit_master_5054_matching as audit_mod


def _write_csv(path, rows, fieldnames):
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


@pytest.fixture
def fixture_paths(tmp_path, monkeypatch):
    ing_csv = tmp_path / "recipe_ingredients.csv"
    ing_json = tmp_path / "recipe_ingredients.json"
    recipes_csv = tmp_path / "recipes.csv"
    recipes_json = tmp_path / "recipes.json"
    out_dir = tmp_path / "reports"

    ing_fields = ["id", "recipe_id", "master_ingredient_code", "master_ingredient_name",
                  "raw_text", "cleaned_name", "match_confidence", "match_method",
                  "calories", "protein_g", "fat_g", "carbs_g"]
    ing_rows = [
        # Class A: bare dairy term wrongly linked to Vu sua (5054). Safe to clear.
        {"id": "row-a", "recipe_id": "r1", "master_ingredient_code": "5054",
         "master_ingredient_name": "Vú sữa", "raw_text": "Sữa tươi 300 ml",
         "cleaned_name": "sữa tươi", "match_confidence": "0.98", "match_method": "PRESET_ALIAS_MATCH",
         "calories": "148", "protein_g": "9.9", "fat_g": "0", "carbs_g": "35.1"},
        # Legitimate Vu sua (fruit) row: must never be cleared.
        {"id": "row-d", "recipe_id": "r1", "master_ingredient_code": "5054",
         "master_ingredient_name": "Vú sữa", "raw_text": "1 quả vú sữa chín",
         "cleaned_name": "vú sữa", "match_confidence": "1.00", "match_method": "EXACT_CATALOG_MATCH",
         "calories": "51", "protein_g": "1", "fat_g": "", "carbs_g": "11.7"},
        # Unrelated row linked to a different code: must never be touched.
        {"id": "row-c", "recipe_id": "r2", "master_ingredient_code": "4007",
         "master_ingredient_name": "Cà rốt", "raw_text": "cà rốt",
         "cleaned_name": "cà rốt", "match_confidence": "1.00", "match_method": "EXACT_CATALOG_MATCH",
         "calories": "41", "protein_g": "0.9", "fat_g": "0.2", "carbs_g": "9.6"},
    ]
    _write_csv(ing_csv, ing_rows, ing_fields)
    ing_json.write_text(json.dumps(ing_rows, ensure_ascii=False), encoding="utf-8")

    recipe_fields = ["id", "total_calories", "total_protein_g", "total_fat_g", "total_carbs_g"]
    recipes = [
        {"id": "r1", "total_calories": "199", "total_protein_g": "10.9", "total_fat_g": "0", "total_carbs_g": "46.8"},
        {"id": "r2", "total_calories": "41", "total_protein_g": "0.9", "total_fat_g": "0.2", "total_carbs_g": "9.6"},
    ]
    _write_csv(recipes_csv, recipes, recipe_fields)
    recipes_json.write_text(json.dumps(recipes, ensure_ascii=False), encoding="utf-8")

    monkeypatch.setattr(audit_mod, "ING", ing_csv)
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
    assert cleared["protein_g"] in (None, "")
    assert cleared["fat_g"] in (None, "")
    assert cleared["carbs_g"] in (None, "")

    preserved_d = rows["row-d"]
    assert preserved_d["master_ingredient_code"] == "5054"
    assert preserved_d["match_method"] == "EXACT_CATALOG_MATCH"
    assert preserved_d["calories"] == "51"

    untouched_c = rows["row-c"]
    assert untouched_c["master_ingredient_code"] == "4007"
    assert untouched_c["calories"] == "41"


def test_apply_recomputes_recipe_rollup_totals(fixture_paths):
    apply_fix.run(apply=True)
    with fixture_paths["recipes_csv"].open(encoding="utf-8-sig", newline="") as f:
        recipes = {r["id"]: r for r in csv.DictReader(f)}
    # r1: only row-d (51 kcal) remains after row-a (148 kcal) is cleared.
    assert recipes["r1"]["total_calories"] == "51.0"
    # r2 is untouched.
    assert recipes["r2"]["total_calories"] == "41.0"


def test_apply_writes_json_mirrors_csv(fixture_paths):
    apply_fix.run(apply=True)
    ing_json_rows = {r["id"]: r for r in json.loads(fixture_paths["ing_json"].read_text(encoding="utf-8"))}
    assert ing_json_rows["row-a"]["master_ingredient_code"] is None
    assert ing_json_rows["row-a"]["match_method"] == "UNMATCHED"
    assert ing_json_rows["row-d"]["master_ingredient_code"] == "5054"


def test_run_is_deterministic(fixture_paths):
    report1 = apply_fix.run(apply=False)
    report2 = apply_fix.run(apply=False)
    assert report1 == report2


def test_apply_is_idempotent(fixture_paths):
    """Re-running --apply after rows are already cleared must not error and
    must find nothing left to correct."""
    apply_fix.run(apply=True)
    second_report = apply_fix.run(apply=True)
    assert second_report["corrected_A"] == 0
