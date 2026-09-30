"""Qwen-recovery matching logic for scripts/run_qwen_line_pipeline.py.

Kept separate from that script (which imports torch/transformers at module
load) so the matching rules and per-row resolution can be unit tested without
a GPU or model weights.

Root causes addressed here (see reports/eda/qwen_matching/):
  A1 - hard-coded (code, name) pairs are validated against the live master
       catalog before they can be used; a stale pair is disabled, not applied.
  A2 - substring-first shadowing: more specific terms are checked before the
       generic terms that contain them as a substring, and known false-positive
       supersets are excluded explicitly instead of relying on ordering alone.
  A3 - Qwen recovery only fires when a row has neither a master code nor a
       master name; a populated link is never overwritten by stale UNMATCHED
       status alone.
  A4 - a candidate is validated against the catalog before any matching field
       is written; a dangling/invalid candidate leaves the row's existing
       matching fields untouched.
  A5 - a weight-only change (no accepted match) never touches match_confidence;
       confidence is only stamped when a validated match is actually applied.
  A6 - Qwen may narrow the parser's ingredient name by dropping an identity or
       state qualifier ("xoai keo" -> "xoai", "tau hu ki kho" -> "tau hu ki").
       Such a rewrite is rejected for cleaned_name only; the row's validated
       match/code/weight update still applies (see resolve_cleaned_name_update).
"""

from __future__ import annotations

import re
import unicodedata
from typing import Any

from nlp.ingredient_parser import VietnameseIngredientParser
from nlp.matching_integrity import MATCH_FIELDS, has_master_link, stage_qwen_update

QWEN_MATCH_CONFIDENCE = "0.98"

