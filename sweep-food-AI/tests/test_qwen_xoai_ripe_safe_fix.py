"""Tests for scripts/eda/apply_qwen_xoai_ripe_safe_fix.py.

Fixture tests never touch the real ~64k-row processed dataset: all module-level
path constants are monkeypatched to a tmp_path fixture, including inside
scripts.eda.audit_qwen_matching (whose audit() is called internally to
cross-check the live Class-D count before anything is written).

A small number of read-only invariant tests at the bottom DO run against the
real dataset, because the properties they protect -- "exactly 39 Class-D rows
stay unresolved", "the duplicate-blocked row is out of scope", "no Bạc hà row
is in scope" -- are facts about the real remediation scope that a fixture
cannot express.
"""

import csv
import json

import pytest

import scripts.eda.apply_qwen_xoai_ripe_safe_fix as fix
import scripts.eda.audit_qwen_matching as audit_mod

REMAP_ID_1, REMAP_RAW_1 = fix.REMAP_ROWS[0]
REMAP_ID_2, REMAP_RAW_2 = fix.REMAP_ROWS[1]
CLEAR_ID_1, CLEAR_RAW_1 = fix.CLEAR_ROWS[0]
CLEAR_ID_2, CLEAR_RAW_2 = fix.CLEAR_ROWS[1]

# The duplicate-blocked Xoài row: raw text does state ripeness ("xoài cát
# chín"), but its recipe already carries a separate 5055 row, so remapping it
# would double-count the same mango. It must stay out of scope.
DUP_BLOCKED_ID = "71e4d150-044c-4f4b-9859-b99a9d40ab4a"
NUTRITION = ("calories", "protein_g", "fat_g", "carbs_g")

ING_FIELDS = [
    "id", "recipe_id", "master_ingredient_code", "master_ingredient_name",
    "raw_text", "cleaned_name", "required_quantity", "match_confidence",
    "match_method", "estimated_weight_g", "calories", "protein_g", "fat_g", "carbs_g",
]


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


MASTER_FIELDS = ["code", "name_vi", "energy_kcal", "protein_g", "fat_g", "carbs_g"]
# Real catalog values for 5055, so the expected nutrition below is the real
# arithmetic this fix will perform on the live dataset.
MASTER_ROWS = [
    {"code": "5055", "name_vi": "Xoài chín", "energy_kcal": "69",
     "protein_g": "0.6", "fat_g": "0.3", "carbs_g": "15.9"},
    {"code": "4026", "name_vi": "Dọc mùng", "energy_kcal": "13",
     "protein_g": "0.4", "fat_g": "", "carbs_g": "2.8"},
    {"code": "4007", "name_vi": "Cà rốt", "energy_kcal": "41",
     "protein_g": "0.9", "fat_g": "0.2", "carbs_g": "9.6"},
]


