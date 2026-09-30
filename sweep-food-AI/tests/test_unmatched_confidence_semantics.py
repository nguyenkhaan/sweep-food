"""match_confidence contract for match_method == 'UNMATCHED' rows.

Evidence for the contract (see reports/eda/eda_findings.md "Van de 8" and the
now-removed nlp/map_crawled_ingredients.py at git ref ae51d8b): a since-deleted
mapper wrote a MATCH_THRESHOLD=0.78 acceptance rule where a rejected
candidate's raw confidence score was deliberately retained alongside a nulled
master_ingredient_code/name, and an untried name got an explicit 0.0. That
mechanism no longer exists anywhere in the active codebase (no current
matcher, Qwen pipeline, or post-processing step ever assigns match_method =
"UNMATCHED" with a meaningful confidence), no current consumer reads that
signal, and the EDA finding's own recommendation is to store any such
diagnostic separately (which the schema does not do) rather than overload
match_confidence. Under the current, active contract this is established
here: an UNMATCHED row must be null/blank across code, name AND confidence --
there is no live ambiguity-rejection sentinel in this codebase to preserve.

This does not touch matching thresholds, candidate ranking, nutrition
semantics (see tests/test_unmatched_nutrition_semantics.py), or Class B/C
Qwen rows.
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


def _row(id_, method, code="", name="", confidence="", calories="", protein="", fat="", carbs="",
         weight="10.0"):
    return {"id": id_, "recipe_id": "r1", "master_ingredient_code": code,
            "master_ingredient_name": name, "raw_text": "x", "cleaned_name": "x",
            "required_quantity": "1", "estimated_weight_g": weight,
            "match_confidence": confidence, "match_method": method,
            "calories": calories, "protein_g": protein, "fat_g": fat, "carbs_g": carbs}


# ---------------------------------------------------------------------------
# scripts/fix_unmatched_invariants.py
# ---------------------------------------------------------------------------

@pytest.fixture
def invariant_paths(tmp_path, monkeypatch):
    ing_rows = [
        # The newly-discovered shape: code/name already blank, but a stale
        # rejected-candidate confidence (e.g. from the removed 0.78-threshold
        # mapper) survives alone.
        _row("stale_conf_only", "UNMATCHED", confidence="0.65"),
        # The original invariant-violation shape: everything stale together.
        _row("fully_stale", "UNMATCHED", code="4007", name="Cà rốt", confidence="0.82",
             calories="41.0", protein="0.9", fat="0.2", carbs="9.6"),
        # Genuinely never matched: already fully blank -- must not be touched.
        _row("already_clean", "UNMATCHED"),
        # A real, valid match: must retain its real confidence untouched.
        _row("valid_match", "EXACT_CATALOG_MATCH", code="4007", name="Cà rốt",
             confidence="1.00", calories="41.0", protein="0.9", fat="0.2", carbs="9.6"),
    ]
    ing_csv = tmp_path / "data" / "processed" / "recipes" / "recipe_ingredients.csv"
    ing_json = tmp_path / "data" / "processed" / "recipes" / "recipe_ingredients.json"
    ing_csv.parent.mkdir(parents=True, exist_ok=True)
    _write_csv(ing_csv, ing_rows, ING_FIELDS)
    ing_json.write_text(json.dumps(ing_rows, ensure_ascii=False), encoding="utf-8")
    monkeypatch.setattr(fix_invariants_mod, "ROOT", tmp_path)
    return ing_csv, ing_json


def test_stale_confidence_alone_is_cleared_in_csv(invariant_paths):
    ing_csv, _ = invariant_paths
    fix_invariants_mod.fix_unmatched_invariants()
    rows = {r["id"]: r for r in _read_csv(ing_csv)}
    assert rows["stale_conf_only"]["match_confidence"] == ""
    assert rows["stale_conf_only"]["master_ingredient_code"] == ""


def test_stale_confidence_alone_is_cleared_in_json(invariant_paths):
    _, ing_json = invariant_paths
    fix_invariants_mod.fix_unmatched_invariants()
    rows = {r["id"]: r for r in json.loads(ing_json.read_text(encoding="utf-8"))}
    assert rows["stale_conf_only"]["match_confidence"] is None


def test_fully_stale_row_clears_confidence_alongside_code_and_nutrition(invariant_paths):
    ing_csv, _ = invariant_paths
    fix_invariants_mod.fix_unmatched_invariants()
    rows = {r["id"]: r for r in _read_csv(ing_csv)}
    row = rows["fully_stale"]
    assert row["master_ingredient_code"] == ""
    assert row["master_ingredient_name"] == ""
    assert row["match_confidence"] == ""
    assert row["calories"] == ""


def test_already_clean_unmatched_row_is_untouched(invariant_paths):
    ing_csv, _ = invariant_paths
    fix_invariants_mod.fix_unmatched_invariants()
    rows = {r["id"]: r for r in _read_csv(ing_csv)}
    assert rows["already_clean"]["match_confidence"] == ""


def test_valid_matched_row_retains_its_real_confidence(invariant_paths):
    ing_csv, _ = invariant_paths
    fix_invariants_mod.fix_unmatched_invariants()
    rows = {r["id"]: r for r in _read_csv(ing_csv)}
    row = rows["valid_match"]
    assert row["match_confidence"] == "1.00"
    assert row["master_ingredient_code"] == "4007"
    assert row["calories"] == "41.0"


def test_invariant_fix_confidence_clearing_is_idempotent(invariant_paths):
    ing_csv, ing_json = invariant_paths
    fix_invariants_mod.fix_unmatched_invariants()
    first_csv = ing_csv.read_bytes()
    first_json = ing_json.read_bytes()
    fix_invariants_mod.fix_unmatched_invariants()
    assert ing_csv.read_bytes() == first_csv
    assert ing_json.read_bytes() == first_json


# ---------------------------------------------------------------------------
# scripts/reprocess_recipe_weights_and_nutrition.py
# ---------------------------------------------------------------------------

@pytest.fixture
def reprocess_paths(tmp_path, monkeypatch):
    ing_rows = [
        _row("stale_conf_only", "UNMATCHED", confidence="0.65"),
        _row("already_clean", "UNMATCHED"),
        _row("valid_match", "EXACT_CATALOG_MATCH", code="4007", name="Cà rốt",
             confidence="1.00", weight="100.0"),
    ]
    recipes = [{"id": "r1", "total_calories": "0", "total_protein_g": "0", "total_fat_g": "0",
                "total_carbs_g": "0", "ingredients_count": "3"}]
    master_rows = [{"code": "4007", "name_vi": "Cà rốt", "category_vi": "Rau, quả, củ dùng làm rau",
                     "energy_kcal": "41", "protein_g": "0.9", "fat_g": "0.2", "carbs_g": "9.6"}]

    ing_csv = tmp_path / "data" / "processed" / "recipes" / "recipe_ingredients.csv"
    ing_json = tmp_path / "data" / "processed" / "recipes" / "recipe_ingredients.json"
    recipes_csv = tmp_path / "data" / "processed" / "recipes" / "recipes.csv"
    recipes_json = tmp_path / "data" / "processed" / "recipes" / "recipes.json"
    master_csv = tmp_path / "data" / "processed" / "viendinhduong" / "master_ingredients_nutrition.csv"
    for p in (ing_csv, recipes_csv, master_csv):
        p.parent.mkdir(parents=True, exist_ok=True)

    _write_csv(ing_csv, ing_rows, ING_FIELDS)
    ing_json.write_text(json.dumps(ing_rows, ensure_ascii=False), encoding="utf-8")
    _write_csv(recipes_csv, recipes, list(recipes[0].keys()))
    recipes_json.write_text(json.dumps(recipes, ensure_ascii=False), encoding="utf-8")
    _write_csv(master_csv, master_rows, list(master_rows[0].keys()))

    monkeypatch.setattr(reprocess_mod, "ROOT", tmp_path)
    return ing_csv


def test_reprocess_clears_stale_confidence_on_unmatched_rows(reprocess_paths):
    reprocess_mod.reprocess()
    rows = {r["id"]: r for r in _read_csv(reprocess_paths)}
    assert rows["stale_conf_only"]["match_confidence"] == ""
    assert rows["already_clean"]["match_confidence"] == ""


def test_reprocess_preserves_confidence_on_valid_match(reprocess_paths):
    reprocess_mod.reprocess()
    rows = {r["id"]: r for r in _read_csv(reprocess_paths)}
    assert rows["valid_match"]["match_confidence"] == "1.00"


def test_reprocess_confidence_clearing_is_idempotent(reprocess_paths):
    reprocess_mod.reprocess()
    first = reprocess_paths.read_bytes()
    reprocess_mod.reprocess()
    assert reprocess_paths.read_bytes() == first