# Ordered most-specific-first. Preserves the original reviewed mapping pairs;
# the two reorderings/exclusions below are the only behavioral departures from
# the historical rule set, and both close a documented substring-shadowing bug.
_QWEN_MAPPER_RULES: tuple[tuple[tuple[str, ...], str, str], ...] = (
    (("hành lá", "hành hoa"), "4038", "Hành lá (hành hoa)"),
    (("cải thảo", "bắp cải thảo"), "4109", "Rau cải thảo"),
    (("bắp cải",), "4010", "Cải bắp"),
    (("đậu bắp",), "20086", "Đậu bắp (Bắp còi)"),
    (("củ sen",), "20103", "Củ sen tươi (Lotus root)"),
    (("ngó sen",), "4059", "Ngó sen"),
    (("cà bi", "cà chua"), "4005", "Cà chua"),
    (("cà rốt", "carrot"), "4007", "Cà rốt"),
    (("cải con", "cải mầm", "cải thìa"), "4016", "Cải bẹ trắng (cải thìa/thảo)"),
    (("cải xoong",), "4017", "Cải xoong"),
    # A2: "bông cải xanh" (broccoli) must not fall through the "cải xanh" rule.
    (("cải xanh", "cải ngồng"), "4015", "Cải bẹ xanh"),
    (("đậu que", "đậu cô ve"), "4031", "Đậu cô ve"),
    (("đậu đũa",), "4033", "Đậu đũa"),
    (("hành tím", "hành khô", "hành củ", "hành trắng", "đầu hành"), "4081", "Hành củ tươi"),
    # A2: "ngò gai" / "mùi tàu" must be checked before the generic "ngò" rule
    # below, since "ngò" is a substring of "ngò gai" and would shadow it.
    (("ngò gai", "mùi tàu"), "4076", "Mùi tàu"),
    # DISPLAY_NAME_BATCH_A: coriander leaf is 4081 "Rau mùi". 4073 carried that
    # display name while its name_en was "Amaranth, sp. Red"; repairing the
    # catalog name deactivated this rule through the A1 identity check, so it is
    # repointed onto the identity it always meant. Terms and position unchanged.
    (("rau mùi", "ngò rí", "ngò"), "4081", "Rau mùi"),
    (("bạc hà",), "13038", "Bạc hà tươi"),
    (("húng lủi", "húng quế", "rau húng"), "4074", "Rau húng"),
    (("nấm rơm",), "4129", "Nấm rơm"),
    (("nấm hương", "nấm đông cô"), "4055", "Nấm hương khô"),
    (("nấm mỡ", "nấm nâu", "nấm chân gà"), "4128", "Nấm mỡ (Nấm tây)"),
    (("nấm kim châm",), "4129", "Nấm kim châm"),
    (("nấm bào ngư", "nấm sò"), "20004", "Nấm bào ngư (nấm sò)"),
    (("nấm đùi gà",), "20007", "Nấm đùi gà"),
    (("xoài",), "5074", "Xoài"),
    # A2: "việt quất" (blueberry) must not fall through the "quất" rule below.
    (("tắc", "quất"), "5003", "Quất (tắc)"),
    (("chanh",), "14008", "Nước chanh tươi"),
    (("thanh long",), "5044", "thanh long"),
    (("chà là",), "5044", "Chà là"),
    (("nạc dăm", "thịt nạc heo", "thịt nạc"), "7017", "Thịt nạc heo (lợn)"),
    (("bắp bò",), "7094", "Thịt bắp bò"),
    (("thịt bò",), "7003", "Thịt bò nạc"),
    (("thịt gà", "chân gà"), "7013", "Thịt gà ta"),
    (("chả huế", "chả lụa"), "7069", "Giò lụa"),
    (("cá cam",), "20104", "Cá cam tươi (Amberjack)"),
    (("cá nục",), "8020", "Cá nục"),
    (("cá cơm khô", "cá cơm"), "8006", "Cá cơm khô"),
    (("tôm càng", "tôm đồng"), "8046", "Tôm đồng"),
    (("cua biển",), "8031", "Cua biển"),
    (("cá thác lác",), "8013", "Cá thát lát"),
    (("bột chiên giòn",), "13045", "Bột chiên giòn"),
    (("bột chiên xù",), "13067", "Bột chiên xù"),
    (("bột bánh xèo",), "1017", "Bột gạo"),
    (("tàu hũ ki", "tàu hủ ki", "váng đậu", "mì căn", "ham chay", "giò sống chay"), "3025", "Đậu phụ"),
    (("tiêu",), "13004", "Hạt tiêu"),
    (("ớt xiêm", "ớt sừng", "ớt"), "13039", "Ớt tươi"),
    (("nước ấm", "nước vo gạo", "nước lọc"), "20002", "Nước lọc (nước dùng nấu)"),
    (("bột màu điều", "hạt điều đỏ", "dầu điều"), "13056", "Bột hạt điều (dầu điều)"),
    (("lá cà ri", "hoa hồi", "đại hồi"), "20010", "Hoa hồi (đại hồi)"),
)

