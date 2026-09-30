"""Apply the reviewed Class-D remediation (31 of 74 dangling-code Qwen rows).

Class D (scripts/eda/audit_qwen_matching.py) is every QWEN_LLM_MATCH row whose
master_ingredient_code no longer exists in the current catalog. All 74 rows
resolve to exactly two dangling codes: 13038 "Bac ha tuoi" (33 rows) and 5074
"Xoai" (41 rows) -- both are still hard-coded in nlp/qwen_matching.py's mapper
table, but the catalog was later renumbered and no longer carries either code.

Manual, recipe-level review (not fuzzy string matching) resolved 31 of the 74
rows with strong-enough evidence to act on now; the other 43 stay open pending
further human review and are never touched here:

  - 30 rows (Xoai, explicit-unripe "xanh/song/keo/non" plus two dish-context
    rows -- a mango-shoot row and a green-mango-salad row) have NO valid
    current catalog identity: the only mango entry left is 5055 "Xoai chin"
    (ripe), which would be nutritionally wrong for all 30. -> CLEAR.
  - 1 row (id dfa8f4c6, raw_text 'Bac ha (Doc mung): 100g') explicitly
    disambiguates itself in the source text, and catalog code 4026 exists
    under the exact name "Doc mung". -> REMAP 13038 -> 4026.
  - 43 rows (3 explicit-ripe Xoai, 8 unqualified Xoai, 32 Bac ha) have
    plausible-but-not-exact-identity evidence only (varietal names, "canh
    chua" dish context, mint-like wording) and are left untouched pending
    human review -- "canh chua" context alone is explicitly not sufficient
    evidence for an automatic remap.

Safety model (fail closed, idempotent, dry-run by default):
  - Every one of the 31 target rows is pinned by id AND exact raw_text.
    Before any mutation, each row must be in exactly one of two states:
    "pending" (still has its original dangling code and stored name) or
    "already_applied" (already carries this script's fixed-state fields).
    Any other observed state -- drifted raw_text, a different code, a
    partially-mutated row -- aborts the ENTIRE run before anything is
    written. Nothing is ever partially applied.
  - REMAP validates the target code (4026) exists in the live catalog under
    the exact expected name before use, via the same identity check
    nlp/matching_integrity.stage_qwen_update already enforces for the normal
    Qwen pipeline. Nutrition for the remap is computed by that function from
    the catalog + the row's own current weight -- never typed by hand.
  - Rows already in "already_applied" state are left byte-identical
    (idempotent reruns produce no diff and no error).
  - Only the 31 named rows are touched. Every other row -- the 43
    NEEDS_REVIEW Class-D rows, Class B/C Qwen rows, non-Qwen rows -- passes
    through unchanged; recipe rollups/status are recomputed for all recipes
    but only actually change (and are only counted as changed) where the
    underlying ingredient rows changed.

Scope: data/processed/recipes/recipe_ingredients.{csv,json} and
data/processed/recipes/recipes.{csv,json} (rollup totals + nutrition_status/
missing_nutrition_count, JSON only -- recipes.csv has no status columns).
Canonical outputs are intentionally NOT regenerated here, same as
scripts/eda/apply_qwen_safe_fix.py's Class-A fix.
"""

import argparse
import csv
import json
from collections import Counter, defaultdict
from pathlib import Path

from nlp.matching_integrity import stage_qwen_update
from nlp.nutrition import nutrition_value
from nlp.qwen_matching import QWEN_MATCH_CONFIDENCE
from scripts.eda.apply_qwen_safe_fix import (
    ING,
    ING_JSON,
    RECIPES_CSV,
    RECIPES_JSON,
    _apply_rollups,
    clear_row,
    read_csv,
    read_json,
    recompute_recipe_rollups,
    write_json,
)
from scripts.eda.audit_qwen_matching import MASTER, OUT, audit


def write_csv(path, rows, fieldnames):
    """Write plain utf-8, no BOM -- matches this dataset's existing encoding.

    apply_qwen_safe_fix.write_csv opens with 'utf-8-sig', which would inject a
    byte-order mark this file has never had, showing up as an unrelated header
    diff on every apply. Reads still tolerate an optional BOM via read_csv's
    'utf-8-sig' (which strips one if present); this only controls what gets
    written.
    """
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)

