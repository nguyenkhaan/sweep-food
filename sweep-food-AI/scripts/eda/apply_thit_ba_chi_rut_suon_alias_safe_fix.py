"""Apply the reviewed "thịt ba chỉ rút sườn" PRESET_ALIAS fix (Batch B of the
70xx meat-band audit). Default previews; --apply writes.

The 70xx meat-band audit found a single corrupted preset alias in
data/processed/viendinhduong/ingredient_alias_map.json:

    "thịt ba chỉ rút sườn" -> 7082 ("Lòng gà (cả bộ)" / chicken giblets)

"Thịt ba chỉ rút sườn" is PORK BELLY with the rib bones removed. 7082 is whole
chicken giblets -- a different species and a different organ/cut entirely. The
correct identity is already in the catalog as 7018
("Thịt ba chỉ (ba rọi) heo" / "Pork, lean and fat meat, raw"), and every
sibling pork-belly alias already points there, including the two that carry the
exact same "rút sườn" qualifier:

    "ba chỉ rút sườn"          -> 7018
    "thịt ba chỉ heo rút sườn" -> 7018
    "thịt ba chỉ rút xương"    -> 7018

The 7082 value is therefore an isolated corruption, not a reviewed decision.

ALIAS DECISION: REMOVE_ALIAS (not SAFE_REPOINT).

Removing the key is strictly better than repointing it to 7018 because
clean_culinary_query() in nlp/entity_matcher.py already strips "rút sườn" as
preparation noise (it sits in that function's prep_patterns list). With the
corrupt key gone, the matcher's Stage-2 cleaned-query lookup resolves
"thịt ba chỉ rút sườn" -> "thịt ba chỉ" -> 7018 through the existing sibling
alias, at the same PRESET_ALIAS_MATCH / 0.98 the rows already carry. Adding a
redundant "thịt ba chỉ rút sườn" -> 7018 entry would duplicate a resolution the
cleaner already provides and grow the alias map for no behavioural gain.

FALLTHROUGH SIMULATION (AGENTS.md §6 -- removing an unsafe alias is not
automatically safe). Simulated in-memory against the real matcher stages
before this script was written, and re-asserted at run time by
_assert_fallthrough_resolves_to_7018():

  Stage 1 EXACT/CLEANED: neither "thịt ba chỉ rút sườn" nor the prep-stripped
      "thịt ba chỉ" is a catalog name ("Thịt ba chỉ (ba rọi) heo" normalizes to
      "thịt ba chỉ ba rọi heo"), so Stage 1 does not fire.
  Stage 2 PRESET_ALIAS: query_norm misses (key removed), cleaned_q
      "thịt ba chỉ" hits -> 7018 at 0.98.  <-- resolves here
  Stage 2.5 SUBPHRASE / Stage 3 NEURAL: never reached.

All ten affected rows therefore land on 7018 by alias resolution alone. NO
row-level override is created, and a future full re-match from raw text
reproduces this state exactly -- unlike the row-level decisions in
scripts/eda/apply_suon_rib_alias_safe_fix.py. One row
("500 gr thịt ba rọi rút sườn") reaches 7018 via the sibling alias
"thịt ba rọi" instead, because its parsed name keeps the "ba rọi" spelling;
same code, same method, same confidence.

Row scope: exactly the 10 processed rows whose cleaned_name is
"thịt ba chỉ rút sườn". All 10 currently carry 7082 / "Lòng gà (cả bộ)" /
PRESET_ALIAS_MATCH / 0.98, and every one of their recipes is a pork-belly dish
("Thịt ba chỉ kho cam", "Ba Chỉ Nướng Riềng Mẻ Mắm Tôm", "Thịt một nắng", ...).

LEGITIMATE 7082 ROWS ARE NEVER TOUCHED. Five processed rows sit on 7082 through
the real chicken-giblet aliases ("lòng gà", "lòng gà cả bộ",
"lòng gà cả bộ tươi") with cleaned_name "lòng gà". Those aliases stay, those
rows stay on 7082, and both facts are asserted before and after writing.

EXPLICITLY OUT OF SCOPE (recorded by the audit, deliberately unchanged here --
this is not a 70xx cleanup): "sườn cốt lết"/"sườn cốt lết xắt lát" -> 7070,
"chả lụa", "da heo", the beef aliases, "vịt", "chim bồ câu",
"sườn bò"/"dẻ sườn bò" -> 7094, "mỡ gà", "thịt heo quay", catalog corruption,
stale-code rows, and cleaner/matcher policy questions.

Safety model (fail closed, idempotent, dry-run by default):
  - The alias edit is pinned: the key must currently hold 7082, or already be
    absent (post-fix). Any other value aborts before anything is written.
    Every other alias entry is verified byte-identical before and after.
  - The sibling pork-belly aliases on 7018 and the chicken-giblet aliases on
    7082 are asserted unchanged, so this fix cannot quietly widen.
  - Each target row is pinned by id AND exact raw_text AND its exact pre-fix
    match fields (7082 / "Lòng gà (cả bộ)" / PRESET_ALIAS_MATCH / 0.98). Every
    row must be either "pending" or "already_applied"; anything else aborts the
    ENTIRE run before any write.
  - The pinned id set is cross-checked against the rows the removal can
    actually reach (recomputed from the live data through the real
    normalize_vietnamese_text/clean_culinary_query functions). A drift in
    either direction aborts.
  - 7018 must exist in the live catalog under its exact expected name, checked
    through the same identity guard nlp.matching_integrity.stage_qwen_update
    enforces for the Qwen pipeline. Nutrition is computed by that function from
    the catalog plus each row's own current weight -- never typed by hand.
    7018 declares no carbs_g, so remapped rows carry a null (not zero) carbs_g,
    per the nullable-nutrition contract in nlp.nutrition.
  - Rows/aliases already in "already_applied" state are left byte-identical
    (idempotent reruns produce no diff and no error).

Scope: data/processed/viendinhduong/ingredient_alias_map.json and
data/processed/recipes/recipe_ingredients.{csv,json} plus the recipe-level
rollup totals and nutrition_status/missing_nutrition_count in
data/processed/recipes/recipes.{csv,json}. Canonical outputs
(data/processed/recipes/canonical_*.csv/json, recipe_canonical_mapping.csv) are
intentionally NOT regenerated here -- regenerate them separately via
scripts/canonicalize_recipes.py (then scripts/export_canonical_json.py) after
this fix is applied, per AGENTS.md §11.
"""

