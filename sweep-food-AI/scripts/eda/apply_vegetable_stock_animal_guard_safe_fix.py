"""Apply the reviewed vegetable-stock animal-identity guard to the 8 live
processed rows it blocks. Default previews; --apply writes.

The guard itself lives in nlp/entity_matcher.py (_blocks_vegetable_stock,
reason VEGETABLE_STOCK_PHRASE_ANIMAL_TARGET) and stops the bad resolution from
ever being produced again. This script repairs the rows that were already
written before the guard existed; it introduces no policy of its own.

REVIEWED POLICY. When ingredient evidence -- the union of NFC-normalized
raw_text and cleaned_name -- explicitly describes a vegetable stock/broth, and
the resolved catalog target is an animal identity, the match is blocked
terminally and the row becomes UNMATCHED.

    "Nước dùng rau củ 1,6 lít" is vegetable stock. It was resolving to 7141
    "Nước dùng" (Broth), filed under "Thịt và sản phẩm chế biến" -- meat.

This is the residual case the vegetarian ("chay") guard explicitly deferred:
those rows carry no ingredient-level "chay" marker, so is_chay_text() is inert
on them and they survived that fix. They are now covered by their own predicate.

THE DETECTOR (nlp.entity_matcher.is_vegetable_stock_text):

    VEG_STOCK_RE              \\bnước\\s+(?:dùng|hầm|luộc)\\s+rau\\b
    VEG_STOCK_ANIMAL_VETO_RE  any reviewed animal token -> do NOT block

Two independent narrowing mechanisms, neither a broad substring rule:

  * ADJACENCY. "rau" must IMMEDIATELY follow the stock head, so an animal
    qualifier in between breaks the pattern structurally rather than by
    exception list: "nước dùng gà rau củ" and "nước dùng bò với rau" do not
    match at all. Bare "rau" is never a trigger -- on its own it resolves to
    4066 "Rau bí", and the live row "Rau củ nấu nước dùng chay : su su" is
    "rau" as a SEPARATE ingredient, which adjacency correctly declines
    ("nước dùng" is followed by "chay", not "rau").
  * ANIMAL VETO. Explicit animal material anywhere in the evidence means the
    line describes an animal broth cooked with vegetables, which 7141
    legitimately covers. The live row "600 ml Nước hầm xương/rau củ/dashi" is
    vetoed by "xương" and "dashi" (normalize_vietnamese_text() turns the
    slashes into spaces, so the tokens stand alone). "nước dùng rau củ và gà"
    is vetoed the same way.

ANIMAL IDENTITY is decided by catalog metadata, reusing the vegetarian guard's
reviewed policy verbatim so the two cannot drift apart:

    category_vi in {"Thịt và sản phẩm chế biến",
                    "Thủy sản và sản phẩm chế biến"}
    OR code in the 11 reviewed supplementary codes

WHY THE GUARD IS KEYED ON THE RESOLVED IDENTITY, NOT THE PHRASE. Removing the
two alias-map keys would fix nothing. Measured against the live catalog:

  * SUBPHRASE_CATALOG_MATCH re-derives 7141 from the catalog head "nước dùng"
    -- "nước dùng rau" at 0.692, "nước dùng rau củ" at 0.562, both far over the
    0.35 threshold.
  * "nước dùng rau củ quả" already reaches 7141 at 0.45 with NO alias at all,
    so the hazard is broader than the two keys.
  * The neural stage is no safer: its top-1 for every variant is an animal
    identity (7141 at 0.54-0.58, else 7140 "Nước canh", also meat), and the
    best non-animal candidate it offers is 4100 "Súp lơ xanh" -- broccoli.

There is no valid catalog target at all, so UNMATCHED is the correct verdict
(AGENTS.md §2, §5).

THE 8 ROWS (measured against the live 63,943-row processed dataset):

    5 rows  cleaned_name "nước dùng rau"     -> 7141 Nước dùng (Thịt)
    3 rows  cleaned_name "nước dùng rau củ"  -> 7141 Nước dùng (Thịt)

All 8 raw texts name the ingredient explicitly as vegetable stock, at
litre-scale quantities in soup/noodle recipes. None is plain water.

STALE cleaned_name (recorded, deliberately NOT repaired here). Seven of the
eight raw texts read "Nước dùng rau củ"; only one (81739420) genuinely reads
"Nước dùng rau". Five rows store cleaned_name "nước dùng rau", so FOUR of them
lost the "củ" -- historical parser drift, since today's
VietnameseIngredientParser preserves "Nước dùng rau củ" for all of them. This
fix does not rewrite cleaned_name: the guard reads the UNION of raw_text and
cleaned_name precisely so it stays correct despite that drift. A global
stale-cleaned_name audit is a separate task (AGENTS.md §18).

FORWARD-PROTECTION ROW (recognized by the guard, deliberately untouched here).
470f6222 "Nước hầm rau 700 ml" is ALREADY UNMATCHED. The guard recognizes it,
which is why the "hầm" stock head is in the pattern, but there is nothing to
repair and its persisted state must not move. It is asserted byte-identical.

EXPLICITLY OUT OF SCOPE (recorded, deliberately unchanged):

  * The two alias-map keys "nước dùng rau" / "nước dùng rau củ" -> 7141. They
    stay in the map and the guard makes them inert, exactly as the chay fix
    left its four hazardous keys. Removal would not help (see above) and would
    only relabel match_method (AGENTS.md §6/§18).
  * 20002 "Nước lọc (nước dùng nấu)" as a repoint target. Vegetable stock is
    not drinking water, and 20002 carries explicit 0.0 macros -- repointing
    would convert MISSING nutrition into asserted real zeros, which AGENTS.md
    §4 forbids, on top of being semantically wrong.
  * A new vegetable-stock catalog entry. This is the correct long-term fix and
    is recorded as a deferred catalog gap; it needs real Viện Dinh Dưỡng
    nutrition and a catalog + embeddings regeneration, so it is not done here.
  * The 6 "nước dùng chay" rows already UNMATCHED, the chay guard, the 7141
    catalog definition, dashi mappings, seasoning analogues.
  * Animal broths with explicit animal semantics (141 of the 149 live 7141
    rows), which keep their identity.
  * "rau trai" -> 8054 Trai, nước ngọt; garnish-list collapse; any other
    matcher divergence.

NUTRITION (AGENTS.md §4, §9). Clearing a row sets calories/protein_g/fat_g/
carbs_g to NULL -- unknown -- never to 0.0, and match_confidence to null rather
than the 0.0 rejection sentinel. raw_text, cleaned_name, required_quantity,
unit_vi, unit, preparation_note and estimated_weight_g are all preserved.
Recipe rollups for the 8 affected recipes are recomputed from the repaired
ingredient rows, removing 99.5 kcal in total. Protein/fat/carbs impact is
exactly 0.0: 7141 is nutritionally near-empty at 1 kcal/100 g and its macros
are already blank in the live catalog, so the 8 rows never carried any.

Safety model (fail closed, idempotent, dry-run by default):
  - The guard must be live in nlp.entity_matcher before anything is written,
    and must actually block each reviewed phrase AND decline each reviewed
    false-positive probe. A run against an unguarded or over-broad matcher
    aborts.
  - The blocked set is RECOMPUTED from live data through the real
    is_vegetable_stock_text() predicate and the real catalog categories, then
    cross-checked against the pinned id set. Drift in either direction aborts
    before any write.
  - Every target row is pinned by id AND exact raw_text AND cleaned_name AND
    its exact pre-fix code/name/method/confidence. Each must be either
    "pending" or "already_applied"; anything else aborts the ENTIRE run.
  - Every code this fix reads must exist in the live catalog under its exact
    current name_vi (AGENTS.md §3).
  - Rows outside the pinned set are asserted byte-identical after the write,
    including the forward-protection row.
  - Reruns are idempotent: an already-cleared row is left byte-identical and
    produces no diff and no error.

Scope: data/processed/recipes/recipe_ingredients.{csv,json} and the recipe-level
rollup totals plus nutrition_status/missing_nutrition_count in
data/processed/recipes/recipes.{csv,json}. Canonical outputs are intentionally
NOT regenerated here -- regenerate them via scripts/canonicalize_recipes.py
(then scripts/export_canonical_json.py, then canonicalize --check) after this
fix is applied, per AGENTS.md §11.
"""

