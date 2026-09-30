"""A6: Qwen must not silently narrow the parser's cleaned_name.

The finding: the Qwen extraction prompt tells the model to drop "descriptors",
and the model reads identity/state qualifiers as descriptors. "Xoài keo 160g"
comes back as "xoài", "Tàu hũ ki khô 2 lá" as "tàu hũ ki", "Cải thảo muối 100
gr" as "cải thảo" -- each dropping the word that says WHICH food the row is.
Green mango becomes bare mango, dried bean-curd skin becomes fresh, preserved
napa becomes fresh napa.

Two design decisions this file pins down:

1. The baseline is RE-DERIVED from raw_text by VietnameseIngredientParser, not
   read from the row's stored cleaned_name. 34 live rows already store a
   damaged Qwen output; comparing a rerun against those would find the narrowed
   name "unchanged" and confirm the loss instead of catching it.

2. Rejecting a cleaned_name rewrite rejects ONLY the cleaned_name. The row's
   validated match, code, confidence and weight update still apply, because
   stage_qwen_update() already treats cleaned_name=None as "do not modify".
   The guard is a name-preservation rule, not a matching veto.

Today this is a forward-regression guard: every live row whose raw_text has an
unsafe cache entry already carries a master link, so Qwen recovery does not
fire on it at all (A3). See test_no_live_row_changes_behaviour_today.

No GPU/model is loaded here.
"""

import csv
import json
import unicodedata

import pytest

from nlp.ingredient_parser import VietnameseIngredientParser
from nlp.matching_integrity import stage_qwen_update
from nlp.qwen_matching import (
    CLEANED_NAME_PROTECTED_QUALIFIERS,
    build_mapper_rules,
    eligible_for_qwen_recovery,
    is_safe_cleaned_name_rewrite,
    map_clean_to_master,
    resolve_cleaned_name_update,
    resolve_qwen_row,
)

QWEN_CACHE = "data/interim/qwen_extracted_map.json"
MASTER_CSV = "data/processed/viendinhduong/master_ingredients_nutrition.csv"
INTERIM_ING = "data/interim/recipe_ingredients.csv"

CATALOG = {
    "5074": {"code": "5074", "name_vi": "Xoài", "energy_kcal": "60", "protein_g": "0.8",
             "fat_g": "0.4", "carbs_g": "15.0"},
    "3025": {"code": "3025", "name_vi": "Đậu phụ", "energy_kcal": "95", "protein_g": "10.9",
             "fat_g": "5.4", "carbs_g": "0.7"},
    "4016": {"code": "4016", "name_vi": "Cải bẹ trắng (cải thìa/thảo)", "energy_kcal": "13",
             "protein_g": "1.5", "fat_g": "0.2", "carbs_g": "1.2"},
    "4007": {"code": "4007", "name_vi": "Cà rốt", "energy_kcal": "41", "protein_g": "0.9",
             "fat_g": "0.2", "carbs_g": "9.6"},
}

# (parser baseline re-derived from raw_text, Qwen output). Every one of these is
# a contiguous parser-token run immediately followed by a protected qualifier.
UNSAFE_REWRITES = (
    ("Xoài keo", "xoài"),
    ("xoài xanh", "xoài"),
    ("xoài sống", "xoài"),
    ("xoài non", "xoài"),
    ("tàu hũ ki khô", "tàu hũ ki"),
    ("tàu hũ ki tươi", "tàu hũ ki"),
    ("cải thảo muối", "cải thảo"),
    ("Tôm càng xanh", "tôm càng"),
    ("Váng đậu tươi", "váng đậu"),
    ("Đậu bắp non", "đậu bắp"),
    ("măng tre già", "măng tre"),
)

