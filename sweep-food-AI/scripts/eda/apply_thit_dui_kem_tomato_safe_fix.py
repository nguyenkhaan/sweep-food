"""Apply the reviewed thit-dui/kem/tomato alias remediation. Default previews; --apply writes.

Manual, recipe-level review (see reports/eda -- not fuzzy string matching) found
three unsafe preset-alias entries in data/processed/viendinhduong/ingredient_alias_map.json
and resolved their currently-affected recipe_ingredients rows:

  - "thit dui" -> 7080 ("Ech (thit dui)", frog leg meat). All 4 rows using this
    alias are pork dishes ("Thit heo ..."); no candidate current catalog code
    (7032 Chan gio heo, 7084 Thit nac mong heo, 7088 Dui ga) is an exact
    deterministic identity for generic "thit dui" -- 7032/7084 name different
    cuts, 7088 is the wrong species. The alias is REMOVED (not repointed to a
    guessed pork code) and its 4 rows are CLEARED to UNMATCHED.
  - "kem" (bare) -> 12073 ("Kem ngo", corn ice cream). The one row using this
    alias ("Kem 120 ml" in "Sup kem nam beo ngay", a savory cream-of-mushroom
    soup) is confirmed by row-specific evidence (recipe title, a sibling "Kem
    sua tuoi 200 ml" ingredient in the same recipe, and 20070's fat-dominant
    nutrition profile matching the dish's "beo ngay"/rich description) to mean
    dairy cream, not ice cream. The alias is REMOVED (bare "kem" remains
    ambiguous across the corpus and must not resolve to any single global
    code) and only that one row is REMAPped to 20070 ("Whipping cream").
  - "tuong ca chua kechup" -> 4005 ("Ca chua", raw tomato). The raw text
    explicitly names "Kechup"; 13032 ("Nuoc sot ca chua (tuong ca)") already
    holds the synonymous "ketchup"/"tuong ca" aliases and its own nutrition
    (21.27g sugar, 907mg sodium /100g) confirms it is the bottled-ketchup
    identity. The alias is CHANGED to 13032 and its 1 affected row REMAPped
    to match.

The other 7 tomato aliases flagged in the same review ("ca chua co dac",
"sot ca chua dam dac", "ca chua paste", "sot ca chua co dac", "xot ca chua
hop", "ca chua hop", "ca chua xay dong") and their 15 rows are explicitly OUT
OF SCOPE here: 13032 is a sugary/salty ketchup identity, not a safe target for
tomato paste/concentrate or plain canned tomato, and no dedicated catalog
code exists yet for either. They are left untouched pending a real catalog
fix. The dormant duplicate catalog pair 12079/20070 ("Kem tuoi") is also out
of scope and is not touched.

Safety model (fail closed, idempotent, dry-run by default):
  - Every target row is pinned by id AND exact raw_text AND its exact
    pre-fix match fields (code, name, method, confidence). Before any
    mutation, each row must be in exactly one of two states: "pending"
    (still carries the original alias-era match) or "already_applied"
    (already carries this script's fixed-state fields). Any other observed
    state aborts the ENTIRE run before anything is written.
  - The alias-map edits are pinned the same way: each removed alias must
    currently map to its known old code (or already be absent -- idempotent
    rerun); the changed alias must currently be "4005" (or already be
    "13032"); any other observed value aborts before any file is written.
    Every other alias entry is verified byte-identical before and after.
  - REMAP validates the target code (20070 / 13032) exists in the live
    catalog under the exact expected name before use, via the same identity
    check nlp/matching_integrity.stage_qwen_update already enforces for the
    Qwen pipeline. Nutrition is computed by that function from the catalog +
    the row's own current weight -- never typed by hand.
  - Rows/aliases already in "already_applied" state are left byte-identical
    (idempotent reruns produce no diff and no error).
  - Only the 3 named aliases and 6 named rows are touched. Every other alias
    and row -- including the 15 unresolved tomato rows and the qualified
    cream/frog aliases -- passes through unchanged; recipe rollups/status are
    recomputed for all recipes but only actually change where the underlying
    ingredient rows changed.

Scope: data/processed/viendinhduong/ingredient_alias_map.json and
data/processed/recipes/recipe_ingredients.{csv,json} plus the recipe-level
rollup totals and nutrition_status/missing_nutrition_count in
data/processed/recipes/recipes.{csv,json}. Canonical outputs
(data/processed/recipes/canonical_*.csv/json, recipe_canonical_mapping.csv)
are intentionally NOT regenerated here -- regenerate them separately via
scripts/canonicalize_recipes.py after this fix is applied.
"""

import argparse
import json
from pathlib import Path

