"""Batch 2 of the disabled-Qwen-mapper-rule audit: 2 GUARDED SAFE_REMAP repairs.

Batch 1 repaired 8 rules whose hard-coded target had merely drifted. The two
rules here are different: each is a generic term that OTHER catalog identities
contain as a substring, so re-pointing the code is only half the repair -- the
other half is an explicit exclusion list, without which the rule would claim
foods that are not the target at all.

    tiêu              13018 Nước mắm cô   ->  13004 Hạt tiêu
    chả huế/chả lụa   7067  Dồi lợn       ->  7069  Giò lụa

Both old codes still EXIST in the catalog; they now name completely different
foods (fish-sauce concentrate, pork blood sausage). That is exactly the drift
A1 exists to catch, and it is why these two rules were disabled rather than
silently resolving to the wrong food.

What these tests pin down:
  * A1 is untouched -- both repairs earn "active" by matching the live
    catalog's current name_vi character-for-character;
  * the split moved 27/22 -> 29/20 and no further;
  * pepper-like phrases reach 13004, but tiêu xanh (20028), bánh tiêu (12091)
    and chuối tiêu (5007) are refused -- each is its own catalog identity;
  * chả lụa / chả huế reach 7069, but any "chay" phrase is refused (20040 is
    the vegetarian identity) and a clearly-beef phrase is refused (7068);
  * the excluded rows are left UNRESOLVED, not remapped somewhere else;
  * Batch 1's 8 rules stay active and every other disabled rule stays disabled;
  * the A3 eligibility guard and the qwen_candidate_eligibility guard still run
    normally over the newly reachable rows;
  * rule ORDER did not regress, and no row that already had a match changes.

Nothing has been applied to processed data: the last section asserts all 31
newly recoverable rows are still UNMATCHED on disk.
"""

import csv
import json
from pathlib import Path

import pytest

from nlp.qwen_matching import (
    _QWEN_MAPPER_EXCLUSIONS,
    _QWEN_MAPPER_RULES,
    build_mapper_rules,
    eligible_for_qwen_recovery,
    map_clean_to_master,
    qwen_candidate_eligibility,
)

ROOT = Path(__file__).resolve().parents[1]
MASTER_CSV = ROOT / "data" / "processed" / "viendinhduong" / "master_ingredients_nutrition.csv"
QWEN_CACHE = ROOT / "data" / "interim" / "qwen_extracted_map.json"
PROCESSED_ING = ROOT / "data" / "processed" / "recipes" / "recipe_ingredients.csv"

TIEU = ("tiêu",)
CHA_LUA = ("chả huế", "chả lụa")

BATCH2_REPAIRS = {
    TIEU: ("13004", "Hạt tiêu"),
    CHA_LUA: ("7069", "Giò lụa"),
}
BATCH2_PRE_REPAIR = {
    TIEU: ("13018", "Hạt tiêu"),
    CHA_LUA: ("7067", "Giò lụa"),
}

# Exclusions that protect a DIFFERENT catalog identity: the phrase names a food
# that already has its own code, and the generic rule may not claim it.
TIEU_IDENTITY_EXCLUSIONS = {
    "tiêu xanh": "20028",   # Tiêu xanh (hạt tiêu tươi) -- fresh green peppercorn
    "bánh tiêu": "12091",   # Bánh tiêu -- a fried dough pastry, not a spice
    "chuối tiêu": "5007",   # Chuối tiêu -- a banana cultivar, not a spice
}
CHA_LUA_IDENTITY_EXCLUSIONS = {
    "chay": "20040",        # Chả lụa chay (giò lụa chay) -- vegetarian
    "chả bò": "7068",       # Giò bò -- beef
    "giò bò": "7068",
    "chả lụa bò": "7068",
}

# Forward-safety exclusions: the phrase is a MIXTURE or processed form whose
# nutrition is not the target food, and it has no single catalog identity of its
# own. Blocked and left unresolved -- deliberately not remapped anywhere.
# "sốt tiêu đen" and "xốt tiêu đen" are ONE identity under two spellings, both
# present in the corpus -- not two separate hazards.
TIEU_MIXTURE_EXCLUSIONS = ("muối tiêu", "sốt tiêu đen", "xốt tiêu đen")
# Poultry giò lụa: a real row ("Chả lụa gà 200 gr") with no catalog code yet.
CHA_LUA_MIXTURE_EXCLUSIONS = ("chả lụa gà",)

TIEU_EXCLUSIONS = tuple(TIEU_IDENTITY_EXCLUSIONS) + TIEU_MIXTURE_EXCLUSIONS
CHA_LUA_EXCLUSIONS = tuple(CHA_LUA_IDENTITY_EXCLUSIONS) + CHA_LUA_MIXTURE_EXCLUSIONS

