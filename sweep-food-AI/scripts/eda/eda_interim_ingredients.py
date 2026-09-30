import pandas as pd


PATH = "data/interim/recipe_ingredients.csv"

df = pd.read_csv(PATH)


print("=" * 80)
print("INTERIM RECIPE INGREDIENTS EDA")
print("=" * 80)


# 1. Nutrition consistency
print("\n[1] INGREDIENT NUTRITION CONSISTENCY")

df["estimated_calories_from_macros"] = (
    df["protein_g"] * 4
    + df["carbs_g"] * 4
    + df["fat_g"] * 9
)

df["calorie_difference_percent"] = (
    (
        df["calories"]
        - df["estimated_calories_from_macros"]
    ).abs()
    / df["calories"].replace(0, pd.NA)
    * 100
)

inconsistent = df[
    df["calorie_difference_percent"] > 30
]

print(f"Total ingredients: {len(df)}")
print(
    f"Ingredients with calorie difference > 30%: "
    f"{len(inconsistent)}"
)
print(
    f"Percentage: "
    f"{len(inconsistent) / len(df) * 100:.2f}%"
)


# 2. Inconsistency by match method
print("\n[2] INCONSISTENCY BY MATCH METHOD")

summary = (
    df.assign(
        inconsistent=df["calorie_difference_percent"] > 30
    )
    .groupby("match_method")
    .agg(
        total=("id", "size"),
        inconsistent=("inconsistent", "sum"),
    )
)

summary["inconsistent_percent"] = (
    summary["inconsistent"]
    / summary["total"]
    * 100
)

print(
    summary.sort_values(
        "inconsistent_percent",
        ascending=False,
    ).round(2)
)


# 3. Zero nutrition
print("\n[3] ZERO NUTRITION")

zero_nutrition = (
    (df["calories"] == 0)
    & (df["protein_g"] == 0)
    & (df["fat_g"] == 0)
    & (df["carbs_g"] == 0)
)

print(f"Rows with all-zero nutrition: {zero_nutrition.sum()}")

print("\nZero nutrition by match method:")

print(
    df.loc[zero_nutrition, "match_method"]
    .value_counts()
)

# 4. Matched ingredients with zero nutrition
print("\n[4] MATCHED INGREDIENTS WITH ZERO NUTRITION")

matched_zero_nutrition = df[
    zero_nutrition
    & (df["match_method"] != "UNMATCHED")
]

print(
    f"Matched rows with all-zero nutrition: "
    f"{len(matched_zero_nutrition)}"
)

print("\nBy match method:")
print(
    matched_zero_nutrition["match_method"]
    .value_counts()
)

print("\nTop master ingredients with zero nutrition:")
print(
    matched_zero_nutrition[
        "master_ingredient_name"
    ]
    .value_counts(dropna=False)
    .head(20)
)

print("\nSample rows:")

columns_to_show = [
    "raw_text",
    "cleaned_name",
    "master_ingredient_code",
    "master_ingredient_name",
    "required_quantity",
    "unit",
    "estimated_weight_g",
    "match_confidence",
    "match_method",
    "calories",
    "protein_g",
    "fat_g",
    "carbs_g",
]

print(
    matched_zero_nutrition[
        columns_to_show
    ]
    .head(30)
    .to_string(index=False)
)

# 5. Compare zero-nutrition matched ingredients with master nutrition data
print("\n[5] ZERO NUTRITION VS MASTER DATA")

master = pd.read_csv(
    "data/processed/viendinhduong/master_ingredients_nutrition.csv"
)

master_subset = master[
    [
        "code",
        "name_vi",
        "energy_kcal",
        "protein_g",
        "fat_g",
        "carbs_g",
    ]
]

comparison = matched_zero_nutrition.merge(
    master_subset,
    left_on="master_ingredient_code",
    right_on="code",
    how="left",
    suffixes=("_recipe", "_master"),
)

print("\nTop matched ingredients with zero recipe nutrition:")

summary = (
    comparison.groupby(
        [
            "master_ingredient_code",
            "master_ingredient_name",
            "energy_kcal",
            "protein_g_master",
            "fat_g_master",
            "carbs_g_master",
        ],
        dropna=False,
    )
    .size()
    .reset_index(name="occurrences")
    .sort_values("occurrences", ascending=False)
)

print(
    summary.head(30).to_string(index=False)
)