# A2: known containment collisions. A rule fires only when the query does not
# also match one of its listed false-positive supersets; the superset itself
# stays unresolved rather than being force-matched to the wrong identity.
_QWEN_MAPPER_EXCLUSIONS: dict[tuple[str, ...], tuple[str, ...]] = {
    ("cải xanh", "cải ngồng"): ("bông cải xanh",),
    ("tắc", "quất"): ("việt quất",),
    # Batch 2. "tiêu" is a bare word that three unrelated catalog identities
    # contain as a substring, each with its own code:
    #   tiêu xanh .... 20028 Tiêu xanh (hạt tiêu tươi) -- fresh green peppercorn
    #   bánh tiêu .... 12091 Bánh tiêu                 -- a fried dough pastry
    #   chuối tiêu ... 5007  Chuối tiêu                -- a banana cultivar
    # None of them is 13004 black pepper, so the generic rule abstains on them
    # rather than claiming them; re-pointing those rows is out of scope here.
    #
    # The last two are forward safety rather than a different food: they are
    # MIXTURES/processed forms whose nutrition is not plain peppercorn --
    #   muối tiêu ..... salt-and-pepper dip; the corpus links these to 13005
    #                   Muối ăn, never to 13004
    #   sốt tiêu đen .. bottled black-pepper sauce ("Nước tương sốt tiêu đen"),
    #   xốt tiêu đen .. and the same sauce under the x-spelling, which the
    #                   corpus also carries ("Xốt tiêu đen 1 muỗng canh").
    #                   One identity, two spellings -- not a second rule.
    # Phrase-level on purpose. "muối", "sốt", "xốt" and "đen" are NOT excluded
    # bare: "tiêu đen" and "hạt tiêu đen nguyên hạt" are plain peppercorn and
    # must still resolve, and a bare "đen" would block them.
    ("tiêu",): ("tiêu xanh", "bánh tiêu", "chuối tiêu",
                "muối tiêu", "sốt tiêu đen", "xốt tiêu đen"),
    # Batch 2. 7069 Giò lụa is pork. Three neighbouring identities exist in the
    # catalog or in the rows, and none may be absorbed by it:
    #   chay ......... 20040 Chả lụa chay (giò lụa chay) -- vegetarian
    #   bò ........... 7068  Giò bò                      -- beef
    #   gà ........... no catalog identity yet; "Chả lụa gà 200 gr" is a real
    #                  row, and poultry giò lụa is not the pork one. Blocked and
    #                  left unresolved rather than remapped.
    # "bò" and "gà" are deliberately NOT excluded bare: both appear inside
    # unrelated context words ("bún bò", "thịt gà" as a separate ingredient in a
    # compound line). Only the full identity heads are listed.
    ("chả huế", "chả lụa"): ("chay", "chả bò", "giò bò", "chả lụa bò", "chả lụa gà"),
}


def _norm_name(value: Any) -> str:
    return " ".join(str(value or "").strip().split()).casefold()


def build_mapper_rules(master_dict: dict[str, dict]) -> tuple[list[tuple], list[tuple]]:
    """Split hard-coded rules into (active, disabled) against the live catalog.

    A1: existence alone is not identity validation. A rule is active only when
    its code exists AND the catalog's current name_vi matches the hard-coded
    name; catalog drift silently relabels a code to a different ingredient
    over time, and a stale rule must not keep resolving against it.
    """
    active, disabled = [], []
    for terms, code, name in _QWEN_MAPPER_RULES:
        master_row = master_dict.get(code)
        if master_row is not None and _norm_name(master_row.get("name_vi")) == _norm_name(name):
            active.append((terms, code, name))
        else:
            disabled.append((terms, code, name, master_row.get("name_vi") if master_row else None))
    return active, disabled


def map_clean_to_master(clean_name: str, mapper_rules) -> tuple[str, str] | tuple[None, None]:
    """Resolve a Qwen-cleaned name to a validated (code, name) pair, or (None, None)."""
    c = (clean_name or "").lower()
    for terms, code, name in mapper_rules:
        exclusions = _QWEN_MAPPER_EXCLUSIONS.get(terms, ())
        if any(term in c for term in terms) and not any(bad in c for bad in exclusions):
            return code, name
    return None, None


# A6: qualifiers whose removal changes WHICH food the row denotes, not merely
# how it was prepared or packaged. Two groups, both reviewed:
#   ripeness / maturity ...... xanh, chín, sống, non, già
#   preservation / state ..... khô, tươi, muối
#   cultivar identity ........ keo, tượng
# Deliberately excluded: "thái" (cultivar AND the slicing verb -- see
# tests/test_green_mango_ripeness_guard.py), "ngâm"/"bào" and other preparation
# verbs, and plain colour words (đỏ, vàng, tím, trắng), which qualify variety
# rather than food identity and have no reviewed evidence behind them here.
CLEANED_NAME_PROTECTED_QUALIFIERS: frozenset[str] = frozenset(
    ("xanh", "chín", "sống", "non", "già", "khô", "tươi", "muối", "keo", "tượng")
)

_TOKEN_RE = re.compile(r"\w+", re.UNICODE)

