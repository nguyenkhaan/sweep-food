"""Tests for scripts/eda/audit_master_5054_matching.py's row classification.

Standard library / dict-fixture only; no dependency on the real ~64k-row
processed dataset so these stay fast and independent of data changes.
"""

from scripts.eda.audit_master_5054_matching import CLASSES, classify


def test_bare_sua_is_class_a_wrong():
    row = {"cleaned_name": "sữa", "raw_text": "50 ml sữa"}
    bucket, _ = classify(row)
    assert bucket == "A"


def test_sua_tuoi_is_class_a_wrong():
    row = {"cleaned_name": "sữa tươi", "raw_text": "Sữa tươi 300 ml"}
    bucket, _ = classify(row)
    assert bucket == "A"


def test_literal_vu_sua_is_class_d_legitimate():
    row = {"cleaned_name": "vú sữa", "raw_text": "1 quả vú sữa chín"}
    bucket, _ = classify(row)
    assert bucket == "D"


def test_vu_sua_reference_in_raw_text_only_is_class_d_legitimate():
    # cleaned_name could plausibly be trimmed differently upstream; the raw
    # text alone naming the fruit must still preserve the row.
    row = {"cleaned_name": "vú sữa tươi", "raw_text": "2 trái vú sữa lò rèn"}
    bucket, _ = classify(row)
    assert bucket == "D"


def test_unrelated_dairy_variant_is_ambiguous_class_b():
    # Not one of the specific reviewed dairy terms that caused the historical
    # bug/alias -- must stay B, not be force-classified A.
    row = {"cleaned_name": "sữa chua", "raw_text": "1 hộp sữa chua"}
    bucket, _ = classify(row)
    assert bucket == "B"


def test_unrelated_identity_defaults_to_class_b():
    row = {"cleaned_name": "nguyên liệu lạ", "raw_text": "nguyên liệu lạ"}
    bucket, _ = classify(row)
    assert bucket == "B"


def test_all_classes_documented():
    assert set(CLASSES) == {"A", "B", "D"}
