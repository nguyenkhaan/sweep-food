"""Batch 1 of the disabled-Qwen-mapper-rule audit: 8 zero-risk rule repairs.

Each repair re-points a rule that A1 catalog-drift validation had disabled onto
the code/name pair that identifies the SAME food in the catalog as it stands
today. Nothing about the A1 guard itself is relaxed: every repaired rule has to
earn its "active" status by passing the identity check against the live
master_ingredients_nutrition.csv, exactly like every other rule.

What these tests pin down:
  * the 8 repaired rules pass live-catalog validation, and their hard-coded
    (code, name) is character-for-character the catalog's current identity;
  * the active/disabled split moved 19/30 -> 27/22 and no further -- measured
    against a rule table with Batch 2 reverted, so this stays a Batch-1 claim
    even now that Batch 2 has taken the split on to 29/20;
  * the rules Batch 1 deliberately did NOT touch are still disabled -- both the
    3 REMOVE rules (xoai, chanh, tau hu ki) and the 17 other disabled rules that
    no later batch has claimed, which must never come back through this door;
  * matching is still exact-substring only, with no fuzzy fallback;
  * rule ORDER did not regress: a repaired rule does not steal a phrase that
    belongs to a different rule.
"""

import csv
import json
from pathlib import Path

import pytest

from nlp.qwen_matching import (
    _QWEN_MAPPER_EXCLUSIONS,
    _QWEN_MAPPER_RULES,
    _REVIEWED_NO_CATALOG_TARGET_RAW,
    build_mapper_rules,
    eligible_for_qwen_recovery,
    map_clean_to_master,
    qwen_candidate_eligibility,
)

ROOT = Path(__file__).resolve().parents[1]
MASTER_CSV = ROOT / "data" / "processed" / "viendinhduong" / "master_ingredients_nutrition.csv"
QWEN_CACHE = ROOT / "data" / "interim" / "qwen_extracted_map.json"
PROCESSED_ING = ROOT / "data" / "processed" / "recipes" / "recipe_ingredients.csv"

# Batch 2 re-pointed these two rules AFTER Batch 1 landed. Every Batch-1
# measurement below reverts them first, so what this file asserts is the effect
# of Batch 1 alone and does not drift as later batches land.
BATCH2_REPAIRS = {
    ("tiêu",): ("13004", "Hạt tiêu"),
    ("chả huế", "chả lụa"): ("7069", "Giò lụa"),
}
BATCH2_PRE_REPAIR = {
    ("tiêu",): ("13018", "Hạt tiêu"),
    ("chả huế", "chả lụa"): ("7067", "Giò lụa"),
}

# The 8 approved Batch 1 repairs: rule terms -> the (code, name) they now carry.
BATCH1_REPAIRS = {
    ("hành lá", "hành hoa"): ("4038", "Hành lá (hành hoa)"),
    ("cải thảo", "bắp cải thảo"): ("4109", "Rau cải thảo"),
    ("nấm rơm",): ("4129", "Nấm rơm"),
    ("nấm bào ngư", "nấm sò"): ("20004", "Nấm bào ngư (nấm sò)"),
    ("nấm đùi gà",): ("20007", "Nấm đùi gà"),
    ("thanh long",): ("5044", "thanh long"),
    ("cá nục",): ("8020", "Cá nục"),
    # Code deliberately unchanged; only the stored target name was corrected to
    # the catalog's current spelling of the same fish (thac lac -> that lat).
    ("cá thác lác",): ("8013", "Cá thát lát"),
}

# Rules whose audit verdict was REMOVE: the hard-coded target is the wrong food,
# not a drifted label, so no code/name repair can make them safe.
REMOVE_RULE_TERMS = {
    ("xoài",),
    ("chanh",),
    ("tàu hũ ki", "tàu hủ ki", "váng đậu", "mì căn", "ham chay", "giò sống chay"),
}

