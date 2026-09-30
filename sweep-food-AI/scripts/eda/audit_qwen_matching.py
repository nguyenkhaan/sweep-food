"""Read-only Qwen diagnosis for the current processed dataset.

Standard library only. Never imports the model pipeline or executes historical
code. Classifies every QWEN_LLM_MATCH row into one of four conservative,
reviewed classes:

    A - Clearly incorrect identity; safe candidate to clear, not automatically remap.
    B - Suspicious or insufficient evidence; includes compounds and preparation proxies.
    C - Likely valid identity with corroborating simple raw text; not nutrition validation.
    D - Dangling code absent from master; structural failure, intended identity unresolved.

The WRONG/VALID tables are manually reviewed semantic pairs (not fuzzy-string
heuristics): a row lands in A or C only when the query's cleaned name is one
of the specific listed synonyms for that master code *and* the raw text is
"simple" (no unrecognized residue beyond quantity/prep words). Everything else
is B -- suspicious but not confidently classified either way. This intentionally
recomputes classification against whatever data is currently on disk; it does
not assume any historical row count still holds.

REVIEWED_ROW_REMAPS is a separate, narrower exception for individually
reviewed rows whose identity was established by explicit in-text evidence
rather than a cleaned-name/code pattern -- each is keyed by row id
specifically so it can never generalize into a WRONG/VALID-style rule for
other rows sharing the same cleaned name or code.
"""

import argparse
import csv
import json
import re
import unicodedata
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ING = ROOT / "data/processed/recipes/recipe_ingredients.csv"
MASTER = ROOT / "data/processed/viendinhduong/master_ingredients_nutrition.csv"
OUT = ROOT / "reports/eda/qwen_matching"

CLASSES = {
    "A": "Clearly incorrect identity; safe candidate to clear, not automatically remap.",
    "B": "Suspicious or insufficient evidence; includes compounds and preparation proxies.",
    "C": "Likely valid identity with corroborating simple raw text; not nutrition validation.",
    "D": "Dangling code absent from master; structural failure, intended identity unresolved.",
}