import argparse
import csv
import json
from pathlib import Path

from nlp.entity_matcher import (
    ANIMAL_CATEGORIES_VI,
    ANIMAL_SUPPLEMENTARY_CODES,
    VEGETABLE_STOCK_GUARD_REASON,
    VietnameseIngredientMatcher,
    is_vegetable_stock_text,
)
from scripts.eda.apply_qwen_class_d_safe_fix import _recompute_status
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
    write_csv,
    write_json,
)

ROOT = Path(__file__).resolve().parents[2]
MASTER = ROOT / "data/processed/viendinhduong/master_ingredients_nutrition.csv"
OUT = ROOT / "reports/eda/vegetable_stock_animal_guard"

# The reviewed blast radius. Pinned by full id, with the exact pre-fix state
# each row must carry.
#   id -> (raw_text, cleaned_name, code, name, method, confidence)
TARGET_ROWS = {
    "f9e2f60c-3f14-4bea-8588-ed6abc045af1": (
        "Nước dùng rau củ 1,6 lít", "nước dùng rau", "7141", "Nước dùng",
        "PRESET_ALIAS_MATCH", "0.98"),
    "e07fe326-e899-4425-995c-f0134cad81e4": (
        "Nước dùng rau củ 1,2 lít", "nước dùng rau", "7141", "Nước dùng",
        "PRESET_ALIAS_MATCH", "0.98"),
    "e3b10cc6-c4fc-4420-a662-17b2c432018c": (
        "Nước dùng rau củ 1 lít", "nước dùng rau", "7141", "Nước dùng",
        "PRESET_ALIAS_MATCH", "0.98"),
    "16c22e9a-db70-4266-8df2-3c834d977495": (
        "Nước dùng rau củ 1,5 lít", "nước dùng rau", "7141", "Nước dùng",
        "PRESET_ALIAS_MATCH", "0.98"),
    "81739420-ba9f-414b-913d-ee6329326cfd": (
        "Nước dùng rau 950 ml", "nước dùng rau", "7141", "Nước dùng",
        "PRESET_ALIAS_MATCH", "0.98"),
    "22b6999f-d0fa-4b27-9a6f-ca6f7cbe5cb8": (
        "Nước dùng rau củ: 1,2 L", "nước dùng rau củ", "7141", "Nước dùng",
        "PRESET_ALIAS_MATCH", "0.98"),
    "ba987c1c-8399-4e93-87ac-33b393e41370": (
        "Nước dùng rau củ: 1 lít", "nước dùng rau củ", "7141", "Nước dùng",
        "PRESET_ALIAS_MATCH", "0.98"),
    "c9f4c65d-b499-4854-9b84-8b4afba86da1": (
        "Nước dùng rau củ: 1,5L", "nước dùng rau củ", "7141", "Nước dùng",
        "PRESET_ALIAS_MATCH", "0.98"),
}
assert len(TARGET_ROWS) == 8