# 6. Zero recipe nutrition despite available master nutrition
print("\n[6] ZERO RECIPE NUTRITION DESPITE MASTER DATA")

master_available = comparison[
    comparison["energy_kcal"].notna()
    & (comparison["energy_kcal"] > 1)
]

print(
    "Matched zero-nutrition rows where master energy_kcal > 1: "
    f"{len(master_available)}"
)

print("\nAffected master ingredients:")

affected = (
    master_available.groupby(
        [
            "master_ingredient_code",
            "master_ingredient_name",
            "energy_kcal",
            "protein_g_master",
            "fat_g_master",
            "carbs_g_master",
        ],
        dropna=False,
    )
    .size()
    .reset_index(name="occurrences")
    .sort_values("occurrences", ascending=False)
)

print(affected.to_string(index=False))


print("\nRows where master nutrition is unavailable:")

master_missing = comparison[
    comparison["energy_kcal"].isna()
]

print(f"Count: {len(master_missing)}")

print(
    master_missing["master_ingredient_name"]
    .value_counts(dropna=False)
    .head(20)
)

# 7. Missing master ingredient investigation
print("\n[7] MISSING MASTER INGREDIENT")

missing_master = df["master_ingredient_code"].isna()

print(f"Rows missing master ingredient: {missing_master.sum()}")

print("\nBy match method:")
print(
    df.loc[missing_master, "match_method"]
    .value_counts(dropna=False)
)

print("\nMatch confidence summary:")
print(
    df.loc[missing_master, "match_confidence"]
    .describe()
    .round(4)
)

print("\nSample unmatched ingredients:")

print(
    df.loc[
        missing_master,
        [
            "raw_text",
            "cleaned_name",
            "required_quantity",
            "unit",
            "estimated_weight_g",
            "match_confidence",
            "match_method",
        ],
    ]
    .head(30)
    .to_string(index=False)
)

# 8. High-confidence unmatched ingredients
print("\n[8] HIGH-CONFIDENCE UNMATCHED INGREDIENTS")

unmatched = df[
    df["match_method"] == "UNMATCHED"
]

high_confidence_unmatched = unmatched[
    unmatched["match_confidence"] >= 0.65
]

print(
    f"UNMATCHED rows with confidence >= 0.65: "
    f"{len(high_confidence_unmatched)}"
)

print(
    f"Percentage of UNMATCHED: "
    f"{len(high_confidence_unmatched) / len(unmatched) * 100:.2f}%"
)

print("\nTop cleaned names:")

print(
    high_confidence_unmatched["cleaned_name"]
    .value_counts()
    .head(30)
)

print("\nSample rows:")

print(
    high_confidence_unmatched[
        [
            "raw_text",
            "cleaned_name",
            "required_quantity",
            "unit",
            "match_confidence",
        ]
    ]
    .sort_values(
        "match_confidence",
        ascending=False,
    )
    .head(30)
    .to_string(index=False)
)

# 9. Missing required quantity investigation
print("\n[9] MISSING REQUIRED QUANTITY")

missing_quantity = df["required_quantity"].isna()

print(f"Rows missing required_quantity: {missing_quantity.sum()}")

print(
    f"Percentage: "
    f"{missing_quantity.mean() * 100:.2f}%"
)

print("\nBy unit:")
print(
    df.loc[missing_quantity, "unit"]
    .value_counts(dropna=False)
    .head(20)
)

print("\nBy match method:")
print(
    df.loc[missing_quantity, "match_method"]
    .value_counts(dropna=False)
)

print("\nSample rows:")
print(
    df.loc[
        missing_quantity,
        [
            "raw_text",
            "cleaned_name",
            "unit_vi",
            "unit",
            "estimated_weight_g",
            "match_method",
        ],
    ]
    .head(40)
    .to_string(index=False)
)

# 10. Estimated weight for missing quantities
print("\n[10] ESTIMATED WEIGHT FOR MISSING QUANTITIES")

missing_quantity_df = df[
    df["required_quantity"].isna()
]

print("\nEstimated weight summary:")
print(
    missing_quantity_df["estimated_weight_g"]
    .describe()
    .round(2)
)

print("\nMost common estimated weights:")
print(
    missing_quantity_df["estimated_weight_g"]
    .value_counts()
    .head(20)
)

