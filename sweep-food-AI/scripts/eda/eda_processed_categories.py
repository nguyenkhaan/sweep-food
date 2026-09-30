import pandas as pd


CATEGORY_PATH = (
    "data/processed/viendinhduong/ingredient_categories.csv"
)

MASTER_PATH = (
    "data/processed/viendinhduong/master_ingredients_nutrition.csv"
)


categories = pd.read_csv(CATEGORY_PATH)
master = pd.read_csv(MASTER_PATH)


print("=" * 80)
print("PROCESSED INGREDIENT CATEGORIES EDA")
print("=" * 80)


# 1. Category coverage
print("\n[1] CATEGORY COVERAGE")

category_set = set(
    categories["category_vi"]
    .dropna()
    .str.strip()
)

master_category_set = set(
    master["category_vi"]
    .dropna()
    .str.strip()
)

print(
    f"Categories defined in ingredient_categories: "
    f"{len(category_set)}"
)

print(
    f"Categories used in master ingredients: "
    f"{len(master_category_set)}"
)


undefined_categories = (
    master_category_set - category_set
)

unused_categories = (
    category_set - master_category_set
)


print("\nCategories used in master but NOT defined:")
print(
    sorted(undefined_categories)
    if undefined_categories
    else "None"
)


print("\nCategories defined but NOT used in master:")
print(
    sorted(unused_categories)
    if unused_categories
    else "None"
)


# Count rows affected by undefined categories
affected_rows = master[
    master["category_vi"].isin(
        undefined_categories
    )
]

print(
    f"\nMaster ingredient rows using undefined categories: "
    f"{len(affected_rows)}"
)

if not affected_rows.empty:
    print("\nAffected rows by category:")

    print(
        affected_rows["category_vi"]
        .value_counts()
        .to_string()
    )

# 2. Inspect ingredients in undefined categories
print("\n[2] INGREDIENTS IN UNDEFINED CATEGORIES")

for category in sorted(undefined_categories):
    rows = master[
        master["category_vi"] == category
    ]

    print("\n" + "-" * 80)
    print(f"Category: {category}")
    print(f"Count: {len(rows)}")

    print(
        rows[
            [
                "code",
                "name_vi",
                "name_en",
            ]
        ]
        .head(30)
        .to_string(index=False)
    )

# 3. Standard category list
print("\n[3] STANDARD CATEGORY LIST")

print(
    categories[
        [
            "category_vi",
            "category_en",
        ]
    ]
    .sort_values("category_vi")
    .to_string(index=False)
)

# 4. Proposed category mapping coverage
print("\n[4] PROPOSED CATEGORY MAPPING COVERAGE")

proposed_mapping = {
    "Gia vị": "Gia vị, nước chấm",
    "Gia vị và nước chấm": "Gia vị, nước chấm",
    "Rau củ quả": "Rau, quả, củ dùng làm rau",
    "Rau củ quả và sản phẩm chế biến": "Rau, quả, củ dùng làm rau",
    "Thủy hải sản": "Thủy sản và sản phẩm chế biến",
    "Đồ ngọt": "Đồ ngọt (đường, bánh, mứt, kẹo)",
    "Đồ uống và nước": "Nước giải khát",
    "Các loại hạt": "Hạt, quả giàu đạm, béo và sản phẩm chế biến",
    "Hạt và sản phẩm chế biến":
        "Hạt, quả giàu đạm, béo và sản phẩm chế biến",
    "Đậu, đỗ và sản phẩm chế biến":
        "Hạt, quả giàu đạm, béo và sản phẩm chế biến",
    "Đậu phụ và sản phẩm chế biến":
        "Hạt, quả giàu đạm, béo và sản phẩm chế biến",
}

affected = master[
    master["category_vi"].isin(proposed_mapping)
].copy()

affected["proposed_category"] = (
    affected["category_vi"].map(proposed_mapping)
)

print(f"Rows covered by proposed mapping: {len(affected)}")

print("\nMapping summary:")

summary = (
    affected.groupby(
        ["category_vi", "proposed_category"]
    )
    .size()
    .reset_index(name="rows")
)

print(summary.to_string(index=False))


still_undefined = (
    set(master["category_vi"])
    - category_set
    - set(proposed_mapping.keys())
)

print("\nUndefined categories remaining after proposed mapping:")
print(
    sorted(still_undefined)
    if still_undefined
    else "None"
)