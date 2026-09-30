import json
from pathlib import Path


PATH = Path(
    "data/processed/viendinhduong/ingredient_alias_map.json"
)

with PATH.open("r", encoding="utf-8") as file:
    data = json.load(file)


print("=" * 80)
print("PROCESSED INGREDIENT ALIAS MAP EDA")
print("=" * 80)

print("\n[1] BASIC STRUCTURE")
print(f"Top-level type: {type(data).__name__}")

if isinstance(data, dict):
    print(f"Number of top-level entries: {len(data)}")

    print("\nFirst 20 entries:")
    for index, (key, value) in enumerate(data.items()):
        if index >= 20:
            break

        print(f"{key!r} -> {value!r}")

elif isinstance(data, list):
    print(f"Number of items: {len(data)}")

    print("\nFirst 20 items:")
    for item in data[:20]:
        print(repr(item))

import pandas as pd


# 2. Alias target validation
print("\n[2] ALIAS TARGET VALIDATION")

MASTER_PATH = (
    "data/processed/viendinhduong/master_ingredients_nutrition.csv"
)

master = pd.read_csv(MASTER_PATH)

master_codes = set(
    master["code"]
    .astype(str)
)

alias_codes = set(
    str(code)
    for code in data.values()
)

invalid_codes = alias_codes - master_codes
unused_master_codes = master_codes - alias_codes


print(f"Unique master codes referenced by aliases: {len(alias_codes)}")

print(
    f"Alias target codes not found in master: "
    f"{len(invalid_codes)}"
)

if invalid_codes:
    print("\nInvalid alias target codes:")
    print(sorted(invalid_codes)[:50])


print(
    f"\nMaster ingredients with no alias: "
    f"{len(unused_master_codes)}"
)

if unused_master_codes:
    print("\nSample master codes with no alias:")
    print(sorted(unused_master_codes)[:50])

# 3. Inspect aliases with invalid target codes
print("\n[3] INVALID ALIAS TARGET DETAILS")

invalid_aliases = {
    alias: str(code)
    for alias, code in data.items()
    if str(code) in invalid_codes
}

print(f"Aliases pointing to invalid codes: {len(invalid_aliases)}")

for alias, code in sorted(invalid_aliases.items()):
    print(f"{alias!r} -> {code}")

# 4. Search candidate master ingredients for invalid aliases
print("\n[4] INVALID ALIAS REPLACEMENT CANDIDATES")

keywords = [
    "kem",
    "ếch",
]

for keyword in keywords:
    print("\n" + "-" * 80)
    print(f"Keyword: {keyword}")

    matches = master[
        master["name_vi"]
        .astype(str)
        .str.contains(
            keyword,
            case=False,
            na=False,
        )
    ]

    print(
        matches[
            [
                "code",
                "name_vi",
                "name_en",
                "category_vi",
            ]
        ]
        .to_string(index=False)
    )

# 5. Compare replacement candidates
print("\n[5] REPLACEMENT CANDIDATE COMPARISON")

candidate_codes = [
    12079,
    20070,
    7080,
]

candidate_rows = master[
    master["code"].isin(candidate_codes)
]

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
    candidate_rows[columns_to_show]
    .to_string(index=False)
)


# Check how these candidates are currently used in recipe ingredients
ingredients = pd.read_csv(
    "data/interim/recipe_ingredients.csv"
)

print("\nCurrent usage in recipe_ingredients:")

for code in candidate_codes:
    rows = ingredients[
        ingredients["master_ingredient_code"] == code
    ]

    print("\n" + "-" * 80)
    print(f"Code: {code}")
    print(f"Occurrences: {len(rows)}")

    if not rows.empty:
        print(
            rows[
                [
                    "raw_text",
                    "cleaned_name",
                    "master_ingredient_name",
                    "match_method",
                ]
            ]
            .head(20)
            .to_string(index=False)
        )

# 6. Normalized alias collision check
print("\n[6] NORMALIZED ALIAS COLLISION CHECK")

import re
import unicodedata
from collections import defaultdict


def normalize_alias(text: str) -> str:
    text = unicodedata.normalize("NFC", text)
    text = text.strip().lower()
    text = re.sub(r"\s+", " ", text)
    return text


normalized_targets = defaultdict(set)
normalized_originals = defaultdict(list)

for alias, code in data.items():
    normalized = normalize_alias(alias)

    normalized_targets[normalized].add(str(code))
    normalized_originals[normalized].append(alias)


collisions = {
    alias: targets
    for alias, targets in normalized_targets.items()
    if len(targets) > 1
}

duplicate_normalized_aliases = {
    alias: originals
    for alias, originals in normalized_originals.items()
    if len(originals) > 1
}


print(
    f"Normalized aliases mapping to multiple codes: "
    f"{len(collisions)}"
)

if collisions:
    print("\nCollisions:")

    for alias, targets in sorted(collisions.items()):
        print(
            f"{alias!r} -> "
            f"{sorted(targets)} | "
            f"originals={normalized_originals[alias]}"
        )


print(
    f"\nNormalized aliases with multiple original forms: "
    f"{len(duplicate_normalized_aliases)}"
)

if duplicate_normalized_aliases:
    print("\nSample duplicated normalized aliases:")

    for index, (alias, originals) in enumerate(
        sorted(duplicate_normalized_aliases.items())
    ):
        if index >= 30:
            break

        print(f"{alias!r} <- {originals}")