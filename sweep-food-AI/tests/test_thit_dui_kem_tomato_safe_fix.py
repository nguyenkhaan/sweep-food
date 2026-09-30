"""Tests for scripts/eda/apply_thit_dui_kem_tomato_safe_fix.py against small
fixtures. Never touches the real ~64k-row processed dataset or the real
alias map: all module-level path constants are monkeypatched to a tmp_path
fixture.
"""

import csv
import json

import pytest

import scripts.eda.apply_thit_dui_kem_tomato_safe_fix as fix

CLEAR_ID_1, CLEAR_RAW_1 = fix.CLEAR_ROWS[0]
CLEAR_ID_2, CLEAR_RAW_2 = fix.CLEAR_ROWS[1]
CLEAR_ID_3, CLEAR_RAW_3 = fix.CLEAR_ROWS[2]
CLEAR_ID_4, CLEAR_RAW_4 = fix.CLEAR_ROWS[3]

THIT_DUI_ALIAS_KEY = "thịt đùi"
KEM_ALIAS_KEY = "kem"


def _write_csv(path, rows, fieldnames):
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


ING_FIELDS = [
    "id", "recipe_id", "master_ingredient_code", "master_ingredient_name",
    "raw_text", "cleaned_name", "required_quantity", "unit_vi", "unit",
    "preparation_note", "match_confidence", "match_method",
    "estimated_weight_g", "calories", "protein_g", "fat_g", "carbs_g",
]


def _row(**kwargs):
    base = {f: "" for f in ING_FIELDS}
    base.update(kwargs)
    return base


