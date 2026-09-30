"""Focused label regressions and source-backed traditional-dish checks."""

import csv
import json
import unicodedata
from pathlib import Path

import pytest

from crawler.crawl_viendinhduong import NUTRIENT_KEY_MAP, nutrient_key, parse_food_item
from scripts.regenerate_traditional_dishes import render_traditional_dishes


@pytest.mark.parametrize("field", ["name", "name_en"])
@pytest.mark.parametrize("label", [
    "Chất béo (Fat)", "Total lipid (Fat)", "fat", "chất béo",
    "  CHẤT  BÉO\t( FAT )  ", unicodedata.normalize("NFD", "Chất béo (Fat)"),
])
def test_fat_labels(label, field):
    parsed = parse_food_item({"nutrition": [{field: label, "value": 32.65}]})
    assert parsed["fat_g"] == 32.65


@pytest.mark.parametrize("label,key", NUTRIENT_KEY_MAP.items())
def test_existing_labels(label, key):
    assert parse_food_item({"nutrition": [{"name": label, "value": 2.5}]})[key] == 2.5


@pytest.mark.parametrize("label", [
    None, "", "unknown", "Saturated fat", "Fatty acids, total saturated",
    "Unknown (Fat)", "Fat (saturated)", "Fat (Protein)", "Fat (unknown) (Fat)",
])
def test_unknown_and_qualified_labels(label):
    assert nutrient_key(label) is None
    parsed = parse_food_item({"nutrition": [{"name": label, "value": 9}]})
    assert all(parsed.get(key) is None for key in set(NUTRIENT_KEY_MAP.values()))


@pytest.mark.parametrize("value", [None, 0, 1.25])
def test_values_and_raw_details_are_preserved(value):
    nutrients = [{"name": "Chất béo (Fat)", "value": value, "unit": "g"}]
    parsed = parse_food_item({"energy": 1, "nutrition": nutrients})
    assert parsed["fat_g"] == value
    assert parsed["energy_kcal"] == 1
    assert json.loads(parsed["raw_nutrition_details"]) == nutrients


def test_english_fallback_and_vietnamese_precedence():
    assert parse_food_item({"nutrition": [
        {"name": "unknown", "name_en": "Total lipid (Fat)", "value": 3},
    ]})["fat_g"] == 3
    parsed = parse_food_item({"nutrition": [
        {"name": "Chất đạm", "name_en": "Fat", "value": 3},
    ]})
    assert parsed["protein_g"] == 3
    assert parsed["fat_g"] is None


def test_processed_traditional_dishes_match_raw():
    root = Path(__file__).resolve().parents[1]
    foods = json.loads((root / "data/raw/viendinhduong/food_nutrition_raw.json")
                       .read_text(encoding="utf-8"))["data"]
    path = root / "data/processed/viendinhduong/traditional_dishes_nutrition.csv"
    with path.open(encoding="utf-8", newline="") as file:
        reader = csv.DictReader(file)
        fields = reader.fieldnames
        rows = list(reader)
    traditional = [item for item in foods if item["category"] == "Thức ăn truyền thống"]
    assert len(rows) == len(traditional) == 78
    assert len({row["code"] for row in rows}) == 78
    for raw, row in zip(traditional, rows):
        assert row["code"] == raw["code"]
        fat = next(n["value"] for n in raw["nutrition"] if n["name"] == "Chất béo (Fat)")
        assert float(row["fat_g"]) == fat >= 0
    muoi = next(row for row in rows if row["code"] == "15074")
    assert muoi["fat_g"] == "32.65"
    assert muoi["energy_kcal"] == "1"
    assert path.read_bytes() == render_traditional_dishes(foods, fields).encode("utf-8")
