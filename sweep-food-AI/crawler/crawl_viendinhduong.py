"""Viện Dinh Dưỡng Quốc Gia (NIN) Food & Nutrition Crawler.

Fetches the complete food composition database from:
https://viendinhduong.vn/vi/cong-cu-va-tien-ich/gia-tri-dinh-duong-thuc-pham

Endpoint: /api/fe/foodNatunal/getPageFoodData
Extracts 853+ standardized Vietnamese ingredients with complete macronutrients,
micronutrients, vitamins, minerals, and amino acids.
"""

from __future__ import annotations

import csv
import json
import logging
import re
import sys
import unicodedata
from pathlib import Path
from typing import Any

import requests

# Ensure UTF-8 output encoding on Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger("nin_crawler")

BASE_URL = "https://viendinhduong.vn/api/fe/foodNatunal/getPageFoodData"

# Mapping common Vietnamese/English nutrient labels to standardized schema keys
NUTRIENT_KEY_MAP = {
    # Macros
    "chất đạm": "protein_g",
    "protein": "protein_g",
    "chất béo": "fat_g",
    "fat": "fat_g",
    "total lipid": "fat_g",
    "chất bột đường": "carbs_g",
    "carbohydrate by difference": "carbs_g",
    "chất xơ": "fiber_g",
    "fiber": "fiber_g",
    "sugars, total": "sugar_g",
    "nước": "water_g",
    "water": "water_g",
    "tro": "ash_g",
    "ash": "ash_g",
    # Minerals
    "canxi": "calcium_mg",
    "ca": "calcium_mg",
    "sắt": "iron_mg",
    "fe": "iron_mg",
    "natri": "sodium_mg",
    "na": "sodium_mg",
    "kali": "potassium_mg",
    "k": "potassium_mg",
    "kẽm": "zinc_mg",
    "zn": "zinc_mg",
    "magie": "magnesium_mg",
    "mg": "magnesium_mg",
    "photpho": "phosphorus_mg",
    "p": "phosphorus_mg",
    "đồng": "copper_mg",
    "cu": "copper_mg",
    "mangan": "manganese_mg",
    "mn": "manganese_mg",
    "selen": "selenium_mcg",
    "se": "selenium_mcg",
    # Vitamins
    "vit c": "vitamin_c_mg",
    "retinol": "retinol_mcg",
    "vit a-rae": "vitamin_a_rae_mcg",
    "thiamin": "vitamin_b1_mg",
    "vitamin b1 (thiamin)": "vitamin_b1_mg",
    "riboflavin": "vitamin_b2_mg",
    "vitamin b2 (riboflavin)": "vitamin_b2_mg",
    "niacin": "vitamin_b3_mg",
    "vitamin b3 (niacin)": "vitamin_b3_mg",
    "pantothenic acid": "vitamin_b5_mg",
    "vitamin b5 (axit pantothenic)": "vitamin_b5_mg",
    "vit b6": "vitamin_b6_mg",
    "folate, total": "folate_total_mcg",
    "folate tổng số": "folate_total_mcg",
    "folate, food": "folate_food_mcg",
}


def normalize_nutrient_label(label: str | None) -> str:
    """Normalize Unicode, case and whitespace without removing qualifiers."""
    return " ".join(unicodedata.normalize("NFC", label or "").casefold().split())


def nutrient_key(label: str | None) -> str | None:
    """Resolve exact labels or a verified pair of parenthetical synonyms.

    Both parts must independently identify the same nutrient. Never discard
    unknown qualifiers (e.g. ``Fat (saturated)``) or match substrings.
    """
    normalized = normalize_nutrient_label(label)
    exact = NUTRIENT_KEY_MAP.get(normalized)
    if exact:
        return exact
    match = re.fullmatch(r"([^()]+)\(([^()]+)\)", normalized)
    if match:
        base = NUTRIENT_KEY_MAP.get(normalize_nutrient_label(match[1]))
        synonym = NUTRIENT_KEY_MAP.get(normalize_nutrient_label(match[2]))
        if base is not None and base == synonym:
            return base
    return None


def fetch_all_food_data(page_size: int = 1000) -> dict[str, Any]:
    """Fetch all food and nutrition records from Viện Dinh Dưỡng API."""
    headers = {
        "Accept": "application/json",
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        ),
    }

    params = {
        "page": 1,
        "pageSize": page_size,
    }

    logger.info("Connecting to Viện Dinh Dưỡng endpoint: %s ...", BASE_URL)
    response = requests.get(BASE_URL, params=params, headers=headers, timeout=30)
    response.raise_for_status()
    payload = response.json()

    total = payload.get("total", 0)
    data = payload.get("data", [])
    logger.info("Successfully fetched %d items out of %d total from API.", len(data), total)
    return payload


