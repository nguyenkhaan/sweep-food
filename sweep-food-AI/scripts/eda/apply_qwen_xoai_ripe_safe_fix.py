"""Apply the reviewed explicit-ripe Xoài remediation (4 of the 43 open Class-D rows).

Follow-up to scripts/eda/apply_qwen_class_d_safe_fix.py, which resolved 31 of
the original 74 dangling-code Qwen rows and deliberately left 43 open (32 "Bạc
hà" on dangling code 13038, 11 "Xoài" on dangling code 5074). A second
row-level review of those 43 resolved exactly 4 of the Xoài rows; the other 39
stay open and are never touched here.

What the review established (per-row evidence, not fuzzy string similarity):

  - 2 rows REMAP 5074 -> 5055 "Xoài chín". Both raw texts state ripeness
    explicitly in the author's own words ("vừa chín tới" = "just ripened"),
    which is in-text evidence rather than an inference from the varietal name
    ("xoài cát") or from the dish. 5055 is the only ripe-mango identity in the
    current catalog, so the target is unique as well as explicit.
  - 2 rows CLEAR ("xoài Thái"). These have NO valid current catalog identity:
    xoài Thái is a cultivar eaten green, the catalog has no green/unripe mango
    entry (5033 "Muỗm, quéo" is a different species, Mangifera foetida), and
    mapping them to ripe 5055 would be nutritionally wrong. This matches how
    the existing dataset already treats green mango: every other explicitly
    green row ("xoài xanh/sống/keo/non", and the one other "Xoài Thái" row)
    is UNMATCHED, and no "xoài thái" alias exists.
  - 39 rows stay untouched: all 32 Bạc hà rows (no raw text names dọc mùng, no
    "bạc hà" alias exists in any form, and 4026 is not a unique identity for
    the string -- the repo maps other bạc hà rows to 4074), plus 7 Xoài rows
    that name only a cultivar with no ripeness word. One of those 7
    (71e4d150) is additionally duplicate-blocked: its recipe already carries a
    separate 5055 row, so remapping it would double-count the same mango.

Deliberately NOT done here, matching the review's scope:
  - No global "xoài" -> 5055 alias is created. The ingredient_alias_map already
    maps bare "xoài" -> 5055, but these rows clean to "xoài cát"/"xoài thái";
    resolving them by id keeps varietal strings out of the alias layer, where
    they would wrongly capture green-mango rows too.
  - No "bạc hà" -> "dọc mùng" mapping, global or otherwise.
  - The master catalog, alias map, taxonomy and weight fallbacks are not touched;
    weights are read from each row as-is and never recomputed.

Safety model (fail closed, idempotent, dry-run by default) -- identical to
apply_qwen_class_d_safe_fix.py:
  - Every one of the 4 target rows is pinned by id AND exact raw_text. Before
    any mutation each row must be in exactly one of two states, "pending" or
    "already_applied"; any other observed state (drifted raw_text, a different
    code, a partially-mutated row) aborts the ENTIRE run before anything is
    written. Nothing is ever partially applied.
  - REMAP validates that target code 5055 exists in the live catalog under the
    exact expected name before use, then computes nutrition via
    nlp.matching_integrity.stage_qwen_update from the catalog plus the row's
    own existing weight -- never typed by hand.
  - Rows already in "already_applied" state are left byte-identical.
  - The 39 untouched Class-D rows are asserted to still number exactly 39 on
    every run, applied or not.

Scope: data/processed/recipes/recipe_ingredients.{csv,json} and
data/processed/recipes/recipes.{csv,json} (rollup totals + nutrition_status/
missing_nutrition_count, JSON only). Canonical outputs are intentionally NOT
regenerated here, same as the two prior safe fixes.
"""

import argparse
import json

