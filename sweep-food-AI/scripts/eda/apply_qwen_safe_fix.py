"""Apply the accepted Qwen Class-A correction. Default previews; --apply writes.

Clears ONLY rows classified 'A' (clearly incorrect identity) by
scripts/eda/audit_qwen_matching.py: reviewed, conservative false positives
where a Qwen recovery resolved a raw ingredient to a master identity that
current catalog evidence shows is wrong (e.g. "hanh la" (scallion) resolved to
a code that now names "Chuoi xanh" (green banana)).

Class B (ambiguous), C (likely valid) and D (dangling code) rows are left
untouched -- ambiguous evidence must not be force-resolved either way, and D
rows are a separate structural question (no master identity is invented here).

Scope: data/processed/recipes/recipe_ingredients.{csv,json} and the recipe-level
rollup totals in data/processed/recipes/recipes.{csv,json}. Canonical outputs
(data/processed/recipes/canonical_*.csv/json, recipe_canonical_mapping.csv) are
INTENTIONALLY NOT regenerated here -- fix/canonical-cutover is a separate,
still-open PR, and this script does not know its final canonicalization logic.
Canonical files will be stale for the corrected rows until that PR lands and
canonical regeneration is re-run afterward.

KNOWN DEPENDENCY (tracked by the upcoming fix/unmatched-nutrition task, not
addressed here): scripts/reprocess_recipe_weights_and_nutrition.py currently
rewrites blank/null nutrition on ANY UNMATCHED row -- including the 162 rows
this script clears -- to a literal measured zero. Re-running that script after
this fix will not resurrect the wrong match identity (code/name/method/
confidence stay correctly blank), but it WILL collapse the missing-vs-zero
nutrition distinction this fix relies on. See tests/test_qwen_reprocess_interaction.py.
"""

import argparse
import csv
import json
from collections import defaultdict
from pathlib import Path

from scripts.eda.audit_qwen_matching import ING, OUT, audit

ROOT = Path(__file__).resolve().parents[2]
ING_JSON = ING.with_suffix(".json")
RECIPES_CSV = ROOT / "data/processed/recipes/recipes.csv"
RECIPES_JSON = ROOT / "data/processed/recipes/recipes.json"

CLEARED_MATCH_FIELDS = {
    "master_ingredient_code": None,
    "master_ingredient_name": None,
    "match_confidence": None,
    "match_method": "UNMATCHED",
}
CLEARED_NUTRITION_FIELDS = {"calories": None, "protein_g": None, "fat_g": None, "carbs_g": None}


def read_csv(path):
    with path.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def write_csv(path, rows, fieldnames):
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def write_json(path, rows):
    path.write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")


def clear_row(row):
    """Apply the clear in place, touching only the known match/nutrition keys.

    Any other keys present on the row (JSON-only fields included) pass through
    unchanged -- this must never silently narrow a record to a fixed schema.
    """
    row = dict(row)
    row.update(CLEARED_MATCH_FIELDS)
    row.update(CLEARED_NUTRITION_FIELDS)
    return row


def recompute_recipe_rollups(ingredient_rows):
    rollups = defaultdict(lambda: {"calories": 0.0, "protein_g": 0.0, "fat_g": 0.0, "carbs_g": 0.0})
    for r in ingredient_rows:
        rid = r.get("recipe_id")
        if not rid:
            continue
        for field in ("calories", "protein_g", "fat_g", "carbs_g"):
            try:
                rollups[rid][field] += float(r.get(field) or 0.0)
            except (TypeError, ValueError):
                pass
    return rollups


def build_plan():
    """Read-only: determine which rows would change and by how much."""
    result = audit()
    class_a_ids = {r["id"] for r in result["rows"] if r["class"] == "A"}
    ing_rows = read_csv(ING)
    cleared_ids = []
    nutrition_removed = {"calories": 0.0, "protein_g": 0.0, "fat_g": 0.0, "carbs_g": 0.0}
    for row in ing_rows:
        if row["id"] in class_a_ids:
            cleared_ids.append(row["id"])
            for field in nutrition_removed:
                try:
                    nutrition_removed[field] += float(row.get(field) or 0.0)
                except (TypeError, ValueError):
                    pass
    return result, class_a_ids, cleared_ids, nutrition_removed