print("\nEstimated weight by unit:")
print(
    missing_quantity_df.groupby("unit")[
        "estimated_weight_g"
    ]
    .agg(["count", "mean", "min", "max"])
    .round(2)
)

default_10g = (
    missing_quantity_df["estimated_weight_g"] == 10
)

print(
    f"\nRows using estimated_weight_g = 10: "
    f"{default_10g.sum()}"
)

print(
    f"Percentage of missing-quantity rows: "
    f"{default_10g.mean() * 100:.2f}%"
)

# 11. Recipe impact of 10g fallback
print("\n[11] RECIPE IMPACT OF 10G FALLBACK")

fallback_10g = (
    df["required_quantity"].isna()
    & (df["estimated_weight_g"] == 10)
)

affected_recipes = df.loc[
    fallback_10g,
    "recipe_id"
].nunique()

total_recipes = df["recipe_id"].nunique()

print(f"Recipes affected by 10g fallback: {affected_recipes}")
print(f"Total recipes: {total_recipes}")

print(
    f"Percentage of recipes affected: "
    f"{affected_recipes / total_recipes * 100:.2f}%"
)

fallback_per_recipe = (
    df.loc[fallback_10g]
    .groupby("recipe_id")
    .size()
)

print("\nNumber of fallback ingredients per affected recipe:")
print(
    fallback_per_recipe
    .describe()
    .round(2)
)

print("\nDistribution:")
print(
    fallback_per_recipe
    .value_counts()
    .sort_index()
    .head(20)
)

# 12. Nutrition contribution of 10g fallback
print("\n[12] NUTRITION CONTRIBUTION OF 10G FALLBACK")

fallback_df = df.loc[fallback_10g].copy()

print(f"Fallback rows: {len(fallback_df)}")

nonzero_fallback = fallback_df[
    (fallback_df["calories"] > 0)
    | (fallback_df["protein_g"] > 0)
    | (fallback_df["fat_g"] > 0)
    | (fallback_df["carbs_g"] > 0)
]

print(
    f"Fallback rows with non-zero nutrition: "
    f"{len(nonzero_fallback)}"
)

print(
    f"Percentage: "
    f"{len(nonzero_fallback) / len(fallback_df) * 100:.2f}%"
)


# Total nutrition per recipe
recipe_total = (
    df.groupby("recipe_id")["calories"]
    .sum()
    .rename("recipe_calories")
)

fallback_total = (
    fallback_df.groupby("recipe_id")["calories"]
    .sum()
    .rename("fallback_calories")
)

impact = (
    pd.concat(
        [recipe_total, fallback_total],
        axis=1,
    )
    .fillna(0)
)

impact["fallback_calorie_percent"] = (
    impact["fallback_calories"]
    / impact["recipe_calories"].replace(0, pd.NA)
    * 100
)

affected_impact = impact[
    impact["fallback_calories"] > 0
]

print("\nFallback calorie contribution summary:")
print(
    affected_impact["fallback_calorie_percent"]
    .describe()
    .round(2)
)

print("\nRecipes where fallback contributes > 20% calories:")
print(
    (
        affected_impact["fallback_calorie_percent"] > 20
    ).sum()
)

print("\nRecipes where fallback contributes > 50% calories:")
print(
    (
        affected_impact["fallback_calorie_percent"] > 50
    ).sum()
)

# 13. Recipes most affected by 10g fallback
print("\n[13] RECIPES MOST AFFECTED BY 10G FALLBACK")

recipes = pd.read_csv(
    "data/interim/recipes_crawled_cleaned.csv"
)

top_affected = (
    impact.reset_index()
    .merge(
        recipes[
            [
                "id",
                "name",
                "source_platform",
                "total_calories",
            ]
        ],
        left_on="recipe_id",
        right_on="id",
        how="left",
    )
)

top_affected = top_affected[
    top_affected["fallback_calories"] > 0
].sort_values(
    "fallback_calorie_percent",
    ascending=False,
)

print(
    top_affected[
        [
            "name",
            "source_platform",
            "recipe_calories",
            "fallback_calories",
            "fallback_calorie_percent",
        ]
    ]
    .head(30)
    .to_string(index=False)
)

# 14. Check propagation of missing master nutrition
print("\n[14] MASTER MISSING NUTRITION PROPAGATION")

