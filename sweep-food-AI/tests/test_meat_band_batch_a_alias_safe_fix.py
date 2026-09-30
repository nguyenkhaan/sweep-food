"""Tests for Batch A of the 70xx meat-band audit -- fifteen PRESET_ALIAS repoints.

Fifteen preset aliases resolved to a catalog identity of the wrong species, the
wrong animal part, or the wrong kingdom (pork belly terms on head cheese, duck
meat on duck liver, pigeon on wild chicken, a cheese on beef head, a mushroom on
chicken thigh, ...). Each was repointed -- never removed -- to the exact catalog
identity that already existed, keeping PRESET_ALIAS_MATCH / 0.98.

Three layers:

  * Fixture tests exercise
    scripts/eda/apply_meat_band_batch_a_alias_safe_fix.py against a small
    tmp_path dataset -- every module-level path constant is monkeypatched, so
    the real ~64k-row processed dataset and the real alias map are never
    touched. They cover the intended repoints, the blocked ones (cure-held and
    out-of-scope rows), fail-closed drift detection, and idempotency.
  * Matcher tests prove the resolution on the REAL alias map and catalog: each
    repointed key now lands on its reviewed code at PRESET_ALIAS_MATCH / 0.98,
    and the nearby identities that must not move (đùi gà chay, gà tre, gan vịt,
    đầu bò, nạm bò/ba chỉ bò, sườn bò) do not.

    The cốt lết family and "bóng bì" USED to be asserted here as still-deferred
    on 7070/7064. That deferral has since been reviewed and resolved by
    scripts/eda/apply_meat_band_batch_a_followup_safe_fix.py (cốt lết* -> 7053,
    "bóng bì" -> 7031, "thịt bò chay lát" -> 20039), so those assertions are
    replaced by the inverse invariant: Batch A must leave those keys alone on
    their NEW codes. See tests/test_meat_band_batch_a_followup_safe_fix.py for
    the follow-up's own coverage.
  * Real-data tests assert the applied outcome on the committed processed and
    canonical datasets: the fifteen alias values, the 111 repaired rows, the 15
    cure-held rows that must NOT have moved, the legitimate populations left on
    the vacated codes, CSV/JSON parity, and canonical propagation.
"""

import csv
import json
from pathlib import Path

import pytest

import scripts.eda.apply_meat_band_batch_a_alias_safe_fix as fix
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

NUTRITION_FIELDS = ("calories", "protein_g", "fat_g", "carbs_g")

# Post-fix master-code populations across the whole processed dataset. Every
# delta is accounted for by the 111 repaired rows; 7094 is unchanged because
# "bò hoa" is latent (all its rows are cure-held).
#
# 7070, 7064 and 7031 were RE-COUNTED after the reviewed follow-up
# (scripts/eda/apply_meat_band_batch_a_followup_safe_fix.py) moved 41 cốt lết
# rows off 7070 (43 -> 2, leaving only the giò thủ rows) and 4 bóng bì rows off
# 7064 (5 -> 1, leaving only the chả row) onto 7053 and 7031 (14 -> 18)
# respectively. Every other population here is Batch A's and is unchanged.
EXPECTED_CODE_ROWS = {
    "7070": 2, "7085": 33,
    "7068": 6, "7069": 17,
    "7064": 1, "7031": 18,
    "7001": 29, "7005": 53, "7043": 17, "7094": 110,
    "7012": 3, "7007": 10,
    "7042": 1, "7028": 62,
    "7035": 0, "10009": 22,
    # 7088 was 85 until the vegetarian "chay" guard cleared the two
    # "Đùi gà chay" analogue rows (f2c392cf, dcc433c7) to UNMATCHED --
    # see reports/eda/vegetarian_chay_animal_guard/applied_fix.md.
    "7088": 83, "7014": 2, "20007": 95,
}


def _blank(value):
    return value is None or str(value).strip() == ""


# =====================================================================
# Module-level policy invariants
# =====================================================================

def test_policy_tables_are_internally_consistent():
    assert len(fix.ALIAS_REPOINTS) == 15
    assert len(fix.REPAIR_IDS) == 111
    assert len(fix.CURE_IDS) == 15
    assert not fix.REPAIR_IDS & fix.CURE_IDS
    # Repoints only: no key is added or removed by this fix.
    assert all(old != new for old, new in fix.ALIAS_REPOINTS.values())


def test_every_repoint_target_differs_from_its_source():
    for key, (old, new) in fix.ALIAS_REPOINTS.items():
        assert old in fix.CODE_NAMES and new in fix.CODE_NAMES, key
        assert fix.CODE_NAMES[old] != fix.CODE_NAMES[new], key


def test_cure_pattern_partitions_the_reachable_rows():
    """Every cure-held row carries the "bắp bò" trigger; no repaired row does.

    This is the guard that keeps a repaired identity from being silently
    overwritten by scripts/run_qwen_line_pipeline.py on a later run.
    """
    for raw in fix.CURE_RAW_BY_ID.values():
        assert fix.CURE_RAW_PATTERN.search(raw.lower()), raw
    for raw in fix.REPAIR_RAW_BY_ID.values():
        assert not fix.CURE_RAW_PATTERN.search(raw.lower()), raw