@pytest.fixture
def fixture_paths(tmp_path, monkeypatch):
    master_csv = tmp_path / "master.csv"
    ing_csv = tmp_path / "recipe_ingredients.csv"
    ing_json = tmp_path / "recipe_ingredients.json"
    recipes_csv = tmp_path / "recipes.csv"
    recipes_json = tmp_path / "recipes.json"
    out_dir = tmp_path / "reports"

    _write_csv(master_csv, MASTER_ROWS, MASTER_FIELDS)

    ing_rows = [
        # Approved REMAP rows: dangling 5074, explicit "vừa chín tới" ripeness.
        _row(id=REMAP_ID_1, recipe_id="r-remap1", master_ingredient_code="5074",
             master_ingredient_name="Xoài", raw_text=REMAP_RAW_1, cleaned_name="xoài cát",
             match_confidence="0.5406", match_method="QWEN_LLM_MATCH",
             estimated_weight_g="600.0", calories="0", protein_g="0.0", fat_g="0.0", carbs_g="0.0"),
        _row(id=REMAP_ID_2, recipe_id="r-remap2", master_ingredient_code="5074",
             master_ingredient_name="Xoài", raw_text=REMAP_RAW_2, cleaned_name="xoài cát",
             match_confidence="0.3277", match_method="QWEN_LLM_MATCH",
             estimated_weight_g="350.0", calories="0", protein_g="0.0", fat_g="0.0", carbs_g="0.0"),
        # Approved CLEAR rows: green-eaten "xoài Thái", no valid catalog identity.
        _row(id=CLEAR_ID_1, recipe_id="r-clear1", master_ingredient_code="5074",
             master_ingredient_name="Xoài", raw_text=CLEAR_RAW_1, cleaned_name="xoài thái",
             match_confidence="0.4225", match_method="QWEN_LLM_MATCH",
             estimated_weight_g="50.0", calories="0", protein_g="0.0", fat_g="0.0", carbs_g="0.0"),
        _row(id=CLEAR_ID_2, recipe_id="r-clear2", master_ingredient_code="5074",
             master_ingredient_name="Xoài", raw_text=CLEAR_RAW_2, cleaned_name="xoài thái",
             match_confidence="0.4225", match_method="QWEN_LLM_MATCH",
             estimated_weight_g="25.0", calories="0", protein_g="0.0", fat_g="0.0", carbs_g="0.0"),
        # Out-of-scope Class-D stand-in 1: a Bạc hà row on dangling 13038. No
        # raw text names dọc mùng, so it must never be remapped by this fix.
        _row(id="bac-ha-row", recipe_id="r-bh", master_ingredient_code="13038",
             master_ingredient_name="Bạc hà tươi", raw_text="Bạc hà 300 gr",
             cleaned_name="bạc hà", match_confidence="0.2875", match_method="QWEN_LLM_MATCH",
             estimated_weight_g="300.0", calories="0", protein_g="0.0", fat_g="0.0", carbs_g="0.0"),
        # Out-of-scope Class-D stand-in 2: the duplicate-blocked ripe-Xoài row.
        _row(id=DUP_BLOCKED_ID, recipe_id="r-dup", master_ingredient_code="5074",
             master_ingredient_name="Xoài", raw_text="ĂN KÈM: xoài cát chín",
             cleaned_name="xoài", match_confidence="0.42", match_method="QWEN_LLM_MATCH",
             estimated_weight_g="150.0", calories="0", protein_g="0.0", fat_g="0.0", carbs_g="0.0"),
        # The sibling 5055 row that makes DUP_BLOCKED_ID a double-count risk.
        _row(id="dup-sibling", recipe_id="r-dup", master_ingredient_code="5055",
             master_ingredient_name="Xoài chín", raw_text="Xoài: 1 trái", cleaned_name="xoài",
             match_confidence="0.95", match_method="PRESET_ALIAS_MATCH",
             estimated_weight_g="50.0", calories="34.5", protein_g="0.3", fat_g="0.1", carbs_g="8.0"),
        # Already-UNMATCHED row: invariants must hold and it must stay untouched.
        _row(id="unmatched-row", recipe_id="r-um", master_ingredient_code="",
             master_ingredient_name="", raw_text="gia vị không rõ", cleaned_name="gia vị",
             match_confidence="", match_method="UNMATCHED",
             estimated_weight_g="10.0", calories="", protein_g="", fat_g="", carbs_g=""),
    ]
    _write_csv(ing_csv, ing_rows, ING_FIELDS)
    ing_json.write_text(json.dumps(ing_rows, ensure_ascii=False), encoding="utf-8")

    recipe_fields = ["id", "total_calories", "total_protein_g", "total_fat_g",
                     "total_carbs_g", "ingredients_count"]
    zero = {"total_calories": "0.0", "total_protein_g": "0.0",
            "total_fat_g": "0.0", "total_carbs_g": "0.0", "ingredients_count": "1"}
    recipes = [
        dict(zero, id="r-remap1"), dict(zero, id="r-remap2"),
        dict(zero, id="r-clear1"), dict(zero, id="r-clear2"),
        dict(zero, id="r-bh"),
        {"id": "r-dup", "total_calories": "34.5", "total_protein_g": "0.3",
         "total_fat_g": "0.1", "total_carbs_g": "8.0", "ingredients_count": "2"},
        dict(zero, id="r-um"),
    ]
    _write_csv(recipes_csv, recipes, recipe_fields)
    # Pre-fix status reflects each recipe's real ingredient truth, so the
    # status recompute only reports a change where this fix changed something.
    initial_status = {
        "r-remap1": ("COMPLETE", 0), "r-remap2": ("COMPLETE", 0),
        "r-clear1": ("COMPLETE", 0), "r-clear2": ("COMPLETE", 0),
        "r-bh": ("COMPLETE", 0), "r-dup": ("COMPLETE", 0),
        "r-um": ("INCOMPLETE", 1),
    }
    recipes_json.write_text(json.dumps([
        dict(r, nutrition_status=initial_status[r["id"]][0],
             missing_nutrition_count=initial_status[r["id"]][1])
        for r in recipes
    ], ensure_ascii=False), encoding="utf-8")

    monkeypatch.setattr(audit_mod, "ING", ing_csv)
    monkeypatch.setattr(audit_mod, "MASTER", master_csv)
    monkeypatch.setattr(fix, "ING", ing_csv)
    monkeypatch.setattr(fix, "ING_JSON", ing_json)
    monkeypatch.setattr(fix, "MASTER", master_csv)
    monkeypatch.setattr(fix, "RECIPES_CSV", recipes_csv)
    monkeypatch.setattr(fix, "RECIPES_JSON", recipes_json)
    monkeypatch.setattr(fix, "OUT", out_dir)
    # This fixture's world has 6 Class-D rows (4 approved targets + 2
    # out-of-scope stand-ins), not the real dataset's 43.
    monkeypatch.setattr(fix, "EXPECTED_CLASS_D_COUNT", 6)

    return {"ing_csv": ing_csv, "ing_json": ing_json,
            "recipes_csv": recipes_csv, "recipes_json": recipes_json, "out": out_dir}


