"""Fix I-3a: impossible over-estimated weights on direct mass/volume units.

For an ingredient line whose source explicitly states a mass/volume quantity
(unit_vi in {g, kg, ml, lít}), the released conversion spec (DATASHEET §2.3:
g/ml = 1 g/ml, kg/lít = 1000 g) makes the weight deterministic: exactly
`required_quantity x factor`. Domain caps (e.g. frying-oil absorption) only ever
*reduce* the consumed weight, never inflate it, so any row whose
`estimated_weight_g` *exceeds* `required_quantity x factor` is a physically
impossible value and an unambiguous bug (e.g. "Nấm đùi gà 20 gr" -> 2400 g,
"Trứng cút 20 gr" -> 1100 g). Those rows are reset to the stated mass and their
nutrition + recipe roll-ups are recomputed from the audited master table.

Deliberately NOT touched (ambiguous, out of scope -> see I-3b in data_issue.md):
- under-estimates (weight < qty x factor): may be intentional caps (frying oil
  ~= qty x 0.15) or compound-split children where the parent weight was divided;
  the correct value cannot be derived deterministically from current columns.
- count/vague units: per-piece grams are approximations by design.

Deterministic and idempotent: re-running changes nothing once applied.
"""

from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from nlp.nutrition import NUTRITION_FIELDS, nutrition_value, scale_nutrition

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

RECIPES_DIR = ROOT / "data" / "processed" / "recipes"
MASTER_PATH = ROOT / "data" / "processed" / "viendinhduong" / "master_ingredients_nutrition.csv"
REPORT = ROOT / "reports" / "eda" / "measure_overestimate_fix.json"

ING_PAIRS = (
    (RECIPES_DIR / "recipe_ingredients.csv", RECIPES_DIR / "recipe_ingredients.json"),
    (RECIPES_DIR / "canonical_recipe_ingredients.csv", RECIPES_DIR / "canonical_recipe_ingredients.json"),
)
RECIPE_PAIRS = (
    (RECIPES_DIR / "recipes.csv", RECIPES_DIR / "recipes.json"),
    (RECIPES_DIR / "canonical_recipes.csv", RECIPES_DIR / "canonical_recipes.json"),
)

MEASURE_FACTOR = {"g": 1.0, "kg": 1000.0, "ml": 1.0, "lít": 1000.0, "lit": 1000.0}
# Only correct clear over-estimates; a small tolerance avoids float noise.
OVER_TOLERANCE = 1.05


def load_master() -> dict:
    with open(MASTER_PATH, "r", encoding="utf-8-sig") as f:
        return {row["code"].strip(): row for row in csv.DictReader(f) if row.get("code")}


def fix_ingredient_rows(rows: list[dict], master: dict) -> list[dict]:
    """Mutate rows in place; return the list of applied fixes for the report."""
    fixes = []
    for row in rows:
        method = (row.get("match_method") or "").strip().upper()
        if method == "UNMATCHED":
            continue
        unit_vi = (row.get("unit_vi") or "").strip()
        factor = MEASURE_FACTOR.get(unit_vi)
        if factor is None:
            continue
        qty = nutrition_value(row.get("required_quantity"))
        old_w = nutrition_value(row.get("estimated_weight_g"))
        if qty is None or qty <= 0 or old_w is None:
            continue
        expected = round(qty * factor, 1)
        if old_w <= expected * OVER_TOLERANCE:
            continue  # not an over-estimate -> leave untouched

        row["estimated_weight_g"] = str(expected)
        code = (row.get("master_ingredient_code") or "").strip()
        m_info = master.get(code)
        if m_info and expected > 0:
            ratio = expected / 100.0
            for field, source in NUTRITION_FIELDS.items():
                scaled = scale_nutrition(m_info.get(source), ratio, 1)
                row[field] = "" if scaled is None else str(scaled)
        fixes.append({
            "id": row.get("id"),
            "recipe_id": row.get("recipe_id"),
            "raw_text": row.get("raw_text"),
            "unit_vi": unit_vi,
            "required_quantity": qty,
            "old_weight_g": old_w,
            "new_weight_g": expected,
        })
    return fixes


