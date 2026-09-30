"""Original raw ingredient text reaching the green-mango guard on the crawler path.

crawler/post_processing.py resolves ingredients in batch over UNIQUE VOCABULARY,
not per row, and until now it called match_batch() with names only. The guard in
nlp/entity_matcher reads the ORIGINAL recipe line -- clean_culinary_query() and
the Small-LLM cleaning step both destroy the green evidence -- so on this path it
could only ever fire when a green marker happened to survive into the cleaned
name. For the 15 remediated rows whose stored cleaned_name is the bare "xoài",
that means it never fired at all: see
test_live_path_was_unguarded_without_raw_contexts below, which pins the exact
"before" behaviour this change fixes.

Threading raw text through a vocabulary-keyed batch needs one raw_context per
batch entry, but a cleaned name is shared by many raw lines. In the current
corpus 2536 of 9358 cleaned names have more than one distinct raw_text, and for
"xoài" the 18 variants DISAGREE about green evidence. The policy is therefore to
key the vocabulary on (cleaned_name, green_flag) -- see the `vocab_key` docs in
crawler/post_processing.py for why that is lossless rather than a heuristic.
The tests holding that policy are under "Duplicate cleaned names" below.

Scope: crawler post-processing behaviour only. Every run here writes to tmp_path.
Nothing reads, rewrites or re-derives processed/canonical data, the alias map, or
the stored Qwen cleaned_name values.
"""

import json

import pytest

from crawler.post_processing import GlobalRecipePostProcessor, vocab_key
from nlp.entity_matcher import (
    GREEN_MANGO_GUARD_REASON,
    RIPE_MANGO_CODE,
    VietnameseIngredientMatcher,
)

BARE_XOAI = "xoài"

# Real corpus lines, taken from data/interim/recipe_ingredients.json. All of
# these are stored with the bare cleaned_name "xoài", which is exactly why the
# guard cannot see their green evidence unless raw_text is threaded through.
GREEN_RAW_TEXTS = (
    "Xoài xanh 1 quả",
    "Xoài cát xanh: 1/2 trái",
    "Xoài keo 160g",
    "Xoài keo: 1 trái",
    "Xoài keo 1 quả nhỏ",
    "2 trái xoài non",
    "xoài sống",
)

# Also stored as bare "xoài", also real corpus lines, and deliberately NOT
# green: these keep today's verdict. They are the reason an arbitrary
# representative raw_context would be unsafe in either direction.
AMBIGUOUS_RAW_TEXTS = (
    "45 g xoài",
    "Xoài 1/2 quả",
    "Xoài: 1 trái",
    "Xoài",
)

RIPE_RAW_TEXTS = (
    "1 quả xoài chín",
    "Xoài chín 2 trái",
    "ĂN KÈM: xoài cát chín",
)

# cleaned_name -> (raw_text, expected master code or None for "just not UNMATCHED")
NON_MANGO_ROWS = {
    "thịt bò": ("500g thịt bò", "7003"),
    "cà rốt": ("2 củ cà rốt", "4007"),
    "cà chua": ("Cà chua 3 quả chín", None),
    "rau muống": ("Rau muống 1 bó", None),
}


@pytest.fixture(scope="module")
def shared_matcher():
    """One catalog load for the whole module; the matcher is stateless per call."""
    return VietnameseIngredientMatcher(device="cpu")


@pytest.fixture
def build_processor(tmp_path, monkeypatch, shared_matcher):
    """Run the real post-processor over a synthetic interim file, in tmp_path.

    Returns (result, recorded_batch_calls). Every output file lands under
    tmp_path, so no processed or canonical artefact is touched.
    """
    import crawler.post_processing as pp

    monkeypatch.setattr(pp, "VietnameseIngredientMatcher", lambda **kw: shared_matcher)

    def _build(rows):
        recipe = {
            "id": "r-1",
            "name": "Test recipe",
            "source_platform": "TEST",
            "source_url": "https://example.invalid/r-1",
            "description": None,
            "instructions": None,
            "media_url": None,
            "default_servings": 2,
            "estimated_cooking_minutes": 10,
            "tags": [],
            "ingredients": [
                {
                    "id": f"i-{n}",
                    "name": cleaned,
                    "raw_text": raw,
                    "quantity": 100.0,
                    "unit": "GRAM",
                    "unit_vi": "gram",
                    "preparation_note": None,
                }
                for n, (cleaned, raw) in enumerate(rows)
            ],
        }

        interim = tmp_path / "interim"
        interim.mkdir(exist_ok=True)
        (interim / "recipes_crawled_cleaned.json").write_text(
            json.dumps([recipe], ensure_ascii=False), encoding="utf-8"
        )

        calls = []
        real_match_batch = shared_matcher.match_batch

        def recording_match_batch(names, **kwargs):
            calls.append({"names": list(names), "raw_contexts": kwargs.get("raw_contexts")})
            return real_match_batch(names, **kwargs)

        monkeypatch.setattr(shared_matcher, "match_batch", recording_match_batch)

        processor = GlobalRecipePostProcessor(
            interim_dir=interim, output_dir=tmp_path / "out"
        )
        return processor.run(), calls

    return _build