@pytest.fixture
def fixture_paths(tmp_path, monkeypatch):
    alias_path = tmp_path / "ingredient_alias_map.json"
    master_csv = tmp_path / "master.csv"
    ing_csv = tmp_path / "recipe_ingredients.csv"
    ing_json = tmp_path / "recipe_ingredients.json"
    recipes_csv = tmp_path / "recipes.csv"
    recipes_json = tmp_path / "recipes.json"
    out_dir = tmp_path / "reports"

    alias_map = {
        THIT_DUI_ALIAS_KEY: "7080",
        KEM_ALIAS_KEY: "12073",
        fix.ALIAS_CHANGE_KEY: fix.ALIAS_CHANGE_OLD,
        # Unrelated aliases that must survive every run untouched.
        "ếch thịt đùi": "7080",
        "kem tươi": "20070",
        "cà chua cô đặc": "4005",
    }
    alias_path.write_text(json.dumps(alias_map, ensure_ascii=False, indent=2), encoding="utf-8")

    master_fields = ["code", "name_vi", "energy_kcal", "protein_g", "fat_g", "carbs_g"]
    _write_csv(master_csv, [
        {"code": "7080", "name_vi": fix.CLEAR_OLD_NAME, "energy_kcal": "90", "protein_g": "20", "fat_g": "1.1", "carbs_g": ""},
        {"code": "12073", "name_vi": fix.KEM_REMAP_OLD_NAME, "energy_kcal": "199", "protein_g": "1.9", "fat_g": "8.4", "carbs_g": "27.6"},
        {"code": fix.KEM_REMAP_NEW_CODE, "name_vi": fix.KEM_REMAP_NEW_NAME, "energy_kcal": "345", "protein_g": "2.1", "fat_g": "37.0", "carbs_g": "2.8"},
        {"code": fix.KETCHUP_REMAP_NEW_CODE, "name_vi": fix.KETCHUP_REMAP_NEW_NAME, "energy_kcal": "115", "protein_g": "1.1", "fat_g": "0.1", "carbs_g": "27.4"},
        {"code": "4005", "name_vi": fix.KETCHUP_REMAP_OLD_NAME, "energy_kcal": "24", "protein_g": "0.6", "fat_g": "0.23", "carbs_g": "4.77"},
    ], master_fields)

    def _clear_row(rid, raw_text, recipe_id):
        return _row(
            id=rid, recipe_id=recipe_id, master_ingredient_code=fix.CLEAR_OLD_CODE,
            master_ingredient_name=fix.CLEAR_OLD_NAME, raw_text=raw_text, cleaned_name="thịt đùi",
            required_quantity="300.0", unit_vi="g", unit="GRAM",
            match_confidence=fix.PRESET_ALIAS_CONFIDENCE, match_method=fix.PRESET_ALIAS_METHOD,
            estimated_weight_g="300.0", calories="270.0", protein_g="60.0", fat_g="3.3", carbs_g="",
        )

    ing_rows = [
        _clear_row(CLEAR_ID_1, CLEAR_RAW_1, "r-clear-1"),
        _clear_row(CLEAR_ID_2, CLEAR_RAW_2, "r-clear-2"),
        _clear_row(CLEAR_ID_3, CLEAR_RAW_3, "r-clear-3"),
        _clear_row(CLEAR_ID_4, CLEAR_RAW_4, "r-clear-4"),
        # Approved kem->cream row remap.
        _row(id=fix.KEM_REMAP_ROW_ID, recipe_id="r-kem", master_ingredient_code=fix.KEM_REMAP_OLD_CODE,
             master_ingredient_name=fix.KEM_REMAP_OLD_NAME, raw_text=fix.KEM_REMAP_RAW_TEXT,
             cleaned_name="kem", required_quantity="120.0", unit_vi="ml", unit="ML",
             match_confidence=fix.PRESET_ALIAS_CONFIDENCE, match_method=fix.PRESET_ALIAS_METHOD,
             estimated_weight_g="120.0", calories="238.8", protein_g="3.8", fat_g="10.1", carbs_g="33.1"),
        # Approved ketchup row remap.
        _row(id=fix.KETCHUP_REMAP_ROW_ID, recipe_id="r-ketchup", master_ingredient_code=fix.KETCHUP_REMAP_OLD_CODE,
             master_ingredient_name=fix.KETCHUP_REMAP_OLD_NAME, raw_text=fix.KETCHUP_REMAP_RAW_TEXT,
             cleaned_name="tương cà chua kechup", required_quantity="2.0", unit_vi="muỗng canh", unit="MUONG_CANH",
             match_confidence=fix.PRESET_ALIAS_CONFIDENCE, match_method=fix.PRESET_ALIAS_METHOD,
             estimated_weight_g="30.0", calories="7.2", protein_g="0.2", fat_g="0.1", carbs_g="1.4"),
        # Qualified frog alias usage -- NOT a target row, must never be touched.
        _row(id="frog-qualified-row", recipe_id="r-frog", master_ingredient_code="7080",
             master_ingredient_name=fix.CLEAR_OLD_NAME, raw_text="Ếch thịt đùi 200g",
             cleaned_name="ếch thịt đùi", required_quantity="200.0", unit_vi="g", unit="GRAM",
             match_confidence=fix.PRESET_ALIAS_CONFIDENCE, match_method=fix.PRESET_ALIAS_METHOD,
             estimated_weight_g="200.0", calories="180.0", protein_g="40.0", fat_g="2.2", carbs_g=""),
        # Qualified cream alias usage -- NOT a target row, must never be touched.
        _row(id="cream-qualified-row", recipe_id="r-cream", master_ingredient_code=fix.KEM_REMAP_NEW_CODE,
             master_ingredient_name=fix.KEM_REMAP_NEW_NAME, raw_text="Whipping cream 50g",
             cleaned_name="whipping cream", required_quantity="50.0", unit_vi="g", unit="GRAM",
             match_confidence=fix.PRESET_ALIAS_CONFIDENCE, match_method=fix.PRESET_ALIAS_METHOD,
             estimated_weight_g="50.0", calories="172.5", protein_g="1.1", fat_g="18.5", carbs_g="1.4"),
        # Unresolved tomato-paste row -- explicitly out of scope, must never be touched.
        _row(id="tomato-unresolved-row", recipe_id="r-tomato", master_ingredient_code="4005",
             master_ingredient_name=fix.KETCHUP_REMAP_OLD_NAME, raw_text="Cà chua cô đặc 50g",
             cleaned_name="cà chua cô đặc", required_quantity="50.0", unit_vi="g", unit="GRAM",
             match_confidence=fix.PRESET_ALIAS_CONFIDENCE, match_method=fix.PRESET_ALIAS_METHOD,
             estimated_weight_g="50.0", calories="12.0", protein_g="0.3", fat_g="0.1", carbs_g="2.4"),
        # Already-UNMATCHED row: invariants (blank code/name/confidence/nutrition) must hold.
        _row(id="unmatched-row", recipe_id="r-um", master_ingredient_code="",
             master_ingredient_name="", raw_text="gia vị không rõ", cleaned_name="gia vị",
             match_confidence="", match_method="UNMATCHED",
             estimated_weight_g="10.0", calories="", protein_g="", fat_g="", carbs_g=""),
    ]
    _write_csv(ing_csv, ing_rows, ING_FIELDS)
    ing_json.write_text(json.dumps(ing_rows, ensure_ascii=False), encoding="utf-8")

    recipe_fields = ["id", "total_calories", "total_protein_g", "total_fat_g", "total_carbs_g", "ingredients_count"]
    recipe_totals = {
        "r-clear-1": ("270.0", "60.0", "3.3", "0.0"),
        "r-clear-2": ("270.0", "60.0", "3.3", "0.0"),
        "r-clear-3": ("270.0", "60.0", "3.3", "0.0"),
        "r-clear-4": ("270.0", "60.0", "3.3", "0.0"),
        "r-kem": ("238.8", "3.8", "10.1", "33.1"),
        "r-ketchup": ("7.2", "0.2", "0.1", "1.4"),
        "r-frog": ("180.0", "40.0", "2.2", "0.0"),
        "r-cream": ("172.5", "1.1", "18.5", "1.4"),
        "r-tomato": ("12.0", "0.3", "0.1", "2.4"),
        "r-um": ("0.0", "0.0", "0.0", "0.0"),
    }
    recipes = [
        {"id": rid, "total_calories": t[0], "total_protein_g": t[1], "total_fat_g": t[2],
         "total_carbs_g": t[3], "ingredients_count": "1"}
        for rid, t in recipe_totals.items()
    ]
    _write_csv(recipes_csv, recipes, recipe_fields)

    initial_status = {rid: ("COMPLETE", 0) for rid in recipe_totals}
    initial_status["r-um"] = ("INCOMPLETE", 1)
    recipes_json_rows = [
        dict(r, nutrition_status=initial_status[r["id"]][0], missing_nutrition_count=initial_status[r["id"]][1])
        for r in recipes
    ]
    recipes_json.write_text(json.dumps(recipes_json_rows, ensure_ascii=False), encoding="utf-8")

    monkeypatch.setattr(fix, "ALIAS_PATH", alias_path)
    monkeypatch.setattr(fix, "MASTER", master_csv)
    monkeypatch.setattr(fix, "ING", ing_csv)
    monkeypatch.setattr(fix, "ING_JSON", ing_json)
    monkeypatch.setattr(fix, "RECIPES_CSV", recipes_csv)
    monkeypatch.setattr(fix, "RECIPES_JSON", recipes_json)
    monkeypatch.setattr(fix, "OUT", out_dir)

    return {
        "alias_path": alias_path, "ing_csv": ing_csv, "ing_json": ing_json,
        "recipes_csv": recipes_csv, "recipes_json": recipes_json,
    }