# Reviewed 2026-09-12: the 30 approved CLEAR rows. Each (id, raw_text) pins
# the exact row reviewed; raw_text is re-checked at run time so an id whose
# row content has since changed for any reason fails closed instead of
# silently clearing the wrong thing.
CLEAR_ROWS = (
    ("060d7262-3a1e-45fb-81b7-a15c24b9cc2a", "Xoài xanh 1 quả"),
    ("09ef19c6-5702-4c3f-8716-a32c8aa3a107", "Xoài keo 1 quả"),
    ("16df2f58-eb84-4c57-9773-36511273861b", "xoài sống"),
    ("1e80a0c1-93ba-4ca9-abcd-b9dfdefbe1ab", "xoài xanh"),
    ("21ffc729-02ca-4cd4-9c47-14211705bba1", "Xoài xanh: 100g"),
    ("24d68c08-e1a1-445f-abcb-7f4d6334a86b", "Xoài sống 100g Cắt que nhỏ cỡ đầu đũa"),
    ("27e350b6-8b9c-4be3-a369-43bcc3cf106d", "Xoài keo 1/4 trái"),
    ("37e1435a-dbfb-48fb-9b78-0f1c84018018", "Xoài xanh 100 gr"),
    ("4e49a406-48c6-4f04-a40b-6f027a9ff01b", "Xoài keo: 1 trái"),
    ("582e8751-5d1f-44b6-a23a-87b21be4110c", "Xoài xanh 1 trái"),
    ("5df91eb7-542b-4f4c-9001-aed0fefbb4ee", "Xoài keo : 100g"),
    ("62ef84c1-7035-466d-b9f9-ac839e7ae011", "Xoài cát xanh: 1/2 trái"),
    ("652e8ceb-54e3-4151-980e-b30c596551d6", "Xoài Thái: 1 quả"),
    ("6bae6edd-6461-4bf8-871d-4f463afdb6fd", "Xoài xanh 150g"),
    ("6cc1b399-d781-4d60-a458-89447edb808a", "1 quả xoài keo xanh"),
    ("7736b6c0-4f38-451c-9a51-dbc6c9be9888", "1/2 quả Xoài xanh"),
    ("7f6a4a2f-c4de-4249-8c76-b885aaaa8e72", "1 trái nhỏ Xoài xanh (xoài Thái hoặc xoài tứ quý)"),
    ("80ccc88a-bca7-4375-803f-59532d0d27c9", "Xoài keo 1 trái"),
    ("8358fe71-1c0a-488d-9759-1f798e3f6afb", "Xoài xanh: 300g"),
    ("8e9117dc-231d-485d-9d0f-3f3c17a1d6c4", "Xoài keo 1 trái"),
    ("904ecd49-281e-47a0-a364-05f4f15c4eff", "Xoài keo 160g"),
    ("a7c6ff77-1bdd-4ed0-b3f2-558e2625b6aa", "2 trái xoài non"),
    ("af49d882-a065-43cf-bc70-a7ee60797ecb", 'ĂN KÈM: Muối ớt sả và rau "rừng" như đọt xoài'),
    ("ba5c2f06-38a0-4f40-83eb-3bebc42212b1", "Xoài xanh 100g"),
    ("baf69bde-9d2d-4ed4-b27b-adc1cc9656ac", "Xoài xanh 1 quả"),
    ("d970541b-e65f-44ca-a3c5-6421589e0d56", "XOÀI KEO: 1 trái (cắt sợi)"),
    ("df528849-437b-4e63-a72c-ae5384683547", "Xoài keo 1 quả"),
    ("e81b0981-fb33-46a8-82b3-141ddf88b393", "Xoài keo 1 quả nhỏ"),
    ("ea11b112-8f99-48ef-a908-d5eff88e298e", "Xoài keo: 1 trái"),
    ("fbe8da09-65d6-4611-ad96-84c5dcb14115", "Xoài keo: 1 trái"),
)
CLEAR_OLD_CODE = "5074"
CLEAR_OLD_NAME = "Xoài"
assert len(CLEAR_ROWS) == 30
assert len({rid for rid, _ in CLEAR_ROWS}) == 30

