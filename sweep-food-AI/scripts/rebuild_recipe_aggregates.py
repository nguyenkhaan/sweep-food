"""Rebuild recipe-level aggregates in the SweepFood AI dataset deterministically.

Pipeline execution order:
    1) scripts/merge_duplicate_dishes.py
    2) scripts/tag_accompaniments.py
    3) scripts/rebuild_recipe_aggregates.py

This script recalculates recipe-level nutrition and metadata aggregates directly
from ingredient rows (data/processed/recipes/recipe_ingredients.csv) and master
ingredient taxonomy (data/processed/viendinhduong/master_ingredients_nutrition.csv),
ensuring full idempotency, reproducibility, and auditability without masking underlying
data-quality issues.

Sodium Coverage Definition:
    `sodium_mg_coverage` is defined as:
        round(sum of `estimated_weight_g` over I rows with non-null `sodium_mg` /
              sum of `estimated_weight_g` over I, 3)
    where I represents all ingredient rows belonging to the recipe (including seasonings).
    If total ingredient weight is zero or no row has non-null sodium, coverage is 0.0
    and total sodium is set to NaN.

Column derivation rules:
    1. Macros (total_calories, total_protein_g, total_fat_g, total_carbs_g):
       - Sum over ALL ingredient rows belonging to the recipe (every nutrition_scope,
         including seasonings and accompaniments).
       - Rounded to 1 decimal place.
       - If every ingredient value is NaN (or ingredient rows empty) -> NaN, never 0.
       - Per serving = round(unrounded_total / default_servings, 1).
    2. Sugar and Fiber (total_sugar_g, total_fiber_g):
       - Sum over ALL ingredient rows belonging to the recipe.
       - sugar_g_coverage and fiber_g_coverage kept unchanged from input baseline.
       - Missing values: total and per-serving are set to NaN (empty in CSV, null in JSON)
         only if:
           (a) every ingredient value is NaN / no rows, OR
           (b) baseline coverage == 0 AND the recomputed sum over all rows == 0.
         Otherwise keep the recomputed sum.
    3. Sodium (total_sodium_mg):
       - Sum over ALL ingredient rows I (including excluded_seasoning).
       - Per serving = round(unrounded_total / default_servings, 1).
       - sodium_mg_coverage defined as documented above.
       - If no row has non-null sodium -> total and per-serving NaN.
    4. Core ingredients count:
       - Number of ingredient rows with ingredient_role == "core".
       - Accompaniment rows have ingredient_role == "accompaniment" and are not core.
    5. Nutrition anomaly flag:
       - Preserves input flag OR sets to 1 if new rule `seasoning_kcal_outlier` is met:
         all-rows kcal/serving > 1500 while included-scope kcal/serving <= 1500.
       - Existing flag 1 is never cleared.
    6. Animal detection:
       - Category check: master category_en in {'Meat and processed products',
         'Seafood and processed products', 'Eggs and processed products'}.
       - Regex check: word-boundary regex of Vietnamese animal terms, including oyster sauce
         ('dầu hào'; regular oyster sauce is animal, 'dầu hào chay' stays exempt via 'chay').
       - Ingredient-level plant exemptions (checked on cleaned_name/master_ingredient_name):
         * Terms containing 'chay' are exempt.
         * Any ingredient whose cleaned_name starts with 'nấm' (e.g. nấm đùi gà, nấm chân gà,
           nấm hủ đùi gà, nấm bào ngư...) is exempt from keyword matching (master category applies).
         * Spice blends: 'bột bò kho', 'gia vị bò kho', 'xốt bò kho', 'sốt bò kho'.
         * 'mì tôm' (instant noodles).
         * Botanical/culinary plant compounds containing animal substrings: 'nấm sò', 'đậu gà',
           'càng cua', 'diếp cá', 'giấp cá', 'xương sông', 'bò khai', 'bò bía', 'quả trứng gà',
           'bánh da lợn', 'bánh tai heo', 'tép tỏi', 'tỏi tép', 'tép sả'.
       - Recipe name is animal if regex matches name without 'chay' after stripping plant compounds
         (including 'mì tôm').
    7. Incomplete flag:
       - 1 if:
         * core_ingredients_count == 0 (no_core), OR
         * calories_per_serving < 50 (kcal_lt_50), computed from rows with
           nutrition_scope == "included" AND ingredient_role != "accompaniment"
           (kcal of the dish's own non-seasoning ingredients per serving < 50, or NaN), OR
         * missing_named_animal is True:
           true only if (a) no ingredient row is animal by master category (Meat/Seafood/Eggs)
           nor matches a non-condiment animal term (rows whose animal evidence comes only from
           CONDIMENT_ANIMAL_TERMS do not satisfy (a)) AND (b) the matched name animal term(s)
           appear in no ingredient cleaned_name AND (c) the name does not start with a
           condiment/marinade prefix ('nước màu', 'nước chấm', 'nước sốt', 'sốt', 'xốt', 'ướp', 'gia vị').
       - Else 0.
    8. Diet tags:
       - Strip existing 'Ăn chay' tag.
       - Prepend 'Ăn chay' as first tag iff recipe is vegan (no animal ingredient, name not animal,
         not missing_named_animal).
    9. Suspected parser noise:
       - Parser noise cases like 'hàu' (from 'lá nhàu') and 'tôm sừng' (from 'ớt sừng') stay animal,
         but in the report their animal_evidence is prefixed with 'parser_noise_suspect:'.
"""

from __future__ import annotations

import argparse
import io
import json
import re
import subprocess
from pathlib import Path

import numpy as np
import pandas as pd

# -----------------------------------------------------------------------------
# Constants & Taxonomy
# -----------------------------------------------------------------------------