# Every rule outside Batch 1 that is still disabled and is NOT a REMOVE verdict.
# This is a union of three audit verdicts, not one of them (2 + 14 + 3 = 19):
#
#   NEEDS_REVIEW (14)
#       húng lủi / húng quế / rau húng      cua biển
#       tắc / quất                          cải xanh / cải ngồng
#       cải con / cải mầm / cải thìa        ngò gai / mùi tàu
#       bắp cải                             nấm hương / nấm đông cô
#       cải xoong                           bạc hà
#       hành tím / hành khô / hành củ / hành trắng / đầu hành
#       cá cơm khô / cá cơm
#       đậu que / đậu cô ve
#       tôm càng / tôm đồng
#
#   OBSOLETE (3)
#       đậu đũa
#       nấm kim châm
#       chà là
#
# The 2 guarded SAFE_REMAP rules (tiêu, chả huế / chả lụa) were also in this
# set until Batch 2 repaired them; they now live in BATCH2_REPAIRS, which is why
# 14 + 3 = 17 terms are listed below rather than the original 19.
#
# Grouped together here only because the assertion is identical for all of them
# -- they must stay disabled until their own batch reviews them. The set is
# deliberately verdict-agnostic; do not read a verdict off this name, and do not
# infer one from catalog shape -- the verdicts above come from the rule audit.
STILL_DISABLED_NON_REMOVE_RULE_TERMS = {
    ("bắp cải",),
    ("cải con", "cải mầm", "cải thìa"),
    ("cải xoong",),
    ("cải xanh", "cải ngồng"),
    ("đậu que", "đậu cô ve"),
    ("đậu đũa",),
    ("hành tím", "hành khô", "hành củ", "hành trắng", "đầu hành"),
    ("ngò gai", "mùi tàu"),
    ("bạc hà",),
    ("húng lủi", "húng quế", "rau húng"),
    ("nấm hương", "nấm đông cô"),
    ("nấm kim châm",),
    ("tắc", "quất"),
    ("chà là",),
    ("cá cơm khô", "cá cơm"),
    ("tôm càng", "tôm đồng"),
    ("cua biển",),
}


@pytest.fixture(scope="module")
def master_dict():
    with open(MASTER_CSV, encoding="utf-8-sig", newline="") as f:
        return {r["code"]: r for r in csv.DictReader(f)}


@pytest.fixture(scope="module")
def split(master_dict):
    return build_mapper_rules(master_dict)


def _table_with(overrides):
    """The live rule table with `overrides` (terms -> (code, name)) applied."""
    return tuple(
        (terms, *overrides[terms]) if terms in overrides else (terms, code, name)
        for terms, code, name in _QWEN_MAPPER_RULES
    )


def _validate(table, master_dict):
    """A1 identity validation, re-implemented over an arbitrary table."""
    return [
        (terms, code, name) for terms, code, name in table
        if code in master_dict
        and master_dict[code]["name_vi"].strip().casefold() == name.strip().casefold()
    ]


@pytest.fixture(scope="module")
def batch1_split(master_dict):
    """The split as it stood at the end of Batch 1: Batch 2 reverted."""
    table = _table_with(BATCH2_PRE_REPAIR)
    active = _validate(table, master_dict)
    return active, [rule for rule in table if rule not in active]


@pytest.fixture(scope="module")
def batch1_active(batch1_split):
    return batch1_split[0]


@pytest.fixture(scope="module")
def active_terms(split):
    return {terms for terms, _, _ in split[0]}


@pytest.fixture(scope="module")
def disabled_terms(split):
    return {terms for terms, _, _, _ in split[1]}


# ---------------------------------------------------------------------------
# The 8 repairs pass live-catalog validation with exact identity
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("terms", sorted(BATCH1_REPAIRS, key=str))
def test_repaired_rule_is_active_against_live_catalog(terms, active_terms):
    assert terms in active_terms


@pytest.mark.parametrize("terms,expected", sorted(BATCH1_REPAIRS.items(), key=str))
def test_repaired_rule_carries_the_approved_code_and_name(terms, expected):
    hard_coded = {t: (c, n) for t, c, n in _QWEN_MAPPER_RULES}
    assert hard_coded[terms] == expected