import argparse
import json
from pathlib import Path

from nlp.entity_matcher import clean_culinary_query, normalize_vietnamese_text
from nlp.matching_integrity import stage_qwen_update
from nlp.nutrition import nutrition_value
from scripts.eda.apply_qwen_class_d_safe_fix import _recompute_status, write_csv
from scripts.eda.apply_qwen_safe_fix import (
    ING,
    ING_JSON,
    RECIPES_CSV,
    RECIPES_JSON,
    _apply_rollups,
    read_csv,
    read_json,
    recompute_recipe_rollups,
    write_json,
)

ROOT = Path(__file__).resolve().parents[2]
ALIAS_PATH = ROOT / "data/processed/viendinhduong/ingredient_alias_map.json"
MASTER = ROOT / "data/processed/viendinhduong/master_ingredients_nutrition.csv"
OUT = ROOT / "reports/eda/thit_ba_chi_rut_suon_alias_fix"

PRESET_ALIAS_METHOD = "PRESET_ALIAS_MATCH"
PRESET_ALIAS_CONFIDENCE = "0.98"

# The contaminated identity the alias and all ten rows currently carry.
OLD_CODE = "7082"
OLD_NAME = "Lòng gà (cả bộ)"

# The correct pork-belly identity, exactly as the live catalog names it.
NEW_CODE = "7018"
NEW_NAME = "Thịt ba chỉ (ba rọi) heo"

# --- Alias-map edits -------------------------------------------------------

