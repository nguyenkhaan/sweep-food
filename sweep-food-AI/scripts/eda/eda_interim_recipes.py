import pandas as pd


PATH = "data/interim/recipes_crawled_cleaned.csv"

df = pd.read_csv(PATH)


print("=" * 80)
print("INTERIM RECIPES EDA")
print("=" * 80)


# 1. Basic information
print("\n[1] BASIC INFORMATION")
print(f"Rows: {len(df)}")
print(f"Columns: {len(df.columns)}")


# 2. ID uniqueness
print("\n[2] ID CHECK")
print(f"Unique IDs: {df['id'].nunique()}")
print(f"Duplicate IDs: {df['id'].duplicated().sum()}")


# 3. Recipe name duplicates
print("\n[3] RECIPE NAME CHECK")

normalized_names = (
    df["name"]
    .astype(str)
    .str.strip()
    .str.lower()
)

duplicate_names = normalized_names.duplicated(keep=False)

print(f"Unique normalized names: {normalized_names.nunique()}")
print(f"Rows with duplicated normalized names: {duplicate_names.sum()}")

if duplicate_names.any():
    print("\nTop duplicated recipe names:")
    print(
        normalized_names[duplicate_names]
        .value_counts()
        .head(20)
    )


# 4. Source URL uniqueness
print("\n[4] SOURCE URL CHECK")
print(f"Unique source URLs: {df['source_url'].nunique()}")
print(f"Duplicate source URLs: {df['source_url'].duplicated().sum()}")


# 5. Numeric validity
print("\n[5] NUMERIC VALIDITY")

numeric_rules = {
    "default_servings <= 0": df["default_servings"] <= 0,
    "estimated_cooking_minutes <= 0": df["estimated_cooking_minutes"] <= 0,
    "total_calories < 0": df["total_calories"] < 0,
    "total_protein_g < 0": df["total_protein_g"] < 0,
    "total_fat_g < 0": df["total_fat_g"] < 0,
    "total_carbs_g < 0": df["total_carbs_g"] < 0,
    "ingredients_count <= 0": df["ingredients_count"] <= 0,
}

for label, mask in numeric_rules.items():
    print(f"{label}: {mask.sum()}")


# 6. Numeric summary
print("\n[6] NUMERIC SUMMARY")

numeric_columns = [
    "default_servings",
    "estimated_cooking_minutes",
    "total_calories",
    "total_protein_g",
    "total_fat_g",
    "total_carbs_g",
    "ingredients_count",
]

print(
    df[numeric_columns]
    .describe()
    .round(2)
)


# 7. Categorical distributions
print("\n[7] SOURCE PLATFORM")
print(df["source_platform"].value_counts(dropna=False))

print("\n[8] COOKING METHOD")
print(df["cooking_method"].value_counts(dropna=False))

print("\n[9] DISH TYPE")
print(df["dish_type"].value_counts(dropna=False))

# 10. Investigate duplicated recipe names
print("\n[10] DUPLICATED RECIPE NAME INVESTIGATION")

df["normalized_name"] = (
    df["name"]
    .astype(str)
    .str.strip()
    .str.lower()
)

duplicate_summary = (
    df.groupby("normalized_name")
    .agg(
        recipe_count=("id", "size"),
        source_count=("source_platform", "nunique"),
        url_count=("source_url", "nunique"),
        min_calories=("total_calories", "min"),
        max_calories=("total_calories", "max"),
        min_ingredients=("ingredients_count", "min"),
        max_ingredients=("ingredients_count", "max"),
    )
    .query("recipe_count > 1")
    .sort_values(
        ["recipe_count", "source_count"],
        ascending=False
    )
)

print("\nTop duplicated names summary:")
print(duplicate_summary.head(20).to_string())


print("\nDetailed examples:")

top_names = duplicate_summary.head(5).index

columns_to_show = [
    "name",
    "source_platform",
    "source_url",
    "default_servings",
    "total_calories",
    "ingredients_count",
]

for recipe_name in top_names:
    print("\n" + "-" * 80)
    print(f"Normalized name: {recipe_name}")

    rows = df[df["normalized_name"] == recipe_name]

    print(
        rows[columns_to_show]
        .to_string(index=False)
    )

# 11. Nutrition outlier investigation
print("\n[11] NUTRITION OUTLIER INVESTIGATION")

df["calories_per_serving"] = (
    df["total_calories"] / df["default_servings"]
)

df["protein_per_serving"] = (
    df["total_protein_g"] / df["default_servings"]
)

df["fat_per_serving"] = (
    df["total_fat_g"] / df["default_servings"]
)

df["carbs_per_serving"] = (
    df["total_carbs_g"] / df["default_servings"]
)


nutrition_columns = [
    "calories_per_serving",
    "protein_per_serving",
    "fat_per_serving",
    "carbs_per_serving",
]

print("\nPer-serving nutrition summary:")
print(
    df[nutrition_columns]
    .describe()
    .round(2)
)


print("\nTop 20 recipes by calories per serving:")

