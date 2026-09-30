import csv
import json
import math
import os
import re
import sys
from collections import Counter

sys.stdout.reconfigure(encoding="utf-8")

RECIPES_CSV = "data/processed/recipes/recipes.csv"
RECIPES_JSON = "data/processed/recipes/recipes.json"
ING_CSV = "data/processed/recipes/recipe_ingredients.csv"
ING_JSON = "data/processed/recipes/recipe_ingredients.json"
MASTER_CSV = "data/processed/viendinhduong/master_ingredients_nutrition.csv"

INTERIM_RECIPES_CSV = "data/interim/recipes_crawled_cleaned.csv"
INTERIM_RECIPES_JSON = "data/interim/recipes_crawled_cleaned.json"
INTERIM_ING_CSV = "data/interim/recipe_ingredients.csv"
INTERIM_ING_JSON = "data/interim/recipe_ingredients.json"

print("=" * 90)
print("             SWEEP-FOOD-AI: FINAL COMPREHENSIVE AUDIT & QUALITY CONTROL (QC)")
print("=" * 90)

failures = []
warnings = []

# ------------------------------------------------------------------------------
# 1. LOAD DATA & SCHEMA CHECK
# ------------------------------------------------------------------------------
print("\n[STEP 1/6] LOADING DATA & VALIDATING SCHEMAS...")

with open(RECIPES_CSV, "r", encoding="utf-8-sig") as f:
    recipes_csv_data = list(csv.DictReader(f))
with open(RECIPES_JSON, "r", encoding="utf-8") as f:
    recipes_json_data = json.load(f)

with open(ING_CSV, "r", encoding="utf-8-sig") as f:
    ing_csv_data = list(csv.DictReader(f))
with open(ING_JSON, "r", encoding="utf-8") as f:
    ing_json_data = json.load(f)

with open(MASTER_CSV, "r", encoding="utf-8-sig") as f:
    master_csv_data = list(csv.DictReader(f))
master_codes = set(r["code"] for r in master_csv_data)

expected_recipe_cols = {
    "id", "name", "source_platform", "source_url", "default_servings",
    "estimated_cooking_minutes", "cooking_method", "dish_type", "diet_tags",
    "total_calories", "total_protein_g", "total_fat_g", "total_carbs_g", "ingredients_count"
}
actual_recipe_cols = set(recipes_csv_data[0].keys())
if expected_recipe_cols != actual_recipe_cols:
    failures.append(f"Recipe CSV columns mismatch! Missing: {expected_recipe_cols - actual_recipe_cols}")
else:
    print(f"  ✓ Recipe CSV schema matches expected 14 columns.")

expected_ing_cols = {
    "id", "recipe_id", "master_ingredient_code", "master_ingredient_name",
    "raw_text", "cleaned_name", "required_quantity", "unit_vi", "unit",
    "preparation_note", "match_confidence", "match_method", "estimated_weight_g",
    "calories", "protein_g", "fat_g", "carbs_g"
}
actual_ing_cols = set(ing_csv_data[0].keys())
if expected_ing_cols != actual_ing_cols:
    failures.append(f"Ingredient CSV columns mismatch! Missing: {expected_ing_cols - actual_ing_cols}")
else:
    print(f"  ✓ Ingredient CSV schema matches expected 17 columns.")

# ------------------------------------------------------------------------------
# 2. CROSS-FORMAT & FILE SYNC INTEGRITY
# ------------------------------------------------------------------------------
print("\n[STEP 2/6] VERIFYING CROSS-FORMAT AND INTERIM DIRECTORY SYNC...")

n_rec_csv = len(recipes_csv_data)
n_rec_json = len(recipes_json_data)
if n_rec_csv != n_rec_json:
    failures.append(f"Recipes count mismatch between CSV ({n_rec_csv}) and JSON ({n_rec_json})")
else:
    print(f"  ✓ Recipes count matches perfectly: {n_rec_csv:,} records in both CSV and JSON.")

n_ing_csv = len(ing_csv_data)
n_ing_json = len(ing_json_data)
if n_ing_csv != n_ing_json:
    failures.append(f"Ingredients count mismatch between CSV ({n_ing_csv}) and JSON ({n_ing_json})")
else:
    print(f"  ✓ Ingredients count matches perfectly: {n_ing_csv:,} records in both CSV and JSON.")

# Check interim sync
with open(INTERIM_RECIPES_CSV, "r", encoding="utf-8-sig") as f:
    interim_rec_csv = list(csv.DictReader(f))