# Batch 1's 8 repairs, restated here so this file fails on its own if a Batch-2
# edit knocks one of them back out.
BATCH1_ACTIVE_TERMS = {
    ("hành lá", "hành hoa"), ("cải thảo", "bắp cải thảo"), ("nấm rơm",),
    ("nấm bào ngư", "nấm sò"), ("nấm đùi gà",), ("thanh long",), ("cá nục",),
    ("cá thác lác",),
}

# Verdict REMOVE: the hard-coded target is the wrong food, so no repair helps.
REMOVE_RULE_TERMS = {
    ("xoài",),
    ("chanh",),
    ("tàu hũ ki", "tàu hủ ki", "váng đậu", "mì căn", "ham chay", "giò sống chay"),
}

# NEEDS_REVIEW (14) + OBSOLETE (3). Batch 2 claimed neither group.
STILL_DISABLED_AFTER_BATCH2 = {
    ("bắp cải",), ("cải con", "cải mầm", "cải thìa"), ("cải xoong",),
    ("cải xanh", "cải ngồng"), ("đậu que", "đậu cô ve"), ("đậu đũa",),
    ("hành tím", "hành khô", "hành củ", "hành trắng", "đầu hành"),
    ("ngò gai", "mùi tàu"), ("bạc hà",), ("húng lủi", "húng quế", "rau húng"),
    ("nấm hương", "nấm đông cô"), ("nấm kim châm",), ("tắc", "quất"),
    ("chà là",), ("cá cơm khô", "cá cơm"), ("tôm càng", "tôm đồng"),
    ("cua biển",),
}


@pytest.fixture(scope="module")
def master_dict():
    with open(MASTER_CSV, encoding="utf-8-sig", newline="") as f:
        return {r["code"]: r for r in csv.DictReader(f)}


@pytest.fixture(scope="module")
def split(master_dict):
    return build_mapper_rules(master_dict)


@pytest.fixture(scope="module")
def active(split):
    return split[0]


@pytest.fixture(scope="module")
def active_terms(split):
    return {terms for terms, _, _ in split[0]}


@pytest.fixture(scope="module")
def disabled_terms(split):
    return {terms for terms, _, _, _ in split[1]}


@pytest.fixture(scope="module")
def before_active(master_dict):
    """The active rule set as it stood at the end of Batch 1.

    Both pre-repair targets fail A1 (13018 is Nước mắm cô, 7067 is Dồi lợn), so
    this is the 27-rule set with neither Batch-2 rule in it.
    """
    table = tuple(
        (terms, *BATCH2_PRE_REPAIR[terms]) if terms in BATCH2_PRE_REPAIR else (terms, code, name)
        for terms, code, name in _QWEN_MAPPER_RULES
    )
    rules = [
        (terms, code, name) for terms, code, name in table
        if code in master_dict
        and master_dict[code]["name_vi"].strip().casefold() == name.strip().casefold()
    ]
    assert len(rules) == 27
    return rules