# --------------------------------------------------------------------------
# Preview / REMAP / CLEAR
# --------------------------------------------------------------------------

def test_preview_writes_nothing(fixture_paths):
    before = {k: p.read_bytes() for k, p in fixture_paths.items() if k != "out"}
    report = fix.run(apply=False)
    assert report["status"] == "preview"
    assert report["remap_applied_now"] == 2
    assert report["clear_applied_now"] == 2
    assert report["needs_review_untouched"] == 2  # fixture-scale stand-in for 39
    for k, p in fixture_paths.items():
        if k != "out":
            assert p.read_bytes() == before[k]
    assert not fixture_paths["out"].exists()


@pytest.mark.parametrize("row_id,weight,expected", [
    (REMAP_ID_1, "600.0", {"calories": "414.0", "protein_g": "3.6", "fat_g": "1.8", "carbs_g": "95.4"}),
    (REMAP_ID_2, "350.0", {"calories": "241.5", "protein_g": "2.1", "fat_g": "1.1", "carbs_g": "55.6"}),
])
def test_remap_rows_take_catalog_identity_and_recomputed_nutrition(
    fixture_paths, row_id, weight, expected
):
    report = fix.run(apply=True)
    assert report["remap_applied_now"] == 2

    row = _read_ing(fixture_paths["ing_csv"])[row_id]
    assert row["master_ingredient_code"] == "5055"
    assert row["master_ingredient_name"] == "Xoài chín"
    assert row["match_method"] == "QWEN_LLM_MATCH"
    assert row["match_confidence"] == fix.QWEN_MATCH_CONFIDENCE
    # Weight is reused as-is; this fix invokes no weight fallback policy.
    assert row["estimated_weight_g"] == weight
    for field, value in expected.items():
        assert row[field] == value, f"{field} must be recomputed from the catalog, not left stale"


@pytest.mark.parametrize("row_id", [CLEAR_ID_1, CLEAR_ID_2])
def test_clear_rows_become_unmatched_with_null_not_zero_nutrition(fixture_paths, row_id):
    report = fix.run(apply=True)
    assert report["clear_applied_now"] == 2

    row = _read_ing(fixture_paths["ing_csv"])[row_id]
    assert row["master_ingredient_code"] in (None, "")
    assert row["master_ingredient_name"] in (None, "")
    assert row["match_method"] == "UNMATCHED"
    assert row["match_confidence"] in (None, "")
    for field in NUTRITION:
        assert row[field] in (None, ""), f"{field} must be null"
        assert row[field] not in ("0", "0.0"), f"{field} must be null, not a measured zero"


def test_clear_rows_are_not_remapped_to_ripe_mango(fixture_paths):
    """The two 'xoài Thái' rows are green-eaten; mapping them to ripe 5055
    would be nutritionally wrong. They must clear, never remap."""
    fix.run(apply=True)
    rows = _read_ing(fixture_paths["ing_csv"])
    for row_id in (CLEAR_ID_1, CLEAR_ID_2):
        assert rows[row_id]["master_ingredient_code"] != "5055"


# --------------------------------------------------------------------------
# Drift guards
# --------------------------------------------------------------------------

def test_catalog_identity_drift_aborts(tmp_path, monkeypatch, fixture_paths):
    """If the catalog's name_vi for 5055 drifts, refuse rather than publish a
    stale identity."""
    master_csv = tmp_path / "drifted_master.csv"
    _write_csv(master_csv, [dict(MASTER_ROWS[0], name_vi="Something Else")], MASTER_FIELDS)
    monkeypatch.setattr(audit_mod, "MASTER", master_csv)
    monkeypatch.setattr(fix, "MASTER", master_csv)

    with pytest.raises(fix.DriftError):
        fix.run(apply=False)


