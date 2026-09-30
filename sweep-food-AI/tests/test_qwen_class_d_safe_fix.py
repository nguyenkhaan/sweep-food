"""Tests for scripts/eda/apply_qwen_class_d_safe_fix.py against small fixtures.

Never touches the real ~64k-row processed dataset: all module-level path
constants are monkeypatched to a tmp_path fixture, including inside
scripts.eda.audit_qwen_matching (whose audit() is called internally to
cross-check the live Class-D count before anything is written).
"""

import csv
import json

import pytest

import scripts.eda.apply_qwen_class_d_safe_fix as fix
import scripts.eda.audit_qwen_matching as audit_mod

CLEAR_ID, CLEAR_RAW_TEXT = fix.CLEAR_ROWS[0]
REMAP_ID = fix.REMAP_ROW_ID
REMAP_RAW_TEXT = fix.REMAP_RAW_TEXT


def _write_csv(path, rows, fieldnames):
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


ING_FIELDS = [
    "id", "recipe_id", "master_ingredient_code", "master_ingredient_name",
    "raw_text", "cleaned_name", "required_quantity", "match_confidence",
    "match_method", "estimated_weight_g", "calories", "protein_g", "fat_g", "carbs_g",
]


def _row(**kwargs):
    base = {f: "" for f in ING_FIELDS}
    base.update(kwargs)
    return base


