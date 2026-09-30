"""Tests for the rib/bone (suon) PRESET_ALIAS contamination fix.

Two layers:

  * Fixture tests exercise scripts/eda/apply_suon_rib_alias_safe_fix.py against
    a small tmp_path dataset -- every module-level path constant is
    monkeypatched, so the real ~64k-row processed dataset and the real alias
    map are never touched.
  * Real-data tests assert the applied outcome on the committed processed
    dataset: the five alias decisions, the 12 reviewed row outcomes, and the
    populations that must NOT have moved (the 15 correct "sườn non heo" rows
    and the legitimate "Giò lụa" rows on 7069).

One assertion pins the 7069 population jointly with Batch A of the 70xx
meat-band audit, which later repointed "chả lụa" onto 7069.
"""

import csv
import json
from pathlib import Path

import pytest

import scripts.eda.apply_meat_band_batch_a_alias_safe_fix as batch_a
import scripts.eda.apply_suon_rib_alias_safe_fix as fix

ROOT = Path(__file__).resolve().parent.parent
ALIAS_PATH = ROOT / "data/processed/viendinhduong/ingredient_alias_map.json"
ING_CSV = ROOT / "data/processed/recipes/recipe_ingredients.csv"
ING_JSON = ROOT / "data/processed/recipes/recipe_ingredients.json"

CONTAMINATED_CODE = "7069"
RIB_CODE = "7053"
RIB_NAME = "Sườn heo (xương heo)"

# The two rows with no valid catalog target.
AMBIGUOUS_ROW_ID = "c9c53624-3d09-4680-9bed-fc9590d5b8ad"  # "3 lát sườn", pork-hock recipe
BEEF_RIB_ROW_ID = "78e45baf-dd51-4f0e-8d7a-ba4cee3612e2"  # "Sườn 1 kg", "Sườn bò hầm mềm"

# Two row-level remaps called out for explicit safeguarding.
PORK_CHOP_ROW_ID = "19504d22-3999-4ae0-bca7-db81df889ad5"  # "2 miếng Sườn"
BBQ_PORK_RIB_ROW_ID = "ac206911-216e-4742-adfa-a7bd9d199e58"  # "4 dẻ sườn", BBQ Pork Rib

# Legitimate Giò lụa rows on 7069 -- EXACT_CATALOG matches that must never move.
LEGIT_GIO_LUA_ROW_IDS = (
    "a14a7764-e2fc-433c-a9e7-de7a8842111b",
    "83a86aea-51a3-423b-9f23-44c215d900c4",
    "86f68bfa-3dce-4d63-8875-c1cb7a4f9e97",
    "b9a86de7-a679-4a41-be34-996d6a7d1a07",
    "2b2b749c-2bc3-4a03-b90c-a2016493a546",
    "a1513916-d715-41c9-b359-f50eb8959c3c",
    "05db21bc-07b8-4870-b602-4289a1a27f5c",
)

SUON_NON_HEO_CLEANED_NAME = "sườn non heo"
EXPECTED_SUON_NON_HEO_ROWS = 15

NUTRITION_FIELDS = ("calories", "protein_g", "fat_g", "carbs_g")


def _blank(value):
    return value is None or str(value).strip() == ""


# =====================================================================
# Fixture-based tests of the remediation script
# =====================================================================

ING_FIELDS = [
    "id", "recipe_id", "master_ingredient_code", "master_ingredient_name",
    "raw_text", "cleaned_name", "required_quantity", "unit_vi", "unit",
    "preparation_note", "match_confidence", "match_method",
    "estimated_weight_g", "calories", "protein_g", "fat_g", "carbs_g",
]


def _write_csv(path, rows, fieldnames):
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def _row(**kwargs):
    base = {f: "" for f in ING_FIELDS}
    base.update(kwargs)
    return base


