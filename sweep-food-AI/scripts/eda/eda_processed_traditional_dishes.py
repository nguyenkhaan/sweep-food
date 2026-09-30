import pandas as pd


PATH = (
    "data/processed/viendinhduong/"
    "traditional_dishes_nutrition.csv"
)

df = pd.read_csv(PATH)

print("=" * 80)
print("PROCESSED TRADITIONAL DISHES NUTRITION EDA")
print("=" * 80)


# 1. Identifier checks
print("\n[1] IDENTIFIER CHECK")

print(f"Rows: {len(df)}")
print(f"Unique codes: {df['code'].nunique()}")
print(f"Duplicate codes: {df['code'].duplicated().sum()}")

normalized_names = (
    df["name_vi"]
    .astype(str)
    .str.strip()
    .str.lower()
)

print(
    f"Unique normalized Vietnamese names: "
    f"{normalized_names.nunique()}"
)

print(
    f"Rows with duplicated normalized names: "
    f"{normalized_names.duplicated(keep=False).sum()}"
)


# 2. Negative nutrition
print("\n[2] NEGATIVE NUTRITION VALUES")

non_nutrition_columns = {
    "code",
    "name_vi",
    "name_en",
    "category_vi",
    "category_en",
}

nutrition_columns = [
    column
    for column in df.columns
    if column not in non_nutrition_columns
]

negative_found = False

for column in nutrition_columns:
    count = (df[column] < 0).sum()

    if count > 0:
        negative_found = True
        print(f"{column}: {count}")

if not negative_found:
    print("None")

# 3. Core nutrition completeness
print("\n[3] CORE NUTRITION COMPLETENESS")

core_columns = [
    "energy_kcal",
    "protein_g",
    "fat_g",
    "carbs_g",
]

for column in core_columns:
    missing = df[column].isna().sum()
    zero = (df[column] == 0).sum()

    print(
        f"{column}: "
        f"missing={missing} "
        f"({missing / len(df) * 100:.2f}%), "
        f"zero={zero}"
    )

missing_any_core = df[core_columns].isna().any(axis=1)
missing_all_core = df[core_columns].isna().all(axis=1)

print(
    f"\nRows missing at least one core nutrition field: "
    f"{missing_any_core.sum()}"
)

print(
    f"Rows missing all core nutrition fields: "
    f"{missing_all_core.sum()}"
)

print("\nSample rows missing core nutrition:")

print(
    df.loc[
        missing_any_core,
        [
            "code",
            "name_vi",
            "energy_kcal",
            "protein_g",
            "fat_g",
            "carbs_g",
        ],
    ]
    .head(30)
    .to_string(index=False)
)

# 4. Estimate missing fat from calories
print("\n[4] IMPLIED FAT ESTIMATION")

df["implied_fat_g"] = (
    df["energy_kcal"]
    - 4 * df["protein_g"]
    - 4 * df["carbs_g"]
) / 9

print("\nImplied fat summary:")
print(
    df["implied_fat_g"]
    .describe()
    .round(2)
)

negative_fat = df["implied_fat_g"] < 0

print(
    f"\nRows with negative implied fat: "
    f"{negative_fat.sum()}"
)

print("\nLowest implied fat values:")

print(
    df[
        [
            "code",
            "name_vi",
            "energy_kcal",
            "protein_g",
            "carbs_g",
            "implied_fat_g",
        ]
    ]
    .sort_values("implied_fat_g")
    .head(20)
    .to_string(index=False)
)

print("\nHighest implied fat values:")

print(
    df[
        [
            "code",
            "name_vi",
            "energy_kcal",
            "protein_g",
            "carbs_g",
            "implied_fat_g",
        ]
    ]
    .sort_values(
        "implied_fat_g",
        ascending=False,
    )
    .head(20)
    .to_string(index=False)
)

# 5. Overall nutrition completeness
print("\n[5] NUTRITION COMPLETENESS")

non_nutrition_columns = {
    "code",
    "name_vi",
    "name_en",
    "category_vi",
    "category_en",
}

nutrition_columns = [
    column
    for column in df.columns
    if column not in non_nutrition_columns
]

completeness = pd.DataFrame(
    {
        "missing_count": df[nutrition_columns].isna().sum(),
        "missing_percent": (
            df[nutrition_columns].isna().mean() * 100
        ).round(2),
        "available_count": df[nutrition_columns].notna().sum(),
    }
).sort_values(
    "missing_percent",
    ascending=False,
)

print(completeness.to_string())

# 6. Core nutrition outlier check
print("\n[6] CORE NUTRITION OUTLIERS")

columns_to_check = [
    "energy_kcal",
    "protein_g",
    "carbs_g",
]

print("\nSummary:")
print(
    df[columns_to_check]
    .describe()
    .round(2)
)

for column in columns_to_check:
    q1 = df[column].quantile(0.25)
    q3 = df[column].quantile(0.75)
    iqr = q3 - q1

    lower = q1 - 1.5 * iqr
    upper = q3 + 1.5 * iqr

    outliers = df[
        (df[column] < lower)
        | (df[column] > upper)
    ]

    print("\n" + "-" * 80)
    print(f"{column}")
    print(f"IQR range: {lower:.2f} -> {upper:.2f}")
    print(f"Outlier rows: {len(outliers)}")

    if not outliers.empty:
        print(
            outliers[
                [
                    "code",
                    "name_vi",
                    "energy_kcal",
                    "protein_g",
                    "carbs_g",
                ]
            ]
            .sort_values(
                column,
                ascending=False,
            )
            .to_string(index=False)
        )