master_core = master[
    [
        "code",
        "energy_kcal",
        "protein_g",
        "fat_g",
        "carbs_g",
    ]
].rename(
    columns={
        "energy_kcal": "master_energy_kcal",
        "protein_g": "master_protein_g",
        "fat_g": "master_fat_g",
        "carbs_g": "master_carbs_g",
    }
)

matched = df[
    df["master_ingredient_code"].notna()
].merge(
    master_core,
    left_on="master_ingredient_code",
    right_on="code",
    how="left",
)

checks = [
    ("protein", "master_protein_g", "protein_g"),
    ("fat", "master_fat_g", "fat_g"),
    ("carbs", "master_carbs_g", "carbs_g"),
]

for label, master_col, recipe_col in checks:
    missing_master = matched[master_col].isna()

    downstream_zero = (
        missing_master
        & (matched[recipe_col] == 0)
    )

    print(f"\n{label.upper()}")
    print(f"Master missing: {missing_master.sum()}")
    print(
        f"Downstream value becomes 0: "
        f"{downstream_zero.sum()}"
    )

    if missing_master.sum() > 0:
        print(
            f"Percentage converted to 0: "
            f"{downstream_zero.sum() / missing_master.sum() * 100:.2f}%"
        )

# 15. Inconsistency related to missing master macros
print("\n[15] INCONSISTENCY RELATED TO MISSING MASTER MACROS")

matched["master_has_missing_macro"] = matched[
    [
        "master_protein_g",
        "master_fat_g",
        "master_carbs_g",
    ]
].isna().any(axis=1)

matched["macro_inconsistent"] = (
    (
        matched["calories"]
        - (
            matched["protein_g"] * 4
            + matched["carbs_g"] * 4
            + matched["fat_g"] * 9
        )
    ).abs()
    / matched["calories"].replace(0, pd.NA)
    * 100
) > 30

inconsistent_matched = matched[
    matched["macro_inconsistent"]
]

related_to_missing_master = inconsistent_matched[
    inconsistent_matched["master_has_missing_macro"]
]

print(
    f"Inconsistent matched rows: "
    f"{len(inconsistent_matched)}"
)

print(
    f"Inconsistent rows with missing macro in master: "
    f"{len(related_to_missing_master)}"
)

if len(inconsistent_matched) > 0:
    print(
        f"Percentage explained by missing master macros: "
        f"{len(related_to_missing_master) / len(inconsistent_matched) * 100:.2f}%"
    )

# 16. Inconsistency not explained by missing master macros
print("\n[16] REMAINING NUTRITION INCONSISTENCY")

remaining_inconsistent = inconsistent_matched[
    ~inconsistent_matched["master_has_missing_macro"]
]

print(
    f"Remaining inconsistent rows: "
    f"{len(remaining_inconsistent)}"
)

print("\nBy match method:")
print(
    remaining_inconsistent["match_method"]
    .value_counts()
)

print("\nTop affected master ingredients:")
print(
    remaining_inconsistent["master_ingredient_name"]
    .value_counts()
    .head(20)
)

print("\nSample rows:")

columns_to_show = [
    "raw_text",
    "cleaned_name",
    "master_ingredient_name",
    "estimated_weight_g",
    "calories",
    "protein_g",
    "fat_g",
    "carbs_g",
    "master_energy_kcal",
    "master_protein_g",
    "master_fat_g",
    "master_carbs_g",
    "match_method",
]

print(
    remaining_inconsistent[
        columns_to_show
    ]
    .head(30)
    .to_string(index=False)
)

master_complete = master[
    ["energy_kcal", "protein_g", "fat_g", "carbs_g"]
].notna().all(axis=1)

master_check = master.loc[master_complete].copy()

master_check["estimated_energy"] = (
    master_check["protein_g"] * 4
    + master_check["carbs_g"] * 4
    + master_check["fat_g"] * 9
)

master_check["energy_diff_percent"] = (
    (master_check["energy_kcal"] - master_check["estimated_energy"]).abs()
    / master_check["energy_kcal"].replace(0, pd.NA)
    * 100
)

inconsistent_master = master_check[
    master_check["energy_diff_percent"] > 30
]

# 17. Remaining inconsistency explained by inconsistent master records
print("\n[17] REMAINING INCONSISTENCY VS MASTER INCONSISTENCY")

inconsistent_master_codes = set(
    inconsistent_master["code"]
)

