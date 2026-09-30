import pandas as pd


PATH = "data/processed/viendinhduong/master_ingredients_nutrition.csv"

df = pd.read_csv(PATH)

print("=" * 80)
print("PROCESSED MASTER INGREDIENTS NUTRITION EDA")
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

print(f"Unique normalized Vietnamese names: {normalized_names.nunique()}")
print(
    "Rows with duplicated normalized names: "
    f"{normalized_names.duplicated(keep=False).sum()}"
)


# 2. Negative nutrition values
print("\n[2] NEGATIVE NUTRITION VALUES")

nutrition_columns = [
    col
    for col in df.columns
    if col not in [
        "code",
        "name_vi",
        "name_en",
        "category_vi",
        "category_en",
    ]
]

for column in nutrition_columns:
    negative_count = (df[column] < 0).sum()

    if negative_count > 0:
        print(f"{column}: {negative_count}")

# 3. Investigate duplicated Vietnamese names
print("\n[3] DUPLICATED VIETNAMESE NAME INVESTIGATION")

df["normalized_name_vi"] = (
    df["name_vi"]
    .astype(str)
    .str.strip()
    .str.lower()
)

duplicated_names = df[
    df["normalized_name_vi"].duplicated(keep=False)
].sort_values("normalized_name_vi")

columns_to_show = [
    "code",
    "name_vi",
    "name_en",
    "category_vi",
    "energy_kcal",
    "protein_g",
    "fat_g",
    "carbs_g",
]

print(
    duplicated_names[columns_to_show]
    .to_string(index=False)
)

# 4. Core nutrition completeness
print("\n[4] CORE NUTRITION COMPLETENESS")

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
            "category_vi",
            *core_columns,
        ],
    ]
    .head(30)
    .to_string(index=False)
)

# 5. Missing core nutrition by category
print("\n[5] MISSING CORE NUTRITION BY CATEGORY")

df["missing_core_count"] = df[core_columns].isna().sum(axis=1)
df["missing_any_core"] = df["missing_core_count"] > 0

category_missing = (
    df.groupby("category_vi")
    .agg(
        total=("code", "size"),
        missing_any_core=("missing_any_core", "sum"),
    )
)

category_missing["missing_percent"] = (
    category_missing["missing_any_core"]
    / category_missing["total"]
    * 100
)

print(
    category_missing.sort_values(
        "missing_percent",
        ascending=False,
    ).round(2)
)


print("\nRows missing all four core nutrition fields:")

missing_all = df[core_columns].isna().all(axis=1)

print(
    df.loc[
        missing_all,
        [
            "code",
            "name_vi",
            "name_en",
            "category_vi",
            *core_columns,
        ],
    ].to_string(index=False)
)

# 6. Core nutrition missing patterns
print("\n[6] CORE NUTRITION MISSING PATTERNS")

missing_pattern = df[core_columns].isna().copy()

missing_pattern["pattern"] = missing_pattern.apply(
    lambda row: ", ".join(
        column
        for column in core_columns
        if row[column]
    )
    if row.any()
    else "NONE",
    axis=1,
)

pattern_counts = (
    missing_pattern["pattern"]
    .value_counts()
)

print(pattern_counts.head(20))

print("\nRows with energy available but missing at least one macro:")

energy_available_macro_missing = (
    df["energy_kcal"].notna()
    & df[
        [
            "protein_g",
            "fat_g",
            "carbs_g",
        ]
    ].isna().any(axis=1)
)

print(
    energy_available_macro_missing.sum()
)

# 7. Master calorie vs macronutrient consistency
print("\n[7] MASTER NUTRITION CONSISTENCY")

complete_macros = df[
    [
        "energy_kcal",
        "protein_g",
        "fat_g",
        "carbs_g",
    ]
].notna().all(axis=1)

complete_df = df.loc[complete_macros].copy()

complete_df["estimated_energy_from_macros"] = (
    complete_df["protein_g"] * 4
    + complete_df["carbs_g"] * 4
    + complete_df["fat_g"] * 9
)

complete_df["energy_difference_percent"] = (
    (
        complete_df["energy_kcal"]
        - complete_df["estimated_energy_from_macros"]
    ).abs()
    / complete_df["energy_kcal"].replace(0, pd.NA)
    * 100
)

inconsistent_master = complete_df[
    complete_df["energy_difference_percent"] > 30
]

print(f"Rows with complete core nutrition: {len(complete_df)}")

print(
    "Rows with calorie difference > 30%: "
    f"{len(inconsistent_master)}"
)

print(
    f"Percentage: "
    f"{len(inconsistent_master) / len(complete_df) * 100:.2f}%"
)

print("\nTop inconsistent master ingredients:")

print(
    inconsistent_master[
        [
            "code",
            "name_vi",
            "category_vi",
            "energy_kcal",
            "estimated_energy_from_macros",
            "energy_difference_percent",
            "protein_g",
            "fat_g",
            "carbs_g",
        ]
    ]
    .sort_values(
        "energy_difference_percent",
        ascending=False,
    )
    .head(30)
    .to_string(index=False)
)