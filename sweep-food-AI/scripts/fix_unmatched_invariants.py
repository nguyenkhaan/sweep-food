"""
Fix invariant violations on match_method == 'UNMATCHED' rows: a stale populated
master_ingredient_code/name, a stale match_confidence left over from a since-
rejected or since-cleared candidate, or nutrition manufactured as literal zero.
All three are cleared together to the same missing semantics (CSV blank / JSON
null) -- an UNMATCHED row asserts "no master link", and a leftover numeric
confidence for an identity that link no longer names is exactly the shape of
staleness this invariant already exists to remove.
Applies to data/processed/recipes/recipe_ingredients.csv and .json.
"""

import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def _populated(value):
    return value is not None and str(value).strip() != ""


def fix_unmatched_invariants():
    csv_path = ROOT / "data" / "processed" / "recipes" / "recipe_ingredients.csv"
    json_path = ROOT / "data" / "processed" / "recipes" / "recipe_ingredients.json"

    with open(csv_path, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        rows = list(reader)

    fixed_count = 0
    for row in rows:
        if row.get("match_method", "").strip().upper() == "UNMATCHED":
            stale = _populated(row.get("master_ingredient_code")) or _populated(row.get("match_confidence"))
            if stale:
                fixed_count += 1
                row["master_ingredient_code"] = ""
                row["master_ingredient_name"] = ""
                row["match_confidence"] = ""
                # Unknown, not a measured zero: nlp/nutrition.py's missing
                # semantics (blank/None/NaN) apply here too. csv.DictWriter
                # renders None as an empty CSV cell.
                row["calories"] = None
                row["protein_g"] = None
                row["fat_g"] = None
                row["carbs_g"] = None

    print(f"Fixed {fixed_count} UNMATCHED rows in CSV.")

    with open(csv_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    if json_path.exists():
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        json_fixed = 0
        for item in data:
            if item.get("match_method", "").strip().upper() == "UNMATCHED":
                stale = _populated(item.get("master_ingredient_code")) or _populated(item.get("match_confidence"))
                if stale:
                    json_fixed += 1
                    item["master_ingredient_code"] = ""
                    item["master_ingredient_name"] = ""
                    item["match_confidence"] = None
                    # Unknown, not a measured zero -- JSON null, matching the CSV blank above.
                    item["calories"] = None
                    item["protein_g"] = None
                    item["fat_g"] = None
                    item["carbs_g"] = None

        print(f"Fixed {json_fixed} UNMATCHED rows in JSON.")

        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    fix_unmatched_invariants()