def _contaminated_row(rid, raw_text, recipe_id, cleaned_name, weight):
    """A row in the exact pre-fix state: 7069 / Giò lụa / PRESET_ALIAS / 0.98.

    Nutrition is 7069's profile scaled to the row weight, matching what the
    fixture catalog below declares, so the script's pending-probe accepts it.
    """
    factor = weight / 100.0
    return _row(
        id=rid, recipe_id=recipe_id,
        master_ingredient_code=fix.OLD_CODE, master_ingredient_name=fix.OLD_NAME,
        raw_text=raw_text, cleaned_name=cleaned_name,
        required_quantity=str(weight), unit_vi="g", unit="GRAM",
        match_confidence=fix.PRESET_ALIAS_CONFIDENCE, match_method=fix.PRESET_ALIAS_METHOD,
        estimated_weight_g=str(round(weight, 1)),
        calories=str(round(205 * factor, 1)), protein_g=str(round(16.9 * factor, 1)),
        fat_g=str(round(15.0 * factor, 1)), carbs_g=str(round(1.8 * factor, 1)),
    )


@pytest.fixture
def fixture_paths(tmp_path, monkeypatch):
    alias_path = tmp_path / "ingredient_alias_map.json"
    master_csv = tmp_path / "master.csv"
    ing_csv = tmp_path / "recipe_ingredients.csv"
    ing_json = tmp_path / "recipe_ingredients.json"
    recipes_csv = tmp_path / "recipes.csv"
    recipes_json = tmp_path / "recipes.json"
    out_dir = tmp_path / "reports"

    alias_map = {key: fix.OLD_CODE for key in fix.ALIAS_REPOINTS}
    alias_map.update({key: fix.OLD_CODE for key in fix.ALIAS_REMOVALS})
    # Already-correct rib/bone aliases that must survive untouched.
    alias_map.update({key: RIB_CODE for key in fix.ALIAS_MUST_REMAIN_7053})
    # Out-of-scope rib aliases that must survive untouched. "sườn cốt lết" sat
    # on 7070 when this fix ran and has since been repointed to 7053 by the
    # reviewed Batch-A follow-up; it is carried at its CURRENT value so the
    # fixture proves this fix leaves it alone wherever it points.
    alias_map.update({
        "sườn cốt lết": RIB_CODE,
        "sườn bò": "7094",
        "dẻ sườn bò": "7094",
        "thịt ba chỉ rút sườn": "7082",
        "giò lụa": fix.OLD_CODE,
    })
    alias_path.write_text(json.dumps(alias_map, ensure_ascii=False, indent=2), encoding="utf-8")

    master_fields = ["code", "name_vi", "energy_kcal", "protein_g", "fat_g", "carbs_g"]
    _write_csv(master_csv, [
        # 7053 carries no carbs value -- remapped rows must end up null, not 0.0.
        {"code": RIB_CODE, "name_vi": RIB_NAME, "energy_kcal": "187",
         "protein_g": "17.9", "fat_g": "12.8", "carbs_g": ""},
        {"code": fix.OLD_CODE, "name_vi": fix.OLD_NAME, "energy_kcal": "205",
         "protein_g": "16.9", "fat_g": "15", "carbs_g": "1.8"},
        {"code": "7094", "name_vi": "Thịt bắp bò", "energy_kcal": "150",
         "protein_g": "21.0", "fat_g": "7.0", "carbs_g": ""},
    ], master_fields)

    weights = {}
    ing_rows = []
    for i, (rid, raw_text) in enumerate(fix.REMAP_ROWS):
        weight = 100.0 * (i + 1)
        weights[rid] = weight
        ing_rows.append(_contaminated_row(rid, raw_text, f"r-remap-{i}", "sườn", weight))
    for i, (rid, raw_text) in enumerate(fix.CLEAR_ROWS):
        weight = 150.0 * (i + 1)
        weights[rid] = weight
        ing_rows.append(_contaminated_row(rid, raw_text, f"r-clear-{i}", "sườn", weight))

    # Populations that must never move.
    ing_rows.append(_row(
        id="suon-non-heo-correct", recipe_id="r-correct", master_ingredient_code=RIB_CODE,
        master_ingredient_name=RIB_NAME, raw_text="Sườn non heo 200g",
        cleaned_name=SUON_NON_HEO_CLEANED_NAME, required_quantity="200.0", unit_vi="g", unit="GRAM",
        match_confidence=fix.PRESET_ALIAS_CONFIDENCE, match_method=fix.PRESET_ALIAS_METHOD,
        estimated_weight_g="200.0", calories="374.0", protein_g="35.8", fat_g="25.6", carbs_g="",
    ))
    ing_rows.append(_row(
        id="gio-lua-legit", recipe_id="r-gio-lua", master_ingredient_code=fix.OLD_CODE,
        master_ingredient_name=fix.OLD_NAME, raw_text="Giò lụa 100 gr", cleaned_name="giò lụa",
        required_quantity="100.0", unit_vi="g", unit="GRAM",
        match_confidence="1.0", match_method="EXACT_CATALOG_MATCH",
        estimated_weight_g="100.0", calories="205.0", protein_g="16.9", fat_g="15.0", carbs_g="1.8",
    ))
    ing_rows.append(_row(
        id="suon-bo-out-of-scope", recipe_id="r-suon-bo", master_ingredient_code="7094",
        master_ingredient_name="Thịt bắp bò", raw_text="Sườn bò 300g", cleaned_name="sườn bò",
        required_quantity="300.0", unit_vi="g", unit="GRAM",
        match_confidence=fix.PRESET_ALIAS_CONFIDENCE, match_method=fix.PRESET_ALIAS_METHOD,
        estimated_weight_g="300.0", calories="450.0", protein_g="63.0", fat_g="21.0", carbs_g="",
    ))

    _write_csv(ing_csv, ing_rows, ING_FIELDS)
    ing_json.write_text(json.dumps(ing_rows, ensure_ascii=False), encoding="utf-8")

    recipe_fields = ["id", "total_calories", "total_protein_g", "total_fat_g",
                     "total_carbs_g", "ingredients_count"]
    recipes = []
    for row in ing_rows:
        recipes.append({
            "id": row["recipe_id"],
            "total_calories": row["calories"] or "0.0",
            "total_protein_g": row["protein_g"] or "0.0",
            "total_fat_g": row["fat_g"] or "0.0",
            "total_carbs_g": row["carbs_g"] or "0.0",
            "ingredients_count": "1",
        })
    _write_csv(recipes_csv, recipes, recipe_fields)
    recipes_json.write_text(json.dumps(
        [dict(r, nutrition_status="COMPLETE", missing_nutrition_count=0) for r in recipes],
        ensure_ascii=False), encoding="utf-8")

    monkeypatch.setattr(fix, "ALIAS_PATH", alias_path)
    monkeypatch.setattr(fix, "MASTER", master_csv)
    monkeypatch.setattr(fix, "ING", ing_csv)
    monkeypatch.setattr(fix, "ING_JSON", ing_json)
    monkeypatch.setattr(fix, "RECIPES_CSV", recipes_csv)
    monkeypatch.setattr(fix, "RECIPES_JSON", recipes_json)
    monkeypatch.setattr(fix, "OUT", out_dir)

    return {
        "alias_path": alias_path, "ing_csv": ing_csv, "ing_json": ing_json,
        "recipes_csv": recipes_csv, "recipes_json": recipes_json, "weights": weights,
    }


