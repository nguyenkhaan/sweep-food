"""Tests for the Batch-A FOLLOW-UP of the 70xx meat-band audit -- six PRESET_ALIAS repoints.

scripts/eda/apply_meat_band_batch_a_alias_safe_fix.py deferred a set of aliases
whose correct identity needed an approximation policy rather than an exact
catalog match. That policy was reviewed and approved, and
scripts/eda/apply_meat_band_batch_a_followup_safe_fix.py applies the approved
subset:

    sườn cốt lết / thịt cốt lết / cốt lết / sườn cốt lết xắt lát
                               7070 Giò thủ lợn -> 7053 Sườn heo (xương heo)
    bóng bì                    7064 Chả lợn     -> 7031 Bì lợn
    thịt bò chay lát           7006 Thịt bò...  -> 20039 Thịt chay (sườn non chay)

41 + 4 + 1 = 46 processed ingredient rows across 43 recipes. Every one keeps
PRESET_ALIAS_MATCH / 0.98; no alias is added or removed; no row-level override
is created; no row's weight or raw context is touched.

Three layers:

  * Fixture tests exercise the script against a small tmp_path dataset -- every
    module-level path constant is monkeypatched, so the real ~64k-row processed
    dataset and the real alias map are never touched. They cover the intended
    repoints, fail-closed drift detection, the null-carbs contract, raw-context
    preservation and idempotency.
  * Matcher tests prove the resolution on the REAL alias map and catalog: each
    repointed key now lands on its reviewed code at PRESET_ALIAS_MATCH / 0.98,
    the siblings that must not move do not, and the still-deferred vegan
    analogues are asserted to be untouched.
  * Real-data tests assert the applied outcome on the committed processed and
    canonical datasets: the six alias values, the 46 repaired rows, the
    legitimate populations left behind on the vacated codes, the 4 measured ->
    null carbs transitions, CSV/JSON parity and canonical propagation.

Two approximation policies are asserted deliberately rather than assumed, so a
future reader cannot mistake them for exact identities (see the script
docstring for the full reasoning):

  * 7053 for cốt lết is the only bone-in pork rib identity in the catalog;
    there is no pork chop/cutlet entry, and a prior review already chose 7053
    for this exact recipe context.
  * 7031 for bóng bì is RAW pork skin standing in for DRIED/puffed pork skin.
    The hydration/density gap is real, reviewed, and explicitly not a blocker.
"""

import csv
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import scripts.eda.apply_meat_band_batch_a_followup_safe_fix as fix  # noqa: E402
from nlp.entity_matcher import VietnameseIngredientMatcher  # noqa: E402
from nlp.nutrition import nutrition_value  # noqa: E402

ALIAS_PATH = ROOT / "data/processed/viendinhduong/ingredient_alias_map.json"
MASTER_CSV = ROOT / "data/processed/viendinhduong/master_ingredients_nutrition.csv"
ING_CSV = ROOT / "data/processed/recipes/recipe_ingredients.csv"
ING_JSON = ROOT / "data/processed/recipes/recipe_ingredients.json"
RECIPES_CSV = ROOT / "data/processed/recipes/recipes.csv"
RECIPES_JSON = ROOT / "data/processed/recipes/recipes.json"
CANON_ING_CSV = ROOT / "data/processed/recipes/canonical_recipe_ingredients.csv"

ING_FIELDS = [
    "id", "recipe_id", "master_ingredient_code", "master_ingredient_name", "raw_text",
    "cleaned_name", "required_quantity", "unit_vi", "unit", "preparation_note",
    "match_confidence", "match_method", "estimated_weight_g",
    "calories", "protein_g", "fat_g", "carbs_g",
]

NUTRITION_FIELDS = ("calories", "protein_g", "fat_g", "carbs_g")

# Live per-100g profiles for every code this fix reads or writes. Carbs is ""
# for 7031/7053/7070 -- those codes declare none, and a repaired row must then
# report carbs as NULL, never 0.0.
FIX_MASTER = {
    "7006": {"energy_kcal": "174", "protein_g": "21.53", "fat_g": "9.49", "carbs_g": "0.7"},
    "7031": {"energy_kcal": "118", "protein_g": "23.3", "fat_g": "2.7", "carbs_g": ""},
    "7053": {"energy_kcal": "187", "protein_g": "17.9", "fat_g": "12.8", "carbs_g": ""},
    "7064": {"energy_kcal": "517", "protein_g": "10.8", "fat_g": "50.4", "carbs_g": "5.1"},
    "7070": {"energy_kcal": "553", "protein_g": "16", "fat_g": "54.3", "carbs_g": ""},
    "20039": {"energy_kcal": "310", "protein_g": "50.0", "fat_g": "1.2", "carbs_g": "25.0"},
}
assert set(FIX_MASTER) == set(fix.CODE_NAMES)

# Post-fix master-code populations across the whole processed dataset, measured
# on live data. 7070 43 -> 2 and 7064 5 -> 1 are this fix's vacations; 7053
# (378 -> 419) and 7031 (14 -> 18) absorb them; 7006 204 -> 203 and 20039
# 32 -> 33 move by the single vegan row. Every delta is +/- this fix's 46 rows.
EXPECTED_CODE_ROWS = {
    "7070": 2, "7053": 419,
    "7064": 1, "7031": 18,
    "7006": 203, "20039": 33,
}

