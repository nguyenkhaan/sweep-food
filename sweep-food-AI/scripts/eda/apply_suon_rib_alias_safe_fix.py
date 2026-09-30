"""Apply the reviewed rib/bone (suon) PRESET_ALIAS contamination fix. Default previews; --apply writes.

Manual, recipe-level review found five rib/bone preset-alias entries in
data/processed/viendinhduong/ingredient_alias_map.json all resolving to
7069 ("Gio lua", a steamed minced-pork sausage) -- an identity unrelated to
pork rib. The catalog already carries the correct rib identity as
7053 ("Suon heo (xuong heo)" / "Pork, ribs, raw"), and several other rib/bone
aliases ("suon heo", "suon non", "xuong heo", "xuong lon", "xuong ong",
"suon than", "suon cong", "suo n non") already point there correctly.

Alias decisions (reviewed):

  REPOINT 7069 -> 7053, because each key is explicitly qualified as pork rib
  and is therefore globally safe:
    - "xuong suon heo"   (xuong suon heo)
    - "suon non heo"     (suon non heo)
    - "suo n non heo"    (a cleaned-name spelling variant already in the map)

  REMOVE entirely, because neither key is globally safe and no single catalog
  identity can carry them:
    - "suon"     -- spans pork rib, pork chop, beef rib and ambiguous uses
    - "de suon"  -- likewise not species-safe on its own

  No new broad "suon" alias is added. Bare "suon" rows are resolved
  individually below, on recipe-level evidence, never by a global rule.

LATENT REGRESSION THIS FIXES: the alias "suon non heo" already pointed at
7069, yet the 15 processed rows whose cleaned_name is "suon non heo" currently
sit correctly on 7053 (they predate the bad alias value). Regenerating
processed data BEFORE this alias fix would have regressed all 15 onto 7069.
The alias repoint removes that hazard; those 15 rows are not touched here and
must stay on 7053.

Row decisions for the 12 currently-contaminated rows (the only PRESET_ALIAS
rows sitting on 7069; the other 7 rows on 7069 are legitimate EXACT_CATALOG
"Gio lua" matches and are never touched):

  REMAP -> 7053, resolved by the three alias repoints above (6 rows):
    qualified "xuong suon heo" / "suon non heo" / "suo n non heo" usages.

  REMAP -> 7053, resolved by row-specific recipe evidence because their alias
  is being REMOVED (4 rows):
    - "300 g suon"   in "Canh cai thia nau suon non"        -- pork rib dish
    - "15 g suon"    in "Chao suon heo ca rot"              -- pork rib dish
    - "2 mieng Suon" in "Cot let chien nuoc mam"            -- pork chop/rib cut
      context; 7053 is the appropriate pork-rib catalog identity available in
      this dataset, so the row resolves there rather than being dropped.
    - "4 de suon"    in "De Suon Nuong Sot Thai - BBQ Pork Rib with Thai Sauce"
      -- the recipe title names Pork Rib explicitly.

  CLEAR -> UNMATCHED, because no valid catalog target exists (2 rows):
    - "3 lat suon" in "Thit chan gio chien nuoc mam" -- the ingredient identity
      is ambiguous relative to a pork-hock recipe; not force-resolved.
    - "Suon 1 kg" in "Suon bo ham mem" -- this is BEEF rib. There is no valid
      beef-rib catalog entry; it must NOT be mapped to pork 7053 nor to a beef
      shank/brisket code that names a different cut.

Expected outcome across the 12: 10 -> 7053, 2 -> UNMATCHED.

EXPLICITLY OUT OF SCOPE (left exactly as-is for a later audit, not a 70xx
cleanup): "suon cot let" -> 7070, "suon cot let xat lat" -> 7070,
"thit ba chi rut suon" -> 7082, "suon bo" -> 7094, "de suon bo" -> 7094,
"canh suon khoai so" -> 2013, and any other suspicious 70xx alias.

Safety model (fail closed, idempotent, dry-run by default):
  - Every target row is pinned by id AND exact raw_text AND its exact pre-fix
    match fields (7069 / "Gio lua" / PRESET_ALIAS_MATCH / 0.98). Before any
    mutation each row must be in exactly one of two states: "pending" (still
    carries the contaminated match) or "already_applied" (already carries this
    script's fixed-state fields). Any other observed state aborts the ENTIRE
    run before anything is written.
  - The alias edits are pinned the same way: each must currently hold 7069, or
    already be in its post-fix state (repointed to 7053 / absent). Any other
    observed value aborts before any file is written. Every other alias entry
    is verified byte-identical before and after.
  - REMAP validates that 7053 exists in the live catalog under the exact
    expected name before use, via the same identity check
    nlp.matching_integrity.stage_qwen_update enforces for the Qwen pipeline.
    Nutrition is computed by that function from the catalog + the row's own
    current weight -- never typed by hand. 7053 has no carbs_g value, so
    remapped rows carry a null (not zero) carbs_g, per the nullable-nutrition
    contract in nlp.nutrition.
  - Rows/aliases already in "already_applied" state are left byte-identical
    (idempotent reruns produce no diff and no error).

REGENERATION NOTE: the 6 alias-driven remaps are reproducible by re-running
the matcher after this fix. The 4 row-level remaps and 2 clears are NOT --
they are reviewed, row-specific overrides that exist precisely because no safe
global alias covers bare "suon"/"de suon". A future full re-match from raw
text will leave those 6 rows UNMATCHED unless the decisions are re-applied.

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
OUT = ROOT / "reports/eda/suon_rib_alias_fix"

PRESET_ALIAS_METHOD = "PRESET_ALIAS_MATCH"
PRESET_ALIAS_CONFIDENCE = "0.98"

# The contaminated identity every target alias and row currently carries.
OLD_CODE = "7069"
OLD_NAME = "Giò lụa"

# The correct pork-rib identity.
NEW_CODE = "7053"
NEW_NAME = "Sườn heo (xương heo)"

# --- Alias-map edits -------------------------------------------------------

# Qualified pork-rib keys: safe to repoint globally.
ALIAS_REPOINTS = ("xương sườn heo", "sườn non heo", "sươ n non heo")

# Unqualified keys: no safe global target, removed outright.
ALIAS_REMOVALS = ("sườn", "dẻ sườn")

# Correct rib/bone aliases that must survive this fix untouched. Asserted
# before writing so a future edit to this script cannot quietly disturb them.
ALIAS_MUST_REMAIN_7053 = (
    "sườn heo", "sườn non", "xương heo", "xương lợn", "xương ống",
    "sườn thăn", "sườn cọng", "sươ n non",
)

assert not set(ALIAS_REPOINTS) & set(ALIAS_REMOVALS)
assert not set(ALIAS_MUST_REMAIN_7053) & (set(ALIAS_REPOINTS) | set(ALIAS_REMOVALS))

# --- Row-level edits --------------------------------------------------------

# Six rows whose correction follows directly from the three alias repoints.
REMAP_ALIAS_DRIVEN_ROWS = (
    ("a56ffa1e-1225-4c4e-a830-0b756eab2c81", "400 gr xương / sườn heo"),
    ("25f14bf1-192c-41f4-9d1b-dc0006e7084c", "500g xương sườn heo"),
    ("0f84cccc-deac-4bf9-9fd8-a879d66bd1aa", "Xương sườn heo 1 kg"),
    ("d1400f26-18dc-4e96-8acd-78267045f499", "Xương sườn heo 400 gr"),
    ("5fbe1cf4-3c16-45d9-a999-c7345dde881c", "Xương sườn heo 8 miếng"),
    # This row's raw_text is NOT NFC-normalized: it holds "sươ" + a combining
    # grave accent (U+0300) + "n" rather than the precomposed "ườ" (U+1EDD).
    # It renders identically to "500 gr sườn non heo" but is a different byte
    # sequence, and it is the reason this row's cleaned_name came out as
    # "sươ n non heo" (with a space) -- the cleaner dropped the combining mark
    # and left a gap, which is in turn why the alias map carries that odd key.
    # Pinned as explicit escapes so the literal cannot be silently re-normalized
    # by an editor and quietly stop matching (the raw_text guard is fail-closed,
    # so a re-normalized literal would abort the run rather than mis-edit).
    ("dfd609c0-7829-4da0-8821-34fbeb960500", "500 gr s\u01b0\u01a1\u0300n non heo"),
)

# Four rows whose alias is being removed but whose recipe context resolves
# them to pork rib on review.
REMAP_ROW_LEVEL_ROWS = (
    ("36db3701-6ae4-4720-9d4c-c6d8d533decf", "300 g sườn"),
    ("1da91cd2-565a-4467-8f54-bd480ab7294a", "15 g sườn"),
    ("19504d22-3999-4ae0-bca7-db81df889ad5", "2 miếng Sườn"),
    ("ac206911-216e-4742-adfa-a7bd9d199e58", "4 dẻ sườn"),
)

REMAP_ROWS = REMAP_ALIAS_DRIVEN_ROWS + REMAP_ROW_LEVEL_ROWS

# Two rows with no valid catalog target.
CLEAR_ROWS = (
    ("c9c53624-3d09-4680-9bed-fc9590d5b8ad", "3 lát sườn"),
    ("78e45baf-dd51-4f0e-8d7a-ba4cee3612e2", "Sườn 1 kg"),
)

# The beef-rib row must never be resolved to pork rib, nor to the beef codes an
# over-eager "just pick something beefy" fix would reach for (7094 Thit bap bo,
# 7006 beef brisket/nam, 7061 beef bone).
BEEF_RIB_ROW_ID = "78e45baf-dd51-4f0e-8d7a-ba4cee3612e2"
BEEF_RIB_FORBIDDEN_CODES = ("7053", "7094", "7006", "7061")

assert len(REMAP_ROWS) == 10
assert len(CLEAR_ROWS) == 2
TARGET_IDS = frozenset([rid for rid, _ in REMAP_ROWS] + [rid for rid, _ in CLEAR_ROWS])
assert len(TARGET_IDS) == 12
assert BEEF_RIB_ROW_ID in {rid for rid, _ in CLEAR_ROWS}

REPORT_ROW_FIELDS = (
    "master_ingredient_code", "master_ingredient_name", "match_method",
    "match_confidence", "calories", "protein_g", "fat_g", "carbs_g",
)


class DriftError(ValueError):
    """A reviewed target (alias or row) no longer matches its expected pre/post state."""


def read_alias_map():
    return json.loads(ALIAS_PATH.read_text(encoding="utf-8"))


def write_alias_map(alias_map):
    ALIAS_PATH.write_text(
        json.dumps(alias_map, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


def _alias_repoint_state(alias_map, key):
    if key not in alias_map:
        raise DriftError(f"alias {key!r} is missing entirely from {ALIAS_PATH}")
    value = alias_map[key]
    if value == OLD_CODE:
        return "pending"
    if value == NEW_CODE:
        return "already_applied"
    raise DriftError(
        f"alias {key!r} has unexpected value {value!r} (expected {OLD_CODE!r} or {NEW_CODE!r})"
    )


def _alias_removal_state(alias_map, key):
    if key not in alias_map:
        return "already_applied"
    if alias_map[key] == OLD_CODE:
        return "pending"
    raise DriftError(
        f"alias {key!r} has unexpected value {alias_map[key]!r} (expected {OLD_CODE!r} or absent)"
    )


def build_alias_plan(alias_map):
    """Read-only: classify each of the 5 alias edits, fail closed on drift."""
    states = {key: _alias_repoint_state(alias_map, key) for key in ALIAS_REPOINTS}
    states.update({key: _alias_removal_state(alias_map, key) for key in ALIAS_REMOVALS})
    return states


def apply_alias_changes(alias_map, states):
    """Build the new alias map, touching only the 5 known keys."""
    new_map = dict(alias_map)
    for key in ALIAS_REPOINTS:
        if states[key] == "pending":
            new_map[key] = NEW_CODE
    for key in ALIAS_REMOVALS:
        if states[key] == "pending":
            del new_map[key]

    # Belt-and-suspenders: every key outside the 5 targeted ones must be
    # byte-identical between old and new maps.
    touched = set(ALIAS_REPOINTS) | set(ALIAS_REMOVALS)
    for key, value in alias_map.items():
        if key in touched:
            continue
        if new_map.get(key) != value:
            raise DriftError(f"unrelated alias {key!r} would be changed -- refusing to write")
    if not len(alias_map) - len(ALIAS_REMOVALS) <= len(new_map) <= len(alias_map):
        raise DriftError("alias map size changed by more than the 2 expected removals")

    # The already-correct rib/bone aliases must be untouched and still on 7053.
    for key in ALIAS_MUST_REMAIN_7053:
        if key in alias_map and new_map.get(key) != alias_map[key]:
            raise DriftError(f"correct rib alias {key!r} would be changed -- refusing to write")

    # No reviewed rib key may be left pointing at the contaminated code.
    for key in touched:
        if new_map.get(key) == OLD_CODE:
            raise DriftError(f"alias {key!r} would still point at {OLD_CODE} -- refusing to write")
    return new_map


def _pending_probe(row):
    code = (row.get("master_ingredient_code") or "").strip()
    name = (row.get("master_ingredient_name") or "").strip()
    return (
        code == OLD_CODE
        and name == OLD_NAME
        and row.get("match_method") == PRESET_ALIAS_METHOD
        and (row.get("match_confidence") or "").strip() == PRESET_ALIAS_CONFIDENCE
    )


def _remap_applied_probe(row):
    code = (row.get("master_ingredient_code") or "").strip()
    name = (row.get("master_ingredient_name") or "").strip()
    return (
        code == NEW_CODE
        and name == NEW_NAME
        and row.get("match_method") == PRESET_ALIAS_METHOD
        and (row.get("match_confidence") or "").strip() == PRESET_ALIAS_CONFIDENCE
    )


def _clear_applied_probe(row):
    code = row.get("master_ingredient_code")
    name = row.get("master_ingredient_name")
    conf = row.get("match_confidence")
    return (
        (code is None or str(code).strip() == "")
        and (name is None or str(name).strip() == "")
        and row.get("match_method") == "UNMATCHED"
        and (conf is None or str(conf).strip() == "")
        and all(
            row.get(f) is None or str(row.get(f)).strip() == ""
            for f in ("calories", "protein_g", "fat_g", "carbs_g")
        )
    )


def _row_state(row, raw_text, applied_probe, applied_label):
    rid = row.get("id")
    if row.get("raw_text") != raw_text:
        raise DriftError(
            f"row {rid}: raw_text drifted (expected {raw_text!r}, found {row.get('raw_text')!r})"
        )
    if _pending_probe(row):
        return "pending"
    if applied_probe(row):
        return "already_applied"
    raise DriftError(
        f"row {rid}: neither pending ({OLD_CODE}/{OLD_NAME!r}) nor {applied_label} state matched "
        f"(found code={row.get('master_ingredient_code')!r} name={row.get('master_ingredient_name')!r} "
        f"method={row.get('match_method')!r} confidence={row.get('match_confidence')!r})"
    )


def build_plan():
    """Read-only: locate the 5 alias edits and 12 target rows, classify each."""
    alias_map = read_alias_map()
    alias_states = build_alias_plan(alias_map)

    masters = {r["code"]: r for r in read_csv(MASTER)}
    if NEW_CODE not in masters:
        raise DriftError(f"remap target code {NEW_CODE!r} is absent from the current catalog")
    if masters[NEW_CODE].get("name_vi", "").strip() != NEW_NAME:
        raise DriftError(
            f"remap target code {NEW_CODE!r} now names "
            f"{masters[NEW_CODE].get('name_vi')!r}, not {NEW_NAME!r}"
        )

    ing_rows = read_csv(ING)
    by_id = {r["id"]: r for r in ing_rows}

    row_states = {}
    for rid, raw_text in REMAP_ROWS:
        row = by_id.get(rid)
        if row is None:
            raise DriftError(f"REMAP row {rid} not found in {ING}")
        row_states[rid] = _row_state(row, raw_text, _remap_applied_probe, "already-remapped")

    for rid, raw_text in CLEAR_ROWS:
        row = by_id.get(rid)
        if row is None:
            raise DriftError(f"CLEAR row {rid} not found in {ING}")
        row_states[rid] = _row_state(row, raw_text, _clear_applied_probe, "already-cleared")

    return alias_map, alias_states, masters, row_states


def _apply_remap(row, masters):
    match_fields = {
        "master_ingredient_code": NEW_CODE,
        "master_ingredient_name": NEW_NAME,
        "match_method": PRESET_ALIAS_METHOD,
        "match_confidence": PRESET_ALIAS_CONFIDENCE,
    }
    weight = nutrition_value(row.get("estimated_weight_g")) or 0.0
    updates = stage_qwen_update(row, masters, weight, match_fields=match_fields)
    new_row = dict(row)
    new_row.update(updates)
    return new_row


def _nutrition_totals(rows):
    """Sum the four nutrition fields, treating null (unknown) as absent, not zero."""
    totals = {"calories": 0.0, "protein_g": 0.0, "fat_g": 0.0, "carbs_g": 0.0}
    for row in rows:
        for field in totals:
            value = nutrition_value(row.get(field))
            if value is not None:
                totals[field] += value
    return {k: round(v, 1) for k, v in totals.items()}


def run(apply=False):
    alias_map, alias_states, masters, row_states = build_plan()

    remap_ids = {rid for rid, _ in REMAP_ROWS}
    clear_ids = {rid for rid, _ in CLEAR_ROWS}
    remap_now = {rid for rid in remap_ids if row_states[rid] == "pending"}
    clear_now = {rid for rid in clear_ids if row_states[rid] == "pending"}

    ing_csv_rows = read_csv(ING)
    ing_json_rows = read_json(ING_JSON)

    def transform(row):
        rid = row["id"]
        if row_states.get(rid) != "pending":
            return row
        if rid in remap_ids:
            return _apply_remap(row, masters)
        if rid in clear_ids:
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

    before_by_id = {r["id"]: r for r in ing_csv_rows if r["id"] in TARGET_IDS}
    after_by_id = {r["id"]: r for r in new_ing_csv_rows if r["id"] in TARGET_IDS}

    # Post-transform guard: the beef-rib row must be UNMATCHED, never on a
    # pork or substitute-beef code, whatever path produced its final state.
    beef_row = after_by_id[BEEF_RIB_ROW_ID]
    beef_code = (beef_row.get("master_ingredient_code") or "").strip()
    if beef_code in BEEF_RIB_FORBIDDEN_CODES or beef_row.get("match_method") != "UNMATCHED":
        raise DriftError(
            f"beef-rib row {BEEF_RIB_ROW_ID} resolved to {beef_code!r}/"
            f"{beef_row.get('match_method')!r} -- refusing to write"
        )

    nutrition_before = _nutrition_totals(before_by_id.values())
    nutrition_after = _nutrition_totals(after_by_id.values())
    remap_before = _nutrition_totals(before_by_id[rid] for rid in remap_ids)
    remap_after = _nutrition_totals(after_by_id[rid] for rid in remap_ids)
    clear_before = _nutrition_totals(before_by_id[rid] for rid in clear_ids)
    clear_after = _nutrition_totals(after_by_id[rid] for rid in clear_ids)
    affected_recipe_ids = {r["recipe_id"] for r in ing_csv_rows if r["id"] in TARGET_IDS}

    def _delta(before, after):
        return {k: round(after[k] - before[k], 1) for k in before}

    report = {
        "status": "applied" if apply else "preview",
        "alias_states": alias_states,
        "alias_repoints": {k: NEW_CODE for k in ALIAS_REPOINTS},
        "alias_removals": list(ALIAS_REMOVALS),
        "remap_target_count": len(remap_ids),
        "remap_applied_now": len(remap_now),
        "remap_already_applied": len(remap_ids) - len(remap_now),
        "remap_alias_driven_count": len(REMAP_ALIAS_DRIVEN_ROWS),
        "remap_row_level_count": len(REMAP_ROW_LEVEL_ROWS),
        "clear_target_count": len(clear_ids),
        "clear_applied_now": len(clear_now),
        "clear_already_applied": len(clear_ids) - len(clear_now),
        "affected_recipe_count": len(affected_recipe_ids),
        "affected_recipe_ids": sorted(affected_recipe_ids),
        "recipes_with_changed_totals": changed_totals,
        "recipes_with_changed_missing_count": status_report["recipes_with_changed_missing_count"],
        "recipes_with_status_label_changed": status_report["recipes_with_status_label_changed"],
        "status_transitions": status_report["status_transitions"],
        "nutrition_all_12": {
            "before": nutrition_before,
            "after": nutrition_after,
            "delta": _delta(nutrition_before, nutrition_after),
        },
        "nutrition_remapped_10": {
            "before": remap_before,
            "after": remap_after,
            "delta": _delta(remap_before, remap_after),
        },
        "nutrition_cleared_2": {
            "before": clear_before,
            "after": clear_after,
            "delta": _delta(clear_before, clear_after),
        },
        "remap_row_ids": sorted(remap_ids),
        "clear_row_ids": sorted(clear_ids),
        "row_outcomes": {
            rid: {
                "raw_text": before_by_id[rid].get("raw_text"),
                "cleaned_name": before_by_id[rid].get("cleaned_name"),
                "recipe_id": before_by_id[rid].get("recipe_id"),
                "estimated_weight_g": after_by_id[rid].get("estimated_weight_g"),
                "decision": "REMAP_7053" if rid in remap_ids else "CLEAR_UNMATCHED",
                "before": {f: before_by_id[rid].get(f) for f in REPORT_ROW_FIELDS},
                "after": {f: after_by_id[rid].get(f) for f in REPORT_ROW_FIELDS},
            }
            for rid in sorted(TARGET_IDS)
        },
        "out_of_scope_note": (
            "Other suspicious 70xx rib aliases are intentionally NOT touched: "
            "'suon cot let'->7070, 'suon cot let xat lat'->7070, 'thit ba chi rut suon'->7082, "
            "'suon bo'->7094, 'de suon bo'->7094, 'canh suon khoai so'->2013. This fix is scoped "
            "to the five reviewed keys only and is not a 70xx cleanup."
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
    print(json.dumps(
        {k: v for k, v in report.items() if k not in ("remap_row_ids", "clear_row_ids", "row_outcomes")},
        ensure_ascii=False, indent=2,
    ))


if __name__ == "__main__":
    main()