@pytest.mark.parametrize("terms,expected", sorted(BATCH1_REPAIRS.items(), key=str))
def test_repaired_rule_name_is_the_catalogs_current_identity(terms, expected, master_dict):
    """Byte-exact, not merely case/whitespace-equal under the A1 normaliser.

    build_mapper_rules() compares casefolded/whitespace-collapsed names, so a
    repair could pass A1 while still storing a differently-spelled label into
    master_ingredient_name. Batch 1 stores the catalog string verbatim.
    """
    code, name = expected
    assert code in master_dict, f"{code} is not in the live catalog"
    assert master_dict[code]["name_vi"] == name


def test_ca_thac_lac_keeps_its_code_and_only_the_name_was_corrected():
    hard_coded = {t: (c, n) for t, c, n in _QWEN_MAPPER_RULES}
    code, name = hard_coded[("cá thác lác",)]
    assert code == "8013"
    assert name == "Cá thát lát"


# ---------------------------------------------------------------------------
# The split moved exactly 19/30 -> 27/22
# ---------------------------------------------------------------------------

def test_rule_table_size_is_unchanged():
    assert len(_QWEN_MAPPER_RULES) == 49


def test_active_and_disabled_counts_after_batch1(batch1_split):
    """Batch 1's own split, measured with Batch 2 reverted."""
    active, disabled = batch1_split
    assert len(active) == 27
    assert len(disabled) == 22
    assert len(active) + len(disabled) == len(_QWEN_MAPPER_RULES)


def test_batch1_is_the_only_thing_that_became_active(active_terms):
    """19 rules were active before; the 8 repairs are the entire Batch-1 delta.

    Guards against a repair accidentally re-activating an unrelated rule by
    colliding with a code another rule also hard-codes. Batch 2's own 2 rules
    are named explicitly rather than folded in, so a THIRD rule slipping into
    the active set still fails here.
    """
    previously_active = {
        ("đậu bắp",), ("củ sen",), ("ngó sen",), ("cà bi", "cà chua"),
        ("cà rốt", "carrot"), ("rau mùi", "ngò rí", "ngò"),
        ("nấm mỡ", "nấm nâu", "nấm chân gà"),
        ("nạc dăm", "thịt nạc heo", "thịt nạc"), ("bắp bò",), ("thịt bò",),
        ("thịt gà", "chân gà"), ("cá cam",), ("bột chiên giòn",),
        ("bột chiên xù",), ("bột bánh xèo",), ("ớt xiêm", "ớt sừng", "ớt"),
        ("nước ấm", "nước vo gạo", "nước lọc"),
        ("bột màu điều", "hạt điều đỏ", "dầu điều"),
        ("lá cà ri", "hoa hồi", "đại hồi"),
    }
    assert len(previously_active) == 19
    assert active_terms == previously_active | set(BATCH1_REPAIRS) | set(BATCH2_REPAIRS)


# ---------------------------------------------------------------------------
# Unrelated rules stay disabled
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("terms", sorted(REMOVE_RULE_TERMS, key=str))
def test_remove_verdict_rules_remain_disabled(terms, disabled_terms):
    assert terms in disabled_terms


@pytest.mark.parametrize("terms", sorted(STILL_DISABLED_NON_REMOVE_RULE_TERMS, key=str))
def test_still_disabled_non_remove_rules_remain_disabled(terms, disabled_terms):
    assert terms in disabled_terms


def test_disabled_set_is_exactly_the_untouched_rules(disabled_terms):
    assert disabled_terms == REMOVE_RULE_TERMS | STILL_DISABLED_NON_REMOVE_RULE_TERMS


@pytest.mark.parametrize("phrase", ["xoài", "xoài keo", "xoài xanh", "chanh",
                                    "nước cốt chanh", "tàu hũ ki", "váng đậu", "mì căn"])