def _alias_map(paths):
    return json.loads(paths["alias_path"].read_text(encoding="utf-8"))


def _ing_rows(paths):
    return {r["id"]: r for r in csv.DictReader(paths["ing_csv"].open(encoding="utf-8", newline=""))}


# --- Alias-map edits ---------------------------------------------------

def test_thit_dui_alias_removed(fixture_paths):
    fix.run(apply=True)
    assert THIT_DUI_ALIAS_KEY not in _alias_map(fixture_paths)


def test_bare_kem_alias_removed(fixture_paths):
    fix.run(apply=True)
    assert KEM_ALIAS_KEY not in _alias_map(fixture_paths)


def test_ketchup_alias_points_to_13032(fixture_paths):
    fix.run(apply=True)
    assert _alias_map(fixture_paths)[fix.ALIAS_CHANGE_KEY] == "13032"


def test_unrelated_frog_alias_preserved(fixture_paths):
    fix.run(apply=True)
    assert _alias_map(fixture_paths)["ếch thịt đùi"] == "7080"


def test_qualified_cream_alias_preserved(fixture_paths):
    fix.run(apply=True)
    assert _alias_map(fixture_paths)["kem tươi"] == "20070"


def test_unresolved_tomato_alias_preserved(fixture_paths):
    fix.run(apply=True)
    assert _alias_map(fixture_paths)["cà chua cô đặc"] == "4005"


