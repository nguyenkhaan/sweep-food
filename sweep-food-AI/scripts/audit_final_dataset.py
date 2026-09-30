"""Audit the processed SweepFood dataset.

Distinguishes hard INVARIANTS (must hold; failure exits non-zero) from soft
QUALITY METRICS (reported honestly, never silently claimed as "ready").
"""

import csv
import json
import sys

sys.stdout.reconfigure(encoding="utf-8")

RECIPES_CSV = "data/processed/recipes/recipes.csv"
RECIPES_JSON = "data/processed/recipes/recipes.json"
ING_CSV = "data/processed/recipes/recipe_ingredients.csv"
ING_JSON = "data/processed/recipes/recipe_ingredients.json"
MASTER_CSV = "data/processed/viendinhduong/master_ingredients_nutrition.csv"
MAP_CSV = "data/processed/recipes/recipe_canonical_mapping.csv"

failures = []
warnings = []


def check(cond, msg):
    (print(f"  [PASS] {msg}") if cond else (failures.append(msg) or print(f"  [FAIL] {msg}")))


def load_csv(path):
    with open(path, "r", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def num(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return None


print("=" * 78)
print("SWEEPFOOD DATASET AUDIT  (invariants + honest quality metrics)")
print("=" * 78)

recipes = load_csv(RECIPES_CSV)
recipes_json = load_json(RECIPES_JSON)
ings = load_csv(ING_CSV)
ings_json = load_json(ING_JSON)
master = load_csv(MASTER_CSV)
mapping = load_csv(MAP_CSV)

recipe_ids = [r["id"] for r in recipes]
recipe_id_set = set(recipe_ids)
total_recipes = len(recipes)
total_ings = len(ings)

print("\n1. STRUCTURAL INVARIANTS (must hold):")
check(len(recipe_id_set) == total_recipes, f"recipe ids unique ({total_recipes:,})")
check(len(recipes_json) == total_recipes, "recipes.json row count matches recipes.csv")
check(len(ings_json) == total_ings, "recipe_ingredients.json row count matches .csv")
orphans = [r for r in ings if r["recipe_id"] not in recipe_id_set]
check(len(orphans) == 0, f"0 orphan ingredient rows (found {len(orphans)})")
ids_with_ings = {r["recipe_id"] for r in ings}
missing_ings = recipe_id_set - ids_with_ings
check(len(missing_ings) == 0, f"every recipe has >=1 ingredient (found {len(missing_ings)} without)")
has_ws = all("weight_source" in r for r in ings)
has_ps = all("nutrition_anomaly_flag" in r and "calories_per_serving" in r for r in recipes)
check(has_ps, "per-serving macros and nutrition_anomaly_flag present on all recipes")
check(has_ws, "weight_source present on all ingredient rows")
has_roles = all("ingredient_role" in r for r in ings)
check(has_roles, "ingredient_role present on all ingredient rows")
has_clusters = all("core_ingredients_count" in r and "dish_cluster_id" in r for r in recipes)
check(has_clusters, "core_ingredients_count and dish_cluster_id present on all recipes")
check(len(mapping) == 5641, f"canonical mapping contains all 5,641 original recipes ({len(mapping):,})")
orphaned_maps = [
    r for r in mapping
    if (r.get("canonical_recipe_id") or "").strip() and (r.get("canonical_recipe_id") or "").strip() not in recipe_id_set
]
check(len(orphaned_maps) == 0, f"0 orphan mapping rows referencing non-existent canonical recipes (found {len(orphaned_maps)})")

print("\n2. NUTRITION CONSISTENCY INVARIANTS:")
# UNMATCHED rows must carry no master link and no nutrition
bad_unmatched = [
    r for r in ings
    if (r.get("match_method") or "").strip().upper() == "UNMATCHED"
    and (r.get("master_ingredient_code") or "").strip()
]
check(len(bad_unmatched) == 0, f"UNMATCHED rows carry no master code (violations: {len(bad_unmatched)})")
bad_ws = [
    r for r in ings
    if ((r.get("match_method") or "").strip().upper() == "UNMATCHED") != ((r.get("weight_source") or "").strip() == "unmatched_no_nutrition")
]
check(len(bad_ws) == 0, f"weight_source matches UNMATCHED status with 0 violations (found {len(bad_ws)})")

print("\n3. QUALITY METRICS (reported, NOT pass/fail):")
matched = sum(1 for r in ings if (r.get("master_ingredient_code") or "").strip())
print(f"  - ingredient rows: {total_ings:,}")
print(f"  - matched to master: {matched:,} ({matched/total_ings*100:.1f}%)  | UNMATCHED: {total_ings-matched:,} ({(total_ings-matched)/total_ings*100:.1f}%)")

ws = {}
for r in ings:
    ws[r["weight_source"]] = ws.get(r["weight_source"], 0) + 1
print("  - weight provenance:")
for k, v in sorted(ws.items(), key=lambda kv: -kv[1]):
    print(f"      {k:26} {v:7,} ({v/total_ings*100:5.1f}%)")
low = ws.get("vague_portion_fallback", 0) + ws.get("role_category_estimate", 0)
print(f"    -> low-confidence weight (no source quantity): {low:,} ({low/total_ings*100:.1f}%)")

# missing macros at ingredient level
miss_fat = sum(1 for r in ings if num(r.get("fat_g")) is None and (r.get("master_ingredient_code") or "").strip())
print(f"  - matched rows missing fat_g: {miss_fat:,}")

# master completeness
mfat = sum(1 for m in master if (m.get("fat_g") or "").strip() == "")
print(f"  - master ingredients: {len(master):,}  | missing fat_g: {mfat}")

# recipe-level macro/calorie coherence (soft)
anom = 0
for r in recipes:
    tc = num(r["total_calories"]); p = num(r["total_protein_g"]); f = num(r["total_fat_g"]); c = num(r["total_carbs_g"])
    if tc and tc > 0:
        est = 4 * (p or 0) + 4 * (c or 0) + 9 * (f or 0)
        if est > 0 and abs(est - tc) / tc > 0.3:
            anom += 1
print(f"  - recipes with >30% macro/calorie divergence: {anom} ({anom/total_recipes*100:.1f}%)")
flagged_cnt = sum(1 for r in recipes if r.get("nutrition_anomaly_flag") in ("1", 1))
print(f"  - recipes flagged as nutrition anomalies: {flagged_cnt:,} ({flagged_cnt/total_recipes*100:.2f}%)")
roles = {}
for r in ings:
    roles[r["ingredient_role"]] = roles.get(r["ingredient_role"], 0) + 1
print("  - ingredient roles:")
for k, v in sorted(roles.items(), key=lambda kv: -kv[1]):
    print(f"      {k:26} {v:7,} ({v/total_ings*100:5.1f}%)")
clusters_cnt = len(set(r.get("dish_cluster_id") for r in recipes))
print(f"  - distinct dish clusters (dialect-grouped): {clusters_cnt:,} (from {total_recipes:,} recipes)")

print("\n" + "=" * 78)
if failures:
    print(f"AUDIT FAILED: {len(failures)} invariant(s) broken:")
    for m in failures:
        print(f"  - {m}")
    sys.exit(1)
print("AUDIT PASSED: all structural/nutrition invariants hold.")
print("Quality metrics above are descriptive; see reports/eda/ for limitations.")
print("=" * 78)