def test_bo_hoa_is_the_only_latent_alias():
    assert fix.LATENT_ALIASES == ("bò hoa",)
    assert "bò hoa" not in fix.REPAIR_ROWS
    assert len(fix.CURE_HELD_ROWS["bò hoa"]) == 12


def test_no_reviewed_key_is_also_a_pinned_sibling():
    siblings = {k for keys in fix.ALIAS_MUST_REMAIN.values() for k in keys}
    assert not set(fix.ALIAS_REPOINTS) & siblings


# =====================================================================
# Fixture-based tests of the remediation script
# =====================================================================

ING_FIELDS = [
    "id", "recipe_id", "master_ingredient_code", "master_ingredient_name",
    "raw_text", "cleaned_name", "required_quantity", "unit_vi", "unit",
    "preparation_note", "match_confidence", "match_method",
    "estimated_weight_g", "calories", "protein_g", "fat_g", "carbs_g",
]

# Fixture catalog values. Several targets declare no carbs, exactly like the
# real rows -- repaired rows must end up null there, never 0.0.
FIX_MASTER = {
    "7001": {"energy_kcal": "171", "protein_g": "19.0", "fat_g": "10.5", "carbs_g": ""},
    "7005": {"energy_kcal": "121", "protein_g": "23.07", "fat_g": "3.16", "carbs_g": "0.1"},
    "7007": {"energy_kcal": "340", "protein_g": "17.5", "fat_g": "30", "carbs_g": ""},
    "7012": {"energy_kcal": "141", "protein_g": "24.4", "fat_g": "4.8", "carbs_g": ""},
    "7014": {"energy_kcal": "218", "protein_g": "20.06", "fat_g": "15.3", "carbs_g": "0.04"},
    "7028": {"energy_kcal": "267", "protein_g": "17.8", "fat_g": "21.8", "carbs_g": ""},
    "7031": {"energy_kcal": "118", "protein_g": "23.3", "fat_g": "2.7", "carbs_g": ""},
    "7035": {"energy_kcal": "185", "protein_g": "18.2", "fat_g": "12.4", "carbs_g": ""},
    "7042": {"energy_kcal": "136", "protein_g": "19.1", "fat_g": "5.3", "carbs_g": "3.5"},
    "7043": {"energy_kcal": "124", "protein_g": "30.2", "fat_g": "0.3", "carbs_g": ""},
    "7064": {"energy_kcal": "199", "protein_g": "12.4", "fat_g": "15.6", "carbs_g": "2.4"},
    "7068": {"energy_kcal": "402", "protein_g": "21.8", "fat_g": "34.8", "carbs_g": ""},
    "7069": {"energy_kcal": "205", "protein_g": "16.9", "fat_g": "15", "carbs_g": "1.8"},
    "7070": {"energy_kcal": "565", "protein_g": "20.8", "fat_g": "52.5", "carbs_g": ""},
    "7085": {"energy_kcal": "118", "protein_g": "23", "fat_g": "2.9", "carbs_g": "0.04"},
    "7088": {"energy_kcal": "137", "protein_g": "18.0", "fat_g": "6.8", "carbs_g": "0.9"},
    "7094": {"energy_kcal": "122", "protein_g": "21.75", "fat_g": "3.85", "carbs_g": ""},
    "10009": {"energy_kcal": "380", "protein_g": "25.5", "fat_g": "30.9", "carbs_g": ""},
    "20007": {"energy_kcal": "35", "protein_g": "3.0", "fat_g": "0.4", "carbs_g": "6.5"},
}

# Out-of-scope aliases that must survive this fix untouched, on codes this fix
# never writes. They sit outside ALIAS_MUST_REMAIN so the test proves the
# "no unrelated key changes" guard, not just the pinned-sibling guard.
OUT_OF_SCOPE_ALIASES = {
    "thịt ba chỉ rút sườn": "7018",
    # mỡ gà was removed by the reviewed catalog-integrity repair.
    "thịt heo quay": "7086",
    "xương bò": "7096",
    "đùi gà chay 20039": "20039",
    # Resolved by the reviewed follow-up, NOT by Batch A. They live here rather
    # than in ALIAS_MUST_REMAIN so the fixture proves the "no unrelated key
    # changes" guard holds them on their NEW codes -- the inverse of the
    # obsolete pin that used to hold them on 7070/7064.
    "sườn cốt lết": "7053",
    "thịt cốt lết": "7053",
    "cốt lết": "7053",
    "sườn cốt lết xắt lát": "7053",
    "bóng bì": "7031",
    "thịt bò chay lát": "20039",
}


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