def _new_totals(rollup):
    return {
        "total_calories": str(round(rollup["calories"], 1)),
        "total_protein_g": str(round(rollup["protein_g"], 1)),
        "total_fat_g": str(round(rollup["fat_g"], 1)),
        "total_carbs_g": str(round(rollup["carbs_g"], 1)),
    }


def _apply_rollups(records, rollups):
    """Update only the four total_* keys already present on each record,
    leaving every other key (CSV or JSON-only) untouched. Returns changed count."""
    changed = 0
    for rec in records:
        rid = rec.get("id")
        if rid not in rollups:
            continue
        new_totals = _new_totals(rollups[rid])
        if any(rec.get(k) != v for k, v in new_totals.items() if k in rec):
            changed += 1
        for k, v in new_totals.items():
            if k in rec:
                rec[k] = v
    return changed


def run(apply=False):
    result, class_a_ids, cleared_ids, nutrition_removed = build_plan()
    if len(cleared_ids) != len(class_a_ids):
        raise ValueError("Row-id mismatch between audit classification and processed CSV")

    # Ingredients: CSV and JSON are read/cleared/written independently so
    # neither format's field set is ever narrowed to the other's.
    ing_csv_rows = read_csv(ING)
    ing_csv_fields = list(ing_csv_rows[0].keys())
    new_ing_csv_rows = [clear_row(r) if r["id"] in class_a_ids else r for r in ing_csv_rows]

    ing_json_rows = read_json(ING_JSON)
    new_ing_json_rows = [clear_row(r) if r["id"] in class_a_ids else r for r in ing_json_rows]

    # Recipe rollups are computed once from the corrected ingredient rows and
    # applied independently to the CSV and JSON recipe records.
    rollups = recompute_recipe_rollups(new_ing_csv_rows)

    recipes_csv_rows = read_csv(RECIPES_CSV)
    recipes_csv_fields = list(recipes_csv_rows[0].keys())
    changed_recipes = _apply_rollups(recipes_csv_rows, rollups)

    recipes_json_rows = read_json(RECIPES_JSON)
    _apply_rollups(recipes_json_rows, rollups)

    report = {
        "status": "applied" if apply else "preview",
        "corrected_A": len(cleared_ids),
        "remaining_classes": {c: result["summary"]["class_counts"][c] for c in ("A", "B", "C", "D") if c != "A"} | {"A": 0 if apply else result["summary"]["class_counts"]["A"]},
        "recipes_with_changed_totals": changed_recipes,
        "nutrition_removed": {k: round(v, 1) for k, v in nutrition_removed.items()},
        "cleared_row_ids": sorted(cleared_ids),
        "canonical_note": (
            "Canonical outputs (canonical_recipes.csv/json, canonical_recipe_ingredients.csv/json, "
            "recipe_canonical_mapping.csv) are NOT regenerated by this script and are now stale for "
            "these rows/recipes. Regenerate canonical outputs after fix/canonical-cutover lands."
        ),
        "not_recomputed_note": (
            "Recipe-level nutrition_status/missing_nutrition_count (if present in recipes.json) are "
            "NOT recalculated here -- that is a separate, leader-owned completeness policy. Clearing "
            "these 162 rows' nutrition may make such flags stale for the affected recipes; re-run "
            "that policy's own tooling separately if needed."
        ),
    }

    if apply:
        write_csv(ING, new_ing_csv_rows, ing_csv_fields)
        write_json(ING_JSON, new_ing_json_rows)
        write_csv(RECIPES_CSV, recipes_csv_rows, recipes_csv_fields)
        write_json(RECIPES_JSON, recipes_json_rows)
        OUT.mkdir(parents=True, exist_ok=True)
        (OUT / "applied_fix.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    return report


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args(argv)
    report = run(apply=args.apply)
    print(json.dumps({k: v for k, v in report.items() if k != "cleared_row_ids"}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