# Row counts this fix moved ONTO each target, so the population pins above stay
# tied to the reviewed blast radius rather than drifting with unrelated work.
EXPECTED_ROWS_GAINED = {"7053": 41, "7031": 4, "20039": 1}

# Still deferred after this fix: the vegan analogues whose FORM (wet formed
# product vs dry TVP) the review did not settle, and the vegan seasonings.
STILL_DEFERRED_ALIASES = {
    "đùi gà chay": "7088",
    "xúc xích chay": "7077",
    "nem chua chay": "7073",
    "thịt cua chay": "8069",
    "nước mắm chay": "13017",
    "dầu hào chay": "13027",
}

# Out-of-scope aliases that must survive this fix untouched, on codes it never
# writes. They sit outside ALIAS_MUST_REMAIN so the test proves the "no
# unrelated key changes" guard, not just the pinned-sibling guard.
OUT_OF_SCOPE_ALIASES = dict(STILL_DEFERRED_ALIASES, **{
    "sườn bò": "7094",
    "dẻ sườn bò": "7094",
    "thịt ba chỉ rút sườn": "7018",
})


def _blank(value):
    return value is None or str(value).strip() == ""


def _write_csv(path, rows, fieldnames):
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def _row(**kwargs):
    base = {f: "" for f in ING_FIELDS}
    base.update(kwargs)
    return base


def _scaled(code, weight):
    profile = FIX_MASTER[code]
    factor = weight / 100.0
    out = {}
    for field, source in (("calories", "energy_kcal"), ("protein_g", "protein_g"),
                          ("fat_g", "fat_g"), ("carbs_g", "carbs_g")):
        raw = profile[source]
        out[field] = "" if raw == "" else str(round(float(raw) * factor, 1))
    return out


def _contaminated_row(rid, raw_text, cleaned_name, recipe_id, old_code, weight):
    """A row in the exact pre-fix state: old code / old name / PRESET_ALIAS / 0.98."""
    return _row(
        id=rid, recipe_id=recipe_id,
        master_ingredient_code=old_code, master_ingredient_name=fix.CODE_NAMES[old_code],
        raw_text=raw_text, cleaned_name=cleaned_name,
        required_quantity=str(weight), unit_vi="g", unit="GRAM",
        match_confidence=fix.PRESET_ALIAS_CONFIDENCE, match_method=fix.PRESET_ALIAS_METHOD,
        estimated_weight_g=str(round(weight, 1)), **_scaled(old_code, weight),
    )


def _build_alias_map():
    alias_map = {key: old for key, (old, _) in fix.ALIAS_REPOINTS.items()}
    for code, keys in fix.ALIAS_MUST_REMAIN.items():
        alias_map.update({key: code for key in keys})
    alias_map.update(OUT_OF_SCOPE_ALIASES)
    return alias_map


# The cleaned_name each reviewed alias key reaches its rows by. Taken from the
# live dataset: every in-scope row's cleaned_name is the alias key itself.
CLEANED_NAME_BY_ALIAS = {key: key for key in fix.ALIAS_REPOINTS}


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
        dict(code=code, name_vi=fix.CODE_NAMES[code], **FIX_MASTER[code])
        for code in sorted(FIX_MASTER)
    ], master_fields)

    weights = {}
    ing_rows = []
    # One recipe per row keeps the rollup arithmetic in the fixture trivial; the
    # real-data layer below covers the many-rows-per-recipe case.
    for i, (rid, raw_text) in enumerate(sorted(fix.REPAIR_RAW_BY_ID.items())):
        alias_key = fix.ALIAS_BY_REPAIR_ID[rid]
        old, _ = fix.ALIAS_REPOINTS[alias_key]
        weight = 100.0 + 10.0 * i
        weights[rid] = weight
        ing_rows.append(_contaminated_row(
            rid, raw_text, CLEANED_NAME_BY_ALIAS[alias_key], f"r-{i}", old, weight,
        ))

    # Legitimate populations on the vacated codes that must never move.
    ing_rows.append(_row(
        id="gio-thu-legit", recipe_id="r-gio-thu", master_ingredient_code="7070",
        master_ingredient_name=fix.CODE_NAMES["7070"], raw_text="Giò thủ 300g",
        cleaned_name="giò thủ", required_quantity="300.0", unit_vi="g", unit="GRAM",
        match_confidence=fix.PRESET_ALIAS_CONFIDENCE, match_method=fix.PRESET_ALIAS_METHOD,
        estimated_weight_g="300.0", **_scaled("7070", 300.0),
    ))
    ing_rows.append(_row(
        id="cha-legit", recipe_id="r-cha", master_ingredient_code="7064",
        master_ingredient_name=fix.CODE_NAMES["7064"], raw_text="Chả 50g",
        cleaned_name="chả", required_quantity="50.0", unit_vi="g", unit="GRAM",
        match_confidence=fix.PRESET_ALIAS_CONFIDENCE, match_method=fix.PRESET_ALIAS_METHOD,
        estimated_weight_g="50.0", **_scaled("7064", 50.0),
    ))
    ing_rows.append(_row(
        id="thit-bo-legit", recipe_id="r-thit-bo", master_ingredient_code="7006",
        master_ingredient_name=fix.CODE_NAMES["7006"], raw_text="Thịt bò lát 100g",
        cleaned_name="thịt bò lát", required_quantity="100.0", unit_vi="g", unit="GRAM",
        match_confidence=fix.PRESET_ALIAS_CONFIDENCE, match_method=fix.PRESET_ALIAS_METHOD,
        estimated_weight_g="100.0", **_scaled("7006", 100.0),
    ))

    _write_csv(ing_csv, ing_rows, ING_FIELDS)
    ing_json.write_text(json.dumps(ing_rows, ensure_ascii=False), encoding="utf-8")

    recipe_fields = ["id", "total_calories", "total_protein_g", "total_fat_g",
                     "total_carbs_g", "ingredients_count"]
    recipes = [{
        "id": row["recipe_id"],
        "total_calories": row["calories"] or "0.0",
        "total_protein_g": row["protein_g"] or "0.0",
        "total_fat_g": row["fat_g"] or "0.0",
        "total_carbs_g": row["carbs_g"] or "0.0",
        "ingredients_count": "1",
    } for row in ing_rows]
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
    # The fixture gives every reviewed row its own recipe, which the real data
    # does not; relax only that pin so the rest of the guard set still runs.
    monkeypatch.setattr(fix, "EXPECTED_RECIPE_COUNT", len(fix.REPAIR_IDS))

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