def _fx_alias_map(paths):
    return json.loads(paths["alias_path"].read_text(encoding="utf-8"))


def _fx_rows(paths):
    return {r["id"]: r for r in csv.DictReader(paths["ing_csv"].open(encoding="utf-8", newline=""))}


# --- Alias policy -------------------------------------------------------

def test_fixture_three_qualified_aliases_repointed_to_7053(fixture_paths):
    fix.run(apply=True)
    alias_map = _fx_alias_map(fixture_paths)
    for key in fix.ALIAS_REPOINTS:
        assert alias_map[key] == RIB_CODE, f"{key!r} should point at {RIB_CODE}"


def test_fixture_bare_suon_alias_removed(fixture_paths):
    fix.run(apply=True)
    assert "sườn" not in _fx_alias_map(fixture_paths)


def test_fixture_de_suon_alias_removed(fixture_paths):
    fix.run(apply=True)
    assert "dẻ sườn" not in _fx_alias_map(fixture_paths)


def test_fixture_no_reviewed_alias_still_points_at_7069(fixture_paths):
    fix.run(apply=True)
    alias_map = _fx_alias_map(fixture_paths)
    for key in tuple(fix.ALIAS_REPOINTS) + tuple(fix.ALIAS_REMOVALS):
        assert alias_map.get(key) != CONTAMINATED_CODE


def test_fixture_correct_rib_aliases_preserved(fixture_paths):
    fix.run(apply=True)
    alias_map = _fx_alias_map(fixture_paths)
    for key in fix.ALIAS_MUST_REMAIN_7053:
        assert alias_map[key] == RIB_CODE, f"correct rib alias {key!r} changed"


