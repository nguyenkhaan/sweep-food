"""Narrow recovery eligibility and execution of the real pipeline B block."""

import ast
from collections import Counter, defaultdict
import logging
import unicodedata

import pytest

from nlp.qwen_matching import (
    build_mapper_rules, eligible_for_qwen_recovery, map_clean_to_master,
    qwen_candidate_eligibility, resolve_cleaned_name_update, resolve_qwen_row,
)
from scripts.eda.audit_qwen_eligibility_guard import ROOT, BATCH1_RAW, load_inputs, build_report


@pytest.mark.parametrize("separator", ["/", " + ", " - ", "; ", " và ", " hoặc ", " hay "])
@pytest.mark.parametrize("left,right,code", [
    ("hành lá", "hành hoa", "4038"),
    ("nấm bào ngư", "nấm sò", "20004"),
    ("hành lá", "hành lá", "4038"),
    ("hành lá", "hành lá.", "4038"),
])
def test_single_identity_fragments(separator, left, right, code, inputs, recovery_block):
    _, master, _, active = inputs
    output = left + separator + right
    assert qwen_candidate_eligibility("raw", output) == (True, None)
    assert qwen_candidate_eligibility("raw", right + separator + left) == (True, None)
    patch, env = run_recovery(recovery_block, dict(raw_text=output, match_method="UNMATCHED"),
                              output, master, active)
    assert patch["master_ingredient_code"] == code
    assert not env["rejected_eligibility_reasons"]


@pytest.mark.parametrize("output", [
    "hành lá/ngò rí", "hành lá/hành tím", "nấm bào ngư/nấm rơm", "hành lá hoặc ngò rí",
    "hành lá/hành hoa/ngò rí", "hành lá/ngò rí/hành hoa", "ngò rí/hành lá/hành hoa",
    "nấm bào ngư/nấm sò/nấm rơm", "hành lá/hành hoa/nấm sò",
    "hành lá/hành hoa tươi", "hành lá non/hành lá",  # substring target is insufficient
    "húng lủi/húng quế", "nấm mỡ/nấm nâu",  # same mapper target, unreviewed identities
    "hành-lá/hành lá", "hành.lá/hành lá", "hành,lá/hành lá",
    "hành:lá/hành lá", "hành (lá)/hành lá",
])
def test_mixed_or_unreviewed_fragments_rejected(output):
    assert qwen_candidate_eligibility("raw", output, "4038") == (
        False, "qwen_explicit_ingredient_list")


def test_fragment_normalization_and_all_fragment_equivalence():
    output = unicodedata.normalize("NFD", "  HÀNH  LÁ. / hành HOA! / hành lá…  ")
    assert qwen_candidate_eligibility("raw", output) == (True, None)
    assert qwen_candidate_eligibility("raw", "nấm sò/nấm bào ngư/nấm sò.") == (True, None)
    assert qwen_candidate_eligibility("raw", "rau lạ/rau lạ.") == (True, None)
    # Structural bypass must still run the two downstream guards.
    assert qwen_candidate_eligibility("Hành lá và ngò rí", "hành lá/hành hoa") == (
        False, "qwen_collapsed_reviewed_raw_list")
    assert qwen_candidate_eligibility("ngò gai", "ngò/ngò.", "4081") == (
        False, "generic_ngo_conflicts_with_raw_ngo_gai")


@pytest.fixture(scope="module")
def inputs():
    _, cache, master, rows = load_inputs()
    active, _ = build_mapper_rules(master)
    return cache, master, rows, active


@pytest.fixture(scope="module")
def recovery_block():
    tree = ast.parse((ROOT / "scripts/run_qwen_line_pipeline.py").read_text(encoding="utf-8"))
    block = next(node for node in ast.walk(tree) if isinstance(node, ast.If)
                 and ast.unparse(node.test) == 'eligible_for_qwen_recovery(r) and raw_t in llm_extracted_map')
    return compile(ast.fix_missing_locations(ast.Module(body=[block], type_ignores=[])),
                   "<actual pipeline recovery block>", "exec")


