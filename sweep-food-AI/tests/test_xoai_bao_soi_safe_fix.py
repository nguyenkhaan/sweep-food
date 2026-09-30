"""Tests for scripts/eda/apply_xoai_bao_soi_safe_fix.py.

Fixture tests never touch the real ~64k-row processed dataset: all module-level
path constants are monkeypatched to a tmp_path fixture. ALIAS_PATH is patched
in BOTH this fix module and scripts.eda.apply_thit_dui_kem_tomato_safe_fix,
because the read_alias_map/write_alias_map helpers this fix reuses resolve
ALIAS_PATH from their own defining module's globals.

A small number of read-only invariant tests at the bottom DO run against the
real dataset and the real matcher, because the properties they protect are
facts about the real remediation scope and about why this fix is shaped the
way it is -- above all that removing the "xoài bào sợi" alias does NOT on its
own fix the row, which is the whole reason the row-level CLEAR exists.
"""

import csv
import json

import pytest

import scripts.eda.apply_thit_dui_kem_tomato_safe_fix as tomato
import scripts.eda.apply_xoai_bao_soi_safe_fix as fix

TARGET_ID = fix.CLEAR_ROW_ID
TARGET_RAW = fix.CLEAR_RAW_TEXT
NUTRITION = ("calories", "protein_g", "fat_g", "carbs_g")

# The five mango aliases this fix must leave exactly as it found them.
BARE_XOAI_ALIAS = "xoài"
PRESERVED_ALIASES = ("xoài", "xoài chín", "xoài chín giòn", "trang trí xoài chín", "xoài đông lạnh")

ING_FIELDS = [
    "id", "recipe_id", "master_ingredient_code", "master_ingredient_name",
    "raw_text", "cleaned_name", "required_quantity", "unit_vi", "unit",
    "preparation_note", "match_confidence", "match_method", "estimated_weight_g",
    "calories", "protein_g", "fat_g", "carbs_g",
]

# Every mango row in the fixture that is deliberately out of scope, paired with
# the identity it must still carry after the fix runs. Covers all five
# preserved aliases, an already-cleared green row, and the dangling-5074 rows.
UNRELATED_MANGO_ROWS = {
    "bare-xoai-row": ("5055", "Xoài chín", "PRESET_ALIAS_MATCH"),
    "xoai-chin-row": ("5055", "Xoài chín", "EXACT_CATALOG_MATCH"),
    "xoai-chin-gion-row": ("5055", "Xoài chín", "PRESET_ALIAS_MATCH"),
    "trang-tri-row": ("5055", "Xoài chín", "PRESET_ALIAS_MATCH"),
    "dong-lanh-row": ("5055", "Xoài chín", "PRESET_ALIAS_MATCH"),
    "green-unmatched-row": ("", "", "UNMATCHED"),
    "dangling-row-1": ("5074", "Xoài", "QWEN_LLM_MATCH"),
    "dangling-row-2": ("5074", "Xoài", "QWEN_LLM_MATCH"),
}

ALIAS_MAP = {
    # The two removal targets.
    "xoài bào sợi": "5055",
    "xoài chín tươi": "5055",
    # The five preserved mango aliases.
    "xoài": "5055",
    "xoài chín": "5055",
    "xoài chín giòn": "5055",
    "trang trí xoài chín": "5055",
    "xoài đông lạnh": "5055",
    # Unrelated neighbours that must survive byte-identical.
    "xà lách xoong": "4093",
    "cải xoăn": "4016",
    "măng cụt": "5061",
}


def _write_csv(path, rows, fieldnames):
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def _row(**kwargs):
    base = {f: "" for f in ING_FIELDS}
    base.update(kwargs)
    return base


def _read_ing(path):
    with path.open(encoding="utf-8-sig", newline="") as f:
        return {r["id"]: r for r in csv.DictReader(f)}


def _alias_map(paths):
    return json.loads(paths["alias_path"].read_text(encoding="utf-8"))


def _recipes_json(paths):
    return {r["id"]: r for r in json.loads(paths["recipes_json"].read_text(encoding="utf-8"))}


