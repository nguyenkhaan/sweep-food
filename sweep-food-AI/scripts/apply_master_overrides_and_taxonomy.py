"""
Apply master nutrition overrides and standardize category taxonomy in master_ingredients_nutrition.csv.
"""

import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

def apply_overrides_and_taxonomy():
    master_path = ROOT / "data" / "processed" / "viendinhduong" / "master_ingredients_nutrition.csv"
    overrides_path = ROOT / "data" / "processed" / "viendinhduong" / "master_nutrition_overrides.json"
    taxonomy_path = ROOT / "data" / "processed" / "viendinhduong" / "category_taxonomy_mapping.json"
    cat_std_path = ROOT / "data" / "processed" / "viendinhduong" / "ingredient_categories.csv"

    with open(overrides_path, "r", encoding="utf-8") as f:
        overrides = json.load(f)

    with open(taxonomy_path, "r", encoding="utf-8") as f:
        taxonomy_data = json.load(f)
        category_map = taxonomy_data["mappings"]

    with open(cat_std_path, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        vi_to_en = {row["category_vi"].strip(): row["category_en"].strip() for row in reader}

    with open(master_path, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        rows = list(reader)

    overridden_count = 0
    cat_remapped_count = 0

    for row in rows:
        code = row.get("code", "").strip()
        if code in overrides:
            ov = overrides[code]
            for k in ["energy_kcal", "protein_g", "fat_g", "carbs_g", "fiber_g"]:
                if k in ov and k in row:
                    row[k] = ov[k]
            overridden_count += 1

        cat_vi = row.get("category_vi", "").strip()
        if cat_vi in category_map:
            std_vi = category_map[cat_vi]
            if std_vi != cat_vi:
                cat_remapped_count += 1
            row["category_vi"] = std_vi
            if std_vi in vi_to_en:
                row["category_en"] = vi_to_en[std_vi]

    print(f"Applied overrides to {overridden_count} master ingredients.")
    print(f"Standardized category taxonomy on {cat_remapped_count} master ingredients.")

    # Check that all category_vi are in vi_to_en
    final_cats = set(r["category_vi"] for r in rows)
    unknown_cats = final_cats - set(vi_to_en.keys())
    if unknown_cats:
        raise ValueError(f"Unknown categories after standardization: {unknown_cats}")
    print(f"All categories standardized. Unique categories: {len(final_cats)} (expected 15).")

    with open(master_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

if __name__ == "__main__":
    apply_overrides_and_taxonomy()