def test_alias_map_only_the_three_target_keys_change(fixture_paths):
    before = _alias_map(fixture_paths)
    fix.run(apply=True)
    after = _alias_map(fixture_paths)
    touched = {THIT_DUI_ALIAS_KEY, KEM_ALIAS_KEY, fix.ALIAS_CHANGE_KEY}
    for key, value in before.items():
        if key in touched:
            continue
        assert after.get(key) == value, f"unrelated alias {key!r} changed"


# --- Row-level CLEAR (thit dui) -----------------------------------------

def test_four_thit_dui_rows_cleared(fixture_paths):
    report = fix.run(apply=True)
    assert report["clear_applied_now"] == 4

    rows = _ing_rows(fixture_paths)
    for rid in (CLEAR_ID_1, CLEAR_ID_2, CLEAR_ID_3, CLEAR_ID_4):
        r = rows[rid]
        assert r["master_ingredient_code"] in (None, "")
        assert r["master_ingredient_name"] in (None, "")
        assert r["match_method"] == "UNMATCHED"
        assert r["match_confidence"] in (None, "")
        for f in ("calories", "protein_g", "fat_g", "carbs_g"):
            assert r[f] in (None, ""), f"{f} should be null, not zero, for cleared row {rid}"


def test_clear_does_not_remap_to_a_pork_code(fixture_paths):
    fix.run(apply=True)
    rows = _ing_rows(fixture_paths)
    for rid in (CLEAR_ID_1, CLEAR_ID_2, CLEAR_ID_3, CLEAR_ID_4):
        assert rows[rid]["master_ingredient_code"] != "7084"
        assert rows[rid]["master_ingredient_code"] != "7088"
        assert rows[rid]["master_ingredient_code"] != "7032"


# --- Row-level REMAP (kem -> 20070, ketchup -> 13032) -------------------

def test_kem_row_remapped_to_whipping_cream(fixture_paths):
    report = fix.run(apply=True)
    assert report["remap_applied_now"] == 2

    row = _ing_rows(fixture_paths)[fix.KEM_REMAP_ROW_ID]
    assert row["master_ingredient_code"] == "20070"
    assert row["master_ingredient_name"] == fix.KEM_REMAP_NEW_NAME
    assert row["match_method"] == "PRESET_ALIAS_MATCH"
    assert row["match_confidence"] == "0.98"
    # weight 120g at 345 kcal / 2.1 protein / 37.0 fat / 2.8 carbs per 100g
    assert row["calories"] == "414.0"
    assert row["protein_g"] == "2.5"
    assert row["fat_g"] == "44.4"
    assert row["carbs_g"] == "3.4"


def test_ketchup_row_remapped_to_13032(fixture_paths):
    fix.run(apply=True)
    row = _ing_rows(fixture_paths)[fix.KETCHUP_REMAP_ROW_ID]
    assert row["master_ingredient_code"] == "13032"
    assert row["master_ingredient_name"] == fix.KETCHUP_REMAP_NEW_NAME
    assert row["match_method"] == "PRESET_ALIAS_MATCH"
    assert row["match_confidence"] == "0.98"
    # weight 30g at 115 kcal / 1.1 protein / 0.1 fat / 27.4 carbs per 100g
    assert row["calories"] == "34.5"
    assert row["protein_g"] == "0.3"
    assert row["fat_g"] == "0.0"
    assert row["carbs_g"] == "8.2"


