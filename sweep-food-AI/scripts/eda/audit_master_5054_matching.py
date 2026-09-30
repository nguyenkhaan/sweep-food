"""Read-only diagnosis for every processed row currently linked to master
code 5054 ("Vú sữa" / starapple, a ripe fruit).

Root cause (fixed at the source in nlp/entity_matcher.py and
data/processed/viendinhduong/ingredient_alias_map.json, not here):

1. An unsafe bare alias, "sữa": "5054", let the single ambiguous word "sữa"
   (milk) resolve straight to the Vú sữa fruit identity.
2. VietnameseIngredientMatcher.match()/match_batch() looked up preset aliases
   with `alias_dict.get(query_norm) or alias_dict.get(cleaned_q)`. Python
   treats catalog index 0 as falsy, and code 10001 ("Sữa tươi không đường",
   the correct identity for fresh milk) sits at index 0. So a query whose
   exact form correctly resolved to 10001 fell through to the cleaned-name
   lookup instead. clean_culinary_query() separately strips the bare word
   "tươi" as freshness noise, so "sữa tươi" cleaned down to "sữa" -- which hit
   the unsafe bare alias above and landed on 5054.

This script only classifies what is still sitting in processed data from
before those two fixes landed. It never imports the model pipeline or
executes historical matching code.

    A - Definitely wrong: cleaned name is a dairy/milk term ("sữa", "sữa
        tươi", ...) that does not literally name the Vú sữa fruit. Safe to
        clear to UNMATCHED; not remapped, since the correct milk code should
        come from the already-fixed alias/matcher stage on the next raw
        reprocessing pass, not be invented here.
    B - Ambiguous: neither clearly dairy nor clearly the fruit. Left
        untouched; ambiguous evidence must not be force-resolved either way.
    D - Legitimate: cleaned name or raw text literally names the Vú sữa
        fruit. Preserved untouched.

(There is no C bucket here -- unlike the Qwen audit, this script only ever
looks at rows already pinned to one single code, so "likely valid" and
"legitimate" collapse into the same D bucket.)
"""

import argparse
import csv
import json
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ING = ROOT / "data/processed/recipes/recipe_ingredients.csv"
OUT = ROOT / "reports/eda/master_5054"

TARGET_CODE = "5054"

CLASSES = {
    "A": "Definitely wrong: dairy/milk term incorrectly linked to the Vú sữa fruit.",
    "B": "Ambiguous: neither clearly dairy nor clearly the fruit; left untouched.",
    "D": "Legitimate: raw/cleaned text literally names Vú sữa; preserved.",
}


def norm(value):
    return " ".join(unicodedata.normalize("NFC", str(value or "")).lower().split())


def is_fruit_reference(text):
    return "vú sữa" in norm(text) or "vu sua" in norm(text)


def is_dairy_term(cleaned):
    """Conservative, reviewed dairy vocabulary -- not a fuzzy heuristic. Only
    terms that are the literal drivers of the historical bug/alias are
    classified A; anything else stays B (ambiguous)."""
    return norm(cleaned) in {"sữa", "sữa tươi"}


def classify(row):
    cleaned = row.get("cleaned_name", "")
    raw = row.get("raw_text", "")
    if is_fruit_reference(cleaned) or is_fruit_reference(raw):
        return "D", "Raw or cleaned text literally names Vú sữa (the fruit); legitimate link."
    if is_dairy_term(cleaned):
        return "A", "Cleaned name is a bare dairy/milk term; historically caused by the bare 'sữa' alias and/or the index-0 alias-lookup fallthrough bug, not a genuine Vú sữa reference."
    return "B", "Neither a reviewed dairy term nor a literal Vú sữa reference; ambiguous, left untouched."


def read_csv(path):
    with path.open(encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


def audit():
    rows = read_csv(ING)
    linked = [r for r in rows if (r.get("master_ingredient_code") or "").strip() == TARGET_CODE]
    review = []
    for r in linked:
        bucket, reason = classify(r)
        review.append({
            "id": r["id"], "recipe_id": r["recipe_id"], "raw_text": r["raw_text"],
            "cleaned_name": r["cleaned_name"], "master_ingredient_code": r["master_ingredient_code"],
            "master_ingredient_name": r["master_ingredient_name"], "match_confidence": r["match_confidence"],
            "match_method": r["match_method"], "class": bucket, "reason": reason,
        })
    review.sort(key=lambda r: r["id"])
    class_counts = {c: sum(r["class"] == c for r in review) for c in CLASSES}
    class_recipes = {c: len({r["recipe_id"] for r in review if r["class"] == c}) for c in CLASSES}
    return {
        "scope": "Current processed baseline only; recomputed against whatever is on disk now.",
        "target_code": TARGET_CODE,
        "classes": CLASSES,
        "summary": {
            "total_rows": len(rows),
            "linked_rows": len(linked),
            "linked_recipes": len({r["recipe_id"] for r in linked}),
            "class_counts": class_counts,
            "class_recipes": class_recipes,
        },
        "rows": review,
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write-report", action="store_true")
    args = parser.parse_args(argv)
    result = audit()
    if args.write_report:
        OUT.mkdir(parents=True, exist_ok=True)
        (OUT / "current_audit.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result["summary"], ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
