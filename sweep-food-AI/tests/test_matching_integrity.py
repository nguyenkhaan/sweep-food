"""Contract tests for nlp/matching_integrity.py: link integrity helpers only.

No ranking, replacement or confidence policy is exercised here -- see
tests/test_qwen_matching.py for the Qwen-specific root-cause regressions.
"""

import pytest

from nlp.matching_integrity import (
    MATCH_FIELDS,
    catalog_match_fields,
    has_master_link,
    missing_link_value,
    stage_qwen_update,
    validate_catalog_codes,
)

CATALOG = {
    "4007": {"code": "4007", "name_vi": "Cà rốt", "energy_kcal": "41", "protein_g": "0.9", "fat_g": "0.2", "carbs_g": "9.6"},
    "10001": {"code": "10001", "name_vi": "Sữa tươi không đường", "energy_kcal": "74", "protein_g": "3.9", "fat_g": "4.4", "carbs_g": "4.8"},
}


@pytest.mark.parametrize("value", [None, "", "  ", "None", "none", "NULL", "nan", "NaN"])
def test_missing_link_value_true(value):
    assert missing_link_value(value) is True


@pytest.mark.parametrize("value", ["4007", "0", 0, "Cà rốt"])
def test_missing_link_value_false(value):
    assert missing_link_value(value) is False


def test_has_master_link_requires_code_or_name():
    assert has_master_link({"master_ingredient_code": "4007", "master_ingredient_name": None}) is True
    assert has_master_link({"master_ingredient_code": None, "master_ingredient_name": "Cà rốt"}) is True
    assert has_master_link({"master_ingredient_code": None, "master_ingredient_name": None}) is False
    assert has_master_link({"master_ingredient_code": "", "master_ingredient_name": "None"}) is False


def test_catalog_match_fields_accepts_existing_code():
    fields = catalog_match_fields("4007", "Cà rốt", "QWEN_LLM_MATCH", "0.98", CATALOG)
    assert fields == {
        "master_ingredient_code": "4007",
        "master_ingredient_name": "Cà rốt",
        "match_method": "QWEN_LLM_MATCH",
        "match_confidence": "0.98",
    }


def test_catalog_match_fields_rejects_dangling_code():
    assert catalog_match_fields("99999", "Ghost", "QWEN_LLM_MATCH", "0.98", CATALOG) is None
    assert catalog_match_fields(None, "Ghost", "QWEN_LLM_MATCH", "0.98", CATALOG) is None
    assert catalog_match_fields("", "Ghost", "QWEN_LLM_MATCH", "0.98", CATALOG) is None


def test_validate_catalog_codes_passes_for_known_codes():
    validate_catalog_codes({"cà rốt": {"code": "4007"}}, CATALOG)  # no raise


def test_validate_catalog_codes_raises_for_unknown_code():
    with pytest.raises(ValueError):
        validate_catalog_codes({"ghost": {"code": "99999"}}, CATALOG)


def test_stage_qwen_update_weight_only_preserves_existing_link():
    row = {"master_ingredient_code": "4007", "master_ingredient_name": "Cà rốt",
           "match_method": "EXACT_CATALOG_MATCH", "match_confidence": "1.00"}
    updates = stage_qwen_update(row, CATALOG, 150.0, match_fields=None)
    assert set(updates) & set(MATCH_FIELDS) == set()
    assert updates["estimated_weight_g"] == "150.0"
    assert updates["calories"] == "61.5"


def test_stage_qwen_update_applies_complete_validated_match():
    row = {"master_ingredient_code": None, "master_ingredient_name": None,
           "match_method": "UNMATCHED", "match_confidence": None}
    match_fields = dict(zip(MATCH_FIELDS, ("10001", "Sữa tươi không đường", "QWEN_LLM_MATCH", "0.98")))
    updates = stage_qwen_update(row, CATALOG, 200.0, match_fields=match_fields, cleaned_name="sữa tươi")
    assert updates["master_ingredient_code"] == "10001"
    assert updates["cleaned_name"] == "sữa tươi"
    assert updates["calories"] == "148.0"


def test_stage_qwen_update_rejects_dangling_match_code():
    row = {"master_ingredient_code": None, "master_ingredient_name": None}
    match_fields = dict(zip(MATCH_FIELDS, ("99999", "Ghost", "QWEN_LLM_MATCH", "0.98")))
    with pytest.raises(ValueError):
        stage_qwen_update(row, CATALOG, 100.0, match_fields=match_fields)


def test_stage_qwen_update_rejects_existing_code_with_drifted_name():
    """Existence alone is not identity validation: code 4007 exists, but the
    candidate's name no longer matches what that code currently identifies."""
    row = {"master_ingredient_code": None, "master_ingredient_name": None}
    match_fields = dict(zip(MATCH_FIELDS, ("4007", "Bắp cải", "STANDARDIZED_CURE", "0.98")))
    with pytest.raises(ValueError):
        stage_qwen_update(row, CATALOG, 100.0, match_fields=match_fields)


def test_stage_qwen_update_rejects_incomplete_match_fields():
    row = {"master_ingredient_code": None, "master_ingredient_name": None}
    with pytest.raises(ValueError):
        stage_qwen_update(row, CATALOG, 100.0, match_fields={"master_ingredient_code": "4007"})
