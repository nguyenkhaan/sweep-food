"""Regression tests for nlp/qwen_matching.py -- the Qwen false-positive fix.

Root causes covered (reports/eda/qwen_matching/root_causes.md):
  A1 hard-coded candidate codes must be validated against the live catalog
  A2 substring-first shadowing must not recur (ngo/ngo gai, quat/viet quat,
     cai xanh/bong cai xanh)
  A3 a populated master link must not be overwritten by stale UNMATCHED status
  A4 a dangling/invalid candidate code must never be written to a row
  A5 a weight-only change must not stamp match_confidence

No GPU/model is loaded; only the pure matching/staging functions are tested.
"""

import pytest

from nlp.qwen_matching import (
    build_mapper_rules,
    eligible_for_qwen_recovery,
    map_clean_to_master,
    resolve_qwen_row,
)

CATALOG = {
    "4019": {"code": "4019", "name_vi": "Chuối xanh", "energy_kcal": "90", "protein_g": "1.0", "fat_g": "0.2", "carbs_g": "22"},
    # Deliberately drifted: the live catalog's 4038 is "Hành lá (hành hoa)", which
    # is what the repaired rule hard-codes. Here it names a different food, so the
    # A1 identity guard must disable that rule against THIS catalog.
    "4038": {"code": "4038", "name_vi": "Chuối xanh", "energy_kcal": "90", "protein_g": "1.0", "fat_g": "0.2", "carbs_g": "22"},
    # DISPLAY_NAME_BATCH_A: coriander leaf is 4081 "Rau mùi"; 4073 is red amaranth.
    "4081": {"code": "4081", "name_vi": "Rau mùi", "energy_kcal": "22", "protein_g": "2.6", "fat_g": "0.33", "carbs_g": "2.17"},
    "4073": {"code": "4073", "name_vi": "Rau giền đỏ", "energy_kcal": "47", "protein_g": "3.3", "fat_g": "0.31", "carbs_g": "7.79"},
    "4076": {"code": "4076", "name_vi": "Mùi tàu", "energy_kcal": "26", "protein_g": "2.0", "fat_g": "0.3", "carbs_g": "4.0"},
    "4015": {"code": "4015", "name_vi": "Cải bẹ xanh", "energy_kcal": "16", "protein_g": "1.6", "fat_g": "0.2", "carbs_g": "2.1"},
    "5003": {"code": "5003", "name_vi": "Quất (tắc)", "energy_kcal": "36", "protein_g": "0.8", "fat_g": "0.3", "carbs_g": "8.0"},
    "4007": {"code": "4007", "name_vi": "Cà rốt", "energy_kcal": "41", "protein_g": "0.9", "fat_g": "0.2", "carbs_g": "9.6"},
}


# ---------------------------------------------------------------------------
# A1: hard-coded candidates validated against the live catalog
# ---------------------------------------------------------------------------

def test_build_mapper_rules_disables_stale_code_name_pair():
    # The "hành lá" rule hard-codes 4038 / "Hành lá (hành hoa)" but this
    # catalog's 4038 is "Chuối xanh" -- the rule must be disabled, not applied
    # blindly. Existence of the code alone is not identity validation.
    active, disabled = build_mapper_rules(CATALOG)
    active_codes = {code for _, code, _ in active}
    assert "4038" not in active_codes
    disabled_codes = {code for _, code, _, _ in disabled}
    assert "4038" in disabled_codes


def test_build_mapper_rules_disables_dangling_code():
    # "5074" (xoài) does not exist in this catalog fixture.
    active, disabled = build_mapper_rules(CATALOG)
    active_codes = {code for _, code, _ in active}
    assert "5074" not in active_codes


def test_map_clean_to_master_rejects_hardcoded_code_name_mismatch():
    active, _ = build_mapper_rules(CATALOG)
    # "hành lá" would have hit the disabled 4038 rule; it must now be unresolved.
    assert map_clean_to_master("hành lá", active) == (None, None)


def test_map_clean_to_master_rejects_dangling_master_code():
    active, _ = build_mapper_rules(CATALOG)
    assert map_clean_to_master("xoài", active) == (None, None)


def test_valid_exact_match_is_unaffected_by_validation():
    active, _ = build_mapper_rules(CATALOG)
    assert map_clean_to_master("cà rốt", active) == ("4007", "Cà rốt")


# ---------------------------------------------------------------------------
# A2: substring-first shadowing does not recur
# ---------------------------------------------------------------------------

def test_ngo_gai_is_not_shadowed_by_generic_ngo_rule():
    active, _ = build_mapper_rules(CATALOG)
    assert map_clean_to_master("ngò gai", active) == ("4076", "Mùi tàu")
    assert map_clean_to_master("rau ngò gai", active) == ("4076", "Mùi tàu")


def test_generic_ngo_still_resolves_when_not_ngo_gai():
    active, _ = build_mapper_rules(CATALOG)
    assert map_clean_to_master("ngò rí", active) == ("4081", "Rau mùi")
    assert map_clean_to_master("rau mùi", active) == ("4081", "Rau mùi")


def test_viet_quat_is_excluded_from_quat_rule():
    active, _ = build_mapper_rules(CATALOG)
    assert map_clean_to_master("việt quất", active) == (None, None)
    assert map_clean_to_master("quả việt quất tươi (blueberry)", active) == (None, None)


def test_tac_and_quat_still_resolve_normally():
    active, _ = build_mapper_rules(CATALOG)
    assert map_clean_to_master("tắc", active) == ("5003", "Quất (tắc)")
    assert map_clean_to_master("quất", active) == ("5003", "Quất (tắc)")


def test_bong_cai_xanh_is_excluded_from_cai_xanh_rule():
    active, _ = build_mapper_rules(CATALOG)
    assert map_clean_to_master("bông cải xanh", active) == (None, None)