@pytest.fixture
def fixture_paths(tmp_path, monkeypatch):
    master_csv = tmp_path / "master.csv"
    ing_csv = tmp_path / "recipe_ingredients.csv"
    ing_json = tmp_path / "recipe_ingredients.json"
    recipes_csv = tmp_path / "recipes.csv"
    recipes_json = tmp_path / "recipes.json"
    out_dir = tmp_path / "reports"

    master_fields = ["code", "name_vi", "energy_kcal", "protein_g", "fat_g", "carbs_g"]
    _write_csv(master_csv, [
        {"code": "4026", "name_vi": "Dọc mùng", "energy_kcal": "13", "protein_g": "0.4", "fat_g": "", "carbs_g": "2.8"},
        {"code": "4007", "name_vi": "Cà rốt", "energy_kcal": "41", "protein_g": "0.9", "fat_g": "0.2", "carbs_g": "9.6"},
    ], master_fields)

    ing_rows = [
        # Approved CLEAR row: dangling code 5074, matches the reviewed id+raw_text exactly.
        _row(id=CLEAR_ID, recipe_id="r-clear", master_ingredient_code="5074",
             master_ingredient_name="Xoài", raw_text=CLEAR_RAW_TEXT, cleaned_name="xoài",
             match_confidence="0.4272", match_method="QWEN_LLM_MATCH",
             estimated_weight_g="50.0", calories="0", protein_g="0.0", fat_g="0.0", carbs_g="0.0"),
        # Approved REMAP row: dangling code 13038, explicit dọc mùng raw text.
        _row(id=REMAP_ID, recipe_id="r-remap", master_ingredient_code="13038",
             master_ingredient_name="Bạc hà tươi", raw_text=REMAP_RAW_TEXT, cleaned_name="bạc hà",
             match_confidence="0.2875", match_method="QWEN_LLM_MATCH",
             estimated_weight_g="100.0", calories="13", protein_g="0.4", fat_g="0.0", carbs_g="2.8"),
        # A different dangling-code Qwen row NOT in the approved list (stand-in for a
        # NEEDS_REVIEW row): must never be touched by this script.
        _row(id="needs-review-row", recipe_id="r-needs-review", master_ingredient_code="5074",
             master_ingredient_name="Xoài", raw_text="Xoài cát chu vừa chín tới 600g",
             cleaned_name="xoài cát", match_confidence="0.54", match_method="QWEN_LLM_MATCH",
             estimated_weight_g="600.0", calories="0", protein_g="0.0", fat_g="0.0", carbs_g="0.0"),
        # Qwen Class-B/C-shaped row (valid current code): must never be touched.
        _row(id="qwen-bc-row", recipe_id="r-bc", master_ingredient_code="4007",
             master_ingredient_name="Cà rốt", raw_text="2 củ cà rốt to", cleaned_name="cà rốt",
             match_confidence="0.98", match_method="QWEN_LLM_MATCH",
             estimated_weight_g="80.0", calories="33", protein_g="0.7", fat_g="0.2", carbs_g="7.7"),
        # Already-UNMATCHED row: invariants (blank code/name/confidence/nutrition) must hold.
        _row(id="unmatched-row", recipe_id="r-um", master_ingredient_code="",
             master_ingredient_name="", raw_text="gia vị không rõ", cleaned_name="gia vị",
             match_confidence="", match_method="UNMATCHED",
             estimated_weight_g="10.0", calories="", protein_g="", fat_g="", carbs_g=""),
    ]
    _write_csv(ing_csv, ing_rows, ING_FIELDS)
    ing_json.write_text(json.dumps(ing_rows, ensure_ascii=False), encoding="utf-8")

    recipe_fields = ["id", "total_calories", "total_protein_g", "total_fat_g", "total_carbs_g", "ingredients_count"]
    recipes = [
        {"id": "r-clear", "total_calories": "0", "total_protein_g": "0.0", "total_fat_g": "0.0",
         "total_carbs_g": "0.0", "ingredients_count": "1"},
        {"id": "r-remap", "total_calories": "13", "total_protein_g": "0.4", "total_fat_g": "0.0",
         "total_carbs_g": "2.8", "ingredients_count": "1"},
        {"id": "r-needs-review", "total_calories": "0", "total_protein_g": "0.0", "total_fat_g": "0.0",
         "total_carbs_g": "0.0", "ingredients_count": "1"},
        {"id": "r-bc", "total_calories": "33", "total_protein_g": "0.7", "total_fat_g": "0.2",
         "total_carbs_g": "7.7", "ingredients_count": "1"},
        {"id": "r-um", "total_calories": "0", "total_protein_g": "0.0", "total_fat_g": "0.0",
         "total_carbs_g": "0.0", "ingredients_count": "1"},
    ]
    _write_csv(recipes_csv, recipes, recipe_fields)
    # Status/missing-count reflect each recipe's real pre-fix ingredient truth
    # (r-um's only row already has empty/missing calories) so that the status
    # recompute pass -- which runs over every recipe, not just the 31 targets
    # -- only reports a change where this fix actually changed something.
    initial_status = {
        "r-clear": ("COMPLETE", 0), "r-remap": ("COMPLETE", 0),
        "r-needs-review": ("COMPLETE", 0), "r-bc": ("COMPLETE", 0),
        "r-um": ("INCOMPLETE", 1),
    }
    recipes_json_rows = [
        dict(r, nutrition_status=initial_status[r["id"]][0], missing_nutrition_count=initial_status[r["id"]][1])
        for r in recipes
    ]
    recipes_json.write_text(json.dumps(recipes_json_rows, ensure_ascii=False), encoding="utf-8")

    monkeypatch.setattr(audit_mod, "ING", ing_csv)
    monkeypatch.setattr(audit_mod, "MASTER", master_csv)
    monkeypatch.setattr(fix, "ING", ing_csv)
    monkeypatch.setattr(fix, "ING_JSON", ing_json)
    monkeypatch.setattr(fix, "MASTER", master_csv)
    monkeypatch.setattr(fix, "RECIPES_CSV", recipes_csv)
    monkeypatch.setattr(fix, "RECIPES_JSON", recipes_json)
    monkeypatch.setattr(fix, "OUT", out_dir)
    # This fixture models the shape of a 74-row Class D / 700-row Qwen world with
    # exactly two extra rows standing in for the 42 other untouched rows; patch the
    # hard cross-checks in build_plan() to match this fixture's actual size (2 target
    # + 1 stand-in = 3 Class-D rows here) rather than the real dataset's 74/31.
    monkeypatch.setattr(fix, "TARGET_IDS", frozenset([CLEAR_ID, REMAP_ID]))
    monkeypatch.setattr(
        fix, "CLEAR_ROWS", tuple(r for r in fix.CLEAR_ROWS if r[0] == CLEAR_ID)
    )
    # This fixture's world has 3 Class-D rows total (2 approved targets + 1
    # needs-review stand-in), not the real dataset's 74.
    monkeypatch.setattr(fix, "EXPECTED_CLASS_D_COUNT", 3)

    return {
        "ing_csv": ing_csv, "ing_json": ing_json,
        "recipes_csv": recipes_csv, "recipes_json": recipes_json,
    }


def test_preview_does_not_write_any_file(fixture_paths):
    before = fixture_paths["ing_csv"].read_bytes()
    report = fix.run(apply=False)
    assert report["status"] == "preview"
    assert report["clear_applied_now"] == 1
    assert report["remap_applied_now"] == 1
    assert fixture_paths["ing_csv"].read_bytes() == before