REMAP_ROW_ID = "dfa8f4c6-ffc5-4dc5-87de-ec2d52632bea"
REMAP_RAW_TEXT = "Bạc hà (Dọc mùng): 100g"
REMAP_OLD_CODE = "13038"
REMAP_OLD_NAME = "Bạc hà tươi"
REMAP_NEW_CODE = "4026"
REMAP_NEW_NAME = "Dọc mùng"
REMAP_METHOD = "QWEN_LLM_MATCH"

TARGET_IDS = frozenset([rid for rid, _ in CLEAR_ROWS] + [REMAP_ROW_ID])

# The full current Class-D population this remediation was reviewed against.
# Tests targeting a smaller fixture world monkeypatch this alongside CLEAR_ROWS
# / TARGET_IDS so build_plan()'s drift guard tracks the fixture's actual size
# instead of re-implementing the check with a different hardcoded number.
EXPECTED_CLASS_D_COUNT = 74


class DriftError(ValueError):
    """A reviewed target row no longer matches its expected pre/post state."""


def _row_state(row, raw_text, old_code, old_name, applied_probe):
    """Classify one row as 'pending', 'already_applied', or raise on drift.

    raw_text is checked in both states: this is recipe-authored source text
    that this script never writes, so it must be identical in both states or
    the row is not the one that was reviewed.
    """
    rid = row.get("id")
    if row.get("raw_text") != raw_text:
        raise DriftError(
            f"row {rid}: raw_text drifted (expected {raw_text!r}, found {row.get('raw_text')!r})"
        )
    code = (row.get("master_ingredient_code") or "").strip()
    name = (row.get("master_ingredient_name") or "").strip()
    if code == old_code and name == old_name and row.get("match_method") == "QWEN_LLM_MATCH":
        return "pending"
    if applied_probe(row):
        return "already_applied"
    raise DriftError(
        f"row {rid}: neither pending ({old_code!r}/{old_name!r}) nor already-applied state matched "
        f"(found code={code!r} name={name!r} method={row.get('match_method')!r})"
    )


def _clear_applied_probe(row):
    code = row.get("master_ingredient_code")
    name = row.get("master_ingredient_name")
    conf = row.get("match_confidence")
    cal = row.get("calories")
    return (
        (code is None or str(code).strip() == "")
        and (name is None or str(name).strip() == "")
        and row.get("match_method") == "UNMATCHED"
        and (conf is None or str(conf).strip() == "")
        and (cal is None or str(cal).strip() == "")
    )


def _remap_applied_probe(row):
    code = (row.get("master_ingredient_code") or "").strip()
    name = (row.get("master_ingredient_name") or "").strip()
    return code == REMAP_NEW_CODE and name == REMAP_NEW_NAME