def run_recovery(block, row, output, master, active):
    original = dict(row)
    raw = row["raw_text"].strip()
    env = dict(r=row, raw_t=raw, llm_extracted_map={raw: output},
               eligible_for_qwen_recovery=eligible_for_qwen_recovery,
               map_clean_to_master=lambda name: map_clean_to_master(name, active),
               qwen_candidate_eligibility=qwen_candidate_eligibility,
               resolve_cleaned_name_update=resolve_cleaned_name_update,
               candidate=None, cleaned_name_update=None, preserved_cleaned_name_count=0,
               rejected_eligibility_reasons=defaultdict(int), logger=logging.getLogger(__name__))
    exec(block, env)
    patch = resolve_qwen_row(row, master, 25.0, env["candidate"], env["cleaned_name_update"])
    assert row == original
    return patch, env


@pytest.mark.parametrize("separator", ["/", " + ", " - ", ";", " và ", " hoặc ", " hay "])
def test_explicit_outputs_rejected(separator, inputs, recovery_block):
    _, master, _, active = inputs
    output = "hành lá" + separator + "ngò rí"
    assert qwen_candidate_eligibility("raw", output) == (False, "qwen_explicit_ingredient_list")
    row = dict(raw_text=output, match_method="UNMATCHED", cleaned_name="original")
    patch, env = run_recovery(recovery_block, row, output, master, active)
    assert env["candidate"] is None
    assert env["rejected_eligibility_reasons"] == {"qwen_explicit_ingredient_list": 1}
    assert not {"master_ingredient_code", "master_ingredient_name", "match_method",
                "match_confidence", "cleaned_name"}.intersection(patch)
    assert {**row, **patch}["match_method"] == "UNMATCHED"


@pytest.mark.parametrize("raw,output", [
    ("Hành lá và ngò rí", "hành lá"),
    ("Hành lá và ngò rí 1 ít", "ngò rí"),
    ("Hành lá và ngò rí 20 gr", "hành lá"),
    ("Hành lá, hành tím", "hành lá"),
    ("Ngò rí, hành lá", "hành lá"),
    ("Tỏi băm, ngò rí", "ngò rí"),
    ("Tỏi băm, ngò rí: 1 muỗng canh", "ngò rí"),
    ("Ngò rí, ớt sừng", "ớt sừng"),
    ("RAU NÊM: Hành lá, ngò gai", "hành lá"),
    ("Xà lách/ dưa leo/ ớt sừng/ ngò rí 1 ít", "ngò rí"),
])
def test_reviewed_raw_collapse(raw, output, inputs, recovery_block):
    assert qwen_candidate_eligibility(raw, output) == (False, "qwen_collapsed_reviewed_raw_list")
    _, master, _, active = inputs
    patch, env = run_recovery(recovery_block, dict(raw_text=raw, match_method="UNMATCHED"),
                              output, master, active)
    assert env["candidate"] is None
    assert env["rejected_eligibility_reasons"] == {"qwen_collapsed_reviewed_raw_list": 1}
    assert "master_ingredient_code" not in patch


@pytest.mark.parametrize("raw", [
    "Ngò gai cắt sợi nhuyễn 3 muỗng canh", "Gốc ngò gai 1 ít", "Rau ngò gai 1 cây",
    "Rau ngò gai 1 ít", "Rau ngò gai 4 nhánh", "Rau ngò gai 3 nhánh", "Rau ngò gai 1 nhánh",
])
def test_generic_ngo_collision(raw, inputs, recovery_block):
    cache, master, rows, active = inputs
    output = cache[raw]
    assert map_clean_to_master(output, active)[0] == "4081"
    assert qwen_candidate_eligibility(raw, output, "4081") == (
        False, "generic_ngo_conflicts_with_raw_ngo_gai")
    assert qwen_candidate_eligibility(raw, output, "4076") == (True, None)
    row = next(r for r in rows if r["raw_text"] == raw)
    patch, env = run_recovery(recovery_block, row, output, master, active)
    assert env["candidate"] is None
    assert env["rejected_eligibility_reasons"] == {"generic_ngo_conflicts_with_raw_ngo_gai": 1}
    assert {**row, **patch}["match_method"] == "UNMATCHED"
    assert "master_ingredient_code" not in patch