SAFE_REWRITES = (
    # preparation verbs -- the whole point of the Qwen pass
    ("hành lá thái nhỏ", "hành lá"),
    ("hành lá cắt khúc", "hành lá"),
    ("cà rốt bào sợi", "cà rốt"),
    ("đu đủ ngâm chua", "đu đủ"),
    ("thịt ba chỉ thái mỏng", "thịt ba chỉ"),
    # units / quantities the parser left behind
    ("cải thảo 2 bắp", "cải thảo"),
    ("nấm hương 5 cái", "nấm hương"),
    # brand removal
    ("Aji-Quick Bột Chiên Giòn", "bột chiên giòn"),
    ("Knorr hạt nêm", "hạt nêm"),
    # colours are not protected: variety, not identity
    ("ớt sừng đỏ", "ớt sừng"),
    ("hành tím", "hành"),
    ("gạo nếp trắng", "gạo nếp"),
    ("cà tím", "cà"),
    ("bí đỏ", "bí"),
    # identical / widening / unchanged
    ("cải xoong", "cải xoong"),
    ("xoài", "xoài keo"),
    ("tàu hũ ki", "tàu hũ ki khô"),
)

# Rewords: the Qwen output is NOT a contiguous run of parser tokens, so the rule
# does not apply at all and existing behaviour is left exactly as it was -- even
# where a protected qualifier is present in the parser baseline.
NON_CONTIGUOUS_REWRITES = (
    ("xoài keo", "quả xoài"),
    ("xoài xanh", "mango"),
    ("Tàu hũ ki khô 2 lá", "váng đậu"),
    ("hành lá xanh cắt nhỏ", "hành hoa"),
    ("cải thảo muối", "kim chi"),
    ("thịt bò xào", "bò xào thịt"),        # reorder, not a contiguous run
    ("xoài keo", "xoài chín"),             # token added, not pure narrowing
)


@pytest.fixture(scope="module")
def parser():
    return VietnameseIngredientParser()