def build_plan():
    """Read-only: locate the 31 rows in the live CSV and classify each one.

    Also cross-checks against the current Class-D audit so a run aborts if
    the dataset has moved since this remediation was reviewed. The 43
    untouched (non-target) Class-D rows must number exactly
    EXPECTED_CLASS_D_COUNT - len(TARGET_IDS) on every run, applied or not --
    that population is never mutated by this script. Target rows themselves
    are deliberately NOT required to still classify as D: a target row that
    this script already applied has legitimately left Class D (CLEARed rows
    become UNMATCHED; the REMAPed row gets a valid code), which is exactly
    what makes reruns idempotent. Per-row correctness for target rows is
    instead established independently by _row_state() below, which inspects
    the row's own fields rather than the audit's classification bucket.
    """
    result = audit()
    class_d_ids = {r["id"] for r in result["rows"] if r["class"] == "D"}
    other_d_ids = class_d_ids - TARGET_IDS
    expected_other = EXPECTED_CLASS_D_COUNT - len(TARGET_IDS)
    if len(other_d_ids) != expected_other:
        raise DriftError(
            f"expected {expected_other} untouched Class-D rows outside this remediation's "
            f"scope, found {len(other_d_ids)}"
        )

    masters = {r["code"]: r for r in read_csv(MASTER)}
    if REMAP_NEW_CODE not in masters:
        raise DriftError(f"remap target code {REMAP_NEW_CODE!r} is absent from the current catalog")
    if masters[REMAP_NEW_CODE].get("name_vi", "").strip() != REMAP_NEW_NAME:
        raise DriftError(
            f"remap target code {REMAP_NEW_CODE!r} now names "
            f"{masters[REMAP_NEW_CODE].get('name_vi')!r}, not {REMAP_NEW_NAME!r}"
        )

    ing_rows = read_csv(ING)
    by_id = {r["id"]: r for r in ing_rows}

    states = {}
    for rid, raw_text in CLEAR_ROWS:
        row = by_id.get(rid)
        if row is None:
            raise DriftError(f"CLEAR row {rid} not found in {ING}")
        states[rid] = _row_state(row, raw_text, CLEAR_OLD_CODE, CLEAR_OLD_NAME, _clear_applied_probe)

    remap_row = by_id.get(REMAP_ROW_ID)
    if remap_row is None:
        raise DriftError(f"REMAP row {REMAP_ROW_ID} not found in {ING}")
    states[REMAP_ROW_ID] = _row_state(
        remap_row, REMAP_RAW_TEXT, REMAP_OLD_CODE, REMAP_OLD_NAME, _remap_applied_probe
    )

    # Belt-and-suspenders cross-check between the two independent signals:
    # a still-pending row must currently show up as Class D, and an
    # already-applied one must not.
    for rid, state in states.items():
        in_d = rid in class_d_ids
        if state == "pending" and not in_d:
            raise DriftError(f"row {rid} is pending but the audit no longer classifies it as Class D")
        if state == "already_applied" and in_d:
            raise DriftError(f"row {rid} looks already-applied but the audit still classifies it as Class D")

    return result, masters, states


def _apply_clear(row):
    return clear_row(row)


def _apply_remap(row, masters):
    match_fields = {
        "master_ingredient_code": REMAP_NEW_CODE,
        "master_ingredient_name": REMAP_NEW_NAME,
        "match_method": REMAP_METHOD,
        "match_confidence": QWEN_MATCH_CONFIDENCE,
    }
    weight = nutrition_value(row.get("estimated_weight_g")) or 0.0
    updates = stage_qwen_update(row, masters, weight, match_fields=match_fields)
    new_row = dict(row)
    new_row.update(updates)
    return new_row


def _recompute_status(recipe_json_rows, ing_json_rows):
    """Recompute nutrition_status/missing_nutrition_count the same way
    scripts/reprocess_recipe_weights_and_nutrition.py does: a recipe is
    COMPLETE when every ingredient row has a non-null calories value,
    INCOMPLETE when 30%+ of rows are missing it, PARTIAL otherwise. Only
    applied to recipes.json -- recipes.csv carries no status columns.

    Returns a breakdown that keeps two distinct things separate: a bump in
    missing_nutrition_count (expected for every recipe touched by a CLEAR,
    since exactly one of its rows newly reports missing nutrition) versus an
    actual nutrition_status LABEL transition (only some of those recipes
    cross the COMPLETE/PARTIAL/INCOMPLETE threshold). Collapsing the two into
    one "changed" count is what produced a prior "8 changed" vs "5+4"
    reporting inconsistency -- the undercount was in the summary, not in the
    written nutrition_status/missing_nutrition_count values themselves.
    """
    missing_by_recipe = defaultdict(int)
    count_by_recipe = defaultdict(int)
    for r in ing_json_rows:
        rid = r.get("recipe_id")
        if not rid:
            continue
        count_by_recipe[rid] += 1
        if nutrition_value(r.get("calories")) is None:
            missing_by_recipe[rid] += 1

    missing_count_changed = 0
    status_transitions = Counter()
    for rec in recipe_json_rows:
        if "nutrition_status" not in rec and "missing_nutrition_count" not in rec:
            continue
        rid = rec.get("id")
        tot_cnt = count_by_recipe.get(rid) or int(rec.get("ingredients_count") or 1)
        miss_cnt = missing_by_recipe.get(rid, 0)
        if miss_cnt == 0:
            status = "COMPLETE"
        elif miss_cnt / max(tot_cnt, 1) < 0.3:
            status = "PARTIAL"
        else:
            status = "INCOMPLETE"
        old_status = rec.get("nutrition_status")
        if old_status != status or rec.get("missing_nutrition_count") != miss_cnt:
            missing_count_changed += 1
        status_transitions[f"{old_status} -> {status}" if old_status != status else "unchanged"] += 1
        rec["nutrition_status"] = status
        rec["missing_nutrition_count"] = miss_cnt
    return {
        "recipes_with_changed_missing_count": missing_count_changed,
        "recipes_with_status_label_changed": sum(v for k, v in status_transitions.items() if k != "unchanged"),
        "status_transitions": dict(status_transitions),
    }