from nlp.matching_integrity import stage_qwen_update
from nlp.nutrition import nutrition_value
from nlp.qwen_matching import QWEN_MATCH_CONFIDENCE
from scripts.eda.apply_qwen_class_d_safe_fix import (
    DriftError,
    _apply_rollups,
    _clear_applied_probe,
    _recompute_status,
    _row_state,
    clear_row,
    read_csv,
    read_json,
    recompute_recipe_rollups,
    write_csv,
    write_json,
)
from scripts.eda.apply_qwen_safe_fix import ING, ING_JSON, RECIPES_CSV, RECIPES_JSON
from scripts.eda.audit_qwen_matching import MASTER, OUT, audit

# Reviewed 2026-09-13. Both raw texts carry the explicit ripeness phrase
# "vừa chín tới"; raw_text is re-checked at run time so an id whose row content
# has since changed fails closed instead of silently remapping the wrong thing.
REMAP_ROWS = (
    ("114d0cb0-d4af-4dab-a094-b95a04ea4b1b", "Xoài cát chu vừa chín tới 600g (2 quả nhỏ)"),
    ("60c41843-1d7b-45bf-aa7e-0ba399cb2258", "Xoài cát ( vừa chín tới) 1 quả"),
)
# Reviewed 2026-09-13. Green-eaten cultivar with no valid catalog identity.
CLEAR_ROWS = (
    ("607464a4-747d-497e-8853-b886849e8197", "1 trái xoài Thái"),
    ("7d81d723-cf55-4349-aa59-8f2cfa699dbb", "1/2 trái xoài Thái"),
)

OLD_CODE = "5074"
OLD_NAME = "Xoài"
REMAP_NEW_CODE = "5055"
REMAP_NEW_NAME = "Xoài chín"
REMAP_METHOD = "QWEN_LLM_MATCH"

TARGET_IDS = frozenset([rid for rid, _ in REMAP_ROWS] + [rid for rid, _ in CLEAR_ROWS])
assert len(REMAP_ROWS) == 2 and len(CLEAR_ROWS) == 2
assert len(TARGET_IDS) == 4

# The full current Class-D population this remediation was reviewed against:
# 43 open rows, of which 4 are targeted here and 39 stay open. Tests targeting a
# smaller fixture world monkeypatch this so the drift guard tracks the fixture's
# actual size instead of re-implementing the check with a different number.
EXPECTED_CLASS_D_COUNT = 43


def _remap_applied_probe(row):
    code = (row.get("master_ingredient_code") or "").strip()
    name = (row.get("master_ingredient_name") or "").strip()
    return code == REMAP_NEW_CODE and name == REMAP_NEW_NAME