BASELINE_REV = "48cae9a"

COLUMNS_ORDER = [
    "id",
    "name",
    "source_platform",
    "source_url",
    "default_servings",
    "estimated_cooking_minutes",
    "cooking_method",
    "dish_type",
    "diet_tags",
    "total_calories",
    "total_protein_g",
    "total_fat_g",
    "total_carbs_g",
    "calories_per_serving",
    "protein_per_serving",
    "fat_per_serving",
    "carbs_per_serving",
    "nutrition_anomaly_flag",
    "ingredients_count",
    "core_ingredients_count",
    "dish_cluster_id",
    "incomplete_flag",
    "nutrition_confidence",
    "total_sodium_mg",
    "sodium_mg_per_serving",
    "sodium_mg_coverage",
    "total_sugar_g",
    "sugar_g_per_serving",
    "sugar_g_coverage",
    "total_fiber_g",
    "fiber_g_per_serving",
    "fiber_g_coverage",
]

INT_COLUMNS = [
    "estimated_cooking_minutes",
    "nutrition_anomaly_flag",
    "ingredients_count",
    "core_ingredients_count",
    "incomplete_flag",
]

FLOAT_COLUMNS = [
    "default_servings",
    "total_calories",
    "total_protein_g",
    "total_fat_g",
    "total_carbs_g",
    "calories_per_serving",
    "protein_per_serving",
    "fat_per_serving",
    "carbs_per_serving",
    "nutrition_confidence",
    "total_sodium_mg",
    "sodium_mg_per_serving",
    "sodium_mg_coverage",
    "total_sugar_g",
    "sugar_g_per_serving",
    "sugar_g_coverage",
    "total_fiber_g",
    "fiber_g_per_serving",
    "fiber_g_coverage",
]

STRING_COLUMNS = [
    "id",
    "name",
    "source_platform",
    "source_url",
    "cooking_method",
    "dish_type",
    "diet_tags",
    "dish_cluster_id",
]

ANIMAL_CATEGORIES = {
    "Meat and processed products",
    "Seafood and processed products",
    "Eggs and processed products",
}

# Vietnamese animal terms (Rule 6 + Item 1: dầu hào)
VIETNAMESE_ANIMAL_TERMS = [
    "thịt", "heo", "lợn", "bò", "bê", "gà", "vịt", "ngan", "ngỗng",
    "bồ câu", "cút", "dê", "cừu", "cá", "tôm", "tép", "mực", "bạch tuộc",
    "cua", "ghẹ", "ốc", "ngao", "nghêu", "sò", "hến", "hàu", "lươn", "ếch",
    "sườn", "ba chỉ", "ba rọi", "xương", "giò heo", "chả cá", "bacon",
    "dăm bông", "xúc xích", "lạp xưởng", "pate", "trứng", "lòng", "gan",
    "cật", "dạ dày", "nội tạng", "mỡ heo", "mỡ lợn", "nước mắm", "mắm tôm",
    "mắm ruốc", "mắm tép", "mắm nêm", "mắm cá", "nước dùng gà", "nước hầm xương",
    "dầu hào",
]

# Named constant for condiment animal terms (rows with only these terms do not satisfy condition a)
CONDIMENT_ANIMAL_TERMS = {
    "nước mắm", "dầu hào", "mắm tôm", "mắm ruốc", "mắm tép",
    "mắm nêm", "mắm cá", "nước dùng gà", "nước hầm xương",
}

NON_CONDIMENT_ANIMAL_TERMS = [t for t in VIETNAMESE_ANIMAL_TERMS if t not in CONDIMENT_ANIMAL_TERMS]

# Regex patterns
_REGEX_PATTERN_ALL = r"\b(?:" + "|".join(sorted(VIETNAMESE_ANIMAL_TERMS, key=len, reverse=True)) + r")\b"
ANIMAL_REGEX_ALL = re.compile(_REGEX_PATTERN_ALL, re.IGNORECASE)

_REGEX_PATTERN_NON_COND = r"\b(?:" + "|".join(sorted(NON_CONDIMENT_ANIMAL_TERMS, key=len, reverse=True)) + r")\b"
ANIMAL_REGEX_NON_COND = re.compile(_REGEX_PATTERN_NON_COND, re.IGNORECASE)

# Plant compound exemptions for recipe names (Rule 6 + Item 4: mì tôm)
NAME_PLANT_COMPOUNDS = (
    "nấm đùi gà", "nấm gà", "bánh da lợn", "bánh tai heo", "tép tỏi", "tỏi tép", "tép sả",
    "nấm sò", "đậu gà", "càng cua", "diếp cá", "giấp cá", "xương sông", "bò khai", "bò bía", "quả trứng gà",
    "mì tôm",
)

# Ingredient-level plant exemptions (Item 2)
INGREDIENT_EXEMPT_COMPOUNDS = (
    "nấm đùi gà", "nấm gà", "bánh da lợn", "bánh tai heo", "tép tỏi", "tỏi tép", "tép sả",
    "nấm sò", "đậu gà", "càng cua", "diếp cá", "giấp cá", "xương sông", "bò khai", "bò bía", "quả trứng gà",
    "bột bò kho", "gia vị bò kho", "xốt bò kho", "sốt bò kho", "mì tôm",
)

# Condiment / marinade prefixes for missing_named_animal (Item 4)
CONDIMENT_PREFIXES = ("nước màu", "nước chấm", "nước sốt", "sốt", "xốt", "ướp", "gia vị")

# Suspected parser noise pairs (Item 3)
SUSPECTED_PARSER_NOISE = {
    ("d238cfbc-b29a-4995-9e53-ebdc272fb286", "hàu"),
    ("0b2e1d97-85d7-464a-bbf1-0cac678523bf", "tôm sừng"),
}


