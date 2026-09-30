"""Vegetarian ("chay") animal-identity guard at the matcher resolution layer.

The audit finding this protects: four alias-map keys resolve explicit
vegetarian analogue phrases to animal identities -- "đùi gà chay" -> 7088 Đùi
gà, "xúc xích chay" -> 7077 Xúc xích, "nem chua chay" -> 7073 Nem chua,
"thịt cua chay" -> 8069 Thịt cua -- and a fifth route, "nước dùng chay" ->
7141 Nước dùng, reaches meat broth the same way.

Removing those aliases is ineffective, which is why the guard is terminal and
lives at the resolution layer:

  * SUBPHRASE_CATALOG_MATCH re-derives every one of them from the catalog head
    ("đùi gà chay" -> 7088 at 0.55, "thịt cua chay" -> 8069 at 0.62), all well
    above the 0.35 threshold.
  * The neural stage reaches animal identities on its own, with no alias
    involved at all ("tôm chay" -> 8056, "thịt heo chay" -> 7065,
    "bò chay khô" -> 7076, "vịt chay" -> 11021).

Unlike the green-mango guard, this one must NOT blanket-return before the
neural stage. Green mango has no valid catalog target; "chay" does, and the
bi-encoder finds it ("gà chay" -> 20040, "sườn ống chay" -> 20039). The neural
RESULT is filtered instead, so correct vegan resolutions survive.

Scope of these tests: matcher behaviour only. The four hazardous alias-map keys
are deliberately left in place (the guard makes them inert, which keeps the
blast-radius measurement clean), seasoning analogues in "Gia vị, nước chấm" are
explicitly out of scope, and nothing here writes canonical data.
"""

import csv
import inspect
import json
import re
import unicodedata

import pytest

from nlp.entity_matcher import (
    ANIMAL_CATEGORIES_VI,
    ANIMAL_SUPPLEMENTARY_CODES,
    VEGETARIAN_GUARD_REASON,
    VietnameseIngredientMatcher,
    is_chay_text,
    normalize_vietnamese_text,
)
from nlp.pipeline import IngredientProcessingPipeline

ING = "data/processed/recipes/recipe_ingredients.csv"
CATALOG = "data/processed/viendinhduong/master_ingredients_nutrition.csv"
ALIAS = "data/processed/viendinhduong/ingredient_alias_map.json"

# The reviewed blast radius: 11 rows, keyed by id prefix, with the animal
# identity each one carried BEFORE remediation (recorded for traceability; the
# rows are UNMATCHED now). If this set drifts, the remediation script and the
# numbers in the applied-fix report are stale.
BLAST_RADIUS = {
    "f2c392cf": ("7088", "Đùi gà"),
    "dcc433c7": ("7088", "Đùi gà"),
    "fb37da49": ("7077", "Xúc xích"),
    "256d7443": ("7073", "Nem chua"),
    "7c4d60bc": ("8069", "Thịt cua"),
    "1d643050": ("7141", "Nước dùng"),
    "22d71f4f": ("7141", "Nước dùng"),
    "318fddc7": ("7141", "Nước dùng"),
    "bb9a520c": ("7141", "Nước dùng"),
    "2175a41f": ("7141", "Nước dùng"),
    "1e0d1e8b": ("7141", "Nước dùng"),
}

# The four hazardous alias-map keys. Kept in the map on purpose for this task.
HAZARDOUS_ALIASES = {
    "đùi gà chay": "7088",
    "xúc xích chay": "7077",
    "nem chua chay": "7073",
    "thịt cua chay": "8069",
}

# Blocked at the alias stage: each is a live alias-map key pointing at an animal.
ALIAS_STAGE_BLOCKED = ("đùi gà chay", "xúc xích chay", "nem chua chay",
                       "thịt cua chay", "nước dùng chay")

# Blocked at the subphrase stage: not alias keys, but the catalog head matches.
SUBPHRASE_STAGE_BLOCKED = ("đùi gà chay khô", "nem chua chay loại ngon")

# Blocked at the neural stage: no alias, no subphrase, animal picked by BERT.
NEURAL_STAGE_BLOCKED = ("tôm chay", "thịt heo chay", "thịt dê chay",
                        "mỡ heo chay", "bò chay khô", "vịt chay")

