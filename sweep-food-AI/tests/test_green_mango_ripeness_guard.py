"""Mango ripeness guard at the matcher resolution layer.

The audit finding this protects: removing the "xoài" -> 5055 alias is
ineffective. clean_culinary_query() strips the green evidence ("xanh non",
"tươi sống", "bào sợi", ...) and the grammar parser strips the cultivar, so the
bare "xoài" that survives still reaches ripe 5055 -- through the alias while it
exists, and through SUBPHRASE_CATALOG_MATCH the moment it does not. Patching
the alias map alone therefore cannot hold the line; the guard has to sit at the
resolution layer and read the ORIGINAL raw ingredient text.

Why green mango must stay UNMATCHED rather than be remapped: the catalog holds
exactly one mango identity, 5055 "Xoài chín" (ripe). 5033 "Muỗm, quéo" is
Mangifera foetida, a different species, and is not a substitute. There is no
green-mango master to point at, and adding one is explicitly out of scope here.

Scope of these tests: matcher behaviour only. Nothing here writes canonical
data, re-derives stored cleaned_name values, touches the 6 ambiguous bare-xoài
rows, or touches the 7 dangling 5074 rows.
"""

import csv

import pytest

from nlp.entity_matcher import (
    GREEN_MANGO_GUARD_REASON,
    GREEN_MANGO_MARKER_RE,
    RIPE_MANGO_CODE,
    THAI_SLICING_COMPLEMENTS,
    VietnameseIngredientMatcher,
    clean_culinary_query,
    is_green_mango_text,
    normalize_vietnamese_text,
)
from nlp.pipeline import IngredientProcessingPipeline

ING = "data/processed/recipes/recipe_ingredients.csv"
ALIAS = "data/processed/viendinhduong/ingredient_alias_map.json"

BARE_XOAI = "xoài"

# The reviewed marker set, and only it. See test_chua_is_not_a_marker for why
# "chua" is absent. Used here as a plain substring scan to DEFINE the reviewed
# green population in the dataset -- it is not the guard's rule, which treats
# "thái" separately (see the cultivar/slicing section below).
REVIEWED_MARKERS = ("xanh", "sống", "non", "keo", "tượng", "thái", "tứ quý")

# Every xoài+thái line in the corpus, hand-classified. All four are the Thai
# cultivar; the corpus contains no mango slicing instruction at all, so the
# cultivar rule below costs nothing and closes a latent false positive.
CULTIVAR_THAI_RAW_TEXTS = (
    "1 trái xoài Thái",
    "1/2 trái xoài Thái",
    "Xoài Thái: 1 quả",
    "1 trái nhỏ Xoài xanh (xoài Thái hoặc xoài tứ quý)",
)

# "thái" as the verb "to slice". None of these exist in the corpus today; they
# are the constructions a future crawl will produce, and none of them is
# evidence of an unripe mango.
SLICING_THAI_RAW_TEXTS = (
    "xoài thái lát",
    "xoài thái mỏng",
    "xoài thái sợi",
    "xoài thái nhỏ",
    "xoài thái chỉ",
    "xoài thái miếng",
    "xoài thái hạt lựu",
    "xoài thái múi cau",
    "xoài thái khúc",
    "xoài thái rối",
    "xoài thái vuông",
    "xoài thái nhuyễn",
    "1 quả xoài thái lát mỏng",
)

# ---------------------------------------------------------------------------
# The 16 GREEN_CONFIRMED rows the audit flagged as at regression risk: every
# currently-UNMATCHED mango row whose stored cleaned_name reduces to the bare
# "xoài" that still resolves to ripe 5055. Listed as raw strings, with
# duplicates kept, because the row count is the load-bearing number.
# ---------------------------------------------------------------------------
AT_RISK_GUARDED = (
    "xoài sống",
    "xoài xanh",
    "2 trái xoài non",
    "Xoài keo 160g",
    "Xoài keo: 1 trái",
    "Xoài keo: 1 trái",
    "Xoài keo: 1 trái",
    "Xoài cát xanh: 1/2 trái",
    "Xoài keo 1 quả",
    "Xoài keo 1 quả nhỏ",
    "Xoài keo 1 quả",
    "Xoài keo 1/4 trái",
    "Xoài keo 1 trái",
    "Xoài keo 1 trái",
    "Xoài keo : 100g",
)