_PARSER = VietnameseIngredientParser()


def _normalize_for_tokens(value: Any) -> str:
    """NFC + casefold, applied in that order and re-composed afterwards.

    casefold() can decompose a few code points, so the result is normalized
    again; without it two visually identical Vietnamese strings can tokenize to
    unequal tokens and a genuine narrowing would read as an unrelated reword.
    """
    text = unicodedata.normalize("NFC", str(value or ""))
    return unicodedata.normalize("NFC", text.casefold())


def _tokens(value: Any) -> list[str]:
    return _TOKEN_RE.findall(_normalize_for_tokens(value))


# Reviewed list shapes, not a general ingredient vocabulary. Full-string
# matching accepts only the small set of trailing forms seen in these fixtures.
_REVIEWED_RAW_LISTS = (
    ("hành lá và ngò rí", ("hành lá", "ngò rí")),
    ("hành lá, hành tím", ("hành lá", "hành tím")),
    ("ngò rí, hành lá", ("ngò rí", "hành lá")),
    ("tỏi băm, ngò rí", ("tỏi", "ngò rí")),
    ("ngò rí, ớt sừng", ("ngò rí", "ớt sừng")),
    ("rau nêm: hành lá, ngò gai", ("hành lá", "ngò gai")),
    ("xà lách/ dưa leo/ ớt sừng/ ngò rí", ("xà lách", "dưa leo", "ớt sừng", "ngò rí")),
)
_OUTPUT_LIST_SEPARATOR = re.compile(r"[/+;]|\s+-\s+|\b(?:và|hoặc|hay)\b")

# Reviewed lines whose food has NO exact catalog identity, pinned by exact raw
# text. Same mechanism as _REVIEWED_RAW_LISTS above -- a reviewed whole-line
# exclusion, matched through _list_text() -- for a different reviewed cause.
# _REVIEWED_RAW_LISTS refuses a line because Qwen collapsed a MULTI-ingredient
# line down to one member. These lines are single-ingredient and are extracted
# correctly; they simply have nowhere right to go. The mapper still resolves the
# cleaned output to a NEIGHBOURING identity, and publishing that neighbour would
# restate a reviewed UNMATCHED decision as a wrong match -- exactly the forced
# coverage AGENTS.md section 5 rejects, and the inverse of section 2's
# preference for UNMATCHED over a known-wrong target.
#
# Keyed on the whole raw line and nothing else, deliberately:
#   * a rule on the cleaned output "cải thảo" would block every fresh napa row,
#     all of which correctly reach 4109;
#   * a rule on "muối" or "khô" would block salt-pickled napa and kimchi, which
#     DO have catalog identities (4115 Dưa cải bắp, 20034 Kim chi) and are
#     matched correctly today;
#   * a rule on the winning code would block the whole 4109 rule.
# Only the exact reviewed lines below are refused. The code recorded with each
# is the neighbour the mapper WOULD have published, kept as evidence; the guard
# refuses the line whatever the mapper resolves it to, because the claim under
# review is "no exact catalog identity exists", not "not this one code".
_REVIEWED_NO_CATALOG_TARGET_RAW: dict[str, tuple[str, str]] = {
    # DISPLAY_NAME_BATCH_C1, row 2c660d89 `1 muỗng cải thảo muối khô`.
    # Dried salted napa. C1 cleared it to UNMATCHED by explicit reviewer
    # decision: its semantic identity is dried AND salted napa, the catalog
    # carries no such row, and the repaired 4016 `Cải xanh` is fresh mustard
    # greens. Clearing it made the row Qwen-eligible for the first time, and its
    # cached output "cải thảo" resolves to 4109 `Rau cải thảo` -- FRESH napa, a
    # different preparation with a different nutrition profile -- so a recovery
    # pass would silently undo the clear. Refused here, in the production guard.
    "1 muỗng cải thảo muối khô": ("4109", "DRIED_SALTED_NAPA_NO_EXACT_CATALOG_TARGET"),
}