def write_ingredient_pair(csv_path: Path, json_path: Path, rows: list[dict], fieldnames) -> None:
    with open(csv_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    with open(json_path, "r", encoding="utf-8") as f:
        json_rows = json.load(f)
    by_id = {r["id"]: r for r in rows}
    for jr in json_rows:
        src = by_id.get(jr.get("id"))
        if src is None:
            continue
        jr["estimated_weight_g"] = nutrition_value(src.get("estimated_weight_g"))
        for field in NUTRITION_FIELDS:
            jr[field] = nutrition_value(src.get(field))
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(json_rows, f, ensure_ascii=False, indent=2)


def rollup(rows: list[dict]) -> tuple[dict, dict]:
    totals, missing = {}, {}
    for row in rows:
        rid = row["recipe_id"]
        t = totals.setdefault(rid, {"calories": 0.0, "protein": 0.0, "fat": 0.0, "carbs": 0.0, "count": 0})
        missing.setdefault(rid, 0)
        t["count"] += 1
        cal = nutrition_value(row.get("calories"))
        if cal is None:
            missing[rid] += 1
        else:
            t["calories"] += cal
        for key, field in (("protein", "protein_g"), ("fat", "fat_g"), ("carbs", "carbs_g")):
            val = nutrition_value(row.get(field))
            if val is not None:
                t[key] += val
    return totals, missing


def write_recipe_pair(csv_path: Path, json_path: Path, totals: dict, missing: dict) -> None:
    with open(csv_path, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        recipe_rows = list(reader)
    for r in recipe_rows:
        t = totals.get(r["id"])
        if not t:
            continue
        r["total_calories"] = str(round(t["calories"], 1))
        r["total_protein_g"] = str(round(t["protein"], 1))
        r["total_fat_g"] = str(round(t["fat"], 1))
        r["total_carbs_g"] = str(round(t["carbs"], 1))
        r["ingredients_count"] = str(t["count"])
    with open(csv_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(recipe_rows)

    with open(json_path, "r", encoding="utf-8") as f:
        json_rows = json.load(f)
    by_id = {r["id"]: r for r in recipe_rows}
    for jr in json_rows:
        src = by_id.get(jr.get("id"))
        if src is None:
            continue
        for col in ("total_calories", "total_protein_g", "total_fat_g", "total_carbs_g"):
            jr[col] = float(src[col])
        jr["ingredients_count"] = int(src["ingredients_count"])
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(json_rows, f, ensure_ascii=False, indent=2)


def main() -> None:
    master = load_master()
    all_fixes = []
    canonical_rows = None

    for csv_path, json_path in ING_PAIRS:
        with open(csv_path, "r", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            fieldnames = list(reader.fieldnames)
            rows = list(reader)
        fixes = fix_ingredient_rows(rows, master)
        write_ingredient_pair(csv_path, json_path, rows, fieldnames)
        print(f"{csv_path.name}: fixed {len(fixes)} over-estimated measure rows.")
        if not all_fixes:
            all_fixes = fixes
        if csv_path.name.startswith("canonical"):
            canonical_rows = rows

    # Recipe roll-ups computed from the canonical ingredient rows (identical set).
    totals, missing = rollup(canonical_rows)
    for csv_path, json_path in RECIPE_PAIRS:
        write_recipe_pair(csv_path, json_path, totals, missing)
        print(f"{csv_path.name}: recomputed roll-ups.")

    REPORT.parent.mkdir(parents=True, exist_ok=True)
    with open(REPORT, "w", encoding="utf-8") as f:
        json.dump({"fixed_rows": len(all_fixes), "fixes": all_fixes}, f, ensure_ascii=False, indent=2)
    print(f"Report -> {REPORT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