# Exact reviewed identities and exact current target guards prevent generalizing
# a string difference into a false-positive label. All other names stay B.
WRONG = {
    "4019": ("Chuối xanh", "hành lá|hành hoa|hành lá chẻ|gốc hành lá", "Allium herb versus green banana"),
    "4074": ("Rau giền trắng", "húng lủi|lá húng lủi|đọt húng lủi|rau húng lủi|lá húng quế trắng", "Mint/basil versus amaranth"),
    "4081": ("Rau mùi", "hành tím|hành trắng|củ hành trắng|đầu hành|hành tím băm", "Onion versus coriander"),
    "4017": ("Cần ta", "cải xoong|cải xoong baby", "Watercress versus water celery"),
    # DISPLAY_NAME_BATCH_C1: 4016 stays in WRONG -- the code is still the wrong
    # home for the rows that remain on it -- but its signature is re-keyed. C1
    # repaired 4016's display name from the corrupt "Dưa chuột (dưa leo)" to
    # "Cải xanh" (its own name_en is "Mustard greens, raw"), moved 248 cucumber
    # rows to 4027, and cleared or rehomed every napa, kimchi, spinach and kale
    # row that had been parked here. Exactly ten reviewed rows survive on 4016:
    # five "cải con" and five of the "cải thìa" family. The synonym list is
    # narrowed to the cleaned names those rows actually carry. "cải thảo" and
    # "lá cải thảo" are dropped because those rows are gone -- including
    # 2c660d89, the one row that would have justified keeping "cải thảo", which
    # C1 cleared to UNMATCHED by reviewer decision. "cải thìa chua" is
    # deliberately absent: the existing compound/preparation logic already holds
    # it in class B, and widening this regex to reach it would relabel rows on
    # other codes that share the pattern.
    "4016": ("Cải xanh", "cải con|cải thìa|cải thìa con", "Bok-choy and sprout greens versus mustard greens"),
    "13018": ("Nước mắm cô", "tiêu|tiêu trắng|tiêu đen|tiêu sọ|bột tiêu trắng|tiêu trắng mịn|hạt tiêu đen nguyên hạt|tiêu hạt|tiêu sọ giã bễ|tiêu sọ bể|tiêu sọ hạt|hạt tiêu|tiêu hạt trắng|tiêu hạt tứ xuyên", "Pepper spice versus concentrated fish sauce"),
    "8031": ("Cá trích", "cua biển", "Crab versus herring"),
    "8046": ("Rạm", "tôm càng|tôm càng xanh", "Prawn versus crab"),
    "8006": ("Cá diếc", "cá cơm khô", "Dried anchovy versus crucian carp"),
    "7067": ("Dồi lợn", "chả huế|chả huế cây", "Pork paste sausage versus intestine/blood sausage"),
    "5003": ("Chanh", "tắc|quất|nước tắc|vỏ tắc|quả việt quất tươi (blueberry)", "Kumquat or blueberry versus lime/lemon"),
    "14008": ("Nước khoáng", "chanh|chanh vàng|chanh không hạt|nước cốt chanh|nước cốt chanh vàng|vỏ chanh|vỏ chanh vàng|lá chanh|lá húng chanh|nước cốt chanh dây|nước chanh dây có hạt|nước chanh vàng|nước chanh muối|nước cốt chanh muối", "Citrus/leaf/passionfruit versus mineral water"),
    "4031": ("Đậu Hà Lan, quả", "đậu que|đậu que nhật|đậu que dẹp", "Green bean versus pea pod"),
    "4076": ("Rau khoai lang", "mùi tàu", "Culantro versus sweet-potato leaves"),
    "4073": ("Rau mùi (ngò rí)", "ngò gai|rau ngò gai|gốc ngò gai|ngò tây", "Culantro/parsley versus coriander; generic ngò shadows specific rule"),
    "3025": ("Đậu phụ (đậu hũ)", "mì căn|mì căn ống", "Wheat gluten versus soy tofu"),
    "4015": ("Cải thìa (cải trắng)", "bông cải xanh|bông cải xanh baby", "Broccoli versus bok choy; substring cải xanh"),
}
VALID = {
    "4007": ("Cà rốt", "cà rốt|carrot"),
    "4005": ("Cà chua", "cà chua|cà chua bi|cà bi|cà bi nhỏ"),
    "4073": ("Rau mùi (ngò rí)", "ngò rí|rau ngò rí|rau mùi|rau ngò|rau mùi thơm|lá ngò rí"),
    "7017": ("Thịt nạc heo (lợn)", "nạc dăm|thịt nạc dăm|nạc dăm heo"),
    "7003": ("Thịt bò nạc", "thịt bò"),
    "8013": ("Cá thát lát", "cá thác lác|cá thác lác nạo|phi lê cá thác lác"),
    "13039": ("Ớt tươi", "ớt|ớt sừng|ớt hiểm|ớt hiểm sừng|trái ớt|ớt xoăn|ớt sừng cắt sợi|ớt băm|ớt sợi"),
    "20002": ("Nước lọc (nước dùng nấu)", "nước ấm"),
    # DISPLAY_NAME_BATCH_C2: 4010 used to sit in WRONG above, keyed on the
    # corrupt display name "Cần tây" with the reason "Cabbage family versus
    # celery". That signature described the defect, not the data: it could only
    # fire while 4010 published celery's name, and C2 repaired 4010 to "Cải bắp
    # trắng" (Cabbage, common, raw) and moved every celery row and alias off it.
    # Retired and replaced with the reviewed identity, in the narrow VALID form
    # used by every other entry here -- an exact pipe-separated list of the
    # cleaned names the surviving reviewed rows actually carry, NOT a generic
    # cabbage pattern. "bắp cải tím" and the other red-cabbage spellings are
    # deliberately absent: they are 20035, and claiming them here would relabel
    # a different ingredient as valid.
    "4010": ("Cải bắp trắng", "bắp cải|bắp cải trắng|bắp cải nhỏ|bắp cải trái tim|bắp cải trộn"),
}

# Row-specific reviewed remaps: identity confirmed for this ONE exact row by
# explicit in-text disambiguation, not by a generic cleaned-name/code
# equivalence. Deliberately keyed by row id (not code+cleaned_name, like
# WRONG/VALID above) so this can never generalize to any other row that
# happens to share the same code or cleaned name -- in particular, the other
# "bạc hà" rows still resolving to dangling code 13038, and the other "xoài"
# rows still resolving to dangling code 5074, are untouched by this and
# remain Class D regardless of this table's contents. Each entry is
# re-validated against the live catalog on every run, same as WRONG/VALID: a
# row falls through to normal classification (not silently kept C) if the
# code/name it names ever stops matching.
REVIEWED_ROW_REMAPS = {
    "dfa8f4c6-ffc5-4dc5-87de-ec2d52632bea": (
        "4026", "Dọc mùng",
        'Row-specific reviewed remap: raw_text explicitly reads "Bạc hà (Dọc '
        'mùng): 100g" -- the recipe author\'s own in-text disambiguation, not '
        "an inferred synonym -- and catalog code 4026 exists under the exact "
        "name \"Dọc mùng\". Applied 2026-09-12 via "
        "scripts/eda/apply_qwen_class_d_safe_fix.py (previously Class D, "
        "code 13038, absent from catalog).",
    ),
    "114d0cb0-d4af-4dab-a094-b95a04ea4b1b": (
        "5055", "Xoài chín",
        'Row-specific reviewed remap: raw_text explicitly reads "Xoài cát chu '
        'vừa chín tới 600g (2 quả nhỏ)" -- "vừa chín tới" ("just ripened") is '
        "the author's own explicit ripeness statement, not an inference from "
        "the varietal name or the dish -- and catalog code 5055 exists under "
        'the exact name "Xoài chín" (ripe mango), the only ripe-mango identity '
        "in the catalog. Applied 2026-09-13 via "
        "scripts/eda/apply_qwen_xoai_ripe_safe_fix.py (previously Class D, "
        "code 5074, absent from catalog).",
    ),
    "60c41843-1d7b-45bf-aa7e-0ba399cb2258": (
        "5055", "Xoài chín",
        'Row-specific reviewed remap: raw_text explicitly reads "Xoài cát ( '
        'vừa chín tới) 1 quả" -- "vừa chín tới" ("just ripened") is the '
        "author's own explicit ripeness statement, not an inference from the "
        "varietal name or the dish -- and catalog code 5055 exists under the "
        'exact name "Xoài chín" (ripe mango), the only ripe-mango identity in '
        "the catalog. Applied 2026-09-13 via "
        "scripts/eda/apply_qwen_xoai_ripe_safe_fix.py (previously Class D, "
        "code 5074, absent from catalog).",
    ),
}


