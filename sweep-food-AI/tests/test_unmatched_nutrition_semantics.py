"""Part A: UNMATCHED rows must carry missing nutrition (CSV blank / JSON null),
never a manufactured literal zero. Covers both code paths that previously wrote
zero: scripts/fix_unmatched_invariants.py and
scripts/reprocess_recipe_weights_and_nutrition.py.

Only the zero-manufacturing bug is touched -- master-link clearing behavior,
the COMPLETE/PARTIAL/INCOMPLETE thresholds and known-only summation are
pre-existing and unchanged; these tests pin them, not redesign them.
"""

import csv
import json

import pytest

import scripts.fix_unmatched_invariants as fix_invariants_mod
import scripts.reprocess_recipe_weights_and_nutrition as reprocess_mod


def _write_csv(path, rows, fieldnames):
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def _read_csv(path):
    with path.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


ING_FIELDS = ["id", "recipe_id", "master_ingredient_code", "master_ingredient_name",
              "raw_text", "cleaned_name", "required_quantity", "estimated_weight_g",
              "match_confidence", "match_method", "calories", "protein_g", "fat_g", "carbs_g"]
RECIPE_FIELDS = ["id", "total_calories", "total_protein_g", "total_fat_g", "total_carbs_g", "ingredients_count"]
MASTER_FIELDS = ["code", "name_vi", "category_vi", "energy_kcal", "protein_g", "fat_g", "carbs_g"]


# ---------------------------------------------------------------------------
# scripts/reprocess_recipe_weights_and_nutrition.py
# ---------------------------------------------------------------------------

@pytest.fixture
def reprocess_paths(tmp_path, monkeypatch):
    ing_rows = [
        # r_all_unmatched: single UNMATCHED row -> recipe must become INCOMPLETE.
        {"id": "u1", "recipe_id": "r_all_unmatched", "master_ingredient_code": "",
         "master_ingredient_name": "", "raw_text": "nguyên liệu lạ", "cleaned_name": "nguyên liệu lạ",
         "required_quantity": "1", "estimated_weight_g": "10.0", "match_confidence": "",
         "match_method": "UNMATCHED", "calories": "", "protein_g": "", "fat_g": "", "carbs_g": ""},
        # r_mixed: 3 known rows + 1 missing (25% < 30% threshold) -> PARTIAL, and
        # totals must reflect only the known contributions.
        {"id": "m1", "recipe_id": "r_mixed", "master_ingredient_code": "4007",
         "master_ingredient_name": "Cà rốt", "raw_text": "cà rốt", "cleaned_name": "cà rốt",
         "required_quantity": "1", "estimated_weight_g": "100.0", "match_confidence": "1.00",
         "match_method": "EXACT_CATALOG_MATCH", "calories": "", "protein_g": "", "fat_g": "", "carbs_g": ""},
        {"id": "m2", "recipe_id": "r_mixed", "master_ingredient_code": "4007",
         "master_ingredient_name": "Cà rốt", "raw_text": "cà rốt", "cleaned_name": "cà rốt",
         "required_quantity": "1", "estimated_weight_g": "100.0", "match_confidence": "1.00",
         "match_method": "EXACT_CATALOG_MATCH", "calories": "", "protein_g": "", "fat_g": "", "carbs_g": ""},
        {"id": "m3", "recipe_id": "r_mixed", "master_ingredient_code": "4007",
         "master_ingredient_name": "Cà rốt", "raw_text": "cà rốt", "cleaned_name": "cà rốt",
         "required_quantity": "1", "estimated_weight_g": "100.0", "match_confidence": "1.00",
         "match_method": "EXACT_CATALOG_MATCH", "calories": "", "protein_g": "", "fat_g": "", "carbs_g": ""},
        {"id": "m4", "recipe_id": "r_mixed", "master_ingredient_code": "",
         "master_ingredient_name": "", "raw_text": "nguyên liệu lạ", "cleaned_name": "nguyên liệu lạ",
         "required_quantity": "1", "estimated_weight_g": "10.0", "match_confidence": "",
         "match_method": "UNMATCHED", "calories": "", "protein_g": "", "fat_g": "", "carbs_g": ""},
        # r_genuine_zero: known match whose master nutrient is a real, measured zero.
        {"id": "z1", "recipe_id": "r_genuine_zero", "master_ingredient_code": "9999",
         "master_ingredient_name": "Bột ngọt", "raw_text": "bột ngọt", "cleaned_name": "bột ngọt",
         "required_quantity": "1", "estimated_weight_g": "5.0", "match_confidence": "1.00",
         "match_method": "EXACT_CATALOG_MATCH", "calories": "", "protein_g": "", "fat_g": "", "carbs_g": ""},
    ]
    recipes = [
        {"id": "r_all_unmatched", "total_calories": "0", "total_protein_g": "0", "total_fat_g": "0",
         "total_carbs_g": "0", "ingredients_count": "1"},
        {"id": "r_mixed", "total_calories": "0", "total_protein_g": "0", "total_fat_g": "0",
         "total_carbs_g": "0", "ingredients_count": "4"},
        {"id": "r_genuine_zero", "total_calories": "0", "total_protein_g": "0", "total_fat_g": "0",
         "total_carbs_g": "0", "ingredients_count": "1"},
    ]
    master_rows = [
        {"code": "4007", "name_vi": "Cà rốt", "category_vi": "Rau, quả, củ dùng làm rau",
         "energy_kcal": "41", "protein_g": "0.9", "fat_g": "0.2", "carbs_g": "9.6"},
        {"code": "9999", "name_vi": "Bột ngọt", "category_vi": "Gia vị, nước chấm",
         "energy_kcal": "0", "protein_g": "0", "fat_g": "0", "carbs_g": "0"},
    ]

    ing_csv = tmp_path / "data" / "processed" / "recipes" / "recipe_ingredients.csv"
    ing_json = tmp_path / "data" / "processed" / "recipes" / "recipe_ingredients.json"
    recipes_csv = tmp_path / "data" / "processed" / "recipes" / "recipes.csv"
    recipes_json = tmp_path / "data" / "processed" / "recipes" / "recipes.json"
    master_csv = tmp_path / "data" / "processed" / "viendinhduong" / "master_ingredients_nutrition.csv"
    for p in (ing_csv, recipes_csv, master_csv):
        p.parent.mkdir(parents=True, exist_ok=True)

    _write_csv(ing_csv, ing_rows, ING_FIELDS)
    ing_json.write_text(json.dumps(ing_rows, ensure_ascii=False), encoding="utf-8")
    _write_csv(recipes_csv, recipes, RECIPE_FIELDS)
    recipes_json.write_text(json.dumps(recipes, ensure_ascii=False), encoding="utf-8")
    _write_csv(master_csv, master_rows, MASTER_FIELDS)

    monkeypatch.setattr(reprocess_mod, "ROOT", tmp_path)
    return {"ing_csv": ing_csv, "recipes_csv": recipes_csv, "recipes_json": recipes_json}