# Reviewed vegan aliases that must keep resolving. "thịt bò chay lát" is the
# precedent repair: it reaches 20039 only because the alias stage runs before
# the subphrase stage, which would otherwise hand it 7006 Thịt bò at 0.44.
VEGAN_ALIASES_ALLOWED = {
    "thịt bò chay lát": "20039",
    "thịt bò chay": "20039",
    "bò lát chay": "20039",
    "sườn chay": "20039",
    "sườn non chay": "20039",
    "thịt chay": "20039",
    "chả lụa chay": "20040",
    "chả chay": "20040",
    "giò lụa chay": "20040",
}

# Genuinely vegan neural picks. These exist only because the guard filters the
# neural result instead of short-circuiting ahead of it.
VEGAN_NEURAL_ALLOWED = ("gà chay", "giò sống chay", "ham chay",
                        "sườn ống chay", "thịt bằm chay")

# Non-animal categories that must pass without any phrase special-casing.
NON_ANIMAL_ALLOWED = {
    "nấm đùi gà chay": "20007",   # king oyster mushroom, NOT poultry
    "nấm rơm chả lụa chay": "4129",
}

# Out of scope by reviewed policy: animal-derived condiments live in
# "Gia vị, nước chấm", so the category test exempts them structurally.
SEASONING_ALLOWED = {
    "nước mắm chay": "13017",
    "dầu hào chay": "13027",
    "hạt nêm chay": "13026",
    "sa tế chay": "13054",
}

# Near-miss tokens present in the corpus. Diacritics are preserved through
# normalize_vietnamese_text(), so none of these is the vegetarian marker.
NON_MARKER_TEXTS = ("rang cháy cạnh", "cơm cháy", "vịt cháy tỏi",
                    "bơ lạt đun chảy", "bơ lạt hơ chảy", "chày giã", "chạy bộ")