# Already UNMATCHED, recognized by the guard, must not move. Pinned so that a
# future change that starts writing to it fails this script rather than the
# dataset.
FORWARD_PROTECTION_ROWS = {
    "470f6222-a04d-46a7-9404-656880fdf968": ("Nước hầm rau 700 ml", "nước hầm rau"),
}

# Every code this fix reads, with its exact current live name_vi.
CODE_NAMES = {
    "7141": "Nước dùng",
}

# Phrases the guard must actually block for this fix to be coherent.
GUARDED_PHRASES = ("nước dùng rau", "nước dùng rau củ", "nước dùng rau củ quả",
                   "nước hầm rau")

# Phrases that must NOT be blocked -- the reviewed false-positive probes. A
# guard that blocked any of these would be over-broad and must not be applied.
# Value is the code each must keep, or None for "any resolved identity".
NOT_BLOCKED_PHRASES = {
    "nước dùng gà rau củ": None,
    "nước dùng bò với rau": None,
    "nước dùng rau củ và gà": None,
    "nước hầm xương rau củ": None,
    "600 ml Nước hầm xương/rau củ/dashi": None,
    "nước dùng tôm": "7141",
    "nước dùng gà": "7141",
    "nước dùng": "7141",
    "rau muống": "4083",
    "cà chua": "4005",
}

# Preserved verbatim on every cleared row (AGENTS.md §4).
PRESERVED_FIELDS = ("raw_text", "cleaned_name", "required_quantity", "unit_vi",
                    "unit", "preparation_note", "estimated_weight_g")

NUTRITION_FIELDS = ("calories", "protein_g", "fat_g", "carbs_g")


