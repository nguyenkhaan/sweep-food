"""Add per-serving nutrition metrics and recipe-level anomaly flags (Q-2, Q-3).

Rationale
---------
1. Per-serving macros (calories_per_serving, protein_per_serving,
   fat_per_serving, carbs_per_serving) standardize nutrition across recipes
   with different default_servings (ranging 1-12, mean 3.4), preventing
   downstream recommendation models from comparing raw recipe totals.
2. nutrition_anomaly_flag (0 or 1) explicitly labels recipes with gross
   nutrition distortions (106 recipes, ~1.9%) without silently modifying or
   deleting source data (per AGENTS.md §7). Downstream rankers and filters can
   safely exclude or penalize flagged recipes.

Deterministic criteria for nutrition_anomaly_flag == 1:
- total_calories > 15,000 kcal
- total_fat_g > 1,000 g
- total_carbs_g > 1,500 g
- calories_per_serving > 4,000 kcal/serving
- calories_per_serving < 50 kcal/serving
- total_calories <= 0 kcal
- default_servings <= 0

The script is deterministic and idempotent.
"""

from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PROCESSED_DIR = ROOT / "data" / "processed" / "recipes"
REPORT_PATH = ROOT / "reports" / "eda" / "recipe_nutrition_anomalies_and_servings.json"

RECIPE_PAIRS = (
    (PROCESSED_DIR / "recipes.csv", PROCESSED_DIR / "recipes.json"),
    (PROCESSED_DIR / "canonical_recipes.csv", PROCESSED_DIR / "canonical_recipes.json"),
)

NEW_COLS = [
    "calories_per_serving",
    "protein_per_serving",
    "fat_per_serving",
    "carbs_per_serving",
    "nutrition_anomaly_flag",
]


def _float(val) -> float:
    try:
        return float(val or 0.0)
    except (ValueError, TypeError):
        return 0.0


def compute_metrics(row: dict) -> dict:
    servings = _float(row.get("default_servings"))
    if servings <= 0:
        servings = 1.0

    cals = _float(row.get("total_calories"))
    prot = _float(row.get("total_protein_g"))
    fat = _float(row.get("total_fat_g"))
    carbs = _float(row.get("total_carbs_g"))

    cals_per_serv = round(cals / servings, 1)
    prot_per_serv = round(prot / servings, 1)
    fat_per_serv = round(fat / servings, 1)
    carbs_per_serv = round(carbs / servings, 1)

    # Anomaly conditions
    is_anomaly = (
        cals > 15000.0
        or fat > 1000.0
        or carbs > 1500.0
        or cals_per_serv > 4000.0
        or cals_per_serv < 50.0
        or cals <= 0.0
        or _float(row.get("default_servings")) <= 0
    )

    reasons = []
    if cals > 15000.0:
        reasons.append("HIGH_TOTAL_CALORIES")
    if fat > 1000.0:
        reasons.append("HIGH_TOTAL_FAT")
    if carbs > 1500.0:
        reasons.append("HIGH_TOTAL_CARBS")
    if cals_per_serv > 4000.0:
        reasons.append("HIGH_SERVING_CALORIES")
    if cals_per_serv < 50.0:
        reasons.append("LOW_SERVING_CALORIES")
    if cals <= 0.0:
        reasons.append("ZERO_CALORIES")
    if _float(row.get("default_servings")) <= 0:
        reasons.append("INVALID_SERVINGS")

    return {
        "calories_per_serving": cals_per_serv,
        "protein_per_serving": prot_per_serv,
        "fat_per_serving": fat_per_serv,
        "carbs_per_serving": carbs_per_serv,
        "nutrition_anomaly_flag": 1 if is_anomaly else 0,
        "anomaly_reasons": reasons,
    }


def process_pair(csv_path: Path, json_path: Path) -> dict:
    with open(csv_path, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        old_fieldnames = list(reader.fieldnames)
        rows = list(reader)

    # Insert new columns after total_carbs_g if present, else append
    new_fieldnames = []
    inserted = False
    for col in old_fieldnames:
        if col in NEW_COLS:
            continue  # Avoid duplicate columns on re-run
        new_fieldnames.append(col)
        if col == "total_carbs_g":
            new_fieldnames.extend(NEW_COLS)
            inserted = True
    if not inserted:
        new_fieldnames.extend([c for c in NEW_COLS if c not in new_fieldnames])

    flagged_recipes = []

    for r in rows:
        metrics = compute_metrics(r)
        r["calories_per_serving"] = str(metrics["calories_per_serving"])
        r["protein_per_serving"] = str(metrics["protein_per_serving"])
        r["fat_per_serving"] = str(metrics["fat_per_serving"])
        r["carbs_per_serving"] = str(metrics["carbs_per_serving"])
        r["nutrition_anomaly_flag"] = str(metrics["nutrition_anomaly_flag"])

        if metrics["nutrition_anomaly_flag"] == 1:
            flagged_recipes.append({
                "id": r.get("id"),
                "name": r.get("name"),
                "source_platform": r.get("source_platform"),
                "default_servings": _float(r.get("default_servings")),
                "total_calories": _float(r.get("total_calories")),
                "calories_per_serving": metrics["calories_per_serving"],
                "reasons": metrics["anomaly_reasons"],
            })

    # Write CSV
    with open(csv_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=new_fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    # Write JSON with exact numeric types
    with open(json_path, "r", encoding="utf-8") as f:
        json_rows = json.load(f)

    metrics_by_id = {r["id"]: compute_metrics(r) for r in rows}
    for jr in json_rows:
        rid = jr.get("id")
        m = metrics_by_id.get(rid)
        if m:
            jr["calories_per_serving"] = m["calories_per_serving"]
            jr["protein_per_serving"] = m["protein_per_serving"]
            jr["fat_per_serving"] = m["fat_per_serving"]
            jr["carbs_per_serving"] = m["carbs_per_serving"]
            jr["nutrition_anomaly_flag"] = m["nutrition_anomaly_flag"]

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(json_rows, f, ensure_ascii=False, indent=2)

    return {
        "file": str(csv_path.name),
        "total_recipes": len(rows),
        "flagged_anomalies": len(flagged_recipes),
        "anomaly_percentage": round(len(flagged_recipes) / len(rows) * 100, 2),
        "flagged_recipes": flagged_recipes,
    }


def main() -> None:
    reports = []
    for csv_path, json_path in RECIPE_PAIRS:
        rep = process_pair(csv_path, json_path)
        print(f"Processed {rep['file']}: {rep['total_recipes']} recipes, {rep['flagged_anomalies']} anomalies flagged ({rep['anomaly_percentage']}%)")
        reports.append(rep)

    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(REPORT_PATH, "w", encoding="utf-8") as f:
        json.dump(reports[0], f, ensure_ascii=False, indent=2)
    print(f"Report saved to {REPORT_PATH.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