# --- Reviewed scope is what the module declares ---------------------------

def test_scope_is_exactly_six_aliases_and_forty_six_rows():
    assert len(fix.ALIAS_REPOINTS) == 6
    assert len(fix.REPAIR_IDS) == 46
    assert set(fix.REPAIR_ROWS) == set(fix.ALIAS_REPOINTS)
    assert fix.EXPECTED_RECIPE_COUNT == 43


def test_reviewed_per_target_split_is_41_4_1():
    by_target = {}
    for key, (_, new) in fix.ALIAS_REPOINTS.items():
        by_target[new] = by_target.get(new, 0) + len(fix.REPAIR_ROWS[key])
    assert by_target == {"7053": 41, "7031": 4, "20039": 1}


def test_no_repaired_row_carries_a_systemic_cure_trigger():
    """A cure runs after matching and wins; a repaired identity must be safe
    from being silently overwritten by the next pipeline run."""
    for raw in fix.REPAIR_RAW_BY_ID.values():
        for pattern in fix.CURE_RAW_PATTERNS:
            assert not pattern.search(raw.lower()), (raw, pattern.pattern)


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
    assert report["alias_decision"] == "SAFE_REPOINT"
    assert report["alias_repoint_count"] == 6
    assert report["aliases_added"] == 0
    assert report["aliases_removed"] == 0
    assert report["rows_in_scope"] == 46
    assert report["rows_repaired_total"] == 46
    assert report["rows_repaired_now"] == 46
    assert report["match_method_semantics"]["row_level_overrides"] == 0
    assert report["match_method_semantics"]["cure_held_rows"] == 0


# --- Applied behaviour ----------------------------------------------------

def test_fixture_apply_repoints_exactly_the_six_keys(fixture_paths):
    before = _fx_alias_map(fixture_paths)
    fix.run(apply=True)
    after = _fx_alias_map(fixture_paths)
    assert set(after) == set(before)
    changed = {k for k in before if before[k] != after[k]}
    assert changed == set(fix.ALIAS_REPOINTS)
    for key, (_, new) in fix.ALIAS_REPOINTS.items():
        assert after[key] == new, key


def test_fixture_apply_moves_every_row_to_its_reviewed_code(fixture_paths):
    fix.run(apply=True)
    rows = _fx_rows(fixture_paths)
    for rid in fix.REPAIR_IDS:
        _, new = fix.ALIAS_REPOINTS[fix.ALIAS_BY_REPAIR_ID[rid]]
        assert rows[rid]["master_ingredient_code"] == new, rid
        assert rows[rid]["master_ingredient_name"] == fix.CODE_NAMES[new], rid


def test_fixture_match_method_and_confidence_are_unchanged(fixture_paths):
    """The rows were alias-resolved before and after; only the identity moves."""
    before = _fx_rows(fixture_paths)
    fix.run(apply=True)
    after = _fx_rows(fixture_paths)
    for rid in fix.REPAIR_IDS:
        assert after[rid]["match_method"] == before[rid]["match_method"] == fix.PRESET_ALIAS_METHOD
        assert after[rid]["match_confidence"] == before[rid]["match_confidence"]
        assert after[rid]["match_confidence"] == fix.PRESET_ALIAS_CONFIDENCE


def test_fixture_nutrition_is_rescaled_from_the_target_and_the_rows_own_weight(fixture_paths):
    weights = fixture_paths["weights"]
    fix.run(apply=True)
    rows = _fx_rows(fixture_paths)
    for rid in fix.REPAIR_IDS:
        _, new = fix.ALIAS_REPOINTS[fix.ALIAS_BY_REPAIR_ID[rid]]
        expected = _scaled(new, weights[rid])
        for field in NUTRITION_FIELDS:
            assert rows[rid][field] == expected[field], (rid, field)