def test_apply_clears_only_the_approved_row(fixture_paths):
    report = fix.run(apply=True)
    assert report["status"] == "applied"
    assert report["clear_applied_now"] == 1

    rows = {r["id"]: r for r in csv.DictReader(fixture_paths["ing_csv"].open(encoding="utf-8-sig", newline=""))}
    cleared = rows[CLEAR_ID]
    assert cleared["master_ingredient_code"] in (None, "")
    assert cleared["master_ingredient_name"] in (None, "")
    assert cleared["match_method"] == "UNMATCHED"
    assert cleared["match_confidence"] in (None, "")
    for f in ("calories", "protein_g", "fat_g", "carbs_g"):
        assert cleared[f] in (None, ""), f"{f} should be null, not zero"

    untouched_needs_review = rows["needs-review-row"]
    assert untouched_needs_review["master_ingredient_code"] == "5074"
    assert untouched_needs_review["match_method"] == "QWEN_LLM_MATCH"


def test_clear_uses_null_not_zero_for_nutrition(fixture_paths):
    fix.run(apply=True)
    rows = {r["id"]: r for r in csv.DictReader(fixture_paths["ing_csv"].open(encoding="utf-8-sig", newline=""))}
    cleared = rows[CLEAR_ID]
    for f in ("calories", "protein_g", "fat_g", "carbs_g"):
        assert cleared[f] != "0" and cleared[f] != "0.0"


def test_apply_remaps_using_current_catalog_identity_and_nutrition(fixture_paths):
    report = fix.run(apply=True)
    assert report["remap_applied_now"] == 1

    rows = {r["id"]: r for r in csv.DictReader(fixture_paths["ing_csv"].open(encoding="utf-8-sig", newline=""))}
    remapped = rows[REMAP_ID]
    assert remapped["master_ingredient_code"] == "4026"
    assert remapped["master_ingredient_name"] == "Dọc mùng"
    assert remapped["match_method"] == "QWEN_LLM_MATCH"
    assert remapped["match_confidence"] == fix.QWEN_MATCH_CONFIDENCE
    # weight is 100g and master 4026 carries 13 kcal / 0.4 protein / (missing fat) / 2.8 carbs per 100g
    assert remapped["calories"] == "13.0"
    assert remapped["protein_g"] == "0.4"
    assert remapped["carbs_g"] == "2.8"
    assert remapped["fat_g"] in (None, ""), "master has no fat_g for 4026; must stay null, not the old stale 0.0"


def test_remap_requires_exact_catalog_identity_match(tmp_path, monkeypatch, fixture_paths):
    """If the catalog's name_vi for 4026 drifts away from 'Dọc mùng', the
    remap must refuse to run rather than publish a stale/mismatched identity."""
    master_csv = tmp_path / "master.csv"
    _write_csv(master_csv, [
        {"code": "4026", "name_vi": "Something Else", "energy_kcal": "13", "protein_g": "0.4", "fat_g": "", "carbs_g": "2.8"},
    ], ["code", "name_vi", "energy_kcal", "protein_g", "fat_g", "carbs_g"])
    monkeypatch.setattr(audit_mod, "MASTER", master_csv)
    monkeypatch.setattr(fix, "MASTER", master_csv)

    with pytest.raises(fix.DriftError):
        fix.run(apply=False)


def test_needs_review_rows_remain_untouched(fixture_paths):
    before = json.loads(fixture_paths["ing_json"].read_text(encoding="utf-8"))
    before_row = next(r for r in before if r["id"] == "needs-review-row")

    fix.run(apply=True)

    after = json.loads(fixture_paths["ing_json"].read_text(encoding="utf-8"))
    after_row = next(r for r in after if r["id"] == "needs-review-row")
    assert after_row == before_row


def test_qwen_bc_row_preserved(fixture_paths):
    fix.run(apply=True)
    rows = {r["id"]: r for r in csv.DictReader(fixture_paths["ing_csv"].open(encoding="utf-8-sig", newline=""))}
    bc = rows["qwen-bc-row"]
    assert bc["master_ingredient_code"] == "4007"
    assert bc["match_confidence"] == "0.98"
    assert bc["calories"] == "33"


def test_unmatched_invariants_preserved(fixture_paths):
    fix.run(apply=True)
    rows = {r["id"]: r for r in csv.DictReader(fixture_paths["ing_csv"].open(encoding="utf-8-sig", newline=""))}
    um = rows["unmatched-row"]
    assert um["match_method"] == "UNMATCHED"
    assert um["master_ingredient_code"] in (None, "")
    assert um["calories"] in (None, "")