# The single unsafe key. Removed rather than repointed: clean_culinary_query()
# strips "rút sườn", so the sibling "thịt ba chỉ" alias already resolves it.
ALIAS_REMOVALS = ("thịt ba chỉ rút sườn",)

# The cleaned form the removal falls through to, and the sibling that carries
# it. If this alias ever stops pointing at 7018 the removal is no longer safe.
FALLTHROUGH_CLEANED_NAME = "thịt ba chỉ"

# Sibling pork-belly aliases that must survive this fix untouched on 7018 --
# including the two that carry the same "rút sườn" qualifier and prove the
# 7082 value was an isolated corruption rather than a reviewed decision.
ALIAS_MUST_REMAIN_7018 = (
    "thịt ba chỉ", "thịt ba rọi", "ba chỉ", "ba chỉ heo", "ba rọi",
    "thịt ba chỉ heo", "ba chỉ rút sườn", "thịt ba chỉ heo rút sườn",
    "ba rọi rút sườn", "thịt ba chỉ rút xương", "thịt ba chỉ cắt lát",
    "thịt ba chỉ xay", "thịt ba chỉ heo xay", "thịt ba chỉ heo cắt nhỏ",
    "thịt ba chỉ ngon", "ba rọi ngon", "thi t ba chi",
    "thịt lợn nửa nạc nửa mỡ tươi",
)

# The real chicken-giblet aliases. 7082 is a legitimate identity; only the one
# pork-belly key is wrong, so these must stay exactly where they are.
ALIAS_MUST_REMAIN_7082 = ("lòng gà", "lòng gà cả bộ", "lòng gà cả bộ tươi")

assert not set(ALIAS_REMOVALS) & set(ALIAS_MUST_REMAIN_7018)
assert not set(ALIAS_REMOVALS) & set(ALIAS_MUST_REMAIN_7082)
assert FALLTHROUGH_CLEANED_NAME in ALIAS_MUST_REMAIN_7018

# --- Row-level edits --------------------------------------------------------

# The ten contaminated rows, pinned by id and exact raw_text. Every one of them
# is resolved by the alias removal alone -- there are no row-level overrides in
# this fix, so re-running the matcher reproduces all ten.
REMAP_ROWS = (
    ("649979f6-91b9-487e-be84-7465328d395b", "400 g Thịt ba chỉ rút sườn"),
    ("d74a55d5-4036-40b0-8a78-c5849b4d6969", "500 gr thịt ba rọi rút sườn"),
    ("49e65216-cbf8-4c09-8496-41d629b4ad6e", "Thịt ba chỉ rút sườn 600g"),
    ("42cf8d71-b3ae-45fd-8de9-a2d69809dfc1", "Thịt ba chỉ rút sườn 300g"),
    ("e2278878-b9fb-4392-b15a-318885739704", "Thịt ba chỉ rút sườn: 300g"),
    ("dfce19a5-520b-4eb3-9a6c-af9c3e00d88a", "Thịt ba chỉ rút sườn 500g"),
    ("d321c9bf-8c2c-4bb0-9397-c482d93f7731", "Thịt ba chỉ rút sườn 400g"),
    ("6f9cfee5-507d-433e-a9fd-9e0e6ad168e2", "Thịt ba chỉ rút sườn 300g"),
    ("9dd7353b-f0aa-46a8-9b02-0fa7aa679398", "Thịt ba chỉ rút sườn 2.5 kg"),
    ("7d78336c-9527-4dee-89f3-dc79c33e32f3", "Thịt ba chỉ rút sườn 500 gr"),
)

# The cleaned_name every target row carries, and the only cleaned_name whose
# alias lookup can reach the removed key.
TARGET_CLEANED_NAME = "thịt ba chỉ rút sườn"

assert len(REMAP_ROWS) == 10
TARGET_IDS = frozenset(rid for rid, _ in REMAP_ROWS)
assert len(TARGET_IDS) == 10

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


def _alias_removal_state(alias_map, key):
    if key not in alias_map:
        return "already_applied"
    if alias_map[key] == OLD_CODE:
        return "pending"
    raise DriftError(
        f"alias {key!r} has unexpected value {alias_map[key]!r} (expected {OLD_CODE!r} or absent)"
    )


