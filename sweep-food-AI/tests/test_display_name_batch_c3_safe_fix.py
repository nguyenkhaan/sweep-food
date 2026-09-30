"""Focused regression coverage for the reviewed C3 stored-data repair."""

import hashlib
import json
from pathlib import Path

from scripts.eda import apply_display_name_batch_c3_safe_fix as fix


def _report():
    return json.loads((fix.OUT / "applied_fix.json").read_text(encoding="utf-8"))


def test_c3_exact_scope_and_state():
    report = _report()
    assert report["rows_changed"] == 91
    assert report["cleaned_name_repairs"] == 78
    assert report["processed_recipes_touched"] == 86
    assert report["populations"] == fix.AFTER_POP
    assert report["corpus_nulls"] == fix.AFTER_NULLS
    assert report["alias_map_size"] == 4684
    assert report["PARSER_BAP_CAI_FIX_NEEDED"] is True
    assert report["PARSER_DURABILITY_GAP"] == 82
    assert report["validation"]["complete"] is True

    outcomes = report["row_outcomes"]
    assert len(outcomes) == 91
    assert sum(o["before"]["master_ingredient_code"] == "4013" for o in outcomes) == 68
    assert sum(o["before"]["master_ingredient_code"] == "4021" for o in outcomes) == 19
    assert sum(not o["before"]["master_ingredient_code"] for o in outcomes) == 4
    assert sum(o["before"]["cleaned_name"] != o["after"]["cleaned_name"] for o in outcomes) == 78
    assert report["matcher_replay"]["stored_count"] == 91
    assert report["matcher_replay"]["raw_count"] == {"single": 9, "batch": 9}


def test_c3_alias_boundaries_and_exclusions():
    aliases = fix.read_json(fix.ROOT / fix.ALIASES)
    assert len(aliases) == 4684
    assert aliases["cải"] == "4013"
    assert aliases["cải trắng"] == "4021"
    for key in ("cải bào", "cải bào mỏng", "cải trắng bào", "cải trắng xắt sợi",
                "bắp cải tròn", "lá bắp cải", "rau bắp cải", "bắp cải tim"):
        assert aliases[key] == "4010"
    rows = {r["id"][:8]: r for r in fix.read_csv(fix.ROOT / fix.DATA / "recipe_ingredients.csv")}
    for rid in fix.KEEP_UNMATCHED:
        assert rows[rid]["match_method"] == "UNMATCHED"
        assert not rows[rid]["master_ingredient_code"]
    assert not rows["eb72aab4"]["master_ingredient_code"]


def test_parser_files_and_interim_are_unchanged():
    review = fix.read_json(fix.REVIEW)
    for name, digest in review["protected_files"].items():
        assert hashlib.sha256((fix.ROOT / name).read_bytes()).hexdigest() == digest
    assert fix.interim_digest(fix.ROOT) == review["interim"]


def test_c3_idempotent_replay():
    result = fix.run(apply=True)
    assert result["rows_pending"] == 0
    assert result["idempotent"] is True
