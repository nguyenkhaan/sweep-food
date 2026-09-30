"""Tests for the "thịt ba chỉ rút sườn" PRESET_ALIAS fix (Batch B of the 70xx
meat-band audit).

The alias mapped pork belly ("thịt ba chỉ rút sườn") onto 7082
"Lòng gà (cả bộ)" -- whole chicken giblets. It was removed rather than
repointed, because clean_culinary_query() already strips "rút sườn" and the
sibling alias "thịt ba chỉ" -> 7018 resolves the rows at the same
PRESET_ALIAS_MATCH / 0.98.

Three layers:

  * Fixture tests exercise
    scripts/eda/apply_thit_ba_chi_rut_suon_alias_safe_fix.py against a small
    tmp_path dataset -- every module-level path constant is monkeypatched, so
    the real ~64k-row processed dataset and the real alias map are never
    touched.
  * Matcher tests prove the fallthrough on the REAL alias map and catalog:
    with the key gone, the ten rows still resolve to 7018 at 0.98, and the
    nearby pork-belly/giblet/bacon/beef identities do not move.
  * Real-data tests assert the applied outcome on the committed processed and
    canonical datasets: the single alias removal, the 10 row outcomes, and the
    populations that must NOT have moved (the 5 legitimate "lòng gà" rows on
    7082 and the 525 pre-existing 7018 rows).
"""

import csv
import json
from pathlib import Path

import pytest

import scripts.eda.apply_thit_ba_chi_rut_suon_alias_safe_fix as fix
from nlp.entity_matcher import (
    VietnameseIngredientMatcher,
    clean_culinary_query,
    normalize_vietnamese_text,
)

ROOT = Path(__file__).resolve().parent.parent
ALIAS_PATH = ROOT / "data/processed/viendinhduong/ingredient_alias_map.json"
MASTER_CSV = ROOT / "data/processed/viendinhduong/master_ingredients_nutrition.csv"
ING_CSV = ROOT / "data/processed/recipes/recipe_ingredients.csv"
ING_JSON = ROOT / "data/processed/recipes/recipe_ingredients.json"
RECIPES_CSV = ROOT / "data/processed/recipes/recipes.csv"
RECIPES_JSON = ROOT / "data/processed/recipes/recipes.json"
CANON_ING_CSV = ROOT / "data/processed/recipes/canonical_recipe_ingredients.csv"
CANON_RECIPES_CSV = ROOT / "data/processed/recipes/canonical_recipes.csv"

GIBLET_CODE = "7082"
GIBLET_NAME = "Lòng gà (cả bộ)"
PORK_BELLY_CODE = "7018"
PORK_BELLY_NAME = "Thịt ba chỉ (ba rọi) heo"
REMOVED_ALIAS = "thịt ba chỉ rút sườn"

# 525 rows already sat on 7018 before this fix; the 10 repaired rows join them.
PRE_EXISTING_7018_ROWS = 525
EXPECTED_7018_ROWS = 535
EXPECTED_7082_ROWS = 5

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

# Fixture catalog values. 7018 declares no carbs, exactly like the real row.
FIX_7018 = {"energy_kcal": "260", "protein_g": "16.5", "fat_g": "21.5", "carbs_g": ""}
FIX_7082 = {"energy_kcal": "119", "protein_g": "17.88", "fat_g": "4.47", "carbs_g": "1.79"}


def _write_csv(path, rows, fieldnames):
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def _row(**kwargs):
    base = {f: "" for f in ING_FIELDS}
    base.update(kwargs)
    return base


def _contaminated_row(rid, raw_text, recipe_id, weight):
    """A row in the exact pre-fix state: 7082 / Lòng gà (cả bộ) / 0.98."""
    factor = weight / 100.0
    return _row(
        id=rid, recipe_id=recipe_id,
        master_ingredient_code=fix.OLD_CODE, master_ingredient_name=fix.OLD_NAME,
        raw_text=raw_text, cleaned_name=fix.TARGET_CLEANED_NAME,
        required_quantity=str(weight), unit_vi="g", unit="GRAM",
        match_confidence=fix.PRESET_ALIAS_CONFIDENCE, match_method=fix.PRESET_ALIAS_METHOD,
        estimated_weight_g=str(round(weight, 1)),
        calories=str(round(float(FIX_7082["energy_kcal"]) * factor, 1)),
        protein_g=str(round(float(FIX_7082["protein_g"]) * factor, 1)),
        fat_g=str(round(float(FIX_7082["fat_g"]) * factor, 1)),
        carbs_g=str(round(float(FIX_7082["carbs_g"]) * factor, 1)),
    )