def build_plan():
    """Read-only: locate the 4 rows in the live CSV and classify each one.

    Cross-checks against the current Class-D audit so a run aborts if the
    dataset has moved since this remediation was reviewed. The untouched
    Class-D rows outside this remediation's scope must number exactly
    EXPECTED_CLASS_D_COUNT - len(TARGET_IDS) on every run, applied or not --
    that population is never mutated here. Target rows themselves are
    deliberately NOT required to still classify as D: once applied, a CLEARed
    row becomes UNMATCHED (leaving the Qwen population entirely) and a REMAPed
    row carries a valid code, which is exactly what makes reruns idempotent.
    Per-row correctness is established independently by _row_state() below,
    which inspects the row's own fields rather than the audit's bucket.
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

    by_id = {r["id"]: r for r in read_csv(ING)}
    states = {}
    for rid, raw_text in CLEAR_ROWS:
        row = by_id.get(rid)
        if row is None:
            raise DriftError(f"CLEAR row {rid} not found in {ING}")
        states[rid] = _row_state(row, raw_text, OLD_CODE, OLD_NAME, _clear_applied_probe)
    for rid, raw_text in REMAP_ROWS:
        row = by_id.get(rid)
        if row is None:
            raise DriftError(f"REMAP row {rid} not found in {ING}")
        states[rid] = _row_state(row, raw_text, OLD_CODE, OLD_NAME, _remap_applied_probe)

    # Belt-and-suspenders cross-check between the two independent signals: a
    # still-pending row must currently show up as Class D, and an
    # already-applied one must not.
    for rid, state in states.items():
        in_d = rid in class_d_ids
        if state == "pending" and not in_d:
            raise DriftError(f"row {rid} is pending but the audit no longer classifies it as Class D")
        if state == "already_applied" and in_d:
            raise DriftError(f"row {rid} looks already-applied but the audit still classifies it as Class D")

    return result, masters, states


def _apply_remap(row, masters):
    match_fields = {
        "master_ingredient_code": REMAP_NEW_CODE,
        "master_ingredient_name": REMAP_NEW_NAME,
        "match_method": REMAP_METHOD,
        "match_confidence": QWEN_MATCH_CONFIDENCE,
    }
    # The row's own stored weight is reused as-is; no weight fallback or
    # re-estimation policy is invoked by this fix.
    weight = nutrition_value(row.get("estimated_weight_g")) or 0.0
    updates = stage_qwen_update(row, masters, weight, match_fields=match_fields)
    new_row = dict(row)
    new_row.update(updates)
    return new_row


def run(apply=False):
    result, masters, states = build_plan()
    other_d_ids = {r["id"] for r in result["rows"] if r["class"] == "D"} - TARGET_IDS

    ing_csv_rows = read_csv(ING)
    ing_csv_fields = list(ing_csv_rows[0].keys())
    ing_json_rows = read_json(ING_JSON)

    clear_ids = {rid for rid, _ in CLEAR_ROWS}
    remap_ids = {rid for rid, _ in REMAP_ROWS}
    clear_now = {rid for rid in clear_ids if states[rid] == "pending"}
    remap_now = {rid for rid in remap_ids if states[rid] == "pending"}

    def transform(row):
        rid = row["id"]
        if states.get(rid) != "pending":
            return row
        if rid in clear_ids:
            return clear_row(row)
        if rid in remap_ids:
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

    recipe_of = {r["id"]: r["recipe_id"] for r in ing_csv_rows if r["id"] in TARGET_IDS}
    report = {
        "status": "applied" if apply else "preview",
        "remap_target_count": len(remap_ids),
        "remap_applied_now": len(remap_now),
        "remap_already_applied": len(remap_ids) - len(remap_now),
        "clear_target_count": len(clear_ids),
        "clear_applied_now": len(clear_now),
        "clear_already_applied": len(clear_ids) - len(clear_now),
        "needs_review_untouched": len(other_d_ids),
        "affected_recipe_count": len(set(recipe_of.values())),
        "recipes_with_changed_totals": changed,
        "recipes_with_changed_missing_count": status_report["recipes_with_changed_missing_count"],
        "recipes_with_status_label_changed": status_report["recipes_with_status_label_changed"],
        "status_transitions": status_report["status_transitions"],
        "remap_row_ids": sorted(remap_ids),
        "clear_row_ids": sorted(clear_ids),
        "affected_recipe_ids": sorted(set(recipe_of.values())),
        "canonical_note": (
            "Canonical outputs (canonical_recipes.csv/json, canonical_recipe_ingredients.csv/json, "
            "recipe_canonical_mapping.csv) are NOT regenerated by this script and are now stale for "
            "these rows/recipes."
        ),
    }

    if apply:
        write_csv(ING, new_ing_csv_rows, ing_csv_fields)
        write_json(ING_JSON, new_ing_json_rows)
        write_csv(RECIPES_CSV, recipes_csv_rows, recipes_csv_fields)
        write_json(RECIPES_JSON, recipes_json_rows)
        OUT.mkdir(parents=True, exist_ok=True)
        (OUT / "applied_xoai_ripe_fix.json").write_text(
            json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )

    return report


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args(argv)
    print(json.dumps(run(apply=args.apply), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