@pytest.fixture(scope="module")
def cache():
    with open(QWEN_CACHE, encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture(scope="module")
def rows():
    with open(PROCESSED_ING, encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


# ---------------------------------------------------------------------------
# A1 identity validation is intact -- the repairs earn "active", not bypass it
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("terms", sorted(BATCH2_REPAIRS, key=str))
def test_repaired_rule_is_active_against_live_catalog(terms, active_terms):
    assert terms in active_terms


@pytest.mark.parametrize("terms,expected", sorted(BATCH2_REPAIRS.items(), key=str))
def test_repaired_rule_carries_the_approved_code_and_name(terms, expected):
    hard_coded = {t: (c, n) for t, c, n in _QWEN_MAPPER_RULES}
    assert hard_coded[terms] == expected


@pytest.mark.parametrize("terms,expected", sorted(BATCH2_REPAIRS.items(), key=str))
def test_repaired_rule_name_is_the_catalogs_current_identity(terms, expected, master_dict):
    """Byte-exact, not merely equal under the A1 casefold/whitespace normaliser."""
    code, name = expected
    assert code in master_dict, f"{code} is not in the live catalog"
    assert master_dict[code]["name_vi"] == name


@pytest.mark.parametrize("terms,stale", sorted(BATCH2_PRE_REPAIR.items(), key=str))
def test_the_old_target_exists_but_is_a_different_food(terms, stale, master_dict):
    """Why these rules needed a guarded repair rather than a deletion: the stale
    code is not dangling, it silently names something else entirely. Existence
    checking alone would have kept both rules live and wrong."""
    stale_code, _ = stale
    assert stale_code in master_dict
    good_code, good_name = BATCH2_REPAIRS[terms]
    assert master_dict[stale_code]["name_vi"] != good_name
    assert stale_code != good_code


def test_a1_still_disables_a_rule_whose_name_drifts(master_dict):
    """The guard itself is unchanged: feed it a Batch-2 rule with a wrong name
    and it must refuse to activate it."""
    broken = dict(master_dict)
    broken["13004"] = {**master_dict["13004"], "name_vi": "Hạt tiêu đen rang"}
    active, _ = build_mapper_rules(broken)
    assert TIEU not in {terms for terms, _, _ in active}


# ---------------------------------------------------------------------------
# The split moved exactly 27/22 -> 29/20
# ---------------------------------------------------------------------------

def test_rule_table_size_is_unchanged():
    assert len(_QWEN_MAPPER_RULES) == 49


def test_active_and_disabled_counts_after_batch2(split):
    active, disabled = split
    assert len(active) == 29
    assert len(disabled) == 20
    assert len(active) + len(disabled) == len(_QWEN_MAPPER_RULES)


def test_batch2_is_the_only_thing_that_became_active(active_terms, before_active):
    before_terms = {terms for terms, _, _ in before_active}
    assert active_terms - before_terms == set(BATCH2_REPAIRS)
    assert before_terms - active_terms == set()


def test_batch1_rules_are_all_still_active(active_terms):
    assert BATCH1_ACTIVE_TERMS <= active_terms


@pytest.mark.parametrize("terms", sorted(REMOVE_RULE_TERMS, key=str))
def test_remove_verdict_rules_remain_disabled(terms, disabled_terms):
    assert terms in disabled_terms


@pytest.mark.parametrize("terms", sorted(STILL_DISABLED_AFTER_BATCH2, key=str))
def test_needs_review_and_obsolete_rules_remain_disabled(terms, disabled_terms):
    assert terms in disabled_terms


def test_disabled_set_is_exactly_the_untouched_rules(disabled_terms):
    assert disabled_terms == REMOVE_RULE_TERMS | STILL_DISABLED_AFTER_BATCH2


# ---------------------------------------------------------------------------
# A. tiêu -> 13004, with its three exclusions
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("phrase", [
    "tiêu",
    "hạt tiêu",
    "tiêu trắng",
    "tiêu trắng mịn",
    "tiêu đen",
    "tiêu sọ",
    "tiêu sọ hạt",
    "tiêu sọ giã bễ",
    "tiêu hạt trắng",
    "tiêu hạt tứ xuyên",
    "bột tiêu trắng",
    "hạt tiêu đen nguyên hạt",
])
def test_pepper_like_phrase_recovers_to_13004(phrase, active):
    assert map_clean_to_master(phrase, active) == ("13004", "Hạt tiêu")


@pytest.mark.parametrize("phrase", [
    "tiêu xanh",
    "tiêu xanh giã dập",
    "tiêu xanh đập dập",
    "bột tiêu xanh",
    "hoa tiêu xanh",
    "chùm tiêu xanh",
    "tiêu xanh tươi",
])
def test_tieu_xanh_never_recovers_to_13004(phrase, active):
    """20028 is green peppercorn's own identity. The generic rule abstains."""
    assert map_clean_to_master(phrase, active) == (None, None), phrase


@pytest.mark.parametrize("phrase", [
    "bánh tiêu",
    "lá chuối cắt tròn làm đế bánh tiêu",
])
def test_banh_tieu_never_recovers_to_13004(phrase, active):
    """12091 Bánh tiêu is a fried pastry; it merely contains the word."""
    assert map_clean_to_master(phrase, active) == (None, None), phrase


@pytest.mark.parametrize("phrase", ["chuối tiêu", "chuối tiêu chín"])
def test_chuoi_tieu_never_recovers_to_13004(phrase, active):
    """5007 Chuối tiêu is a banana cultivar."""
    assert map_clean_to_master(phrase, active) == (None, None), phrase


def test_excluded_tieu_phrases_are_not_remapped_anywhere_else(active):
    """Batch 2 blocks these phrases; it does not redirect them. Re-pointing them
    at 20028 / 12091 / 5007 is a separate, unreviewed action."""
    for phrase in ("tiêu xanh", "bánh tiêu", "chuối tiêu"):
        code, name = map_clean_to_master(phrase, active)
        assert (code, name) == (None, None), phrase


def test_tieu_exclusion_targets_are_real_and_distinct_identities(master_dict):
    for phrase, code in TIEU_IDENTITY_EXCLUSIONS.items():
        assert code in master_dict, f"{phrase} -> {code} is not in the catalog"
        assert code != BATCH2_REPAIRS[TIEU][0]


def test_tieu_exclusion_list_is_exactly_the_reviewed_hazards():
    assert _QWEN_MAPPER_EXCLUSIONS[TIEU] == (
        "tiêu xanh", "bánh tiêu", "chuối tiêu",     # other catalog identities
        "muối tiêu",                                # salt-and-pepper mixture
        "sốt tiêu đen", "xốt tiêu đen",             # one sauce, two spellings
    )


def test_tieu_exclusions_are_phrase_level_not_bare_words(active):
    """The mixture exclusions must not leak into plain peppercorn. "muối",
    "sốt", "đen" and "ớt" are NOT excluded bare -- a bare "đen" would kill
    "tiêu đen" and "hạt tiêu đen nguyên hạt", which are the target food."""
    for bare in ("muối", "sốt", "xốt", "đen", "ớt", "chanh", "tiêu đen"):
        assert bare not in _QWEN_MAPPER_EXCLUSIONS[TIEU], bare
    assert map_clean_to_master("tiêu đen", active) == ("13004", "Hạt tiêu")
    assert map_clean_to_master("hạt tiêu đen nguyên hạt", active) == ("13004", "Hạt tiêu")
    assert map_clean_to_master("tiêu trắng", active) == ("13004", "Hạt tiêu")


# ---------------------------------------------------------------------------
# B. chả huế / chả lụa -> 7069, with its chay and beef exclusions
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("phrase", [
    "chả lụa",
    "chả huế",
    "chả huế cây",
    "chả lụa khoanh",
    "chả lụa cắt hạt lựu nhỏ",
    "chả lụa nem chua bánh tôm chiên",
])
def test_ordinary_cha_lua_recovers_to_7069(phrase, active):
    assert map_clean_to_master(phrase, active) == ("7069", "Giò lụa")


@pytest.mark.parametrize("phrase", [
    "chả lụa chay",
    "chả huế chay",
    "chả lụa chay cắt hạt lựu",
    "chả lụa chay cắt hạt lựu nhỏ",
    "chả lụa chay cắt que như măng tây",
])
def test_chay_variant_never_recovers_to_pork_7069(phrase, active):
    """20040 Chả lụa chay is the vegetarian identity. Deliberately NOT remapped
    to it here: that action needs its own reviewed policy."""
    assert map_clean_to_master(phrase, active) == (None, None), phrase


def test_chay_phrase_owned_by_an_earlier_rule_still_is_not_claimed_by_7069(active):
    """"nấm rơm chả lụa chay" is a real processed cleaned_name. The nấm rơm rule
    sits earlier in the table and wins it; what matters for Batch 2 is only that
    the pork rule does not -- and the exclusion holds without that head start.
    """
    assert map_clean_to_master("nấm rơm chả lụa chay", active) == ("4129", "Nấm rơm")
    assert map_clean_to_master("chả lụa chay", active) == (None, None)


@pytest.mark.parametrize("phrase", [
    "chả lụa bò",
    "chả bò",
    "giò bò",
    "chả lụa bò cắt lát",
])
def test_beef_variant_is_not_stolen_by_7069(phrase, active):
    """7068 Giò bò is beef, and processed rows already link the beef identity.
    The pork rule must abstain rather than absorb it."""
    assert map_clean_to_master(phrase, active) == (None, None), phrase


def test_excluded_cha_phrases_are_not_remapped_anywhere_else(active):
    for phrase in ("chả lụa chay", "chả bò", "giò bò", "chả lụa bò"):
        assert map_clean_to_master(phrase, active) == (None, None), phrase


def test_cha_lua_exclusion_targets_are_real_and_distinct_identities(master_dict):
    for phrase, code in CHA_LUA_IDENTITY_EXCLUSIONS.items():
        if phrase == "chay":
            continue
        assert code in master_dict, f"{phrase} -> {code} is not in the catalog"
        assert code != BATCH2_REPAIRS[CHA_LUA][0]
    assert "20040" in master_dict
    assert master_dict["20040"]["name_vi"] == "Chả lụa chay (giò lụa chay)"
    assert master_dict["7068"]["name_vi"] == "Giò bò"


def test_cha_lua_exclusion_list_is_exactly_the_reviewed_hazards():
    assert _QWEN_MAPPER_EXCLUSIONS[CHA_LUA] == (
        "chay", "chả bò", "giò bò", "chả lụa bò",   # vegetarian + beef identities
        "chả lụa gà",                               # poultry, no code yet
    )


def test_ga_is_not_excluded_bare(active):
    """Only the full "chả lụa gà" head is blocked. A bare "gà" would also block
    a compound line that merely mentions chicken alongside real giò lụa.

    ("chả lụa ăn với thịt gà" is NOT the probe here: the thịt gà rule sits
    earlier in the table and wins that phrase outright, which would make the
    assertion about ordering rather than about the exclusion.)
    """
    assert "gà" not in _QWEN_MAPPER_EXCLUSIONS[CHA_LUA]
    assert map_clean_to_master("chả lụa và gà xé", active) == ("7069", "Giò lụa")
    assert map_clean_to_master("chả lụa gà xé", active) == (None, None)


def test_bo_is_not_excluded_bare(active):
    """"bò" alone appears inside unrelated context ("bún bò"), so excluding it
    bare would over-block. Only the beef identity heads are listed."""
    assert "bò" not in _QWEN_MAPPER_EXCLUSIONS[CHA_LUA]
    assert map_clean_to_master("chả lụa ăn với bún bò", active) == ("7069", "Giò lụa")


def test_bare_cha_and_gio_do_not_reach_7069(active):
    """The rule needs the full two-word head. A bare "chả" or "giò sống" is a
    different food and stays unresolved."""
    for phrase in ("chả", "chả chiên", "giò sống", "giò heo"):
        assert map_clean_to_master(phrase, active) == (None, None), phrase
    # Owned by the cá thác lác rule, and still not the pork rule's to take.
    assert map_clean_to_master("chả cá thác lác", active) == ("8013", "Cá thát lát")


# ---------------------------------------------------------------------------
# Batch 2 added nothing else, and matching stayed exact-substring
# ---------------------------------------------------------------------------

def test_batch2_added_exactly_two_exclusion_keys():
    assert set(_QWEN_MAPPER_EXCLUSIONS) == {
        ("cải xanh", "cải ngồng"),
        ("tắc", "quất"),
        TIEU,
        CHA_LUA,
    }
    assert _QWEN_MAPPER_EXCLUSIONS[("cải xanh", "cải ngồng")] == ("bông cải xanh",)
    assert _QWEN_MAPPER_EXCLUSIONS[("tắc", "quất")] == ("việt quất",)


def test_matching_is_still_exact_substring_only(active):
    for near_miss in ("tieu", "tiêu xanh", "hat tieu", "cha lua", "cha hue",
                      "chả lua", "gio lua"):
        assert map_clean_to_master(near_miss, active) == (None, None), near_miss


# ---------------------------------------------------------------------------
# No mapper ordering regression
# ---------------------------------------------------------------------------

def test_batch2_rules_kept_their_original_positions():
    """Batch 2 changed code + exclusions only. A reorder would change which rule
    wins a substring collision, so position is asserted rather than assumed."""
    order = [terms for terms, _, _ in _QWEN_MAPPER_RULES]
    assert order.index(TIEU) == 44
    assert order.index(CHA_LUA) == 33
    assert order.index(("thịt gà", "chân gà")) < order.index(CHA_LUA)
    assert order.index(CHA_LUA) < order.index(
        ("tàu hũ ki", "tàu hủ ki", "váng đậu", "mì căn", "ham chay", "giò sống chay"))
    assert order.index(TIEU) < order.index(("ớt xiêm", "ớt sừng", "ớt"))


def test_the_full_rule_order_is_unchanged_by_batch2():
    """Terms are the identity of a rule's slot; Batch 2 touched codes, not slots."""
    order = [terms for terms, _, _ in _QWEN_MAPPER_RULES]
    assert len(order) == len(set(order)) == 49
    assert order[0] == ("hành lá", "hành hoa")
    assert order[1] == ("cải thảo", "bắp cải thảo")
    assert order[-1] == ("lá cà ri", "hoa hồi", "đại hồi")
    assert order.index(("cải thảo", "bắp cải thảo")) < order.index(("bắp cải",))
    assert order.index(("ngò gai", "mùi tàu")) < order.index(("rau mùi", "ngò rí", "ngò"))


def test_batch2_does_not_steal_a_phrase_owned_by_another_rule(active):
    for phrase, expected in (
        ("ớt sừng", ("13039", "Ớt tươi")),
        ("ớt xiêm", ("13039", "Ớt tươi")),
        ("thịt bò", ("7003", "Thịt bò nạc")),
        ("bắp bò", ("7094", "Thịt bắp bò")),
        ("thịt gà", ("7013", "Thịt gà ta")),
        ("nấm rơm", ("4129", "Nấm rơm")),
        ("hành lá", ("4038", "Hành lá (hành hoa)")),
    ):
        assert map_clean_to_master(phrase, active) == expected, phrase


def test_tieu_now_precedes_ot_for_mixed_phrases(active, before_active, cache):
    """The one behavioural side effect of re-activating a rule that always sat
    ahead of the ớt rule: a phrase naming BOTH now resolves to 13004 instead of
    13039. Exactly two cache outputs are in that shape and BOTH belong to rows
    that already carry a master link, so no row changes (asserted below).
    Pinned here so the count cannot grow unnoticed."""
    shadowed = {
        out for out in cache.values()
        if map_clean_to_master(out, before_active) == ("13039", "Ớt tươi")
        and map_clean_to_master(out, active) == ("13004", "Hạt tiêu")
    }
    assert shadowed == {"tiêu hạt/ớt xanh/ ớt đỏ", "hành tím ớt tiêu"}


# ---------------------------------------------------------------------------
# The Qwen eligibility guards still run normally
# ---------------------------------------------------------------------------

def test_a3_guard_still_gates_on_the_master_link():
    assert eligible_for_qwen_recovery(
        {"master_ingredient_code": "", "master_ingredient_name": "", "match_method": "UNMATCHED"})
    assert not eligible_for_qwen_recovery(
        {"master_ingredient_code": "13004", "master_ingredient_name": "Hạt tiêu",
         "match_method": "UNMATCHED"})


def test_candidate_guard_allows_the_plain_batch2_candidates():
    assert qwen_candidate_eligibility("Tiêu trắng", "tiêu trắng", "13004") == (True, None)
    assert qwen_candidate_eligibility("chả Huế", "chả huế", "7069") == (True, None)


def test_candidate_guard_still_rejects_a_list_output_carrying_a_batch2_code():
    """The guard is not bypassed for Batch-2 codes: a multi-ingredient output
    that happens to contain a pepper head is still refused."""
    ok, reason = qwen_candidate_eligibility(
        "Tiêu hạt/ớt xanh/ ớt đỏ 1 ít", "tiêu hạt/ớt xanh/ ớt đỏ", "13004")
    assert not ok
    assert reason == "qwen_explicit_ingredient_list"


def test_candidate_guard_still_rejects_a_collapsed_reviewed_raw_list():
    ok, reason = qwen_candidate_eligibility("hành lá và ngò rí", "hành lá", "4038")
    assert not ok
    assert reason == "qwen_collapsed_reviewed_raw_list"


def test_ngo_gai_guard_is_untouched_by_batch2():
    ok, reason = qwen_candidate_eligibility("ngò gai 1 ít", "ngò", "4081")
    assert not ok
    assert reason == "generic_ngo_conflicts_with_raw_ngo_gai"


# ---------------------------------------------------------------------------
# Measured impact on the CURRENT processed data
# ---------------------------------------------------------------------------

def _regain(rows, cache, before_active, active):
    newly, changed = [], []
    for r in rows:
        raw = (r.get("raw_text") or "").strip()
        if raw not in cache or not eligible_for_qwen_recovery(r):
            continue
        out = cache[raw]
        before = map_clean_to_master(out, before_active)
        after = map_clean_to_master(out, active)
        if before == after:
            continue
        (newly if before == (None, None) else changed).append((raw, out, after))
    return newly, changed


def test_batch2_never_changes_a_match_that_already_resolved(rows, cache, before_active, active):
    _, changed = _regain(rows, cache, before_active, active)
    assert changed == []


def test_batch2_row_level_regain_is_exactly_31_rows(rows, cache, before_active, active):
    """The measured impact on current processed data. Applying these matches is
    a separate, not-yet-taken step; this pins the size and shape of the pending
    change so it cannot grow silently."""
    newly, _ = _regain(rows, cache, before_active, active)
    assert len(newly) == 31
    assert {after for _, _, after in newly} == {
        ("13004", "Hạt tiêu"),
        ("7069", "Giò lụa"),
    }
    assert sum(1 for _, _, a in newly if a[0] == "13004") == 22
    assert sum(1 for _, _, a in newly if a[0] == "7069") == 9


def test_every_newly_recoverable_row_passes_the_candidate_guard(rows, cache, before_active, active):
    newly, _ = _regain(rows, cache, before_active, active)
    for raw, out, after in newly:
        ok, reason = qwen_candidate_eligibility(raw, out, after[0])
        assert ok, f"{raw!r} -> {out!r} blocked by {reason}"


def test_the_nine_cha_hue_rows_are_the_reviewed_ones(rows, cache, before_active, active):
    newly, _ = _regain(rows, cache, before_active, active)
    assert sorted(raw for raw, _, a in newly if a[0] == "7069") == [
        "10 cây chả Huế",
        "10 cây chả Huế",
        "2 cây chả Huế",
        "2 cây chả Huế",
        "4 cây chả Huế",
        "5 cây chả Huế",
        "Chả Huế 1 ít",
        "Chả Huế cây 4 cây",
        "chả Huế",
    ]


def _blocked_by_batch2_exclusion(output):
    """Would this Qwen output hit a Batch-2 rule if its exclusions were removed?"""
    text = (output or "").lower()
    for terms in (TIEU, CHA_LUA):
        if any(term in text for term in terms):
            return any(bad in text for bad in _QWEN_MAPPER_EXCLUSIONS[terms])
    return False


def test_the_exclusions_block_exactly_these_cache_outputs(cache):
    """The mixture exclusions are the first ones with live bite: 7 cached Qwen
    outputs would reach 13004 without them. Every one is a salt-mix or a bottled
    sauce, and all of them sit on rows that already carry a master link, which is
    why the row-level count below is still 31.

    The identity exclusions (tiêu xanh / bánh tiêu / chuối tiêu / chay / beef)
    still block nothing in the cache -- they guard rows that have no cache entry
    yet ("Bột tiêu xanh 2 gr", "Chả lụa chay cắt hạt lựu nhỏ 50g", "Chả lụa gà
    200 gr") and future re-extractions.
    """
    blocked = {out for out in cache.values() if _blocked_by_batch2_exclusion(out)}
    assert blocked == {
        "sốt tiêu đen",
        "nước tương sốt tiêu đen",
        "xốt tiêu đen",
        "muối tiêu",
        "hành tím muối tiêu dầu ăn",
    }


def test_no_eligible_row_is_blocked_by_a_batch2_exclusion(rows, cache):
    """Every cache output the exclusions block belongs to an already-linked row,
    so the exclusions cost the recovery nothing today."""
    reachable = [
        raw for r in rows
        if (raw := (r.get("raw_text") or "").strip()) in cache
        and eligible_for_qwen_recovery(r)
        and _blocked_by_batch2_exclusion(cache[raw])
    ]
    assert reachable == []


def test_the_identity_exclusions_still_block_nothing_in_the_cache(cache):
    identity_only = tuple(TIEU_IDENTITY_EXCLUSIONS) + tuple(CHA_LUA_IDENTITY_EXCLUSIONS)
    hits = [
        out for out in cache.values()
        if _blocked_by_batch2_exclusion(out)
        and any(bad in (out or "").lower() for bad in identity_only)
    ]
    assert hits == []
    # ...but the corpus does contain the substring, so the guard is not vacuous.
    assert any("chay" in (out or "").lower() for out in cache.values())


@pytest.mark.parametrize("hazard,head,forbidden", [
    ("tiêu xanh", "tiêu", ("13004", "Hạt tiêu")),
    ("bánh tiêu", "tiêu", ("13004", "Hạt tiêu")),
    ("chay", "chả", ("7069", "Giò lụa")),
])
def test_the_excluded_phrases_exist_in_processed_data_and_are_never_claimed(
        hazard, head, forbidden, rows, active):
    """The hazards are real rows, not hypotheticals. Each hazard is checked only
    against the rule it actually threatens: "chay" endangers the pork rule, not
    the pepper rule, and a cleaned_name like "muối mì chính nước mắm chay tiêu"
    is legitimately pepper.
    """
    seen = 0
    for r in rows:
        cleaned = (r.get("cleaned_name") or "").strip().lower()
        if hazard in cleaned and head in cleaned:
            seen += 1
            assert map_clean_to_master(cleaned, active) != forbidden, cleaned
    assert seen > 0, f"fixture drifted: no processed row carries {hazard!r}"


# ---------------------------------------------------------------------------
# Nothing was written to processed data
# ---------------------------------------------------------------------------

def test_batch2_regain_rows_are_still_unmatched_on_disk(rows, cache, before_active, active):
    newly, _ = _regain(rows, cache, before_active, active)
    targets = {raw for raw, _, _ in newly}
    assert targets
    hits = [r for r in rows if (r.get("raw_text") or "").strip() in targets]
    assert len(hits) == 31
    for r in hits:
        assert not (r.get("master_ingredient_code") or "").strip()
        assert not (r.get("master_ingredient_name") or "").strip()
        assert (r.get("match_method") or "").strip() == "UNMATCHED"


def test_no_processed_row_carries_a_batch2_target_via_qwen(rows):
    """QWEN_LLM_MATCH is the only method this change can write, so its absence on
    both target codes is the proof that nothing was applied.

    Both codes are already present in the data by OTHER methods, and those rows
    are untouched: 13004 via PRESET_ALIAS/EXACT/CLEANED_NAME, and 7069 via
    EXACT_CATALOG_MATCH on "giò lụa" plus a set of PRESET_ALIAS "sườn" rows that
    predate this work and are out of Batch-2 scope.
    """
    for code in ("13004", "7069"):
        via_qwen = [
            r for r in rows
            if (r.get("master_ingredient_code") or "").strip() == code
            and (r.get("match_method") or "").strip() == "QWEN_LLM_MATCH"
        ]
        assert via_qwen == [], code
    assert [r for r in rows if (r.get("master_ingredient_code") or "").strip() == "7069"]


# ---------------------------------------------------------------------------
# Batch-2 hardening pass: the exact allowed/blocked matrix
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("phrase,expected", [
    ("tiêu trắng", ("13004", "Hạt tiêu")),
    ("hạt tiêu đen nguyên hạt", ("13004", "Hạt tiêu")),
    ("chả huế", ("7069", "Giò lụa")),
    ("chả lụa", ("7069", "Giò lụa")),
])
def test_hardening_allowed_phrases(phrase, expected, active):
    assert map_clean_to_master(phrase, active) == expected


@pytest.mark.parametrize("phrase", [
    "tiêu xanh",
    "bánh tiêu",
    "chuối tiêu",
    "muối tiêu",
    "sốt tiêu đen",
    "chả lụa chay",
    "chả lụa bò",
    "chả lụa gà",
])
def test_hardening_blocked_phrases(phrase, active):
    """Blocked means UNRESOLVED, never redirected: the pass adds no remapping."""
    assert map_clean_to_master(phrase, active) == (None, None), phrase


@pytest.mark.parametrize("phrase", [
    "muối tiêu",
    "sốt tiêu đen",
    "chả lụa gà",
])
def test_hardening_blocked_phrases_are_not_remapped_elsewhere(phrase, active, master_dict):
    """No Batch-2 exclusion sends its phrase to another code. 20028/12091/5007/
    20040/7068 stay reachable only through other matching stages."""
    assert map_clean_to_master(phrase, active) == (None, None)
    assert all(map_clean_to_master(phrase, [rule]) == (None, None)
               for rule in active if rule[0] in (TIEU, CHA_LUA))


def test_hardening_blocked_phrases_survive_surrounding_context(active):
    """Real corpus forms, not just the bare heads."""
    for phrase in ("muối tiêu chanh", "ăn kèm muối tiêu chanh xà lách trộn",
                   "nước tương sốt tiêu đen", "hành tím muối tiêu dầu ăn",
                   "chả lụa gà 200 gr", "chả lụa chay cắt hạt lựu nhỏ"):
        assert map_clean_to_master(phrase, active) == (None, None), phrase


def test_hardening_did_not_touch_the_eligibility_guard():
    """The pass is exclusion-only: the guard's reasons and verdicts are as they
    were, including on a phrase the new exclusions now block."""
    assert qwen_candidate_eligibility("Tiêu trắng", "tiêu trắng", "13004") == (True, None)
    assert qwen_candidate_eligibility("chả Huế", "chả huế", "7069") == (True, None)
    assert qwen_candidate_eligibility("ĂN KÈM: Muối tiêu chanh", "muối tiêu", None) == (True, None)


def test_hanh_tim_ot_tieu_remains_a_documented_known_compound_risk(active, cache):
    """NOT solved in Batch 2, by instruction. "hành tím ớt tiêu" names three
    ingredients with no separator, so the list guard cannot see it.

    It is now inert for a different reason: "muối tiêu" and friends aside, this
    output is caught by the muối/sốt exclusions only in its sibling form. This
    one resolves to 13004 on the strength of "tiêu" alone -- and stays harmless
    solely because its row already carries a master link (A3). Pinned here so
    that if A3 ever stops covering it, this test fails rather than the data.
    """
    assert "hành tím ớt tiêu" in cache.values()
    assert map_clean_to_master("hành tím ớt tiêu", active) == ("13004", "Hạt tiêu")
    raws = [raw for raw, out in cache.items() if out == "hành tím ớt tiêu"]
    assert raws == ["ngò rí Hành tím băm,  cắt nhỏ, ớt băm, tiêu sọ giã bể"]


# ---------------------------------------------------------------------------
# x-spelling of the black-pepper sauce: same identity, same exclusion
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("phrase", [
    "xốt tiêu đen",
    "1 muỗng xốt tiêu đen",
    "xốt tiêu đen 1 muỗng canh",
    "nước tương xốt tiêu đen",
    "ướp xốt tiêu đen",
])
def test_xot_tieu_den_is_blocked_in_and_out_of_context(phrase, active):
    """"Xốt tiêu đen 1 muỗng canh" is the same bottled sauce as "sốt tiêu đen",
    only with the x-spelling. Blocked, and left unresolved -- not remapped."""
    assert map_clean_to_master(phrase, active) == (None, None), phrase


@pytest.mark.parametrize("phrase", [
    "tiêu đen",
    "hạt tiêu đen nguyên hạt",
    "tiêu đen bể",
    "tiêu đen nguyên hạt",
    "2 gr tiêu đen nguyên hạt",
])
def test_plain_black_peppercorn_still_resolves_to_13004(phrase, active):
    """The sauce exclusions must not spill onto the spice. Both spellings end in
    "tiêu đen", so a careless exclusion here would silently kill the target
    food; only the full two-word sauce head is listed."""
    assert map_clean_to_master(phrase, active) == ("13004", "Hạt tiêu"), phrase


def test_both_sauce_spellings_behave_identically(active):
    for s_form, x_form in (("sốt tiêu đen", "xốt tiêu đen"),
                           ("nước tương sốt tiêu đen", "nước tương xốt tiêu đen")):
        assert map_clean_to_master(s_form, active) == map_clean_to_master(x_form, active)
        assert map_clean_to_master(s_form, active) == (None, None)


def test_the_xot_row_is_real_and_currently_unreachable(rows, cache):
    """Evidence for the exclusion, and why it costs the recovery nothing: the
    one "xốt tiêu đen" row already carries a (stale, pre-A1) master link, so A3
    keeps it out of reach. The exclusion is forward safety for a re-extraction.
    """
    assert "xốt tiêu đen" in cache.values()
    hits = [r for r in rows if (r.get("cleaned_name") or "").strip().lower() == "xốt tiêu đen"]
    assert len(hits) == 1
    assert not eligible_for_qwen_recovery(hits[0])