# Explicit review evidence, independent of mapper rules, aliases and fuzzy
# matches. Exact whole fragments only; shared mapper targets are insufficient.
_REVIEWED_FRAGMENT_IDENTITIES = (
    (("hành lá", "hành hoa"), "4038", "Hành lá (hành hoa)"),
    (("nấm bào ngư", "nấm sò"), "20004", "Nấm bào ngư (nấm sò)"),
)


def _fragment_identity(fragment: str) -> tuple[str, str]:
    # Only terminal sentence punctuation is disposable. Preserve internal
    # punctuation, hyphens, parentheses and identity/state qualifiers.
    normalized = " ".join(_normalize_for_tokens(fragment).split()).rstrip(" .,!?:;…")
    for names, code, _ in _REVIEWED_FRAGMENT_IDENTITIES:
        if normalized in names:
            return "reviewed", code
    return "literal", normalized


def _list_text(value: str) -> str:
    text = " ".join(_normalize_for_tokens(value).split())
    return re.sub(r"\s*([,/:;])\s*", r"\1", text)


# Normalised once through the same function the guard compares against, so the
# table above stays readable as the reviewed raw text while the lookup is exact.
_REVIEWED_NO_CATALOG_TARGET_INDEX: dict[str, tuple[str, str]] = {
    _list_text(raw): value for raw, value in _REVIEWED_NO_CATALOG_TARGET_RAW.items()
}


def qwen_candidate_eligibility(
    raw_text: str, qwen_cleaned_name: str, winning_code: str | None = None,
) -> tuple[bool, str | None]:
    """Conservative first recovery guard; never a complete compound classifier.

    `winning_code` is from the validated mapper, not an existing row link.
    4081 uniquely identifies its ngò rule in the current table (it was 4073
    until DISPLAY_NAME_BATCH_A moved the coriander display name onto the code
    whose name_en always said Coriander). No remapping, catalog changes, or
    separator-free ingredient-head inference happens here.
    """
    output = " ".join(_normalize_for_tokens(qwen_cleaned_name).split())
    # Reviewed catalog-gap lines first: this is the most specific evidence there
    # is -- an exact reviewed raw line -- so it decides the reason rather than
    # letting a generic heuristic label the row. It refuses whatever the mapper
    # resolved to, because the reviewed claim is that no exact catalog identity
    # exists for the line at all.
    reviewed_gap = _REVIEWED_NO_CATALOG_TARGET_INDEX.get(_list_text(raw_text))
    if reviewed_gap is not None:
        return False, reviewed_gap[1]

    # Require textual items on both sides: fractions and quantity ranges alone
    # are not lists. Repetition, units and purpose/comparison clauses abstain.
    parts = _OUTPUT_LIST_SEPARATOR.split(output)
    non_item = re.compile(
        r"\b(?:để|dùng|trang trí|so với|như|muỗng|thìa|gram|ml|kg)\b"
    )
    if len(parts) > 1 and not non_item.search(output):
        items = [part.strip() for part in parts]
        if (all(any(char.isalpha() for char in part) for part in items)
                and not any(re.fullmatch(r"[\d.\s]+(?:g|gr|ml|kg)", part) for part in items)
                and not any(re.match(r"(?:rửa|cắt|thái|băm|chẻ)\b", part) for part in items)
                and len({_fragment_identity(part) for part in items}) > 1):
            return False, "qwen_explicit_ingredient_list"

    raw = _list_text(raw_text)
    for reviewed, members in _REVIEWED_RAW_LISTS:
        if re.fullmatch(
            re.escape(_list_text(reviewed))
            + r"(?::?\s*(?:1 ít|(?:10|20|50) gr|1 muỗng canh|bào|băm|cắt sợi))?",
            raw,
        ):
            retained = [member for member in members
                        if re.search(r"\b" + re.escape(member) + r"\b", output)]
            if len(retained) == 1:
                return False, "qwen_collapsed_reviewed_raw_list"

    if str(winning_code) == "4081" and re.search(r"\bngò\s+gai\b", raw):
        return False, "generic_ngo_conflicts_with_raw_ngo_gai"
    return True, None