def test_remove_verdict_phrases_stay_unresolved(phrase, split):
    active, _ = split
    assert map_clean_to_master(phrase, active) == (None, None)


# ---------------------------------------------------------------------------
# No fuzzy fallback was introduced
# ---------------------------------------------------------------------------

def test_matching_is_exact_substring_only(split):
    """A near-miss must NOT resolve. If a fuzzy/edit-distance fallback is ever
    added, these unresolve-assertions are the first thing to fail."""
    active, _ = split
    for near_miss in ("hanh la", "hành l", "cai thao", "nam rom", "thanhlong",
                      "ca nuc", "nam bao ngu", "cá thát lát"):
        assert map_clean_to_master(near_miss, active) == (None, None), near_miss


def test_unknown_phrase_returns_none_rather_than_nearest_rule(split):
    active, _ = split
    assert map_clean_to_master("bánh mì sandwich nguyên cám", active) == (None, None)
    assert map_clean_to_master("", active) == (None, None)
    assert map_clean_to_master(None, active) == (None, None)


def test_batch1_added_no_exclusions_of_its_own():
    """The two pre-existing A2 exclusions are untouched, and the only keys that
    have since joined them are Batch 2's -- keyed on Batch 2's own rule terms,
    so neither can alter how a Batch-1 rule resolves."""
    assert _QWEN_MAPPER_EXCLUSIONS[("cải xanh", "cải ngồng")] == ("bông cải xanh",)
    assert _QWEN_MAPPER_EXCLUSIONS[("tắc", "quất")] == ("việt quất",)
    assert set(_QWEN_MAPPER_EXCLUSIONS) == {
        ("cải xanh", "cải ngồng"), ("tắc", "quất"),
    } | set(BATCH2_REPAIRS)
    assert not set(_QWEN_MAPPER_EXCLUSIONS) & set(BATCH1_REPAIRS)


# ---------------------------------------------------------------------------
# Ordering: a repaired rule must not steal an unrelated phrase
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("phrase,expected", [
    # The repaired rules resolve their own phrases...
    ("hành lá", ("4038", "Hành lá (hành hoa)")),
    ("hành lá chẻ", ("4038", "Hành lá (hành hoa)")),
    ("lá cải thảo", ("4109", "Rau cải thảo")),
    ("bắp cải thảo", ("4109", "Rau cải thảo")),
    ("nấm rơm", ("4129", "Nấm rơm")),
    ("nấm bào ngư", ("20004", "Nấm bào ngư (nấm sò)")),
    ("nấm sò", ("20004", "Nấm bào ngư (nấm sò)")),
    ("nấm đùi gà", ("20007", "Nấm đùi gà")),
    ("thanh long", ("5044", "thanh long")),
    ("cá nục", ("8020", "Cá nục")),
    ("cá thác lác", ("8013", "Cá thát lát")),
])
def test_repaired_rule_resolves_its_own_phrase(phrase, expected, split):
    active, _ = split
    assert map_clean_to_master(phrase, active) == expected


@pytest.mark.parametrize("phrase", [
    "nấm kim châm",     # own rule still disabled -- "nấm rơm" must not claim it
    "nấm hương",        # own rule still disabled
    "nấm đông cô",      # own rule still disabled
    "chà là",           # shares code 5044 with thanh long; rule still disabled
    "bắp cải",          # "cải thảo" must not claim plain cabbage
    "cải thìa",         # own rule still disabled
    "cải xanh",         # own rule still disabled
    "bông cải xanh",    # A2 exclusion, must stay unresolved
    "hành tím",         # own rule still disabled
    "hành khô",         # own rule still disabled
    "cá cơm",           # own rule still disabled
])
def test_repaired_rule_does_not_steal_an_unrelated_phrase(phrase, split):
    active, _ = split
    assert map_clean_to_master(phrase, active) == (None, None), phrase