@pytest.mark.parametrize("output", ["cá thác lác nạo", "lá cải thảo", "hành lá chẻ",
                                      "phi lê cá thác lác", "nấm bào ngư", "nấm đùi gà"])
def test_allowed_controls_identical_patches(output, inputs, recovery_block):
    _, master, _, active = inputs
    assert qwen_candidate_eligibility(output, output) == (True, None)
    row = dict(raw_text=output, match_method="UNMATCHED")
    patch, env = run_recovery(recovery_block, row, output, master, active)
    code, name = map_clean_to_master(output, active)
    assert code is not None
    expected = resolve_qwen_row(row, master, 25.0, (code, name, "QWEN_LLM_MATCH"),
                                resolve_cleaned_name_update(output, output))
    assert patch == expected
    assert patch["master_ingredient_code"] == code
    assert patch["estimated_weight_g"] == "25.0"
    assert not env["rejected_eligibility_reasons"]


def test_eight_batch1_rows_recover_identically(inputs, recovery_block):
    cache, master, rows, active = inputs
    hits = [r for r in rows if r["raw_text"].strip() in BATCH1_RAW]
    assert len(hits) == 8
    codes = []
    for row in hits:
        raw = row["raw_text"].strip()
        assert eligible_for_qwen_recovery(row)
        code, name = map_clean_to_master(cache[raw], active)
        patch, env = run_recovery(recovery_block, row, cache[raw], master, active)
        expected = resolve_qwen_row(row, master, 25.0, (code, name, "QWEN_LLM_MATCH"),
                                    resolve_cleaned_name_update(raw, cache[raw]))
        assert patch == expected
        assert patch["master_ingredient_code"] == code
        assert not env["rejected_eligibility_reasons"]
        codes.append(code)
    assert codes.count("4038") == 5
    assert codes.count("4109") == 3


@pytest.mark.parametrize("text", [
    "hành lá, cắt nhỏ", "hành lá, dùng để trang trí", "hành lá, giống ngò rí",
    "1/2 kg hành lá", "4,5 nhánh hành lá", "2-3 lá cải thảo",
    "hành lá/hành lá", "hành lá và hành lá", "hành lá và ngò rí để trang trí",
    "hành lá cắt và rửa sạch", "hành lá 10 g/20 g", "hành lá như ngò rí",
])
def test_non_lists_abstain(text):
    assert qwen_candidate_eligibility(text, "hành lá") == (True, None)
    assert qwen_candidate_eligibility(text, text) == (True, None)


def test_unicode_and_whitespace():
    raw = unicodedata.normalize("NFD", "  HÀNH LÁ ,  HÀNH TÍM ")
    output = unicodedata.normalize("NFD", "HÀNH LÁ")
    assert qwen_candidate_eligibility(raw, output)[0] is False
    assert qwen_candidate_eligibility("NGÒ GAI", "ngò", "4081")[0] is False
    assert qwen_candidate_eligibility("ngò gai vị", "ngò", "4038") == (True, None)