def _mango(row_id, recipe_id, code, name, raw, method, conf, cals):
    """One matched mango row carrying real 5055-derived nutrition."""
    return _row(
        id=row_id, recipe_id=recipe_id, master_ingredient_code=code,
        master_ingredient_name=name, raw_text=raw, cleaned_name=raw.lower(),
        unit_vi="phần ăn", unit="OTHER", match_confidence=conf, match_method=method,
        estimated_weight_g="50.0", calories=cals, protein_g="0.3", fat_g="0.1", carbs_g="8.0",
    )


@pytest.fixture
def fixture_paths(tmp_path, monkeypatch):
    alias_path = tmp_path / "ingredient_alias_map.json"
    ing_csv = tmp_path / "recipe_ingredients.csv"
    ing_json = tmp_path / "recipe_ingredients.json"
    recipes_csv = tmp_path / "recipes.csv"
    recipes_json = tmp_path / "recipes.json"
    out_dir = tmp_path / "reports"

    alias_path.write_text(
        json.dumps(ALIAS_MAP, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    ing_rows = [
        # THE target row, in its exact real pre-fix state.
        _row(id=TARGET_ID, recipe_id="r-target", master_ingredient_code="5055",
             master_ingredient_name="Xoài chín", raw_text=TARGET_RAW,
             cleaned_name="xoài bào sợi", unit_vi="phần ăn", unit="OTHER",
             match_confidence="0.98", match_method="PRESET_ALIAS_MATCH",
             estimated_weight_g="10.0", calories="6.9", protein_g="0.1",
             fat_g="0.0", carbs_g="1.6"),
        # Out-of-scope rows for each of the five preserved aliases.
        _mango("bare-xoai-row", "r-target", "5055", "Xoài chín", "Xoài: 1 trái",
               "PRESET_ALIAS_MATCH", "0.98", "34.5"),
        _mango("xoai-chin-row", "r-other", "5055", "Xoài chín", "Xoài chín 1 quả",
               "EXACT_CATALOG_MATCH", "1.0", "34.5"),
        _mango("xoai-chin-gion-row", "r-other", "5055", "Xoài chín", "Xoài chín giòn 1/2 trái",
               "PRESET_ALIAS_MATCH", "0.98", "34.5"),
        _mango("trang-tri-row", "r-other", "5055", "Xoài chín", "Trang trí: xoài chín",
               "PRESET_ALIAS_MATCH", "0.98", "34.5"),
        _mango("dong-lanh-row", "r-other", "5055", "Xoài chín", "Xoài đông lạnh 340 gr",
               "PRESET_ALIAS_MATCH", "0.98", "34.5"),
        # An already-cleared green row: the precedent this fix follows.
        _row(id="green-unmatched-row", recipe_id="r-target", raw_text="xoài xanh",
             cleaned_name="xoài", unit_vi="phần ăn", unit="OTHER", match_method="UNMATCHED",
             estimated_weight_g="10.0"),
        # Out-of-scope dangling-5074 Qwen rows.
        _mango("dangling-row-1", "r-target", "5074", "Xoài", "1 trái xoài cát",
               "QWEN_LLM_MATCH", "0.3277", "34.5"),
        _mango("dangling-row-2", "r-other", "5074", "Xoài", "Xoài cát Hòa lộc: 1 trái",
               "QWEN_LLM_MATCH", "0.3071", "34.5"),
        # Filler so the target recipe holds 8 rows and, like the real "Bún bì
        # căn", stays PARTIAL across the fix instead of crossing a threshold.
        *[_row(id=f"filler-{i}", recipe_id="r-target", master_ingredient_code="4005",
               master_ingredient_name="Cà chua", raw_text=f"nguyên liệu {i}",
               cleaned_name=f"nguyên liệu {i}", match_confidence="0.98",
               match_method="PRESET_ALIAS_MATCH", estimated_weight_g="100.0",
               calories="20.0", protein_g="1.0", fat_g="0.5", carbs_g="4.0")
          for i in range(4)],
    ]
    _write_csv(ing_csv, ing_rows, ING_FIELDS)
    ing_json.write_text(json.dumps(ing_rows, ensure_ascii=False), encoding="utf-8")

    recipe_fields = ["id", "total_calories", "total_protein_g", "total_fat_g",
                     "total_carbs_g", "ingredients_count"]
    # r-target: 6.9 + 34.5 + 34.5 + 4*20.0 = 155.9 over 8 rows, 1 already missing.
    # Carbs: 1.6 + 8.0 + 8.0 + 4*4.0 = 33.6.
    recipes = [
        {"id": "r-target", "total_calories": "155.9", "total_protein_g": "4.7",
         "total_fat_g": "2.2", "total_carbs_g": "33.6", "ingredients_count": "8"},
        {"id": "r-other", "total_calories": "172.5", "total_protein_g": "1.5",
         "total_fat_g": "0.5", "total_carbs_g": "40.0", "ingredients_count": "5"},
    ]
    _write_csv(recipes_csv, recipes, recipe_fields)
    recipes_json.write_text(json.dumps([
        dict(recipes[0], nutrition_status="PARTIAL", missing_nutrition_count=1),
        dict(recipes[1], nutrition_status="COMPLETE", missing_nutrition_count=0),
    ], ensure_ascii=False), encoding="utf-8")

    monkeypatch.setattr(fix, "ALIAS_PATH", alias_path)
    # read_alias_map/write_alias_map resolve ALIAS_PATH from the module that
    # defines them, so the reused helpers need their own module patched too.
    monkeypatch.setattr(tomato, "ALIAS_PATH", alias_path)
    monkeypatch.setattr(fix, "ING", ing_csv)
    monkeypatch.setattr(fix, "ING_JSON", ing_json)
    monkeypatch.setattr(fix, "RECIPES_CSV", recipes_csv)
    monkeypatch.setattr(fix, "RECIPES_JSON", recipes_json)
    monkeypatch.setattr(fix, "OUT", out_dir)
    # This fixture's world holds 2 dangling-5074 rows, not the real dataset's 7.
    monkeypatch.setattr(fix, "EXPECTED_DANGLING_COUNT", 2)

    return {"alias_path": alias_path, "ing_csv": ing_csv, "ing_json": ing_json,
            "recipes_csv": recipes_csv, "recipes_json": recipes_json, "out": out_dir}


# --------------------------------------------------------------------------
# Preview
# --------------------------------------------------------------------------

def test_preview_writes_nothing(fixture_paths):
    before = {k: p.read_bytes() for k, p in fixture_paths.items() if k != "out"}
    report = fix.run(apply=False)
    assert report["status"] == "preview"
    assert report["clear_applied_now"] == 1
    assert sorted(report["aliases_removed"]) == ["xoài bào sợi", "xoài chín tươi"]
    for k, p in fixture_paths.items():
        if k != "out":
            assert p.read_bytes() == before[k]
    assert not fixture_paths["out"].exists()


# --------------------------------------------------------------------------
# Row-level CLEAR
# --------------------------------------------------------------------------

def test_target_row_is_cleared_to_unmatched(fixture_paths):
    report = fix.run(apply=True)
    assert report["clear_applied_now"] == 1

    row = _read_ing(fixture_paths["ing_csv"])[TARGET_ID]
    assert row["master_ingredient_code"] in (None, "")
    assert row["master_ingredient_name"] in (None, "")
    assert row["match_method"] == "UNMATCHED"
    assert row["match_confidence"] in (None, "")


def test_cleared_row_nutrition_is_null_not_zero(fixture_paths):
    """Null means "unknown". A measured 0.0 would make the row look like a
    real zero-calorie ingredient and silently understate the recipe."""
    fix.run(apply=True)
    row = _read_ing(fixture_paths["ing_csv"])[TARGET_ID]
    for field in NUTRITION:
        assert row[field] in (None, ""), f"{field} must be null"
        assert row[field] not in ("0", "0.0"), f"{field} must be null, not a measured zero"


def test_cleared_row_is_null_in_json_not_empty_string(fixture_paths):
    """JSON carries real nulls, matching every previously cleared row."""
    fix.run(apply=True)
    rows = {r["id"]: r for r in json.loads(fixture_paths["ing_json"].read_text(encoding="utf-8"))}
    row = rows[TARGET_ID]
    assert row["master_ingredient_code"] is None
    assert row["master_ingredient_name"] is None
    assert row["match_confidence"] is None
    for field in NUTRITION:
        assert row[field] is None, f"{field} must be JSON null"


def test_clear_preserves_weight_and_source_text(fixture_paths):
    """The CLEAR removes an identity claim, not the row's evidence."""
    fix.run(apply=True)
    row = _read_ing(fixture_paths["ing_csv"])[TARGET_ID]
    assert row["estimated_weight_g"] == "10.0"
    assert row["raw_text"] == TARGET_RAW
    assert row["cleaned_name"] == "xoài bào sợi"
    assert row["unit_vi"] == "phần ăn"
    assert row["recipe_id"] == "r-target"


def test_target_row_is_not_remapped_to_any_code(fixture_paths):
    """The catalog has no green/unripe mango identity, so there is nothing to
    remap to -- least of all ripe 5055, which is what made this row wrong."""
    fix.run(apply=True)
    row = _read_ing(fixture_paths["ing_csv"])[TARGET_ID]
    assert row["master_ingredient_code"] != "5055"
    assert row["master_ingredient_code"] in (None, "")


# --------------------------------------------------------------------------
# Alias-map edits
# --------------------------------------------------------------------------

@pytest.mark.parametrize("alias", ["xoài bào sợi", "xoài chín tươi"])
def test_both_target_aliases_are_removed(fixture_paths, alias):
    fix.run(apply=True)
    assert alias not in _alias_map(fixture_paths)


@pytest.mark.parametrize("alias", PRESERVED_ALIASES)
def test_preserved_mango_aliases_survive(fixture_paths, alias):
    fix.run(apply=True)
    assert _alias_map(fixture_paths)[alias] == "5055"


def test_bare_xoai_alias_is_preserved(fixture_paths):
    """The bare alias is the root enabler and is deliberately left in place:
    removing it would strand 5 plausibly-ripe rows, which is out of scope."""
    fix.run(apply=True)
    assert _alias_map(fixture_paths)[BARE_XOAI_ALIAS] == "5055"


def test_alias_map_only_the_two_target_keys_change(fixture_paths):
    before = _alias_map(fixture_paths)
    fix.run(apply=True)
    after = _alias_map(fixture_paths)
    assert set(before) - set(after) == {"xoài bào sợi", "xoài chín tươi"}
    assert set(after) - set(before) == set()
    for key, value in after.items():
        assert before[key] == value, f"unrelated alias {key!r} changed value"


# --------------------------------------------------------------------------
# Unrelated rows
# --------------------------------------------------------------------------

@pytest.mark.parametrize("row_id,expected", sorted(UNRELATED_MANGO_ROWS.items()))
def test_unrelated_mango_rows_keep_their_identity(fixture_paths, row_id, expected):
    fix.run(apply=True)
    row = _read_ing(fixture_paths["ing_csv"])[row_id]
    code, name, method = expected
    assert (row["master_ingredient_code"] or "") == code
    assert (row["master_ingredient_name"] or "") == name
    assert row["match_method"] == method


def test_unrelated_rows_are_byte_identical(fixture_paths):
    before = _read_ing(fixture_paths["ing_csv"])
    fix.run(apply=True)
    after = _read_ing(fixture_paths["ing_csv"])
    assert set(before) == set(after)
    for row_id in before:
        if row_id == TARGET_ID:
            continue
        assert before[row_id] == after[row_id], f"row {row_id} must not change"


def test_dangling_5074_rows_are_untouched(fixture_paths):
    """The remaining Qwen dangling-code rows stay open for their own review."""
    fix.run(apply=True)
    rows = _read_ing(fixture_paths["ing_csv"])
    dangling = [r for r in rows.values() if r["master_ingredient_code"] == "5074"]
    assert len(dangling) == 2


# --------------------------------------------------------------------------
# Rollups and status
# --------------------------------------------------------------------------

def test_affected_recipe_rollup_drops_by_exactly_the_cleared_row(fixture_paths):
    fix.run(apply=True)
    with fixture_paths["recipes_csv"].open(encoding="utf-8-sig", newline="") as f:
        recipes = {r["id"]: r for r in csv.DictReader(f)}
    target = recipes["r-target"]
    assert target["total_calories"] == "149.0"   # 155.9 - 6.9
    assert target["total_protein_g"] == "4.6"    # 4.7 - 0.1
    assert target["total_fat_g"] == "2.2"        # unchanged, row contributed 0.0
    assert target["total_carbs_g"] == "32.0"     # 33.6 - 1.6


def test_unaffected_recipe_rollup_is_unchanged(fixture_paths):
    fix.run(apply=True)
    with fixture_paths["recipes_csv"].open(encoding="utf-8-sig", newline="") as f:
        recipes = {r["id"]: r for r in csv.DictReader(f)}
    other = recipes["r-other"]
    assert other["total_calories"] == "172.5"
    assert other["total_protein_g"] == "1.5"


def test_missing_nutrition_count_increments_by_one(fixture_paths):
    report = fix.run(apply=True)
    assert report["recipes_with_changed_missing_count"] == 1
    recipes = _recipes_json(fixture_paths)
    assert recipes["r-target"]["missing_nutrition_count"] == 2  # was 1
    assert recipes["r-other"]["missing_nutrition_count"] == 0


def test_status_label_does_not_cross_threshold(fixture_paths):
    """2 missing of 8 is 25%, under the 30% INCOMPLETE threshold -- the same
    place the real "Bún bì căn" lands (4 of 16)."""
    report = fix.run(apply=True)
    assert report["recipes_with_status_label_changed"] == 0
    assert _recipes_json(fixture_paths)["r-target"]["nutrition_status"] == "PARTIAL"


def test_report_names_the_single_affected_recipe(fixture_paths):
    report = fix.run(apply=True)
    assert report["affected_recipe_count"] == 1
    assert report["affected_recipe_id"] == "r-target"
    assert report["recipes_with_changed_totals"] == 1
    assert (fixture_paths["out"] / "applied_xoai_bao_soi_fix.json").exists()


# --------------------------------------------------------------------------
# Idempotence
# --------------------------------------------------------------------------

def test_second_apply_is_a_no_op(fixture_paths):
    fix.run(apply=True)
    after_first = {k: p.read_bytes() for k, p in fixture_paths.items() if k != "out"}

    report = fix.run(apply=True)
    assert report["clear_applied_now"] == 0
    assert report["clear_already_applied"] == 1
    assert report["aliases_removed"] == []
    assert all(s == "already_applied" for s in report["alias_states"].values())

    for k, p in fixture_paths.items():
        if k != "out":
            assert p.read_bytes() == after_first[k], f"{k} changed on idempotent rerun"


def test_preview_after_apply_still_succeeds(fixture_paths):
    fix.run(apply=True)
    report = fix.run(apply=False)
    assert report["status"] == "preview"
    assert report["clear_already_applied"] == 1


# --------------------------------------------------------------------------
# Drift guards -- every one must abort before writing anything
# --------------------------------------------------------------------------

def _assert_nothing_written(paths, before):
    for k, p in paths.items():
        if k != "out":
            assert p.read_bytes() == before[k], f"{k} was written despite a drift abort"


def test_raw_text_drift_aborts(fixture_paths):
    rows = list(csv.DictReader(
        fixture_paths["ing_csv"].open(encoding="utf-8-sig", newline="")))
    for r in rows:
        if r["id"] == TARGET_ID:
            r["raw_text"] = "xoài bào sợi (đã sửa)"
    _write_csv(fixture_paths["ing_csv"], rows, ING_FIELDS)
    before = {k: p.read_bytes() for k, p in fixture_paths.items() if k != "out"}

    with pytest.raises(fix.DriftError, match="raw_text drifted"):
        fix.run(apply=True)
    _assert_nothing_written(fixture_paths, before)


def test_row_code_drift_aborts(fixture_paths):
    """A row that is neither pending nor already-cleared must not be touched."""
    rows = list(csv.DictReader(
        fixture_paths["ing_csv"].open(encoding="utf-8-sig", newline="")))
    for r in rows:
        if r["id"] == TARGET_ID:
            r["master_ingredient_code"] = "9999"
            r["master_ingredient_name"] = "Something Else"
    _write_csv(fixture_paths["ing_csv"], rows, ING_FIELDS)
    before = {k: p.read_bytes() for k, p in fixture_paths.items() if k != "out"}

    with pytest.raises(fix.DriftError):
        fix.run(apply=True)
    _assert_nothing_written(fixture_paths, before)


def test_missing_target_row_aborts(fixture_paths):
    rows = [r for r in csv.DictReader(
        fixture_paths["ing_csv"].open(encoding="utf-8-sig", newline="")) if r["id"] != TARGET_ID]
    _write_csv(fixture_paths["ing_csv"], rows, ING_FIELDS)
    before = {k: p.read_bytes() for k, p in fixture_paths.items() if k != "out"}

    with pytest.raises(fix.DriftError, match="not found"):
        fix.run(apply=True)
    _assert_nothing_written(fixture_paths, before)


@pytest.mark.parametrize("alias", ["xoài bào sợi", "xoài chín tươi"])
def test_alias_value_drift_aborts(fixture_paths, alias):
    """A removal target pointing somewhere unexpected is no longer the alias
    that was reviewed -- refuse rather than delete a different mapping."""
    alias_map = _alias_map(fixture_paths)
    alias_map[alias] = "9999"
    fixture_paths["alias_path"].write_text(
        json.dumps(alias_map, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    before = {k: p.read_bytes() for k, p in fixture_paths.items() if k != "out"}

    with pytest.raises(fix.DriftError, match="unexpected value"):
        fix.run(apply=True)
    _assert_nothing_written(fixture_paths, before)


@pytest.mark.parametrize("alias", PRESERVED_ALIASES)
def test_preserved_alias_value_drift_aborts(fixture_paths, alias):
    alias_map = _alias_map(fixture_paths)
    alias_map[alias] = "9999"
    fixture_paths["alias_path"].write_text(
        json.dumps(alias_map, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    before = {k: p.read_bytes() for k, p in fixture_paths.items() if k != "out"}

    with pytest.raises(fix.DriftError, match="now maps to"):
        fix.run(apply=True)
    _assert_nothing_written(fixture_paths, before)


@pytest.mark.parametrize("alias", PRESERVED_ALIASES)
def test_preserved_alias_removal_aborts(fixture_paths, alias):
    """If someone else deletes one of the five -- the bare "xoài" alias above
    all -- this fix must fail closed, not quietly run against a changed map."""
    alias_map = _alias_map(fixture_paths)
    del alias_map[alias]
    fixture_paths["alias_path"].write_text(
        json.dumps(alias_map, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    before = {k: p.read_bytes() for k, p in fixture_paths.items() if k != "out"}

    with pytest.raises(fix.DriftError, match="is missing"):
        fix.run(apply=True)
    _assert_nothing_written(fixture_paths, before)


def test_dangling_row_count_drift_aborts(fixture_paths, monkeypatch):
    """The out-of-scope Qwen population is an invariant: if it has moved, this
    remediation is no longer running against the dataset it was reviewed on."""
    monkeypatch.setattr(fix, "EXPECTED_DANGLING_COUNT", 5)
    before = {k: p.read_bytes() for k, p in fixture_paths.items() if k != "out"}

    with pytest.raises(fix.DriftError, match="dangling code"):
        fix.run(apply=True)
    _assert_nothing_written(fixture_paths, before)


# --------------------------------------------------------------------------
# Read-only invariants against the REAL dataset and the REAL matcher
# --------------------------------------------------------------------------

def _real_alias_map():
    return json.loads(tomato.ALIAS_PATH.read_text(encoding="utf-8"))


def test_real_removing_the_alias_alone_would_not_fix_the_row():
    """The core finding, in executable form.

    clean_culinary_query() strips "bào sợi", so the raw text reduces to the
    bare "xoài" alias and would still resolve to ripe 5055 at the same stage
    and confidence even with "xoài bào sợi" deleted. That is precisely why
    this fix also CLEARs the row by id -- if this assertion ever flips, the
    row-level CLEAR is no longer load-bearing and this fix should be revisited.
    """
    from nlp.entity_matcher import clean_culinary_query

    assert clean_culinary_query(TARGET_RAW) == BARE_XOAI_ALIAS
    assert _real_alias_map().get(BARE_XOAI_ALIAS) == "5055"


def test_real_removed_aliases_are_provable_no_ops():
    """Neither removal changes any matching outcome: one reduces to the bare
    alias, the other to the catalog's own name (a CLEANED_NAME_MATCH)."""
    from nlp.entity_matcher import clean_culinary_query

    assert clean_culinary_query("xoài bào sợi") == "xoài"
    assert clean_culinary_query("xoài chín tươi") == "xoài chín"


def test_real_preserved_aliases_still_point_at_ripe_mango():
    alias_map = _real_alias_map()
    for alias in PRESERVED_ALIASES:
        assert alias_map.get(alias) == "5055", f"preserved alias {alias!r} drifted"


def test_real_catalog_has_no_green_mango_identity():
    """The reason this row CLEARs instead of remapping. 5033 "Muỗm, quéo" is
    Mangifera foetida, a different species, and is not a substitute."""
    with tomato.MASTER.open(encoding="utf-8-sig", newline="") as f:
        mango = [r for r in csv.DictReader(f) if "xoài" in r["name_vi"].lower()]
    assert [r["code"] for r in mango] == ["5055"]
    assert mango[0]["name_vi"] == "Xoài chín"


def test_real_target_row_is_the_reviewed_row():
    with fix.ING.open(encoding="utf-8-sig", newline="") as f:
        rows = {r["id"]: r for r in csv.DictReader(f)}
    assert TARGET_ID in rows
    row = rows[TARGET_ID]
    assert row["raw_text"] == TARGET_RAW
    # Pending before the fix is applied, cleared after -- both are valid.
    assert row["match_method"] in ("PRESET_ALIAS_MATCH", "UNMATCHED")


def test_real_other_bare_xoai_rows_stay_out_of_scope():
    """Five other rows resolve through the bare alias and are NOT touched here;
    they need their own review."""
    with fix.ING.open(encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))
    others = [
        r for r in rows
        if r["cleaned_name"] == "xoài"
        and r["match_method"] == "PRESET_ALIAS_MATCH"
        and r["id"] != TARGET_ID
    ]
    assert len(others) == 6
    assert all(r["master_ingredient_code"] == "5055" for r in others)


def test_real_dangling_5074_population_is_unchanged():
    with fix.ING.open(encoding="utf-8-sig", newline="") as f:
        dangling = [r for r in csv.DictReader(f)
                    if (r["master_ingredient_code"] or "").strip() == "5074"]
    assert len(dangling) == fix.EXPECTED_DANGLING_COUNT == 7


def test_real_explicit_green_mango_rows_are_all_unmatched():
    """The precedent this fix follows, asserted against the live dataset."""
    tokens = ("xanh", "sống", "non", "keo", "thái", "tứ quý")
    with fix.ING.open(encoding="utf-8-sig", newline="") as f:
        green = [r for r in csv.DictReader(f)
                 if "xoài" in r["raw_text"].lower()
                 and any(t in r["raw_text"].lower() for t in tokens)]
    assert len(green) == 31
    assert all(r["match_method"] == "UNMATCHED" for r in green)
    assert all((r["master_ingredient_code"] or "") == "" for r in green)