def test_unmatched_nutrition_is_blank_not_zero(reprocess_paths):
    reprocess_mod.reprocess()
    rows = {r["id"]: r for r in _read_csv(reprocess_paths["ing_csv"])}
    for field in ("calories", "protein_g", "fat_g", "carbs_g"):
        assert rows["u1"][field] == ""
        assert rows["m4"][field] == ""


def test_unmatched_master_code_and_name_remain_blank(reprocess_paths):
    reprocess_mod.reprocess()
    rows = {r["id"]: r for r in _read_csv(reprocess_paths["ing_csv"])}
    assert rows["u1"]["master_ingredient_code"] == ""
    assert rows["u1"]["master_ingredient_name"] == ""


def test_genuine_zero_nutrition_is_preserved_as_zero(reprocess_paths):
    reprocess_mod.reprocess()
    rows = {r["id"]: r for r in _read_csv(reprocess_paths["ing_csv"])}
    assert rows["z1"]["calories"] == "0.0"
    assert rows["z1"]["protein_g"] == "0.0"
    assert rows["z1"]["fat_g"] == "0.0"
    assert rows["z1"]["carbs_g"] == "0.0"


def test_all_unmatched_recipe_becomes_incomplete(reprocess_paths):
    reprocess_mod.reprocess()
    recipes = {r["id"]: r for r in json.loads(reprocess_paths["recipes_json"].read_text(encoding="utf-8"))}
    assert recipes["r_all_unmatched"]["nutrition_status"] == "INCOMPLETE"
    assert recipes["r_all_unmatched"]["missing_nutrition_count"] == 1


def test_mixed_recipe_keeps_known_only_totals_and_counts_missing(reprocess_paths):
    reprocess_mod.reprocess()
    recipes_csv = {r["id"]: r for r in _read_csv(reprocess_paths["recipes_csv"])}
    recipes_json = {r["id"]: r for r in json.loads(reprocess_paths["recipes_json"].read_text(encoding="utf-8"))}
    # 3 known rows x 41 kcal (100g of a 41 kcal/100g item) = 123.0; the missing
    # row contributes nothing to the sum, but is still counted as missing.
    assert recipes_csv["r_mixed"]["total_calories"] == "123.0"
    assert recipes_json["r_mixed"]["missing_nutrition_count"] == 1
    assert recipes_json["r_mixed"]["nutrition_status"] == "PARTIAL"


def test_genuine_zero_recipe_is_complete(reprocess_paths):
    reprocess_mod.reprocess()
    recipes_json = {r["id"]: r for r in json.loads(reprocess_paths["recipes_json"].read_text(encoding="utf-8"))}
    assert recipes_json["r_genuine_zero"]["nutrition_status"] == "COMPLETE"
    assert recipes_json["r_genuine_zero"]["missing_nutrition_count"] == 0