# -----------------------------------------------------------------------------
# Animal Detection Helpers
# -----------------------------------------------------------------------------

def is_recipe_name_animal(name: str) -> tuple[bool, list[str]]:
    """Check if recipe name matches animal terms, after removing plant exemptions.

    If name contains 'chay', returns (False, []).
    Otherwise returns (is_animal, list_of_matched_terms).
    """
    if not name or pd.isna(name):
        return False, []
    s = str(name)
    if "chay" in s.lower():
        return False, []
    s_clean = s.lower()
    for compound in NAME_PLANT_COMPOUNDS:
        s_clean = s_clean.replace(compound, " ")
    matches = ANIMAL_REGEX_ALL.findall(s_clean)
    return len(matches) > 0, matches


def check_ingredient_rows_animal(
    df_ingredients: pd.DataFrame,
    master_category_map: dict[str, str],
) -> tuple[pd.Series, pd.Series, pd.Series]:
    """Vectorized check of animal presence across ingredient rows."""
    cats = df_ingredients["master_ingredient_code"].astype(str).map(master_category_map)
    is_anim_cat = cats.isin(ANIMAL_CATEGORIES)

    cleaned = df_ingredients["cleaned_name"].fillna("").astype(str).str.lower()
    raw = df_ingredients["raw_text"].fillna("").astype(str).str.lower()
    m_name = df_ingredients["master_ingredient_name"].fillna("").astype(str).str.lower()

    is_chay = cleaned.str.contains("chay") | raw.str.contains("chay") | m_name.str.contains("chay")
    is_nam_prefix = cleaned.str.startswith("nấm ") | (cleaned == "nấm")

    cleaned_for_regex = cleaned.copy()
    for comp in INGREDIENT_EXEMPT_COMPOUNDS:
        cleaned_for_regex = cleaned_for_regex.str.replace(comp, " ", regex=False)

    match_all = cleaned_for_regex.apply(lambda s: ANIMAL_REGEX_ALL.findall(s))
    has_regex_all = match_all.apply(lambda l: len(l) > 0)

    match_non_cond = cleaned_for_regex.apply(lambda s: ANIMAL_REGEX_NON_COND.findall(s))
    has_regex_non_cond = match_non_cond.apply(lambda l: len(l) > 0)

    is_animal = (~is_chay) & (is_anim_cat | ((~is_nam_prefix) & has_regex_all))
    is_animal_non_cond = (~is_chay) & (is_anim_cat | ((~is_nam_prefix) & has_regex_non_cond))

    evidence = []
    for anim, cat_name, m_list in zip(is_animal, cats, match_all):
        if not anim:
            evidence.append("")
        elif cat_name in ANIMAL_CATEGORIES:
            evidence.append(f"cat:{cat_name}")
        elif m_list:
            evidence.append(m_list[0])
        else:
            evidence.append("animal")

    evidence_series = pd.Series(evidence, index=df_ingredients.index)
    return is_animal, is_animal_non_cond, evidence_series


# -----------------------------------------------------------------------------
# Baseline Loader (Idempotency Helper)
# -----------------------------------------------------------------------------