def test_no_global_kem_remap_created(fixture_paths):
    """The bare 'kem' alias must be removed, not repointed to 20070 -- only
    the one reviewed row is remapped."""
    fix.run(apply=True)
    assert _alias_map(fixture_paths).get(KEM_ALIAS_KEY) is None


# --- Untouched rows ------------------------------------------------------

def test_unresolved_tomato_row_untouched(fixture_paths):
    before = json.loads(fixture_paths["ing_json"].read_text(encoding="utf-8"))
    before_row = next(r for r in before if r["id"] == "tomato-unresolved-row")

    fix.run(apply=True)

    after = json.loads(fixture_paths["ing_json"].read_text(encoding="utf-8"))
    after_row = next(r for r in after if r["id"] == "tomato-unresolved-row")
    assert after_row == before_row


def test_qualified_frog_row_untouched(fixture_paths):
    fix.run(apply=True)
    row = _ing_rows(fixture_paths)["frog-qualified-row"]
    assert row["master_ingredient_code"] == "7080"
    assert row["match_method"] == "PRESET_ALIAS_MATCH"


def test_qualified_cream_row_untouched(fixture_paths):
    fix.run(apply=True)
    row = _ing_rows(fixture_paths)["cream-qualified-row"]
    assert row["master_ingredient_code"] == "20070"
    assert row["calories"] == "172.5"


def test_unmatched_invariants_preserved(fixture_paths):
    fix.run(apply=True)
    row = _ing_rows(fixture_paths)["unmatched-row"]
    assert row["match_method"] == "UNMATCHED"
    assert row["master_ingredient_code"] in (None, "")
    assert row["calories"] in (None, "")


# --- Rollups / recipe-level side effects --------------------------------

def test_affected_recipe_count_and_rollups(fixture_paths):
    report = fix.run(apply=True)
    assert report["affected_recipe_count"] == 6

    recipes = {r["id"]: r for r in csv.DictReader(fixture_paths["recipes_csv"].open(encoding="utf-8", newline=""))}
    assert recipes["r-clear-1"]["total_calories"] == "0.0"
    assert recipes["r-kem"]["total_calories"] == "414.0"
    assert recipes["r-ketchup"]["total_calories"] == "34.5"
    # Unrelated recipes must show no change.
    assert recipes["r-frog"]["total_calories"] == "180.0"
    assert recipes["r-cream"]["total_calories"] == "172.5"
    assert recipes["r-tomato"]["total_calories"] == "12.0"


def test_status_recomputed_for_cleared_recipes_only(fixture_paths):
    fix.run(apply=True)
    recipes_json = {r["id"]: r for r in json.loads(fixture_paths["recipes_json"].read_text(encoding="utf-8"))}
    for rid in ("r-clear-1", "r-clear-2", "r-clear-3", "r-clear-4"):
        assert recipes_json[rid]["nutrition_status"] == "INCOMPLETE"
        assert recipes_json[rid]["missing_nutrition_count"] == 1
    # Remapped recipes keep non-null nutrition -> status unaffected.
    assert recipes_json["r-kem"]["nutrition_status"] == "COMPLETE"
    assert recipes_json["r-ketchup"]["nutrition_status"] == "COMPLETE"
    # Untouched recipes unaffected.
    assert recipes_json["r-frog"]["nutrition_status"] == "COMPLETE"
    assert recipes_json["r-cream"]["nutrition_status"] == "COMPLETE"
    assert recipes_json["r-tomato"]["nutrition_status"] == "COMPLETE"
    assert recipes_json["r-um"]["nutrition_status"] == "INCOMPLETE"


# --- Dry-run / idempotence / drift ---------------------------------------