def test_fixture_codes_without_carbs_write_null_not_zero(fixture_paths):
    """AGENTS.md §4/§9: missing nutrition stays null. 7053/7031/7070 declare no
    carbs_g, so every row landing on one must report carbs as blank."""
    fix.run(apply=True)
    rows = _fx_rows(fixture_paths)
    json_rows = _fx_json_rows(fixture_paths)
    checked = 0
    for rid in fix.REPAIR_IDS:
        _, new = fix.ALIAS_REPOINTS[fix.ALIAS_BY_REPAIR_ID[rid]]
        if new in fix.NULL_CARBS_CODES:
            assert _blank(rows[rid]["carbs_g"]), rid
            assert _blank(json_rows[rid]["carbs_g"]), rid
            checked += 1
    assert checked == 45  # 41 cốt lết -> 7053 + 4 bóng bì -> 7031


def test_fixture_bong_bi_rows_move_from_measured_carbs_to_null(fixture_paths):
    """The one real null transition in this fix: 7064 declares carbs 5.1,
    7031 declares none. The value must become unknown, not 0.0."""
    before = _fx_rows(fixture_paths)
    report = fix.run(apply=True)
    after = _fx_rows(fixture_paths)
    bong_bi = fix.REPAIR_IDS_BY_ALIAS["bóng bì"]
    for rid in bong_bi:
        assert nutrition_value(before[rid]["carbs_g"]) is not None, rid
        assert _blank(after[rid]["carbs_g"]), rid
        assert after[rid]["carbs_g"] != "0.0", rid
    transitions = report["null_nutrition_transitions"]["carbs_g"]
    assert transitions["known_to_null"] == 4
    assert transitions["null_to_known"] == 0
    assert set(transitions["known_to_null_ids"]) == set(bong_bi)


def test_fixture_cot_let_rows_have_no_carbs_transition(fixture_paths):
    """7070 and 7053 both declare no carbs, so those 41 rows are null both
    before and after -- a non-transition worth pinning so a future catalog edit
    that gave either code a carbs value would surface here."""
    before = _fx_rows(fixture_paths)
    fix.run(apply=True)
    after = _fx_rows(fixture_paths)
    for key, (_, new) in fix.ALIAS_REPOINTS.items():
        if new != "7053":
            continue
        for rid in fix.REPAIR_IDS_BY_ALIAS[key]:
            assert _blank(before[rid]["carbs_g"]) and _blank(after[rid]["carbs_g"]), rid


def test_fixture_legitimate_rows_on_vacated_codes_are_untouched(fixture_paths):
    before = _fx_rows(fixture_paths)
    fix.run(apply=True)
    after = _fx_rows(fixture_paths)
    for rid in ("gio-thu-legit", "cha-legit", "thit-bo-legit"):
        assert after[rid] == before[rid], rid


def test_fixture_no_unrelated_row_changes(fixture_paths):
    before = _fx_rows(fixture_paths)
    fix.run(apply=True)
    after = _fx_rows(fixture_paths)
    changed = {rid for rid in before if before[rid] != after[rid]}
    assert changed == set(fix.REPAIR_IDS)


def test_fixture_raw_context_and_weight_are_preserved(fixture_paths):
    """AGENTS.md §8: this fix changes identity, never evidence."""
    before = _fx_rows(fixture_paths)
    fix.run(apply=True)
    after = _fx_rows(fixture_paths)
    for rid in fix.REPAIR_IDS:
        for field in ("raw_text", "cleaned_name", "required_quantity", "unit_vi",
                      "unit", "estimated_weight_g", "recipe_id"):
            assert after[rid][field] == before[rid][field], (rid, field)


def test_fixture_out_of_scope_aliases_untouched(fixture_paths):
    fix.run(apply=True)
    alias_map = _fx_alias_map(fixture_paths)
    for key, code in OUT_OF_SCOPE_ALIASES.items():
        assert alias_map[key] == code, key


def test_fixture_csv_and_json_stay_in_parity(fixture_paths):
    """Parity is LOGICAL, not byte-level: a null nutrient is "" in CSV and
    JSON null, which are the same absent value in their own formats. What must
    never differ is which values are present and what they are."""
    fix.run(apply=True)
    rows = _fx_rows(fixture_paths)
    json_rows = _fx_json_rows(fixture_paths)
    assert set(rows) == set(json_rows)
    for rid in fix.REPAIR_IDS:
        for field in ("master_ingredient_code", "master_ingredient_name",
                      "match_method", "match_confidence", *NUTRITION_FIELDS):
            json_value = json_rows[rid][field]
            json_value = "" if json_value is None else str(json_value)
            assert str(rows[rid][field]) == json_value, (rid, field)


def test_fixture_recipe_totals_follow_the_repaired_rows(fixture_paths):
    fix.run(apply=True)
    rows = _fx_rows(fixture_paths)
    with fixture_paths["recipes_csv"].open(encoding="utf-8-sig", newline="") as f:
        recipes = {r["id"]: r for r in csv.DictReader(f)}
    for rid in fix.REPAIR_IDS:
        recipe = recipes[rows[rid]["recipe_id"]]
        for field, total in (("calories", "total_calories"), ("protein_g", "total_protein_g"),
                             ("fat_g", "total_fat_g"), ("carbs_g", "total_carbs_g")):
            expected = nutrition_value(rows[rid][field]) or 0.0
            assert float(recipe[total]) == pytest.approx(round(expected, 1)), (rid, field)