def _assert_siblings_intact(alias_map):
    """The pork-belly siblings on 7018 and the chicken-giblet aliases on 7082
    are the evidence this fix rests on. If either family has drifted, the
    reviewed conclusion no longer holds and nothing may be written."""
    for key in ALIAS_MUST_REMAIN_7018:
        if alias_map.get(key) != NEW_CODE:
            raise DriftError(
                f"sibling pork-belly alias {key!r} is {alias_map.get(key)!r}, expected {NEW_CODE!r}"
            )
    for key in ALIAS_MUST_REMAIN_7082:
        if alias_map.get(key) != OLD_CODE:
            raise DriftError(
                f"chicken-giblet alias {key!r} is {alias_map.get(key)!r}, expected {OLD_CODE!r}"
            )


def _assert_fallthrough_resolves_to_7018(new_map):
    """Simulate the post-removal matcher fallthrough, through the real cleaner.

    Stage 2 of VietnameseIngredientMatcher.match() looks up the normalized query
    first and the prep-stripped cleaned query second. After the removal the
    first lookup must miss and the second must land on 7018 -- otherwise the row
    would fall into SUBPHRASE/neural matching and this removal is unsafe.
    """
    norm_keys = {normalize_vietnamese_text(k): v for k, v in new_map.items()}
    query_norm = normalize_vietnamese_text(TARGET_CLEANED_NAME)
    if query_norm in norm_keys:
        raise DriftError(
            f"post-fix alias map still resolves {TARGET_CLEANED_NAME!r} directly "
            f"to {norm_keys[query_norm]!r} -- the removal did not take effect"
        )
    cleaned_q = clean_culinary_query(TARGET_CLEANED_NAME)
    if cleaned_q != FALLTHROUGH_CLEANED_NAME:
        raise DriftError(
            f"clean_culinary_query({TARGET_CLEANED_NAME!r}) is now {cleaned_q!r}, "
            f"not {FALLTHROUGH_CLEANED_NAME!r} -- the 'rút sườn' prep rule changed"
        )
    if norm_keys.get(normalize_vietnamese_text(cleaned_q)) != NEW_CODE:
        raise DriftError(
            f"fallthrough alias {cleaned_q!r} does not resolve to {NEW_CODE!r} -- "
            "removing the unsafe alias would leave these rows to a weaker matcher stage"
        )


def apply_alias_changes(alias_map, states):
    """Build the new alias map, touching only the one known key."""
    new_map = dict(alias_map)
    for key in ALIAS_REMOVALS:
        if states[key] == "pending":
            del new_map[key]

    # Belt-and-suspenders: every key outside the targeted one must be
    # byte-identical between old and new maps.
    touched = set(ALIAS_REMOVALS)
    for key, value in alias_map.items():
        if key in touched:
            continue
        if new_map.get(key) != value:
            raise DriftError(f"unrelated alias {key!r} would be changed -- refusing to write")
    if not len(alias_map) - len(ALIAS_REMOVALS) <= len(new_map) <= len(alias_map):
        raise DriftError("alias map size changed by more than the 1 expected removal")

    _assert_siblings_intact(new_map)
    for key in touched:
        if key in new_map:
            raise DriftError(f"alias {key!r} would survive the removal -- refusing to write")
    _assert_fallthrough_resolves_to_7018(new_map)
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


def _row_state(row, raw_text):
    rid = row.get("id")
    if row.get("raw_text") != raw_text:
        raise DriftError(
            f"row {rid}: raw_text drifted (expected {raw_text!r}, found {row.get('raw_text')!r})"
        )
    if row.get("cleaned_name") != TARGET_CLEANED_NAME:
        raise DriftError(
            f"row {rid}: cleaned_name is {row.get('cleaned_name')!r}, "
            f"expected {TARGET_CLEANED_NAME!r} -- the alias removal would not reach this row"
        )
    if _pending_probe(row):
        return "pending"
    if _remap_applied_probe(row):
        return "already_applied"
    raise DriftError(
        f"row {rid}: neither pending ({OLD_CODE}/{OLD_NAME!r}) nor already-remapped state matched "
        f"(found code={row.get('master_ingredient_code')!r} name={row.get('master_ingredient_name')!r} "
        f"method={row.get('match_method')!r} confidence={row.get('match_confidence')!r})"
    )


