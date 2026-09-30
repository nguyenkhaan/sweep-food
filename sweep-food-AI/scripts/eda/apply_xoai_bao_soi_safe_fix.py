"""Apply the reviewed "xoài bào sợi" remediation. Default previews; --apply writes.

Follow-up to the mango alias audit (2026-09-13), which reviewed all seven
"xoài" entries in data/processed/viendinhduong/ingredient_alias_map.json and
their 55 mango rows. Two findings are acted on here:

  - Row 3573cbc5 (raw_text "xoài bào sợi", recipe "Bún bì căn") is matched to
    5055 "Xoài chín" (ripe mango) by the preset-alias stage, but the recipe's
    own source text says the opposite twice: the description calls it "xoài
    chua" (sour mango) and step 3 lists "dưa leo, xoài xanh, rau thơm" --
    "xoài xanh" is green mango in the author's own words. 5055 is a ripe
    identity (sugar 14.8 g/100 g), so the row is nutritionally as well as
    semantically wrong. The catalog has no green/unripe mango entry (5033
    "Muỗm, quéo" is Mangifera foetida, a different species), so there is no
    valid target to remap to. -> CLEAR to UNMATCHED, which is exactly how
    every other author-declared green mango row in this dataset is already
    treated: all 31 rows carrying an explicit green token in raw_text
    ("xanh"/"sống"/"non"/"keo"/"thái"/"tứ quý") are UNMATCHED, without
    exception.
  - Two alias entries are dead weight and are REMOVED: "xoài bào sợi" (a
    preparation phrase that asserts a ripeness the words do not carry) and
    "xoài chín tươi" (0 rows). Both are provably no-ops for matching --
    clean_culinary_query() reduces "xoài bào sợi" to "xoài" (still resolving
    via the bare alias) and "xoài chín tươi" to "xoài chín" (resolving as
    CLEANED_NAME_MATCH against the catalog name). Removing them changes no
    row; it removes a false claim from the alias layer.

Removing the "xoài bào sợi" alias is therefore NOT what fixes the row -- the
cleaning stage collapses the string to "xoài" and the bare "xoài" -> 5055
alias would still capture it at the same stage and confidence. The row-level
CLEAR above is the only change that actually corrects the data. This is why
both edits ship together.

Deliberately NOT done here, matching the review's approved scope:
  - The bare "xoài" -> 5055 alias stays. It is the actual root enabler (it
    encodes "mango = ripe" as a global default), but removing it would strand
    6 rows, 5 of which are plausibly ripe. It needs its own reviewed pass.
  - "xoài chín", "xoài chín giòn", "trang trí xoài chín" and "xoài đông lạnh"
    stay: each is backed by explicit ripeness in its rows' raw text or source
    body. All five preserved aliases are asserted present and unchanged on
    every run.
  - The other 5 bare-"xoài" rows, the 7 rows on dangling code 5074, the 32
    Bạc hà rows, the green-mango catalog gap, cleaner behaviour, the master
    catalog, taxonomy and weight fallbacks are all untouched.

Safety model (fail closed, idempotent, dry-run by default) -- same as the
three prior safe fixes:
  - The target row is pinned by id AND exact raw_text AND its exact pre-fix
    match fields (5055 / "Xoài chín" / PRESET_ALIAS_MATCH / 0.98), reusing
    apply_thit_dui_kem_tomato_safe_fix._row_state_clear. It must be in
    exactly one of two states, "pending" or "already_applied"; any other
    observed state -- drifted raw_text, a different code, a partially-mutated
    row -- aborts the ENTIRE run before anything is written.
  - Each removed alias must currently map to its known old code, or already
    be absent (idempotent rerun); any other value aborts. Every alias outside
    the two targeted keys is verified byte-identical before and after, and
    the five preserved mango aliases are additionally pinned by exact value.
  - CLEAR writes nulls through the shared clear_row() helper, so the cleared
    row carries the same null semantics as every previously cleared row
    (null in JSON, empty field in CSV) and its weight, raw_text, cleaned_name
    and unit fields pass through untouched.
  - The 7 out-of-scope dangling-5074 rows are asserted to still number
    exactly 7 on every run, applied or not.

Scope: data/processed/viendinhduong/ingredient_alias_map.json and
data/processed/recipes/recipe_ingredients.{csv,json} plus the recipe-level
rollup totals and nutrition_status/missing_nutrition_count in
data/processed/recipes/recipes.{csv,json}. Canonical outputs
(canonical_recipes.csv/json, canonical_recipe_ingredients.csv/json,
recipe_canonical_mapping.csv) are intentionally NOT regenerated here, same as
all three prior safe fixes.
"""