def test_missing_catalog_code_aborts(tmp_path, monkeypatch, fixture_paths):
    master_csv = tmp_path / "no5055_master.csv"
    _write_csv(master_csv, [MASTER_ROWS[1]], MASTER_FIELDS)
    monkeypatch.setattr(audit_mod, "MASTER", master_csv)
    monkeypatch.setattr(fix, "MASTER", master_csv)

    with pytest.raises(fix.DriftError):
        fix.run(apply=False)


@pytest.mark.parametrize("row_id", [REMAP_ID_1, CLEAR_ID_1])
def test_raw_text_drift_aborts_before_writing(fixture_paths, row_id):
    """A pinned row whose source text changed is no longer the reviewed row."""
    path = fixture_paths["ing_csv"]
    with path.open(encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))
    for r in rows:
        if r["id"] == row_id:
            r["raw_text"] = "something the reviewer never saw"
    _write_csv(path, rows, ING_FIELDS)
    before = path.read_bytes()

    with pytest.raises(fix.DriftError):
        fix.run(apply=True)
    assert path.read_bytes() == before, "nothing may be written when any target row drifted"


def test_unexpected_class_d_population_aborts(fixture_paths, monkeypatch):
    """If the open Class-D population is not the reviewed size, abort."""
    monkeypatch.setattr(fix, "EXPECTED_CLASS_D_COUNT", 99)
    with pytest.raises(fix.DriftError):
        fix.run(apply=False)


# --------------------------------------------------------------------------
# Idempotence and scope
# --------------------------------------------------------------------------

def test_apply_is_idempotent(fixture_paths):
    fix.run(apply=True)
    after_first = {k: p.read_bytes() for k, p in fixture_paths.items() if k != "out"}

    report = fix.run(apply=True)
    assert report["remap_applied_now"] == 0
    assert report["remap_already_applied"] == 2
    assert report["clear_applied_now"] == 0
    assert report["clear_already_applied"] == 2
    for k, p in fixture_paths.items():
        if k != "out":
            assert p.read_bytes() == after_first[k], f"{k} changed on a second apply"


def test_out_of_scope_rows_are_byte_identical(fixture_paths):
    """Every non-target row -- the Bạc hà row, the duplicate-blocked row, its
    5055 sibling, and the pre-existing UNMATCHED row -- passes through."""
    before = {r["id"]: r for r in json.loads(fixture_paths["ing_json"].read_text(encoding="utf-8"))}
    fix.run(apply=True)
    after = {r["id"]: r for r in json.loads(fixture_paths["ing_json"].read_text(encoding="utf-8"))}

    for row_id in ("bac-ha-row", DUP_BLOCKED_ID, "dup-sibling", "unmatched-row"):
        assert after[row_id] == before[row_id], f"{row_id} must not be touched"


def test_bac_ha_row_is_never_remapped(fixture_paths):
    """No bạc hà -> dọc mùng generalization: the row keeps its dangling code."""
    fix.run(apply=True)
    row = _read_ing(fixture_paths["ing_csv"])["bac-ha-row"]
    assert row["master_ingredient_code"] == "13038"
    assert row["master_ingredient_name"] == "Bạc hà tươi"
    assert row["match_method"] == "QWEN_LLM_MATCH"


def test_duplicate_blocked_row_stays_unresolved(fixture_paths):
    """71e4d150 states ripeness but its recipe already carries a 5055 row;
    remapping it would double-count. It must stay on the dangling code."""
    fix.run(apply=True)
    rows = _read_ing(fixture_paths["ing_csv"])
    assert rows[DUP_BLOCKED_ID]["master_ingredient_code"] == "5074"
    assert rows[DUP_BLOCKED_ID]["match_method"] == "QWEN_LLM_MATCH"
    same_recipe_5055 = [
        r for r in rows.values()
        if r["recipe_id"] == "r-dup" and r["master_ingredient_code"] == "5055"
    ]
    assert len(same_recipe_5055) == 1, "the recipe must not end up with two 5055 rows"


def test_unmatched_invariants_hold_for_every_unmatched_row(fixture_paths):
    fix.run(apply=True)
    for row in _read_ing(fixture_paths["ing_csv"]).values():
        if row["match_method"] != "UNMATCHED":
            continue
        assert row["master_ingredient_code"] in (None, "")
        assert row["master_ingredient_name"] in (None, "")
        assert row["match_confidence"] in (None, "")
        for field in NUTRITION:
            assert row[field] in (None, "")