def is_safe_cleaned_name_rewrite(parser_name: str, qwen_name: str) -> bool:
    """Is replacing the parser-derived name with the Qwen name lossless enough?

    Pure; no catalog, no row, no I/O. A rewrite is unsafe ONLY in the single
    narrow shape this guard exists for: the Qwen output is a contiguous run of
    parser tokens (i.e. a strict narrowing, not a reword) and the token
    IMMEDIATELY following that run is a protected qualifier -- the qualifier
    Qwen dropped. Anything else -- a reword, a reorder, an added token, a
    dropped preparation verb/unit/brand, a dropped colour -- is safe, so the
    existing behaviour is left exactly as it was.

    Adjacency is the whole rule: "hành lá thái nhỏ" -> "hành lá" drops only
    "thái nhỏ" and is safe, while "xoài keo" -> "xoài" drops the cultivar that
    distinguishes green mango from the ripe 5055 identity and is not.
    """
    parser_tokens = _tokens(parser_name)
    qwen_tokens = _tokens(qwen_name)
    if not qwen_tokens or len(qwen_tokens) >= len(parser_tokens):
        return True

    span = len(qwen_tokens)
    # `- span` and not `- span + 1`: a run ending at the very last parser token
    # has no following token, so it can never have dropped a trailing qualifier.
    for start in range(len(parser_tokens) - span):
        if parser_tokens[start:start + span] != qwen_tokens:
            continue
        if parser_tokens[start + span] in CLEANED_NAME_PROTECTED_QUALIFIERS:
            return False
    return True


def resolve_cleaned_name_update(
    raw_text: str, qwen_name: str, parser: VietnameseIngredientParser | None = None
) -> str | None:
    """The Qwen cleaned_name to write for `raw_text`, or None to leave it alone.

    The baseline is RE-DERIVED from raw_text by the grammar parser. The row's
    stored cleaned_name is deliberately not consulted: historical rows may
    already hold a damaged Qwen output, and comparing against that would make
    the loss invisible and self-confirming.

    None means "do not modify cleaned_name" -- stage_qwen_update() already
    treats it that way, so rejecting the rewrite never blocks the row's
    match/code/weight update.
    """
    if qwen_name is None or not str(qwen_name).strip():
        return None
    parser_name = (parser or _PARSER).parse(str(raw_text or "")).name
    return qwen_name if is_safe_cleaned_name_rewrite(parser_name, qwen_name) else None


def resolve_qwen_row(
    row: dict,
    master_dict: dict[str, dict],
    weight: float,
    candidate: tuple[str, str, str] | None,
    cleaned_name: str | None = None,
) -> dict | None:
    """Stage the update for one ingredient row, or None if nothing changes.

    `candidate` is (code, name, method) from a cure rule or map_clean_to_master,
    or None when only a weight correction applies. A candidate whose code is
    dangling/invalid is rejected outright (A4): no matching field is written,
    but an independent weight correction on the same row still applies (A5),
    and match_confidence is stamped only when a validated match is written.
    """
    match_fields = None
    if candidate is not None:
        code, name, method = candidate
        match_fields = dict(zip(MATCH_FIELDS, (str(code), name, method, QWEN_MATCH_CONFIDENCE)))

    try:
        return stage_qwen_update(row, master_dict, weight, match_fields=match_fields, cleaned_name=cleaned_name)
    except ValueError:
        if match_fields is None:
            raise
        # Candidate rejected: retry as a weight-only patch so an independent,
        # already-validated weight correction is not blocked by an unrelated
        # invalid match candidate.
        return stage_qwen_update(row, master_dict, weight, match_fields=None)


def eligible_for_qwen_recovery(row: dict) -> bool:
    """A3: recovery requires BOTH the code and the name to be genuinely missing."""
    return not has_master_link(row)