def rows_reachable_by_removal(ing_rows):
    """Recompute, from live data, which rows the removed alias can actually
    reach -- via either Stage-2 lookup route (normalized query or prep-stripped
    cleaned query). Used to prove the pinned id set is neither stale nor short.
    """
    removed = {normalize_vietnamese_text(k) for k in ALIAS_REMOVALS}
    hit = set()
    for row in ing_rows:
        cleaned = row.get("cleaned_name") or ""
        if normalize_vietnamese_text(cleaned) in removed or clean_culinary_query(cleaned) in removed:
            hit.add(row["id"])
    return hit


def build_plan():
    """Read-only: locate the alias edit and the 10 target rows, classify each."""
    alias_map = read_alias_map()
    _assert_siblings_intact(alias_map)
    alias_states = {key: _alias_removal_state(alias_map, key) for key in ALIAS_REMOVALS}

    masters = {r["code"]: r for r in read_csv(MASTER)}
    if NEW_CODE not in masters:
        raise DriftError(f"remap target code {NEW_CODE!r} is absent from the current catalog")
    if masters[NEW_CODE].get("name_vi", "").strip() != NEW_NAME:
        raise DriftError(
            f"remap target code {NEW_CODE!r} now names "
            f"{masters[NEW_CODE].get('name_vi')!r}, not {NEW_NAME!r}"
        )
    if OLD_CODE not in masters or masters[OLD_CODE].get("name_vi", "").strip() != OLD_NAME:
        raise DriftError(
            f"contaminated code {OLD_CODE!r} no longer names {OLD_NAME!r} -- "
            "the reviewed evidence for this fix has drifted"
        )

    ing_rows = read_csv(ING)
    by_id = {r["id"]: r for r in ing_rows}

    row_states = {}
    for rid, raw_text in REMAP_ROWS:
        row = by_id.get(rid)
        if row is None:
            raise DriftError(f"REMAP row {rid} not found in {ING}")
        row_states[rid] = _row_state(row, raw_text)

    # The pinned set must equal the set the removal can actually reach. A row
    # appearing or disappearing means the blast radius is no longer the
    # reviewed one, so nothing may be written.
    reachable = rows_reachable_by_removal(ing_rows)
    if reachable != set(TARGET_IDS):
        raise DriftError(
            f"blast radius drifted: rows reachable by the removal {sorted(reachable)} "
            f"!= reviewed rows {sorted(TARGET_IDS)}"
        )

    # Legitimate chicken-giblet rows must exist and must not be in scope.
    legit_7082 = {
        r["id"] for r in ing_rows
        if (r.get("master_ingredient_code") or "").strip() == OLD_CODE
        and r["id"] not in TARGET_IDS
    }
    if legit_7082 & set(TARGET_IDS):
        raise DriftError("legitimate 7082 rows overlap the reviewed target rows")

    return alias_map, alias_states, masters, row_states, legit_7082


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
    alias_map, alias_states, masters, row_states, legit_7082 = build_plan()
    remap_now = {rid for rid in TARGET_IDS if row_states[rid] == "pending"}

    ing_csv_rows = read_csv(ING)
    ing_json_rows = read_json(ING_JSON)

    def transform(row):
        rid = row["id"]
        if rid in TARGET_IDS and row_states.get(rid) == "pending":
            return _apply_remap(row, masters)
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

    # Post-transform guards.
    for rid, row in after_by_id.items():
        if not _remap_applied_probe(row):
            raise DriftError(f"row {rid} did not reach the 7018 fixed state -- refusing to write")
    # Legitimate chicken-giblet rows must come through byte-identical.
    after_all = {r["id"]: r for r in new_ing_csv_rows}
    for rid in legit_7082:
        before_row = next(r for r in ing_csv_rows if r["id"] == rid)
        if after_all[rid] != before_row:
            raise DriftError(f"legitimate 7082 row {rid} was modified -- refusing to write")
    # No unrelated row may change at all.
    changed_ids = {
        r["id"] for r, o in zip(new_ing_csv_rows, ing_csv_rows) if r != o
    }
    if not changed_ids <= set(TARGET_IDS):
        raise DriftError(
            f"unrelated rows would change: {sorted(changed_ids - set(TARGET_IDS))[:10]}"
        )

    nutrition_before = _nutrition_totals(before_by_id.values())
    nutrition_after = _nutrition_totals(after_by_id.values())
    affected_recipe_ids = {r["recipe_id"] for r in ing_csv_rows if r["id"] in TARGET_IDS}

    def _delta(before, after):
        return {k: round(after[k] - before[k], 1) for k in before}

    report = {
        "status": "applied" if apply else "preview",
        "alias_states": alias_states,
        "alias_removals": list(ALIAS_REMOVALS),
        "alias_decision": "REMOVE_ALIAS",
        "fallthrough": {
            "cleaned_query": FALLTHROUGH_CLEANED_NAME,
            "resolves_to": NEW_CODE,
            "method": PRESET_ALIAS_METHOD,
            "confidence": PRESET_ALIAS_CONFIDENCE,
            "row_level_overrides": 0,
        },
        "remap_target_count": len(TARGET_IDS),
        "remap_applied_now": len(remap_now),
        "remap_already_applied": len(TARGET_IDS) - len(remap_now),
        "legitimate_7082_rows_untouched": len(legit_7082),
        "affected_recipe_count": len(affected_recipe_ids),
        "affected_recipe_ids": sorted(affected_recipe_ids),
        "recipes_with_changed_totals": changed_totals,
        "recipes_with_changed_missing_count": status_report["recipes_with_changed_missing_count"],
        "recipes_with_status_label_changed": status_report["recipes_with_status_label_changed"],
        "status_transitions": status_report["status_transitions"],
        "nutrition_all_10": {
            "before": nutrition_before,
            "after": nutrition_after,
            "delta": _delta(nutrition_before, nutrition_after),
        },
        "remap_row_ids": sorted(TARGET_IDS),
        "row_outcomes": {
            rid: {
                "raw_text": before_by_id[rid].get("raw_text"),
                "cleaned_name": before_by_id[rid].get("cleaned_name"),
                "recipe_id": before_by_id[rid].get("recipe_id"),
                "estimated_weight_g": after_by_id[rid].get("estimated_weight_g"),
                "decision": "REMAP_7018_VIA_ALIAS_FALLTHROUGH",
                "before": {f: before_by_id[rid].get(f) for f in REPORT_ROW_FIELDS},
                "after": {f: after_by_id[rid].get(f) for f in REPORT_ROW_FIELDS},
            }
            for rid in sorted(TARGET_IDS)
        },
        "out_of_scope_note": (
            "Batch B removes exactly one alias. Every other 70xx audit finding is deliberately "
            "unchanged: 'sườn cốt lết'/'sườn cốt lết xắt lát'->7070, chả lụa, da heo, the beef "
            "aliases, vịt, chim bồ câu, 'sườn bò'/'dẻ sườn bò'->7094, mỡ gà, thịt heo quay, "
            "catalog corruption, stale-code rows, and cleaner/matcher policy issues."
        ),
        "canonical_note": (
            "Canonical outputs (canonical_recipes.csv/json, canonical_recipe_ingredients.csv/json, "
            "recipe_canonical_mapping.csv/json, recipe_canonicalization_summary.json) are NOT "
            "regenerated by this script and are stale for these rows/recipes until "
            "scripts/canonicalize_recipes.py and scripts/export_canonical_json.py are re-run."
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
        {k: v for k, v in report.items() if k not in ("remap_row_ids", "row_outcomes")},
        ensure_ascii=False, indent=2,
    ))


if __name__ == "__main__":
    main()