def test_audit_reclassifies_remapped_rows_as_C_without_touching_others(fixture_paths):
    """The two remapped rows must classify as C via their row-id-keyed reviewed
    entries; the out-of-scope dangling rows must stay D."""
    before = {r["id"]: r["class"] for r in audit_mod.audit()["rows"]}
    assert before[REMAP_ID_1] == "D" and before[REMAP_ID_2] == "D"

    fix.run(apply=True)

    after = {r["id"]: r["class"] for r in audit_mod.audit()["rows"]}
    assert after[REMAP_ID_1] == "C" and after[REMAP_ID_2] == "C"
    assert after["bac-ha-row"] == "D"
    assert after[DUP_BLOCKED_ID] == "D"
    # Cleared rows leave the Qwen population entirely.
    assert CLEAR_ID_1 not in after and CLEAR_ID_2 not in after


def test_recipe_rollups_follow_the_changed_rows(fixture_paths):
    fix.run(apply=True)
    with fixture_paths["recipes_csv"].open(encoding="utf-8-sig", newline="") as f:
        recipes = {r["id"]: r for r in csv.DictReader(f)}
    assert recipes["r-remap1"]["total_calories"] == "414.0"
    assert recipes["r-remap2"]["total_calories"] == "241.5"
    # Clearing removes the row's (zero) contribution; totals stay 0.0.
    assert recipes["r-clear1"]["total_calories"] == "0.0"
    # Out-of-scope recipes keep their totals.
    assert recipes["r-dup"]["total_calories"] == "34.5"


# --------------------------------------------------------------------------
# Real-dataset scope invariants (read-only)
# --------------------------------------------------------------------------

def test_scope_is_exactly_four_rows_all_on_the_dangling_mango_code():
    assert len(fix.TARGET_IDS) == 4
    assert fix.OLD_CODE == "5074" and fix.OLD_NAME == "Xoài"
    assert fix.REMAP_NEW_CODE == "5055" and fix.REMAP_NEW_NAME == "Xoài chín"
    # OLD_CODE being the mango code is what structurally keeps every Bạc hà
    # row (dangling code 13038) out of this remediation's reach.
    assert fix.OLD_CODE != "13038"


def test_duplicate_blocked_and_bac_ha_rows_are_out_of_scope_on_real_data():
    rows = {r["id"]: r for r in audit_mod.read_csv(audit_mod.ING)}
    dup = next((r for r in rows.values()
                if r["raw_text"] == "ĂN KÈM: xoài cát chín"), None)
    assert dup is not None, "duplicate-blocked row not found in the live dataset"
    assert dup["id"] not in fix.TARGET_IDS
    assert dup["master_ingredient_code"] == "5074"

    bac_ha_ids = {r["id"] for r in rows.values()
                  if r["master_ingredient_code"] == "13038"}
    assert len(bac_ha_ids) == 32
    assert not (bac_ha_ids & fix.TARGET_IDS), "no Bạc hà row may be in scope"


def test_real_dataset_leaves_thirty_nine_class_d_rows_unresolved():
    class_d = {r["id"] for r in audit_mod.audit()["rows"] if r["class"] == "D"}
    assert len(class_d - fix.TARGET_IDS) == 39


def test_no_global_xoai_or_bac_ha_alias_was_introduced():
    """This fix resolves rows by id; the alias layer must be untouched."""
    alias_map = json.loads(
        (audit_mod.ROOT / "data/processed/viendinhduong/ingredient_alias_map.json")
        .read_text(encoding="utf-8")
    )
    for varietal in ("xoài cát", "xoài thái", "xoài cát chu", "xoài hòa lộc", "xoài cát lộc"):
        assert varietal not in alias_map, f"{varietal!r} must not become an alias"
    for mint in ("bạc hà", "rau bạc hà", "cây bạc hà", "lá bạc hà"):
        assert mint not in alias_map, f"{mint!r} must not become an alias"


def test_reviewed_row_remaps_stay_row_keyed_and_narrow():
    """Every reviewed remap is keyed by row id and targets an exact catalog
    identity -- none may generalize to a cleaned name or a bare code."""
    remaps = audit_mod.REVIEWED_ROW_REMAPS
    assert set(remaps) == {
        "dfa8f4c6-ffc5-4dc5-87de-ec2d52632bea",
        "114d0cb0-d4af-4dab-a094-b95a04ea4b1b",
        "60c41843-1d7b-45bf-aa7e-0ba399cb2258",
    }
    masters = {r["code"]: r for r in audit_mod.read_csv(audit_mod.MASTER)}
    for row_id, (code, name, reason) in remaps.items():
        assert len(row_id) == 36, "keys must be row ids, not cleaned names"
        assert masters[code]["name_vi"] == name, f"{code} no longer names {name!r}"
        assert reason.strip(), "each reviewed remap must carry its evidence"
    for row_id, _ in fix.REMAP_ROWS:
        assert remaps[row_id][0] == "5055"