def load_catalog():
    with MASTER.open(encoding="utf-8-sig", newline="") as f:
        return {r["code"].strip(): r for r in csv.DictReader(f)}


def is_animal_code(catalog, code):
    code = (code or "").strip()
    if not code or code not in catalog:
        return False
    row = catalog[code]
    return (row["category_vi"].strip() in ANIMAL_CATEGORIES_VI
            or code in ANIMAL_SUPPLEMENTARY_CODES)


def verify_guard_is_live():
    """The guard must exist and behave, or this fix is repairing rows the
    matcher will simply rewrite on the next run."""
    matcher = VietnameseIngredientMatcher(device="cpu")
    for phrase in GUARDED_PHRASES:
        result = matcher.match(phrase)
        if (result["method"] != "UNMATCHED"
                or result.get("guard") != VEGETABLE_STOCK_GUARD_REASON):
            raise SystemExit(
                f"FAIL-CLOSED: guard is not live -- {phrase!r} resolved as "
                f"{result['method']} ({result['matched_item'].get('code')})"
            )
    for phrase, code in NOT_BLOCKED_PHRASES.items():
        result = matcher.match(phrase)
        if result["method"] == "UNMATCHED":
            raise SystemExit(
                f"FAIL-CLOSED: guard is over-broad -- {phrase!r} was blocked "
                f"({result.get('guard')})"
            )
        if code is not None and result["matched_item"].get("code") != code:
            raise SystemExit(
                f"FAIL-CLOSED: guard shifted {phrase!r} to "
                f"{result['matched_item'].get('code')}, expected {code}"
            )
    return matcher


def classify(row):
    """pending | already_applied -- anything else aborts the run."""
    raw_text, cleaned_name, code, name, method, confidence = TARGET_ROWS[row["id"]]

    if (row.get("raw_text") or "") != raw_text:
        raise SystemExit(
            f"FAIL-CLOSED: raw_text drift on {row['id']}\n"
            f"  expected {raw_text!r}\n  found    {row.get('raw_text')!r}"
        )
    if (row.get("cleaned_name") or "") != cleaned_name:
        raise SystemExit(
            f"FAIL-CLOSED: cleaned_name drift on {row['id']}\n"
            f"  expected {cleaned_name!r}\n  found    {row.get('cleaned_name')!r}"
        )

    current_code = (row.get("master_ingredient_code") or "").strip()
    current_method = (row.get("match_method") or "").strip()

    if current_code == code:
        if (row.get("master_ingredient_name") or "").strip() != name:
            raise SystemExit(f"FAIL-CLOSED: name drift on {row['id']}")
        if current_method != method:
            raise SystemExit(f"FAIL-CLOSED: method drift on {row['id']}: {current_method}")
        if str(row.get("match_confidence") or "").strip() != confidence:
            raise SystemExit(f"FAIL-CLOSED: confidence drift on {row['id']}")
        return "pending"

    if not current_code and current_method == "UNMATCHED":
        return "already_applied"

    raise SystemExit(
        f"FAIL-CLOSED: unexpected state on {row['id']}: "
        f"code={current_code!r} method={current_method!r}"
    )


