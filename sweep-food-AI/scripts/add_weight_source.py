"""Add a deterministic `weight_source` provenance column to processed recipe
ingredients.

Rationale
---------
Ingredient weights (`estimated_weight_g`) are produced by different mechanisms
with very different reliability. For a scientific/reproducible dataset we do NOT
re-guess the weights that the source never quantified (that would fabricate
precision); instead we label how each weight was obtained so downstream users
can filter by confidence.

`weight_source` values
----------------------
- measured_mass_volume : a numeric quantity in a direct mass/volume unit
                         (g, kg, ml, lit) -> weight is directly measured.
- unit_conversion_std  : a numeric quantity in a spoon/cup unit converted with a
                         standard gram factor (muong canh=15g, muong ca phe=5g,
                         chen/coc/bat=200g).
- count_portion_estimate : a numeric quantity in a countable unit
                         (qua/cu/trai/lat/con/...) times an ingredient-agnostic
                         per-piece portion; quantity is real, per-piece grams are
                         an approximation.
- vague_portion_fallback : the source gave no usable quantity (unit is
                         "phan an" or "vua du / chut it"); the weight is a
                         portion/role estimate -> lowest confidence.
- role_category_estimate : residual estimate not covered above.
- unmatched_no_nutrition : row is UNMATCHED (no master link, no nutrition).

The script is deterministic and idempotent: existing values are never modified,
only the `weight_source` column is (re)computed and appended.
"""

from __future__ import annotations

import csv
import json
import sys
from collections import Counter
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parent.parent
ING_CSV = ROOT / "data" / "processed" / "recipes" / "recipe_ingredients.csv"
ING_JSON = ROOT / "data" / "processed" / "recipes" / "recipe_ingredients.json"
CANON_ING_CSV = ROOT / "data" / "processed" / "recipes" / "canonical_recipe_ingredients.csv"
CANON_ING_JSON = ROOT / "data" / "processed" / "recipes" / "canonical_recipe_ingredients.json"
# Every processed ingredient file that must carry a consistent weight_source.
ING_FILE_PAIRS = ((ING_CSV, ING_JSON), (CANON_ING_CSV, CANON_ING_JSON))
REPORT = ROOT / "reports" / "eda" / "weight_provenance.json"

MEASURE = {"g", "kg", "ml", "lít", "lit"}
SPOON_CUP = {"muỗng canh", "muỗng cà phê", "chén / cốc", "chén / bát"}
COUNT = {
    "củ", "quả", "trái", "cái", "con", "lát", "miếng", "cây", "nhánh", "tép",
    "bó", "cọng", "nắm", "gói", "hộp", "lon", "khúc", "tô", "viên", "ổ",
    "chiếc", "xấp", "lọ", "bìa", "vắt",
}
VAGUE = {"phần ăn", "vừa đủ / chút ít"}


def _num(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return None


def classify(row: dict) -> str:
    method = (row.get("match_method") or "").strip().upper()
    if method == "UNMATCHED":
        return "unmatched_no_nutrition"
    unit_vi = (row.get("unit_vi") or "").strip()
    qty = _num(row.get("required_quantity"))
    weight = _num(row.get("estimated_weight_g"))
    has_qty = qty is not None and qty > 0
    if unit_vi in MEASURE and has_qty:
        return "measured_mass_volume"
    if unit_vi in SPOON_CUP and has_qty:
        return "unit_conversion_std"
    if unit_vi in COUNT and has_qty:
        return "count_portion_estimate"
    if unit_vi in VAGUE:
        return "vague_portion_fallback"
    if weight == 10.0:
        return "vague_portion_fallback"
    return "role_category_estimate"


def process_pair(csv_path, json_path) -> Counter:
    """(Re)compute weight_source deterministically for one csv/json pair."""
    with open(csv_path, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        fieldnames = list(reader.fieldnames)
        rows = list(reader)

    for r in rows:
        r["weight_source"] = classify(r)

    if "weight_source" not in fieldnames:
        fieldnames.append("weight_source")

    with open(csv_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    with open(json_path, "r", encoding="utf-8") as f:
        json_rows = json.load(f)
    by_id = {r["id"]: r["weight_source"] for r in rows}
    for jr in json_rows:
        jr["weight_source"] = by_id.get(jr.get("id"))
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(json_rows, f, ensure_ascii=False, indent=2)

    return Counter(r["weight_source"] for r in rows)


def main() -> None:
    canon_dist = None
    for csv_path, json_path in ING_FILE_PAIRS:
        dist = process_pair(csv_path, json_path)
        total = sum(dist.values())
        print(f"weight_source recomputed for {csv_path.name} ({total:,} rows):")
        for k, v in dist.most_common():
            print(f"  {k:26} {v:7,} ({v/total*100:5.1f}%)")
        if csv_path == CANON_ING_CSV:
            canon_dist = dist

    # Report is anchored on the canonical (analysis) ingredient file.
    dist = canon_dist if canon_dist is not None else dist
    total = sum(dist.values())
    high = dist["measured_mass_volume"] + dist["unit_conversion_std"]
    low = dist["vague_portion_fallback"] + dist["role_category_estimate"]
    report = {
        "source_file": str(CANON_ING_CSV.relative_to(ROOT)),
        "total_ingredient_rows": total,
        "distribution": dict(dist.most_common()),
        "distribution_pct": {k: round(v / total * 100, 2) for k, v in dist.most_common()},
        "high_confidence_rows": high,
        "high_confidence_pct": round(high / total * 100, 2),
        "low_confidence_rows": low,
        "low_confidence_pct": round(low / total * 100, 2),
        "conversion_factors_g": {
            "muỗng canh": 15.0, "muỗng cà phê": 5.0, "chén / cốc": 200.0,
            "kg": 1000.0, "g": 1.0, "ml": 1.0, "lít": 1000.0,
        },
    }
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    with open(REPORT, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    print(f"Report -> {REPORT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