def test_cai_thao_is_still_checked_before_bap_cai():
    """A2 ordering: "bắp cải thảo" contains "bắp cải" as a substring, so the
    napa-cabbage rule has to come first. The repair kept that order."""
    order = [terms for terms, _, _ in _QWEN_MAPPER_RULES]
    assert order.index(("cải thảo", "bắp cải thảo")) < order.index(("bắp cải",))


def test_repaired_rules_kept_their_original_positions():
    """Batch 1 changed code/name only. A reorder would change which rule wins a
    substring collision, so position is asserted rather than assumed."""
    order = [terms for terms, _, _ in _QWEN_MAPPER_RULES]
    assert order[0] == ("hành lá", "hành hoa")
    assert order[1] == ("cải thảo", "bắp cải thảo")
    assert order.index(("nấm rơm",)) < order.index(("nấm kim châm",))
    assert order.index(("thanh long",)) < order.index(("chà là",))


# ---------------------------------------------------------------------------
# Measured impact on the current processed data
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def old_active(master_dict):
    """The active rule set as it stood immediately before Batch 1.

    Batch 2's two rules are reverted as well, so "before" really is before
    Batch 1 and the measured delta below belongs to Batch 1 alone. Both pre-
    repair targets were already failing A1 anyway, so reverting them changes
    the disabled list, not this active list.
    """
    pre_repair = {
        ("hành lá", "hành hoa"): ("4019", "Hành hoa, tươi"),
        ("cải thảo", "bắp cải thảo"): ("4016", "Cải bẹ trắng (cải thìa/thảo)"),
        ("nấm rơm",): ("4057", "Nấm rơm"),
        ("nấm bào ngư", "nấm sò"): ("4130", "Nấm bào ngư (Nấm sò)"),
        ("nấm đùi gà",): ("4131", "Nấm đùi gà"),
        ("thanh long",): ("5055", "Thanh long"),
        ("cá nục",): ("8021", "Cá nục"),
        ("cá thác lác",): ("8013", "Cá thác lác"),
    }
    rules = _validate(_table_with({**pre_repair, **BATCH2_PRE_REPAIR}), master_dict)
    assert len(rules) == 19
    return rules


def test_batch1_widens_the_cache_surface_only_through_repaired_rules(old_active, batch1_active):
    """20 cached Qwen extractions become resolvable that were not before, and
    every one resolves through a Batch 1 code. This is the CACHE surface, not
    the row impact -- see the row-level test below."""
    with open(QWEN_CACHE, encoding="utf-8") as f:
        cache = json.load(f)

    newly = {
        out for out in cache.values()
        if map_clean_to_master(out, old_active) == (None, None)
        and map_clean_to_master(out, batch1_active) != (None, None)
    }
    assert len(newly) == 20

    batch1_codes = {code for code, _ in BATCH1_REPAIRS.values()}
    assert {map_clean_to_master(out, batch1_active)[0] for out in newly} <= batch1_codes


def test_compound_cache_entries_are_inert_because_no_row_is_eligible(old_active, batch1_active):
    """Several newly-resolvable cache entries name MORE than one ingredient
    ("hành lá/hành tím/hành tây"). Substring matching would collapse them to
    hành lá alone, so it matters that A3 keeps them out of reach: every row
    carrying one of these raw_texts already has a master link.

    If this ever fails, a rerun would write a compound line to a single-food
    code and the Batch 1 scope no longer holds.
    """
    with open(QWEN_CACHE, encoding="utf-8") as f:
        cache = json.load(f)
    with open(PROCESSED_ING, encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))

    compound = {
        raw for raw, out in cache.items()
        if map_clean_to_master(out, old_active) == (None, None)
        and map_clean_to_master(out, batch1_active) != (None, None)
        and any(sep in out for sep in ("/", "+", ","))
    }
    assert compound, "fixture drifted: expected some compound cache entries"

    exposed = [
        r for r in rows
        if (r.get("raw_text") or "").strip() in compound and eligible_for_qwen_recovery(r)
    ]
    assert exposed == []