def test_fixture_out_of_scope_aliases_untouched(fixture_paths):
    fix.run(apply=True)
    alias_map = _fx_alias_map(fixture_paths)
    assert alias_map["sườn cốt lết"] == RIB_CODE
    assert alias_map["sườn bò"] == "7094"
    assert alias_map["dẻ sườn bò"] == "7094"
    assert alias_map["thịt ba chỉ rút sườn"] == "7082"
    assert alias_map["giò lụa"] == CONTAMINATED_CODE


def test_fixture_only_the_five_target_keys_change(fixture_paths):
    before = _fx_alias_map(fixture_paths)
    fix.run(apply=True)
    after = _fx_alias_map(fixture_paths)
    touched = set(fix.ALIAS_REPOINTS) | set(fix.ALIAS_REMOVALS)
    for key, value in before.items():
        if key in touched:
            continue
        assert after.get(key) == value, f"unrelated alias {key!r} changed"


def test_fixture_no_broad_suon_alias_is_created(fixture_paths):
    fix.run(apply=True)
    alias_map = _fx_alias_map(fixture_paths)
    assert alias_map.get("sườn") is None
    assert alias_map.get("dẻ sườn") is None


# --- Row outcomes -------------------------------------------------------

def test_fixture_ten_remapped_two_cleared(fixture_paths):
    report = fix.run(apply=True)
    assert report["remap_applied_now"] == 10
    assert report["clear_applied_now"] == 2
    assert report["remap_alias_driven_count"] == 6
    assert report["remap_row_level_count"] == 4


def test_fixture_remapped_rows_carry_7053_identity(fixture_paths):
    fix.run(apply=True)
    rows = _fx_rows(fixture_paths)
    for rid, _ in fix.REMAP_ROWS:
        row = rows[rid]
        assert row["master_ingredient_code"] == RIB_CODE
        assert row["master_ingredient_name"] == RIB_NAME
        assert row["match_method"] == fix.PRESET_ALIAS_METHOD
        assert row["match_confidence"] == fix.PRESET_ALIAS_CONFIDENCE


def test_fixture_remapped_nutrition_scaled_from_7053(fixture_paths):
    fix.run(apply=True)
    rows = _fx_rows(fixture_paths)
    for rid, _ in fix.REMAP_ROWS:
        weight = fixture_paths["weights"][rid]
        row = rows[rid]
        assert row["calories"] == str(round(187 * weight / 100.0, 1))
        assert row["protein_g"] == str(round(17.9 * weight / 100.0, 1))
        assert row["fat_g"] == str(round(12.8 * weight / 100.0, 1))
        # 7053 has no carbs value: unknown must stay null, never a measured 0.0.
        assert _blank(row["carbs_g"]), f"row {rid} carbs should be null, got {row['carbs_g']!r}"


def test_fixture_cleared_rows_follow_unmatched_contract(fixture_paths):
    fix.run(apply=True)
    rows = _fx_rows(fixture_paths)
    for rid, _ in fix.CLEAR_ROWS:
        row = rows[rid]
        assert _blank(row["master_ingredient_code"])
        assert _blank(row["master_ingredient_name"])
        assert row["match_method"] == "UNMATCHED"
        assert _blank(row["match_confidence"]), "0.0 must not be used as a confidence sentinel"
        for field in NUTRITION_FIELDS:
            assert _blank(row[field]), f"{field} must be null for cleared row {rid}"


def test_fixture_cleared_rows_preserve_raw_text_cleaned_name_and_weight(fixture_paths):
    before = _fx_rows(fixture_paths)
    fix.run(apply=True)
    after = _fx_rows(fixture_paths)
    for rid, _ in fix.CLEAR_ROWS:
        for field in ("raw_text", "cleaned_name", "estimated_weight_g"):
            assert after[rid][field] == before[rid][field]


def test_fixture_beef_rib_row_never_mapped_to_pork_or_substitute_beef(fixture_paths):
    fix.run(apply=True)
    row = _fx_rows(fixture_paths)[BEEF_RIB_ROW_ID]
    assert row["match_method"] == "UNMATCHED"
    for code in fix.BEEF_RIB_FORBIDDEN_CODES:
        assert row["master_ingredient_code"] != code


