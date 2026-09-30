"""Read-only eligibility measurement; optionally write evidence under reports/."""

import argparse
import csv
import hashlib
import json
from collections import Counter
from pathlib import Path

from nlp.qwen_matching import (
    build_mapper_rules, eligible_for_qwen_recovery, map_clean_to_master,
    qwen_candidate_eligibility,
)

ROOT = Path(__file__).resolve().parents[2]
BATCH1_RAW = {
    "1 chén lá cải thảo", "1 ít hành lá chẻ", "1 ít hành lá chẻ (trang trí)",
    "10 g Hành lá cắt nhuyễn", "2 muỗng canh hành lá thái nhỏ",
    "2-3 lá cải thảo", "3 lá cải thảo", "Hành lá: 1 nhánh nhỏ",
}
# Explicitly enumerated evidence, NOT production classification or a claim to
# reproduce the prior 47-item audit (that labeled artifact is not in this repo).
KNOWN_COMPOUND_RAW = {
    "Dầu mè, ngò rí", "Dầu ăn, dầu điều", "Tỏi băm, ngò rí",
    "Tỏi băm nhỏ, hành lá thái nhỏ", "Hành lá và tỏi băm 1 ít",
    "Hành lá, ngò gai", "1 củ hành tím, 2 cọng hành lá",
    "Ngò rí, cọng ngò gai", "Hành lá, ớt sừng",
}

SAME_IDENTITY_PROBES = [
    "hành lá/hành hoa", "hành lá + hành hoa", "hành lá - hành hoa",
    "hành lá; hành hoa", "hành lá và hành hoa", "hành lá hoặc hành hoa",
    "hành lá hay hành hoa", "nấm bào ngư/nấm sò", "hành lá/hành lá.",
    "hành lá/hành lá",
]


def load_inputs():
    paths = [ROOT / "data/interim/qwen_extracted_map.json",
             ROOT / "data/processed/viendinhduong/master_ingredients_nutrition.csv",
             ROOT / "data/processed/recipes/recipe_ingredients.csv"]
    cache = json.loads(paths[0].read_text(encoding="utf-8"))
    with paths[1].open(encoding="utf-8-sig", newline="") as stream:
        master = {row["code"]: row for row in csv.DictReader(stream)}
    with paths[2].open(encoding="utf-8-sig", newline="") as stream:
        rows = list(csv.DictReader(stream))
    return paths, cache, master, rows


def build_report():
    paths, cache, master, rows = load_inputs()
    active, _ = build_mapper_rules(master)
    rejected_cache, candidates = [], {}
    for raw, output in sorted(cache.items()):
        code, name = map_clean_to_master(output, active)
        if code is None:
            continue
        allowed, reason = qwen_candidate_eligibility(raw, output, code)
        evidence = dict(raw_text=raw, qwen_cleaned_name=output,
                        winning_code=code, winning_name=name, reason=reason)
        candidates[raw] = (allowed, evidence)
        if not allowed:
            rejected_cache.append(evidence)
    eligible_rows, rejected_rows = [], []
    for row in rows:
        raw = row.get("raw_text", "").strip()
        if eligible_for_qwen_recovery(row) and raw in candidates:
            allowed, evidence = candidates[raw]
            eligible_rows.append(raw)
            if not allowed:
                rejected_rows.append(dict(evidence, row_id=row.get("id"),
                                          recipe_id=row.get("recipe_id")))
    known_misses = [dict(candidates[raw][1],
                        unlinked_rows=eligible_rows.count(raw))
                   for raw in sorted(KNOWN_COMPOUND_RAW)
                   if raw in candidates and candidates[raw][0]]
    return {
        "scope": "Conservative first guard, not complete compound detection. "
                 "Eligibility = no master link + cached output + active mapper candidate; "
                 "not a replay of STANDARDIZED_CURE precedence or data remediation.",
        "structural_identity_comparison": {
            "normalization": "NFC, casefold, NFC, collapsed/trimmed whitespace; strip only "
                             "terminal spaces and .,!?:;…; preserve internal punctuation.",
            "reviewed_equivalences": [
                {"fragments": ["hành lá", "hành hoa"], "code": "4038",
                 "name": "Hành lá (hành hoa)"},
                {"fragments": ["nấm bào ngư", "nấm sò"], "code": "20004",
                 "name": "Nấm bào ngư (nấm sò)"},
            ],
            "rule": "Every fragment must have one identical normalized literal identity or "
                    "one explicitly reviewed identity. No mapper, alias or fuzzy inference. "
                    "Bypass only the structural rejection; downstream guards still apply.",
        },
        "same_identity_probes": [
            dict(output=output, eligible_before_hardening=output == "hành lá/hành lá",
                 eligible_after_hardening=qwen_candidate_eligibility("raw", output)[0])
            for output in SAME_IDENTITY_PROBES
        ],
        "input_sha256": {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
                         for p in paths},
        "processed_eligible_before": len(eligible_rows),
        "processed_eligible_after": len(eligible_rows) - len(rejected_rows),
        "newly_rejected_rows": rejected_rows,
        "batch1_eligible_before": sum(raw in BATCH1_RAW for raw in eligible_rows),
        "batch1_false_positives": sum(r["raw_text"] in BATCH1_RAW for r in rejected_rows),
        "cache_candidates_before": len(candidates),
        "cache_candidates_after": len(candidates) - len(rejected_cache),
        "cache_rejections_by_reason": dict(Counter(r["reason"] for r in rejected_cache)),
        "cache_rejections": rejected_cache,
        "known_compound_misses": known_misses,
        "known_miss_scope": "Enumerated regression examples only, not exhaustive. "
                            "Separator-free outputs and unreviewed raw-list shapes remain unsupported.",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write-report", action="store_true")
    args = parser.parse_args()
    before = {str(p): hashlib.sha256(p.read_bytes()).hexdigest()
              for p in (ROOT / "data").rglob("*") if p.is_file()}
    report = build_report()
    assert report == build_report(), "Non-deterministic audit"
    after = {str(p): hashlib.sha256(p.read_bytes()).hexdigest()
             for p in (ROOT / "data").rglob("*") if p.is_file()}
    assert before == after, "Data changed during read-only audit"
    report["all_data_hashes_unchanged"] = True
    if args.write_report:
        target = ROOT / "reports/eda/qwen_matching/eligibility_guard.json"
        target.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: v for k, v in report.items()
                      if k not in {"cache_rejections", "input_sha256"}}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