# The 16th. Reviewed green (shredded green-mango salad) but its raw text
# carries no ripeness word at all -- "bào sợi" is a preparation verb this
# corpus applies to ripe and unripe produce alike (cà rốt bào sợi, đu đủ bào
# sợi), so it is preparation evidence, not ripeness evidence. Admitting it
# would be exactly the unreviewed generic blocker that "chua" was rejected for.
# It stays protected by its row-level CLEAR instead; see
# scripts/eda/apply_xoai_bao_soi_safe_fix.py.
AT_RISK_UNCOVERED = "xoài bào sợi"

AT_RISK_ROW_COUNT = 16

# Every distinct raw string in the live dataset that carries an explicit green
# marker. A superset of AT_RISK_GUARDED: the rest were already safe by accident
# (the bi-encoder happened to prefer "Quả sấu xanh"), and must now be UNMATCHED
# by decision rather than by luck.
GREEN_MARKER_RAW_TEXTS = (
    "1 quả xoài keo xanh",
    "1 trái nhỏ Xoài xanh (xoài Thái hoặc xoài tứ quý)",
    "1 trái xoài Thái",
    "1/2 quả Xoài xanh",
    "1/2 trái xoài Thái",
    "2 trái xoài non",
    "XOÀI KEO: 1 trái (cắt sợi)",
    "Xoài Thái: 1 quả",
    "Xoài cát xanh: 1/2 trái",
    "Xoài keo 1 quả",
    "Xoài keo 1 quả nhỏ",
    "Xoài keo 1 trái",
    "Xoài keo 1/4 trái",
    "Xoài keo 160g",
    "Xoài keo : 100g",
    "Xoài keo: 1 trái",
    "Xoài sống 100g Cắt que nhỏ cỡ đầu đũa",
    "Xoài xanh 1 quả",
    "Xoài xanh 1 trái",
    "Xoài xanh 100 gr",
    "Xoài xanh 100g",
    "Xoài xanh 150g",
    "Xoài xanh: 100g",
    "Xoài xanh: 300g",
    "xoài sống",
    "xoài xanh",
)

# Ripe rows that must keep resolving to 5055 -- the three named in the brief
# plus the reviewed ripe rows already fixed on this branch.
RIPE_RAW_TEXTS = (
    "1 quả xoài chín",
    "Xoài chín : 100 gr",
    "Xoài chín 1 quả",
    "Xoài chín 2 trái",
    "Xoài chín giòn 1/2 trái",
    "Trang trí: xoài chín",
    "Xoài đông lạnh 340 gr",
    "Xoài cát chu vừa chín tới 600g (2 quả nhỏ)",
    "Xoài cát ( vừa chín tới) 1 quả",
)

# The bare-xoài rows deliberately left alone: ambiguous, plausibly ripe, and
# out of scope for this change. Their behaviour must be bit-for-bit unchanged.
# Five distinct strings across six live rows ("Xoài" appears twice).
AMBIGUOUS_BARE_XOAI_RAW_TEXTS = (
    "Xoài",
    "45 g xoài",
    "Xoài: 1/2 trái",
    "Xoài 1/2 quả",
    "Xoài: 1 trái",
)

# Non-mango lines, including ones that carry a marker word in an unrelated
# sense: "sườn non" (pork ribs), "cà chua" (tomato), "thái" as a slicing verb,
# "xanh" on a different fruit.
NON_MANGO_RAW_TEXTS = {
    "2 quả Cà chua": "4005",
    "300 g Dưa cải chua": None,
    "sườn non 500g": None,
    "Thịt ba chỉ thái mỏng 200g": None,
    "Đu đủ xanh 300g": None,
    "Chuối xanh 2 quả": None,
    "Rau muống 1 bó": None,
    "hành lá thái nhỏ": None,
}