def test_fixture_ambiguous_row_remains_unmatched(fixture_paths):
    fix.run(apply=True)
    assert _fx_rows(fixture_paths)[AMBIGUOUS_ROW_ID]["match_method"] == "UNMATCHED"


def test_fixture_pork_chop_and_bbq_rib_rows_map_to_7053(fixture_paths):
    fix.run(apply=True)
    rows = _fx_rows(fixture_paths)
    assert rows[PORK_CHOP_ROW_ID]["master_ingredient_code"] == RIB_CODE
    assert rows[BBQ_PORK_RIB_ROW_ID]["master_ingredient_code"] == RIB_CODE


def test_fixture_correct_suon_non_heo_row_does_not_regress(fixture_paths):
    before = _fx_rows(fixture_paths)["suon-non-heo-correct"]
    fix.run(apply=True)
    after = _fx_rows(fixture_paths)["suon-non-heo-correct"]
    assert after == before
    assert after["master_ingredient_code"] == RIB_CODE


def test_fixture_legit_gio_lua_row_untouched(fixture_paths):
    before = _fx_rows(fixture_paths)["gio-lua-legit"]
    fix.run(apply=True)
    after = _fx_rows(fixture_paths)["gio-lua-legit"]
    assert after == before
    assert after["master_ingredient_code"] == CONTAMINATED_CODE


def test_fixture_out_of_scope_suon_bo_row_untouched(fixture_paths):
    before = _fx_rows(fixture_paths)["suon-bo-out-of-scope"]
    fix.run(apply=True)
    assert _fx_rows(fixture_paths)["suon-bo-out-of-scope"] == before


def test_fixture_no_unrelated_row_changes(fixture_paths):
    before = {r["id"]: r for r in json.loads(fixture_paths["ing_json"].read_text(encoding="utf-8"))}
    fix.run(apply=True)
    after = {r["id"]: r for r in json.loads(fixture_paths["ing_json"].read_text(encoding="utf-8"))}
    for rid, row in before.items():
        if rid in fix.TARGET_IDS:
            continue
        assert after[rid] == row, f"unrelated row {rid} changed"


# --- Dry-run / idempotence / drift ---------------------------------------

def test_fixture_preview_writes_nothing(fixture_paths):
    before_alias = fixture_paths["alias_path"].read_bytes()
    before_ing = fixture_paths["ing_csv"].read_bytes()
    report = fix.run(apply=False)
    assert report["status"] == "preview"
    assert report["remap_applied_now"] == 10
    assert report["clear_applied_now"] == 2
    assert fixture_paths["alias_path"].read_bytes() == before_alias
    assert fixture_paths["ing_csv"].read_bytes() == before_ing


def test_fixture_preview_is_deterministic(fixture_paths):
    assert fix.run(apply=False) == fix.run(apply=False)


def test_fixture_second_apply_is_a_no_op(fixture_paths):
    fix.run(apply=True)
    after_first = (
        fixture_paths["ing_csv"].read_bytes(),
        fixture_paths["alias_path"].read_bytes(),
        fixture_paths["recipes_csv"].read_bytes(),
    )
    report = fix.run(apply=True)
    assert report["remap_applied_now"] == 0
    assert report["remap_already_applied"] == 10
    assert report["clear_applied_now"] == 0
    assert report["clear_already_applied"] == 2
    assert all(v == "already_applied" for v in report["alias_states"].values())
    assert (
        fixture_paths["ing_csv"].read_bytes(),
        fixture_paths["alias_path"].read_bytes(),
        fixture_paths["recipes_csv"].read_bytes(),
    ) == after_first


def test_fixture_raw_text_drift_aborts_before_writing(fixture_paths):
    rows = list(csv.DictReader(fixture_paths["ing_csv"].open(encoding="utf-8", newline="")))
    for r in rows:
        if r["id"] == fix.REMAP_ROWS[0][0]:
            r["raw_text"] = "something else entirely"
    _write_csv(fixture_paths["ing_csv"], rows, ING_FIELDS)
    before_alias = fixture_paths["alias_path"].read_bytes()
    before_ing = fixture_paths["ing_csv"].read_bytes()

    with pytest.raises(fix.DriftError):
        fix.run(apply=True)

    assert fixture_paths["alias_path"].read_bytes() == before_alias
    assert fixture_paths["ing_csv"].read_bytes() == before_ing