def parse_food_item(item: dict[str, Any]) -> dict[str, Any]:
    """Normalize raw API food record into structured schema."""
    code = str(item.get("code") or "").strip()
    name_vi = str(item.get("name_vi") or "").strip()
    name_en = str(item.get("name_en") or "").strip()
    category_vi = str(item.get("category") or "").strip()
    category_en = str(item.get("categoryEn") or "").strip()
    energy_kcal = item.get("energy")

    flattened: dict[str, Any] = {
        "code": code,
        "name_vi": name_vi,
        "name_en": name_en,
        "category_vi": category_vi,
        "category_en": category_en,
        "energy_kcal": energy_kcal,
        "protein_g": None,
        "fat_g": None,
        "carbs_g": None,
        "fiber_g": None,
        "sugar_g": None,
        "water_g": None,
        "ash_g": None,
        "calcium_mg": None,
        "iron_mg": None,
        "sodium_mg": None,
        "potassium_mg": None,
        "zinc_mg": None,
        "magnesium_mg": None,
        "phosphorus_mg": None,
        "copper_mg": None,
        "manganese_mg": None,
        "selenium_mcg": None,
        "vitamin_c_mg": None,
        "retinol_mcg": None,
        "vitamin_a_rae_mcg": None,
        "vitamin_b1_mg": None,
        "vitamin_b2_mg": None,
        "vitamin_b3_mg": None,
        "vitamin_b5_mg": None,
        "vitamin_b6_mg": None,
        "folate_total_mcg": None,
    }

    raw_nutrients = item.get("nutrition", [])
    for n in raw_nutrients:
        val = n.get("value")

        std_key = nutrient_key(n.get("name")) or nutrient_key(n.get("name_en"))
        if std_key and val is not None:
            flattened[std_key] = val

    # Retain full raw nutrients for deep auditing / ML expansion
    flattened["raw_nutrition_details"] = json.dumps(raw_nutrients, ensure_ascii=False)
    return flattened


def main() -> None:
    """Execute end-to-end crawl, parsing, and export."""
    workspace_root = Path(__file__).resolve().parent.parent
    raw_dir = workspace_root / "data" / "raw" / "viendinhduong"
    processed_dir = workspace_root / "data" / "processed" / "viendinhduong"

    raw_dir.mkdir(parents=True, exist_ok=True)
    processed_dir.mkdir(parents=True, exist_ok=True)

    # 1. Fetch raw API payload
    payload = fetch_all_food_data(page_size=1000)
    data = payload.get("data", [])

    raw_json_path = raw_dir / "food_nutrition_raw.json"
    with open(raw_json_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    logger.info("Raw JSON saved to: %s", raw_json_path)

    # 2. Parse and normalize items
    parsed_items = [parse_food_item(item) for item in data]

    # 3. Export flattened CSV for master_ingredients catalog
    csv_path = processed_dir / "master_ingredients_nutrition.csv"
    if parsed_items:
        fieldnames = [k for k in parsed_items[0].keys() if k != "raw_nutrition_details"]
        with open(csv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for row in parsed_items:
                row_copy = {k: v for k, v in row.items() if k != "raw_nutrition_details"}
                writer.writerow(row_copy)
        logger.info("Processed catalog CSV saved to: %s", csv_path)

    # 4. Export distinct categories
    categories: set[tuple[str, str]] = set()
    for item in parsed_items:
        c_vi = item.get("category_vi", "")
        c_en = item.get("category_en", "")
        if c_vi:
            categories.add((c_vi, c_en))

    cat_csv_path = processed_dir / "ingredient_categories.csv"
    with open(cat_csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["category_vi", "category_en"])
        for c_vi, c_en in sorted(categories):
            writer.writerow([c_vi, c_en])
    logger.info("Extracted %d unique categories saved to: %s", len(categories), cat_csv_path)

    # 5. Output summary statistics
    print("\n" + "=" * 60)
    print("VIỆN DINH DƯỠNG CRAWL & INGESTION COMPLETED")
    print("=" * 60)
    print(f"Total Ingredients Harvested: {len(parsed_items)}")
    print(f"Total Unique Categories:     {len(categories)}")
    print(f"Raw Output:                  {raw_json_path}")
    print(f"Processed Catalog CSV:       {csv_path}")
    print(f"Categories CSV:              {cat_csv_path}")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
