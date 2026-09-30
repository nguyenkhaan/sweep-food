"""
Export canonical CSV artifacts to JSON for fast production Web / API serving.
"""

import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

def export_canonical_json():
    recipes_csv = ROOT / "data" / "processed" / "recipes" / "canonical_recipes.csv"
    recipes_json = ROOT / "data" / "processed" / "recipes" / "canonical_recipes.json"
    
    ing_csv = ROOT / "data" / "processed" / "recipes" / "canonical_recipe_ingredients.csv"
    ing_json = ROOT / "data" / "processed" / "recipes" / "canonical_recipe_ingredients.json"

    map_csv = ROOT / "data" / "processed" / "recipes" / "recipe_canonical_mapping.csv"
    map_json = ROOT / "data" / "processed" / "recipes" / "recipe_canonical_mapping.json"

    print("Exporting canonical_recipes.json...")
    with open(recipes_csv, "r", encoding="utf-8-sig") as f:
        recipes = list(csv.DictReader(f))
    with open(recipes_json, "w", encoding="utf-8") as f:
        json.dump(recipes, f, ensure_ascii=False, indent=2)

    print("Exporting canonical_recipe_ingredients.json...")
    with open(ing_csv, "r", encoding="utf-8-sig") as f:
        ingredients = list(csv.DictReader(f))
    with open(ing_json, "w", encoding="utf-8") as f:
        json.dump(ingredients, f, ensure_ascii=False, indent=2)

    print("Exporting recipe_canonical_mapping.json...")
    with open(map_csv, "r", encoding="utf-8-sig") as f:
        mappings = {row["original_recipe_id"]: row["canonical_recipe_id"] for row in csv.DictReader(f)}
    with open(map_json, "w", encoding="utf-8") as f:
        json.dump(mappings, f, ensure_ascii=False, indent=2)

    print(f"Exported {len(recipes)} canonical recipes and {len(ingredients)} canonical ingredient rows.")

if __name__ == "__main__":
    export_canonical_json()