@pytest.fixture(scope="module")
def qwen_cache():
    with open(QWEN_CACHE, encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture(scope="module")
def master_dict():
    with open(MASTER_CSV, encoding="utf-8-sig", newline="") as f:
        return {r["code"]: r for r in csv.DictReader(f)}


@pytest.fixture(scope="module")
def interim_rows():
    with open(INTERIM_ING, encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


# ---------------------------------------------------------------------------
# The rule: a narrowing that drops a protected qualifier is unsafe
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("parser_name,qwen_name", UNSAFE_REWRITES)
def test_dropping_a_protected_qualifier_is_unsafe(parser_name, qwen_name):
    assert is_safe_cleaned_name_rewrite(parser_name, qwen_name) is False


@pytest.mark.parametrize("parser_name,qwen_name", SAFE_REWRITES)
def test_prep_unit_brand_and_colour_removal_is_safe(parser_name, qwen_name):
    assert is_safe_cleaned_name_rewrite(parser_name, qwen_name) is True


@pytest.mark.parametrize("parser_name,qwen_name", NON_CONTIGUOUS_REWRITES)
def test_a_reword_is_left_to_existing_behaviour(parser_name, qwen_name):
    """Not a contiguous narrowing -> the rule abstains rather than guessing."""
    assert is_safe_cleaned_name_rewrite(parser_name, qwen_name) is True


def test_qualifier_must_immediately_follow_the_matched_run():
    """Adjacency is the rule, stated on its own. "xanh" sitting two tokens away
    is not evidence that THIS narrowing dropped it, and firing on it would
    catch ordinary prep removal as collateral. The cost is visible and
    accepted: "xoài cát xanh" -> "xoài" is judged safe here, and stays covered
    by the raw-text ripeness guard in nlp/entity_matcher.py instead."""
    assert is_safe_cleaned_name_rewrite("xoài keo", "xoài") is False
    assert is_safe_cleaned_name_rewrite("xoài cát xanh", "xoài") is True


def test_any_occurrence_of_the_run_can_make_it_unsafe():
    """A repeated head token must not let one safe occurrence mask a lossy one."""
    assert is_safe_cleaned_name_rewrite("xoài thái xoài xanh", "xoài") is False


def test_a_trailing_run_has_no_following_token():
    """The run ends at the last parser token, so nothing was dropped after it."""
    assert is_safe_cleaned_name_rewrite("gỏi xoài xanh", "xoài xanh") is True


def test_empty_qwen_output_changes_nothing():
    assert is_safe_cleaned_name_rewrite("xoài keo", "") is True
    assert resolve_cleaned_name_update("Xoài keo 160g", "") is None
    assert resolve_cleaned_name_update("Xoài keo 160g", None) is None


def test_rule_is_case_and_unicode_normalisation_insensitive():
    """NFC + casefold on both sides: a decomposed or upper-case Qwen output is
    the same narrowing and must get the same verdict."""
    assert is_safe_cleaned_name_rewrite("XOÀI KEO", "xoài") is False
    assert is_safe_cleaned_name_rewrite("Xoài Keo", "XOÀI") is False
    decomposed = unicodedata.normalize("NFD", "Xoài keo")
    assert decomposed != "Xoài keo"
    assert is_safe_cleaned_name_rewrite(decomposed, "xoài") is False
    assert is_safe_cleaned_name_rewrite("xoài keo", unicodedata.normalize("NFD", "xoài")) is False


def test_punctuation_is_not_a_token():
    assert is_safe_cleaned_name_rewrite("xoài keo, gọt vỏ", "xoài") is False
    assert is_safe_cleaned_name_rewrite("Xoài keo : 100g", "xoài") is False


# ---------------------------------------------------------------------------
# The protected set: exactly the reviewed words, and nothing adjacent to them
# ---------------------------------------------------------------------------

def test_protected_qualifier_set_is_exactly_the_reviewed_words():
    assert set(CLEANED_NAME_PROTECTED_QUALIFIERS) == {
        "xanh", "chín", "sống", "non", "già", "khô", "tươi", "muối", "keo", "tượng",
    }


@pytest.mark.parametrize("word", ["thái", "ngâm", "bào", "luộc", "nướng", "băm", "cắt",
                                  "đỏ", "vàng", "tím", "trắng", "nâu", "đen"])
def test_excluded_words_are_not_protected(word):
    """Prep verbs and colours stay out: "thái" is also the slicing verb (see
    tests/test_green_mango_ripeness_guard.py), and a colour qualifies variety
    rather than food identity. Dropping either is what the Qwen pass is for."""
    assert word not in CLEANED_NAME_PROTECTED_QUALIFIERS
    assert is_safe_cleaned_name_rewrite(f"hành lá {word}", "hành lá") is True


# ---------------------------------------------------------------------------
# The baseline is re-derived from raw_text, never read from the stored row
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("raw_text,qwen_name", [
    ("Xoài keo 160g", "xoài"),
    ("Xoài keo: 1 trái", "xoài"),
    ("Xoài keo : 100g", "xoài"),
    ("2 trái xoài non", "xoài"),
    ("xoài xanh", "xoài"),
    ("xoài sống", "xoài"),
    ("Tàu hũ ki khô 2 lá", "tàu hũ ki"),
    ("Tàu hũ ki tươi 200g", "tàu hũ ki"),
    ("Cải thảo muối 100 gr", "cải thảo"),
    ("1 muỗng cải thảo muối khô", "cải thảo"),
    ("Tôm càng xanh 500 gr", "tôm càng"),
    ("Váng đậu tươi 4 miếng", "váng đậu"),
])
def test_lossy_rewrite_rejected_from_raw_text(raw_text, qwen_name):
    assert resolve_cleaned_name_update(raw_text, qwen_name) is None


@pytest.mark.parametrize("raw_text,qwen_name", [
    ("1 bó cải xoong", "cải xoong"),
    ("hành lá thái nhỏ", "hành lá"),
    ("1 chén bắp cải bào nhuyễn", "bắp cải"),
    ("Aji-Quick Bột Chiên Giòn 100g", "bột chiên giòn"),
    ("1 củ  carrot", "carrot"),
    ("2 quả Cà chua", "cà chua"),
])
def test_safe_rewrite_passes_through_from_raw_text(raw_text, qwen_name):
    assert resolve_cleaned_name_update(raw_text, qwen_name) == qwen_name


def test_baseline_ignores_an_already_damaged_stored_cleaned_name():
    """The load-bearing decision. This row's stored cleaned_name is ALREADY the
    narrowed "xoài" from a historical Qwen run; comparing against it would see
    no change and re-publish the loss. Re-deriving from raw_text still catches
    the dropped cultivar."""
    row = {
        "raw_text": "Xoài keo 160g",
        "cleaned_name": "xoài",                       # historical damage
        "master_ingredient_code": None,
        "master_ingredient_name": None,
        "match_method": "UNMATCHED",
        "match_confidence": None,
    }
    assert is_safe_cleaned_name_rewrite(row["cleaned_name"], "xoài") is True
    assert resolve_cleaned_name_update(row["raw_text"], "xoài") is None


@pytest.mark.parametrize("raw_text", ["Xoài keo 160g", "Tàu hũ ki tươi 200g", "Cải thảo muối 100 gr"])
def test_parser_baseline_is_what_the_parser_actually_returns(parser, raw_text):
    """The helper must read the same baseline the production parser produces,
    not a hand-written approximation of it: drop the trailing qualifier from
    the parser's OWN output and the result is rejected."""
    name = parser.parse(raw_text).name
    narrowed = " ".join(name.split()[:-1])
    assert is_safe_cleaned_name_rewrite(name, narrowed) is False
    assert resolve_cleaned_name_update(raw_text, narrowed) is None


def test_injected_parser_is_used(parser):
    assert resolve_cleaned_name_update("Xoài keo 160g", "xoài", parser=parser) is None
    assert resolve_cleaned_name_update("1 bó cải xoong", "cải xoong", parser=parser) == "cải xoong"


# ---------------------------------------------------------------------------
# Rejecting cleaned_name must not reject the match, the code or the weight
# ---------------------------------------------------------------------------

def test_match_code_and_weight_still_apply_when_cleaned_name_is_rejected():
    row = {"raw_text": "Xoài keo 160g", "cleaned_name": "xoài keo",
           "master_ingredient_code": None, "master_ingredient_name": None,
           "match_method": "UNMATCHED", "match_confidence": None,
           "estimated_weight_g": "0.0"}
    rejected = resolve_cleaned_name_update(row["raw_text"], "xoài")
    assert rejected is None

    updates = resolve_qwen_row(row, CATALOG, 160.0, ("5074", "Xoài", "QWEN_LLM_MATCH"), rejected)
    assert updates["master_ingredient_code"] == "5074"
    assert updates["master_ingredient_name"] == "Xoài"
    assert updates["match_method"] == "QWEN_LLM_MATCH"
    assert updates["match_confidence"] == "0.98"
    assert updates["estimated_weight_g"] == "160.0"
    assert updates["calories"] == "96.0"


def test_rejected_cleaned_name_is_absent_from_the_patch():
    """"do not modify" must mean absent, not present-and-None: a None in the
    patch would blank the column on r.update(updates)."""
    updates = resolve_qwen_row(
        {"master_ingredient_code": None, "master_ingredient_name": None,
         "match_method": "UNMATCHED", "match_confidence": None},
        CATALOG, 100.0, ("3025", "Đậu phụ", "QWEN_LLM_MATCH"), None,
    )
    assert "cleaned_name" not in updates


def test_cleaned_name_none_leaves_the_existing_value_untouched():
    row = {"raw_text": "Tàu hũ ki khô 2 lá", "cleaned_name": "tàu hũ ki khô",
           "master_ingredient_code": None, "master_ingredient_name": None,
           "match_method": "UNMATCHED", "match_confidence": None}
    updates = resolve_qwen_row(row, CATALOG, 40.0, ("3025", "Đậu phụ", "QWEN_LLM_MATCH"), None)
    row.update(updates)
    assert row["cleaned_name"] == "tàu hũ ki khô"
    assert row["master_ingredient_code"] == "3025"


def test_accepted_cleaned_name_is_still_written():
    """The negative control: the guard must not have disabled the feature."""
    row = {"raw_text": "2 quả cà rốt to", "cleaned_name": "cà rốt to",
           "master_ingredient_code": None, "master_ingredient_name": None,
           "match_method": "UNMATCHED", "match_confidence": None}
    accepted = resolve_cleaned_name_update(row["raw_text"], "cà rốt")
    updates = resolve_qwen_row(row, CATALOG, 100.0, ("4007", "Cà rốt", "QWEN_LLM_MATCH"), accepted)
    assert updates["cleaned_name"] == "cà rốt"


def test_rejection_is_independent_of_candidate_validation():
    """Two orthogonal gates: a rejected cleaned_name does not rescue a dangling
    candidate, and a dangling candidate does not change the cleaned_name
    verdict. Only the weight survives."""
    row = {"master_ingredient_code": None, "master_ingredient_name": None,
           "match_method": "UNMATCHED", "match_confidence": None}
    updates = resolve_qwen_row(row, CATALOG, 55.0, ("99999", "Ghost", "QWEN_LLM_MATCH"), None)
    assert "master_ingredient_code" not in updates
    assert "cleaned_name" not in updates
    assert updates["estimated_weight_g"] == "55.0"


def test_stage_qwen_update_contract_for_none_is_unchanged():
    """matching_integrity.py was deliberately not modified; this pins the
    behaviour the guard leans on."""
    row = {"cleaned_name": "xoài keo"}
    fields = {"master_ingredient_code": "5074", "master_ingredient_name": "Xoài",
              "match_method": "QWEN_LLM_MATCH", "match_confidence": "0.98"}
    assert "cleaned_name" not in stage_qwen_update(row, CATALOG, 10.0, fields, None)
    assert stage_qwen_update(row, CATALOG, 10.0, fields, "xoài")["cleaned_name"] == "xoài"


# ---------------------------------------------------------------------------
# The green mango guard keeps working, and this rule does not overlap it
# ---------------------------------------------------------------------------

GREEN_MANGO_RAW_TEXTS = (
    "1 quả xoài keo xanh",
    "1/2 quả Xoài xanh",
    "2 trái xoài non",
    "Xoài keo 1 quả",
    "Xoài keo 1 trái",
    "Xoài keo 1/4 trái",
    "Xoài keo 160g",
    "Xoài keo : 100g",
    "Xoài keo: 1 trái",
    "Xoài sống 100g Cắt que nhỏ cỡ đầu đũa",
    "Xoài xanh 1 quả",
    "Xoài xanh 100g",
    "xoài sống",
    "xoài xanh",
)


@pytest.mark.parametrize("raw_text", GREEN_MANGO_RAW_TEXTS)
def test_green_mango_evidence_is_never_narrowed_away(raw_text):
    assert resolve_cleaned_name_update(raw_text, "xoài") is None


def test_ripe_mango_qualifier_is_protected_too():
    """Symmetry: "chín" is as load-bearing as "xanh". Narrowing a ripe row to
    bare "xoài" would drop the one word that makes 5055 the right answer."""
    assert resolve_cleaned_name_update("Xoài chín 1 quả", "xoài") is None


def test_this_rule_does_not_decide_matching_for_mango():
    """Scope line: the ripeness guard lives in nlp/entity_matcher.py and reads
    raw_text at resolution time. This rule only ever decides what is written to
    cleaned_name -- it neither adds nor removes a mango match."""
    from nlp.entity_matcher import is_green_mango_text

    assert is_green_mango_text("xoài bào sợi") is False           # unchanged
    assert is_safe_cleaned_name_rewrite("xoài bào sợi", "xoài") is True
    assert is_green_mango_text("xoài thái lát") is False          # unchanged
    assert is_safe_cleaned_name_rewrite("xoài thái lát", "xoài") is True


def test_cultivar_thai_is_not_pulled_into_the_protected_set():
    """"thái" is green evidence for the MATCHER (cultivar, adjacency-checked)
    but is not a protected cleaned_name qualifier here, because the same token
    is the slicing verb and this rule has no adjacency evidence to tell them
    apart. Deliberate asymmetry; flip this test if that ever changes."""
    from nlp.entity_matcher import is_green_mango_text

    assert is_green_mango_text("1 trái xoài Thái") is True
    assert is_safe_cleaned_name_rewrite("xoài Thái", "xoài") is True


# ---------------------------------------------------------------------------
# Measured impact on the live cache, pinned
# ---------------------------------------------------------------------------

def test_measured_cache_impact(qwen_cache, parser):
    unsafe = {
        raw: out for raw, out in qwen_cache.items()
        if not is_safe_cleaned_name_rewrite(parser.parse(raw).name, out)
    }
    mango = {raw for raw in unsafe if "xoài" in raw.casefold()}
    assert len(qwen_cache) == 935
    assert len(unsafe) == 31
    assert len(mango) == 10
    assert len(unsafe) - len(mango) == 21


def test_no_live_row_changes_behaviour_today(qwen_cache, master_dict, interim_rows, parser):
    """This is a forward guard, not a data fix: every row whose raw_text has an
    unsafe cache entry already carries a master link, so A3 stops Qwen recovery
    before the cleaned_name question is even asked. If this ever fails, a rerun
    would genuinely change rows and the change needs re-review."""
    unsafe = {
        raw for raw, out in qwen_cache.items()
        if not is_safe_cleaned_name_rewrite(parser.parse(raw).name, out)
    }
    active, _ = build_mapper_rules(master_dict)
    would_change = [
        r for r in interim_rows
        if (r.get("raw_text") or "").strip() in unsafe
        and eligible_for_qwen_recovery(r)
        and all(map_clean_to_master(qwen_cache[(r.get("raw_text") or "").strip()], active))
    ]
    assert would_change == []


def test_future_risk_surface_if_disabled_mapper_rules_are_repaired(qwen_cache, master_dict, parser):
    """20 of the 49 hard-coded mapper rules are still disabled by A1
    catalog-drift validation, after Batch 1 repaired 8 of them (19 -> 27 active)
    and Batch 2 repaired 2 more (27 -> 29). Repairing the remaining 20 is what
    would re-arm the rest of the unsafe population, which is why this guard went
    in before that work.

    Batch 1 moved resolvable_now 5 -> 9: the four extra are unsafe cache
    entries under the newly active "hành lá"/"cải thảo" rules. That is the
    guard doing its job, not a regression -- the cleaned_name for those rows is
    still rejected by is_safe_cleaned_name_rewrite, and
    test_no_live_row_changes_behaviour_today proves A3 keeps them untouched.

    Batch 2 moved NEITHER number: none of the 31 unsafe-rewrite cache entries is
    a tiêu or chả lụa phrase, so re-activating those two rules added nothing to
    this risk surface. Only the active/disabled split shifted."""
    unsafe = {
        raw: out for raw, out in qwen_cache.items()
        if not is_safe_cleaned_name_rewrite(parser.parse(raw).name, out)
    }
    active, disabled = build_mapper_rules(master_dict)
    assert len(active) == 29
    assert len(disabled) == 20

    full = [(terms, code, name) for terms, code, name, _ in disabled] + active
    resolvable_now = {raw for raw, out in unsafe.items() if all(map_clean_to_master(out, active))}
    resolvable_repaired = {raw for raw, out in unsafe.items() if all(map_clean_to_master(out, full))}
    assert len(resolvable_now) == 9
    assert len(resolvable_repaired) == 30
    assert resolvable_now < resolvable_repaired


def test_historical_damage_is_visible_and_left_alone(interim_rows, parser):
    """The 34 rows the rule would have prevented. This task does not repair
    them; the count is asserted so a silent data change is impossible."""
    damaged = [
        r for r in interim_rows
        if not is_safe_cleaned_name_rewrite(
            parser.parse(r.get("raw_text") or "").name, r.get("cleaned_name") or ""
        )
    ]
    assert len(damaged) == 34
    assert all(r["match_method"] == "QWEN_LLM_MATCH" for r in damaged)