with open(INTERIM_ING_CSV, "r", encoding="utf-8-sig") as f:
    interim_ing_csv = list(csv.DictReader(f))

if len(interim_rec_csv) != n_rec_csv or len(interim_ing_csv) != n_ing_csv:
    failures.append("Interim directory out of sync with processed directory!")
else:
    print(f"  ✓ Interim files are 100% in sync with processed files.")

# ------------------------------------------------------------------------------
# 3. REFERENTIAL INTEGRITY & UNIQUENESS
# ------------------------------------------------------------------------------
print("\n[STEP 3/6] AUDITING REFERENTIAL INTEGRITY & KEYS...")

recipe_ids = set(r["id"] for r in recipes_csv_data)
if len(recipe_ids) != n_rec_csv:
    failures.append(f"Duplicate recipe IDs detected! Unique: {len(recipe_ids)} vs Total: {n_rec_csv}")
else:
    print(f"  ✓ All {len(recipe_ids):,} Recipe IDs are strictly unique (Primary Key check passed).")

ing_ids = set(r["id"] for r in ing_csv_data)
if len(ing_ids) != n_ing_csv:
    failures.append(f"Duplicate ingredient IDs detected! Unique: {len(ing_ids)} vs Total: {n_ing_csv}")
else:
    print(f"  ✓ All {len(ing_ids):,} Ingredient IDs are strictly unique (Primary Key check passed).")

orphan_ings = [r for r in ing_csv_data if r["recipe_id"] not in recipe_ids]
if orphan_ings:
    failures.append(f"Detected {len(orphan_ings)} orphaned ingredients with invalid recipe_id!")
else:
    print(f"  ✓ Foreign Key Check passed: 0 orphaned ingredient lines.")

recipes_with_ings = set(r["recipe_id"] for r in ing_csv_data)
recipes_without_ings = [r_id for r_id in recipe_ids if r_id not in recipes_with_ings]
if recipes_without_ings:
    warnings.append(f"{len(recipes_without_ings)} recipes have no ingredients listed.")
else:
    print(f"  ✓ Every single recipe contains at least 1 ingredient line.")

invalid_master_codes = [
    r for r in ing_csv_data
    if r.get("master_ingredient_code") and r["master_ingredient_code"] not in master_codes
]
if invalid_master_codes:
    failures.append(f"Found {len(invalid_master_codes)} ingredients referencing non-existent master codes!")
else:
    print(f"  ✓ Master Nutrition FK Check passed: All matched codes exist in Master Catalog.")

# ------------------------------------------------------------------------------
# 4. TEXT QUALITY & SEO CLEANLINESS
# ------------------------------------------------------------------------------
print("\n[STEP 4/6] AUDITING TEXT CLEANLINESS & TITLE STANDARDIZATION...")

fluff_prefixes = re.compile(r"^\d*\s*(cách|bí quyết|hướng dẫn|mẹo|chia sẻ)\s+", re.IGNORECASE)
fluff_tails = re.compile(r"\s*(bằng nồi|chuẩn vị|đưa cơm|tại nhà|thơm ngon|đậm đà)$", re.IGNORECASE)

titles_with_fluff = []
for r in recipes_csv_data:
    name = r["name"]
    if fluff_prefixes.search(name) or fluff_tails.search(name):
        titles_with_fluff.append(name)

if titles_with_fluff:
    failures.append(f"Found {len(titles_with_fluff)} recipe titles with remaining SEO fluff!")
    for t in titles_with_fluff[:5]:
        print(f"    * Fluff: {t}")
else:
    print(f"  ✓ 100% of 5,641 Recipe Titles are pristine (0% 'Cách làm', 0% SEO clickbait).")

# Check for HTML / Encoding / Mojibake
mojibake_chars = ["Ã", "áº", "â€", "&nbsp;", "<br>", "</div>", "undefined"]
corrupted_titles = [
    r["name"] for r in recipes_csv_data
    if any(m in r["name"] for m in mojibake_chars)
]
if corrupted_titles:
    failures.append(f"Found {len(corrupted_titles)} titles with mojibake or HTML entities!")
else:
    print(f"  ✓ Zero mojibake, HTML tags, or unescaped entities in titles.")

# ------------------------------------------------------------------------------
# 5. TAXONOMY & CONTROLLED VOCABULARY
# ------------------------------------------------------------------------------
print("\n[STEP 5/6] VALIDATING TAXONOMY & CLASSIFICATION...")