@pytest.fixture(scope="module")
def matcher():
    return VietnameseIngredientMatcher(device="cpu")


@pytest.fixture(scope="module")
def pipeline():
    return IngredientProcessingPipeline(device="cpu")


@pytest.fixture(scope="module")
def dataset_rows():
    with open(ING, encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def _run(pipeline, raw_text):
    """A full matcher run: parse the recipe line, then resolve it, exactly as
    the production pipeline does."""
    return pipeline.process(raw_text)["matched_master_ingredient"]


# ---------------------------------------------------------------------------
# The at-risk population, asserted against the live dataset
# ---------------------------------------------------------------------------

def test_at_risk_population_is_still_sixteen_rows(dataset_rows):
    """If this count moves, the fixed raw-string lists below are stale."""
    at_risk = [
        r for r in dataset_rows
        if "xoài" in (r["raw_text"] or "").lower()
        and clean_culinary_query(r["cleaned_name"] or "") == BARE_XOAI
        and r["match_method"] == "UNMATCHED"
    ]
    assert len(at_risk) == AT_RISK_ROW_COUNT
    assert sorted(r["raw_text"] for r in at_risk) == sorted(
        AT_RISK_GUARDED + (AT_RISK_UNCOVERED,)
    )


def test_green_marker_rows_are_all_unmatched_in_the_dataset(dataset_rows):
    """The state the guard exists to preserve."""
    green = [
        r for r in dataset_rows
        if "xoài" in (r["raw_text"] or "").lower()
        and any(m in (r["raw_text"] or "").lower() for m in REVIEWED_MARKERS)
    ]
    assert len(green) == 31
    assert all(r["match_method"] == "UNMATCHED" for r in green)
    assert all((r["master_ingredient_code"] or "") == "" for r in green)
    assert sorted({r["raw_text"] for r in green}) == sorted(GREEN_MARKER_RAW_TEXTS)


# ---------------------------------------------------------------------------
# Regression: green mango stays UNMATCHED through a full matcher run
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("raw_text", sorted(set(AT_RISK_GUARDED)))
def test_at_risk_row_stays_unmatched(pipeline, raw_text):
    matched = _run(pipeline, raw_text)
    assert matched["match_method"] == "UNMATCHED"
    assert matched["code"] is None
    assert matched["match_confidence"] is None


@pytest.mark.parametrize("raw_text", GREEN_MARKER_RAW_TEXTS)
def test_green_marker_row_stays_unmatched(pipeline, raw_text):
    matched = _run(pipeline, raw_text)
    assert matched["match_method"] == "UNMATCHED"
    assert matched["code"] is None


@pytest.mark.parametrize("raw_text", GREEN_MARKER_RAW_TEXTS)
def test_green_marker_row_never_resolves_to_ripe_mango(pipeline, raw_text):
    """The narrow contract, stated on its own: whatever else happens, green
    evidence must never be handed ripe mango's nutrition."""
    assert _run(pipeline, raw_text)["code"] != RIPE_MANGO_CODE


def test_batch_and_single_agree_on_every_green_row(pipeline):
    """match_batch() has its own copy of the resolution ladder; the guard must
    be on both or a bulk reprocess would silently reintroduce the regression."""
    batch = pipeline.process_batch(list(GREEN_MARKER_RAW_TEXTS))
    for raw_text, record in zip(GREEN_MARKER_RAW_TEXTS, batch):
        matched = record["matched_master_ingredient"]
        assert matched["match_method"] == "UNMATCHED", raw_text
        assert matched["code"] is None, raw_text


def test_guarded_rows_carry_no_nutrition(pipeline):
    """UNMATCHED means "unknown", so the portion nutrition must be null rather
    than a measured zero that would silently understate the recipe."""
    for raw_text in GREEN_MARKER_RAW_TEXTS:
        nutrition = pipeline.process(raw_text)["estimated_portion_nutrition"]
        assert all(v is None for v in nutrition.values()), raw_text


def test_guard_verdict_names_its_reason(matcher):
    result = matcher.match("xoài", raw_context="Xoài keo 1 trái")
    assert result["method"] == "UNMATCHED"
    assert result["guard"] == GREEN_MANGO_GUARD_REASON
    assert result["matched_item"] == {}
    assert result["confidence"] is None
    assert result["top_candidates"] == []


# ---------------------------------------------------------------------------
# The 16th row: documented gap, not silent coverage
# ---------------------------------------------------------------------------

def test_shredded_green_mango_is_the_only_at_risk_row_the_markers_miss(matcher):
    """"bào sợi" is a preparation verb, not a ripeness word, so the reviewed
    marker set does not and should not fire on it. The row is held UNMATCHED by
    its row-level CLEAR instead. Asserted here so the gap stays visible: if a
    reviewed marker for this row is ever added, this test is the one to flip."""
    assert is_green_mango_text(AT_RISK_UNCOVERED) is False

    result = matcher.match(
        clean_culinary_query(AT_RISK_UNCOVERED), raw_context=AT_RISK_UNCOVERED
    )
    assert result["method"] == "PRESET_ALIAS_MATCH"
    assert result["matched_item"]["code"] == RIPE_MANGO_CODE

    for raw_text in AT_RISK_GUARDED:
        assert is_green_mango_text(raw_text) is True, raw_text


def test_shredded_green_mango_row_is_still_cleared_in_the_dataset(dataset_rows):
    rows = [r for r in dataset_rows if r["raw_text"] == AT_RISK_UNCOVERED]
    assert len(rows) == 1
    assert rows[0]["match_method"] == "UNMATCHED"
    assert (rows[0]["master_ingredient_code"] or "") == ""


# ---------------------------------------------------------------------------
# Ripe mango is preserved
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("raw_text", RIPE_RAW_TEXTS)
def test_ripe_mango_still_resolves_to_5055(pipeline, raw_text):
    matched = _run(pipeline, raw_text)
    assert matched["code"] == RIPE_MANGO_CODE
    assert matched["name_vi"] == "Xoài chín"
    assert matched["match_method"] != "UNMATCHED"


@pytest.mark.parametrize(
    "raw_text", ["xoài chín", "xoài chín giòn", "trang trí xoài chín"]
)
def test_named_ripe_forms_resolve_to_5055(matcher, raw_text):
    result = matcher.match(raw_text, raw_context=raw_text)
    assert result["matched_item"]["code"] == RIPE_MANGO_CODE


# ---------------------------------------------------------------------------
# "thái": Thai cultivar vs the verb "to slice"
# ---------------------------------------------------------------------------

def test_thai_is_not_a_bare_marker():
    """A bare \\bthái\\b in the marker alternation would read every "xoài thái
    lát" as green mango. It must be handled by the cultivar rule instead."""
    assert GREEN_MANGO_MARKER_RE.search("thái") is None
    assert GREEN_MANGO_MARKER_RE.search("xoài thái lát") is None


def test_corpus_xoai_thai_rows_are_all_cultivar(dataset_rows):
    """The classification these rules rest on, asserted against the live data:
    every xoài+thái line in the corpus is the cultivar, written adjacently, and
    none is a slicing instruction."""
    rows = [
        r for r in dataset_rows
        if "xoài" in (r["raw_text"] or "").lower()
        and "thái" in (r["raw_text"] or "").lower()
    ]
    assert len(rows) == 4
    assert sorted(r["raw_text"] for r in rows) == sorted(CULTIVAR_THAI_RAW_TEXTS)

    for row in rows:
        text = normalize_vietnamese_text(row["raw_text"])
        assert "xoài thái" in text, row["raw_text"]
        after = text.split("xoài thái", 1)[1].strip().split(" ")
        assert after[0] not in THAI_SLICING_COMPLEMENTS, row["raw_text"]


@pytest.mark.parametrize("raw_text", CULTIVAR_THAI_RAW_TEXTS)
def test_cultivar_thai_is_still_green(pipeline, raw_text):
    assert is_green_mango_text(raw_text) is True
    assert _run(pipeline, raw_text)["match_method"] == "UNMATCHED"


@pytest.mark.parametrize("raw_text", SLICING_THAI_RAW_TEXTS)
def test_slicing_verb_is_not_green_evidence(raw_text):
    """The negative case: "thái" followed by a cutting complement is the verb,
    and a sliced mango says nothing about its ripeness."""
    assert is_green_mango_text(raw_text) is False


@pytest.mark.parametrize("raw_text", SLICING_THAI_RAW_TEXTS)
def test_sliced_mango_keeps_bare_xoai_behaviour(pipeline, raw_text):
    """Not green means not guarded: these fall back to the unqualified-mango
    behaviour they had before this change, rather than being cleared."""
    matched = _run(pipeline, raw_text)
    assert matched["match_method"] != "UNMATCHED"
    assert matched["code"] == RIPE_MANGO_CODE


def test_cultivar_rule_requires_adjacency(pipeline):
    """An unrelated Thai ingredient in the same line is not mango cultivar
    evidence, so it must not drag the line into the guard."""
    assert is_green_mango_text("xoài, ớt sừng thái") is False
    assert _run(pipeline, "xoài, ớt sừng thái")["code"] == RIPE_MANGO_CODE


def test_another_marker_still_carries_a_sliced_line(pipeline):
    """Disarming "thái" must not disarm the line: "xoài xanh thái sợi" is still
    green on the strength of "xanh"."""
    assert is_green_mango_text("xoài xanh thái sợi") is True
    assert _run(pipeline, "xoài xanh thái sợi")["match_method"] == "UNMATCHED"


@pytest.mark.parametrize(
    "raw_text", ["xoài chín thái lát", "Xoài chín thái lát 100g", "xoài chín thái sợi"]
)
def test_ripe_mango_with_a_knife_instruction_resolves_to_5055(pipeline, raw_text):
    assert is_green_mango_text(raw_text) is False
    assert _run(pipeline, raw_text)["code"] == RIPE_MANGO_CODE


def test_explicit_ripeness_overrides_a_marker(matcher):
    """"thái" is a cultivar marker and also the slicing verb. Explicit ripeness
    evidence in the same line wins, so a ripe row with a knife instruction is
    not collateral damage."""
    assert is_green_mango_text("xoài chín thái lát") is False
    result = matcher.match("xoài chín", raw_context="xoài chín thái lát 100g")
    assert result["matched_item"]["code"] == RIPE_MANGO_CODE


# ---------------------------------------------------------------------------
# Both resolution paths are guarded, and no alias was removed
# ---------------------------------------------------------------------------

def test_bare_xoai_alias_still_points_at_5055(matcher):
    """No global alias removal: the fix is a guard, not a deletion. The bare
    alias is what the 6 ambiguous rows still resolve through."""
    idx = matcher.alias_dict[BARE_XOAI]
    assert matcher.catalog[idx]["code"] == RIPE_MANGO_CODE


def test_alias_map_file_still_carries_the_bare_xoai_entry():
    import json

    with open(ALIAS, encoding="utf-8") as f:
        alias_map = json.load(f)
    assert alias_map[BARE_XOAI] == RIPE_MANGO_CODE


def test_alias_path_is_guarded(matcher):
    """Same query, same alias hit, opposite verdict -- the only difference is
    the raw evidence."""
    assert matcher.match("xoài")["method"] == "PRESET_ALIAS_MATCH"
    assert matcher.match("xoài", raw_context="Xoài keo 1 trái")["method"] == "UNMATCHED"


def test_subphrase_path_reaches_5055_without_the_alias(matcher):
    """The audit's core finding, in executable form: deleting the alias would
    not have helped, because the catalog head "xoài chín" swallows bare "xoài"
    at SUBPHRASE_CATALOG_MATCH."""
    stashed = matcher.alias_dict.pop(BARE_XOAI)
    try:
        result = matcher.match("xoài")
        assert result["method"] == "SUBPHRASE_CATALOG_MATCH"
        assert result["matched_item"]["code"] == RIPE_MANGO_CODE
    finally:
        matcher.alias_dict[BARE_XOAI] = stashed


def test_subphrase_path_is_guarded(matcher):
    """And with the alias gone, the guard still holds the subphrase route."""
    stashed = matcher.alias_dict.pop(BARE_XOAI)
    try:
        result = matcher.match("xoài", raw_context="Xoài keo 1 trái")
        assert result["method"] == "UNMATCHED"
        assert result["guard"] == GREEN_MANGO_GUARD_REASON
    finally:
        matcher.alias_dict[BARE_XOAI] = stashed


def test_guard_is_terminal_and_does_not_leak_into_the_neural_stage(matcher):
    """"xoài xanh" used to escape 5055 only because the bi-encoder happened to
    prefer "Quả sấu xanh" -- a different wrong fruit. The guard stops it before
    the neural stage instead of relying on that accident."""
    result = matcher.match("xoài xanh", raw_context="Xoài xanh 100g")
    assert result["method"] == "UNMATCHED"
    assert result["matched_item"] == {}


# ---------------------------------------------------------------------------
# Nothing else moves
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("raw_text", AMBIGUOUS_BARE_XOAI_RAW_TEXTS)
def test_ambiguous_bare_xoai_behaviour_is_unchanged(pipeline, raw_text):
    """Deliberately still resolving to 5055. These rows need their own review;
    this change must not pre-empt it in either direction."""
    matched = _run(pipeline, raw_text)
    assert matched["code"] == RIPE_MANGO_CODE
    assert matched["match_method"] == "PRESET_ALIAS_MATCH"


@pytest.mark.parametrize("raw_text", sorted(NON_MANGO_RAW_TEXTS))
def test_non_mango_lines_are_untouched(pipeline, raw_text):
    matched = _run(pipeline, raw_text)
    assert matched["match_method"] != "UNMATCHED"
    expected = NON_MANGO_RAW_TEXTS[raw_text]
    if expected is not None:
        assert matched["code"] == expected


def test_guard_never_fires_on_a_non_mango_line(dataset_rows):
    """Swept across all ~64k live rows: the predicate requires the word "xoài",
    so no other ingredient can be caught by "non", "xanh", "thái" or "keo"."""
    fired = [
        r["raw_text"] for r in dataset_rows
        if is_green_mango_text(r["raw_text"])
        and "xoài" not in normalize_vietnamese_text(r["raw_text"])
    ]
    assert fired == []


def test_guard_fires_on_exactly_the_green_marker_population(dataset_rows):
    fired = {r["raw_text"] for r in dataset_rows if is_green_mango_text(r["raw_text"])}
    assert fired == set(GREEN_MARKER_RAW_TEXTS)


def test_chua_is_not_a_marker(dataset_rows):
    """Excluded on evidence, not caution: no mango row in the corpus carries
    "chua", while ~1.5k non-mango rows do -- overwhelmingly inside an unrelated
    ingredient name (cà chua, sữa chua, cải chua) or as recipe-taste context
    ("tuỳ độ chua của kim chi"). There is nothing at ingredient level to
    support it, so it stays out until an audit produces some."""
    mango_with_chua = [
        r for r in dataset_rows
        if "xoài" in (r["raw_text"] or "").lower() and "chua" in (r["raw_text"] or "").lower()
    ]
    assert mango_with_chua == []

    non_mango_with_chua = [
        r for r in dataset_rows
        if "chua" in (r["raw_text"] or "").lower() and "xoài" not in (r["raw_text"] or "").lower()
    ]
    assert len(non_mango_with_chua) > 1000

    assert is_green_mango_text("xoài chua") is False
    assert is_green_mango_text("cà chua") is False


def test_dangling_5074_rows_are_untouched(dataset_rows):
    """Out of scope here; they carry no green marker and the guard only ever
    blocks 5055."""
    dangling = [
        r for r in dataset_rows
        if (r["master_ingredient_code"] or "").strip() == "5074"
    ]
    assert len(dangling) == 7
    assert not any(is_green_mango_text(r["raw_text"]) for r in dangling)