def test_measured_impact_and_known_misses():
    """Batch 2 widened only the DENOMINATOR here.

    Repairing the tiêu and chả huế/chả lụa rules made 31 more eligible rows
    resolve to a mapper candidate, so processed_eligible_before moved 15 -> 46
    and _after 8 -> 39. The guard's own behaviour did not move: the same 7 rows
    are rejected, for the same single reason, and the cache-level rejection
    totals below are byte-identical. The one Batch-2 candidate the guard does
    refuse ("Tiêu hạt/ớt xanh/ ớt đỏ") was already being refused under the ớt
    rule, so only the winning_code recorded against it changed.

    DISPLAY_NAME_BATCH_A then widened the denominator by exactly one more:
    clearing "Bột và hạt rau mùi Corriander" to UNMATCHED makes it eligible, so
    _before moved 46 -> 47 while _after stayed at 39. The row is refused by the
    pre-existing qwen_explicit_ingredient_list guard, independently of the new
    matcher-level coriander seed/powder guard, so the spice cannot be recovered
    onto the coriander leaf by either route. Cache-level totals are unchanged.

    DISPLAY_NAME_BATCH_C2 widened the denominator by exactly one more, the same
    way: clearing the multi-identity line "Bắp cải tím/ ngò rí 1 ít" to UNMATCHED
    makes it eligible, so _before moved 47 -> 48 and newly_rejected_rows 8 -> 9,
    while _after stayed at 39. That row is refused by the same pre-existing
    qwen_explicit_ingredient_list guard -- it names red cabbage AND coriander --
    so the clear cannot be silently recovered onto coriander 4081. The guard's
    own behaviour did not move and the cache-level totals are unchanged.

    DISPLAY_NAME_BATCH_C1 then widened it by exactly one more, and this one the
    guard had to LEARN. Clearing "1 muỗng cải thảo muối khô" -- dried salted napa,
    which has no catalog identity -- to UNMATCHED made it eligible, so _before
    moved 48 -> 49. Unlike the two rows above, no existing guard refused it: it is
    a clean single-ingredient line, and the mapper resolved its cached output
    "cải thảo" to 4109 "Rau cải thảo" -- FRESH napa, a different preparation with a
    different nutrition profile -- so a recovery pass would have silently undone
    the reviewed clear. Measured before the fix, it reached the pipeline with
    candidate_applied = True.

    C1 hardening therefore added the reviewed catalog-gap exclusion
    _REVIEWED_NO_CATALOG_TARGET_RAW, pinned on that exact raw line, which refuses
    it in production with the reason DRIED_SALTED_NAPA_NO_EXACT_CATALOG_TARGET. So
    _after returns to 39 -- the guard fully absorbs C1's new candidate -- and
    newly_rejected_rows moves 9 -> 10. The cache-level totals move by exactly one
    for the same reason: the line is a cache entry too, so cache_candidates_after
    drops 342 -> 341 and cache_rejections rises 71 -> 72.

    Nothing else moved: every other fresh-napa, leaf-napa and kimchi line still
    resolves to 4109 and is still allowed, and the three pre-existing cache-level
    reasons fire exactly as many times as before.
    """
    report = build_report()
    assert report == build_report()
    assert report["processed_eligible_before"] == 49
    assert report["processed_eligible_after"] == 39
    assert len(report["newly_rejected_rows"]) == 10
    assert report["batch1_eligible_before"] == 8
    assert report["batch1_false_positives"] == 0
    assert report["cache_rejections_by_reason"] == {
        "qwen_explicit_ingredient_list": 18,
        "qwen_collapsed_reviewed_raw_list": 15,
        "generic_ngo_conflicts_with_raw_ngo_gai": 38,
        "DRIED_SALTED_NAPA_NO_EXACT_CATALOG_TARGET": 1,
    }
    assert len(report["cache_rejections"]) == 72
    assert Counter(r["reason"] for r in report["newly_rejected_rows"]) == {
        "generic_ngo_conflicts_with_raw_ngo_gai": 7,
        "qwen_explicit_ingredient_list": 2,
        "DRIED_SALTED_NAPA_NO_EXACT_CATALOG_TARGET": 1,
    }
    dried = [r for r in report["newly_rejected_rows"]
             if r["reason"] == "DRIED_SALTED_NAPA_NO_EXACT_CATALOG_TARGET"]
    assert len(dried) == 1
    assert dried[0]["raw_text"] == "1 muỗng cải thảo muối khô"
    assert dried[0]["row_id"].startswith("2c660d89")
    assert dried[0]["winning_code"] == "4109"
    assert all(p["eligible_after_hardening"] for p in report["same_identity_probes"])
    assert report["known_compound_misses"]
    assert all(r["unlinked_rows"] == 0 for r in report["known_compound_misses"])
