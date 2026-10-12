"""Tag accompaniment ingredient rows ("ăn kèm") in recipe_ingredients.

Pipeline execution order:
    1) scripts/merge_duplicate_dishes.py
    2) scripts/tag_accompaniments.py
    3) scripts/rebuild_recipe_aggregates.py

Shared contract:
    - Sets ingredient_role = "accompaniment" on rows whose raw_text (unicodedata NFC,
      stripped, lowercased) starts with "ăn kèm".
    - Touches no other column.
    - Accompaniment rows are not core ingredients, not counted in core_ingredients_count,
      not indexed for candidate retrieval, not part of feasibility features; they still
      count toward recipe calories and vegetarian/animal checks.
    - Byte-preserving rewrite for recipe_ingredients.csv and recipe_ingredients.json.
    - Idempotent: a second run detects 0 changes and does not rewrite the report.

Report: reports/eda/accompaniment_tagging.csv (id, recipe_id, raw_text, cleaned_name, old_role, new_role)
written only when rows change.
"""

from __future__ import annotations

import csv
import io
import json
import unicodedata
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RECIPES_DIR = ROOT / "data" / "processed" / "recipes"
INGREDIENTS_CSV = RECIPES_DIR / "recipe_ingredients.csv"
INGREDIENTS_JSON = RECIPES_DIR / "recipe_ingredients.json"
REPORT_CSV = ROOT / "reports" / "eda" / "accompaniment_tagging.csv"


# --------------------------------------------------------------------------
# Byte-preserving readers/writers
# --------------------------------------------------------------------------
def read_csv_rows(path: Path) -> list[list[str]]:
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.reader(f))


def safe_write_bytes(path: Path, data: bytes) -> None:
    import time
    for attempt in range(10):
        try:
            path.write_bytes(data)
            return
        except OSError:
            if attempt == 9:
                raise
            time.sleep(0.2)


def write_csv_rows(path: Path, rows: list[list[str]], lineterminator: str) -> None:
    buf = io.StringIO(newline="")
    csv.writer(buf, lineterminator=lineterminator).writerows(rows)
    safe_write_bytes(path, buf.getvalue().encode("utf-8"))

def detect_lineterminator(path: Path) -> str:
    head = path.read_bytes()[:4096]
    return "\r\n" if b"\r\n" in head else "\n"


def dump_pandas_style_json(records: list[dict], crlf: bool) -> bytes:
    """Same bytes as pandas ``to_json(orient='records', indent=2, force_ascii=False)``."""
    text = json.dumps(records, ensure_ascii=False, indent=2, separators=(",", ":")).replace("/", "\\/")
    if crlf:
        text = text.replace("\n", "\r\n")
    return text.encode("utf-8")


def is_accompaniment(raw_text: str) -> bool:
    norm = unicodedata.normalize("NFC", raw_text or "").strip().lower()
    return norm.startswith("ăn kèm")


def main() -> None:
    ing_rows = read_csv_rows(INGREDIENTS_CSV)
    header, body = ing_rows[0], ing_rows[1:]

    id_idx = header.index("id")
    rid_idx = header.index("recipe_id")
    raw_idx = header.index("raw_text")
    clean_idx = header.index("cleaned_name")
    role_idx = header.index("ingredient_role")

    changed_report_rows: list[dict[str, str]] = []
    old_role_counts: Counter[str] = Counter()
    total_accompaniment_rows = 0
    unique_recipes: set[str] = set()

    for row in body:
        if is_accompaniment(row[raw_idx]):
            total_accompaniment_rows += 1
            unique_recipes.add(row[rid_idx])
            old_role = row[role_idx]
            if old_role != "accompaniment":
                old_role_counts[old_role] += 1
                changed_report_rows.append({
                    "id": row[id_idx],
                    "recipe_id": row[rid_idx],
                    "raw_text": row[raw_idx],
                    "cleaned_name": row[clean_idx],
                    "old_role": old_role,
                    "new_role": "accompaniment",
                })
                row[role_idx] = "accompaniment"

    print("=" * 80)
    print("ACCOMPANIMENT TAGGING SUMMARY")
    print("=" * 80)
    print(f"Total accompaniment rows:     {total_accompaniment_rows}")
    print(f"Unique recipes affected:      {len(unique_recipes)}")
    print(f"Newly tagged rows:            {len(changed_report_rows)}")
    print("Old role breakdown of newly tagged rows:")
    for role, count in old_role_counts.most_common():
        print(f"  - {role:15s}: {count}")
    print("=" * 80)

    if changed_report_rows:
        # Write CSV
        lt = detect_lineterminator(INGREDIENTS_CSV)
        write_csv_rows(INGREDIENTS_CSV, [header] + body, lt)

        # Write JSON
        ing_raw = INGREDIENTS_JSON.read_bytes()
        crlf = b"\r\n" in ing_raw[:4096]
        ing_json = json.loads(ing_raw)
        for record in ing_json:
            if is_accompaniment(record.get("raw_text", "")):
                record["ingredient_role"] = "accompaniment"
        safe_write_bytes(INGREDIENTS_JSON, dump_pandas_style_json(ing_json, crlf))

        # Write report
        REPORT_CSV.parent.mkdir(parents=True, exist_ok=True)
        buf = io.StringIO(newline="")
        fields = ["id", "recipe_id", "raw_text", "cleaned_name", "old_role", "new_role"]
        writer = csv.DictWriter(buf, fieldnames=fields, lineterminator=lt)
        writer.writeheader()
        writer.writerows(changed_report_rows)
        safe_write_bytes(REPORT_CSV, buf.getvalue().encode("utf-8"))
        print(f"Wrote report: {REPORT_CSV} ({len(changed_report_rows)} rows)")
    else:
        print("Idempotent run: no ingredient_role changes needed. Report not rewritten.")

if __name__ == "__main__":
    main()