explained_by_bad_master = remaining_inconsistent[
    remaining_inconsistent["master_ingredient_code"].isin(
        inconsistent_master_codes
    )
]

print(
    f"Remaining inconsistent rows: "
    f"{len(remaining_inconsistent)}"
)

print(
    f"Rows linked to inconsistent master ingredients: "
    f"{len(explained_by_bad_master)}"
)

if len(remaining_inconsistent) > 0:
    print(
        f"Percentage explained: "
        f"{len(explained_by_bad_master) / len(remaining_inconsistent) * 100:.2f}%"
    )

print("\nBy master ingredient:")

print(
    explained_by_bad_master["master_ingredient_name"]
    .value_counts()
)

# 18. Remaining unexplained nutrition inconsistency
print("\n[18] UNEXPLAINED NUTRITION INCONSISTENCY")

unexplained = remaining_inconsistent[
    ~remaining_inconsistent["master_ingredient_code"].isin(
        inconsistent_master_codes
    )
]

print(f"Unexplained inconsistent rows: {len(unexplained)}")

print("\nBy match method:")
print(
    unexplained["match_method"]
    .value_counts()
)

print("\nTop master ingredients:")
print(
    unexplained["master_ingredient_name"]
    .value_counts()
    .head(20)
)

print("\nSample rows:")

columns_to_show = [
    "raw_text",
    "cleaned_name",
    "master_ingredient_name",
    "estimated_weight_g",
    "calories",
    "protein_g",
    "fat_g",
    "carbs_g",
    "master_energy_kcal",
    "master_protein_g",
    "master_fat_g",
    "master_carbs_g",
    "match_confidence",
    "match_method",
]

print(
    unexplained[
        columns_to_show
    ]
    .head(30)
    .to_string(index=False)
)

# 19. Rounding vs true nutrition inconsistency
print("\n[19] ROUNDING VS TRUE NUTRITION INCONSISTENCY")

check = unexplained.copy()

# Expected values when scaling master nutrition by estimated weight
check["expected_calories"] = (
    check["master_energy_kcal"]
    * check["estimated_weight_g"]
    / 100
)

check["expected_protein"] = (
    check["master_protein_g"]
    * check["estimated_weight_g"]
    / 100
)

check["expected_fat"] = (
    check["master_fat_g"]
    * check["estimated_weight_g"]
    / 100
)

check["expected_carbs"] = (
    check["master_carbs_g"]
    * check["estimated_weight_g"]
    / 100
)


# Absolute differences
check["calories_abs_diff"] = (
    check["calories"] - check["expected_calories"]
).abs()

check["protein_abs_diff"] = (
    check["protein_g"] - check["expected_protein"]
).abs()

check["fat_abs_diff"] = (
    check["fat_g"] - check["expected_fat"]
).abs()

check["carbs_abs_diff"] = (
    check["carbs_g"] - check["expected_carbs"]
).abs()


# Tolerances account for downstream rounding
check["consistent_with_rounding"] = (
    (check["calories_abs_diff"] <= 1.0)
    & (check["protein_abs_diff"] <= 0.11)
    & (check["fat_abs_diff"] <= 0.11)
    & (check["carbs_abs_diff"] <= 0.11)
)

rounding_rows = check[
    check["consistent_with_rounding"]
]

true_mismatch = check[
    ~check["consistent_with_rounding"]
]

print(f"Unexplained rows: {len(check)}")

print(
    f"Rows consistent with rounding/scaling: "
    f"{len(rounding_rows)}"
)

print(
    f"Percentage explained by rounding: "
    f"{len(rounding_rows) / len(check) * 100:.2f}%"
)

print(
    f"Remaining possible true mismatches: "
    f"{len(true_mismatch)}"
)

print("\nRemaining mismatches by match method:")
print(
    true_mismatch["match_method"]
    .value_counts()
)

print("\nSample remaining mismatches:")

columns_to_show = [
    "raw_text",
    "cleaned_name",
    "master_ingredient_name",
    "estimated_weight_g",
    "calories",
    "expected_calories",
    "protein_g",
    "expected_protein",
    "fat_g",
    "expected_fat",
    "carbs_g",
    "expected_carbs",
    "match_confidence",
    "match_method",
]

print(
    true_mismatch[
        columns_to_show
    ]
    .head(30)
    .to_string(index=False)
)