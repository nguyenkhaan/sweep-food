"""Correct a small set of unambiguous, standard-portion per-piece weights for
count-based ingredient rows, then recompute affected nutrition and recipe totals.

Only well-established, low-ambiguity standard portions are corrected (a garlic
clove, a scallion stalk, a lemongrass stalk). Ambiguous large countable items
(e.g. "1 con gà", "1 trái dứa" -- whole vs. portion is undecidable from the
source text) are deliberately left unchanged and documented as a limitation.

Deterministic and idempotent: weight is set to quantity * standard_per_piece
(absolute), nutrition is rescaled from master, and affected recipe totals are
recomputed from their ingredient sums using the project's missing-aware
semantics.
"""

from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from nlp.nutrition import nutrition_value, scale_nutrition, NUTRITION_FIELDS

MASTER = ROOT / "data" / "processed" / "viendinhduong" / "master_ingredients_nutrition.csv"
ING_CSV = ROOT / "data" / "processed" / "recipes" / "recipe_ingredients.csv"
ING_JSON = ROOT / "data" / "processed" / "recipes" / "recipe_ingredients.json"
REC_CSV = ROOT / "data" / "processed" / "recipes" / "recipes.csv"
REC_JSON = ROOT / "data" / "processed" / "recipes" / "recipes.json"
REPORT = ROOT / "reports" / "eda" / "count_weight_corrections.json"

# (master_ingredient_name exact lower, unit_vi, standard grams/piece, citation)
CORRECTIONS = [
    ("tỏi", "tép", 5.0, "Standard garlic clove ~4-5 g (USDA SR: 1 clove ≈ 3 g; VN clove ~5 g)."),
    ("hành lá (hành hoa)", "nhánh", 15.0, "Standard scallion/green-onion stalk ~15 g (USDA: 1 stalk ≈ 15 g)."),
    ("sả", "cây", 20.0, "Standard lemongrass stalk ~20 g (edible trimmed portion)."),
]


def load_csv(p):
    with open(p, "r", encoding="utf-8-sig") as f:
        r = csv.DictReader(f)
        return list(r.fieldnames), list(r)


def write_csv(p, fields, rows):
    with open(p, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)


def main() -> None:
    _, masters = load_csv(MASTER)
    master_by_code = {m["code"]: m for m in masters}
    i_fields, ings = load_csv(ING_CSV)

    rule = {(name, unit): (g, cit) for name, unit, g, cit in CORRECTIONS}
    changed_rows = 0
    affected_recipes = set()
    per_rule_counts = {f"{n}|{u}": 0 for n, u, _, _ in CORRECTIONS}

    for r in ings:
        name = (r.get("master_ingredient_name") or "").strip().lower()
        unit = (r.get("unit_vi") or "").strip()
        key = (name, unit)
        if key not in rule:
            continue
        qty = nutrition_value(r.get("required_quantity"))
        code = (r.get("master_ingredient_code") or "").strip()
        if qty is None or qty <= 0 or not code:
            continue
        per_piece, _ = rule[key]
        new_w = round(qty * per_piece, 1)
        r["estimated_weight_g"] = str(new_w)
        m = master_by_code.get(code)
        if m:
            factor = new_w / 100.0
            for field, source in NUTRITION_FIELDS.items():
                scaled = scale_nutrition(m.get(source), factor, 1)
                r[field] = "" if scaled is None else str(scaled)
        changed_rows += 1
        affected_recipes.add(r["recipe_id"])
        per_rule_counts[f"{name}|{unit}"] += 1

    write_csv(ING_CSV, i_fields, ings)

    # sync JSON ingredient rows (weight + macros) for changed rows
    json_ings = json.loads(ING_JSON.read_text(encoding="utf-8"))
    by_id = {r["id"]: r for r in ings}
    for jr in json_ings:
        src = by_id.get(jr.get("id"))
        if src and src["recipe_id"] in affected_recipes:
            jr["estimated_weight_g"] = float(src["estimated_weight_g"])
            for field in NUTRITION_FIELDS:
                v = src.get(field)
                jr[field] = None if (v is None or v == "") else float(v)
    ING_JSON.write_text(json.dumps(json_ings, ensure_ascii=False, indent=2), encoding="utf-8")

    # recompute totals for affected recipes only, from their ingredient sums
    totals = {rid: {"calories": 0.0, "protein_g": 0.0, "fat_g": 0.0, "carbs_g": 0.0} for rid in affected_recipes}
    for r in ings:
        rid = r["recipe_id"]
        if rid in totals:
            for field in ("calories", "protein_g", "fat_g", "carbs_g"):
                v = nutrition_value(r.get(field))
                if v is not None:
                    totals[rid][field] += v

    rec_fields, recs = load_csv(REC_CSV)
    col = {"calories": "total_calories", "protein_g": "total_protein_g",
           "fat_g": "total_fat_g", "carbs_g": "total_carbs_g"}
    for rec in recs:
        if rec["id"] in totals:
            t = totals[rec["id"]]
            for k, c in col.items():
                rec[c] = str(round(t[k], 1))
    write_csv(REC_CSV, rec_fields, recs)

    json_recs = json.loads(REC_JSON.read_text(encoding="utf-8"))
    new_tot = {rec["id"]: rec for rec in recs}
    for jr in json_recs:
        src = new_tot.get(jr.get("id"))
        if src and jr.get("id") in totals:
            for c in col.values():
                jr[c] = src[c]
    REC_JSON.write_text(json.dumps(json_recs, ensure_ascii=False, indent=2), encoding="utf-8")

    report = {
        "corrections": [{"master_ingredient_name": n, "unit_vi": u, "grams_per_piece": g, "citation": c}
                        for n, u, g, c in CORRECTIONS],
        "ingredient_rows_changed": changed_rows,
        "per_rule_rows": per_rule_counts,
        "recipes_recomputed": len(affected_recipes),
        "note": "Ambiguous large countable items (e.g. '1 con ga', '1 trai dua') left unchanged; see DATASHEET limitations.",
    }
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Corrected {changed_rows} rows across {len(affected_recipes)} recipes.")
    for k, v in per_rule_counts.items():
        print(f"  {k}: {v}")
    print(f"Report -> {REPORT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