def test_batch1_row_level_regain_is_exactly_the_eight_reviewed_rows(old_active, batch1_active):
    """The measured impact on CURRENT processed data: 9 rows, all of them
    hành lá or cải thảo. Applying these matches is a separate, not-yet-taken
    step -- this test asserts the size and shape of the pending change so it
    cannot grow silently.

    The measured set was 8 until DISPLAY_NAME_BATCH_C1 cleared "1 muỗng cải thảo
    muối khô" to UNMATCHED, which made that row eligible and added the ninth
    entry. This list is a MAPPER-level measurement -- what map_clean_to_master()
    resolves -- so that row is still in it: the mapper does resolve its cached
    output "cải thảo" to 4109 "Rau cải thảo", FRESH napa, and the row is DRIED
    SALTED napa with no catalog identity at all.

    What changed is that the hazard is no longer only documented. C1 hardening
    added the reviewed catalog-gap exclusion _REVIEWED_NO_CATALOG_TARGET_RAW, so
    the production guard qwen_candidate_eligibility() now refuses that exact line
    and the pending recovery step cannot apply it. The final assertion below ties
    the two together: every entry in this mapper-level list is checked against the
    production guard, and this one -- and only this one -- comes back refused."""
    with open(QWEN_CACHE, encoding="utf-8") as f:
        cache = json.load(f)
    with open(PROCESSED_ING, encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))

    regain = []
    for r in rows:
        raw = (r.get("raw_text") or "").strip()
        if raw not in cache or not eligible_for_qwen_recovery(r):
            continue
        before = map_clean_to_master(cache[raw], old_active)
        after = map_clean_to_master(cache[raw], batch1_active)
        if before == after:
            continue
        assert before == (None, None), f"{raw}: a repair CHANGED an existing match"
        regain.append((raw, after))

    assert len(regain) == 9
    assert {after for _, after in regain} == {
        ("4038", "Hành lá (hành hoa)"),
        ("4109", "Rau cải thảo"),
    }
    assert sorted(raw for raw, _ in regain) == [
        "1 chén lá cải thảo",
        "1 muỗng cải thảo muối khô",
        "1 ít hành lá chẻ",
        "1 ít hành lá chẻ (trang trí)",
        "10 g Hành lá cắt nhuyễn",
        "2 muỗng canh hành lá thái nhỏ",
        "2-3 lá cải thảo",
        "3 lá cải thảo",
        "Hành lá: 1 nhánh nhỏ",
    ]
    # The mapper still resolves the C1 row, and the production guard refuses it.
    assert ("1 muỗng cải thảo muối khô", ("4109", "Rau cải thảo")) in regain
    refused = {raw: qwen_candidate_eligibility(raw, cache[raw], after[0])[1]
               for raw, after in regain
               if not qwen_candidate_eligibility(raw, cache[raw], after[0])[0]}
    assert refused == {
        "1 muỗng cải thảo muối khô": "DRIED_SALTED_NAPA_NO_EXACT_CATALOG_TARGET"}
    assert "1 muỗng cải thảo muối khô" in _REVIEWED_NO_CATALOG_TARGET_RAW


def test_batch1_regain_rows_are_still_unmatched_in_processed_data():
    """Nothing was applied: all 8 rows must still be UNMATCHED on disk."""
    with open(PROCESSED_ING, encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))
    targets = {
        "1 chén lá cải thảo", "1 ít hành lá chẻ", "1 ít hành lá chẻ (trang trí)",
        "10 g Hành lá cắt nhuyễn", "2 muỗng canh hành lá thái nhỏ",
        "2-3 lá cải thảo", "3 lá cải thảo", "Hành lá: 1 nhánh nhỏ",
    }
    hits = [r for r in rows if (r.get("raw_text") or "").strip() in targets]
    assert len(hits) == 8
    for r in hits:
        assert not (r.get("master_ingredient_code") or "").strip()
        assert not (r.get("master_ingredient_name") or "").strip()
        assert (r.get("match_method") or "").strip() == "UNMATCHED"
