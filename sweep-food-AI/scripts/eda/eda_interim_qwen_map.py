import json
from pathlib import Path


PATH = Path("data/interim/qwen_extracted_map.json")

with PATH.open("r", encoding="utf-8") as file:
    data = json.load(file)

print("[1] QWEN EXTRACTED MAP STRUCTURE")
print(f"Top-level type: {type(data).__name__}")

if isinstance(data, dict):
    print(f"Number of entries: {len(data)}")

    print("\nFirst 5 entries:")
    for index, (key, value) in enumerate(data.items()):
        if index >= 5:
            break

        print("-" * 80)
        print(f"KEY: {key!r}")
        print(f"VALUE TYPE: {type(value).__name__}")
        print(f"VALUE: {value!r}")

elif isinstance(data, list):
    print(f"Number of entries: {len(data)}")

    print("\nFirst 5 entries:")
    for value in data[:5]:
        print("-" * 80)
        print(f"TYPE: {type(value).__name__}")
        print(f"VALUE: {value!r}")

# 2. Basic mapping quality
print("\n[2] BASIC MAPPING QUALITY")

empty_keys = [
    key
    for key in data
    if not str(key).strip()
]

empty_values = [
    key
    for key, value in data.items()
    if value is None or not str(value).strip()
]

identity_mappings = [
    (key, value)
    for key, value in data.items()
    if str(key).strip().lower()
    == str(value).strip().lower()
]

unique_outputs = len(
    {
        str(value).strip().lower()
        for value in data.values()
        if value is not None
    }
)

print(f"Total mappings: {len(data)}")
print(f"Empty keys: {len(empty_keys)}")
print(f"Empty values: {len(empty_values)}")
print(f"Unique normalized outputs: {unique_outputs}")
print(f"Identity mappings: {len(identity_mappings)}")

print("\nSample identity mappings:")
for key, value in identity_mappings[:20]:
    print(f"{key!r} -> {value!r}")

# 3. Complex extracted outputs
print("\n[3] COMPLEX EXTRACTED OUTPUTS")

complex_markers = [
    " hoặc ",
    " và ",
    " / ",
    "/",
    " + ",
]

complex_outputs = []

for raw_text, extracted in data.items():
    text = str(extracted).strip().lower()

    markers_found = [
        marker
        for marker in complex_markers
        if marker in text
    ]

    word_count = len(text.split())

    if markers_found or word_count >= 6:
        complex_outputs.append(
            {
                "raw_text": raw_text,
                "extracted": extracted,
                "markers": markers_found,
                "word_count": word_count,
            }
        )

print(f"Complex mappings: {len(complex_outputs)}")
print(
    f"Percent of mappings: "
    f"{len(complex_outputs) / len(data) * 100:.2f}%"
)

print("\nSample complex mappings:")

for row in complex_outputs[:40]:
    print("-" * 80)
    print(f"RAW: {row['raw_text']!r}")
    print(f"EXTRACTED: {row['extracted']!r}")
    print(
        f"WORD COUNT: {row['word_count']} | "
        f"MARKERS: {row['markers']}"
    )

# 4. Match outcomes for complex Qwen outputs
print("\n[4] COMPLEX OUTPUT MATCH OUTCOMES")

import pandas as pd

ingredients = pd.read_csv(
    "data/interim/recipe_ingredients.csv"
)

complex_names = {
    str(row["extracted"]).strip().lower()
    for row in complex_outputs
}

affected = ingredients[
    ingredients["cleaned_name"]
    .astype(str)
    .str.strip()
    .str.lower()
    .isin(complex_names)
].copy()

print(f"Affected recipe ingredient rows: {len(affected)}")

print("\nMatch method distribution:")
print(
    affected["match_method"]
    .value_counts(dropna=False)
    .to_string()
)

print("\nMatched vs unmatched:")

unmatched = affected[
    affected["master_ingredient_code"].isna()
]

print(f"Matched rows: {len(affected) - len(unmatched)}")
print(f"Unmatched rows: {len(unmatched)}")

if len(affected) > 0:
    print(
        f"Unmatched rate: "
        f"{len(unmatched) / len(affected) * 100:.2f}%"
    )

print("\nSample affected rows:")

print(
    affected[
        [
            "raw_text",
            "cleaned_name",
            "master_ingredient_name",
            "match_method",
            "match_confidence",
        ]
    ]
    .head(40)
    .to_string(index=False)
)

# 5. Qwen match confidence distribution
print("\n[5] QWEN MATCH CONFIDENCE DISTRIBUTION")

qwen_rows = ingredients[
    ingredients["match_method"] == "QWEN_LLM_MATCH"
]

print(f"Total QWEN_LLM_MATCH rows: {len(qwen_rows)}")

print("\nConfidence value counts:")
print(
    qwen_rows["match_confidence"]
    .value_counts(dropna=False)
    .sort_index()
    .to_string()
)

print("\nConfidence summary:")
print(
    qwen_rows["match_confidence"]
    .describe()
    .to_string()
)

# 6. Qwen map usage coverage
print("\n[6] QWEN MAP USAGE COVERAGE")

ingredient_raw_texts = set(
    ingredients["raw_text"]
    .dropna()
    .astype(str)
)

map_keys = set(data.keys())

used_keys = map_keys & ingredient_raw_texts
unused_keys = map_keys - ingredient_raw_texts

print(f"Qwen map entries: {len(map_keys)}")
print(f"Entries found in recipe_ingredients: {len(used_keys)}")
print(f"Entries not found in recipe_ingredients: {len(unused_keys)}")

print(
    f"Usage rate: "
    f"{len(used_keys) / len(map_keys) * 100:.2f}%"
)

print("\nSample unused entries:")
for key in sorted(unused_keys)[:30]:
    print(f"{key!r} -> {data[key]!r}")

# 7. Final outcomes for Qwen-extracted inputs
print("\n[7] QWEN EXTRACTED INPUT OUTCOMES")

qwen_input_rows = ingredients[
    ingredients["raw_text"]
    .astype(str)
    .isin(map_keys)
].copy()

print(f"Rows corresponding to Qwen map keys: {len(qwen_input_rows)}")
print(f"Unique raw_text values: {qwen_input_rows['raw_text'].nunique()}")

print("\nFinal match method distribution:")
print(
    qwen_input_rows["match_method"]
    .value_counts(dropna=False)
    .to_string()
)

missing_master = qwen_input_rows[
    qwen_input_rows["master_ingredient_code"].isna()
]

print(f"\nRows without master ingredient: {len(missing_master)}")

if len(qwen_input_rows) > 0:
    print(
        f"Missing master rate: "
        f"{len(missing_master) / len(qwen_input_rows) * 100:.2f}%"
    )

print("\nSample rows without master ingredient:")

print(
    missing_master[
        [
            "raw_text",
            "cleaned_name",
            "match_method",
            "match_confidence",
        ]
    ]
    .head(30)
    .to_string(index=False)
)

# 8. UNMATCHED rows that still have master ingredient
print("\n[8] UNMATCHED WITH MASTER INGREDIENT")

unmatched_with_master = qwen_input_rows[
    (qwen_input_rows["match_method"] == "UNMATCHED")
    & qwen_input_rows["master_ingredient_code"].notna()
].copy()

print(
    f"UNMATCHED rows with master ingredient: "
    f"{len(unmatched_with_master)}"
)

print("\nSample rows:")

print(
    unmatched_with_master[
        [
            "raw_text",
            "cleaned_name",
            "master_ingredient_code",
            "master_ingredient_name",
            "match_method",
            "match_confidence",
        ]
    ]
    .head(40)
    .to_string(index=False)
)