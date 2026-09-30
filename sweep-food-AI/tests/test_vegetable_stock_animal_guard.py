"""Vegetable-stock animal-identity guard at the matcher resolution layer.

The audit finding this protects: "Nước dùng rau củ 1,6 lít" is vegetable stock,
and it was resolving to 7141 "Nước dùng" (Broth) -- filed under "Thịt và sản
phẩm chế biến", meat. 8 live rows were scored that way.

This is the residual case the vegetarian ("chay") guard explicitly deferred:
these rows carry no ingredient-level "chay" marker, so is_chay_text() is inert
on them and they survived that fix.

Removing the two alias-map keys is ineffective, which is why the guard is
terminal and lives at the resolution layer:

  * SUBPHRASE_CATALOG_MATCH re-derives 7141 from the catalog head "nước dùng"
    ("nước dùng rau" -> 0.692, "nước dùng rau củ" -> 0.562), far over the 0.35
    threshold.
  * "nước dùng rau củ quả" already reaches 7141 at 0.45 with NO alias at all.
  * The neural stage's top-1 is an animal identity for every variant (7141 at
    0.54-0.58, else 7140 "Nước canh", also meat); its best non-animal candidate
    is 4100 "Súp lơ xanh" -- broccoli.

Unlike the green-mango guard, this one must NOT blanket-return before the
neural stage, and unlike the chay guard it must stay inert on non-animal
targets: a future vegetable-stock catalog entry (a recorded, deferred catalog
gap) has to be reachable by exactly these phrases. The guard blocks animal
IDENTITIES, not the phrase -- see test_non_animal_target_is_not_blocked.

Scope of these tests: matcher behaviour plus the live-data invariants for the 8
remediated rows. The two alias-map keys are deliberately left in place (the
guard makes them inert), and nothing here writes canonical data.
"""

import csv
import inspect
import json

import pytest

from nlp.entity_matcher import (
    ANIMAL_CATEGORIES_VI,
    ANIMAL_SUPPLEMENTARY_CODES,
    VEGETABLE_STOCK_GUARD_REASON,
    VEGETARIAN_GUARD_REASON,
    VietnameseIngredientMatcher,
    is_chay_text,
    is_vegetable_stock_text,
    normalize_vietnamese_text,
)
from nlp.pipeline import IngredientProcessingPipeline

ING = "data/processed/recipes/recipe_ingredients.csv"
CATALOG = "data/processed/viendinhduong/master_ingredients_nutrition.csv"
ALIAS = "data/processed/viendinhduong/ingredient_alias_map.json"

# The reviewed blast radius: 8 rows, keyed by id prefix, with the raw_text and
# the stored cleaned_name each carries. Note the cleaned_name column: FOUR rows
# store "nước dùng rau" although their raw text reads "Nước dùng rau củ" --
# historical parser drift, deliberately NOT repaired here (AGENTS.md §18).
# (81739420 also stores "nước dùng rau", but its raw text genuinely says that.)
# The guard reads the UNION of both fields precisely so that drift cannot hide
# the phrase.
BLAST_RADIUS = {
    "f9e2f60c": ("Nước dùng rau củ 1,6 lít", "nước dùng rau"),
    "e07fe326": ("Nước dùng rau củ 1,2 lít", "nước dùng rau"),
    "e3b10cc6": ("Nước dùng rau củ 1 lít", "nước dùng rau"),
    "16c22e9a": ("Nước dùng rau củ 1,5 lít", "nước dùng rau"),
    "81739420": ("Nước dùng rau 950 ml", "nước dùng rau"),
    "22b6999f": ("Nước dùng rau củ: 1,2 L", "nước dùng rau củ"),
    "ba987c1c": ("Nước dùng rau củ: 1 lít", "nước dùng rau củ"),
    "c9f4c65d": ("Nước dùng rau củ: 1,5L", "nước dùng rau củ"),
}

# Already UNMATCHED before this fix; recognized by the guard, untouched by the
# remediation. This is why "hầm" is in the stock-head pattern.
FORWARD_PROTECTION = {"470f6222": ("Nước hầm rau 700 ml", "nước hầm rau")}

# The two alias-map keys. Kept in the map on purpose for this task.
HAZARDOUS_ALIASES = {
    "nước dùng rau": "7141",
    "nước dùng rau củ": "7141",
}