import argparse
import json

from scripts.eda.apply_qwen_class_d_safe_fix import _recompute_status, write_csv
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
from scripts.eda.apply_thit_dui_kem_tomato_safe_fix import (
    ALIAS_PATH,
    OUT,
    DriftError,
    _alias_removal_state,
    _row_state_clear,
    read_alias_map,
    write_alias_map,
)

# --- Alias-map edits -------------------------------------------------------

# Reviewed 2026-09-13. Both are provable no-ops for matching (see module
# docstring); removing them deletes a false ripeness claim, not a behaviour.
ALIAS_REMOVALS = {
    "xoài bào sợi": "5055",
    "xoài chín tươi": "5055",
}

# Reviewed 2026-09-13 and explicitly kept. Pinned by exact value so that a
# later edit to any of them -- including a well-meant "cleanup" that removes
# the bare "xoài" alias this fix deliberately leaves in place -- fails closed
# here instead of silently changing what this remediation was reviewed against.
ALIAS_PRESERVED = {
    "xoài": "5055",
    "xoài chín": "5055",
    "xoài chín giòn": "5055",
    "trang trí xoài chín": "5055",
    "xoài đông lạnh": "5055",
}

assert not (set(ALIAS_REMOVALS) & set(ALIAS_PRESERVED))

# --- Row-level edit ---------------------------------------------------------

# Reviewed 2026-09-13. raw_text is re-checked at run time so an id whose row
# content has since changed fails closed instead of clearing the wrong thing.
CLEAR_ROW_ID = "3573cbc5-bbc0-430c-a7e1-af5f996174bb"
CLEAR_RAW_TEXT = "xoài bào sợi"
CLEAR_OLD_CODE = "5055"
CLEAR_OLD_NAME = "Xoài chín"

# Out-of-scope invariant: the dangling-code Qwen mango rows this fix must not
# touch. Tests targeting a smaller fixture world monkeypatch this so the drift
# guard tracks the fixture's actual size instead of re-implementing the check
# with a different hardcoded number.
DANGLING_CODE = "5074"
EXPECTED_DANGLING_COUNT = 7


def build_alias_plan(alias_map):
    """Read-only: classify both alias removals and pin the preserved five."""
    for key, expected in ALIAS_PRESERVED.items():
        if key not in alias_map:
            raise DriftError(f"preserved alias {key!r} is missing from {ALIAS_PATH}")
        if alias_map[key] != expected:
            raise DriftError(
                f"preserved alias {key!r} now maps to {alias_map[key]!r}, not {expected!r}"
            )
    return {
        key: _alias_removal_state(alias_map, key, old_code)
        for key, old_code in ALIAS_REMOVALS.items()
    }


def apply_alias_changes(alias_map, states):
    """Build the new alias map, touching only the two known keys."""
    new_map = dict(alias_map)
    for key in ALIAS_REMOVALS:
        if states[key] == "pending":
            del new_map[key]

    # Belt-and-suspenders: every key outside the two targeted ones -- the five
    # preserved mango aliases included -- must be byte-identical before/after.
    for key, value in alias_map.items():
        if key in ALIAS_REMOVALS:
            continue
        if new_map.get(key) != value:
            raise DriftError(f"unrelated alias {key!r} would be changed -- refusing to write")
    expected_removed = sum(1 for s in states.values() if s == "pending")
    if len(new_map) != len(alias_map) - expected_removed:
        raise DriftError("alias map size changed by more than the expected removals")
    return new_map


