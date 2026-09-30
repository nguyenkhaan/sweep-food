import json
import sys
from collections import Counter
from pathlib import Path


# Add project root to Python path
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from crawler.crawl_viendinhduong import nutrient_key


RAW_PATH = ROOT / "data" / "raw" / "viendinhduong" / "food_nutrition_raw.json"

with open(RAW_PATH, "r", encoding="utf-8") as file:
    payload = json.load(file)

foods = payload["data"]

traditional = [
    item
    for item in foods
    if item.get("category") == "Thức ăn truyền thống"
]

print("[1] UNMAPPED RAW NUTRIENT LABELS")
print(f"Traditional dishes: {len(traditional)}")

unmapped = Counter()

for item in traditional:
    for nutrient in item.get("nutrition", []):
        mapped = (
            nutrient_key(nutrient.get("name"))
            or nutrient_key(nutrient.get("name_en"))
        )

        if not mapped:
            unmapped[
                (
                    nutrient.get("name"),
                    nutrient.get("name_en"),
                )
            ] += 1

print(f"Unique unmapped label pairs: {len(unmapped)}")

for (name, name_en), count in unmapped.most_common():
    print(
        f"{count:>3} | "
        f"name={name!r} | "
        f"name_en={name_en!r}"
    )