def _by_raw_text(result):
    return {ing["raw_text"]: ing for ing in result["ingredients"]}


# ---------------------------------------------------------------------------
# The "before" state this change fixes
# ---------------------------------------------------------------------------

def test_live_path_was_unguarded_without_raw_contexts(shared_matcher):
    """Names alone -- the old call -- cannot guard a remediated row.

    Every one of these is stored with cleaned_name "xoài"; with no raw_context
    the guard has nothing green left to read and all of them reach ripe 5055.
    This is the regression the change closes, pinned so it cannot come back.
    """
    names = [BARE_XOAI] * len(GREEN_RAW_TEXTS)
    for res in shared_matcher.match_batch(names):
        assert res["method"] == "PRESET_ALIAS_MATCH"
        assert res["matched_item"]["code"] == RIPE_MANGO_CODE


# ---------------------------------------------------------------------------
# Green mango on the live crawler path
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("raw_text", GREEN_RAW_TEXTS)
def test_green_mango_row_is_unmatched_through_post_processing(build_processor, raw_text):
    result, _ = build_processor([(BARE_XOAI, raw_text)])
    row = _by_raw_text(result)[raw_text]
    assert row["match_method"] == "UNMATCHED"
    assert row["master_ingredient_code"] is None
    assert row["master_ingredient_name"] is None


def test_green_mango_row_never_carries_ripe_nutrition(build_processor):
    """The whole point of the guard: no borrowed 5055 numbers."""
    result, _ = build_processor([(BARE_XOAI, raw) for raw in GREEN_RAW_TEXTS])
    for row in result["ingredients"]:
        assert row["master_ingredient_code"] != RIPE_MANGO_CODE
        assert all(v is None for v in row["portion_nutrition"].values())


def test_unmatched_row_confidence_is_null_not_zero(build_processor):
    """An UNMATCHED row asserts "no master link", not a scored rejection --
    the contract in tests/test_unmatched_confidence_semantics.py. It also must
    not raise: the old `conf < 0.70` triage compared against None."""
    result, _ = build_processor([(BARE_XOAI, "Xoài xanh 1 quả")])
    assert result["ingredients"][0]["match_confidence"] is None


def test_guarded_row_goes_to_triage(build_processor):
    result, _ = build_processor([(BARE_XOAI, "Xoài keo 160g")])
    assert result["triage_count"] == 1
    assert result["aliases_learned"] == 0


def test_guard_verdict_names_its_reason(shared_matcher):
    res = shared_matcher.match_batch([BARE_XOAI], raw_contexts=["Xoài keo 160g"])[0]
    assert res["guard"] == GREEN_MANGO_GUARD_REASON


# ---------------------------------------------------------------------------
# Everything the guard must not touch
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("raw_text", AMBIGUOUS_RAW_TEXTS)
def test_ambiguous_bare_xoai_keeps_existing_behaviour(build_processor, raw_text):
    """These rows carry no green marker and still need their own review; this
    change must not pre-empt it in either direction."""
    result, _ = build_processor([(BARE_XOAI, raw_text)])
    row = _by_raw_text(result)[raw_text]
    assert row["master_ingredient_code"] == RIPE_MANGO_CODE
    assert row["match_method"] == "PRESET_ALIAS_MATCH"


@pytest.mark.parametrize("raw_text", RIPE_RAW_TEXTS)
def test_ripe_mango_still_resolves_to_5055(build_processor, raw_text):
    result, _ = build_processor([("xoài chín", raw_text)])
    row = _by_raw_text(result)[raw_text]
    assert row["master_ingredient_code"] == RIPE_MANGO_CODE
    assert row["match_method"] != "UNMATCHED"