def test_reprocess_is_idempotent(reprocess_paths):
    reprocess_mod.reprocess()
    first_csv = reprocess_paths["ing_csv"].read_bytes()
    first_recipes_json = reprocess_paths["recipes_json"].read_bytes()
    reprocess_mod.reprocess()
    assert reprocess_paths["ing_csv"].read_bytes() == first_csv
    assert reprocess_paths["recipes_json"].read_bytes() == first_recipes_json


# ---------------------------------------------------------------------------
# scripts/fix_unmatched_invariants.py
# ---------------------------------------------------------------------------

@pytest.fixture
def invariant_paths(tmp_path, monkeypatch):
    # An invariant VIOLATION: match_method says UNMATCHED but a code/name/
    # nutrition are still populated from a stale prior state.
    ing_rows = [
        {"id": "v1", "recipe_id": "r1", "master_ingredient_code": "4007",
         "master_ingredient_name": "Cà rốt", "raw_text": "cà rốt", "cleaned_name": "cà rốt",
         "required_quantity": "1", "estimated_weight_g": "100.0", "match_confidence": "0.98",
         "match_method": "UNMATCHED", "calories": "41.0", "protein_g": "0.9", "fat_g": "0.2", "carbs_g": "9.6"},
        # A correctly-shaped UNMATCHED row (no code) must be left alone.
        {"id": "v2", "recipe_id": "r1", "master_ingredient_code": "",
         "master_ingredient_name": "", "raw_text": "lạ", "cleaned_name": "lạ",
         "required_quantity": "1", "estimated_weight_g": "10.0", "match_confidence": "",
         "match_method": "UNMATCHED", "calories": "", "protein_g": "", "fat_g": "", "carbs_g": ""},
        # A genuinely matched row must be left alone.
        {"id": "v3", "recipe_id": "r1", "master_ingredient_code": "4007",
         "master_ingredient_name": "Cà rốt", "raw_text": "cà rốt", "cleaned_name": "cà rốt",
         "required_quantity": "1", "estimated_weight_g": "100.0", "match_confidence": "1.00",
         "match_method": "EXACT_CATALOG_MATCH", "calories": "41.0", "protein_g": "0.9", "fat_g": "0.2", "carbs_g": "9.6"},
    ]
    ing_csv = tmp_path / "data" / "processed" / "recipes" / "recipe_ingredients.csv"
    ing_json = tmp_path / "data" / "processed" / "recipes" / "recipe_ingredients.json"
    ing_csv.parent.mkdir(parents=True, exist_ok=True)
    _write_csv(ing_csv, ing_rows, ING_FIELDS)
    ing_json.write_text(json.dumps(ing_rows, ensure_ascii=False), encoding="utf-8")
    monkeypatch.setattr(fix_invariants_mod, "ROOT", tmp_path)
    return ing_csv, ing_json


def test_invariant_fix_blanks_nutrition_not_zero_in_csv(invariant_paths):
    ing_csv, _ = invariant_paths
    fix_invariants_mod.fix_unmatched_invariants()
    rows = {r["id"]: r for r in _read_csv(ing_csv)}
    for field in ("calories", "protein_g", "fat_g", "carbs_g"):
        assert rows["v1"][field] == ""
    assert rows["v1"]["master_ingredient_code"] == ""
    assert rows["v1"]["master_ingredient_name"] == ""


def test_invariant_fix_writes_json_null_not_zero(invariant_paths):
    _, ing_json = invariant_paths
    fix_invariants_mod.fix_unmatched_invariants()
    rows = {r["id"]: r for r in json.loads(ing_json.read_text(encoding="utf-8"))}
    for field in ("calories", "protein_g", "fat_g", "carbs_g"):
        assert rows["v1"][field] is None


def test_invariant_fix_leaves_non_violating_rows_untouched(invariant_paths):
    ing_csv, _ = invariant_paths
    fix_invariants_mod.fix_unmatched_invariants()
    rows = {r["id"]: r for r in _read_csv(ing_csv)}
    assert rows["v2"]["calories"] == ""  # already-blank UNMATCHED row: unchanged
    assert rows["v3"]["calories"] == "41.0"  # matched row: unchanged
    assert rows["v3"]["master_ingredient_code"] == "4007"


def test_invariant_fix_is_idempotent(invariant_paths):
    ing_csv, ing_json = invariant_paths
    fix_invariants_mod.fix_unmatched_invariants()
    first_csv = ing_csv.read_bytes()
    first_json = ing_json.read_bytes()
    fix_invariants_mod.fix_unmatched_invariants()
    assert ing_csv.read_bytes() == first_csv
    assert ing_json.read_bytes() == first_json