# Blocked at the alias stage: live alias-map keys pointing at an animal.
ALIAS_STAGE_BLOCKED = ("nước dùng rau", "nước dùng rau củ")

# Blocked at the subphrase stage: no alias exists, the catalog head "nước dùng"
# is re-derived from inside the query.
SUBPHRASE_STAGE_BLOCKED = ("nước dùng rau củ quả",)

# Blocked at the neural stage: no alias, no subphrase hit, BERT picks 7140.
NEURAL_STAGE_BLOCKED = ("nước hầm rau",)

# Reviewed false positives. Each names animal material explicitly, so the veto
# applies and 7141/7140 remain legitimate. The last two are the live corpus
# rows that make this concrete.
ANIMAL_VETOED = (
    "nước dùng gà rau củ",
    "nước dùng bò với rau",
    "nước dùng rau củ và gà",
    "nước hầm xương rau củ",
    "600 ml Nước hầm xương/rau củ/dashi",
)

# Ordinary phrases that must be untouched.
UNAFFECTED = {
    "nước dùng": "7141",
    "nước dùng gà": "7141",
    "nước dùng tôm": "7141",
    "nước dùng dashi": "7141",
    "rau muống": "4083",
    "cà chua": "4005",
}


@pytest.fixture(scope="module")
def matcher():
    return VietnameseIngredientMatcher(device="cpu")


@pytest.fixture(scope="module")
def pipeline():
    return IngredientProcessingPipeline(device="cpu")


@pytest.fixture(scope="module")
def catalog_by_code():
    with open(CATALOG, encoding="utf-8-sig", newline="") as f:
        return {r["code"].strip(): r for r in csv.DictReader(f)}