def test_explicit_ripeness_overrides_a_marker_on_this_path(build_processor):
    """A ripeness marker beats a green one in the same line, cleaned name
    notwithstanding."""
    result, _ = build_processor([(BARE_XOAI, "Xoài cát xanh, chín tới: 1/2 trái")])
    assert result["ingredients"][0]["master_ingredient_code"] == RIPE_MANGO_CODE


@pytest.mark.parametrize(
    "cleaned,raw,code", [(k, v[0], v[1]) for k, v in NON_MANGO_ROWS.items()]
)
def test_non_mango_rows_are_untouched(build_processor, cleaned, raw, code):
    result, _ = build_processor([(cleaned, raw)])
    row = _by_raw_text(result)[raw]
    assert row["match_method"] != "UNMATCHED"
    if code is not None:
        assert row["master_ingredient_code"] == code


def test_guard_never_fires_on_a_non_mango_line(build_processor):
    """A green marker with no mango in the line is not evidence of anything."""
    rows = [
        ("hành lá", "hành lá thái nhỏ"),
        ("đu đủ", "Đu đủ xanh 200g"),
        ("chuối", "1 quả chuối sống"),
    ]
    result, _ = build_processor(rows)
    for row in result["ingredients"]:
        assert row["match_method"] != "UNMATCHED"


# ---------------------------------------------------------------------------
# Batch alignment
# ---------------------------------------------------------------------------

def test_raw_contexts_are_passed_to_match_batch(build_processor):
    _, calls = build_processor([(BARE_XOAI, "Xoài xanh 1 quả")])
    assert len(calls) == 1
    assert calls[0]["raw_contexts"] is not None


def test_every_query_is_paired_with_its_own_raw_context(build_processor):
    """Positional alignment, asserted pair by pair rather than by length."""
    rows = [
        ("thịt bò", "500g thịt bò"),
        (BARE_XOAI, "Xoài xanh 1 quả"),
        ("cà rốt", "2 củ cà rốt"),
        (BARE_XOAI, "45 g xoài"),
        ("xoài chín", "1 quả xoài chín"),
    ]
    _, calls = build_processor(rows)
    names, contexts = calls[0]["names"], calls[0]["raw_contexts"]

    assert len(names) == len(contexts)
    submitted = dict(zip(contexts, names))
    for cleaned, raw in rows:
        if raw in submitted:
            assert submitted[raw] == cleaned, f"{raw!r} was paired with the wrong query"


def test_batch_order_is_deterministic(build_processor):
    """A set-built vocabulary varies between processes (string hash
    randomisation), which would make both the batch and the chosen
    representative raw_context unreproducible."""
    rows = [(c, r) for c, (r, _) in NON_MANGO_ROWS.items()]
    rows += [(BARE_XOAI, raw) for raw in GREEN_RAW_TEXTS + AMBIGUOUS_RAW_TEXTS]
    _, first = build_processor(rows)
    _, second = build_processor(rows)
    assert first[0]["names"] == second[0]["names"]
    assert first[0]["raw_contexts"] == second[0]["raw_contexts"]


def test_batch_carries_no_duplicate_keys(build_processor):
    """Vocabulary batching still deduplicates; the split adds entries only
    where the green evidence actually disagrees."""
    rows = [(BARE_XOAI, raw) for raw in AMBIGUOUS_RAW_TEXTS]
    _, calls = build_processor(rows)
    assert calls[0]["names"] == [BARE_XOAI]


# ---------------------------------------------------------------------------
# Duplicate cleaned names with different raw contexts
# ---------------------------------------------------------------------------

def test_one_cleaned_name_with_disagreeing_contexts_splits(build_processor):
    """The core policy test. "xoài" is submitted once per green_flag, never
    collapsed onto a single arbitrary raw_context."""
    rows = [(BARE_XOAI, "Xoài xanh 1 quả"), (BARE_XOAI, "45 g xoài")]
    _, calls = build_processor(rows)
    names, contexts = calls[0]["names"], calls[0]["raw_contexts"]

    assert names == [BARE_XOAI, BARE_XOAI]
    assert set(contexts) == {"Xoài xanh 1 quả", "45 g xoài"}


