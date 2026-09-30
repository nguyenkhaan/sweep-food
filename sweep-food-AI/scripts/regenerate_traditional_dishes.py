"""Reparse the saved raw traditional dishes, allowing only fat-column changes.

Run from the repository root: python -m scripts.regenerate_traditional_dishes
No crawling, imputation, or other dataset writes are performed.
"""

import csv
import io
import json
import statistics
from pathlib import Path

from crawler.crawl_viendinhduong import parse_food_item

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data/raw/viendinhduong/food_nutrition_raw.json"
OUTPUT = ROOT / "data/processed/viendinhduong/traditional_dishes_nutrition.csv"


def render_traditional_dishes(foods, fieldnames):
    """Use the production parser and raw order with the existing CSV schema."""
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=fieldnames)
    writer.writeheader()
    for item in foods:
        if item.get("category") == "Thức ăn truyền thống":
            parsed = parse_food_item(item)
            writer.writerow({key: parsed.get(key) for key in fieldnames})
    return stream.getvalue()


def main():
    foods = json.loads(RAW.read_text(encoding="utf-8"))["data"]
    with OUTPUT.open(encoding="utf-8-sig", newline="") as file:
        reader = csv.DictReader(file)
        fieldnames = reader.fieldnames
        before = list(reader)
    rendered = render_traditional_dishes(foods, fieldnames)
    after = list(csv.DictReader(io.StringIO(rendered)))
    if not before or len(before) != len(after):
        raise ValueError("Traditional-dish row count changed; refusing to write")
    codes = [row["code"] for row in after]
    if len(codes) != len(set(codes)):
        raise ValueError("Duplicate traditional-dish codes; refusing to write")
    changed = sorted({key for old, new in zip(before, after)
                      for key in fieldnames if old[key] != new[key]})
    if set(changed) - {"fat_g"}:
        raise ValueError(f"Unexpected columns changed: {changed}; refusing to write")
    if rendered != render_traditional_dishes(foods, fieldnames):
        raise ValueError("Non-deterministic output; refusing to write")
    fats = [float(row["fat_g"]) for row in after if row["fat_g"]]
    missing_before = sum(not row["fat_g"] for row in before)
    missing_after = len(after) - len(fats)
    muoi_raw = next(item for item in foods if str(item["code"]) == "15074")
    muoi = next(row for row in after if row["code"] == "15074")
    raw_fat = next(n["value"] for n in muoi_raw["nutrition"]
                   if n["name"] == "Chất béo (Fat)")
    if float(muoi["fat_g"]) != raw_fat or muoi["energy_kcal"] != "1":
        raise ValueError("Muối vừng source values were not preserved")
    OUTPUT.write_bytes(rendered.encode("utf-8"))
    print(json.dumps({
        "rows": len(after), "missing_fat_before": missing_before,
        "missing_fat_after": missing_after,
        "recovered": missing_before - missing_after,
        "fat_min": min(fats), "fat_median": statistics.median(fats),
        "fat_mean": statistics.mean(fats), "fat_max": max(fats),
        "negative_fat_count": sum(fat < 0 for fat in fats),
        "changed_columns": changed, "deterministic": True,
        "muoi_vung_raw_fat": raw_fat,
        "muoi_vung_processed_fat": muoi["fat_g"],
        "muoi_vung_raw_energy": muoi_raw["energy"],
        "muoi_vung_processed_energy": muoi["energy_kcal"],
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
