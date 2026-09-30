"""Tests for scripts/eda/audit_qwen_matching.py's row classification.

Standard library / CSV-fixture only; no dependency on the real ~64k-row
processed dataset so these stay fast and independent of data changes.
"""

from scripts.eda.audit_qwen_matching import CLASSES, REVIEWED_ROW_REMAPS, classify

REMAP_ID = "dfa8f4c6-ffc5-4dc5-87de-ec2d52632bea"
XOAI_REMAP_IDS = (
    "114d0cb0-d4af-4dab-a094-b95a04ea4b1b",
    "60c41843-1d7b-45bf-aa7e-0ba399cb2258",
)


def _master(code, name):
    return {code: {"code": code, "name_vi": name}}


def test_known_class_a_false_positive_is_rejected():
    row = {"master_ingredient_code": "4019", "master_ingredient_name": "Hành hoa, tươi",
           "cleaned_name": "hành lá", "raw_text": "2 muỗng canh hành lá thái nhỏ"}
    bucket, _ = classify(row, _master("4019", "Chuối xanh"))
    assert bucket == "A"


def test_dangling_master_code_is_class_d():
    row = {"master_ingredient_code": "13038", "master_ingredient_name": "Bạc hà tươi",
           "cleaned_name": "bạc hà", "raw_text": "bạc hà"}
    bucket, _ = classify(row, {})
    assert bucket == "D"


def test_likely_valid_match_is_class_c():
    row = {"master_ingredient_code": "4007", "master_ingredient_name": "Cà rốt",
           "cleaned_name": "cà rốt", "raw_text": "2 củ cà rốt"}
    bucket, _ = classify(row, _master("4007", "Cà rốt"))
    assert bucket == "C"


def test_reviewed_identity_with_extra_raw_semantics_is_ambiguous_class_b():
    # cleaned name matches a reviewed WRONG pair, but raw text carries
    # unrecognized residue -- must stay B, not be force-classified A.
    row = {"master_ingredient_code": "4019", "master_ingredient_name": "Hành hoa, tươi",
           "cleaned_name": "hành lá", "raw_text": "hành lá và một loại rau thơm khác không rõ"}
    bucket, _ = classify(row, _master("4019", "Chuối xanh"))
    assert bucket == "B"


def test_unreviewed_identity_defaults_to_class_b():
    row = {"master_ingredient_code": "9999", "master_ingredient_name": "Nguyên liệu khác",
           "cleaned_name": "nguyên liệu lạ", "raw_text": "nguyên liệu lạ"}
    bucket, _ = classify(row, _master("9999", "Nguyên liệu khác"))
    assert bucket == "B"


def test_all_classes_documented():
    assert set(CLASSES) == {"A", "B", "C", "D"}


def test_reviewed_row_remap_classifies_as_c():
    # The one approved Class-D remap (bac ha -> doc mung), identified by its
    # explicit in-text disambiguation. Note the raw text would NOT satisfy
    # simple_raw()'s generic residue check (the "(Doc mung)" parenthetical
    # counts as unrecognized residue) -- this row is C only via the
    # row-specific reviewed-remap path, not the generic VALID mechanism.
    row = {"id": REMAP_ID, "master_ingredient_code": "4026", "master_ingredient_name": "Dọc mùng",
           "cleaned_name": "bạc hà", "raw_text": "Bạc hà (Dọc mùng): 100g"}
    bucket, reason = classify(row, _master("4026", "Dọc mùng"))
    assert bucket == "C"
    assert "4026" in reason and "Dọc mùng" in reason


def test_reviewed_row_remap_does_not_generalize_by_code_or_cleaned_name():
    # A DIFFERENT row that happens to share the same code and cleaned name
    # must NOT be swept into C -- REVIEWED_ROW_REMAPS is keyed by row id
    # specifically so this can never become a generic "bac ha == doc mung"
    # rule. Since 4026 is not in the WRONG/VALID tables either, this falls
    # through to the unreviewed default of B.
    row = {"id": "some-other-row-id", "master_ingredient_code": "4026",
           "master_ingredient_name": "Dọc mùng", "cleaned_name": "bạc hà", "raw_text": "bạc hà"}
    bucket, _ = classify(row, _master("4026", "Dọc mùng"))
    assert bucket == "B"