def test_disagreeing_contexts_reach_different_verdicts_in_one_run(build_processor):
    """Both rows share the cleaned name "xoài" and are resolved in the SAME
    batch, yet each is judged on its own evidence."""
    rows = [(BARE_XOAI, "Xoài xanh 1 quả"), (BARE_XOAI, "45 g xoài")]
    result, _ = build_processor(rows)
    by_raw = _by_raw_text(result)

    assert by_raw["Xoài xanh 1 quả"]["match_method"] == "UNMATCHED"
    assert by_raw["45 g xoài"]["master_ingredient_code"] == RIPE_MANGO_CODE


def test_verdict_does_not_depend_on_row_order(build_processor):
    """No "first raw line wins": reversing the recipe must not move a verdict.
    This is what an arbitrary representative would have broken."""
    rows = [(BARE_XOAI, "Xoài keo 160g"), (BARE_XOAI, "Xoài 1/2 quả")]
    forward, _ = build_processor(rows)
    backward, _ = build_processor(list(reversed(rows)))

    def verdicts(result):
        return {
            raw: ing["master_ingredient_code"]
            for raw, ing in _by_raw_text(result).items()
        }

    assert verdicts(forward) == verdicts(backward)
    assert verdicts(forward) == {"Xoài keo 160g": None, "Xoài 1/2 quả": RIPE_MANGO_CODE}


def test_many_green_variants_share_one_batch_entry(build_processor):
    """Guard-equivalent raw lines collapse, as intended -- the split is on the
    boolean, not on the raw string, so the batch does not blow up."""
    rows = [(BARE_XOAI, raw) for raw in GREEN_RAW_TEXTS]
    result, calls = build_processor(rows)

    assert calls[0]["names"] == [BARE_XOAI]
    assert len(result["ingredients"]) == len(GREEN_RAW_TEXTS)
    assert all(ing["match_method"] == "UNMATCHED" for ing in result["ingredients"])


def test_non_mango_duplicates_still_collapse_to_one_entry(build_processor):
    """The split must not leak into unrelated vocabulary."""
    rows = [("cà rốt", "2 củ cà rốt"), ("cà rốt", "Cà rốt 100g"), ("cà rốt", "cà rốt xanh")]
    result, calls = build_processor(rows)

    assert calls[0]["names"].count("cà rốt") == 1
    codes = {ing["master_ingredient_code"] for ing in result["ingredients"]}
    assert codes == {"4007"}


def test_vocab_key_is_pure_and_falls_back_to_the_cleaned_name():
    """vocab_key mirrors match_batch's own `contexts[idx] or raw_name`."""
    assert vocab_key(BARE_XOAI, "Xoài xanh 1 quả") == (BARE_XOAI, True)
    assert vocab_key(BARE_XOAI, "45 g xoài") == (BARE_XOAI, False)
    assert vocab_key(BARE_XOAI, None) == (BARE_XOAI, False)
    assert vocab_key("xoài xanh", None) == ("xoài xanh", True)
    assert vocab_key("thịt bò", "500g thịt bò") == ("thịt bò", False)


# ---------------------------------------------------------------------------
# match_batch backward compatibility
# ---------------------------------------------------------------------------

def test_match_batch_without_raw_contexts_still_works(shared_matcher):
    names = ["thịt bò", "cà rốt", "xoài chín", "xoài xanh"]
    results = shared_matcher.match_batch(names)
    assert len(results) == len(names)
    assert [r["query"] for r in results] == names


def test_match_batch_falls_back_to_the_name_when_context_is_missing(shared_matcher):
    """A green marker surviving into the cleaned name still guards with no
    raw_contexts at all -- the only protection the crawler path used to have."""
    assert shared_matcher.match_batch(["xoài xanh"])[0]["method"] == "UNMATCHED"
    assert shared_matcher.match_batch(["xoài chín"])[0]["matched_item"]["code"] == RIPE_MANGO_CODE


def test_short_raw_contexts_list_is_padded_not_misaligned(shared_matcher):
    """Documented fallback: a shorter list must not shift contexts onto the
    wrong queries."""
    names = [BARE_XOAI, "xoài chín", "cà rốt"]
    results = shared_matcher.match_batch(names, raw_contexts=["Xoài xanh 1 quả"])
    assert results[0]["method"] == "UNMATCHED"
    assert results[1]["matched_item"]["code"] == RIPE_MANGO_CODE
    assert results[2]["matched_item"]["code"] == "4007"


def test_empty_batch_is_still_empty(shared_matcher):
    assert shared_matcher.match_batch([], raw_contexts=[]) == []
