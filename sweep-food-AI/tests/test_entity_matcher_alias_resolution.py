"""Regression tests for nlp/entity_matcher.py's preset-alias resolution
(master code 5054 "Vu sua" false-positive investigation).

Root cause: VietnameseIngredientMatcher.match()/match_batch() used to
resolve preset aliases with
`alias_dict.get(query_norm) or alias_dict.get(cleaned_q)`. Python treats
catalog index 0 as falsy, and code 10001 ("Sua tuoi khong duong", the
correct identity for fresh milk) sits at index 0 in the real catalog. So a
query whose exact form correctly resolved to 10001 fell through to the
cleaned-name lookup instead -- and clean_culinary_query() separately strips
the bare word "tuoi" as freshness noise, turning "sua tuoi" into "sua",
which (via the since-removed bare "sua" alias in
data/processed/viendinhduong/ingredient_alias_map.json) resolved to the
wrong identity, code 5054 ("Vu sua", the starapple fruit).

See scripts/eda/audit_master_5054_matching.py and
scripts/eda/apply_master_5054_safe_fix.py for the data-side cleanup of rows
already affected before this fix landed.

No GPU/model/catalog CSV is loaded; a minimal in-memory catalog and alias
dict are built directly on the instance via __new__, matching the pattern
used by nlp/qwen_matching.py's own pure-function tests.
"""

import json
from pathlib import Path

from nlp.entity_matcher import VietnameseIngredientMatcher, normalize_vietnamese_text

ALIAS_MAP_PATH = (
    Path(__file__).resolve().parent.parent
    / "data" / "processed" / "viendinhduong" / "ingredient_alias_map.json"
)

CATALOG = [
    {"code": "10001", "name_vi": "Sữa tươi không đường", "category_vi": "Sữa và sản phẩm sữa"},
    {"code": "5054", "name_vi": "Vú sữa", "category_vi": "Quả chín"},
]

# Mirrors the real ingredient_alias_map.json entries relevant to this bug,
# post-fix (no bare "sữa" alias).
ALIASES = {
    "sữa tươi": "10001",
    "sữa tươi không đường": "10001",
    "vú sữa": "5054",
    "vú sữa tươi": "5054",
}


def _make_matcher(catalog, aliases):
    """Build a matcher instance without touching disk or any model -- only
    the attributes match()/match_batch()/_resolve_alias() actually read."""
    m = VietnameseIngredientMatcher.__new__(VietnameseIngredientMatcher)
    m.catalog = catalog
    m.catalog_names = [c["name_vi"] for c in catalog]
    m.normalized_to_index = {
        normalize_vietnamese_text(c["name_vi"]): idx for idx, c in enumerate(catalog)
    }
    m.catalog_subphrase_items = []
    code_to_idx = {c["code"]: idx for idx, c in enumerate(catalog)}
    m.alias_dict = {
        normalize_vietnamese_text(alias): code_to_idx[code] for alias, code in aliases.items()
    }
    return m


def test_code_10001_sits_at_catalog_index_zero_precondition():
    """The bug depended on this precondition: the correct milk identity is
    the first catalog row (index 0), which Python treats as falsy."""
    matcher = _make_matcher(CATALOG, ALIASES)
    assert matcher.alias_dict[normalize_vietnamese_text("sữa tươi")] == 0


def test_sua_tuoi_resolves_to_milk_not_vu_sua():
    """Historical matcher/index-0 falsiness bug: 'a or b' treated index 0 as
    falsy and fell through to the cleaned-name lookup, which (with the old
    bare 'sữa' alias) landed on code 5054. Must now resolve to 10001."""
    matcher = _make_matcher(CATALOG, ALIASES)
    result = matcher.match("sữa tươi")
    assert result["matched_item"]["code"] == "10001"
    assert result["method"] == "PRESET_ALIAS_MATCH"


def test_bare_sua_does_not_resolve_via_alias_stage():
    """With the unsafe bare 'sữa' alias removed, a bare 'sữa' query must not
    resolve through the alias stage at all -- "sữa" alone is ambiguous
    (fresh, powdered, condensed milk, ...) and must not be force-mapped to
    any single code here; it should fall through to later matching stages."""
    matcher = _make_matcher(CATALOG, ALIASES)
    query_norm = normalize_vietnamese_text("sữa")
    cleaned_q = normalize_vietnamese_text("sữa")
    assert matcher._resolve_alias(query_norm, cleaned_q) is None


def test_legitimate_vu_sua_still_resolves_to_5054():
    matcher = _make_matcher(CATALOG, ALIASES)
    result = matcher.match("vú sữa")
    assert result["matched_item"]["code"] == "5054"


def test_legitimate_vu_sua_alias_lookup_resolves_to_5054():
    matcher = _make_matcher(CATALOG, ALIASES)
    query_norm = normalize_vietnamese_text("vú sữa tươi")
    assert matcher._resolve_alias(query_norm, "unrelated cleaned text") == 1


def test_resolve_alias_prefers_exact_query_over_cleaned_when_both_present():
    """Generic index-0 regression, not specific to milk/fruit: an exact
    query resolving to index 0 must win over a cleaned-query candidate that
    resolves to a different index -- index 0 is a valid match, not a falsy
    'no match' sentinel."""
    matcher = _make_matcher(CATALOG, ALIASES)
    exact = normalize_vietnamese_text("sữa tươi")  # -> index 0
    cleaned = normalize_vietnamese_text("vú sữa")  # -> index 1
    assert matcher._resolve_alias(exact, cleaned) == 0


def test_resolve_alias_falls_back_to_cleaned_when_exact_query_unresolved():
    matcher = _make_matcher(CATALOG, ALIASES)
    cleaned = normalize_vietnamese_text("vú sữa")
    assert matcher._resolve_alias("unresolvable query text", cleaned) == 1


def test_resolve_alias_returns_none_when_neither_resolves():
    matcher = _make_matcher(CATALOG, ALIASES)
    assert matcher._resolve_alias("nothing matches this", "nor this") is None


def test_no_bare_sua_alias_in_processed_alias_map():
    """Data-side guard: the unsafe bare alias must not silently reappear."""
    alias_map = json.loads(ALIAS_MAP_PATH.read_text(encoding="utf-8"))
    assert "sữa" not in alias_map


def test_legitimate_vu_sua_aliases_still_present_in_processed_alias_map():
    alias_map = json.loads(ALIAS_MAP_PATH.read_text(encoding="utf-8"))
    assert alias_map.get("vú sữa") == "5054"
    assert alias_map.get("vú sữa tươi") == "5054"