def _cure_row(rid, raw_text, cleaned_name, recipe_id, weight):
    """A row the "bắp bò" cure already standardised onto 7094."""
    return _row(
        id=rid, recipe_id=recipe_id,
        master_ingredient_code=fix.CURE_CODE,
        master_ingredient_name=fix.CODE_NAMES[fix.CURE_CODE],
        raw_text=raw_text, cleaned_name=cleaned_name,
        required_quantity=str(weight), unit_vi="g", unit="GRAM",
        match_confidence=fix.CURE_CONFIDENCE, match_method=fix.CURE_METHOD,
        estimated_weight_g=str(round(weight, 1)), **_scaled(fix.CURE_CODE, weight),
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
    for i, (rid, raw_text) in enumerate(sorted(fix.REPAIR_RAW_BY_ID.items())):
        alias_key = fix.ALIAS_BY_REPAIR_ID[rid]
        old, _ = fix.ALIAS_REPOINTS[alias_key]
        weight = 100.0 + 10.0 * i
        weights[rid] = weight
        ing_rows.append(_contaminated_row(
            rid, raw_text, CLEANED_NAME_BY_ALIAS[alias_key], f"r-{i}", old, weight,
        ))
    for i, (rid, raw_text) in enumerate(sorted(fix.CURE_RAW_BY_ID.items())):
        alias_key = next(k for k, rows in fix.CURE_HELD_ROWS.items()
                         if rid in {r for r, _ in rows})
        weight = 200.0 + 10.0 * i
        weights[rid] = weight
        ing_rows.append(_cure_row(
            rid, raw_text, CLEANED_NAME_BY_ALIAS[alias_key], f"r-cure-{i}", weight,
        ))

    # Legitimate populations on vacated codes that must never move.
    ing_rows.append(_row(
        id="gan-vit-legit", recipe_id="r-gan-vit", master_ingredient_code="7042",
        master_ingredient_name=fix.CODE_NAMES["7042"], raw_text="Gan vịt 100g",
        cleaned_name="gan vịt", required_quantity="100.0", unit_vi="g", unit="GRAM",
        match_confidence=fix.PRESET_ALIAS_CONFIDENCE, match_method=fix.PRESET_ALIAS_METHOD,
        estimated_weight_g="100.0", **_scaled("7042", 100.0),
    ))
    # 7070's legitimate population is head cheese, not cốt lết: the cốt lết rows
    # that used to stand here were moved to 7053 by the reviewed follow-up.
    ing_rows.append(_row(
        id="gio-thu-legit", recipe_id="r-gio-thu", master_ingredient_code="7070",
        master_ingredient_name=fix.CODE_NAMES["7070"], raw_text="Giò thủ 300g",
        cleaned_name="giò thủ", required_quantity="300.0", unit_vi="g", unit="GRAM",
        match_confidence=fix.PRESET_ALIAS_CONFIDENCE, match_method=fix.PRESET_ALIAS_METHOD,
        estimated_weight_g="300.0", **_scaled("7070", 300.0),
    ))
    ing_rows.append(_row(
        id="dui-ga-chay-legit", recipe_id="r-chay", master_ingredient_code="7088",
        master_ingredient_name=fix.CODE_NAMES["7088"], raw_text="Đùi gà chay 200g",
        cleaned_name="đùi gà chay", required_quantity="200.0", unit_vi="g", unit="GRAM",
        match_confidence=fix.PRESET_ALIAS_CONFIDENCE, match_method=fix.PRESET_ALIAS_METHOD,
        estimated_weight_g="200.0", **_scaled("7088", 200.0),
    ))
    # Likewise 7064 keeps "chả", not "bóng bì" (follow-up: bóng bì -> 7031).
    ing_rows.append(_row(
        id="cha-legit", recipe_id="r-cha", master_ingredient_code="7064",
        master_ingredient_name=fix.CODE_NAMES["7064"], raw_text="Chả 50g",
        cleaned_name="chả", required_quantity="50.0", unit_vi="g", unit="GRAM",
        match_confidence=fix.PRESET_ALIAS_CONFIDENCE, match_method=fix.PRESET_ALIAS_METHOD,
        estimated_weight_g="50.0", **_scaled("7064", 50.0),
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
    assert report["alias_decision"] == "SAFE_REPOINT"
    assert report["alias_repoint_count"] == 15
    assert report["aliases_added"] == 0
    assert report["aliases_removed"] == 0
    assert report["rows_in_scope"] == 126
    assert report["rows_repaired_total"] == 111
    assert report["rows_repaired_now"] == 111
    assert report["rows_cure_held_untouched"] == 15
    assert report["match_method_semantics"]["row_level_overrides"] == 0
    assert report["latent_aliases"] == ["bò hoa"]


# --- Alias outcomes -------------------------------------------------------

def test_fixture_every_alias_is_repointed(fixture_paths):
    fix.run(apply=True)
    alias_map = _fx_alias_map(fixture_paths)
    for key, (_, new) in fix.ALIAS_REPOINTS.items():
        assert alias_map[key] == new, f"{key!r} -> {alias_map[key]!r}"


def test_fixture_no_alias_key_is_added_or_removed(fixture_paths):
    before = _fx_alias_map(fixture_paths)
    fix.run(apply=True)
    after = _fx_alias_map(fixture_paths)
    assert set(before) == set(after)
    assert len(before) == len(after)


def test_fixture_only_the_fifteen_keys_change(fixture_paths):
    before = _fx_alias_map(fixture_paths)
    fix.run(apply=True)
    after = _fx_alias_map(fixture_paths)
    changed = {k for k in before if before[k] != after[k]}
    assert changed == set(fix.ALIAS_REPOINTS)


def test_fixture_sibling_aliases_keep_their_codes(fixture_paths):
    fix.run(apply=True)
    alias_map = _fx_alias_map(fixture_paths)
    for code, keys in fix.ALIAS_MUST_REMAIN.items():
        for key in keys:
            assert alias_map[key] == code, f"{key!r} -> {alias_map[key]!r}"


def test_fixture_out_of_scope_aliases_untouched(fixture_paths):
    fix.run(apply=True)
    alias_map = _fx_alias_map(fixture_paths)
    for key, code in OUT_OF_SCOPE_ALIASES.items():
        assert alias_map[key] == code, f"{key!r} -> {alias_map[key]!r}"
    assert "mỡ gà" not in alias_map


# --- Row outcomes ---------------------------------------------------------

def test_fixture_every_repair_row_reaches_its_reviewed_identity(fixture_paths):
    fix.run(apply=True)
    rows = _fx_rows(fixture_paths)
    for rid in fix.REPAIR_IDS:
        _, new = fix.ALIAS_REPOINTS[fix.ALIAS_BY_REPAIR_ID[rid]]
        row = rows[rid]
        assert row["master_ingredient_code"] == new
        assert row["master_ingredient_name"] == fix.CODE_NAMES[new]


def test_fixture_match_method_and_confidence_are_preserved(fixture_paths):
    """Alias-resolved before, alias-resolved after: the semantics do not move."""
    fix.run(apply=True)
    rows = _fx_rows(fixture_paths)
    for rid in fix.REPAIR_IDS:
        assert rows[rid]["match_method"] == fix.PRESET_ALIAS_METHOD
        assert rows[rid]["match_confidence"] == fix.PRESET_ALIAS_CONFIDENCE
    for rid in fix.CURE_IDS:
        assert rows[rid]["match_method"] == fix.CURE_METHOD
        assert rows[rid]["match_confidence"] == fix.CURE_CONFIDENCE


def test_fixture_cure_held_rows_are_byte_identical(fixture_paths):
    before = _fx_rows(fixture_paths)
    fix.run(apply=True)
    after = _fx_rows(fixture_paths)
    for rid in fix.CURE_IDS:
        assert after[rid] == before[rid], rid


def test_fixture_bo_hoa_rows_do_not_move(fixture_paths):
    """The latent repoint must change zero rows."""
    before = _fx_rows(fixture_paths)
    fix.run(apply=True)
    after = _fx_rows(fixture_paths)
    for rid, _ in fix.CURE_HELD_ROWS["bò hoa"]:
        assert after[rid] == before[rid], rid
        assert after[rid]["master_ingredient_code"] == fix.CURE_CODE


def test_fixture_legitimate_rows_on_vacated_codes_are_untouched(fixture_paths):
    before = _fx_rows(fixture_paths)
    fix.run(apply=True)
    after = _fx_rows(fixture_paths)
    for rid in ("gan-vit-legit", "gio-thu-legit", "dui-ga-chay-legit", "cha-legit"):
        assert after[rid] == before[rid], rid


def test_fixture_no_unrelated_row_changes(fixture_paths):
    before = _fx_rows(fixture_paths)
    fix.run(apply=True)
    after = _fx_rows(fixture_paths)
    changed = {rid for rid in before if before[rid] != after[rid]}
    assert changed == set(fix.REPAIR_IDS)


def test_fixture_raw_context_and_weight_are_preserved(fixture_paths):
    before = _fx_rows(fixture_paths)
    fix.run(apply=True)
    after = _fx_rows(fixture_paths)
    for rid in fix.REPAIR_IDS:
        for field in ("raw_text", "cleaned_name", "required_quantity", "unit_vi",
                      "unit", "estimated_weight_g", "recipe_id"):
            assert after[rid][field] == before[rid][field], (rid, field)


def test_fixture_null_nutrition_is_never_converted_to_zero(fixture_paths):
    """Targets declaring no carbs must leave carbs_g null, not 0.0."""
    fix.run(apply=True)
    rows = _fx_rows(fixture_paths)
    checked = 0
    for rid in fix.REPAIR_IDS:
        _, new = fix.ALIAS_REPOINTS[fix.ALIAS_BY_REPAIR_ID[rid]]
        if FIX_MASTER[new]["carbs_g"] == "":
            assert _blank(rows[rid]["carbs_g"]), rid
            checked += 1
        else:
            assert not _blank(rows[rid]["carbs_g"]), rid
    assert checked > 0


def test_fixture_nutrition_is_scaled_from_the_target_catalog(fixture_paths):
    weights = fixture_paths["weights"]
    fix.run(apply=True)
    rows = _fx_rows(fixture_paths)
    for rid in fix.REPAIR_IDS:
        _, new = fix.ALIAS_REPOINTS[fix.ALIAS_BY_REPAIR_ID[rid]]
        expected = _scaled(new, weights[rid])
        for field in NUTRITION_FIELDS:
            assert (rows[rid][field] or "") == expected[field], (rid, field)


def test_fixture_csv_and_json_stay_in_parity(fixture_paths):
    fix.run(apply=True)
    csv_rows = _fx_rows(fixture_paths)
    json_rows = _fx_json_rows(fixture_paths)
    assert set(csv_rows) == set(json_rows)
    for rid, row in csv_rows.items():
        other = json_rows[rid]
        for field in ("master_ingredient_code", "master_ingredient_name",
                      "match_method", "match_confidence", *NUTRITION_FIELDS):
            assert (row[field] or "") == (other[field] or ""), (rid, field)


def test_fixture_recipe_totals_match_ingredient_sums(fixture_paths):
    fix.run(apply=True)
    rows = _fx_rows(fixture_paths)
    by_recipe = {}
    for row in rows.values():
        totals = by_recipe.setdefault(row["recipe_id"], dict.fromkeys(NUTRITION_FIELDS, 0.0))
        for field in NUTRITION_FIELDS:
            if not _blank(row[field]):
                totals[field] += float(row[field])
    with fixture_paths["recipes_csv"].open(encoding="utf-8-sig", newline="") as f:
        for rec in csv.DictReader(f):
            expected = by_recipe[rec["id"]]
            for field in NUTRITION_FIELDS:
                assert rec["total_" + field] == str(round(expected[field], 1)), rec["id"]


def test_fixture_report_is_written_on_apply(fixture_paths):
    fix.run(apply=True)
    report = json.loads((fixture_paths["out"] / "applied_fix.json").read_text(encoding="utf-8"))
    assert report["status"] == "applied"
    assert report["rows_repaired_now"] == 111
    assert report["rows_cure_held_untouched"] == 15
    assert len(report["row_outcomes"]) == 111
    assert len(report["cure_held_outcomes"]) == 15


# --- Idempotency ----------------------------------------------------------

def test_fixture_second_apply_is_a_byte_identical_no_op(fixture_paths):
    fix.run(apply=True)
    alias_bytes = fixture_paths["alias"].read_bytes()
    ing_bytes = fixture_paths["ing_csv"].read_bytes()
    recipes_bytes = fixture_paths["recipes_csv"].read_bytes()
    report = fix.run(apply=True)
    assert report["rows_repaired_now"] == 0
    assert report["rows_already_applied"] == 111
    assert set(report["alias_states"].values()) == {"already_applied"}
    assert fixture_paths["alias"].read_bytes() == alias_bytes
    assert fixture_paths["ing_csv"].read_bytes() == ing_bytes
    assert fixture_paths["recipes_csv"].read_bytes() == recipes_bytes


# --- Fail-closed drift detection ------------------------------------------

def test_fixture_unexpected_alias_value_aborts(fixture_paths):
    alias_map = _fx_alias_map(fixture_paths)
    alias_map["gân bò"] = "7096"  # neither the reviewed old nor the reviewed new code
    fixture_paths["alias"].write_text(json.dumps(alias_map, ensure_ascii=False), encoding="utf-8")
    with pytest.raises(fix.DriftError, match="gân bò"):
        fix.run(apply=False)


def test_fixture_drifted_sibling_alias_aborts(fixture_paths):
    """A pinned sibling moving off its code is still fail-closed.

    This used to be asserted with "bóng bì" -> 7031, which the reviewed
    follow-up has since made the CORRECT value. The guard is unchanged; only
    the example moved to a sibling that is genuinely still pinned.
    """
    alias_map = _fx_alias_map(fixture_paths)
    alias_map["giò thủ"] = "7053"  # an out-of-scope finding someone tried to sneak in
    fixture_paths["alias"].write_text(json.dumps(alias_map, ensure_ascii=False), encoding="utf-8")
    with pytest.raises(fix.DriftError, match="giò thủ"):
        fix.run(apply=False)


def test_fixture_followup_repointed_keys_are_not_touched_by_batch_a(fixture_paths):
    """Batch A must leave the follow-up's six keys exactly where they are.

    Replaces the obsolete assertion that held them on 7070/7064: the reviewed
    policy for them is now 7053/7031/20039, and Batch A still owns none of them.
    """
    before = _fx_alias_map(fixture_paths)
    fix.run(apply=True)
    after = _fx_alias_map(fixture_paths)
    for key in ("sườn cốt lết", "thịt cốt lết", "cốt lết", "sườn cốt lết xắt lát",
                "bóng bì", "thịt bò chay lát"):
        assert after[key] == before[key] == OUT_OF_SCOPE_ALIASES[key], key
        assert key not in fix.ALIAS_REPOINTS


def test_fixture_renamed_catalog_code_aborts(fixture_paths):
    with fixture_paths["master"].open(encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))
        fieldnames = list(rows[0].keys())
    for row in rows:
        if row["code"] == "7005":
            row["name_vi"] = "Thịt bò gì đó khác"
    _write_csv(fixture_paths["master"], rows, fieldnames)
    with pytest.raises(fix.DriftError, match="7005"):
        fix.run(apply=False)


def test_fixture_drifted_row_raw_text_aborts(fixture_paths):
    rows = list(_fx_rows(fixture_paths).values())
    target = next(r for r in rows if r["id"] in fix.REPAIR_IDS)
    target["raw_text"] = "something else entirely"
    _write_csv(fixture_paths["ing_csv"], rows, ING_FIELDS)
    with pytest.raises(fix.DriftError, match="raw_text drifted"):
        fix.run(apply=False)


def test_fixture_row_on_a_third_code_aborts(fixture_paths):
    rows = list(_fx_rows(fixture_paths).values())
    target = next(r for r in rows if r["id"] in fix.REPAIR_IDS)
    target["master_ingredient_code"] = "7096"
    target["master_ingredient_name"] = "Xương bò"
    _write_csv(fixture_paths["ing_csv"], rows, ING_FIELDS)
    with pytest.raises(fix.DriftError, match="neither pending"):
        fix.run(apply=False)


def test_fixture_cure_held_row_moved_off_7094_aborts(fixture_paths):
    rows = list(_fx_rows(fixture_paths).values())
    target = next(r for r in rows if r["id"] in fix.CURE_IDS)
    target["master_ingredient_code"] = "7001"
    target["master_ingredient_name"] = fix.CODE_NAMES["7001"]
    _write_csv(fixture_paths["ing_csv"], rows, ING_FIELDS)
    with pytest.raises(fix.DriftError, match="cure evidence has drifted"):
        fix.run(apply=False)


def test_fixture_missing_row_aborts(fixture_paths):
    rows = [r for r in _fx_rows(fixture_paths).values() if r["id"] not in fix.REPAIR_IDS]
    _write_csv(fixture_paths["ing_csv"], rows, ING_FIELDS)
    with pytest.raises(fix.DriftError, match="not found"):
        fix.run(apply=False)


def test_fixture_extra_reachable_row_aborts(fixture_paths):
    """A new row the alias reaches but nobody reviewed must stop the run."""
    rows = list(_fx_rows(fixture_paths).values())
    rows.append(_contaminated_row(
        "unreviewed-new-row", "Gân bò 999 gr", "gân bò", "r-new", "7001", 999.0,
    ))
    _write_csv(fixture_paths["ing_csv"], rows, ING_FIELDS)
    with pytest.raises(fix.DriftError, match="blast radius drifted"):
        fix.run(apply=False)


# =====================================================================
# Matcher tests against the REAL alias map and catalog
# =====================================================================

@pytest.fixture(scope="module")
def real_matcher():
    return VietnameseIngredientMatcher(catalog_csv_path=MASTER_CSV)


@pytest.mark.parametrize("alias_key", sorted(fix.ALIAS_REPOINTS))
def test_real_alias_resolves_to_its_reviewed_target(real_matcher, alias_key):
    _, new = fix.ALIAS_REPOINTS[alias_key]
    result = real_matcher.match(alias_key)
    assert result["matched_item"]["code"] == new, alias_key
    assert result["method"] == fix.PRESET_ALIAS_METHOD
    assert result["confidence"] == 0.98


@pytest.mark.parametrize("alias_key", sorted(fix.ALIAS_REPOINTS))
def test_real_alias_map_holds_the_reviewed_value(alias_key):
    alias_map = json.loads(ALIAS_PATH.read_text(encoding="utf-8"))
    _, new = fix.ALIAS_REPOINTS[alias_key]
    assert alias_map[alias_key] == new


def test_real_no_alias_key_was_added_or_removed():
    """Batch A repoints only; catalog repair removed two keys, and the
    display-name repair removed the two coriander seed/powder keys."""
    alias_map = json.loads(ALIAS_PATH.read_text(encoding="utf-8"))
    # DISPLAY_NAME_BATCH_C2 later removed 3 celery/fragment keys and added 5
    # white-cabbage keys, moving the live map 4672 -> 4674, and
    # DISPLAY_NAME_BATCH_C1 then removed 2 spinach/kale keys and added 8
    # mustard-green/napa/kimchi keys, moving it 4674 -> 4680. Batch C3 added
    # four reviewed white-cabbage aliases. This batch still added and removed
    # nothing; the four keys named below are still absent.
    assert len(alias_map) == 4684
    assert "mỡ gà" not in alias_map
    assert "đuôi heo đuôi lợn" not in alias_map
    assert "bột rau mùi" not in alias_map
    assert "hạt rau mùi" not in alias_map
    for key in fix.ALIAS_REPOINTS:
        assert key in alias_map


def test_real_sibling_aliases_did_not_regress():
    alias_map = json.loads(ALIAS_PATH.read_text(encoding="utf-8"))
    for code, keys in fix.ALIAS_MUST_REMAIN.items():
        for key in keys:
            assert alias_map[key] == code, f"{key!r} -> {alias_map[key]!r}"


def test_real_deferred_findings_are_still_deferred():
    """The out-of-scope siblings on the vacated codes must not have moved.

    The cốt lết family and "bóng bì" are deliberately absent here: their
    deferral was reviewed and resolved by the follow-up, and their new reviewed
    values are asserted in
    test_real_followup_resolved_findings_hold_their_new_codes below.
    """
    alias_map = json.loads(ALIAS_PATH.read_text(encoding="utf-8"))
    assert alias_map["đùi gà chay"] == "7088"
    assert alias_map["xúc xích chay"] == "7077"
    assert alias_map["nem chua chay"] == "7073"
    assert alias_map["thịt cua chay"] == "8069"
    assert alias_map["gà tre"] == "7012"
    assert alias_map["chả chiên"] == "7068"
    assert alias_map["nạm bò"] == "7001"
    assert alias_map["ba chỉ bò"] == "7001"
    assert alias_map["sườn bò"] == "7094"
    assert alias_map["dẻ sườn bò"] == "7094"


def test_real_followup_resolved_findings_hold_their_new_codes():
    """The two deferrals Batch A recorded that have since been resolved.

    Kept in this file so Batch A's own contract stays complete: these keys left
    its vacated codes by a reviewed decision, not by drift, and Batch A must
    neither pin them nor pull them back.
    """
    alias_map = json.loads(ALIAS_PATH.read_text(encoding="utf-8"))
    for key in ("cốt lết", "sườn cốt lết", "sườn cốt lết xắt lát", "thịt cốt lết"):
        assert alias_map[key] == "7053", key
    assert alias_map["bóng bì"] == "7031"
    assert alias_map["thịt bò chay lát"] == "20039"
    pinned = {k for keys in fix.ALIAS_MUST_REMAIN.values() for k in keys}
    for key in ("cốt lết", "sườn cốt lết", "sườn cốt lết xắt lát", "thịt cốt lết",
                "bóng bì", "thịt bò chay lát"):
        assert key not in fix.ALIAS_REPOINTS, key
        assert key not in pinned, key


def test_real_vacated_codes_keep_their_own_aliases(real_matcher):
    """Each vacated code is a legitimate identity; only the listed keys were wrong."""
    for query, code in (("gan vịt", "7042"), ("đầu bò", "7035"), ("đùi gà", "7088"),
                        ("giò bò", "7068"), ("chả lợn", "7064"), ("thịt bê mỡ", "7001"),
                        ("thịt gà rừng", "7012")):
        result = real_matcher.match(query)
        assert result["matched_item"]["code"] == code, query


def test_real_repoint_targets_exist_under_their_expected_names():
    with MASTER_CSV.open(encoding="utf-8-sig", newline="") as f:
        catalog = {r["code"]: r["name_vi"].strip() for r in csv.DictReader(f)}
    for code, name in fix.CODE_NAMES.items():
        assert catalog[code] == name, code


def test_real_stage_one_does_not_shadow_any_repointed_alias(real_matcher):
    """If a key were also a catalog name, Stage 1 would fire and the repoint
    would be dead code. None of the fifteen is."""
    for key in fix.ALIAS_REPOINTS:
        assert normalize_vietnamese_text(key) not in real_matcher.normalized_to_index, key
        assert clean_culinary_query(key) not in real_matcher.normalized_to_index, key


# =====================================================================
# Real-data tests on the applied processed + canonical datasets
# =====================================================================

@pytest.fixture(scope="module")
def real_ing_rows():
    with ING_CSV.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


@pytest.fixture(scope="module")
def real_ing_by_id(real_ing_rows):
    return {r["id"]: r for r in real_ing_rows}


def test_real_every_repaired_row_is_on_its_reviewed_identity(real_ing_by_id):
    for rid in fix.REPAIR_IDS:
        _, new = fix.ALIAS_REPOINTS[fix.ALIAS_BY_REPAIR_ID[rid]]
        row = real_ing_by_id[rid]
        assert row["master_ingredient_code"] == new, rid
        assert row["master_ingredient_name"] == fix.CODE_NAMES[new], rid
        assert row["match_method"] == fix.PRESET_ALIAS_METHOD, rid
        assert row["match_confidence"] == fix.PRESET_ALIAS_CONFIDENCE, rid
        assert row["raw_text"] == fix.REPAIR_RAW_BY_ID[rid], rid


def test_real_cure_held_rows_are_still_on_7094(real_ing_by_id):
    for rid in fix.CURE_IDS:
        row = real_ing_by_id[rid]
        assert row["master_ingredient_code"] == fix.CURE_CODE, rid
        assert row["master_ingredient_name"] == fix.CODE_NAMES[fix.CURE_CODE], rid
        assert row["match_method"] == fix.CURE_METHOD, rid
        assert row["raw_text"] == fix.CURE_RAW_BY_ID[rid], rid


def test_real_bo_hoa_rows_did_not_change(real_ing_by_id):
    """The latent repoint moved nothing: all 12 are cure-held beef shank."""
    for rid, raw in fix.CURE_HELD_ROWS["bò hoa"]:
        row = real_ing_by_id[rid]
        assert row["master_ingredient_code"] == fix.CURE_CODE, rid
        assert row["match_method"] == fix.CURE_METHOD, rid
        assert row["raw_text"] == raw


@pytest.mark.parametrize("code,expected", sorted(EXPECTED_CODE_ROWS.items()))
def test_real_master_code_populations(real_ing_rows, code, expected):
    actual = sum(1 for r in real_ing_rows
                 if (r["master_ingredient_code"] or "").strip() == code)
    assert actual == expected, code


def test_real_no_row_outside_the_repair_set_sits_on_a_repointed_identity_by_a_reviewed_alias(
    real_ing_rows,
):
    """Rows still on a vacated code must have got there by some other route."""
    reviewed_cleaned = {normalize_vietnamese_text(k) for k in fix.ALIAS_REPOINTS}
    for row in real_ing_rows:
        code = (row["master_ingredient_code"] or "").strip()
        if code not in {old for old, _ in fix.ALIAS_REPOINTS.values()}:
            continue
        cleaned = normalize_vietnamese_text(row.get("cleaned_name") or "")
        assert cleaned not in reviewed_cleaned, row["id"]


def test_real_null_nutrition_semantics_hold(real_ing_by_id):
    with MASTER_CSV.open(encoding="utf-8-sig", newline="") as f:
        catalog = {r["code"]: r for r in csv.DictReader(f)}
    sources = {"calories": "energy_kcal", "protein_g": "protein_g",
               "fat_g": "fat_g", "carbs_g": "carbs_g"}
    nulls_seen = 0
    for rid in fix.REPAIR_IDS:
        row = real_ing_by_id[rid]
        master = catalog[row["master_ingredient_code"]]
        for field, source in sources.items():
            if _blank(master[source]):
                assert _blank(row[field]), (rid, field)
                nulls_seen += 1
            else:
                assert not _blank(row[field]), (rid, field)
    assert nulls_seen > 0, "expected at least one null-carb target in the repair set"


def test_real_csv_json_parity_for_repaired_and_cure_held_rows():
    json_rows = {r["id"]: r for r in json.loads(ING_JSON.read_text(encoding="utf-8-sig"))}
    with ING_CSV.open(encoding="utf-8-sig", newline="") as f:
        csv_rows = {r["id"]: r for r in csv.DictReader(f)}
    assert len(csv_rows) == len(json_rows)
    for rid in fix.REPAIR_IDS | fix.CURE_IDS:
        a, b = csv_rows[rid], json_rows[rid]
        for field in ("master_ingredient_code", "master_ingredient_name", "match_method",
                      "match_confidence", "raw_text", "cleaned_name",
                      "estimated_weight_g", *NUTRITION_FIELDS):
            assert (a[field] or "") == (b.get(field) or ""), (rid, field)


def test_real_recipe_totals_agree_with_ingredient_sums(real_ing_rows):
    affected = {real_ing_rows_by_id["recipe_id"]
                for real_ing_rows_by_id in real_ing_rows
                if real_ing_rows_by_id["id"] in fix.REPAIR_IDS}
    sums = {}
    for row in real_ing_rows:
        rid = row.get("recipe_id")
        if rid not in affected:
            continue
        totals = sums.setdefault(rid, dict.fromkeys(NUTRITION_FIELDS, 0.0))
        for field in NUTRITION_FIELDS:
            if not _blank(row[field]):
                totals[field] += float(row[field])
    with RECIPES_CSV.open(encoding="utf-8-sig", newline="") as f:
        checked = 0
        for rec in csv.DictReader(f):
            if rec["id"] not in sums:
                continue
            checked += 1
            for field in NUTRITION_FIELDS:
                assert rec["total_" + field] == str(round(sums[rec["id"]][field], 1)), rec["id"]
    assert checked == len(affected) == 105


def test_real_recipes_csv_json_totals_parity():
    json_recipes = {r["id"]: r for r in json.loads(RECIPES_JSON.read_text(encoding="utf-8-sig"))}
    with RECIPES_CSV.open(encoding="utf-8-sig", newline="") as f:
        for rec in csv.DictReader(f):
            other = json_recipes[rec["id"]]
            for field in ("total_calories", "total_protein_g", "total_fat_g", "total_carbs_g"):
                assert (rec[field] or "") == (str(other.get(field)) or ""), rec["id"]


def test_real_canonical_propagated_the_repaired_identities():
    """Canonical rows carry the new identity; none carries a vacated one by a
    reviewed alias. Three repaired rows are absent because their recipe was
    deduplicated into a different representative."""
    with CANON_ING_CSV.open(encoding="utf-8-sig", newline="") as f:
        canon = {r["id"]: r for r in csv.DictReader(f)}
    present = fix.REPAIR_IDS & set(canon)
    assert len(present) == 108
    for rid in present:
        _, new = fix.ALIAS_REPOINTS[fix.ALIAS_BY_REPAIR_ID[rid]]
        assert canon[rid]["master_ingredient_code"] == new, rid
        assert canon[rid]["master_ingredient_name"] == fix.CODE_NAMES[new], rid


def test_real_canonical_cure_held_rows_still_on_7094():
    with CANON_ING_CSV.open(encoding="utf-8-sig", newline="") as f:
        canon = {r["id"]: r for r in csv.DictReader(f)}
    for rid in fix.CURE_IDS & set(canon):
        assert canon[rid]["master_ingredient_code"] == fix.CURE_CODE, rid
        assert canon[rid]["match_method"] == fix.CURE_METHOD, rid


def test_real_canonical_recipe_set_did_not_drift():
    with CANON_RECIPES_CSV.open(encoding="utf-8-sig", newline="") as f:
        recipes = list(csv.DictReader(f))
    with CANON_ING_CSV.open(encoding="utf-8-sig", newline="") as f:
        ingredients = list(csv.DictReader(f))
    assert len(recipes) == 5479
    assert len(ingredients) == 62023
    recipe_ids = {r["id"] for r in recipes}
    assert all(row["recipe_id"] in recipe_ids for row in ingredients)