def test_preview_does_not_write_any_file(fixture_paths):
    before_alias = fixture_paths["alias_path"].read_bytes()
    before_ing = fixture_paths["ing_csv"].read_bytes()
    report = fix.run(apply=False)
    assert report["status"] == "preview"
    assert report["clear_applied_now"] == 4
    assert report["remap_applied_now"] == 2
    assert fixture_paths["alias_path"].read_bytes() == before_alias
    assert fixture_paths["ing_csv"].read_bytes() == before_ing


def test_run_preview_is_deterministic(fixture_paths):
    report1 = fix.run(apply=False)
    report2 = fix.run(apply=False)
    assert report1 == report2


def test_idempotent_second_apply_is_a_no_op(fixture_paths):
    fix.run(apply=True)
    after_first_ing = fixture_paths["ing_csv"].read_bytes()
    after_first_alias = fixture_paths["alias_path"].read_bytes()
    after_first_recipes = fixture_paths["recipes_csv"].read_bytes()

    report2 = fix.run(apply=True)
    assert report2["status"] == "applied"
    assert report2["clear_applied_now"] == 0
    assert report2["clear_already_applied"] == 4
    assert report2["remap_applied_now"] == 0
    assert report2["remap_already_applied"] == 2
    assert report2["alias_states"] == {
        THIT_DUI_ALIAS_KEY: "already_applied",
        KEM_ALIAS_KEY: "already_applied",
        fix.ALIAS_CHANGE_KEY: "already_applied",
    }

    assert fixture_paths["ing_csv"].read_bytes() == after_first_ing
    assert fixture_paths["alias_path"].read_bytes() == after_first_alias
    assert fixture_paths["recipes_csv"].read_bytes() == after_first_recipes


def test_raw_text_drift_on_clear_row_aborts_before_writing(fixture_paths):
    rows = list(csv.DictReader(fixture_paths["ing_csv"].open(encoding="utf-8", newline="")))
    for r in rows:
        if r["id"] == CLEAR_ID_1:
            r["raw_text"] = "some other ingredient entirely"
    _write_csv(fixture_paths["ing_csv"], rows, ING_FIELDS)
    before_ing = fixture_paths["ing_csv"].read_bytes()
    before_alias = fixture_paths["alias_path"].read_bytes()

    with pytest.raises(fix.DriftError):
        fix.run(apply=True)

    assert fixture_paths["ing_csv"].read_bytes() == before_ing
    assert fixture_paths["alias_path"].read_bytes() == before_alias


def test_unexpected_alias_value_aborts_before_writing(fixture_paths):
    alias_map = _alias_map(fixture_paths)
    alias_map[fix.ALIAS_CHANGE_KEY] = "9999"
    fixture_paths["alias_path"].write_text(json.dumps(alias_map, ensure_ascii=False), encoding="utf-8")
    before_ing = fixture_paths["ing_csv"].read_bytes()

    with pytest.raises(fix.DriftError):
        fix.run(apply=True)

    assert fixture_paths["ing_csv"].read_bytes() == before_ing


def test_remap_requires_exact_catalog_identity_match(tmp_path, monkeypatch, fixture_paths):
    """If the catalog's name_vi for 20070 drifts away from the expected
    name, the remap must refuse to run rather than publish a mismatched
    identity."""
    master_csv = tmp_path / "drifted_master.csv"
    _write_csv(master_csv, [
        {"code": "20070", "name_vi": "Something Else", "energy_kcal": "345", "protein_g": "2.1", "fat_g": "37.0", "carbs_g": "2.8"},
        {"code": fix.KETCHUP_REMAP_NEW_CODE, "name_vi": fix.KETCHUP_REMAP_NEW_NAME, "energy_kcal": "115", "protein_g": "1.1", "fat_g": "0.1", "carbs_g": "27.4"},
    ], ["code", "name_vi", "energy_kcal", "protein_g", "fat_g", "carbs_g"])
    monkeypatch.setattr(fix, "MASTER", master_csv)

    with pytest.raises(fix.DriftError):
        fix.run(apply=False)