def test_fixture_report_is_written_on_apply(fixture_paths):
    fix.run(apply=True)
    report = json.loads((fixture_paths["out"] / "applied_fix.json").read_text(encoding="utf-8"))
    assert report["status"] == "applied"
    assert report["rows_repaired_total"] == 46
    assert set(report["row_outcomes"]) == set(fix.REPAIR_IDS)
    assert set(report["approximation_caveats"]) == {"7053", "7031", "20039"}


def test_fixture_second_apply_is_a_no_op(fixture_paths):
    fix.run(apply=True)
    alias_bytes = fixture_paths["alias"].read_bytes()
    ing_bytes = fixture_paths["ing_csv"].read_bytes()
    recipes_bytes = fixture_paths["recipes_csv"].read_bytes()
    report = fix.run(apply=True)
    assert report["rows_repaired_now"] == 0
    assert report["rows_already_applied"] == 46
    assert set(report["alias_states"].values()) == {"already_applied"}
    assert fixture_paths["alias"].read_bytes() == alias_bytes
    assert fixture_paths["ing_csv"].read_bytes() == ing_bytes
    assert fixture_paths["recipes_csv"].read_bytes() == recipes_bytes


# --- Fail-closed drift detection ------------------------------------------

def test_fixture_unexpected_alias_value_aborts(fixture_paths):
    alias_map = _fx_alias_map(fixture_paths)
    alias_map["bóng bì"] = "7096"  # neither the reviewed old nor the reviewed new code
    fixture_paths["alias"].write_text(json.dumps(alias_map, ensure_ascii=False), encoding="utf-8")
    with pytest.raises(fix.DriftError, match="bóng bì"):
        fix.run(apply=False)


def test_fixture_missing_alias_key_aborts(fixture_paths):
    alias_map = _fx_alias_map(fixture_paths)
    del alias_map["cốt lết"]
    fixture_paths["alias"].write_text(json.dumps(alias_map, ensure_ascii=False), encoding="utf-8")
    with pytest.raises(fix.DriftError, match="cốt lết"):
        fix.run(apply=False)


def test_fixture_drifted_sibling_alias_aborts(fixture_paths):
    """The sibling families are this fix's evidence. "bóng bì lợn" on 7031 is
    the precedent the bóng bì repoint rests on; if it moved, the conclusion
    would no longer hold."""
    alias_map = _fx_alias_map(fixture_paths)
    alias_map["bóng bì lợn"] = "7064"
    fixture_paths["alias"].write_text(json.dumps(alias_map, ensure_ascii=False), encoding="utf-8")
    with pytest.raises(fix.DriftError, match="bóng bì lợn"):
        fix.run(apply=False)


def test_fixture_drifted_20039_sibling_alias_aborts(fixture_paths):
    """"thịt bò chay" on 20039 is the entire justification for repointing
    "thịt bò chay lát" there."""
    alias_map = _fx_alias_map(fixture_paths)
    alias_map["thịt bò chay"] = "7006"
    fixture_paths["alias"].write_text(json.dumps(alias_map, ensure_ascii=False), encoding="utf-8")
    with pytest.raises(fix.DriftError, match="thịt bò chay"):
        fix.run(apply=False)


def test_fixture_renamed_catalog_code_aborts(fixture_paths):
    with fixture_paths["master"].open(encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))
        fieldnames = list(rows[0].keys())
    for row in rows:
        if row["code"] == "7053":
            row["name_vi"] = "Sườn gì đó khác"
    _write_csv(fixture_paths["master"], rows, fieldnames)
    with pytest.raises(fix.DriftError, match="7053"):
        fix.run(apply=False)


def test_fixture_target_code_gaining_carbs_aborts(fixture_paths):
    """The reviewed null-carbs set is part of the policy: if 7053 suddenly
    declared carbs, the "41 rows keep null carbs" conclusion would be false."""
    with fixture_paths["master"].open(encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))
        fieldnames = list(rows[0].keys())
    for row in rows:
        if row["code"] == "7053":
            row["carbs_g"] = "1.2"
    _write_csv(fixture_paths["master"], rows, fieldnames)
    with pytest.raises(fix.DriftError, match="7053"):
        fix.run(apply=False)


def test_fixture_drifted_row_raw_text_aborts(fixture_paths):
    rows = list(_fx_rows(fixture_paths).values())
    for row in rows:
        if row["id"] in fix.REPAIR_IDS:
            row["raw_text"] = "something else entirely"
            break
    _write_csv(fixture_paths["ing_csv"], rows, ING_FIELDS)
    with pytest.raises(fix.DriftError, match="raw_text"):
        fix.run(apply=False)


def test_fixture_drifted_row_match_state_aborts(fixture_paths):
    rows = list(_fx_rows(fixture_paths).values())
    for row in rows:
        if row["id"] in fix.REPAIR_IDS:
            row["master_ingredient_code"] = "7096"
            break
    _write_csv(fixture_paths["ing_csv"], rows, ING_FIELDS)
    with pytest.raises(fix.DriftError):
        fix.run(apply=False)


def test_fixture_extra_reachable_row_aborts(fixture_paths):
    """A 47th row reachable by a reviewed alias means the blast radius is no
    longer the reviewed one -- nothing may be written."""
    rows = list(_fx_rows(fixture_paths).values())
    rows.append(_contaminated_row(
        "unreviewed-extra", "Cốt lết 200g", "cốt lết", "r-extra", "7070", 200.0,
    ))
    _write_csv(fixture_paths["ing_csv"], rows, ING_FIELDS)
    with pytest.raises(fix.DriftError, match="blast radius"):
        fix.run(apply=False)