# Bare animal phrases: no marker, so the guard must never touch them.
BARE_ANIMAL_UNAFFECTED = {
    "đùi gà": "7088",
    "xúc xích": "7077",
    "nem chua": "7073",
    "thịt cua": "8069",
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


@pytest.fixture(scope="module")
def catalog_by_code():
    with open(CATALOG, encoding="utf-8-sig", newline="") as f:
        return {r["code"].strip(): r for r in csv.DictReader(f)}


def _is_animal(catalog_by_code, code):
    code = (code or "").strip()
    if not code or code not in catalog_by_code:
        return False
    row = catalog_by_code[code]
    return (row["category_vi"].strip() in ANIMAL_CATEGORIES_VI
            or code in ANIMAL_SUPPLEMENTARY_CODES)


# ---------------------------------------------------------------------------
# The token predicate
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("text", ["chay", "đùi gà chay", "CHAY", "Chay ",
                                  "món chay, ngon", "ăn chay"])
def test_standalone_chay_token_is_detected(text):
    assert is_chay_text(text) is True


@pytest.mark.parametrize("text", NON_MARKER_TEXTS)
def test_near_miss_tokens_do_not_trigger(text):
    """cháy/chảy/chày/chạy are unrelated words. Diacritics keep them distinct."""
    assert is_chay_text(text) is False


def test_chay_is_not_matched_as_a_substring():
    assert is_chay_text("chayote") is False
    assert is_chay_text("machay") is False


def test_evidence_is_the_union_of_both_sources():
    """The reviewed policy reads raw_text OR cleaned_name, not just one."""
    assert is_chay_text("Chân nấm tẩm ướp (Chân dê chay)", "chân nấm tẩm ướp")
    assert is_chay_text(None, "đùi gà chay") is True
    assert is_chay_text("Đùi gà chay 250 gr", None) is True
    assert is_chay_text(None, None) is False


def test_raw_text_only_evidence_blocks(matcher):
    """The marker can survive only in the raw line; that must still count."""
    result = matcher.match("đùi gà", raw_context="Đùi gà chay 250 gr")
    assert result["method"] == "UNMATCHED"
    assert result["guard"] == VEGETARIAN_GUARD_REASON


# ---------------------------------------------------------------------------
# Per-stage blocking
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("phrase", ALIAS_STAGE_BLOCKED)
def test_alias_stage_animal_target_is_blocked(matcher, phrase):
    result = matcher.match(phrase)
    assert result["method"] == "UNMATCHED", phrase
    assert result["guard"] == VEGETARIAN_GUARD_REASON


@pytest.mark.parametrize("phrase", SUBPHRASE_STAGE_BLOCKED)
def test_subphrase_stage_animal_target_is_blocked(matcher, phrase):
    """Not alias keys -- these reach the animal identity through the catalog
    head, which is exactly why removing the aliases would not have helped."""
    assert matcher._resolve_alias(normalize_vietnamese_text(phrase), phrase) is None
    result = matcher.match(phrase)
    assert result["method"] == "UNMATCHED", phrase
    assert result["guard"] == VEGETARIAN_GUARD_REASON


@pytest.mark.parametrize("phrase", NEURAL_STAGE_BLOCKED)
def test_neural_stage_animal_target_is_blocked(matcher, phrase):
    result = matcher.match(phrase)
    assert result["method"] == "UNMATCHED", phrase
    assert result["guard"] == VEGETARIAN_GUARD_REASON


def test_supplementary_animal_codes_are_blocked(matcher, catalog_by_code):
    """Animal identities filed under non-animal categories, which the category
    test alone would miss. "vịt chay" reaches 11021 (Đồ hộp) via the neural
    stage; without the supplementary set it would resolve to canned duck."""
    assert catalog_by_code["11021"]["category_vi"] not in ANIMAL_CATEGORIES_VI
    assert catalog_by_code["6003"]["category_vi"] not in ANIMAL_CATEGORIES_VI
    for code in ANIMAL_SUPPLEMENTARY_CODES:
        assert code in catalog_by_code, code
    result = matcher.match("vịt chay")
    assert result["method"] == "UNMATCHED"
    assert result["guard"] == VEGETARIAN_GUARD_REASON


def test_guard_predicate_is_keyed_on_resolved_identity(matcher, catalog_by_code):
    """_blocks_vegetarian reads the resolved catalog entry, never the phrase."""
    for idx, item in enumerate(matcher.catalog):
        code = str(item.get("code", "")).strip()
        assert matcher._blocks_vegetarian(idx, False) is False, code
        assert matcher._blocks_vegetarian(idx, True) is _is_animal(catalog_by_code, code), code


# ---------------------------------------------------------------------------
# What must NOT be blocked
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("phrase,code", sorted(VEGAN_ALIASES_ALLOWED.items()))
def test_reviewed_vegan_aliases_still_resolve(matcher, phrase, code):
    result = matcher.match(phrase)
    assert result["method"] != "UNMATCHED", phrase
    assert result["matched_item"]["code"] == code


def test_thit_bo_chay_lat_precedent_is_preserved(matcher):
    """The prior repair. It survives only because the guard runs AFTER alias
    resolution: the subphrase stage would hand this phrase 7006 Thịt bò."""
    result = matcher.match("thịt bò chay lát")
    assert result["method"] == "PRESET_ALIAS_MATCH"
    assert result["matched_item"]["code"] == "20039"


@pytest.mark.parametrize("phrase", VEGAN_NEURAL_ALLOWED)
def test_valid_vegan_neural_target_is_allowed(matcher, phrase):
    """The reason the guard filters the neural result rather than returning
    UNMATCHED ahead of the neural stage."""
    result = matcher.match(phrase)
    assert result["method"] != "UNMATCHED", phrase
    assert result["matched_item"]["code"] in {"20039", "20040"}


@pytest.mark.parametrize("phrase,code", sorted(NON_ANIMAL_ALLOWED.items()))
def test_non_animal_identities_pass(matcher, phrase, code):
    """20007 Nấm đùi gà is a mushroom. A substring rule on "gà" would wrongly
    block it; the category policy exempts it with no special case."""
    result = matcher.match(phrase)
    assert result["method"] != "UNMATCHED", phrase
    assert result["matched_item"]["code"] == code


@pytest.mark.parametrize("phrase,code", sorted(SEASONING_ALLOWED.items()))
def test_seasoning_analogues_are_not_blocked(matcher, phrase, code):
    """Explicitly out of scope. Not a claim that these mappings are perfect."""
    result = matcher.match(phrase)
    assert result["method"] != "UNMATCHED", phrase
    assert result["matched_item"]["code"] == code
    assert result["matched_item"]["category_vi"] == "Gia vị, nước chấm"


@pytest.mark.parametrize("phrase,code", sorted(BARE_ANIMAL_UNAFFECTED.items()))
def test_bare_animal_phrases_are_unaffected(matcher, phrase, code):
    result = matcher.match(phrase)
    assert result["method"] != "UNMATCHED", phrase
    assert result["matched_item"]["code"] == code


@pytest.mark.parametrize("text", NON_MARKER_TEXTS)
def test_near_miss_rows_still_resolve_normally(matcher, text):
    """A "cháy" row must not be collateral damage."""
    assert matcher.match(text)["method"] != "UNMATCHED"


def test_guard_does_not_read_diet_tags(matcher):
    """No diet_tags-based logic. 534 recipes carry "Ăn chay" and 89 of their
    rows are genuinely meat ("Ba rọi xào mắm ruốc", "Canh sườn non nấu khoai
    mỡ") -- a tag-driven guard would blank all of them. The matcher has no
    access to recipe metadata at all, and these resolve untouched."""
    src = inspect.getsource(VietnameseIngredientMatcher._blocks_vegetarian)
    assert "diet" not in src.lower()
    for phrase, code in (("thịt ba chỉ", "7018"), ("sườn non", "7053")):
        result = matcher.match(phrase)
        assert result["method"] != "UNMATCHED"
        assert result["matched_item"]["code"] == code


# ---------------------------------------------------------------------------
# UNMATCHED contract and match()/match_batch() parity
# ---------------------------------------------------------------------------

def test_guard_verdict_names_its_reason(matcher):
    result = matcher.match("đùi gà chay")
    assert result["method"] == "UNMATCHED"
    assert result["guard"] == VEGETARIAN_GUARD_REASON
    assert result["matched_item"] == {}
    assert result["confidence"] is None
    assert result["top_candidates"] == []


@pytest.mark.parametrize(
    "phrase", ALIAS_STAGE_BLOCKED + SUBPHRASE_STAGE_BLOCKED + NEURAL_STAGE_BLOCKED
)
def test_blocked_rows_carry_no_identity_or_nutrition(pipeline, phrase):
    """UNMATCHED means "unknown": null nutrition, not a measured zero."""
    processed = pipeline.process(f"{phrase} 100g")
    matched = processed["matched_master_ingredient"]
    assert matched["match_method"] == "UNMATCHED", phrase
    assert matched["code"] is None
    assert matched["name_vi"] is None
    assert matched["match_confidence"] is None
    assert all(v is None for v in processed["estimated_portion_nutrition"].values())


def test_match_and_match_batch_agree(matcher):
    """match_batch() carries its own copy of the resolution ladder; the guard
    must be on both or a bulk reprocess would reintroduce the regression.

    Blocked-vs-resolved parity is asserted for every phrase. Resolved CODE
    parity is asserted only for chay-marked phrases -- the two ladders already
    disagree on some unmarked phrases for reasons that predate this guard, see
    test_known_preexisting_batch_divergence_is_not_caused_by_the_guard.
    """
    phrases = list(
        ALIAS_STAGE_BLOCKED + SUBPHRASE_STAGE_BLOCKED + NEURAL_STAGE_BLOCKED
        + VEGAN_NEURAL_ALLOWED + NON_MARKER_TEXTS
        + tuple(VEGAN_ALIASES_ALLOWED) + tuple(SEASONING_ALLOWED)
        + tuple(NON_ANIMAL_ALLOWED) + tuple(BARE_ANIMAL_UNAFFECTED)
    )
    batch = matcher.match_batch(phrases)
    for phrase, batched in zip(phrases, batch):
        single = matcher.match(phrase)
        assert (single["method"] == "UNMATCHED") == (batched["method"] == "UNMATCHED"), phrase
        if is_chay_text(phrase):
            assert single["matched_item"].get("code") == batched["matched_item"].get("code"), phrase


def test_known_preexisting_batch_divergence_is_not_caused_by_the_guard(matcher):
    """Recorded, not fixed: out of scope for this task (AGENTS.md §18).

    match() gates SUBPHRASE_CATALOG_MATCH on a 0.35 length ratio and falls
    through to the neural stage when it is not met; match_batch() gates only on
    a 3-character catalog head and resolves there. "vịt cháy tỏi" therefore
    lands on 11021 via BERT in match() and 4103 via subphrase in match_batch().

    The guard cannot be the cause: the phrase carries no "chay" token, so
    _blocks_vegetarian() is inert on both paths. Asserted here so the
    divergence stays visible and a future fix has a home.
    """
    phrase = "vịt cháy tỏi"
    assert is_chay_text(phrase) is False
    single = matcher.match(phrase)
    batched = matcher.match_batch([phrase])[0]
    assert single["method"] != "UNMATCHED"
    assert batched["method"] != "UNMATCHED"
    assert single["matched_item"]["code"] != batched["matched_item"]["code"]


def test_match_batch_blocks_with_raw_context(matcher):
    """The positional raw_contexts path feeds the guard too."""
    results = matcher.match_batch(
        ["đùi gà", "đùi gà"],
        raw_contexts=["Đùi gà chay 250 gr", "Đùi gà 250 gr"],
    )
    assert results[0]["method"] == "UNMATCHED"
    assert results[0]["guard"] == VEGETARIAN_GUARD_REASON
    assert results[1]["matched_item"]["code"] == "7088"


# ---------------------------------------------------------------------------
# Live-data invariants
# ---------------------------------------------------------------------------

def test_hazardous_aliases_are_still_present_and_inert(matcher):
    """Deliberately left in the map for this task: the guard makes them inert,
    which keeps the blast-radius measurement clean. Removing or repointing them
    is a separate reviewed decision."""
    with open(ALIAS, encoding="utf-8") as f:
        alias_map = json.load(f)
    for alias, code in HAZARDOUS_ALIASES.items():
        assert alias_map.get(alias) == code, alias
        assert matcher.match(alias)["method"] == "UNMATCHED", alias


def test_no_vegan_entry_is_filed_under_an_animal_category(catalog_by_code):
    """What makes the category test exact rather than approximate."""
    for code, row in catalog_by_code.items():
        if row["category_vi"].strip() in ANIMAL_CATEGORIES_VI:
            assert "chay" not in row["name_vi"].lower(), code


def test_no_chay_row_resolves_to_an_animal_identity(dataset_rows, catalog_by_code):
    """The post-remediation invariant, and the one that matters long-term: the
    guard's predicate must find nothing left to block in the live dataset."""
    offenders = [
        r for r in dataset_rows
        if (is_chay_text(r["raw_text"], r["cleaned_name"])
            and _is_animal(catalog_by_code, r["master_ingredient_code"]))
    ]
    assert offenders == [], [
        (r["id"][:8], r["raw_text"], r["master_ingredient_name"]) for r in offenders
    ]


def test_the_eleven_remediated_rows_hold_the_unmatched_contract(dataset_rows):
    """The reviewed population, repaired by
    scripts/eda/apply_vegetarian_chay_animal_guard_safe_fix.py. AGENTS.md §4:
    blank code/name, method UNMATCHED, null confidence, null nutrition -- and
    0.0 is never the sentinel for any of them."""
    by_prefix = {r["id"][:8]: r for r in dataset_rows if r["id"][:8] in BLAST_RADIUS}
    assert set(by_prefix) == set(BLAST_RADIUS)
    for prefix, row in sorted(by_prefix.items()):
        assert (row["master_ingredient_code"] or "") == "", prefix
        assert (row["master_ingredient_name"] or "") == "", prefix
        assert row["match_method"] == "UNMATCHED", prefix
        assert (row["match_confidence"] or "") == "", prefix
        for field in ("calories", "protein_g", "fat_g", "carbs_g"):
            assert (row[field] or "") == "", (prefix, field)


def test_remediated_rows_preserve_their_recipe_context(dataset_rows):
    """UNMATCHED drops the master link, not the record of what was asked for."""
    by_prefix = {r["id"][:8]: r for r in dataset_rows if r["id"][:8] in BLAST_RADIUS}
    for prefix, row in sorted(by_prefix.items()):
        assert row["raw_text"].strip(), prefix
        assert row["cleaned_name"].strip(), prefix
        assert float(row["estimated_weight_g"]) > 0, prefix
        assert is_chay_text(row["raw_text"], row["cleaned_name"]), prefix


def test_seasoning_rows_are_outside_the_blast_radius(dataset_rows, catalog_by_code):
    """213 rows resolve to "Gia vị, nước chấm" with a chay marker. None may be
    touched by this guard."""
    seasoning = [
        r for r in dataset_rows
        if is_chay_text(r["raw_text"], r["cleaned_name"])
        and (r["master_ingredient_code"] or "").strip() in catalog_by_code
        and catalog_by_code[r["master_ingredient_code"].strip()]["category_vi"]
        == "Gia vị, nước chấm"
    ]
    assert len(seasoning) == 213
    assert not any(_is_animal(catalog_by_code, r["master_ingredient_code"]) for r in seasoning)


def test_reviewed_vegan_rows_are_outside_the_blast_radius(dataset_rows, catalog_by_code):
    """61 rows already carry a correct 20039/20040 identity."""
    vegan = [
        r for r in dataset_rows
        if is_chay_text(r["raw_text"], r["cleaned_name"])
        and (r["master_ingredient_code"] or "").strip() in {"20039", "20040"}
    ]
    assert len(vegan) == 61
    assert not any(_is_animal(catalog_by_code, r["master_ingredient_code"]) for r in vegan)