def _build_alias_map():
    alias_map = {key: fix.OLD_CODE for key in fix.ALIAS_REMOVALS}
    alias_map.update({key: PORK_BELLY_CODE for key in fix.ALIAS_MUST_REMAIN_7018})
    alias_map.update({key: GIBLET_CODE for key in fix.ALIAS_MUST_REMAIN_7082})
    # Out-of-scope 70xx aliases that must survive untouched. "sườn cốt lết" sat
    # on 7070 when this fix ran and has since been repointed to 7053 by the
    # reviewed Batch-A follow-up; it is carried at its CURRENT value so the
    # fixture proves this fix leaves it alone wherever it points.
    alias_map.update({
        "sườn cốt lết": "7053",
        "sườn bò": "7094",
        "dẻ sườn bò": "7094",
        "thịt ba chỉ xông khói": "20051",
        "thịt lợn ba chỉ": "11020",
    })
    return alias_map


@pytest.fixture
def fixture_paths(tmp_path, monkeypatch):
    alias_path = tmp_path / "ingredient_alias_map.json"
    master_csv = tmp_path / "master.csv"
    ing_csv = tmp_path / "recipe_ingredients.csv"
    ing_json = tmp_path / "recipe_ingredients.json"
    recipes_csv = tmp_path / "recipes.csv"
    recipes_json = tmp_path / "recipes.json"
    out_dir = tmp_path / "reports"

    alias_path.write_text(
        json.dumps(_build_alias_map(), ensure_ascii=False, indent=2), encoding="utf-8"
    )

    master_fields = ["code", "name_vi", "energy_kcal", "protein_g", "fat_g", "carbs_g"]
    _write_csv(master_csv, [
        # 7018 carries no carbs value -- remapped rows must end up null, not 0.0.
        dict(code=PORK_BELLY_CODE, name_vi=PORK_BELLY_NAME, **FIX_7018),
        dict(code=GIBLET_CODE, name_vi=GIBLET_NAME, **FIX_7082),
        {"code": "20051", "name_vi": "Thịt ba chỉ xông khói (Bacon)", "energy_kcal": "541",
         "protein_g": "37.0", "fat_g": "42.0", "carbs_g": "1.4"},
    ], master_fields)

    weights = {}
    ing_rows = []
    for i, (rid, raw_text) in enumerate(fix.REMAP_ROWS):
        weight = 100.0 * (i + 1)
        weights[rid] = weight
        ing_rows.append(_contaminated_row(rid, raw_text, f"r-remap-{i}", weight))

    # Populations that must never move.
    ing_rows.append(_row(
        id="long-ga-legit", recipe_id="r-long-ga", master_ingredient_code=GIBLET_CODE,
        master_ingredient_name=GIBLET_NAME, raw_text="Lòng gà 300 gr", cleaned_name="lòng gà",
        required_quantity="300.0", unit_vi="g", unit="GRAM",
        match_confidence=fix.PRESET_ALIAS_CONFIDENCE, match_method=fix.PRESET_ALIAS_METHOD,
        estimated_weight_g="300.0", calories="357.0", protein_g="53.6", fat_g="13.4", carbs_g="5.4",
    ))
    ing_rows.append(_row(
        id="ba-chi-already-correct", recipe_id="r-ba-chi", master_ingredient_code=PORK_BELLY_CODE,
        master_ingredient_name=PORK_BELLY_NAME, raw_text="500 g Thịt ba chỉ",
        cleaned_name="thịt ba chỉ", required_quantity="500.0", unit_vi="g", unit="GRAM",
        match_confidence=fix.PRESET_ALIAS_CONFIDENCE, match_method=fix.PRESET_ALIAS_METHOD,
        estimated_weight_g="500.0", calories="1300.0", protein_g="82.5", fat_g="107.5", carbs_g="",
    ))
    ing_rows.append(_row(
        id="bacon-out-of-scope", recipe_id="r-bacon", master_ingredient_code="20051",
        master_ingredient_name="Thịt ba chỉ xông khói (Bacon)",
        raw_text="Thịt ba chỉ xông khói 100g", cleaned_name="thịt ba chỉ xông khói",
        required_quantity="100.0", unit_vi="g", unit="GRAM",
        match_confidence=fix.PRESET_ALIAS_CONFIDENCE, match_method=fix.PRESET_ALIAS_METHOD,
        estimated_weight_g="100.0", calories="541.0", protein_g="37.0", fat_g="42.0", carbs_g="1.4",
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
        "alias": alias_path, "master": master_csv, "ing_csv": ing_csv, "ing_json": ing_json,
        "recipes_csv": recipes_csv, "recipes_json": recipes_json, "out": out_dir,
        "weights": weights,
    }


def _fx_alias_map(paths):
    return json.loads(paths["alias"].read_text(encoding="utf-8"))


def _fx_rows(paths):
    with paths["ing_csv"].open(encoding="utf-8-sig", newline="") as f:
        return {r["id"]: r for r in csv.DictReader(f)}


def _fx_json_rows(paths):
    return {r["id"]: r for r in json.loads(paths["ing_json"].read_text(encoding="utf-8-sig"))}


# --- Dry-run behaviour ----------------------------------------------------

def test_fixture_dry_run_writes_nothing(fixture_paths):
    before_alias = fixture_paths["alias"].read_bytes()
    before_ing = fixture_paths["ing_csv"].read_bytes()
    report = fix.run(apply=False)
    assert report["status"] == "preview"
    assert fixture_paths["alias"].read_bytes() == before_alias
    assert fixture_paths["ing_csv"].read_bytes() == before_ing
    assert not fixture_paths["out"].exists()


def test_fixture_preview_reports_the_full_blast_radius(fixture_paths):
    report = fix.run(apply=False)
    assert report["remap_target_count"] == 10
    assert report["remap_applied_now"] == 10
    assert report["affected_recipe_count"] == 10
    assert report["alias_decision"] == "REMOVE_ALIAS"
    assert report["fallthrough"]["row_level_overrides"] == 0


# --- Alias outcomes -------------------------------------------------------

def test_fixture_unsafe_alias_is_removed(fixture_paths):
    fix.run(apply=True)
    assert REMOVED_ALIAS not in _fx_alias_map(fixture_paths)


def test_fixture_pork_belly_siblings_keep_7018(fixture_paths):
    fix.run(apply=True)
    alias_map = _fx_alias_map(fixture_paths)
    for key in fix.ALIAS_MUST_REMAIN_7018:
        assert alias_map[key] == PORK_BELLY_CODE, f"{key!r} -> {alias_map[key]!r}"


def test_fixture_giblet_aliases_keep_7082(fixture_paths):
    """7082 is a legitimate identity -- only the pork-belly key was wrong."""
    fix.run(apply=True)
    alias_map = _fx_alias_map(fixture_paths)
    for key in fix.ALIAS_MUST_REMAIN_7082:
        assert alias_map[key] == GIBLET_CODE, f"{key!r} -> {alias_map[key]!r}"


def test_fixture_out_of_scope_aliases_untouched(fixture_paths):
    fix.run(apply=True)
    alias_map = _fx_alias_map(fixture_paths)
    assert alias_map["sườn cốt lết"] == "7053"
    assert alias_map["sườn bò"] == "7094"
    assert alias_map["dẻ sườn bò"] == "7094"
    assert alias_map["thịt ba chỉ xông khói"] == "20051"
    assert alias_map["thịt lợn ba chỉ"] == "11020"


def test_fixture_only_the_one_target_key_changes(fixture_paths):
    before = _fx_alias_map(fixture_paths)
    fix.run(apply=True)
    after = _fx_alias_map(fixture_paths)
    assert set(before) - set(after) == set(fix.ALIAS_REMOVALS)
    assert {k: v for k, v in before.items() if k not in fix.ALIAS_REMOVALS} == after


# --- Row outcomes ---------------------------------------------------------

def test_fixture_all_ten_rows_land_on_7018(fixture_paths):
    fix.run(apply=True)
    rows = _fx_rows(fixture_paths)
    for rid, _ in fix.REMAP_ROWS:
        row = rows[rid]
        assert row["master_ingredient_code"] == PORK_BELLY_CODE
        assert row["master_ingredient_name"] == PORK_BELLY_NAME
        assert row["match_method"] == fix.PRESET_ALIAS_METHOD
        assert row["match_confidence"] == fix.PRESET_ALIAS_CONFIDENCE


def test_fixture_remapped_nutrition_comes_from_the_catalog(fixture_paths):
    fix.run(apply=True)
    rows = _fx_rows(fixture_paths)
    for rid, _ in fix.REMAP_ROWS:
        weight = fixture_paths["weights"][rid]
        factor = weight / 100.0
        row = rows[rid]
        assert float(row["calories"]) == round(float(FIX_7018["energy_kcal"]) * factor, 1)
        assert float(row["protein_g"]) == round(float(FIX_7018["protein_g"]) * factor, 1)
        assert float(row["fat_g"]) == round(float(FIX_7018["fat_g"]) * factor, 1)


def test_fixture_remapped_carbs_is_null_not_zero(fixture_paths):
    """7018 declares no carbs_g. Missing must stay missing, never become 0.0."""
    fix.run(apply=True)
    rows = _fx_rows(fixture_paths)
    for rid, _ in fix.REMAP_ROWS:
        assert _blank(rows[rid]["carbs_g"]), rows[rid]["carbs_g"]


def test_fixture_raw_context_is_preserved(fixture_paths):
    """raw_text, cleaned_name, quantity and weight carry the evidence a future
    re-match needs; a remap must not rewrite them."""
    before = _fx_rows(fixture_paths)
    fix.run(apply=True)
    after = _fx_rows(fixture_paths)
    for rid, raw_text in fix.REMAP_ROWS:
        assert after[rid]["raw_text"] == raw_text
        assert after[rid]["cleaned_name"] == fix.TARGET_CLEANED_NAME
        for field in ("required_quantity", "unit", "unit_vi", "estimated_weight_g", "recipe_id"):
            assert after[rid][field] == before[rid][field]


def test_fixture_legitimate_giblet_row_untouched(fixture_paths):
    before = _fx_rows(fixture_paths)["long-ga-legit"]
    fix.run(apply=True)
    assert _fx_rows(fixture_paths)["long-ga-legit"] == before


def test_fixture_already_correct_pork_belly_row_untouched(fixture_paths):
    before = _fx_rows(fixture_paths)["ba-chi-already-correct"]
    fix.run(apply=True)
    assert _fx_rows(fixture_paths)["ba-chi-already-correct"] == before


def test_fixture_bacon_row_untouched(fixture_paths):
    """"thịt ba chỉ xông khói" is a different identity that shares the
    "thịt ba chỉ" prefix -- the nearest false-positive risk of this fix."""
    before = _fx_rows(fixture_paths)["bacon-out-of-scope"]
    fix.run(apply=True)
    assert _fx_rows(fixture_paths)["bacon-out-of-scope"] == before


def test_fixture_no_unrelated_row_changes(fixture_paths):
    before = _fx_rows(fixture_paths)
    fix.run(apply=True)
    after = _fx_rows(fixture_paths)
    changed = {rid for rid in after if after[rid] != before[rid]}
    assert changed == set(fix.TARGET_IDS)


def test_fixture_csv_and_json_stay_in_parity(fixture_paths):
    fix.run(apply=True)
    csv_rows, json_rows = _fx_rows(fixture_paths), _fx_json_rows(fixture_paths)
    assert set(csv_rows) == set(json_rows)
    for rid, _ in fix.REMAP_ROWS:
        for field in ("master_ingredient_code", "master_ingredient_name", "match_method",
                      "match_confidence", "calories", "protein_g", "fat_g"):
            assert str(csv_rows[rid][field]) == str(json_rows[rid][field])
        assert _blank(csv_rows[rid]["carbs_g"]) and _blank(json_rows[rid]["carbs_g"])


def test_fixture_recipe_totals_follow_the_rows(fixture_paths):
    fix.run(apply=True)
    rows = _fx_rows(fixture_paths)
    with fixture_paths["recipes_csv"].open(encoding="utf-8-sig", newline="") as f:
        recipes = {r["id"]: r for r in csv.DictReader(f)}
    for rid, _ in fix.REMAP_ROWS:
        recipe = recipes[rows[rid]["recipe_id"]]
        assert float(recipe["total_calories"]) == float(rows[rid]["calories"])
        # A null ingredient carbs value rolls up as absent, i.e. 0.0 here.
        assert float(recipe["total_carbs_g"]) == 0.0


def test_fixture_report_is_written_on_apply(fixture_paths):
    fix.run(apply=True)
    report = json.loads((fixture_paths["out"] / "applied_fix.json").read_text(encoding="utf-8"))
    assert report["status"] == "applied"
    assert report["remap_applied_now"] == 10
    assert report["legitimate_7082_rows_untouched"] == 1
    assert sorted(report["remap_row_ids"]) == sorted(fix.TARGET_IDS)


# --- Idempotency ----------------------------------------------------------

def test_fixture_rerun_is_a_byte_identical_no_op(fixture_paths):
    fix.run(apply=True)
    alias_bytes = fixture_paths["alias"].read_bytes()
    ing_bytes = fixture_paths["ing_csv"].read_bytes()
    recipes_bytes = fixture_paths["recipes_csv"].read_bytes()

    report = fix.run(apply=True)
    assert report["remap_applied_now"] == 0
    assert report["remap_already_applied"] == 10
    assert fixture_paths["alias"].read_bytes() == alias_bytes
    assert fixture_paths["ing_csv"].read_bytes() == ing_bytes
    assert fixture_paths["recipes_csv"].read_bytes() == recipes_bytes


# --- Fail-closed behaviour ------------------------------------------------

def test_fixture_unexpected_alias_value_aborts(fixture_paths):
    alias_map = _fx_alias_map(fixture_paths)
    alias_map[REMOVED_ALIAS] = "7070"
    fixture_paths["alias"].write_text(json.dumps(alias_map, ensure_ascii=False), encoding="utf-8")
    with pytest.raises(fix.DriftError):
        fix.run(apply=False)


def test_fixture_missing_fallthrough_alias_aborts(fixture_paths):
    """THE safety property of a REMOVE_ALIAS decision: if "thịt ba chỉ" no
    longer resolves to 7018, removing the unsafe key would drop these rows into
    SUBPHRASE/neural matching instead. The script must refuse."""
    alias_map = _fx_alias_map(fixture_paths)
    del alias_map[fix.FALLTHROUGH_CLEANED_NAME]
    fixture_paths["alias"].write_text(json.dumps(alias_map, ensure_ascii=False), encoding="utf-8")
    with pytest.raises(fix.DriftError):
        fix.run(apply=False)


def test_fixture_repointed_fallthrough_alias_aborts(fixture_paths):
    alias_map = _fx_alias_map(fixture_paths)
    alias_map[fix.FALLTHROUGH_CLEANED_NAME] = "20051"
    fixture_paths["alias"].write_text(json.dumps(alias_map, ensure_ascii=False), encoding="utf-8")
    with pytest.raises(fix.DriftError):
        fix.run(apply=False)


def test_fixture_drifted_giblet_alias_aborts(fixture_paths):
    alias_map = _fx_alias_map(fixture_paths)
    alias_map["lòng gà"] = PORK_BELLY_CODE
    fixture_paths["alias"].write_text(json.dumps(alias_map, ensure_ascii=False), encoding="utf-8")
    with pytest.raises(fix.DriftError):
        fix.run(apply=False)


def test_fixture_drifted_row_match_state_aborts(fixture_paths):
    rows = list(_fx_rows(fixture_paths).values())
    for row in rows:
        if row["id"] == fix.REMAP_ROWS[0][0]:
            row["master_ingredient_code"] = "7070"
    _write_csv(fixture_paths["ing_csv"], rows, ING_FIELDS)
    with pytest.raises(fix.DriftError):
        fix.run(apply=False)


def test_fixture_drifted_raw_text_aborts(fixture_paths):
    rows = list(_fx_rows(fixture_paths).values())
    for row in rows:
        if row["id"] == fix.REMAP_ROWS[0][0]:
            row["raw_text"] = "something else entirely"
    _write_csv(fixture_paths["ing_csv"], rows, ING_FIELDS)
    with pytest.raises(fix.DriftError):
        fix.run(apply=False)


def test_fixture_drifted_cleaned_name_aborts(fixture_paths):
    """A target row whose cleaned_name no longer routes through the removed
    alias is outside the reviewed blast radius."""
    rows = list(_fx_rows(fixture_paths).values())
    for row in rows:
        if row["id"] == fix.REMAP_ROWS[0][0]:
            row["cleaned_name"] = "thịt ba chỉ"
    _write_csv(fixture_paths["ing_csv"], rows, ING_FIELDS)
    with pytest.raises(fix.DriftError):
        fix.run(apply=False)


def test_fixture_extra_reachable_row_aborts(fixture_paths):
    """An 11th row the removal would also move means the blast radius is no
    longer the reviewed one -- nothing may be written."""
    rows = list(_fx_rows(fixture_paths).values())
    rows.append(_contaminated_row("unreviewed-11th-row", "Thịt ba chỉ rút sườn 100g",
                                  "r-extra", 100.0))
    _write_csv(fixture_paths["ing_csv"], rows, ING_FIELDS)
    with pytest.raises(fix.DriftError):
        fix.run(apply=False)


def test_fixture_missing_target_row_aborts(fixture_paths):
    rows = [r for r in _fx_rows(fixture_paths).values() if r["id"] != fix.REMAP_ROWS[0][0]]
    _write_csv(fixture_paths["ing_csv"], rows, ING_FIELDS)
    with pytest.raises(fix.DriftError):
        fix.run(apply=False)


def test_fixture_remap_requires_exact_catalog_identity(tmp_path, monkeypatch, fixture_paths):
    """If the catalog's name_vi for 7018 drifts, the remap must refuse to run
    rather than publish a stale identity."""
    master_csv = tmp_path / "drifted_master.csv"
    _write_csv(master_csv, [
        dict(code=PORK_BELLY_CODE, name_vi="Something Else", **FIX_7018),
        dict(code=GIBLET_CODE, name_vi=GIBLET_NAME, **FIX_7082),
    ], ["code", "name_vi", "energy_kcal", "protein_g", "fat_g", "carbs_g"])
    monkeypatch.setattr(fix, "MASTER", master_csv)

    with pytest.raises(fix.DriftError):
        fix.run(apply=False)


def test_fixture_absent_target_code_aborts(tmp_path, monkeypatch, fixture_paths):
    master_csv = tmp_path / "no_7018_master.csv"
    _write_csv(master_csv, [
        dict(code=GIBLET_CODE, name_vi=GIBLET_NAME, **FIX_7082),
    ], ["code", "name_vi", "energy_kcal", "protein_g", "fat_g", "carbs_g"])
    monkeypatch.setattr(fix, "MASTER", master_csv)

    with pytest.raises(fix.DriftError):
        fix.run(apply=False)


# =====================================================================
# Matcher tests: the real fallthrough on the real alias map and catalog
# =====================================================================

@pytest.fixture(scope="module")
def real_alias_map():
    return json.loads(ALIAS_PATH.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def real_catalog():
    with MASTER_CSV.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def _make_matcher(catalog, aliases):
    """Build a matcher without touching any model or embedding cache -- only
    the attributes the dictionary stages of match() actually read."""
    m = VietnameseIngredientMatcher.__new__(VietnameseIngredientMatcher)
    m.catalog = catalog
    m.catalog_names = [c["name_vi"] for c in catalog]
    m.normalized_to_index = {}
    for idx, item in enumerate(catalog):
        m.normalized_to_index[normalize_vietnamese_text(item["name_vi"].strip())] = idx
        norm_en = normalize_vietnamese_text((item.get("name_en") or "").strip())
        if norm_en and norm_en not in m.normalized_to_index:
            m.normalized_to_index[norm_en] = idx
    m.catalog_subphrase_items = []
    for idx, item in enumerate(catalog):
        head = normalize_vietnamese_text(item["name_vi"].strip().split(",")[0])
        if head:
            m.catalog_subphrase_items.append((head, f" {head} ", len(head), idx))
    code_to_idx = {c["code"]: idx for idx, c in enumerate(catalog)}
    m.alias_dict = {
        normalize_vietnamese_text(k): code_to_idx[v]
        for k, v in aliases.items() if v in code_to_idx
    }
    return m


@pytest.fixture(scope="module")
def real_matcher(real_catalog, real_alias_map):
    return _make_matcher(real_catalog, real_alias_map)


def test_cleaner_strips_rut_suon(real_matcher):
    """The whole REMOVE_ALIAS decision rests on this cleaner behaviour."""
    assert clean_culinary_query(REMOVED_ALIAS) == fix.FALLTHROUGH_CLEANED_NAME


def test_matcher_resolves_pork_belly_rows_to_7018(real_matcher):
    """Post-removal fallthrough on the real data: Stage 2's cleaned-query
    lookup lands on 7018 at 0.98, so no row-level override is needed."""
    result = real_matcher.match(REMOVED_ALIAS, raw_context="Thịt ba chỉ rút sườn 600g")
    assert result["matched_item"]["code"] == PORK_BELLY_CODE
    assert result["matched_item"]["name_vi"] == PORK_BELLY_NAME
    assert result["method"] == "PRESET_ALIAS_MATCH"
    assert result["confidence"] == 0.98


def test_matcher_resolves_ba_roi_spelling_to_7018(real_matcher):
    """One row parses as "thịt ba rọi rút sườn"; it reaches 7018 through the
    sibling "thịt ba rọi" alias -- same code, method and confidence."""
    result = real_matcher.match("thịt ba rọi rút sườn",
                                raw_context="500 gr thịt ba rọi rút sườn")
    assert result["matched_item"]["code"] == PORK_BELLY_CODE
    assert result["method"] == "PRESET_ALIAS_MATCH"
    assert result["confidence"] == 0.98


def test_matcher_never_returns_giblets_for_pork_belly(real_matcher):
    for query in (REMOVED_ALIAS, "thịt ba chỉ", "ba chỉ rút sườn",
                  "thịt ba chỉ heo rút sườn", "thịt ba rọi rút sườn"):
        assert real_matcher.match(query)["matched_item"]["code"] != GIBLET_CODE, query


def test_matcher_still_resolves_real_giblets_to_7082(real_matcher):
    """7082 is a valid identity. Chicken giblets must still reach it."""
    for query in ("lòng gà", "lòng gà cả bộ"):
        result = real_matcher.match(query)
        assert result["matched_item"]["code"] == GIBLET_CODE, query
        assert result["matched_item"]["name_vi"] == GIBLET_NAME


def test_matcher_nearby_identities_do_not_drift(real_matcher):
    """Nearest false-positive risks: names sharing the "ba chỉ" token that are
    NOT fresh pork belly must keep their own identities."""
    assert real_matcher.match("thịt ba chỉ xông khói")["matched_item"]["code"] == "20051"
    assert real_matcher.match("ba chỉ bò")["matched_item"]["code"] == "7001"
    assert real_matcher.match("thịt bò ba chỉ cắt lát mỏng")["matched_item"]["code"] == "7006"
    assert real_matcher.match("thịt lợn ba chỉ")["matched_item"]["code"] == "11020"


def test_removal_changes_no_other_alias_resolution(real_catalog, real_alias_map):
    """Simulate the pre-fix map and diff Stage-2 resolution across every
    distinct cleaned_name in the processed dataset: only the removed key's own
    rows may change verdict."""
    pre_fix_aliases = dict(real_alias_map)
    pre_fix_aliases[REMOVED_ALIAS] = GIBLET_CODE
    before = _make_matcher(real_catalog, pre_fix_aliases)
    after = _make_matcher(real_catalog, real_alias_map)

    with ING_CSV.open(encoding="utf-8-sig", newline="") as f:
        cleaned_names = {r["cleaned_name"] for r in csv.DictReader(f)}

    drifted = set()
    for name in cleaned_names:
        norm, cleaned_q = normalize_vietnamese_text(name), clean_culinary_query(name)
        if before._resolve_alias(norm, cleaned_q) != after._resolve_alias(norm, cleaned_q):
            drifted.add(name)
    assert drifted == {fix.TARGET_CLEANED_NAME}


# =====================================================================
# Real-data tests: the applied outcome on the committed dataset
# =====================================================================

@pytest.fixture(scope="module")
def real_ing_csv():
    with ING_CSV.open(encoding="utf-8-sig", newline="") as f:
        return {r["id"]: r for r in csv.DictReader(f)}


@pytest.fixture(scope="module")
def real_ing_json():
    return {r["id"]: r for r in json.loads(ING_JSON.read_text(encoding="utf-8-sig"))}


@pytest.fixture(scope="module")
def real_recipes_csv():
    with RECIPES_CSV.open(encoding="utf-8-sig", newline="") as f:
        return {r["id"]: r for r in csv.DictReader(f)}


@pytest.fixture(scope="module")
def real_master():
    with MASTER_CSV.open(encoding="utf-8-sig", newline="") as f:
        return {r["code"]: r for r in csv.DictReader(f)}


# --- Alias policy on real data -------------------------------------------

def test_real_unsafe_alias_absent(real_alias_map):
    assert REMOVED_ALIAS not in real_alias_map


def test_real_no_alias_maps_pork_belly_text_onto_giblets(real_alias_map):
    """No alias containing "ba chỉ"/"ba rọi" may resolve to 7082."""
    for key, code in real_alias_map.items():
        if "ba chỉ" in key or "ba rọi" in key:
            assert code != GIBLET_CODE, f"{key!r} -> {code!r}"


def test_real_pork_belly_siblings_unchanged(real_alias_map):
    for key in fix.ALIAS_MUST_REMAIN_7018:
        assert real_alias_map.get(key) == PORK_BELLY_CODE, f"{key!r} -> {real_alias_map.get(key)!r}"


def test_real_giblet_aliases_unchanged(real_alias_map):
    for key in fix.ALIAS_MUST_REMAIN_7082:
        assert real_alias_map.get(key) == GIBLET_CODE, f"{key!r} -> {real_alias_map.get(key)!r}"


def test_real_no_replacement_alias_was_added(real_alias_map):
    """The decision was REMOVE_ALIAS, not SAFE_REPOINT: the cleaner already
    resolves this phrase, so no new key should exist for it."""
    assert REMOVED_ALIAS not in real_alias_map
    assert real_alias_map.get(fix.FALLTHROUGH_CLEANED_NAME) == PORK_BELLY_CODE


def test_real_out_of_scope_70xx_aliases_left_alone(real_alias_map):
    """Batch B touches one key. Every other 70xx finding is not Batch B's.

    The cốt lết keys were pinned here on 7070 as still-deferred. That deferral
    has since been reviewed and resolved by the Batch-A follow-up
    (scripts/eda/apply_meat_band_batch_a_followup_safe_fix.py), so they are
    asserted on their NEW code -- the point of this test is that Batch B did
    not touch them, not what their reviewed value happens to be.
    """
    assert real_alias_map.get("sườn cốt lết") == "7053"
    assert real_alias_map.get("sườn cốt lết xắt lát") == "7053"
    assert real_alias_map.get("sườn bò") == "7094"
    assert real_alias_map.get("dẻ sườn bò") == "7094"
    assert real_alias_map.get("thịt ba chỉ xông khói") == "20051"
    assert real_alias_map.get("thịt lợn ba chỉ") == "11020"


# --- Row outcomes on real data -------------------------------------------

def test_real_all_ten_reviewed_rows_present(real_ing_csv):
    for rid, raw_text in fix.REMAP_ROWS:
        assert rid in real_ing_csv, rid
        assert real_ing_csv[rid]["raw_text"] == raw_text


def test_real_all_ten_rows_are_on_7018(real_ing_csv):
    for rid, _ in fix.REMAP_ROWS:
        row = real_ing_csv[rid]
        assert row["master_ingredient_code"] == PORK_BELLY_CODE
        assert row["master_ingredient_name"] == PORK_BELLY_NAME
        assert row["match_method"] == "PRESET_ALIAS_MATCH"
        assert row["match_confidence"] == "0.98"


def test_real_no_processed_row_reaches_giblets_through_pork_belly_text(real_ing_csv):
    for row in real_ing_csv.values():
        if row["master_ingredient_code"] == GIBLET_CODE:
            assert "ba chỉ" not in row["cleaned_name"], row["id"]
            assert "ba rọi" not in row["cleaned_name"], row["id"]


def test_real_row_nutrition_matches_catalog_scaling(real_ing_csv, real_master):
    catalog = real_master[PORK_BELLY_CODE]
    for rid, _ in fix.REMAP_ROWS:
        row = real_ing_csv[rid]
        factor = float(row["estimated_weight_g"]) / 100.0
        assert float(row["calories"]) == round(float(catalog["energy_kcal"]) * factor, 1)
        assert float(row["protein_g"]) == round(float(catalog["protein_g"]) * factor, 1)
        assert float(row["fat_g"]) == round(float(catalog["fat_g"]) * factor, 1)


def test_real_row_carbs_is_null_not_zero(real_ing_csv, real_master):
    """7018 declares no carbs_g, so these rows must report unknown, not 0."""
    assert _blank(real_master[PORK_BELLY_CODE]["carbs_g"])
    for rid, _ in fix.REMAP_ROWS:
        assert _blank(real_ing_csv[rid]["carbs_g"]), rid


def test_real_rows_kept_their_raw_context(real_ing_csv):
    for rid, raw_text in fix.REMAP_ROWS:
        row = real_ing_csv[rid]
        assert row["raw_text"] == raw_text
        assert row["cleaned_name"] == fix.TARGET_CLEANED_NAME
        assert not _blank(row["estimated_weight_g"])


def test_real_csv_json_parity_for_repaired_rows(real_ing_csv, real_ing_json):
    for rid, _ in fix.REMAP_ROWS:
        c, j = real_ing_csv[rid], real_ing_json[rid]
        for field in ("master_ingredient_code", "master_ingredient_name", "match_method",
                      "match_confidence", "calories", "protein_g", "fat_g",
                      "raw_text", "cleaned_name", "estimated_weight_g"):
            assert str(c[field]) == str(j[field]), (rid, field)
        assert _blank(c["carbs_g"]) and _blank(j["carbs_g"])


# --- Populations that must NOT have moved --------------------------------

def test_real_legitimate_giblet_rows_remain_on_7082(real_ing_csv):
    """7082 is not an empty identity after this fix -- the real chicken-giblet
    rows are still there, and none of them is one of the repaired rows."""
    giblet_rows = [r for r in real_ing_csv.values()
                   if r["master_ingredient_code"] == GIBLET_CODE]
    assert len(giblet_rows) == EXPECTED_7082_ROWS
    assert {r["cleaned_name"] for r in giblet_rows} == {"lòng gà"}
    assert not {r["id"] for r in giblet_rows} & set(fix.TARGET_IDS)


def test_real_7018_population_grew_by_exactly_ten(real_ing_csv):
    rows = [r for r in real_ing_csv.values() if r["master_ingredient_code"] == PORK_BELLY_CODE]
    assert len(rows) == EXPECTED_7018_ROWS == PRE_EXISTING_7018_ROWS + len(fix.REMAP_ROWS)
    assert all(r["match_method"] == "PRESET_ALIAS_MATCH" for r in rows)
    assert all(r["master_ingredient_name"] == PORK_BELLY_NAME for r in rows)


def test_real_recipe_totals_agree_with_ingredient_rows(real_ing_csv, real_recipes_csv):
    """Recompute the four rollups for the 10 affected recipes from their own
    ingredient rows; null nutrition rolls up as absent."""
    affected = {real_ing_csv[rid]["recipe_id"] for rid, _ in fix.REMAP_ROWS}
    assert len(affected) == 10
    totals = {rid: dict.fromkeys(NUTRITION_FIELDS, 0.0) for rid in affected}
    for row in real_ing_csv.values():
        if row["recipe_id"] in affected:
            for field in NUTRITION_FIELDS:
                if not _blank(row[field]):
                    totals[row["recipe_id"]][field] += float(row[field])
    for rid in affected:
        recipe = real_recipes_csv[rid]
        for field, column in (("calories", "total_calories"), ("protein_g", "total_protein_g"),
                              ("fat_g", "total_fat_g"), ("carbs_g", "total_carbs_g")):
            assert float(recipe[column]) == pytest.approx(round(totals[rid][field], 1), abs=0.05), \
                (rid, column)


def test_real_recipes_csv_json_parity_for_affected_recipes(real_ing_csv, real_recipes_csv):
    affected = {real_ing_csv[rid]["recipe_id"] for rid, _ in fix.REMAP_ROWS}
    recipes_json = {r["id"]: r for r in json.loads(RECIPES_JSON.read_text(encoding="utf-8-sig"))}
    for rid in affected:
        for column in ("total_calories", "total_protein_g", "total_fat_g", "total_carbs_g"):
            assert str(real_recipes_csv[rid][column]) == str(recipes_json[rid][column]), (rid, column)


# --- Canonical propagation ------------------------------------------------

def test_real_canonical_ingredients_carry_the_repaired_identity():
    with CANON_ING_CSV.open(encoding="utf-8-sig", newline="") as f:
        canon = {r["id"]: r for r in csv.DictReader(f)}
    for rid, _ in fix.REMAP_ROWS:
        assert rid in canon, f"{rid} missing from canonical ingredients"
        assert canon[rid]["master_ingredient_code"] == PORK_BELLY_CODE
        assert canon[rid]["master_ingredient_name"] == PORK_BELLY_NAME
    assert not any(r["master_ingredient_code"] == GIBLET_CODE and "ba chỉ" in r["cleaned_name"]
                   for r in canon.values())


def test_real_canonical_recipe_totals_match_processed(real_ing_csv, real_recipes_csv):
    with CANON_RECIPES_CSV.open(encoding="utf-8-sig", newline="") as f:
        canon = {r["id"]: r for r in csv.DictReader(f)}
    affected = {real_ing_csv[rid]["recipe_id"] for rid, _ in fix.REMAP_ROWS}
    for rid in affected:
        assert rid in canon, f"{rid} missing from canonical recipes"
        for column in ("total_calories", "total_protein_g", "total_fat_g", "total_carbs_g"):
            assert canon[rid][column] == real_recipes_csv[rid][column], (rid, column)