def load_baseline_recipes(recipes_path: Path) -> pd.DataFrame:
    """Load baseline recipes for diff reporting using fixed BASELINE_REV."""
    try:
        rel_path = str(recipes_path).replace("\\", "/")
        res = subprocess.run(
            ["git", "show", f"{BASELINE_REV}:{rel_path}"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            check=True,
        )
        if res.stdout:
            return pd.read_csv(io.StringIO(res.stdout))
    except Exception:
        pass
    return pd.read_csv(recipes_path)

def safe_write_bytes(path: Path, data: bytes) -> None:
    import time
    for attempt in range(10):
        try:
            path.write_bytes(data)
            return
        except OSError:
            if attempt == 9:
                raise
            time.sleep(0.2)


# -----------------------------------------------------------------------------
# Main Rebuild Routine
# -----------------------------------------------------------------------------

def rebuild_recipe_aggregates(
    recipes_csv_path: Path,
    recipes_json_path: Path,
    ingredients_csv_path: Path,
    master_csv_path: Path,
    report_csv_path: Path,
) -> tuple[pd.DataFrame, list[dict]]:
    """Execute rebuild of recipe aggregates and write outputs."""
    # 1. Load inputs
    df_recipes_input = pd.read_csv(recipes_csv_path)
    df_baseline = load_baseline_recipes(recipes_csv_path)
    df_ingredients = pd.read_csv(ingredients_csv_path)
    df_master = pd.read_csv(master_csv_path)

    master_category_map = dict(zip(df_master["code"].astype(str), df_master["category_en"]))

    # Ensure recipe sorting by id
    df_recipes = df_recipes_input.sort_values("id").copy()

    # 2. Ingredient-level animal classification
    is_anim_ing, is_anim_non_cond, evidence_ing = check_ingredient_rows_animal(df_ingredients, master_category_map)
    df_ingredients["_is_animal"] = is_anim_ing
    df_ingredients["_is_animal_non_cond"] = is_anim_non_cond
    df_ingredients["_animal_evidence"] = evidence_ing

    # First animal evidence per recipe
    animal_ings_only = df_ingredients[df_ingredients["_is_animal"]].copy()
    first_animal_evidence = animal_ings_only.groupby("recipe_id")["_animal_evidence"].first().to_dict()
    has_animal_ing_map = animal_ings_only.groupby("recipe_id").size().to_dict()

    # Recipes with non-condiment animal rows (for condition a)
    has_animal_non_cond_map = df_ingredients[df_ingredients["_is_animal_non_cond"]].groupby("recipe_id").size().to_dict()

    # All cleaned names concatenated per recipe for term matching
    all_cleaned_per_recipe = df_ingredients.groupby("recipe_id")["cleaned_name"].apply(
        lambda s: " ".join(s.fillna("").astype(str).str.lower())
    ).to_dict()

    # 3. Nutrition aggregations:
    # Rule 1 & 2: Macros, sugar, fiber sum over ALL ingredient rows belonging to the recipe
    all_agg = df_ingredients.groupby("recipe_id")[["calories", "protein_g", "fat_g", "carbs_g", "sugar_g", "fiber_g"]].agg(
        lambda s: s.sum(min_count=1)
    )

    # Included scope only (for seasoning outlier anomaly check)
    inc_mask = df_ingredients["nutrition_scope"] == "included"
    df_inc = df_ingredients[inc_mask]
    inc_agg = df_inc.groupby("recipe_id")[["calories", "protein_g", "fat_g", "carbs_g", "sugar_g", "fiber_g"]].agg(
        lambda s: s.sum(min_count=1)
    )

    # Dish's own non-seasoning, non-accompaniment ingredients for kcal_lt_50 check
    dish_own_mask = (df_ingredients["nutrition_scope"] == "included") & (df_ingredients["ingredient_role"] != "accompaniment")
    df_dish_own = df_ingredients[dish_own_mask]
    dish_own_cal = df_dish_own.groupby("recipe_id")["calories"].agg(lambda s: s.sum(min_count=1))

    # Core ingredients count (role == "core")
    core_counts = df_ingredients[df_ingredients["ingredient_role"] == "core"].groupby("recipe_id").size()

    # 4. Sodium aggregation: All ingredient rows (including excluded_seasoning)
    sod_agg = df_ingredients.groupby("recipe_id")["sodium_mg"].agg(lambda s: s.sum(min_count=1))

    weight_total = df_ingredients.groupby("recipe_id")["estimated_weight_g"].sum()
    weight_with_sodium = df_ingredients[df_ingredients["sodium_mg"].notna()].groupby("recipe_id")["estimated_weight_g"].sum()

    # 5. Populate derived columns per recipe
    servings = df_recipes["default_servings"].astype(float)
    recipe_ids = df_recipes["id"]

    # Rule 1: Macros (all ingredient rows)
    cal_unrounded = recipe_ids.map(all_agg["calories"])
    prot_unrounded = recipe_ids.map(all_agg["protein_g"])
    fat_unrounded = recipe_ids.map(all_agg["fat_g"])
    carbs_unrounded = recipe_ids.map(all_agg["carbs_g"])

    df_recipes["total_calories"] = cal_unrounded.round(1)
    df_recipes["total_protein_g"] = prot_unrounded.round(1)
    df_recipes["total_fat_g"] = fat_unrounded.round(1)
    df_recipes["total_carbs_g"] = carbs_unrounded.round(1)

    df_recipes["calories_per_serving"] = (cal_unrounded / servings).round(1)
    df_recipes["protein_per_serving"] = (prot_unrounded / servings).round(1)
    df_recipes["fat_per_serving"] = (fat_unrounded / servings).round(1)
    df_recipes["carbs_per_serving"] = (carbs_unrounded / servings).round(1)

    # Rule 2: Sugar and Fiber (all ingredient rows)
    # Missing rule: total/per-serving = NaN only if:
    #   (a) every ingredient value is NaN / no rows, OR
    #   (b) baseline coverage == 0 AND recomputed sum == 0.
    # Otherwise keep recomputed sum.
    sugar_unrounded = recipe_ids.map(all_agg["sugar_g"])
    fiber_unrounded = recipe_ids.map(all_agg["fiber_g"])

    sugar_missing_mask = sugar_unrounded.isna() | ((df_recipes["sugar_g_coverage"] == 0) & (sugar_unrounded == 0))
    df_recipes["total_sugar_g"] = np.where(sugar_missing_mask, np.nan, sugar_unrounded.round(1))
    df_recipes["sugar_g_per_serving"] = np.where(sugar_missing_mask, np.nan, (sugar_unrounded / servings).round(1))

    fiber_missing_mask = fiber_unrounded.isna() | ((df_recipes["fiber_g_coverage"] == 0) & (fiber_unrounded == 0))
    df_recipes["total_fiber_g"] = np.where(fiber_missing_mask, np.nan, fiber_unrounded.round(1))
    df_recipes["fiber_g_per_serving"] = np.where(fiber_missing_mask, np.nan, (fiber_unrounded / servings).round(1))

    # Rule 3: Sodium
    sod_unrounded = recipe_ids.map(sod_agg)
    sod_missing_mask = sod_unrounded.isna()

    df_recipes["total_sodium_mg"] = np.where(sod_missing_mask, np.nan, sod_unrounded.round(1))
    df_recipes["sodium_mg_per_serving"] = np.where(sod_missing_mask, np.nan, (sod_unrounded / servings).round(1))

    w_tot = recipe_ids.map(weight_total).fillna(0.0)
    w_sod = recipe_ids.map(weight_with_sodium).fillna(0.0)
    cov_ratio = np.where(w_tot > 0, (w_sod / w_tot).round(3), 0.0)
    df_recipes["sodium_mg_coverage"] = cov_ratio

    # Rule 4: Core count
    df_recipes["core_ingredients_count"] = recipe_ids.map(core_counts).fillna(0).astype(int)

    # Rule 5: Nutrition anomaly flag
    # Preserves input flag OR sets 1 if seasoning_kcal_outlier:
    # all-rows kcal/serving > 1500 while included-scope kcal/serving <= 1500. Never clears an existing flag.
    inc_cal_unrounded = recipe_ids.map(inc_agg["calories"])
    inc_cal_per_serving = (inc_cal_unrounded / servings).round(1)
    all_cal_per_serving = df_recipes["calories_per_serving"]

    seasoning_kcal_outlier_series = (
        all_cal_per_serving.notna()
        & inc_cal_per_serving.notna()
        & (all_cal_per_serving > 1500.0)
        & (inc_cal_per_serving <= 1500.0)
    )
    input_anomaly_series = df_recipes["nutrition_anomaly_flag"].fillna(0).astype(int) == 1
    new_anomaly_series = (input_anomaly_series | seasoning_kcal_outlier_series).astype(int)
    df_recipes["nutrition_anomaly_flag"] = new_anomaly_series

    # Rule 6, 7, 8: Animal detection, Incomplete flag, Diet tags
    has_animal_ing_series = recipe_ids.map(has_animal_ing_map).fillna(0) > 0
    first_ev_series = recipe_ids.map(first_animal_evidence).fillna("")

    name_animal_results = [is_recipe_name_animal(n) for n in df_recipes["name"]]
    name_is_animal_series = pd.Series([r[0] for r in name_animal_results], index=df_recipes.index)
    name_terms_series = pd.Series([r[1] for r in name_animal_results], index=df_recipes.index)
    name_first_term_series = pd.Series([r[1][0] if r[1] else "" for r in name_animal_results], index=df_recipes.index)

    # Rule 7: missing_named_animal refinement:
    # True only if:
    #   (a) no ingredient row is animal by master category (Meat/Seafood/Eggs) nor matches
    #       a non-condiment animal term (rows with only CONDIMENT_ANIMAL_TERMS do not satisfy a) AND
    #   (b) the matched name animal term(s) appear in no ingredient cleaned_name AND
    #   (c) the name does not start with a condiment/marinade prefix
    missing_named_animal_list = []
    for rid, name, is_anim, m_terms in zip(df_recipes["id"], df_recipes["name"], name_is_animal_series, name_terms_series):
        has_anim_non_cond = has_animal_non_cond_map.get(rid, 0) > 0
        if is_anim and (not has_anim_non_cond):
            recipe_cleaned = all_cleaned_per_recipe.get(rid, "")
            term_in_ing = any(re.search(r"\b" + re.escape(t.lower()) + r"\b", recipe_cleaned) for t in m_terms)
            starts_condiment = any(name.lower().startswith(p) for p in CONDIMENT_PREFIXES)
            missing = (not term_in_ing) and (not starts_condiment)
        else:
            missing = False
        missing_named_animal_list.append(missing)
    missing_named_animal_series = pd.Series(missing_named_animal_list, index=df_recipes.index)

    # Incomplete reasons:
    # kcal_lt_50 is computed from dish's own non-seasoning, non-accompaniment ingredients
    no_core_series = df_recipes["core_ingredients_count"] == 0
    dish_own_cal_per_serving = (recipe_ids.map(dish_own_cal) / servings).round(1)
    kcal_lt_50_series = dish_own_cal_per_serving.isna() | (dish_own_cal_per_serving < 50.0)

    new_incomplete_flag_series = (no_core_series | kcal_lt_50_series | missing_named_animal_series).astype(int)
    df_recipes["incomplete_flag"] = new_incomplete_flag_series

    # Vegetarian check: no ingredient row is animal (including condiments) AND recipe name is not animal
    is_veg_series = (~has_animal_ing_series) & (~name_is_animal_series)

    # Diet tags update
    new_diet_tags = []
    for tags_str, is_veg in zip(df_recipes["diet_tags"].fillna(""), is_veg_series):
        tokens = [t.strip() for t in str(tags_str).split(";") if t.strip()]
        other_tokens = [t for t in tokens if t != "Ăn chay"]
        if is_veg:
            merged_tokens = ["Ăn chay"] + other_tokens
        else:
            merged_tokens = other_tokens
        # Deduplicate preserving order
        seen = set()
        deduped = []
        for t in merged_tokens:
            if t not in seen:
                seen.add(t)
                deduped.append(t)
        new_diet_tags.append("; ".join(deduped))
    df_recipes["diet_tags"] = new_diet_tags

    # Enforce exact column order and types
    df_recipes = df_recipes[COLUMNS_ORDER].copy()
    for col in INT_COLUMNS:
        df_recipes[col] = df_recipes[col].astype(int)
    for col in FLOAT_COLUMNS:
        df_recipes[col] = df_recipes[col].astype(float)
    for col in STRING_COLUMNS:
        df_recipes[col] = df_recipes[col].fillna("").astype(str)

    # 6. Prepare JSON records
    records_json = []
    for row in df_recipes.itertuples(index=False):
        d = {}
        for col in df_recipes.columns:
            val = getattr(row, col)
            if col in INT_COLUMNS:
                d[col] = int(val)
            elif col in FLOAT_COLUMNS:
                d[col] = None if pd.isna(val) else float(val)
            else:
                d[col] = "" if pd.isna(val) else str(val)
        records_json.append(d)

    # 7. Assertions (General invariants)
    assert len(df_recipes) == len(df_recipes_input), f"Row count changed: {len(df_recipes_input)} -> {len(df_recipes)}"
    assert df_recipes["id"].is_unique, "Recipe IDs are not unique"
    ing_recipe_ids = set(df_ingredients["recipe_id"])
    assert all(rid in ing_recipe_ids for rid in df_recipes["id"]), "Not every recipe id exists in ingredients"

    # CSV / JSON parity check
    assert len(df_recipes) == len(records_json), "CSV and JSON record count mismatch"
    for r_idx, (r_dict, (csv_idx, csv_row)) in enumerate(zip(records_json, df_recipes.iterrows())):
        for col in COLUMNS_ORDER:
            c_val = csv_row[col]
            j_val = r_dict[col]
            if col in STRING_COLUMNS:
                assert str(c_val) == str(j_val), f"Parity mismatch row {r_idx} col {col}: {c_val!r} vs {j_val!r}"
            elif col in INT_COLUMNS:
                assert int(c_val) == j_val, f"Parity mismatch row {r_idx} col {col}: {c_val!r} vs {j_val!r}"
                assert isinstance(j_val, int), f"JSON {col} not int: {type(j_val)}"
            elif col in FLOAT_COLUMNS:
                if pd.isna(c_val):
                    assert j_val is None, f"Parity mismatch row {r_idx} col {col}: expected None, got {j_val!r}"
                else:
                    assert abs(float(c_val) - float(j_val)) < 1e-5, f"Parity mismatch row {r_idx} col {col}: {c_val} vs {j_val}"
                    assert isinstance(j_val, float), f"JSON {col} not float: {type(j_val)}"

    # 8. Write outputs (Byte-preserving CRLF)
    buf_csv = io.StringIO()
    df_recipes.to_csv(buf_csv, index=False, encoding="utf-8", lineterminator="\r\n")
    safe_write_bytes(recipes_csv_path, buf_csv.getvalue().encode("utf-8"))
    recipes_text = json.dumps(records_json, ensure_ascii=False, indent=2).replace("\n", "\r\n")
    safe_write_bytes(recipes_json_path, recipes_text.encode("utf-8"))

    # 9. Build and write EDA report
    report_rows = []
    base_map = df_baseline.set_index("id").to_dict(orient="index")

    # Reason tracker
    reason_counts = {"no_core": 0, "kcal_lt_50": 0, "missing_named_animal": 0}
    macros_changed_count = 0
    veg_before = 0
    veg_after = 0
    veg_added = 0
    veg_removed = 0
    anomaly_before = 0
    anomaly_after = 0

    for rid, new_row in df_recipes.set_index("id").iterrows():
        base_row = base_map.get(rid, {})
        old_inc_flag = int(base_row.get("incomplete_flag", 0))
        new_inc_flag = int(new_row["incomplete_flag"])

        old_veg = "Ăn chay" in str(base_row.get("diet_tags", ""))
        new_veg = "Ăn chay" in str(new_row["diet_tags"])

        old_anomaly_flag = int(base_row.get("nutrition_anomaly_flag", 0))
        new_anomaly_flag = int(new_row["nutrition_anomaly_flag"])

        if old_veg:
            veg_before += 1
        if new_veg:
            veg_after += 1
        if (not old_veg) and new_veg:
            veg_added += 1
        if old_veg and (not new_veg):
            veg_removed += 1

        if old_anomaly_flag:
            anomaly_before += 1
        if new_anomaly_flag:
            anomaly_after += 1

        # Incomplete reasons for this recipe
        reasons = []
        if new_row["core_ingredients_count"] == 0:
            reasons.append("no_core")
            reason_counts["no_core"] += 1
        own_cal_val = dish_own_cal_per_serving.loc[df_recipes["id"] == rid].iloc[0]
        if pd.isna(own_cal_val) or own_cal_val < 50.0:
            reasons.append("kcal_lt_50")
            reason_counts["kcal_lt_50"] += 1
        is_missing_animal = bool(missing_named_animal_series.loc[df_recipes["id"] == rid].iloc[0])
        if is_missing_animal:
            reasons.append("missing_named_animal")
            reason_counts["missing_named_animal"] += 1

        # Anomaly reasons for this recipe
        anomaly_reasons = []
        is_seasoning_outlier = bool(seasoning_kcal_outlier_series.loc[df_recipes["id"] == rid].iloc[0])
        if is_seasoning_outlier:
            anomaly_reasons.append("seasoning_kcal_outlier")
        if old_anomaly_flag == 1:
            anomaly_reasons.append("input_flag")

        # Macro diff > 0.1 check
        macro_diff = False
        for m_col in ["total_calories", "total_protein_g", "total_fat_g", "total_carbs_g"]:
            old_val = base_row.get(m_col, np.nan)
            new_val = new_row[m_col]
            if pd.isna(old_val) != pd.isna(new_val):
                macro_diff = True
            elif pd.notna(old_val) and abs(float(old_val) - float(new_val)) > 0.1:
                macro_diff = True
        if macro_diff:
            macros_changed_count += 1

        # Report inclusion condition: incomplete_flag, veg status, or nutrition_anomaly_flag changed
        if (old_inc_flag != new_inc_flag) or (old_veg != new_veg) or (old_anomaly_flag != new_anomaly_flag):
            f_ev = first_ev_series.loc[df_recipes["id"] == rid].iloc[0]
            n_ev = name_first_term_series.loc[df_recipes["id"] == rid].iloc[0]
            evidence = f_ev if f_ev else (n_ev if n_ev else "")

            # Suspected parser noise note
            if (rid, evidence) in SUSPECTED_PARSER_NOISE:
                evidence = f"parser_noise_suspect:{evidence}"

            report_rows.append({
                "id": rid,
                "name": new_row["name"],
                "old_incomplete_flag": old_inc_flag,
                "new_incomplete_flag": new_inc_flag,
                "incomplete_reasons": "|".join(reasons),
                "old_veg": old_veg,
                "new_veg": new_veg,
                "animal_evidence": evidence,
                "old_nutrition_anomaly_flag": old_anomaly_flag,
                "new_nutrition_anomaly_flag": new_anomaly_flag,
                "nutrition_anomaly_reasons": "|".join(anomaly_reasons),
            })

    df_report = pd.DataFrame(report_rows).sort_values("id")
    report_csv_path.parent.mkdir(parents=True, exist_ok=True)
    buf_rep = io.StringIO()
    df_report.to_csv(buf_rep, index=False, encoding="utf-8", lineterminator="\r\n")
    safe_write_bytes(report_csv_path, buf_rep.getvalue().encode("utf-8"))

    # 10. Print statistics and verification tables
    seasoning_outliers_count = int(seasoning_kcal_outlier_series.sum())
    print("=" * 80)
    print("RECIPE AGGREGATE REBUILD SUMMARY")
    print("=" * 80)
    print(f"Baseline revision:                 {BASELINE_REV}")
    print(f"Total recipes:                     {len(df_recipes)}")
    print(f"Counts per incomplete reason:      {reason_counts}")
    print(f"Total incomplete recipes:          {(df_recipes['incomplete_flag'] == 1).sum()}")
    print(f"Veg status before:                 {veg_before}")
    print(f"Veg status after:                  {veg_after}")
    print(f"Veg tags added:                    {veg_added}")
    print(f"Veg tags removed:                  {veg_removed}")
    print(f"Nutrition anomaly before:          {anomaly_before}")
    print(f"Nutrition anomaly after:           {anomaly_after}")
    print(f"Newly flagged seasoning outliers:  {seasoning_outliers_count}")
    print(f"Recipes with macros diff >0.1:     {macros_changed_count}")
    print(f"Differences report rows:           {len(df_report)} -> {report_csv_path}")
    print("=" * 80)

    # Sugar and fiber NaN stats
    sugar_nan_count = int(df_recipes["total_sugar_g"].isna().sum())
    fiber_nan_count = int(df_recipes["total_fiber_g"].isna().sum())
    base_sugar = df_baseline.set_index("id")["total_sugar_g"]
    base_fiber = df_baseline.set_index("id")["total_fiber_g"]
    sugar_base_gt0_new_nan = int(((base_sugar > 0) & df_recipes.set_index("id")["total_sugar_g"].isna()).sum())
    fiber_base_gt0_new_nan = int(((base_fiber > 0) & df_recipes.set_index("id")["total_fiber_g"].isna()).sum())
    print(f"Total_sugar_g NaN count:            {sugar_nan_count}")
    print(f"Total_fiber_g NaN count:            {fiber_nan_count}")
    print(f"Sugar NaN where baseline total > 0: {sugar_base_gt0_new_nan}")
    print(f"Fiber NaN where baseline total > 0: {fiber_base_gt0_new_nan}")
    print("=" * 80)

    # Acceptance Criterion 3:
    # Macros vs all-rows-sum mismatches = 0
    macro_mismatches = 0
    for col in ["calories", "protein_g", "fat_g", "carbs_g"]:
        expected = recipe_ids.map(all_agg[col]).round(1)
        actual = df_recipes[f"total_{col}"]
        mismatch_mask = (expected.isna() != actual.isna()) | (
            expected.notna() & (abs(expected - actual) > 1e-4)
        )
        macro_mismatches += int(mismatch_mask.sum())
    print(f"Macros vs all-rows-sum mismatches:  {macro_mismatches}")
    assert macro_mismatches == 0, f"Expected 0 macro mismatches, got {macro_mismatches}"

    # Sugar > Carbs count
    sugar_gt_carbs = df_recipes[df_recipes["total_sugar_g"] > df_recipes["total_carbs_g"]]
    print(f"Sugar_g > carbs_g count:            {len(sugar_gt_carbs)}")

    # Sodium total == sum over all rows
    total_recipe_sodium = df_recipes["total_sodium_mg"].sum()
    total_ingredient_sodium = df_ingredients["sodium_mg"].sum()
    print(f"Total recipe sodium:                {total_recipe_sodium:.1f} mg")
    print(f"Total ingredient sodium:            {total_ingredient_sodium:.1f} mg")
    print(f"Sodium difference:                  {abs(total_recipe_sodium - total_ingredient_sodium):.4f} mg")
    print("=" * 80)

    # Top 10 seasoning kcal outliers
    if seasoning_outliers_count > 0:
        outlier_df = df_recipes[seasoning_kcal_outlier_series][["name", "calories_per_serving"]].sort_values(
            "calories_per_serving", ascending=False
        )
        print("TOP 10 SEASONING KCAL OUTLIERS (kcal/serving):")
        print("=" * 80)
        print(outlier_df.head(10).to_string(index=False))
        print("=" * 80)

    # Missing Named Animal Detailed Audit
    missing_named_animal_df = df_recipes[missing_named_animal_series][["id", "name"]].copy()
    print(f"MISSING NAMED ANIMAL AUDIT: {len(missing_named_animal_df)} recipes")
    print("=" * 80)
    print(missing_named_animal_df.to_string(index=False))
    print("=" * 80)

    # Verification of specific recipe IDs requested by Parent:
    print("PARENT AUDIT RECIPES TABLE")
    print("=" * 80)
    parent_check_groups = [
        ("Item 1 (lose Ăn chay due to dầu hào)", ["1fd3a1a9", "3cbbde8b", "49e4cc14", "6acbc580", "c0c48604", "cbf90dfe", "d0b28d0d"]),
        ("Item 2 (regain Ăn chay)", ["32a46dbf", "6a29dd7f", "63265048", "9a057266"]),
        ("Item 3 (suspected parser noise)", ["d238cfbc", "0b2e1d97"]),
        ("Item 4 (no longer missing_named_animal)", ["c4758088", "22b33d06", "b72d1cf0", "e3e910bf", "831fa111", "4d28e5f3", "8b99dc87"]),
    ]
    for group_name, p_ids in parent_check_groups:
        print(f"--- {group_name} ---")
        p_rows = []
        for p_id in p_ids:
            sub = df_recipes[df_recipes["id"].str.startswith(p_id)]
            if len(sub) == 0:
                continue
            r_item = sub.iloc[0]
            rid = r_item["id"]

            r_reasons = []
            if r_item["core_ingredients_count"] == 0:
                r_reasons.append("no_core")
            own_cal_val = dish_own_cal_per_serving.loc[df_recipes["id"] == rid].iloc[0]
            if pd.isna(own_cal_val) or own_cal_val < 50.0:
                r_reasons.append("kcal_lt_50")
            if missing_named_animal_series.loc[df_recipes["id"] == rid].iloc[0]:
                r_reasons.append("missing_named_animal")

            f_ev = first_ev_series.loc[df_recipes["id"] == rid].iloc[0]
            n_ev = name_first_term_series.loc[df_recipes["id"] == rid].iloc[0]
            ev = f_ev if f_ev else (n_ev if n_ev else "")
            if (rid, ev) in SUSPECTED_PARSER_NOISE:
                ev = f"parser_noise_suspect:{ev}"

            base_tags = base_map.get(rid, {}).get("diet_tags", "")
            p_rows.append({
                "id_prefix": p_id,
                "name": r_item["name"],
                "old_veg": "Ăn chay" in str(base_tags),
                "new_veg": "Ăn chay" in str(r_item["diet_tags"]),
                "incomplete_flag": int(r_item["incomplete_flag"]),
                "reasons": "|".join(r_reasons) or "none",
                "evidence": ev,
            })
        print(pd.DataFrame(p_rows).to_string(index=False))
    print("=" * 80)

    # Verification of the 9 test recipes
    test_names = [
        "Khoai tây xào thịt bằm",
        "Thịt rim sa tế",
        "Sườn non rim nước tương",
        "Steak bò sốt phomai",
        "Cá bống mú hấp cay",
        "Bánh xếp chay",
        "Cuốn đậu hủ kho gừng",
        "Nấm đùi gà hấp cải xanh",
        "Bánh da lợn nước cốt dừa",
    ]
    print("ORIGINAL 9 TEST RECIPES AUDIT TABLE")
    print("=" * 80)
    test_results = []
    for name in test_names:
        sub = df_recipes[df_recipes["name"] == name]
        if len(sub) == 0:
            continue
        row = sub.iloc[0]
        rid = row["id"]
        is_veg = "Ăn chay" in str(row["diet_tags"])

        r_reasons = []
        if row["core_ingredients_count"] == 0:
            r_reasons.append("no_core")
        own_cal_val = dish_own_cal_per_serving.loc[df_recipes["id"] == rid].iloc[0]
        if pd.isna(own_cal_val) or own_cal_val < 50.0:
            r_reasons.append("kcal_lt_50")
        if missing_named_animal_series.loc[df_recipes["id"] == rid].iloc[0]:
            r_reasons.append("missing_named_animal")

        f_ev = first_ev_series.loc[df_recipes["id"] == rid].iloc[0]
        n_ev = name_first_term_series.loc[df_recipes["id"] == rid].iloc[0]
        ev = f_ev if f_ev else (n_ev if n_ev else "")
        if (rid, ev) in SUSPECTED_PARSER_NOISE:
            ev = f"parser_noise_suspect:{ev}"

        test_results.append({
            "name": name,
            "incomplete_flag": int(row["incomplete_flag"]),
            "incomplete_reasons": "|".join(r_reasons) or "none",
            "is_veg": is_veg,
            "animal_evidence": ev,
        })
    df_test = pd.DataFrame(test_results)
    print(df_test.to_string(index=False))
    print("=" * 80)

    # Confirm 'Khoai tây xào thịt bằm' incomplete=1 explicitly
    kt_row = df_recipes[df_recipes["name"] == "Khoai tây xào thịt bằm"].iloc[0]
    assert int(kt_row["incomplete_flag"]) == 1, f"Expected Khoai tây xào thịt bằm incomplete=1, got {kt_row['incomplete_flag']}"
    print("CONFIRMATION: 'Khoai tây xào thịt bằm' incomplete_flag == 1 (PASSED)")
    print("=" * 80)

    return df_recipes, records_json


def main():
    parser = argparse.ArgumentParser(description="Rebuild SweepFood AI recipe aggregates.")
    parser.add_argument(
        "--recipes-csv",
        type=Path,
        default=Path("data/processed/recipes/recipes.csv"),
        help="Path to recipes.csv",
    )
    parser.add_argument(
        "--recipes-json",
        type=Path,
        default=Path("data/processed/recipes/recipes.json"),
        help="Path to recipes.json",
    )
    parser.add_argument(
        "--ingredients-csv",
        type=Path,
        default=Path("data/processed/recipes/recipe_ingredients.csv"),
        help="Path to recipe_ingredients.csv",
    )
    parser.add_argument(
        "--master-csv",
        type=Path,
        default=Path("data/processed/viendinhduong/master_ingredients_nutrition.csv"),
        help="Path to master_ingredients_nutrition.csv",
    )
    parser.add_argument(
        "--report-csv",
        type=Path,
        default=Path("reports/eda/recipe_aggregate_rebuild.csv"),
        help="Path to output report CSV",
    )
    args = parser.parse_args()

    rebuild_recipe_aggregates(
        recipes_csv_path=args.recipes_csv,
        recipes_json_path=args.recipes_json,
        ingredients_csv_path=args.ingredients_csv,
        master_csv_path=args.master_csv,
        report_csv_path=args.report_csv,
    )


if __name__ == "__main__":
    main()