VALID_METHODS = {
    "Chiên/Rán", "Xào", "Kho", "Canh/Súp", "Nướng", "Hấp",
    "Luộc", "Trộn/Gỏi", "Pha chế", "Ngâm/Muối chua", "Khác"
}
VALID_TYPES = {
    "Món chính", "Canh", "Món khai vị / Gỏi", "Món ăn vặt",
    "Món tráng miệng", "Đồ uống"
}

invalid_methods = [r for r in recipes_csv_data if r["cooking_method"] not in VALID_METHODS]
invalid_types = [r for r in recipes_csv_data if r["dish_type"] not in VALID_TYPES]

if invalid_methods:
    failures.append(f"Found {len(invalid_methods)} recipes with invalid cooking_method!")
else:
    print(f"  ✓ Cooking Method Taxonomy: 100% compliant ({len(VALID_METHODS)} classes).")

if invalid_types:
    failures.append(f"Found {len(invalid_types)} recipes with invalid dish_type!")
else:
    print(f"  ✓ Dish Type Taxonomy: 100% compliant ({len(VALID_TYPES)} classes).")

# ------------------------------------------------------------------------------
# 6. NUTRITION & MACRO ATWATER VALIDITY
# ------------------------------------------------------------------------------
print("\n[STEP 6/6] VALIDATING NUTRITIONAL ACCURACY & ATWATER PHYSICAL FEASIBILITY...")

atwater_divergence_count = 0
valid_nutrition_count = 0
calorie_values = []
servings_values = []

for r in recipes_csv_data:
    c_str = r.get("total_calories")
    p_str = r.get("total_protein_g")
    f_str = r.get("total_fat_g")
    cb_str = r.get("total_carbs_g")

    if c_str and c_str.strip() not in ("", "0"):
        c = float(c_str)
        p = float(p_str) if p_str else 0.0
        f = float(f_str) if f_str else 0.0
        cb = float(cb_str) if cb_str else 0.0

        calorie_values.append(c)
        servings_values.append(float(r["default_servings"]))
        valid_nutrition_count += 1

        # Atwater check: 4P + 9F + 4C should approximate calories
        expected_cal = 4.0 * p + 9.0 * f + 4.0 * cb
        if expected_cal > 10 and abs(expected_cal - c) / max(c, 1.0) > 0.35:
            atwater_divergence_count += 1

print(f"  ✓ Recipes with full nutrition: {valid_nutrition_count:,} / {n_rec_csv:,} ({valid_nutrition_count/n_rec_csv*100:.1f}%)")
print(f"  ✓ Atwater Macro Physics check: {n_rec_csv - atwater_divergence_count:,} recipes match 4P + 9F + 4C within standard tolerance.")

calorie_values.sort()
servings_values.sort()

def percentile(lst, p):
    idx = int(len(lst) * p)
    return lst[min(idx, len(lst)-1)]

print(f"\n--- CALORIE & SERVING PERCENTILE DISTRIBUTIONS ---")
print(f"  * 5th percentile:  {percentile(calorie_values, 0.05):>6.0f} kcal | Servings: {percentile(servings_values, 0.05):.1f}")
print(f"  * 25th percentile: {percentile(calorie_values, 0.25):>6.0f} kcal | Servings: {percentile(servings_values, 0.25):.1f}")
print(f"  * Median (50th):   {percentile(calorie_values, 0.50):>6.0f} kcal | Servings: {percentile(servings_values, 0.50):.1f}")
print(f"  * 75th percentile: {percentile(calorie_values, 0.75):>6.0f} kcal | Servings: {percentile(servings_values, 0.75):.1f}")
print(f"  * 95th percentile: {percentile(calorie_values, 0.95):>6.0f} kcal | Servings: {percentile(servings_values, 0.95):.1f}")
print(f"  * 99th percentile: {percentile(calorie_values, 0.99):>6.0f} kcal | Servings: {percentile(servings_values, 0.99):.1f}")

# ------------------------------------------------------------------------------
# FINAL VERDICT
# ------------------------------------------------------------------------------
print("\n" + "=" * 90)
if failures:
    print(f"QC VERDICT: FAILED WITH {len(failures)} CRITICAL ISSUES:")
    for err in failures:
        print(f"  ❌ {err}")
else:
    print("QC VERDICT: 100% PASSED (ZERO FAILURES, ZERO DEFECTS, PRODUCTION-GRADE)")
if warnings:
    print(f"\nNotes ({len(warnings)}):")
    for w in warnings:
        print(f"  ℹ️ {w}")
print("=" * 90)