def test_fixture_unexpected_alias_value_aborts_before_writing(fixture_paths):
    alias_map = _fx_alias_map(fixture_paths)
    alias_map["sườn non heo"] = "9999"
    fixture_paths["alias_path"].write_text(
        json.dumps(alias_map, ensure_ascii=False), encoding="utf-8")
    before_ing = fixture_paths["ing_csv"].read_bytes()

    with pytest.raises(fix.DriftError):
        fix.run(apply=True)

    assert fixture_paths["ing_csv"].read_bytes() == before_ing


def test_fixture_missing_repoint_alias_aborts(fixture_paths):
    alias_map = _fx_alias_map(fixture_paths)
    del alias_map["xương sườn heo"]
    fixture_paths["alias_path"].write_text(
        json.dumps(alias_map, ensure_ascii=False), encoding="utf-8")
    with pytest.raises(fix.DriftError):
        fix.run(apply=False)


def test_fixture_remap_requires_exact_catalog_identity(tmp_path, monkeypatch, fixture_paths):
    """If the catalog's name_vi for 7053 drifts, the remap must refuse to run
    rather than publish a stale identity."""
    master_csv = tmp_path / "drifted_master.csv"
    _write_csv(master_csv, [
        {"code": RIB_CODE, "name_vi": "Something Else", "energy_kcal": "187",
         "protein_g": "17.9", "fat_g": "12.8", "carbs_g": ""},
    ], ["code", "name_vi", "energy_kcal", "protein_g", "fat_g", "carbs_g"])
    monkeypatch.setattr(fix, "MASTER", master_csv)

    with pytest.raises(fix.DriftError):
        fix.run(apply=False)


# =====================================================================
# Real-data tests: the applied outcome on the committed dataset
# =====================================================================