def build_plan():
    """Read-only. Validates preconditions and returns what would change."""
    catalog = load_catalog()

    for code, name in CODE_NAMES.items():
        if code not in catalog:
            raise SystemExit(f"FAIL-CLOSED: code {code} missing from live catalog")
        if catalog[code]["name_vi"].strip() != name:
            raise SystemExit(
                f"FAIL-CLOSED: catalog identity drift on {code}: "
                f"expected {name!r}, found {catalog[code]['name_vi']!r}"
            )
        if not is_animal_code(catalog, code):
            raise SystemExit(f"FAIL-CLOSED: {code} is no longer an animal identity")

    rows = read_csv(ING)
    by_id = {r["id"]: r for r in rows}

    # Recompute the blocked population from live data rather than trusting the
    # pinned list. Drift in EITHER direction aborts.
    recomputed = {
        r["id"] for r in rows
        if is_vegetable_stock_text(r.get("raw_text"), r.get("cleaned_name"))
        and is_animal_code(catalog, r.get("master_ingredient_code"))
    }
    pending_pinned = {
        rid for rid in TARGET_ROWS
        if (by_id[rid].get("master_ingredient_code") or "").strip()
    } if set(TARGET_ROWS) <= set(by_id) else set()
    if recomputed != pending_pinned:
        raise SystemExit(
            "FAIL-CLOSED: blast radius drift.\n"
            f"  recomputed-but-not-pinned: {sorted(recomputed - pending_pinned)}\n"
            f"  pinned-but-not-recomputed: {sorted(pending_pinned - recomputed)}"
        )

    missing = set(TARGET_ROWS) - set(by_id)
    if missing:
        raise SystemExit(f"FAIL-CLOSED: target rows absent from dataset: {sorted(missing)}")

    # The forward-protection row must already be UNMATCHED and stay that way.
    for rid, (raw_text, cleaned_name) in FORWARD_PROTECTION_ROWS.items():
        row = by_id.get(rid)
        if row is None:
            raise SystemExit(f"FAIL-CLOSED: forward-protection row {rid} absent")
        if (row.get("raw_text") or "") != raw_text:
            raise SystemExit(f"FAIL-CLOSED: forward-protection raw_text drift on {rid}")
        if (row.get("match_method") or "").strip() != "UNMATCHED":
            raise SystemExit(
                f"FAIL-CLOSED: forward-protection row {rid} is no longer UNMATCHED"
            )
        if not is_vegetable_stock_text(row.get("raw_text"), row.get("cleaned_name")):
            raise SystemExit(
                f"FAIL-CLOSED: guard no longer recognizes forward-protection row {rid}"
            )

    states = {rid: classify(by_id[rid]) for rid in TARGET_ROWS}

    nutrition_removed = dict.fromkeys(NUTRITION_FIELDS, 0.0)
    per_row = []
    for rid, state in states.items():
        row = by_id[rid]
        removed = {}
        for field in NUTRITION_FIELDS:
            try:
                value = float(row.get(field) or 0.0)
            except (TypeError, ValueError):
                value = 0.0
            removed[field] = value
            if state == "pending":
                nutrition_removed[field] += value
        per_row.append({
            "id": rid,
            "state": state,
            "recipe_id": row.get("recipe_id"),
            "raw_text": row.get("raw_text"),
            "cleaned_name": row.get("cleaned_name"),
            "estimated_weight_g": row.get("estimated_weight_g"),
            "before": {
                "master_ingredient_code": row.get("master_ingredient_code"),
                "master_ingredient_name": row.get("master_ingredient_name"),
                "match_method": row.get("match_method"),
                "match_confidence": row.get("match_confidence"),
                **removed,
            },
            "after": {
                "master_ingredient_code": None,
                "master_ingredient_name": None,
                "match_method": "UNMATCHED",
                "match_confidence": None,
                **dict.fromkeys(NUTRITION_FIELDS, None),
            },
            "reason": VEGETABLE_STOCK_GUARD_REASON,
        })

    recipe_ids = sorted({by_id[rid].get("recipe_id") for rid in TARGET_ROWS})
    return catalog, states, per_row, nutrition_removed, recipe_ids