@pytest.fixture(scope="module")
def dataset_rows():
    with open(ING, encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def _is_animal(catalog_by_code, code):
    code = (code or "").strip()
    if not code or code not in catalog_by_code:
        return False
    row = catalog_by_code[code]
    return (row["category_vi"].strip() in ANIMAL_CATEGORIES_VI
            or code in ANIMAL_SUPPLEMENTARY_CODES)


# ---------------------------------------------------------------------------
# The detector
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("text", [
    "nước dùng rau",
    "nước dùng rau củ",
    "nước dùng rau củ quả",
    "nước hầm rau",
    "nước hầm rau củ",
    "nước luộc rau",
    "Nước dùng rau củ 1,6 lít",
    "Nước dùng rau củ: 1,5L",
    "Nước dùng rau 950 ml",
])
def test_vegetable_stock_phrases_are_detected(text):
    assert is_vegetable_stock_text(text) is True


@pytest.mark.parametrize("text", ANIMAL_VETOED)
def test_animal_token_vetoes_detection(text):
    """An animal broth cooked with vegetables is still an animal broth."""
    assert is_vegetable_stock_text(text) is False


@pytest.mark.parametrize("text", [
    "rau",
    "rau củ",
    "rau muống",
    "rau thơm",
    "rau củ xào",
    "súp rau củ",
    "canh rau",
    "nước ép rau củ",
    "nước rau má",
    "nước dùng",
    "nước dùng chay",
    "nước mắm",
])
def test_bare_vegetable_and_plain_stock_do_not_trigger(text):
    """Bare "rau" is never the trigger: on its own it resolves to 4066 Rau bí,
    and plain "nước dùng" has no vegetable qualifier at all."""
    assert is_vegetable_stock_text(text) is False


def test_rau_as_a_separate_ingredient_does_not_trigger():
    """Live corpus row. "rau củ" here is the ingredient being used to COOK the
    stock, not a description of the stock. Adjacency declines it: "nước dùng"
    is followed by "chay", not "rau"."""
    assert is_vegetable_stock_text("Rau củ nấu nước dùng chay : su su") is False


def test_adjacency_is_what_makes_the_rule_narrow():
    """An animal qualifier between the stock head and "rau" breaks the pattern
    structurally -- before the veto is even consulted."""
    from nlp.entity_matcher import VEG_STOCK_RE
    assert VEG_STOCK_RE.search(normalize_vietnamese_text("nước dùng gà rau củ")) is None
    assert VEG_STOCK_RE.search(normalize_vietnamese_text("nước dùng rau củ")) is not None


def test_evidence_is_the_union_of_both_sources():
    assert is_vegetable_stock_text("Nước dùng rau củ 1,6 lít", "nước dùng rau") is True
    assert is_vegetable_stock_text(None, "nước dùng rau củ") is True
    assert is_vegetable_stock_text("Nước dùng rau 950 ml", None) is True
    assert is_vegetable_stock_text(None, None) is False


def test_detector_is_nfc_normalized():
    """Decomposed input must detect identically to composed input."""
    import unicodedata
    composed = "Nước dùng rau củ"
    decomposed = unicodedata.normalize("NFD", composed)
    assert composed != decomposed
    assert is_vegetable_stock_text(decomposed) is True


# ---------------------------------------------------------------------------
# Stage coverage
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("phrase", ALIAS_STAGE_BLOCKED)
def test_alias_stage_animal_target_is_blocked(matcher, phrase):
    assert matcher._resolve_alias(normalize_vietnamese_text(phrase), phrase) is not None
    result = matcher.match(phrase)
    assert result["method"] == "UNMATCHED", phrase
    assert result["guard"] == VEGETABLE_STOCK_GUARD_REASON


@pytest.mark.parametrize("phrase", SUBPHRASE_STAGE_BLOCKED)
def test_subphrase_stage_animal_target_is_blocked(matcher, phrase):
    """No alias exists for this phrase, so removing aliases would not have
    saved it -- the catalog head re-derives 7141 on its own."""
    assert matcher._resolve_alias(normalize_vietnamese_text(phrase), phrase) is None
    result = matcher.match(phrase)
    assert result["method"] == "UNMATCHED", phrase
    assert result["guard"] == VEGETABLE_STOCK_GUARD_REASON


@pytest.mark.parametrize("phrase", NEURAL_STAGE_BLOCKED)
def test_neural_stage_animal_target_is_blocked(matcher, phrase):
    result = matcher.match(phrase)
    assert result["method"] == "UNMATCHED", phrase
    assert result["guard"] == VEGETABLE_STOCK_GUARD_REASON


def test_raw_text_only_evidence_blocks(matcher):
    """The parsed name alone carries no vegetable qualifier; the raw line does."""
    result = matcher.match("nước dùng", raw_context="Nước dùng rau củ 1,6 lít")
    assert result["method"] == "UNMATCHED"
    assert result["guard"] == VEGETABLE_STOCK_GUARD_REASON


def test_stale_cleaned_name_case_still_blocks(matcher):
    """The five live rows whose cleaned_name lost "củ". Whichever side of the
    evidence carries the phrase, the guard fires."""
    result = matcher.match("nước dùng rau", raw_context="Nước dùng rau củ 1,6 lít")
    assert result["method"] == "UNMATCHED"
    assert result["guard"] == VEGETABLE_STOCK_GUARD_REASON


def test_guard_is_terminal_no_later_stage_re_derives_an_animal(matcher, catalog_by_code):
    """Every stage that can emit a resolved identity is covered, so no blocked
    phrase can fall through to another animal broth."""
    for phrase in (ALIAS_STAGE_BLOCKED + SUBPHRASE_STAGE_BLOCKED
                   + NEURAL_STAGE_BLOCKED):
        result = matcher.match(phrase)
        assert result["matched_item"] == {}, phrase
        assert not _is_animal(catalog_by_code, result["matched_item"].get("code"))


# ---------------------------------------------------------------------------
# Narrowness: what must NOT be blocked
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("phrase", ANIMAL_VETOED)
def test_animal_broth_with_vegetables_still_resolves(matcher, phrase):
    """The reviewed false positives. An explicit animal broth keeps its
    identity even though the line names vegetables."""
    result = matcher.match(phrase)
    assert result["method"] != "UNMATCHED", phrase


@pytest.mark.parametrize("phrase,code", sorted(UNAFFECTED.items()))
def test_unrelated_phrases_are_unaffected(matcher, phrase, code):
    result = matcher.match(phrase)
    assert result["method"] != "UNMATCHED", phrase
    assert result["matched_item"]["code"] == code


def test_non_animal_target_is_not_blocked(matcher, catalog_by_code):
    """The property that keeps the deferred vegetable-stock catalog entry
    viable: the guard blocks animal IDENTITIES, not the phrase.

    "nước luộc rau" matches VEG_STOCK_RE and carries no animal token, so the
    detector fires -- yet it resolves, because its target is a vegetable.
    """
    assert is_vegetable_stock_text("nước luộc rau") is True
    result = matcher.match("nước luộc rau")
    assert result["method"] != "UNMATCHED"
    code = result["matched_item"]["code"]
    assert not _is_animal(catalog_by_code, code)


def test_guard_predicate_is_keyed_on_resolved_identity(matcher, catalog_by_code):
    """Never on the alias key or the phrase text."""
    for code in ("7141", "7140", "20002", "4066", "4083", "20039"):
        idx = next(i for i, c in enumerate(matcher.catalog) if c["code"] == code)
        assert matcher._blocks_vegetable_stock(idx, False) is False, code
        assert matcher._blocks_vegetable_stock(idx, True) is _is_animal(
            catalog_by_code, code), code


def test_guard_reuses_the_reviewed_animal_policy():
    """The two guards must not drift apart."""
    veg = inspect.getsource(VietnameseIngredientMatcher._blocks_vegetable_stock)
    assert "ANIMAL_CATEGORIES_VI" in veg
    assert "ANIMAL_SUPPLEMENTARY_CODES" in veg
    assert "diet" not in veg.lower()


def test_guard_does_not_block_20002(matcher, catalog_by_code):
    """20002 is explicitly NOT a repoint target for these rows, but it is also
    not an animal identity, so the guard must be inert on it."""
    idx = next(i for i, c in enumerate(matcher.catalog) if c["code"] == "20002")
    assert matcher._blocks_vegetable_stock(idx, True) is False


# ---------------------------------------------------------------------------
# UNMATCHED contract and match()/match_batch() parity
# ---------------------------------------------------------------------------

def test_guard_verdict_names_its_reason(matcher):
    result = matcher.match("nước dùng rau củ")
    assert result["method"] == "UNMATCHED"
    assert result["guard"] == VEGETABLE_STOCK_GUARD_REASON
    assert result["matched_item"] == {}
    assert result["confidence"] is None
    assert result["top_candidates"] == []


@pytest.mark.parametrize(
    "phrase", ALIAS_STAGE_BLOCKED + SUBPHRASE_STAGE_BLOCKED + NEURAL_STAGE_BLOCKED
)
def test_blocked_rows_carry_no_identity_or_nutrition(pipeline, phrase):
    """UNMATCHED means "unknown": null nutrition, not a measured zero."""
    processed = pipeline.process(f"{phrase} 1 lít")
    matched = processed["matched_master_ingredient"]
    assert matched["match_method"] == "UNMATCHED", phrase
    assert matched["code"] is None
    assert matched["name_vi"] is None
    assert matched["match_confidence"] is None
    assert all(v is None for v in processed["estimated_portion_nutrition"].values())


def test_match_and_match_batch_agree(matcher):
    """match_batch() carries its own copy of the resolution ladder; the guard
    must be on both or a bulk reprocess would reintroduce the regression."""
    phrases = list(
        ALIAS_STAGE_BLOCKED + SUBPHRASE_STAGE_BLOCKED + NEURAL_STAGE_BLOCKED
        + ANIMAL_VETOED + tuple(UNAFFECTED)
    )
    batch = matcher.match_batch(phrases)
    for phrase, batched in zip(phrases, batch):
        single = matcher.match(phrase)
        assert (single["method"] == "UNMATCHED") == (batched["method"] == "UNMATCHED"), phrase
        if is_vegetable_stock_text(phrase):
            assert batched["guard"] == VEGETABLE_STOCK_GUARD_REASON, phrase


def test_match_batch_blocks_with_raw_context(matcher):
    """The positional raw_contexts path feeds the guard too."""
    results = matcher.match_batch(
        ["nước dùng", "nước dùng"],
        raw_contexts=["Nước dùng rau củ 1,6 lít", "Nước dùng gà 1,6 lít"],
    )
    assert results[0]["method"] == "UNMATCHED"
    assert results[0]["guard"] == VEGETABLE_STOCK_GUARD_REASON
    assert results[1]["matched_item"]["code"] == "7141"


# ---------------------------------------------------------------------------
# Interaction with the existing chay guard
# ---------------------------------------------------------------------------

def test_chay_guard_still_owns_its_rows(matcher):
    """"nước dùng chay" is the chay guard's row, not this one's. Both verdicts
    are UNMATCHED, but the reason must stay attributed correctly."""
    assert is_vegetable_stock_text("nước dùng chay") is False
    result = matcher.match("nước dùng chay")
    assert result["method"] == "UNMATCHED"
    assert result["guard"] == VEGETARIAN_GUARD_REASON


@pytest.mark.parametrize("phrase", ["đùi gà chay", "xúc xích chay", "thịt cua chay"])
def test_chay_guard_verdicts_are_unchanged(matcher, phrase):
    result = matcher.match(phrase)
    assert result["method"] == "UNMATCHED"
    assert result["guard"] == VEGETARIAN_GUARD_REASON


# ---------------------------------------------------------------------------
# Live-data invariants
# ---------------------------------------------------------------------------

def test_hazardous_aliases_are_still_present_and_inert(matcher):
    """Deliberately left in the map: the guard makes them inert, which keeps
    the blast-radius measurement clean. Removal would not help anyway --
    SUBPHRASE_CATALOG_MATCH re-derives 7141 from the catalog head."""
    with open(ALIAS, encoding="utf-8") as f:
        alias_map = json.load(f)
    for alias, code in HAZARDOUS_ALIASES.items():
        assert alias_map.get(alias) == code, alias
        assert matcher.match(alias)["method"] == "UNMATCHED", alias


def test_removing_the_aliases_would_not_have_helped(matcher):
    """Recorded as an executable fact, because it is the entire justification
    for guarding at the resolution layer instead of editing the alias map."""
    from nlp.entity_matcher import clean_culinary_query
    for phrase in ALIAS_STAGE_BLOCKED:
        cleaned = clean_culinary_query(phrase)
        best_idx, best_score = None, 0.0
        padded_q = f" {cleaned} "
        for norm_c, padded_c, c_len, idx in matcher.catalog_subphrase_items:
            if f"không {cleaned}" in norm_c or f"tách {cleaned}" in norm_c:
                continue
            if c_len >= 3 and padded_c in padded_q:
                score = c_len / len(cleaned)
                if score > best_score:
                    best_score, best_idx = score, idx
        assert best_idx is not None, phrase
        assert best_score >= 0.35, (phrase, best_score)
        assert matcher.catalog[best_idx]["code"] == "7141", phrase


def test_no_vegetable_stock_row_resolves_to_an_animal_identity(dataset_rows, catalog_by_code):
    """The post-remediation invariant: the guard's predicate must find nothing
    left to block in the live dataset."""
    offenders = [
        r for r in dataset_rows
        if (is_vegetable_stock_text(r["raw_text"], r["cleaned_name"])
            and _is_animal(catalog_by_code, r["master_ingredient_code"]))
    ]
    assert offenders == [], [
        (r["id"][:8], r["raw_text"], r["master_ingredient_name"]) for r in offenders
    ]


def test_the_eight_remediated_rows_hold_the_unmatched_contract(dataset_rows):
    """AGENTS.md §4: blank code/name, method UNMATCHED, null confidence, null
    nutrition -- and 0.0 is never the sentinel for any of them."""
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
        raw_text, cleaned_name = BLAST_RADIUS[prefix]
        assert row["raw_text"] == raw_text, prefix
        assert row["cleaned_name"] == cleaned_name, prefix
        assert float(row["estimated_weight_g"]) > 0, prefix
        assert (row["required_quantity"] or "").strip(), prefix
        assert (row["unit"] or "").strip(), prefix
        assert is_vegetable_stock_text(row["raw_text"], row["cleaned_name"]), prefix


def test_stale_cleaned_name_rows_are_recorded_not_repaired(dataset_rows):
    """Deferred (AGENTS.md §18). Four rows store a cleaned_name that today's
    parser no longer produces: raw text "Nước dùng rau củ ...", cleaned_name
    "nước dùng rau". This test pins the drift so the deferred task has a home
    -- and proves the guard does not depend on repairing it.

    Five rows carry cleaned_name "nước dùng rau", but only four are stale:
    81739420's raw text genuinely reads "Nước dùng rau 950 ml".
    """
    stale = {p for p, (raw, cleaned) in BLAST_RADIUS.items()
             if "rau củ" in raw.lower() and cleaned == "nước dùng rau"}
    assert len(stale) == 4
    assert BLAST_RADIUS["81739420"] == ("Nước dùng rau 950 ml", "nước dùng rau")
    by_prefix = {r["id"][:8]: r for r in dataset_rows if r["id"][:8] in stale}
    for prefix, row in sorted(by_prefix.items()):
        assert row["cleaned_name"] == "nước dùng rau", prefix
        assert "rau củ" in row["raw_text"].lower(), prefix
        # Detected via raw_text despite the lossy cleaned_name.
        assert is_vegetable_stock_text(None, row["cleaned_name"]) is True
        assert is_vegetable_stock_text(row["raw_text"], None) is True


def test_forward_protection_row_is_untouched(dataset_rows):
    """470f6222 was already UNMATCHED. The guard recognizes it; the remediation
    must not have written to it."""
    by_prefix = {r["id"][:8]: r for r in dataset_rows if r["id"][:8] in FORWARD_PROTECTION}
    assert set(by_prefix) == set(FORWARD_PROTECTION)
    for prefix, row in by_prefix.items():
        raw_text, cleaned_name = FORWARD_PROTECTION[prefix]
        assert row["raw_text"] == raw_text
        assert row["cleaned_name"] == cleaned_name
        assert row["match_method"] == "UNMATCHED"
        assert (row["master_ingredient_code"] or "") == ""
        assert is_vegetable_stock_text(row["raw_text"], row["cleaned_name"]) is True


def test_animal_broths_keep_their_identity(dataset_rows, catalog_by_code):
    """The 141 live rows still on 7141 are animal broths with explicit animal
    semantics, or plain unqualified "nước dùng". None may be collateral."""
    rows = [r for r in dataset_rows if (r["master_ingredient_code"] or "").strip() == "7141"]
    assert len(rows) == 141
    for r in rows:
        assert not is_vegetable_stock_text(r["raw_text"], r["cleaned_name"]), r["raw_text"]


def test_chay_rows_are_outside_this_blast_radius(dataset_rows):
    """The 6 "nước dùng chay" rows belong to the chay guard and stay UNMATCHED
    for that reason, not this one."""
    chay_stock = [r for r in dataset_rows
                  if normalize_vietnamese_text(r["cleaned_name"] or "") == "nước dùng chay"]
    assert len(chay_stock) == 6
    for r in chay_stock:
        assert r["match_method"] == "UNMATCHED"
        assert is_chay_text(r["raw_text"], r["cleaned_name"]) is True
        assert is_vegetable_stock_text(r["raw_text"], r["cleaned_name"]) is False


def test_dashi_rows_are_outside_the_blast_radius(dataset_rows):
    """Dashi is a fish stock; the veto keeps every dashi row out."""
    dashi = [r for r in dataset_rows
             if "dashi" in normalize_vietnamese_text(
                 f"{r['raw_text']} {r['cleaned_name']}")]
    assert len(dashi) == 14
    assert not any(is_vegetable_stock_text(r["raw_text"], r["cleaned_name"]) for r in dashi)


def test_no_20002_row_was_touched(dataset_rows):
    """20002 was explicitly rejected as a repoint target."""
    rows = [r for r in dataset_rows if (r["master_ingredient_code"] or "").strip() == "20002"]
    assert len(rows) == 358
    assert not any(is_vegetable_stock_text(r["raw_text"], r["cleaned_name"]) for r in rows)


def test_blast_radius_is_exactly_eight_rows(dataset_rows):
    """Nothing else in 63,943 rows may be inside this guard's predicate."""
    assert len(dataset_rows) == 63943
    detected = [r for r in dataset_rows
                if is_vegetable_stock_text(r["raw_text"], r["cleaned_name"])]
    prefixes = {r["id"][:8] for r in detected}
    assert prefixes == set(BLAST_RADIUS) | set(FORWARD_PROTECTION)
    assert all(r["match_method"] == "UNMATCHED" for r in detected)


def test_catalog_still_has_no_vegetable_stock_identity(catalog_by_code):
    """Why UNMATCHED is correct rather than a repoint, and the recorded
    catalog gap. If a vegetable-stock entry is ever added, this test fails and
    the guard's rows should be re-matched to it instead."""
    broths = {code: row["name_vi"] for code, row in catalog_by_code.items()
              if "nước dùng" in row["name_vi"].lower()}
    assert broths == {"7141": "Nước dùng", "20002": "Nước lọc (nước dùng nấu)"}
    assert catalog_by_code["7141"]["category_vi"] == "Thịt và sản phẩm chế biến"