from nlp.matching_integrity import stage_qwen_update
from nlp.nutrition import nutrition_value
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

ROOT = Path(__file__).resolve().parents[2]
ALIAS_PATH = ROOT / "data/processed/viendinhduong/ingredient_alias_map.json"
MASTER = ROOT / "data/processed/viendinhduong/master_ingredients_nutrition.csv"
OUT = ROOT / "reports/eda/alias_semantics_fix"

PRESET_ALIAS_METHOD = "PRESET_ALIAS_MATCH"
PRESET_ALIAS_CONFIDENCE = "0.98"

# --- Alias-map edits -------------------------------------------------------

ALIAS_REMOVALS = {
    "thịt đùi": "7080",
    "kem": "12073",
}

ALIAS_CHANGE_KEY = "tương cà chua kechup"
ALIAS_CHANGE_OLD = "4005"
ALIAS_CHANGE_NEW = "13032"

# --- Row-level edits --------------------------------------------------------

CLEAR_OLD_CODE = "7080"
CLEAR_OLD_NAME = "Ếch (thịt đùi)"
CLEAR_ROWS = (
    ("f1a86141-bc44-4f2e-af1c-40a1909ccbc2", "300 g thịt đùi"),
    ("6df8e7d2-375c-4af1-b201-d8f6041a0eaf", "1 kg thịt đùi"),
    ("939dfb42-acb1-4c3c-af04-c7c815a3e334", "500 g thịt đùi"),
    ("003dfd59-f0cd-4aef-8bf8-9cd470170d82", "300 gr thịt đùi (hoặc ba rọi):"),
)
assert len(CLEAR_ROWS) == 4
assert len({rid for rid, _ in CLEAR_ROWS}) == 4

KEM_REMAP_ROW_ID = "a0e558a7-4ae8-4b7f-8df4-546a64cb7abd"
KEM_REMAP_RAW_TEXT = "Kem 120 ml"
KEM_REMAP_OLD_CODE = "12073"
KEM_REMAP_OLD_NAME = "Kem ngô"
KEM_REMAP_NEW_CODE = "20070"
KEM_REMAP_NEW_NAME = "Whipping cream (Kem tươi whipping)"

KETCHUP_REMAP_ROW_ID = "21e91dd0-9b1c-4b60-a980-897f26d1afb1"
KETCHUP_REMAP_RAW_TEXT = "Tương cà chua Kechup 2 muỗng canh"
KETCHUP_REMAP_OLD_CODE = "4005"
KETCHUP_REMAP_OLD_NAME = "Cà chua"
KETCHUP_REMAP_NEW_CODE = "13032"
KETCHUP_REMAP_NEW_NAME = "Nước sốt cà chua (tương cà)"

REMAPS = (
    (KEM_REMAP_ROW_ID, KEM_REMAP_RAW_TEXT, KEM_REMAP_OLD_CODE, KEM_REMAP_OLD_NAME,
     KEM_REMAP_NEW_CODE, KEM_REMAP_NEW_NAME),
    (KETCHUP_REMAP_ROW_ID, KETCHUP_REMAP_RAW_TEXT, KETCHUP_REMAP_OLD_CODE, KETCHUP_REMAP_OLD_NAME,
     KETCHUP_REMAP_NEW_CODE, KETCHUP_REMAP_NEW_NAME),
)

TARGET_IDS = frozenset([rid for rid, _ in CLEAR_ROWS] + [rid for rid, *_ in REMAPS])


class DriftError(ValueError):
    """A reviewed target (alias or row) no longer matches its expected pre/post state."""


def read_alias_map():
    return json.loads(ALIAS_PATH.read_text(encoding="utf-8"))


