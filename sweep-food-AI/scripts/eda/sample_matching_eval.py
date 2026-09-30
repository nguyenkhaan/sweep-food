"""Draw a deterministic, stratified sample of ingredient->master matches for
human gold-labelling of matching precision.

Stratifies by `match_method` (proportional, with a floor so rare methods such as
QWEN_LLM_MATCH / BERT_SEMANTIC_MATCH are represented), then samples with a fixed
seed so the sheet is reproducible.

Output: reports/eda/matching_eval_sample.csv with a blank `is_correct` column
(annotator fills 1=correct match, 0=wrong, leave blank if unsure) and `notes`.
The human labels themselves are external; once filled, precision per method =
mean(is_correct) over labelled rows.
"""

from __future__ import annotations

import csv
import random
import sys
from collections import defaultdict
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parent.parent.parent
ING_CSV = ROOT / "data" / "processed" / "recipes" / "recipe_ingredients.csv"
OUT = ROOT / "reports" / "eda" / "matching_eval_sample.csv"

SEED = 2026
TARGET_TOTAL = 400
MIN_PER_METHOD = 20  # floor so rare methods are still evaluable

OUT_FIELDS = [
    "id", "recipe_id", "raw_text", "cleaned_name", "unit_vi", "required_quantity",
    "match_method", "match_confidence", "master_ingredient_code",
    "master_ingredient_name", "weight_source", "is_correct", "notes",
]


def main() -> None:
    with open(ING_CSV, "r", encoding="utf-8-sig") as f:
        rows = list(csv.DictReader(f))

    # Only matched rows are meaningful for match-precision evaluation.
    matched = [r for r in rows if (r.get("master_ingredient_code") or "").strip()]

    by_method: dict[str, list] = defaultdict(list)
    for r in matched:
        by_method[(r.get("match_method") or "").strip().upper()].append(r)

    rng = random.Random(SEED)
    total_matched = len(matched)
    sample = []
    for method, group in sorted(by_method.items()):
        proportional = round(TARGET_TOTAL * len(group) / total_matched)
        take = min(len(group), max(MIN_PER_METHOD, proportional))
        sample.extend(rng.sample(group, take))

    rng.shuffle(sample)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=OUT_FIELDS)
        writer.writeheader()
        for r in sample:
            writer.writerow({
                "id": r["id"], "recipe_id": r["recipe_id"],
                "raw_text": r.get("raw_text", ""), "cleaned_name": r.get("cleaned_name", ""),
                "unit_vi": r.get("unit_vi", ""), "required_quantity": r.get("required_quantity", ""),
                "match_method": r.get("match_method", ""),
                "match_confidence": r.get("match_confidence", ""),
                "master_ingredient_code": r.get("master_ingredient_code", ""),
                "master_ingredient_name": r.get("master_ingredient_name", ""),
                "weight_source": r.get("weight_source", ""),
                "is_correct": "", "notes": "",
            })

    counts = defaultdict(int)
    for r in sample:
        counts[(r.get("match_method") or "").strip().upper()] += 1
    print(f"Wrote {len(sample)} rows to {OUT.relative_to(ROOT)} (seed={SEED}).")
    for m, c in sorted(counts.items(), key=lambda kv: -kv[1]):
        print(f"  {m:24} {c:4d}")
    print("Annotators: fill is_correct (1/0); precision/method = mean over labelled rows.")


if __name__ == "__main__":
    main()
