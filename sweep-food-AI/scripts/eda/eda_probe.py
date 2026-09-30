from pathlib import Path

import pandas as pd


CSV_FILES = [
    Path("data/interim/recipes_crawled_cleaned.csv"),
    Path("data/interim/recipe_ingredients.csv"),
    Path("data/processed/recipes/recipes.csv"),
    Path("data/processed/recipes/recipe_ingredients.csv"),
    Path("data/processed/viendinhduong/ingredient_categories.csv"),
    Path("data/processed/viendinhduong/master_ingredients_nutrition.csv"),
    Path("data/processed/viendinhduong/traditional_dishes_nutrition.csv"),
]


def inspect_csv(path: Path) -> None:
    print("\n" + "=" * 100)
    print(path)
    print("=" * 100)

    df = pd.read_csv(path)

    print(f"\nShape: {df.shape}")

    print("\nColumns:")
    for column in df.columns:
        print(f"- {column}")

    print("\nData types:")
    print(df.dtypes)

    print("\nMissing values:")
    missing = pd.DataFrame(
        {
            "count": df.isna().sum(),
            "percent": (df.isna().mean() * 100).round(2),
        }
    )
    print(missing)

    print("\nExact duplicate rows:")
    print(df.duplicated().sum())

    print("\nFirst 3 rows:")
    print(df.head(3).to_string())


def main() -> None:
    for path in CSV_FILES:
        inspect_csv(path)


if __name__ == "__main__":
    main()