columns_to_show = [
    "name",
    "source_platform",
    "default_servings",
    "total_calories",
    "calories_per_serving",
    "total_protein_g",
    "total_fat_g",
    "total_carbs_g",
    "ingredients_count",
]

print(
    df.sort_values(
        "calories_per_serving",
        ascending=False,
    )[columns_to_show]
    .head(20)
    .to_string(index=False)
)

# 12. Nutrition consistency check
print("\n[12] NUTRITION CONSISTENCY CHECK")

df["estimated_calories_from_macros"] = (
    df["total_protein_g"] * 4
    + df["total_carbs_g"] * 4
    + df["total_fat_g"] * 9
)

df["calorie_difference"] = (
    df["total_calories"]
    - df["estimated_calories_from_macros"]
)

df["calorie_difference_percent"] = (
    df["calorie_difference"].abs()
    / df["total_calories"].replace(0, pd.NA)
    * 100
)

print("\nCalorie difference summary:")
print(
    df["calorie_difference_percent"]
    .describe()
    .round(2)
)


# Flag records with > 30% difference
large_difference = df[
    df["calorie_difference_percent"] > 30
]

print(
    f"\nRecipes with calorie difference > 30%: "
    f"{len(large_difference)} / {len(df)}"
)

print("\nTop 20 largest calorie inconsistencies:")

columns_to_show = [
    "name",
    "source_platform",
    "total_calories",
    "estimated_calories_from_macros",
    "calorie_difference_percent",
    "total_protein_g",
    "total_fat_g",
    "total_carbs_g",
]

print(
    df.sort_values(
        "calorie_difference_percent",
        ascending=False,
    )[columns_to_show]
    .head(20)
    .to_string(index=False)
)

# 13. Compare recipe nutrition with ingredient nutrition totals
print("\n[13] RECIPE VS INGREDIENT NUTRITION CHECK")

ingredients = pd.read_csv(
    "data/interim/recipe_ingredients.csv"
)

ingredient_totals = (
    ingredients.groupby("recipe_id")
    .agg(
        ingredient_calories_sum=("calories", "sum"),
        ingredient_protein_sum=("protein_g", "sum"),
        ingredient_fat_sum=("fat_g", "sum"),
        ingredient_carbs_sum=("carbs_g", "sum"),
    )
    .reset_index()
)

comparison = df.merge(
    ingredient_totals,
    left_on="id",
    right_on="recipe_id",
    how="left",
)

comparison["calories_aggregation_diff"] = (
    comparison["total_calories"]
    - comparison["ingredient_calories_sum"]
).abs()

comparison["protein_aggregation_diff"] = (
    comparison["total_protein_g"]
    - comparison["ingredient_protein_sum"]
).abs()

comparison["fat_aggregation_diff"] = (
    comparison["total_fat_g"]
    - comparison["ingredient_fat_sum"]
).abs()

comparison["carbs_aggregation_diff"] = (
    comparison["total_carbs_g"]
    - comparison["ingredient_carbs_sum"]
).abs()


print("\nAggregation difference summary:")
print(
    comparison[
        [
            "calories_aggregation_diff",
            "protein_aggregation_diff",
            "fat_aggregation_diff",
            "carbs_aggregation_diff",
        ]
    ]
    .describe()
    .round(2)
)


print("\nTop 20 calorie aggregation differences:")

columns_to_show = [
    "name",
    "source_platform",
    "total_calories",
    "ingredient_calories_sum",
    "calories_aggregation_diff",
    "total_protein_g",
    "ingredient_protein_sum",
    "total_fat_g",
    "ingredient_fat_sum",
    "total_carbs_g",
    "ingredient_carbs_sum",
]

print(
    comparison.sort_values(
        "calories_aggregation_diff",
        ascending=False,
    )[columns_to_show]
    .head(20)
    .to_string(index=False)
)

# 14. Inspect ingredients of recipes with large nutrition inconsistency
print("\n[14] INGREDIENT-LEVEL INVESTIGATION")

top_inconsistent_recipes = (
    df.sort_values(
        "calorie_difference_percent",
        ascending=False,
    )
    .head(5)
)

ingredient_columns = [
    "raw_text",
    "cleaned_name",
    "master_ingredient_name",
    "required_quantity",
    "unit",
    "estimated_weight_g",
    "calories",
    "protein_g",
    "fat_g",
    "carbs_g",
    "match_confidence",
    "match_method",
]

for _, recipe in top_inconsistent_recipes.iterrows():
    recipe_id = recipe["id"]

    print("\n" + "=" * 100)
    print(f"Recipe: {recipe['name']}")
    print(f"Recipe ID: {recipe_id}")
    print(f"Total calories: {recipe['total_calories']}")
    print(
        "Calories estimated from macros: "
        f"{recipe['estimated_calories_from_macros']:.1f}"
    )
    print(
        "Difference: "
        f"{recipe['calorie_difference_percent']:.2f}%"
    )

    recipe_ingredients = ingredients[
        ingredients["recipe_id"] == recipe_id
    ]

    print(
        recipe_ingredients[ingredient_columns]
        .to_string(index=False)
    )