def run(apply=False):
    result, masters, states = build_plan()
    # The untouched Class-D population outside this remediation's scope is a
    # fixed invariant (43 on the real dataset): unlike the raw Class-D count,
    # it does not shrink once target rows leave Class D after being applied.
    other_d_ids = {r["id"] for r in result["rows"] if r["class"] == "D"} - TARGET_IDS

    ing_csv_rows = read_csv(ING)
    ing_csv_fields = list(ing_csv_rows[0].keys())
    ing_json_rows = read_json(ING_JSON)

    clear_ids = {rid for rid, _ in CLEAR_ROWS}
    clear_now = {rid for rid in clear_ids if states[rid] == "pending"}
    remap_now = states[REMAP_ROW_ID] == "pending"

    def transform(row):
        rid = row["id"]
        if rid in clear_ids and states[rid] == "pending":
            return _apply_clear(row)
        if rid == REMAP_ROW_ID and states[rid] == "pending":
            return _apply_remap(row, masters)
        return row

    new_ing_csv_rows = [transform(r) for r in ing_csv_rows]
    new_ing_json_rows = [transform(r) for r in ing_json_rows]

    rollups = recompute_recipe_rollups(new_ing_csv_rows)
    recipes_csv_rows = read_csv(RECIPES_CSV)
    recipes_csv_fields = list(recipes_csv_rows[0].keys())
    changed = _apply_rollups(recipes_csv_rows, rollups)

    recipes_json_rows = read_json(RECIPES_JSON)
    _apply_rollups(recipes_json_rows, rollups)
    status_report = _recompute_status(recipes_json_rows, new_ing_json_rows)

    remap_recipe_id = next((r["recipe_id"] for r in ing_csv_rows if r["id"] == REMAP_ROW_ID), None)
    clear_recipe_ids = {r["recipe_id"] for r in ing_csv_rows if r["id"] in clear_ids}
    affected_recipe_ids = clear_recipe_ids | ({remap_recipe_id} if remap_recipe_id else set())

    report = {
        "status": "applied" if apply else "preview",
        "clear_target_count": len(clear_ids),
        "clear_applied_now": len(clear_now),
        "clear_already_applied": len(clear_ids) - len(clear_now),
        "remap_target_count": 1,
        "remap_applied_now": 1 if remap_now else 0,
        "remap_already_applied": 0 if remap_now else 1,
        "needs_review_untouched": len(other_d_ids),
        "affected_recipe_count": len(affected_recipe_ids),
        "recipes_with_changed_totals": changed,
        "recipes_with_changed_missing_count": status_report["recipes_with_changed_missing_count"],
        "recipes_with_status_label_changed": status_report["recipes_with_status_label_changed"],
        "status_transitions": status_report["status_transitions"],
        "remap_recipe_id": remap_recipe_id,
        "clear_row_ids": sorted(clear_ids),
        "remap_row_id": REMAP_ROW_ID,
    }

    if apply:
        write_csv(ING, new_ing_csv_rows, ing_csv_fields)
        write_json(ING_JSON, new_ing_json_rows)
        write_csv(RECIPES_CSV, recipes_csv_rows, recipes_csv_fields)
        write_json(RECIPES_JSON, recipes_json_rows)
        OUT.mkdir(parents=True, exist_ok=True)
        (OUT / "applied_class_d_fix.json").write_text(
            json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )

    return report


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args(argv)
    report = run(apply=args.apply)
    print(json.dumps({k: v for k, v in report.items() if k != "clear_row_ids"}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