def test_fixture_missing_row_aborts(fixture_paths):
    rows = [r for r in _fx_rows(fixture_paths).values() if r["id"] not in fix.REPAIR_IDS
            or r["id"] != sorted(fix.REPAIR_IDS)[0]]
    _write_csv(fixture_paths["ing_csv"], rows, ING_FIELDS)
    with pytest.raises(fix.DriftError):
        fix.run(apply=False)


def test_fixture_drifted_recipe_count_aborts(fixture_paths, monkeypatch):
    monkeypatch.setattr(fix, "EXPECTED_RECIPE_COUNT", 999)
    with pytest.raises(fix.DriftError, match="recipe count"):
        fix.run(apply=False)


# --- Real alias map + catalog ---------------------------------------------

@pytest.fixture(scope="module")
def real_alias_map():
    return json.loads(ALIAS_PATH.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def real_matcher():
    return VietnameseIngredientMatcher(catalog_csv_path=MASTER_CSV)


@pytest.fixture(scope="module")
def real_ing_rows():
    with ING_CSV.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def test_real_six_aliases_hold_their_reviewed_codes(real_alias_map):
    for key, (_, new) in fix.ALIAS_REPOINTS.items():
        assert real_alias_map[key] == new, f"{key!r} -> {real_alias_map[key]!r}"


def test_real_no_alias_key_was_added_or_removed(real_alias_map):
    """Follow-up repoints only; catalog repair removed two keys, and the
    display-name repair removed the two coriander seed/powder keys."""
    # DISPLAY_NAME_BATCH_C2 later removed 3 celery/fragment keys and added 5
    # white-cabbage keys, moving the live map 4672 -> 4674, and
    # DISPLAY_NAME_BATCH_C1 then removed 2 spinach/kale keys and added 8
    # mustard-green/napa/kimchi keys, moving it 4674 -> 4680. Batch C3 added
    # four reviewed white-cabbage aliases. This batch still added and removed
    # nothing; the four keys named below are still absent.
    assert len(real_alias_map) == 4684
    assert "mỡ gà" not in real_alias_map
    assert "đuôi heo đuôi lợn" not in real_alias_map
    assert "bột rau mùi" not in real_alias_map
    assert "hạt rau mùi" not in real_alias_map
    for key in fix.ALIAS_REPOINTS:
        assert key in real_alias_map


def test_real_sibling_aliases_did_not_regress(real_alias_map):
    for code, keys in fix.ALIAS_MUST_REMAIN.items():
        for key in keys:
            assert real_alias_map[key] == code, f"{key!r} -> {real_alias_map[key]!r}"


def test_real_still_deferred_findings_are_still_deferred(real_alias_map):
    """This fix applied the APPROVED subset only. The vegan analogues whose
    wet-vs-dry form policy the review did not settle stay exactly where they
    were, wrong though they are -- scope discipline, AGENTS.md §18."""
    for key, code in STILL_DEFERRED_ALIASES.items():
        assert real_alias_map[key] == code, f"{key!r} -> {real_alias_map[key]!r}"


def test_real_matcher_resolves_each_key_to_its_reviewed_identity(real_matcher):
    for key, (_, new) in fix.ALIAS_REPOINTS.items():
        result = real_matcher.match(key)
        assert result["matched_item"]["code"] == new, key
        assert result["matched_item"]["name_vi"] == fix.CODE_NAMES[new], key
        assert result["method"] == fix.PRESET_ALIAS_METHOD, key
        assert result["confidence"] == float(fix.PRESET_ALIAS_CONFIDENCE), key


def test_real_vacated_codes_keep_their_own_aliases(real_matcher):
    """Each vacated code is a legitimate identity; only the listed keys were wrong."""
    for query, code in (("giò thủ", "7070"), ("chả", "7064"), ("thịt bò lát", "7006")):
        assert real_matcher.match(query)["matched_item"]["code"] == code, query


def test_real_sibling_terms_still_reach_their_own_identities(real_matcher):
    """The neighbours whose behaviour must be unchanged by this fix -- including
    the ones whose existence justified it ("bóng bì lợn", "bò lát chay")."""
    for query, code in (("bóng bì lợn", "7031"), ("da heo", "7031"),
                        ("sườn heo", "7053"), ("xương heo", "7053"),
                        ("bò lát chay", "20039"), ("sườn non chay", "20039")):
        assert real_matcher.match(query)["matched_item"]["code"] == code, query


def test_real_deferred_chay_analogues_are_now_guarded(real_matcher):
    """This fix deliberately DEFERRED the vegan meat analogues, recording them
    as out of scope pending a reviewed policy ("any matcher-level chay guard").
    That policy has since been approved and implemented, so the three phrases
    this test previously pinned to their animal codes are now blocked at the
    resolution layer. Their alias-map keys are still present and still point at
    the animal codes -- the guard makes them inert rather than removing them.

    See nlp/entity_matcher.py::_blocks_vegetarian,
    tests/test_vegetarian_chay_animal_guard.py, and
    reports/eda/vegetarian_chay_animal_guard/applied_fix.md.
    """
    for query in ("đùi gà chay", "xúc xích chay", "nem chua chay", "thịt cua chay"):
        result = real_matcher.match(query)
        assert result["method"] == "UNMATCHED", query
        assert result["guard"] == "VEGETARIAN_PHRASE_ANIMAL_TARGET", query


def test_real_repoint_targets_exist_under_their_expected_names():
    with MASTER_CSV.open(encoding="utf-8-sig", newline="") as f:
        catalog = {r["code"]: r for r in csv.DictReader(f)}
    for code, name in fix.CODE_NAMES.items():
        assert catalog[code]["name_vi"].strip() == name, code
    for code in fix.NULL_CARBS_CODES:
        assert nutrition_value(catalog[code]["carbs_g"]) is None, code


def test_real_boneless_cot_let_rows_did_not_join_7053(real_ing_rows):
    """The reviewed scope is bone-in chop only. "cốt lết bỏ xương" is BONELESS
    and must not have been swept onto the rib identity -- it stays UNMATCHED
    until a separate review gives it a boneless-loin home."""
    boneless = [r for r in real_ing_rows if "bỏ xương" in (r.get("cleaned_name") or "")
                and "cốt lết" in (r.get("cleaned_name") or "")]
    assert len(boneless) == 3
    for row in boneless:
        assert row["match_method"] == "UNMATCHED", row["id"]
        assert _blank(row["master_ingredient_code"]), row["id"]


def test_real_vegan_cot_let_row_did_not_join_7053(real_ing_rows):
    """"sườn cốt lết chay" is a vegan row that must not be captured by the
    cốt lết repoint. It carries a "chay" qualifier the cleaner does not strip,
    so it never reaches the alias stage."""
    vegan = [r for r in real_ing_rows if (r.get("cleaned_name") or "") == "sườn cốt lết chay"]
    assert len(vegan) == 1
    assert vegan[0]["master_ingredient_code"] != "7053"
    assert vegan[0]["match_method"] == "UNMATCHED"


# --- Applied outcome on the real processed dataset ------------------------

def test_real_every_reviewed_row_is_on_its_reviewed_code(real_ing_rows):
    by_id = {r["id"]: r for r in real_ing_rows}
    for rid, raw_text in fix.REPAIR_RAW_BY_ID.items():
        row = by_id[rid]
        _, new = fix.ALIAS_REPOINTS[fix.ALIAS_BY_REPAIR_ID[rid]]
        assert row["raw_text"] == raw_text, rid
        assert row["master_ingredient_code"] == new, rid
        assert row["master_ingredient_name"] == fix.CODE_NAMES[new], rid
        assert row["match_method"] == fix.PRESET_ALIAS_METHOD, rid
        assert row["match_confidence"] == fix.PRESET_ALIAS_CONFIDENCE, rid


def test_real_code_populations_match_the_reviewed_outcome(real_ing_rows):
    counts = {}
    for row in real_ing_rows:
        code = (row.get("master_ingredient_code") or "").strip()
        if code in EXPECTED_CODE_ROWS:
            counts[code] = counts.get(code, 0) + 1
    for code, expected in EXPECTED_CODE_ROWS.items():
        assert counts.get(code, 0) == expected, code
    # Tie the pins above to this fix's own blast radius: of each target's
    # population, exactly the reviewed number arrived here through this fix.
    for code, gained in EXPECTED_ROWS_GAINED.items():
        arrived = {rid for rid in fix.REPAIR_IDS
                   if fix.ALIAS_REPOINTS[fix.ALIAS_BY_REPAIR_ID[rid]][1] == code}
        assert len(arrived) == gained, code
        assert gained <= counts[code], code


def test_real_seventy_seventy_keeps_only_gio_thu(real_ing_rows):
    """The vacated code is not orphaned, and nothing cốt lết remains on it."""
    rows = [r for r in real_ing_rows if r["master_ingredient_code"] == "7070"]
    assert len(rows) == 2
    assert {r["cleaned_name"] for r in rows} == {"giò thủ"}


def test_real_seventy_sixty_four_keeps_only_cha(real_ing_rows):
    rows = [r for r in real_ing_rows if r["master_ingredient_code"] == "7064"]
    assert len(rows) == 1
    assert rows[0]["cleaned_name"] == "chả"


def test_real_repaired_rows_have_catalog_consistent_nutrition(real_ing_rows):
    """Every repaired row's nutrition equals the live target profile scaled by
    that row's own weight -- not a hand-typed number.

    Recomputed through nlp.nutrition.scale_nutrition rather than by open-coded
    arithmetic: the scaling order (value * (weight/100) vs (value*weight)/100)
    changes the last rounded digit on some weights, and the row must match what
    the pipeline actually computes, not an equivalent-looking expression.
    """
    from nlp.nutrition import scale_nutrition

    with MASTER_CSV.open(encoding="utf-8-sig", newline="") as f:
        catalog = {r["code"]: r for r in csv.DictReader(f)}
    by_id = {r["id"]: r for r in real_ing_rows}
    for rid in fix.REPAIR_IDS:
        row = by_id[rid]
        code = row["master_ingredient_code"]
        weight = nutrition_value(row["estimated_weight_g"])
        for field, source in (("calories", "energy_kcal"), ("protein_g", "protein_g"),
                              ("fat_g", "fat_g"), ("carbs_g", "carbs_g")):
            expected = scale_nutrition(catalog[code][source], weight / 100.0, 1)
            if expected is None:
                assert _blank(row[field]), (rid, field)
            else:
                assert nutrition_value(row[field]) == expected, (rid, field)


def test_real_null_carbs_contract_holds_on_the_repaired_rows(real_ing_rows):
    by_id = {r["id"]: r for r in real_ing_rows}
    null_rows = 0
    for rid in fix.REPAIR_IDS:
        _, new = fix.ALIAS_REPOINTS[fix.ALIAS_BY_REPAIR_ID[rid]]
        if new in fix.NULL_CARBS_CODES:
            assert _blank(by_id[rid]["carbs_g"]), rid
            assert by_id[rid]["carbs_g"] != "0.0", rid
            null_rows += 1
    assert null_rows == 45


def test_real_unmatched_contract_is_untouched(real_ing_rows):
    """This fix writes no UNMATCHED row and no 0.0 confidence sentinel."""
    for row in real_ing_rows:
        if row["match_method"] != "UNMATCHED":
            continue
        assert _blank(row["master_ingredient_code"])
        assert _blank(row["master_ingredient_name"])
        assert _blank(row["match_confidence"])
        for field in NUTRITION_FIELDS:
            assert _blank(row[field])


def test_real_affected_recipe_totals_match_their_ingredient_rows(real_ing_rows):
    affected = {r["recipe_id"] for r in real_ing_rows if r["id"] in fix.REPAIR_IDS}
    assert len(affected) == fix.EXPECTED_RECIPE_COUNT
    sums = {}
    for row in real_ing_rows:
        if row["recipe_id"] not in affected:
            continue
        bucket = sums.setdefault(row["recipe_id"], dict.fromkeys(NUTRITION_FIELDS, 0.0))
        for field in NUTRITION_FIELDS:
            bucket[field] += nutrition_value(row[field]) or 0.0
    with RECIPES_CSV.open(encoding="utf-8-sig", newline="") as f:
        recipes = {r["id"]: r for r in csv.DictReader(f)}
    for rid, bucket in sums.items():
        for field, total in (("calories", "total_calories"), ("protein_g", "total_protein_g"),
                             ("fat_g", "total_fat_g"), ("carbs_g", "total_carbs_g")):
            assert float(recipes[rid][total]) == pytest.approx(round(bucket[field], 1)), (rid, field)


def test_real_processed_csv_json_parity_on_the_repaired_rows(real_ing_rows):
    json_rows = {r["id"]: r for r in json.loads(ING_JSON.read_text(encoding="utf-8-sig"))}
    by_id = {r["id"]: r for r in real_ing_rows}
    for rid in fix.REPAIR_IDS:
        for field in ("master_ingredient_code", "master_ingredient_name", "match_method",
                      "match_confidence", "estimated_weight_g", *NUTRITION_FIELDS):
            csv_value = by_id[rid][field]
            json_value = json_rows[rid].get(field)
            json_value = "" if json_value is None else str(json_value)
            assert str(csv_value) == json_value, (rid, field)


def test_real_recipes_csv_json_parity_on_the_affected_recipes(real_ing_rows):
    affected = {r["recipe_id"] for r in real_ing_rows if r["id"] in fix.REPAIR_IDS}
    with RECIPES_CSV.open(encoding="utf-8-sig", newline="") as f:
        csv_recipes = {r["id"]: r for r in csv.DictReader(f)}
    json_recipes = {r["id"]: r for r in json.loads(RECIPES_JSON.read_text(encoding="utf-8-sig"))}
    for rid in affected:
        for field in ("total_calories", "total_protein_g", "total_fat_g", "total_carbs_g"):
            assert str(csv_recipes[rid][field]) == str(json_recipes[rid][field]), (rid, field)


# --- Canonical propagation ------------------------------------------------

def test_real_canonical_rows_agree_with_processed(real_ing_rows):
    """Every repaired row that survives de-duplication carries the same identity
    in canonical output. Four do not survive: they are rank-2 duplicates whose
    representative is itself repaired, so every canonical dish is still correct.
    """
    with CANON_ING_CSV.open(encoding="utf-8-sig", newline="") as f:
        canon = {r["id"]: r for r in csv.DictReader(f)}
    by_id = {r["id"]: r for r in real_ing_rows}
    present = [rid for rid in fix.REPAIR_IDS if rid in canon]
    assert len(present) == 42
    assert len(fix.REPAIR_IDS) - len(present) == 4
    for rid in present:
        for field in ("master_ingredient_code", "master_ingredient_name", "match_method",
                      "match_confidence", *NUTRITION_FIELDS):
            assert canon[rid][field] == by_id[rid][field], (rid, field)


def test_real_no_cot_let_or_bong_bi_row_remains_on_a_vacated_code_in_canonical():
    with CANON_ING_CSV.open(encoding="utf-8-sig", newline="") as f:
        canon = list(csv.DictReader(f))
    stale = [r for r in canon
             if (r["master_ingredient_code"] == "7070" and "cốt lết" in r["cleaned_name"])
             or (r["master_ingredient_code"] == "7064" and r["cleaned_name"] == "bóng bì")]
    assert stale == []