def test_recipe_rollups_and_status_recomputed(fixture_paths):
    fix.run(apply=True)
    recipes = {r["id"]: r for r in csv.DictReader(fixture_paths["recipes_csv"].open(encoding="utf-8-sig", newline=""))}
    # r-remap: still 100g of code 4026 at 13 kcal/100g -> unchanged total.
    assert recipes["r-remap"]["total_calories"] == "13.0"
    # r-clear: cleared row already contributed 0 kcal before (fake zero); stays 0.
    assert recipes["r-clear"]["total_calories"] == "0.0"

    recipes_json = {r["id"]: r for r in json.loads(fixture_paths["recipes_json"].read_text(encoding="utf-8"))}
    # r-clear's only ingredient row now has null calories -> recipe flips to INCOMPLETE.
    assert recipes_json["r-clear"]["nutrition_status"] == "INCOMPLETE"
    assert recipes_json["r-clear"]["missing_nutrition_count"] == 1
    # r-remap's calories stayed non-null -> status unaffected.
    assert recipes_json["r-remap"]["nutrition_status"] == "COMPLETE"
    assert recipes_json["r-remap"]["missing_nutrition_count"] == 0
    # Unrelated recipes must show no change at all.
    assert recipes_json["r-bc"]["nutrition_status"] == "COMPLETE"
    assert recipes_json["r-needs-review"]["nutrition_status"] == "COMPLETE"


def test_report_distinguishes_missing_count_bump_from_status_label_change(fixture_paths):
    """Regression: a prior version conflated 'missing_nutrition_count changed'
    with 'nutrition_status label changed' into one ambiguous counter, which
    produced a real reporting inconsistency (a summary claiming '8 changed'
    against its own '5 + 4' breakdown that actually summed to 9). r-clear is a
    single-ingredient recipe, so clearing its only row's nutrition jumps it
    straight from COMPLETE to INCOMPLETE (skipping PARTIAL) -- both counters
    must reflect exactly that one recipe, and the transition breakdown must
    name the exact transition rather than a generic 'changed' bucket."""
    report = fix.run(apply=True)
    assert report["recipes_with_changed_missing_count"] == 1
    assert report["recipes_with_status_label_changed"] == 1
    assert report["status_transitions"]["COMPLETE -> INCOMPLETE"] == 1
    assert report["status_transitions"]["unchanged"] == 4


def test_needs_review_untouched_count_is_stable_across_reruns(fixture_paths):
    """Regression: needs_review_untouched must reflect the fixed 'other Class-D
    rows' population, not the raw post-audit Class-D count -- the raw count
    shrinks once target rows are applied and leave Class D, which previously
    made this field wrongly drop after the first --apply."""
    report1 = fix.run(apply=True)
    report2 = fix.run(apply=True)
    assert report1["needs_review_untouched"] == 1
    assert report2["needs_review_untouched"] == 1


def test_idempotent_second_apply_is_a_no_op(fixture_paths):
    fix.run(apply=True)
    after_first = fixture_paths["ing_csv"].read_bytes()
    recipes_after_first = fixture_paths["recipes_csv"].read_bytes()

    report2 = fix.run(apply=True)
    assert report2["status"] == "applied"
    assert report2["clear_already_applied"] == 1
    assert report2["clear_applied_now"] == 0
    assert report2["remap_already_applied"] == 1
    assert report2["remap_applied_now"] == 0

    assert fixture_paths["ing_csv"].read_bytes() == after_first
    assert fixture_paths["recipes_csv"].read_bytes() == recipes_after_first


def test_run_preview_is_deterministic(fixture_paths):
    report1 = fix.run(apply=False)
    report2 = fix.run(apply=False)
    assert report1 == report2


def test_raw_text_drift_aborts_before_writing_anything(fixture_paths):
    rows = list(csv.DictReader(fixture_paths["ing_csv"].open(encoding="utf-8-sig", newline="")))
    for r in rows:
        if r["id"] == CLEAR_ID:
            r["raw_text"] = "some other ingredient entirely"
    _write_csv(fixture_paths["ing_csv"], rows, ING_FIELDS)
    before = fixture_paths["ing_csv"].read_bytes()
    before_recipes = fixture_paths["recipes_csv"].read_bytes()

    with pytest.raises(fix.DriftError):
        fix.run(apply=True)

    assert fixture_paths["ing_csv"].read_bytes() == before
    assert fixture_paths["recipes_csv"].read_bytes() == before_recipes