@pytest.fixture(scope="module")
def real_alias_map():
    return json.loads(ALIAS_PATH.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def real_ing_csv():
    with ING_CSV.open(encoding="utf-8-sig", newline="") as f:
        return {r["id"]: r for r in csv.DictReader(f)}


@pytest.fixture(scope="module")
def real_ing_json():
    return {r["id"]: r for r in json.loads(ING_JSON.read_text(encoding="utf-8-sig"))}


# --- Alias policy on real data -------------------------------------------

def test_real_qualified_rib_aliases_point_to_7053(real_alias_map):
    for key in fix.ALIAS_REPOINTS:
        assert real_alias_map.get(key) == RIB_CODE, f"{key!r} -> {real_alias_map.get(key)!r}"


def test_real_bare_suon_alias_absent(real_alias_map):
    assert "sườn" not in real_alias_map


def test_real_de_suon_alias_absent(real_alias_map):
    assert "dẻ sườn" not in real_alias_map


def test_real_no_reviewed_rib_alias_points_at_7069(real_alias_map):
    for key in tuple(fix.ALIAS_REPOINTS) + tuple(fix.ALIAS_REMOVALS):
        assert real_alias_map.get(key) != CONTAMINATED_CODE


def test_real_existing_correct_rib_aliases_unchanged(real_alias_map):
    for key in fix.ALIAS_MUST_REMAIN_7053:
        assert real_alias_map.get(key) == RIB_CODE, f"{key!r} -> {real_alias_map.get(key)!r}"


def test_real_out_of_scope_rib_aliases_left_alone(real_alias_map):
    """These are known-suspicious but explicitly deferred to a later audit --
    this fix must not have broadened into a 70xx cleanup.

    "thịt ba chỉ rút sườn" -> 7082 was on this list too, and has since been
    removed by Batch B of the 70xx audit (scripts/eda/
    apply_thit_ba_chi_rut_suon_alias_safe_fix.py). That key is now owned by
    tests/test_thit_ba_chi_rut_suon_alias_safe_fix.py; all this fix still has
    to prove about it is that the rib remediation never touched 7082 itself.

    "sườn cốt lết" and "sườn cốt lết xắt lát" -> 7070 were on this list too,
    and have since been repointed to 7053 -- THIS fix's own rib code -- by the
    reviewed Batch-A follow-up (scripts/eda/
    apply_meat_band_batch_a_followup_safe_fix.py). Their new value is asserted
    in test_real_deferred_cot_let_keys_joined_7053_by_review below, which
    replaces the obsolete 7070 pin.
    """
    assert real_alias_map.get("lòng gà") == "7082"
    assert real_alias_map.get("sườn bò") == "7094"
    assert real_alias_map.get("dẻ sườn bò") == "7094"
    assert real_alias_map.get("canh sườn khoai sọ") == "2013"


def test_real_deferred_cot_let_keys_joined_7053_by_review(real_alias_map):
    """The cốt lết keys this fix deferred now sit on 7053, by later review.

    This fix established 7053 as the pork-rib identity and, in section 2.B of
    its report, already resolved one bare "Sườn" row onto 7053 on the strength
    of a cốt lết recipe context. The Batch-A follow-up extended that same
    reviewed conclusion to the alias family itself, so the four keys joining
    7053 is a continuation of this fix's policy, not drift away from it.

    Asserted here (not only in the follow-up's own tests) because this file
    owns the 7053 rib family's integrity: the keys arriving must not have
    displaced any alias this fix put there.
    """
    for key in ("cốt lết", "sườn cốt lết", "thịt cốt lết", "sườn cốt lết xắt lát"):
        assert real_alias_map.get(key) == RIB_CODE, f"{key!r} -> {real_alias_map.get(key)!r}"
    for key in fix.ALIAS_MUST_REMAIN_7053:
        assert real_alias_map.get(key) == RIB_CODE, f"{key!r} -> {real_alias_map.get(key)!r}"
    for key in fix.ALIAS_REPOINTS:
        assert real_alias_map.get(key) == RIB_CODE, f"{key!r} -> {real_alias_map.get(key)!r}"
    for key in fix.ALIAS_REMOVALS:
        assert key not in real_alias_map, key


# --- Row outcomes on real data -------------------------------------------

def test_real_all_twelve_reviewed_rows_present(real_ing_csv):
    assert fix.TARGET_IDS <= set(real_ing_csv), "a reviewed row id is missing from the dataset"


def test_real_exactly_ten_rows_on_7053_and_two_unmatched(real_ing_csv):
    on_rib = [rid for rid in fix.TARGET_IDS
              if (real_ing_csv[rid]["master_ingredient_code"] or "").strip() == RIB_CODE]
    unmatched = [rid for rid in fix.TARGET_IDS
                 if real_ing_csv[rid]["match_method"] == "UNMATCHED"]
    assert len(on_rib) == 10
    assert len(unmatched) == 2
    assert set(on_rib) | set(unmatched) == fix.TARGET_IDS


def test_real_remapped_rows_carry_full_7053_identity(real_ing_csv):
    for rid, _ in fix.REMAP_ROWS:
        row = real_ing_csv[rid]
        assert row["master_ingredient_code"] == RIB_CODE
        assert row["master_ingredient_name"] == RIB_NAME
        assert row["match_method"] == fix.PRESET_ALIAS_METHOD
        assert row["match_confidence"] == fix.PRESET_ALIAS_CONFIDENCE


def test_real_remapped_rows_nutrition_matches_7053_profile(real_ing_csv):
    for rid, _ in fix.REMAP_ROWS:
        row = real_ing_csv[rid]
        weight = float(row["estimated_weight_g"])
        assert row["calories"] == str(round(187 * weight / 100.0, 1))
        assert row["protein_g"] == str(round(17.9 * weight / 100.0, 1))
        assert row["fat_g"] == str(round(12.8 * weight / 100.0, 1))
        assert _blank(row["carbs_g"]), "7053 has no carbs value -- must stay null, not 0.0"


def test_real_no_reviewed_row_is_left_on_7069(real_ing_csv):
    for rid in fix.TARGET_IDS:
        assert (real_ing_csv[rid]["master_ingredient_code"] or "").strip() != CONTAMINATED_CODE


def test_real_cleared_rows_follow_unmatched_contract(real_ing_csv):
    for rid, _ in fix.CLEAR_ROWS:
        row = real_ing_csv[rid]
        assert _blank(row["master_ingredient_code"])
        assert _blank(row["master_ingredient_name"])
        assert row["match_method"] == "UNMATCHED"
        assert _blank(row["match_confidence"]), "0.0 must not be used as a confidence sentinel"
        for field in NUTRITION_FIELDS:
            assert _blank(row[field]), f"{field} must be null for cleared row {rid}"
        assert not _blank(row["raw_text"])
        assert not _blank(row["estimated_weight_g"])


def test_real_beef_rib_row_is_not_mapped_to_pork(real_ing_csv):
    row = real_ing_csv[BEEF_RIB_ROW_ID]
    assert row["match_method"] == "UNMATCHED"
    for code in fix.BEEF_RIB_FORBIDDEN_CODES:
        assert (row["master_ingredient_code"] or "").strip() != code


def test_real_ambiguous_row_remains_unmatched(real_ing_csv):
    assert real_ing_csv[AMBIGUOUS_ROW_ID]["match_method"] == "UNMATCHED"


def test_real_pork_chop_row_maps_to_7053(real_ing_csv):
    row = real_ing_csv[PORK_CHOP_ROW_ID]
    assert row["raw_text"] == "2 miếng Sườn"
    assert row["master_ingredient_code"] == RIB_CODE


def test_real_bbq_pork_rib_row_maps_to_7053(real_ing_csv):
    row = real_ing_csv[BBQ_PORK_RIB_ROW_ID]
    assert row["raw_text"] == "4 dẻ sườn"
    assert row["master_ingredient_code"] == RIB_CODE


# --- Populations that must not have moved --------------------------------

def test_real_suon_non_heo_rows_stay_on_7053(real_ing_csv):
    rows = [r for r in real_ing_csv.values()
            if (r["cleaned_name"] or "").strip() == SUON_NON_HEO_CLEANED_NAME]
    assert len(rows) == EXPECTED_SUON_NON_HEO_ROWS
    for row in rows:
        assert row["master_ingredient_code"] == RIB_CODE, (
            f"row {row['id']} regressed off {RIB_CODE}"
        )


def test_real_legitimate_gio_lua_rows_untouched(real_ing_csv):
    for rid in LEGIT_GIO_LUA_ROW_IDS:
        row = real_ing_csv[rid]
        assert row["master_ingredient_code"] == CONTAMINATED_CODE
        assert row["master_ingredient_name"] == fix.OLD_NAME
        assert row["match_method"] == "EXACT_CATALOG_MATCH"


def test_real_no_rib_row_remains_on_7069(real_ing_csv):
    """7069 holds exactly two reviewed populations: the legitimate exact-match
    'Giò lụa' rows this fix protected, and the 'chả lụa' rows Batch A of the
    70xx meat-band audit later repointed onto 7069 (the southern name for the
    same steamed pork sausage -- see
    scripts/eda/apply_meat_band_batch_a_alias_safe_fix.py).

    No rib row may sit on 7069 by any route. The blanket
    "every 7069 row is EXACT_CATALOG_MATCH" form this assertion originally took
    was a snapshot of the then-population, not the rib invariant.
    """
    on_7069 = {r["id"] for r in real_ing_csv.values()
               if (r["master_ingredient_code"] or "").strip() == CONTAMINATED_CODE}
    cha_lua_ids = {rid for key in ("chả lụa", "chả lụa cắt hạt lựu")
                   for rid, _ in batch_a.REPAIR_ROWS[key]}
    assert on_7069 == set(LEGIT_GIO_LUA_ROW_IDS) | cha_lua_ids
    assert not on_7069 & set(fix.TARGET_IDS)
    for rid in LEGIT_GIO_LUA_ROW_IDS:
        assert real_ing_csv[rid]["match_method"] == "EXACT_CATALOG_MATCH"
    for rid in cha_lua_ids:
        assert real_ing_csv[rid]["match_method"] == "PRESET_ALIAS_MATCH"


# --- CSV/JSON parity ------------------------------------------------------

def test_real_csv_json_parity_for_reviewed_rows(real_ing_csv, real_ing_json):
    for rid in sorted(fix.TARGET_IDS):
        csv_row = real_ing_csv[rid]
        json_row = real_ing_json[rid]
        for field in ("master_ingredient_code", "master_ingredient_name", "match_method",
                      "match_confidence", "raw_text", "cleaned_name",
                      "estimated_weight_g") + NUTRITION_FIELDS:
            csv_value = csv_row[field]
            json_value = json_row.get(field)
            json_value = "" if json_value is None else str(json_value)
            assert csv_value == json_value, f"row {rid} field {field} differs between CSV and JSON"
