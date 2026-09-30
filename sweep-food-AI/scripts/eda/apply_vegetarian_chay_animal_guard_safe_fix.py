"""Apply the reviewed vegetarian ("chay") animal-identity guard to the 11 live
processed rows it blocks. Default previews; --apply writes.

The guard itself lives in nlp/entity_matcher.py (_blocks_vegetarian, reason
VEGETARIAN_PHRASE_ANIMAL_TARGET) and stops the bad resolution from ever being
produced again. This script repairs the rows that were already written before
the guard existed; it introduces no policy of its own.

REVIEWED POLICY. When ingredient evidence -- the union of NFC-normalized
raw_text and cleaned_name -- carries the standalone token "chay", and the
resolved catalog target is an animal identity, the match is blocked terminally
and the row becomes UNMATCHED.

    "chay" is the explicit Vietnamese vegetarian marker. "Đùi gà chay 250 gr"
    is a seitan drumstick analogue, and was being scored as 250 g of chicken
    thigh; "Xúc xích chay 100g" was being scored as 535 kcal of pork sausage.

ANIMAL IDENTITY is decided by catalog metadata, never by animal-name
substrings:

    category_vi in {"Thịt và sản phẩm chế biến",
                    "Thủy sản và sản phẩm chế biến"}     (199 entries)
    OR code in the 11 reviewed supplementary codes        (canned meat/fish
    11015-11023, pork lard 6003/6004 -- animal identities filed under
    non-animal categories).

    A substring rule would have been wrong: 20007 "Nấm đùi gà" is king oyster
    MUSHROOM, and "nấm đùi gà chay" resolves to it at 0.67. The category test
    exempts it structurally, with no phrase special-case. Symmetrically, the
    live catalog contains ZERO vegan or imitation entries filed under the two
    animal categories, so the test is exact rather than approximate.

THE 11 ROWS (measured against the live 63,943-row processed dataset, not
inferred from the audit):

    2 rows  đùi gà chay      -> 7088 Đùi gà        (Thịt)
    1 row   xúc xích chay    -> 7077 Xúc xích      (Thịt)
    1 row   nem chua chay    -> 7073 Nem chua      (Thịt)
    1 row   thịt cua chay    -> 8069 Thịt cua      (Thủy sản)
    6 rows  nước dùng chay   -> 7141 Nước dùng     (Thịt)

All 11 become UNMATCHED. There is no repoint target: the catalog carries only
two imitation-meat identities (20039 Thịt chay, 20040 Chả lụa chay), and
neither is a drumstick, a sausage, fermented pork, crab meat or a broth.
Pointing these rows at 20039 would assert 50 g protein / 100 g for a product
nobody measured, which AGENTS.md §5 and §7 forbid. UNMATCHED is the correct
verdict when no valid catalog identity exists.

WHY THE ALIASES ARE NOT TOUCHED. "đùi gà chay", "xúc xích chay", "nem chua
chay" and "thịt cua chay" remain in ingredient_alias_map.json pointing at their
animal codes. Removing them would not fix anything -- every one is re-derived
by SUBPHRASE_CATALOG_MATCH from the catalog head ("đùi gà chay" -> 7088 at
0.55, "thịt cua chay" -> 8069 at 0.62, both over the 0.35 threshold) -- and the
guard makes them inert, which keeps this fix's blast-radius measurement clean.
Removing or repointing them is a separate reviewed decision (AGENTS.md §6/§18).

EXPLICITLY OUT OF SCOPE (recorded, deliberately unchanged):

  * Seasoning analogues. 213 chay rows resolve into "Gia vị, nước chấm"
    ("nước mắm chay" -> 13017, "dầu hào chay" -> 13027, "hạt nêm chay" ->
    13026, "sa tế chay" -> 13054). They are exempt structurally, not by
    special case. This is a scope decision, NOT a claim that those mappings
    are semantically perfect -- 13017 is literally fish sauce. They are
    teaspoon-dose condiments whose profile is close to their animal
    counterpart, the catalog has no vegetarian condiment identity to move them
    to, and blocking them would destroy real coverage for no semantic gain.
  * 20002 "Nước lọc (nước dùng nấu)" as a replacement for nước dùng chay.
  * The 61 rows already correct on 20039/20040.
  * Residual rows whose vegetarian intent is stated only at recipe level and
    carries no ingredient-level marker -- "Chà bông chay từ sườn non" (the
    ingredient line reads "6 miếng sườn non" -> 7053) and "Nước dùng rau củ
    1,6 lít" -> 7141. Neither is inside this guard's predicate.
  * Dairy/egg policy: no chay row reaches those categories and no
    "trứng chay"/"sữa chay" phrase exists, so widening would be unevidenced.
  * Any catalog repair, any alias-map edit, any other meat-band finding.

NUTRITION (AGENTS.md §4, §9). Clearing a row sets calories/protein_g/fat_g/
carbs_g to NULL -- unknown -- never to 0.0, and match_confidence to null rather
than the 0.0 rejection sentinel. raw_text, cleaned_name, required_quantity,
unit_vi, unit, preparation_note and estimated_weight_g are all preserved: the
row still records what the recipe asked for, it just no longer claims a master
identity. Recipe rollups for the 11 affected recipes are recomputed from the
repaired ingredient rows, removing 1,663.5 kcal in total (1,579.0 from the five
meat/seafood rows, 84.5 from the six broth rows -- 7141 is nutritionally
near-empty at 1 kcal/100 g with blank macros).

Safety model (fail closed, idempotent, dry-run by default):
  - The guard must be live in nlp.entity_matcher before anything is written,
    and must actually block each of the reviewed phrases. A run against an
    unguarded matcher aborts.
  - The blocked set is RECOMPUTED from live data through the real
    is_chay_text() predicate and the real catalog categories, then cross-checked
    against the pinned id set. Drift in either direction aborts before any
    write, so this script cannot run against a dataset that has moved.
  - Every target row is pinned by id AND exact raw_text AND cleaned_name AND
    its exact pre-fix code/name/method/confidence. Each must be either
    "pending" or "already_applied"; anything else aborts the ENTIRE run.
  - Every code this fix reads must exist in the live catalog under its exact
    current name_vi (AGENTS.md §3).
  - Rows outside the pinned set are asserted byte-identical after the write.
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
    VEGETARIAN_GUARD_REASON,
    VietnameseIngredientMatcher,
    is_chay_text,
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
OUT = ROOT / "reports/eda/vegetarian_chay_animal_guard"

# The reviewed blast radius. Pinned by full id, with the exact pre-fix state
# each row must carry. Ordered by identity for readability only.
#   id -> (raw_text, cleaned_name, code, name, method, confidence)
TARGET_ROWS = {
    "f2c392cf-57dc-4f80-be17-bcf76ef95243": (
        "Đùi gà chay 250 gr", "đùi gà chay", "7088", "Đùi gà",
        "PRESET_ALIAS_MATCH", "0.98"),
    "dcc433c7-a4cf-41a9-8280-40cf7107c41b": (
        "Đùi gà chay 300 gr", "đùi gà chay", "7088", "Đùi gà",
        "PRESET_ALIAS_MATCH", "0.98"),
    "fb37da49-f7ec-4c4e-a42a-0a1b55686bf2": (
        "Xúc xích chay 100g", "xúc xích chay", "7077", "Xúc xích",
        "PRESET_ALIAS_MATCH", "0.98"),
    "256d7443-eff2-4f8e-85ab-ecd60f822547": (
        "Nem chua chay 150g", "nem chua chay", "7073", "Nem chua",
        "PRESET_ALIAS_MATCH", "0.98"),
    "7c4d60bc-5848-4220-8987-9a53380c22d6": (
        "Thịt cua chay: 100g", "thịt cua chay", "8069", "Thịt cua",
        "PRESET_ALIAS_MATCH", "0.98"),
    "1d643050-5137-42a0-b195-c9d6590fd020": (
        "Nước dùng chay: 250ml", "nước dùng chay", "7141", "Nước dùng",
        "PRESET_ALIAS_MATCH", "0.98"),
    "22d71f4f-378d-405a-b0f7-5031b5a2b3d3": (
        "Nước dùng chay 2 lít", "nước dùng chay", "7141", "Nước dùng",
        "PRESET_ALIAS_MATCH", "0.98"),
    "318fddc7-e512-473c-9cf3-86db26c42854": (
        "Nước dùng chay 1.5 lít", "nước dùng chay", "7141", "Nước dùng",
        "PRESET_ALIAS_MATCH", "0.98"),
    "bb9a520c-dcbf-4c31-a776-09cf853410a5": (
        "Nước dùng chay 2,5 lít (Nấu từ củ sắn, củ cải trăng, susu, cải thào, "
        "bắp mỹ, nấm đông cô)", "nước dùng chay", "7141", "Nước dùng",
        "PRESET_ALIAS_MATCH", "0.98"),
    "2175a41f-3184-41a9-bfd9-eb99b942ea17": (
        "Nước dùng chay: 1L", "nước dùng chay", "7141", "Nước dùng",
        "PRESET_ALIAS_MATCH", "0.98"),
    "1e0d1e8b-ec4e-4155-9741-167efaa010ee": (
        "Nước dùng chay : 1,2 lít", "nước dùng chay", "7141", "Nước dùng",
        "PRESET_ALIAS_MATCH", "0.98"),
}
assert len(TARGET_ROWS) == 11

# Every code this fix reads, with its exact current live name_vi.
CODE_NAMES = {
    "7073": "Nem chua",
    "7077": "Xúc xích",
    "7088": "Đùi gà",
    "7141": "Nước dùng",
    "8069": "Thịt cua",
}

# Phrases the guard must actually block for this fix to be coherent. Checked
# against the live matcher before any write.
GUARDED_PHRASES = ("đùi gà chay", "xúc xích chay", "nem chua chay",
                   "thịt cua chay", "nước dùng chay")

# Phrases that must keep resolving -- the reviewed exemptions. A guard that
# blocked these would be over-broad and must not be applied.
EXEMPT_PHRASES = {
    "thịt bò chay lát": "20039",
    "chả lụa chay": "20040",
    "nấm đùi gà chay": "20007",
    "nước mắm chay": "13017",
    "dầu hào chay": "13027",
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
        if result["method"] != "UNMATCHED" or result.get("guard") != VEGETARIAN_GUARD_REASON:
            raise SystemExit(
                f"FAIL-CLOSED: guard is not live -- {phrase!r} resolved as "
                f"{result['method']} ({result['matched_item'].get('code')})"
            )
    for phrase, code in EXEMPT_PHRASES.items():
        result = matcher.match(phrase)
        if result["method"] == "UNMATCHED" or result["matched_item"].get("code") != code:
            raise SystemExit(
                f"FAIL-CLOSED: guard is over-broad -- exempt {phrase!r} resolved as "
                f"{result['method']} ({result['matched_item'].get('code')}), expected {code}"
            )
    return matcher


def classify(row, catalog):
    """pending | already_applied -- anything else aborts the run."""
    pinned = TARGET_ROWS[row["id"]]
    raw_text, cleaned_name, code, name, method, confidence = pinned

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

    # Recompute the blocked population from live data rather than trusting the
    # pinned list. Drift in EITHER direction aborts.
    recomputed = {
        r["id"] for r in rows
        if is_chay_text(r.get("raw_text"), r.get("cleaned_name"))
        and is_animal_code(catalog, r.get("master_ingredient_code"))
    }
    pending_pinned = {
        rid for rid in TARGET_ROWS
        if (next(r for r in rows if r["id"] == rid).get("master_ingredient_code") or "").strip()
    }
    if recomputed != pending_pinned:
        raise SystemExit(
            "FAIL-CLOSED: blast radius drift.\n"
            f"  recomputed-but-not-pinned: {sorted(recomputed - pending_pinned)}\n"
            f"  pinned-but-not-recomputed: {sorted(pending_pinned - recomputed)}"
        )

    by_id = {r["id"]: r for r in rows}
    missing = set(TARGET_ROWS) - set(by_id)
    if missing:
        raise SystemExit(f"FAIL-CLOSED: target rows absent from dataset: {sorted(missing)}")

    states = {rid: classify(by_id[rid], catalog) for rid in TARGET_ROWS}

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
            "reason": VEGETARIAN_GUARD_REASON,
        })

    recipe_ids = sorted({by_id[rid].get("recipe_id") for rid in TARGET_ROWS})
    return catalog, states, per_row, nutrition_removed, recipe_ids


def run(apply=False):
    verify_guard_is_live()
    catalog, states, per_row, nutrition_removed, recipe_ids = build_plan()

    pending = sorted(rid for rid, s in states.items() if s == "pending")
    already = sorted(rid for rid, s in states.items() if s == "already_applied")

    print(f"Guard        : {VEGETARIAN_GUARD_REASON}")
    print(f"Target rows  : {len(TARGET_ROWS)} ({len(pending)} pending, {len(already)} already applied)")
    print(f"Recipes      : {len(recipe_ids)}")
    print("Nutrition removed: " + ", ".join(
        f"{k}={round(v, 1)}" for k, v in nutrition_removed.items()))
    print()
    for entry in per_row:
        before = entry["before"]
        print(f"  [{entry['state']:15}] {entry['id'][:8]}  {entry['raw_text'][:46]:46}"
              f"  {before['master_ingredient_code'] or '-':>5} "
              f"{before['master_ingredient_name'] or '-':16} -> UNMATCHED")

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

    # Nothing outside the reviewed set may move.
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
        "policy": "VEGETARIAN_PHRASE_ANIMAL_TARGET",
        "guard_location": "nlp/entity_matcher.py::VietnameseIngredientMatcher._blocks_vegetarian",
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
        "rows": per_row,
        "out_of_scope": [
            "seasoning analogues in Gia vị, nước chấm (213 rows)",
            "the four hazardous alias-map keys (left inert, not removed)",
            "20002 as a replacement for nước dùng chay",
            "Chà bông chay từ sườn non; Nước dùng rau củ (no ingredient-level marker)",
            "dairy/egg policy",
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