def test_reviewed_row_remap_fails_closed_on_code_drift():
    # Same reviewed row id, but its stored code no longer matches the
    # expected remap target -- must not blindly trust the id alone.
    row = {"id": REMAP_ID, "master_ingredient_code": "9999", "master_ingredient_name": "Something else",
           "cleaned_name": "bạc hà", "raw_text": "Bạc hà (Dọc mùng): 100g"}
    bucket, _ = classify(row, _master("9999", "Something else"))
    assert bucket == "B"


def test_reviewed_row_remap_fails_closed_on_catalog_name_drift():
    # Same reviewed row id and code, but the catalog has since repointed
    # 4026 to a different ingredient -- must fall through, not stay C.
    row = {"id": REMAP_ID, "master_ingredient_code": "4026", "master_ingredient_name": "Dọc mùng",
           "cleaned_name": "bạc hà", "raw_text": "Bạc hà (Dọc mùng): 100g"}
    bucket, _ = classify(row, _master("4026", "Something Else Entirely"))
    assert bucket == "B"


def test_other_bac_ha_rows_with_dangling_code_remain_class_d():
    # The 32 other Bac ha NEEDS_REVIEW rows still carry the original dangling
    # code 13038 -- the reviewed-row-remap table must never touch them, and
    # they must stay D regardless of REVIEWED_ROW_REMAPS's contents.
    row = {"id": "some-other-bac-ha-row", "master_ingredient_code": "13038",
           "master_ingredient_name": "Bạc hà tươi", "cleaned_name": "bạc hà", "raw_text": "Bạc hà 200 gr"}
    bucket, _ = classify(row, {})
    assert bucket == "D"


def test_reviewed_row_remaps_is_scoped_to_the_reviewed_rows_only():
    # Three individually reviewed rows: one Bac ha row that names "Doc mung"
    # in its own raw text, and two Xoai rows that state ripeness explicitly
    # ("vua chin toi"). Any growth here must be a deliberate, row-level review.
    assert set(REVIEWED_ROW_REMAPS) == {REMAP_ID, *XOAI_REMAP_IDS}


def test_reviewed_xoai_rows_classify_as_c_on_the_ripe_catalog_identity():
    for row_id in XOAI_REMAP_IDS:
        row = {"id": row_id, "master_ingredient_code": "5055",
               "master_ingredient_name": "Xoài chín", "cleaned_name": "xoài cát",
               "raw_text": "Xoài cát ( vừa chín tới) 1 quả"}
        bucket, _ = classify(row, _master("5055", "Xoài chín"))
        assert bucket == "C"


def test_reviewed_xoai_remap_does_not_generalize_to_other_mango_rows():
    # A DIFFERENT mango row on the same code and cleaned name must NOT be
    # swept into C. This is what keeps the 7 remaining NEEDS_REVIEW Xoai rows
    # -- varietal names with no ripeness word -- from riding along.
    row = {"id": "some-other-xoai-row-id", "master_ingredient_code": "5055",
           "master_ingredient_name": "Xoài chín", "cleaned_name": "xoài cát",
           "raw_text": "1 trái xoài cát"}
    bucket, _ = classify(row, _master("5055", "Xoài chín"))
    assert bucket == "B"


def test_reviewed_xoai_remap_fails_closed_on_catalog_name_drift():
    # Same reviewed row id and code, but the catalog has since repointed 5055
    # to a different ingredient -- must fall through, not stay C.
    row = {"id": XOAI_REMAP_IDS[0], "master_ingredient_code": "5055",
           "master_ingredient_name": "Xoài chín", "cleaned_name": "xoài cát",
           "raw_text": "Xoài cát chu vừa chín tới 600g (2 quả nhỏ)"}
    bucket, _ = classify(row, _master("5055", "Something Else Entirely"))
    assert bucket == "B"


def test_other_xoai_rows_with_dangling_code_remain_class_d():
    # The 7 other Xoai NEEDS_REVIEW rows still carry the original dangling
    # code 5074 and must stay D regardless of REVIEWED_ROW_REMAPS's contents.
    row = {"id": "some-other-xoai-row", "master_ingredient_code": "5074",
           "master_ingredient_name": "Xoài", "cleaned_name": "xoài cát",
           "raw_text": "1 trái xoài cát"}
    bucket, _ = classify(row, {})
    assert bucket == "D"