def norm(value):
    return " ".join(unicodedata.normalize("NFC", str(value or "")).lower().split())


def missing(value):
    return value is None or str(value).strip().casefold() in ("", "none", "null", "nan")


def simple_raw(raw, clean):
    """Require the identity literally in raw and only known quantity/prep residue."""
    raw, clean = norm(raw), norm(clean)
    if not clean or clean not in raw:
        return False
    residue = raw.replace(clean, " ", 1)
    residue = re.sub(r"\d+(?:[.,]\d+)?", " ", residue)
    residue = re.sub(r"\b(?:muỗng|thìa)\s+(?:canh|cà phê)\b", " ", residue)
    residue = re.sub(r"\b(gram|kg|gr|g|ml|lít|muỗng|thìa|chén|bát|cốc|củ|quả|trái|cây|nhánh|bó|ít|một|vài|tươi|nhỏ|lớn|băm|nhuyễn|thái|cắt|sợi|chẻ|rửa|sạch|giã|xay|nạo|mịn|vừa|đủ|dùng|trang trí)\b", " ", residue)
    return not re.sub(r"[\d\s.,:()\-–/½¼¾]+", "", residue)


def classify(row, masters):
    code = row.get("master_ingredient_code")
    if missing(code) or code not in masters:
        return "D", "Master code is missing or absent from catalog; no invented replacement."
    target, clean = norm(masters[code]["name_vi"]), norm(row["cleaned_name"])

    reviewed = REVIEWED_ROW_REMAPS.get(row.get("id"))
    if reviewed:
        expected_code, expected_name, reason = reviewed
        if code == expected_code and target == norm(expected_name):
            return "C", reason

    for table, bucket in ((WRONG, "A"), (VALID, "C")):
        if code in table:
            expected, names, *reason = table[code]
            if target == norm(expected) and clean in names.split("|"):
                if simple_raw(row["raw_text"], clean):
                    return bucket, reason[0] if reason else "Reviewed identity/synonym; simple raw text corroborates extraction."
                return "B", "Reviewed cleaned identity but raw text has additional or unverified semantics."
    return "B", "Compound, alternative, preparation proxy or identity outside conservative reviewed pairs."


def read_csv(path):
    with path.open(encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


def audit():
    rows = read_csv(ING)
    masters = {r["code"]: r for r in read_csv(MASTER)}
    qwen = [r for r in rows if r["match_method"] == "QWEN_LLM_MATCH"]
    review = []
    for r in qwen:
        bucket, reason = classify(r, masters)
        review.append({
            "id": r["id"], "recipe_id": r["recipe_id"], "raw_text": r["raw_text"],
            "cleaned_name": r["cleaned_name"], "master_ingredient_code": r["master_ingredient_code"],
            "master_ingredient_name": r["master_ingredient_name"], "match_confidence": r["match_confidence"],
            "class": bucket, "reason": reason,
        })
    review.sort(key=lambda r: r["id"])
    class_counts = {c: sum(r["class"] == c for r in review) for c in CLASSES}
    class_recipes = {c: len({r["recipe_id"] for r in review if r["class"] == c}) for c in CLASSES}
    return {
        "scope": "Current processed baseline only; not a dataset-wide precision estimate.",
        "classes": CLASSES,
        "summary": {
            "total_rows": len(rows), "qwen_rows": len(qwen),
            "qwen_recipes": len({r["recipe_id"] for r in qwen}),
            "class_counts": class_counts, "class_recipes": class_recipes,
            "method_counts": dict(sorted(Counter(r["match_method"] for r in rows).items())),
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
