import csv
import json
from pathlib import Path
import unittest

ROOT_DIR = Path(__file__).resolve().parent.parent

class AliasIntegrityTests(unittest.TestCase):
    def test_all_alias_codes_exist_in_master(self):
        alias_path = ROOT_DIR / "data" / "processed" / "viendinhduong" / "ingredient_alias_map.json"
        master_path = ROOT_DIR / "data" / "processed" / "viendinhduong" / "master_ingredients_nutrition.csv"

        with open(alias_path, "r", encoding="utf-8") as f:
            alias_map = json.load(f)

        with open(master_path, "r", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            master_codes = {row["code"].strip() for row in reader if row.get("code")}

        broken = {}
        for alias, code in alias_map.items():
            clean_code = str(code).strip()
            if clean_code not in master_codes:
                broken[alias] = clean_code

        self.assertEqual(
            broken,
            {},
            f"Found broken alias references in {alias_path}: {broken}"
        )

    def test_unmatched_rows_have_no_master_code(self):
        ing_path = ROOT_DIR / "data" / "processed" / "recipes" / "recipe_ingredients.csv"
        with open(ing_path, "r", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            violations = [
                r["id"]
                for r in reader
                if r.get("match_method", "").strip().upper() == "UNMATCHED"
                and r.get("master_ingredient_code", "").strip()
            ]
        self.assertEqual(
            violations,
            [],
            f"Found {len(violations)} UNMATCHED rows with populated master_ingredient_code"
        )

    def test_all_master_categories_are_standard(self):
        master_path = ROOT_DIR / "data" / "processed" / "viendinhduong" / "master_ingredients_nutrition.csv"
        cat_std_path = ROOT_DIR / "data" / "processed" / "viendinhduong" / "ingredient_categories.csv"

        with open(cat_std_path, "r", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            std_cats = {row["category_vi"].strip() for row in reader}

        with open(master_path, "r", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            master_cats = {row["category_vi"].strip() for row in reader}

        invalid_cats = master_cats - std_cats
        self.assertEqual(
            invalid_cats,
            set(),
            f"Found non-standard categories in master: {invalid_cats}"
        )

if __name__ == "__main__":
    unittest.main()