def build_plan():
    """Read-only: classify the alias edits and the single target row."""
    alias_map = read_alias_map()
    alias_states = build_alias_plan(alias_map)

    ing_rows = read_csv(ING)

    dangling = [r for r in ing_rows if (r.get("master_ingredient_code") or "").strip() == DANGLING_CODE]
    if len(dangling) != EXPECTED_DANGLING_COUNT:
        raise DriftError(
            f"expected {EXPECTED_DANGLING_COUNT} untouched rows on dangling code "
            f"{DANGLING_CODE!r}, found {len(dangling)}"
        )

    row = next((r for r in ing_rows if r["id"] == CLEAR_ROW_ID), None)
    if row is None:
        raise DriftError(f"CLEAR row {CLEAR_ROW_ID} not found in {ING}")
    row_state = _row_state_clear(row, CLEAR_RAW_TEXT, CLEAR_OLD_CODE, CLEAR_OLD_NAME)

    return alias_map, alias_states, row_state


def run(apply=False):
    alias_map, alias_states, row_state = build_plan()
    clear_now = row_state == "pending"

    ing_csv_rows = read_csv(ING)
    ing_json_rows = read_json(ING_JSON)

    def transform(row):
        if row["id"] == CLEAR_ROW_ID and clear_now:
            return clear_row(row)
        return row

    new_ing_csv_rows = [transform(r) for r in ing_csv_rows]
    ing_csv_fields = list(ing_csv_rows[0].keys())
    new_ing_json_rows = [transform(r) for r in ing_json_rows]

    rollups = recompute_recipe_rollups(new_ing_csv_rows)
    recipes_csv_rows = read_csv(RECIPES_CSV)
    recipes_csv_fields = list(recipes_csv_rows[0].keys())
    changed_totals = _apply_rollups(recipes_csv_rows, rollups)

    recipes_json_rows = read_json(RECIPES_JSON)
    _apply_rollups(recipes_json_rows, rollups)
    status_report = _recompute_status(recipes_json_rows, new_ing_json_rows)

    new_alias_map = apply_alias_changes(alias_map, alias_states)

    affected_recipe_id = next(
        (r["recipe_id"] for r in ing_csv_rows if r["id"] == CLEAR_ROW_ID), None
    )

    report = {
        "status": "applied" if apply else "preview",
        "alias_states": alias_states,
        "aliases_removed": sorted(k for k, s in alias_states.items() if s == "pending"),
        "aliases_preserved": sorted(ALIAS_PRESERVED),
        "alias_count_before": len(alias_map),
        "alias_count_after": len(new_alias_map),
        "clear_target_count": 1,
        "clear_applied_now": 1 if clear_now else 0,
        "clear_already_applied": 0 if clear_now else 1,
        "clear_row_id": CLEAR_ROW_ID,
        "affected_recipe_count": 1 if affected_recipe_id else 0,
        "affected_recipe_id": affected_recipe_id,
        "recipes_with_changed_totals": changed_totals,
        "recipes_with_changed_missing_count": status_report["recipes_with_changed_missing_count"],
        "recipes_with_status_label_changed": status_report["recipes_with_status_label_changed"],
        "status_transitions": status_report["status_transitions"],
        "dangling_5074_untouched": EXPECTED_DANGLING_COUNT,
        "bare_xoai_alias_note": (
            "The bare 'xoài' -> 5055 alias is deliberately NOT removed here. It is the root "
            "enabler of this defect, but 5 of its 6 rows are plausibly ripe and stranding them "
            "is out of this remediation's reviewed scope."
        ),
        "canonical_note": (
            "Canonical outputs (canonical_recipes.csv/json, canonical_recipe_ingredients.csv/json, "
            "recipe_canonical_mapping.csv) are NOT regenerated by this script and are now stale for "
            "this row/recipe. Regenerate via scripts/canonicalize_recipes.py after applying."
        ),
    }

    if apply:
        write_alias_map(new_alias_map)
        write_csv(ING, new_ing_csv_rows, ing_csv_fields)
        write_json(ING_JSON, new_ing_json_rows)
        write_csv(RECIPES_CSV, recipes_csv_rows, recipes_csv_fields)
        write_json(RECIPES_JSON, recipes_json_rows)
        OUT.mkdir(parents=True, exist_ok=True)
        (OUT / "applied_xoai_bao_soi_fix.json").write_text(
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