def write_alias_map(alias_map):
    ALIAS_PATH.write_text(
        json.dumps(alias_map, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


def _alias_removal_state(alias_map, key, old_code):
    if key not in alias_map:
        return "already_applied"
    if alias_map[key] == old_code:
        return "pending"
    raise DriftError(f"alias {key!r} has unexpected value {alias_map[key]!r} (expected {old_code!r} or absent)")


def _alias_change_state(alias_map):
    if ALIAS_CHANGE_KEY not in alias_map:
        raise DriftError(f"alias {ALIAS_CHANGE_KEY!r} is missing entirely from {ALIAS_PATH}")
    value = alias_map[ALIAS_CHANGE_KEY]
    if value == ALIAS_CHANGE_OLD:
        return "pending"
    if value == ALIAS_CHANGE_NEW:
        return "already_applied"
    raise DriftError(
        f"alias {ALIAS_CHANGE_KEY!r} has unexpected value {value!r} "
        f"(expected {ALIAS_CHANGE_OLD!r} or {ALIAS_CHANGE_NEW!r})"
    )


def build_alias_plan(alias_map):
    """Read-only: classify each of the 3 alias edits, fail closed on drift."""
    states = {key: _alias_removal_state(alias_map, key, old_code) for key, old_code in ALIAS_REMOVALS.items()}
    states[ALIAS_CHANGE_KEY] = _alias_change_state(alias_map)
    return states


def apply_alias_changes(alias_map, states):
    """Build the new alias map, touching only the 3 known keys."""
    new_map = dict(alias_map)
    for key in ALIAS_REMOVALS:
        if states[key] == "pending":
            del new_map[key]
    if states[ALIAS_CHANGE_KEY] == "pending":
        new_map[ALIAS_CHANGE_KEY] = ALIAS_CHANGE_NEW

    # Belt-and-suspenders: every key outside the 3 targeted ones must be
    # byte-identical between old and new maps.
    touched = set(ALIAS_REMOVALS) | {ALIAS_CHANGE_KEY}
    for key, value in alias_map.items():
        if key in touched:
            continue
        if new_map.get(key) != value:
            raise DriftError(f"unrelated alias {key!r} would be changed -- refusing to write")
    if len(new_map) not in (len(alias_map), len(alias_map) - 1, len(alias_map) - 2):
        raise DriftError("alias map size changed by more than the 2 expected removals")
    return new_map


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


def _pending_probe(row, old_code, old_name):
    code = (row.get("master_ingredient_code") or "").strip()
    name = (row.get("master_ingredient_name") or "").strip()
    return (
        code == old_code
        and name == old_name
        and row.get("match_method") == PRESET_ALIAS_METHOD
        and (row.get("match_confidence") or "").strip() == PRESET_ALIAS_CONFIDENCE
    )


def _remap_applied_probe(row, new_code, new_name):
    code = (row.get("master_ingredient_code") or "").strip()
    name = (row.get("master_ingredient_name") or "").strip()
    return (
        code == new_code
        and name == new_name
        and row.get("match_method") == PRESET_ALIAS_METHOD
        and (row.get("match_confidence") or "").strip() == PRESET_ALIAS_CONFIDENCE
    )


def _row_state_clear(row, raw_text, old_code, old_name):
    rid = row.get("id")
    if row.get("raw_text") != raw_text:
        raise DriftError(f"row {rid}: raw_text drifted (expected {raw_text!r}, found {row.get('raw_text')!r})")
    if _pending_probe(row, old_code, old_name):
        return "pending"
    if _clear_applied_probe(row):
        return "already_applied"
    raise DriftError(
        f"row {rid}: neither pending ({old_code!r}/{old_name!r}) nor already-cleared state matched "
        f"(found code={row.get('master_ingredient_code')!r} name={row.get('master_ingredient_name')!r} "
        f"method={row.get('match_method')!r})"
    )


def _row_state_remap(row, raw_text, old_code, old_name, new_code, new_name):
    rid = row.get("id")
    if row.get("raw_text") != raw_text:
        raise DriftError(f"row {rid}: raw_text drifted (expected {raw_text!r}, found {row.get('raw_text')!r})")
    if _pending_probe(row, old_code, old_name):
        return "pending"
    if _remap_applied_probe(row, new_code, new_name):
        return "already_applied"
    raise DriftError(
        f"row {rid}: neither pending ({old_code!r}/{old_name!r}) nor already-remapped "
        f"({new_code!r}/{new_name!r}) state matched "
        f"(found code={row.get('master_ingredient_code')!r} name={row.get('master_ingredient_name')!r} "
        f"method={row.get('match_method')!r})"
    )


def build_plan():
    """Read-only: locate the alias edits and 6 target rows, classify each."""
    alias_map = read_alias_map()
    alias_states = build_alias_plan(alias_map)

    masters = {r["code"]: r for r in read_csv(MASTER)}
    for new_code, new_name in ((KEM_REMAP_NEW_CODE, KEM_REMAP_NEW_NAME), (KETCHUP_REMAP_NEW_CODE, KETCHUP_REMAP_NEW_NAME)):
        if new_code not in masters:
            raise DriftError(f"remap target code {new_code!r} is absent from the current catalog")
        if masters[new_code].get("name_vi", "").strip() != new_name:
            raise DriftError(
                f"remap target code {new_code!r} now names {masters[new_code].get('name_vi')!r}, not {new_name!r}"
            )

    ing_rows = read_csv(ING)
    by_id = {r["id"]: r for r in ing_rows}

    row_states = {}
    for rid, raw_text in CLEAR_ROWS:
        row = by_id.get(rid)
        if row is None:
            raise DriftError(f"CLEAR row {rid} not found in {ING}")
        row_states[rid] = _row_state_clear(row, raw_text, CLEAR_OLD_CODE, CLEAR_OLD_NAME)

    for rid, raw_text, old_code, old_name, new_code, new_name in REMAPS:
        row = by_id.get(rid)
        if row is None:
            raise DriftError(f"REMAP row {rid} not found in {ING}")
        row_states[rid] = _row_state_remap(row, raw_text, old_code, old_name, new_code, new_name)

    return alias_map, alias_states, masters, row_states


def _apply_clear(row):
    return clear_row(row)


def _apply_remap(row, masters, new_code, new_name):
    match_fields = {
        "master_ingredient_code": new_code,
        "master_ingredient_name": new_name,
        "match_method": PRESET_ALIAS_METHOD,
        "match_confidence": PRESET_ALIAS_CONFIDENCE,
    }
    weight = nutrition_value(row.get("estimated_weight_g")) or 0.0
    updates = stage_qwen_update(row, masters, weight, match_fields=match_fields)
    new_row = dict(row)
    new_row.update(updates)
    return new_row


def run(apply=False):
    alias_map, alias_states, masters, row_states = build_plan()

    clear_ids = {rid for rid, _ in CLEAR_ROWS}
    clear_now = {rid for rid in clear_ids if row_states[rid] == "pending"}
    remap_specs = {rid: (new_code, new_name) for rid, _, _, _, new_code, new_name in REMAPS}
    remap_now = {rid for rid in remap_specs if row_states[rid] == "pending"}

    ing_csv_rows = read_csv(ING)
    ing_json_rows = read_json(ING_JSON)

    def transform(row):
        rid = row["id"]
        if rid in clear_ids and row_states[rid] == "pending":
            return _apply_clear(row)
        if rid in remap_specs and row_states[rid] == "pending":
            new_code, new_name = remap_specs[rid]
            return _apply_remap(row, masters, new_code, new_name)
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

    clear_recipe_ids = {r["recipe_id"] for r in ing_csv_rows if r["id"] in clear_ids}
    remap_recipe_ids = {r["recipe_id"] for r in ing_csv_rows if r["id"] in remap_specs}
    affected_recipe_ids = clear_recipe_ids | remap_recipe_ids

    report = {
        "status": "applied" if apply else "preview",
        "alias_states": alias_states,
        "clear_target_count": len(clear_ids),
        "clear_applied_now": len(clear_now),
        "clear_already_applied": len(clear_ids) - len(clear_now),
        "remap_target_count": len(remap_specs),
        "remap_applied_now": len(remap_now),
        "remap_already_applied": len(remap_specs) - len(remap_now),
        "affected_recipe_count": len(affected_recipe_ids),
        "affected_recipe_ids": sorted(affected_recipe_ids),
        "recipes_with_changed_totals": changed_totals,
        "recipes_with_changed_missing_count": status_report["recipes_with_changed_missing_count"],
        "recipes_with_status_label_changed": status_report["recipes_with_status_label_changed"],
        "status_transitions": status_report["status_transitions"],
        "clear_row_ids": sorted(clear_ids),
        "remap_row_ids": sorted(remap_specs),
        "unresolved_tomato_note": (
            "The other 7 tomato aliases (ca chua co dac, sot ca chua dam dac, ca chua paste, "
            "sot ca chua co dac, xot ca chua hop, ca chua hop, ca chua xay dong) and their 15 rows "
            "are intentionally NOT touched by this script -- 13032 is a ketchup identity, unsafe "
            "for paste/canned-tomato meanings; they remain on code 4005 pending a real catalog fix."
        ),
        "canonical_note": (
            "Canonical outputs (canonical_recipes.csv/json, canonical_recipe_ingredients.csv/json, "
            "recipe_canonical_mapping.csv) are NOT regenerated by this script and are now stale for "
            "these rows/recipes. Regenerate via scripts/canonicalize_recipes.py after applying."
        ),
    }

    if apply:
        write_alias_map(new_alias_map)
        write_csv(ING, new_ing_csv_rows, ing_csv_fields)
        write_json(ING_JSON, new_ing_json_rows)
        write_csv(RECIPES_CSV, recipes_csv_rows, recipes_csv_fields)
        write_json(RECIPES_JSON, recipes_json_rows)
        OUT.mkdir(parents=True, exist_ok=True)
        (OUT / "applied_fix.json").write_text(
            json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )

    return report


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args(argv)
    report = run(apply=args.apply)
    print(json.dumps({k: v for k, v in report.items() if k not in ("clear_row_ids", "remap_row_ids")},
                      ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