def test_cai_xanh_still_resolves_normally():
    active, _ = build_mapper_rules(CATALOG)
    assert map_clean_to_master("cải xanh", active) == ("4015", "Cải bẹ xanh")


# ---------------------------------------------------------------------------
# A3: populated links are protected from stale-UNMATCHED overwrite
# ---------------------------------------------------------------------------

def test_populated_code_with_stale_unmatched_status_is_not_recoverable():
    row = {"master_ingredient_code": "4007", "master_ingredient_name": "Cà rốt", "match_method": "UNMATCHED"}
    assert eligible_for_qwen_recovery(row) is False


def test_name_only_link_is_also_protected():
    row = {"master_ingredient_code": None, "master_ingredient_name": "Cà rốt", "match_method": "UNMATCHED"}
    assert eligible_for_qwen_recovery(row) is False


def test_genuinely_unmatched_row_is_recoverable():
    row = {"master_ingredient_code": None, "master_ingredient_name": None, "match_method": "UNMATCHED"}
    assert eligible_for_qwen_recovery(row) is True


# ---------------------------------------------------------------------------
# A4/A5: candidate validation and confidence-only-on-real-match, via resolve_qwen_row
# ---------------------------------------------------------------------------

def test_resolve_qwen_row_applies_validated_candidate_with_confidence():
    row = {"master_ingredient_code": None, "master_ingredient_name": None,
           "match_method": "UNMATCHED", "match_confidence": None}
    updates = resolve_qwen_row(row, CATALOG, 50.0, ("4007", "Cà rốt", "QWEN_LLM_MATCH"), cleaned_name="cà rốt")
    assert updates["master_ingredient_code"] == "4007"
    assert updates["match_confidence"] == "0.98"
    assert updates["cleaned_name"] == "cà rốt"


def test_resolve_qwen_row_rejects_dangling_candidate_without_mutating_link():
    row = {"master_ingredient_code": None, "master_ingredient_name": None,
           "match_method": "UNMATCHED", "match_confidence": None}
    updates = resolve_qwen_row(row, CATALOG, 50.0, ("99999", "Ghost ingredient", "QWEN_LLM_MATCH"))
    assert "master_ingredient_code" not in updates
    assert "match_confidence" not in updates


def test_resolve_qwen_row_rejects_cure_candidate_with_drifted_catalog_name():
    # A CURE-branch candidate is not routed through map_clean_to_master's own
    # validated rule table, so stage_qwen_update's identity check is the only
    # gate protecting it from the same catalog-drift problem (A1).
    row = {"master_ingredient_code": "4019", "master_ingredient_name": "Chuối xanh",
           "match_method": "EXACT_CATALOG_MATCH", "match_confidence": "1.00"}
    # Stale hard-coded cure identity: code 4019 now means "Chuối xanh", not "Hành hoa, tươi".
    updates = resolve_qwen_row(row, CATALOG, 20.0, ("4019", "Hành hoa, tươi", "STANDARDIZED_CURE"))
    assert "master_ingredient_code" not in updates
    assert "match_confidence" not in updates


def test_resolve_qwen_row_weight_only_change_does_not_touch_confidence():
    row = {"master_ingredient_code": "4007", "master_ingredient_name": "Cà rốt",
           "match_method": "EXACT_CATALOG_MATCH", "match_confidence": "1.00"}
    updates = resolve_qwen_row(row, CATALOG, 75.0, None)
    assert "match_confidence" not in updates
    assert "master_ingredient_code" not in updates
    assert updates["estimated_weight_g"] == "75.0"


def test_resolve_qwen_row_weight_still_applies_when_candidate_rejected():
    # A dangling cure candidate must not block an independent, already-valid
    # weight correction on the same row.
    row = {"master_ingredient_code": "4007", "master_ingredient_name": "Cà rốt",
           "match_method": "EXACT_CATALOG_MATCH", "match_confidence": "1.00"}
    updates = resolve_qwen_row(row, CATALOG, 30.0, ("99999", "Ghost", "STANDARDIZED_CURE"))
    assert "master_ingredient_code" not in updates
    assert "match_confidence" not in updates
    assert updates["estimated_weight_g"] == "30.0"


def test_valid_qwen_match_preserved_end_to_end():
    row = {"master_ingredient_code": None, "master_ingredient_name": None,
           "match_method": "UNMATCHED", "match_confidence": None, "cleaned_name": None}
    active, _ = build_mapper_rules(CATALOG)
    code, name = map_clean_to_master("cà rốt", active)
    assert eligible_for_qwen_recovery(row) is True
    updates = resolve_qwen_row(row, CATALOG, 40.0, (code, name, "QWEN_LLM_MATCH"), cleaned_name="cà rốt")
    assert updates["master_ingredient_code"] == "4007"
    assert updates["match_method"] == "QWEN_LLM_MATCH"


# ---------------------------------------------------------------------------
# Determinism and isolation from unrelated methods
# ---------------------------------------------------------------------------

def test_matching_is_deterministic():
    active, _ = build_mapper_rules(CATALOG)
    results = {map_clean_to_master("cải xanh", active) for _ in range(20)}
    assert results == {("4015", "Cải bẹ xanh")}


def test_build_mapper_rules_is_deterministic_and_pure():
    active1, disabled1 = build_mapper_rules(CATALOG)
    active2, disabled2 = build_mapper_rules(CATALOG)
    assert active1 == active2
    assert disabled1 == disabled2


def test_unrecognized_name_stays_unresolved():
    active, _ = build_mapper_rules(CATALOG)
    assert map_clean_to_master("một nguyên liệu lạ hoàn toàn", active) == (None, None)
