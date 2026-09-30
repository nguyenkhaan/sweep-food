import pandas as pd


pairs = [
    (
        "recipes",
        "data/interim/recipes_crawled_cleaned.csv",
        "data/processed/recipes/recipes.csv",
    ),
    (
        "recipe_ingredients",
        "data/interim/recipe_ingredients.csv",
        "data/processed/recipes/recipe_ingredients.csv",
    ),
]


for name, interim_path, processed_path in pairs:
    print("\n" + "=" * 80)
    print(name.upper())
    print("=" * 80)

    interim = pd.read_csv(interim_path)
    processed = pd.read_csv(processed_path)

    print(f"Interim shape:   {interim.shape}")
    print(f"Processed shape: {processed.shape}")

    print(
        f"Same columns: "
        f"{interim.columns.tolist() == processed.columns.tolist()}"
    )

    print(
        f"DataFrames exactly equal: "
        f"{interim.equals(processed)}"
    )

    if (
        interim.shape == processed.shape
        and interim.columns.tolist() == processed.columns.tolist()
    ):
        different_rows = (
            ~(interim.eq(processed) | (interim.isna() & processed.isna()))
        ).any(axis=1)

        print(
            f"Rows containing any difference: "
            f"{different_rows.sum()}"
        )