def run(apply=False):
    verify_guard_is_live()
    catalog, states, per_row, nutrition_removed, recipe_ids = build_plan()

    pending = sorted(rid for rid, s in states.items() if s == "pending")
    already = sorted(rid for rid, s in states.items() if s == "already_applied")

    print(f"Guard        : {VEGETABLE_STOCK_GUARD_REASON}")
    print(f"Target rows  : {len(TARGET_ROWS)} ({len(pending)} pending, "
          f"{len(already)} already applied)")
    print(f"Recipes      : {len(recipe_ids)}")
    print(f"Forward-protection rows (untouched): {len(FORWARD_PROTECTION_ROWS)}")
    print("Nutrition removed: " + ", ".join(
        f"{k}={round(v, 1)}" for k, v in nutrition_removed.items()))
    print()
    for entry in per_row:
        before = entry["before"]
        print(f"  [{entry['state']:15}] {entry['id'][:8]}  {entry['raw_text'][:30]:30}"
              f"  {entry['cleaned_name']:18}"
              f"  {before['master_ingredient_code'] or '-':>5} "
              f"{before['master_ingredient_name'] or '-':10} -> UNMATCHED")

    if not apply:
        print("\nDRY RUN -- no files written. Re-run with --apply to write.")
        return 0

    if not pending:
        print("\nNothing to do: all target rows are already applied.")
        return 0

    pending_set = set(pending)

    ing_csv_rows = read_csv(ING)
    ing_csv_fields = list(ing_csv_rows[0].keys())
    ing_json_rows = read_json(ING_JSON)

    def transform(row):
        if row["id"] not in pending_set:
            return row
        cleared = clear_row(row)
        # The clear must never lose the recipe's own record of the line.
        for field in PRESERVED_FIELDS:
            if field in row and cleared.get(field) != row.get(field):
                raise SystemExit(f"FAIL-CLOSED: {field} not preserved on {row['id']}")
        return cleared

    new_csv = [transform(r) for r in ing_csv_rows]
    new_json = [transform(r) for r in ing_json_rows]

    # Nothing outside the reviewed set may move -- the forward-protection row
    # included.
    for before, after in ((ing_csv_rows, new_csv), (ing_json_rows, new_json)):
        for old, new in zip(before, after):
            if old["id"] not in pending_set and old != new:
                raise SystemExit(f"FAIL-CLOSED: unrelated row changed: {old['id']}")

    write_csv(ING, new_csv, ing_csv_fields)
    write_json(ING_JSON, new_json)

    # Recipe rollups, recomputed from the repaired ingredient rows.
    affected = set(recipe_ids)
    csv_rollups = {rid: v for rid, v in recompute_recipe_rollups(new_csv).items()
                   if rid in affected}
    json_rollups = {rid: v for rid, v in recompute_recipe_rollups(new_json).items()
                    if rid in affected}

    recipes_csv = read_csv(RECIPES_CSV)
    recipes_csv_fields = list(recipes_csv[0].keys())
    recipes_json = read_json(RECIPES_JSON)

    csv_changed = _apply_rollups(recipes_csv, csv_rollups)
    json_changed = _apply_rollups(recipes_json, json_rollups)
    status = _recompute_status(recipes_json, new_json)

    write_csv(RECIPES_CSV, recipes_csv, recipes_csv_fields)
    write_json(RECIPES_JSON, recipes_json)

    OUT.mkdir(parents=True, exist_ok=True)
    report = {
        "policy": VEGETABLE_STOCK_GUARD_REASON,
        "guard_location":
            "nlp/entity_matcher.py::VietnameseIngredientMatcher._blocks_vegetable_stock",
        "detector": "nlp/entity_matcher.py::is_vegetable_stock_text",
        "animal_categories_vi": sorted(ANIMAL_CATEGORIES_VI),
        "animal_supplementary_codes": sorted(ANIMAL_SUPPLEMENTARY_CODES),
        "rows_cleared": len(pending),
        "rows_already_applied": len(already),
        "recipes_affected": len(recipe_ids),
        "recipe_ids": recipe_ids,
        "nutrition_removed": {k: round(v, 1) for k, v in nutrition_removed.items()},
        "recipes_csv_totals_changed": csv_changed,
        "recipes_json_totals_changed": json_changed,
        "nutrition_status": status,
        "forward_protection_rows": sorted(FORWARD_PROTECTION_ROWS),
        "rows": per_row,
        "out_of_scope": [
            "the two alias-map keys nước dùng rau / nước dùng rau củ "
            "(left inert, not removed)",
            "20002 as a repoint target (asserts real 0.0 macros; semantically wrong)",
            "a new vegetable-stock catalog entry (deferred catalog gap)",
            "the 6 nước dùng chay rows and the chay guard",
            "the 7141 catalog definition, dashi mappings, seasoning analogues",
            "141 animal broths with explicit animal semantics",
            "stale cleaned_name on 5 rows (deferred; guard reads raw_text too)",
            "rau trai -> 8054; garnish-list collapse; other matcher divergence",
        ],
    }
    (OUT / "applied_fix.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nAPPLIED. Cleared {len(pending)} rows across {len(recipe_ids)} recipes.")
    print(f"Report: {OUT / 'applied_fix.json'}")
    print("Next (AGENTS.md §11): scripts/canonicalize_recipes.py, "
          "scripts/export_canonical_json.py, then canonicalize --check.")
    return 0


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--apply", action="store_true",
                        help="write changes (default: dry-run preview)")
    args = parser.parse_args(argv)
    return run(apply=args.apply)


if __name__ == "__main__":
    raise SystemExit(main())
