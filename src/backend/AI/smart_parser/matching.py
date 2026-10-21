"""Multi-tier culinary ingredient matching against master catalog and FreshCheck index."""

from __future__ import annotations

import logging
import math
import re
import unicodedata
from collections import Counter
from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from typing import Any

from AI.smart_parser.normalization import (
    normalize_text,
    strip_brand_noise,
    strip_classifier_prefix,
    strip_vietnamese_accents,
)

logger = logging.getLogger(__name__)

# Common Vietnamese regional culinary synonyms mapping to standard terms
COMMON_REGIONAL_SYNONYMS: dict[str, str] = {
    "ba rọi": "thịt ba chỉ",
    "thịt ba rọi": "thịt ba chỉ",
    "thịt ba rọi rút sườn": "thịt ba chỉ",
    "ba rọi heo": "thịt ba chỉ",
    "ba chỉ heo": "thịt ba chỉ",
    "cá lóc": "cá quả",
    "cá quả": "cá quả",
    "cá tràu": "cá quả",
    "tàu hũ": "đậu phụ",
    "tàu hũ non": "đậu phụ",
    "đậu hũ": "đậu phụ",
    "đậu hũ non": "đậu phụ",
    "ngao": "nghêu",
    "ngao sống": "nghêu",
    "rau muống nước": "rau muống",
    "trứng gà ta": "trứng gà",
    "trứng gà công nghiệp": "trứng gà",
    "trứng vịt lộn": "trứng vịt",
    "thịt heo xay": "thịt nạc",
    "thịt băm": "thịt nạc",
    "thịt xay": "thịt nạc",
    "chả cá nha trang": "chả cá",
    "đậu rồng": "đậu rồng",
    "má đùi gà": "thịt gà",
    "đùi gà": "thịt gà",
    "cánh gà": "thịt gà",
    "chân giò heo": "chân giò",
    "xương heo": "xương lợn",
    "bắp cải trắng": "bắp cải",
}

# Candidates scoring below this IDF-weighted token-F1 are not a credible match.
MIN_MATCH_SCORE = 0.5
# Diacritic agreement between a query token and a catalog token of the same letters:
# tone-only (hủ/hũ) and d/đ (diêu/điêu) variants are near-spellings of one word, while
# a vowel-shape clash or accents against a toneless word (nhỏ/nho) is a different word.
TONE_ONLY_SIMILARITY = 0.9
STROKE_VARIANT_SIMILARITY = 0.8
ACCENT_CONFLICT_SIMILARITY = 0.6
# Each later query token counts this much less (head noun first, modifiers after).
POSITION_DECAY = 0.1
# An alias may lack some of its own tokens in the query (nhân in "bánh bao nhân thịt"),
# but must be covered for at least this share of its IDF mass.
MIN_ALIAS_COVERAGE = 0.7
# A partial-alias match needs this score, and must beat a full-alias one by the margin.
MIN_PARTIAL_SCORE = 0.65
PARTIAL_MARGIN = 0.15
# Another ingredient matching a disjoint part of the query at this fraction of the
# winner's score makes the query ambiguous.
AMBIGUITY_RATIO = 0.8
_TONE_MARKS = frozenset("\u0300\u0301\u0303\u0309\u0323")

_PARENTHETICAL_RE = re.compile(r"\([^)]*\)")
_TOKEN_RE = re.compile(r"[^\W_]+")
_QUANTITY_TOKEN_RE = re.compile(r"^\d+[a-z]*$|^(?:g|gr|gram|kg|ml|l)$")


@dataclass(frozen=True)
class _Alias:
    """One searchable catalog name: accented and unaccented tokens plus its master."""

    acc: tuple[str, ...]
    un: tuple[str, ...]
    entry: dict[str, Any]


def _tokenize(text: str) -> list[str]:
    return _TOKEN_RE.findall(text.lower())


def _is_ascii(text: str) -> bool:
    return text.isascii()


def _is_quantity_token(token: str) -> bool:
    return bool(_QUANTITY_TOKEN_RE.match(token))


def _strip_tone(token: str) -> str:
    """Remove tone marks only, keeping vowel shape (ê, ơ, â) and đ."""
    decomposed = unicodedata.normalize("NFD", token)
    kept = "".join(c for c in decomposed if c not in _TONE_MARKS)
    return unicodedata.normalize("NFC", kept)


def _accent_similarity(query_token: str, alias_token: str) -> float:
    """How well the diacritics of two same-letter tokens agree.

    An ASCII query token carries no accent information, so it matches anything.
    An accented query token against a toneless catalog word is a different word
    (nhỏ vs nho). Otherwise tone and d/đ differences are mild, vowel-shape ones not.
    """
    if _is_ascii(query_token) or query_token == alias_token:
        return 1.0
    if _is_ascii(alias_token):
        return ACCENT_CONFLICT_SIMILARITY
    q_base, a_base = _strip_tone(query_token), _strip_tone(alias_token)
    similarity = 1.0
    if q_base != a_base:
        if q_base.replace("đ", "d") != a_base.replace("đ", "d"):
            return ACCENT_CONFLICT_SIMILARITY
        similarity *= STROKE_VARIANT_SIMILARITY
    if _tone_of(query_token) != _tone_of(alias_token):
        similarity *= TONE_ONLY_SIMILARITY
    return similarity


def _tone_of(token: str) -> str:
    """The tone marks of a token, in order (empty for the level tone)."""
    return "".join(
        c for c in unicodedata.normalize("NFD", token) if c in _TONE_MARKS
    )


def _position_weight(index: int) -> float:
    """Vietnamese noun phrases are head-first: earlier tokens name the ingredient."""
    return 1.0 / (1.0 + POSITION_DECAY * index)


def _ordered_overlap(
    q_acc: list[str],
    q_un: list[str],
    alias: _Alias,
    idf: Mapping[str, float],
) -> tuple[float, float]:
    """Best ordered token alignment of a query and an alias.

    Returns (query-side mass, alias-side mass): the first is IDF weight discounted
    by token position and accent agreement, the second plain IDF of the alias tokens
    that were matched, to tell how much of the alias the query actually covers.
    """
    rows, cols = len(q_un), len(alias.un)
    table = [[(0.0, 0.0)] * (cols + 1) for _ in range(rows + 1)]
    for i in range(rows):
        for j in range(cols):
            best = max(table[i][j + 1], table[i + 1][j])
            if q_un[i] == alias.un[j]:
                weight, mass = table[i][j]
                token_idf = idf.get(q_un[i], 1.0)
                similarity = _accent_similarity(q_acc[i], alias.acc[j])
                best = max(
                    best,
                    (
                        weight + token_idf * _position_weight(i) * similarity,
                        mass + token_idf,
                    ),
                )
            table[i + 1][j + 1] = best
    return table[rows][cols]


def count_master_usage(
    ingredients: Iterable[Mapping[str, Any]],
) -> dict[str, int]:
    """Count how many recipe ingredient rows reference each master code."""
    counts: Counter[str] = Counter()
    for row in ingredients:
        code = _clean_code(row.get("master_ingredient_code"))
        if code:
            counts[code] += 1
    return dict(counts)


def _clean_code(code: object) -> str:
    if code is None:
        return ""
    s = str(code).strip().removesuffix(".0")
    return "" if s.lower() == "nan" else s


def _extract_nutrition(row: Mapping[str, Any]) -> dict[str, float]:
    def _safe_float(val: object) -> float:
        try:
            return float(str(val or 0.0))
        except (ValueError, TypeError):
            return 0.0

    return {
        "energy_kcal": _safe_float(row.get("energy_kcal")),
        "protein_g": _safe_float(row.get("protein_g")),
        "fat_g": _safe_float(row.get("fat_g")),
        "carbs_g": _safe_float(row.get("carbs_g")),
    }


class PantryMatcher:
    """Multi-tier ingredient resolution against Viện Dinh Dưỡng master rows and FreshCheck KB."""

    def __init__(
        self,
        *,
        master_alias_index: (
            Mapping[str, tuple[str, ...] | list[str] | set[str]] | None
        ) = None,
        master_by_code: Mapping[str, dict[str, Any]] | None = None,
        fresh_kb: dict[str, Any] | None = None,
        master_usage: Mapping[str, int] | None = None,
    ) -> None:
        self.master_alias_index = master_alias_index or {}
        self.master_by_code: dict[str, dict[str, Any]] = (
            dict(master_by_code) if master_by_code else {}
        )
        self.fresh_kb = fresh_kb or {}
        self.master_usage: Mapping[str, int] = master_usage or {}

        self.alias_to_master: dict[str, dict[str, Any]] = {}
        self.unaccented_to_master: dict[str, dict[str, Any]] = {}

        self._build_indexes()

    def _build_indexes(self) -> None:
        """Construct fast lookup maps from master catalog, aliases, and FreshCheck KB."""
        # 1. Index master rows directly
        for code, row in self.master_by_code.items():
            entry = self._build_master_entry(code, row)
            canonical_name = normalize_text(entry["name"])
            if canonical_name:
                self.alias_to_master[canonical_name] = entry
                self.unaccented_to_master[
                    strip_vietnamese_accents(canonical_name)
                ] = entry

        # 2. Index alias index from CatalogSnapshot / master_index
        for alias, codes in self.master_alias_index.items():
            first_code = next(iter(codes), "")
            first_code_clean = _clean_code(first_code)
            if not first_code_clean:
                continue

            entry = self.alias_to_master.get(
                normalize_text(alias)
            ) or self._build_master_entry(
                first_code_clean,
                self.master_by_code.get(first_code_clean, {}),
            )
            norm_alias = normalize_text(alias)
            if norm_alias:
                self.alias_to_master.setdefault(norm_alias, entry)
                unacc = strip_vietnamese_accents(norm_alias)
                self.unaccented_to_master.setdefault(unacc, entry)

        # 3. Index FreshCheck KB synonyms and ingredient names
        for f_data in self.fresh_kb.get("ingredients", {}).values():
            f_code = _clean_code(f_data.get("code"))
            entry = (
                self.master_by_code.get(f_code)
                if f_code
                else None
            )
            master_entry = (
                self._build_master_entry(f_code, entry)
                if entry
                else None
            )

            for name_vi in f_data.get("names_vi", []):
                norm_f_name = normalize_text(name_vi)
                if norm_f_name and master_entry and norm_f_name not in self.alias_to_master:
                    self.alias_to_master[norm_f_name] = master_entry
                    self.unaccented_to_master.setdefault(
                        strip_vietnamese_accents(norm_f_name), master_entry
                    )

        # 4. Link regional synonyms to master entries
        for syn, target in COMMON_REGIONAL_SYNONYMS.items():
            norm_target = normalize_text(target)
            target_entry = self.alias_to_master.get(norm_target)
            if not target_entry:
                # Try unaccented lookup for target
                target_entry = self.unaccented_to_master.get(
                    strip_vietnamese_accents(norm_target)
                )

            if target_entry:
                # A synonym only fills a gap: a real catalog name always wins.
                norm_syn = normalize_text(syn)
                self.alias_to_master.setdefault(norm_syn, target_entry)
                self.unaccented_to_master.setdefault(
                    strip_vietnamese_accents(norm_syn), target_entry
                )

        self._build_token_index()

    def _build_token_index(self) -> None:
        """Index aliases by unaccented token; one entry per (tokens, code)."""
        merged: dict[tuple[tuple[str, ...], str], _Alias] = {}
        for alias_text, entry in self.alias_to_master.items():
            acc = tuple(_tokenize(alias_text))
            if not acc:
                continue
            un = tuple(strip_vietnamese_accents(t) for t in acc)
            key = (un, entry["code"])
            known = merged.get(key)
            # Keep the accented spelling when both an accented and an ASCII form exist.
            if known is None or (
                all(_is_ascii(t) for t in known.acc)
                and not all(_is_ascii(t) for t in acc)
            ):
                merged[key] = _Alias(acc=acc, un=un, entry=entry)
        self._aliases = list(merged.values())
        self._token_index: dict[str, list[int]] = {}
        for alias_id, alias in enumerate(self._aliases):
            if not alias.un:
                continue
            for token in set(alias.un):
                self._token_index.setdefault(token, []).append(alias_id)
        total = len(self._aliases)
        # Rare tokens identify an ingredient; ubiquitous ones (cá, thịt, nguyên) barely do.
        self._idf: dict[str, float] = {
            token: math.log((total + 1) / (len(ids) + 1)) + 1.0
            for token, ids in self._token_index.items()
        }

    def _build_master_entry(
        self, code: str, row: Mapping[str, Any]
    ) -> dict[str, Any]:
        canonical_name = str(row.get("name_vi") or row.get("name") or code)
        category = str(row.get("category_vi") or row.get("category") or "")
        nutrition = _extract_nutrition(row) if row else None
        return {
            "code": code,
            "name": canonical_name,
            "category": category,
            "nutrition": nutrition,
        }

    def _informative_tokens(self, text: str) -> list[str]:
        """Query tokens that can carry matching signal: known words, not quantities."""
        return [
            t
            for t in _tokenize(text)
            if strip_vietnamese_accents(t) in self._token_index
            and not _is_quantity_token(t)
        ]

    def resolve_master_ingredient(
        self, query: str
    ) -> dict[str, Any] | None:
        """Resolve a free-text ingredient name to the best master ingredient.

        Accent-bearing exact catalog names win immediately. Everything else is
        scored over one pool of accented and unaccented aliases: the alias and
        the query must be ordered sub-sequences of one another, accents the
        query carries must agree, and candidates rank by token F1, accent
        agreement and how often recipes use the ingredient. Weak candidates
        (< MIN_MATCH_SCORE) return None instead of a guess.
        """
        if not query or not query.strip():
            return None

        q = normalize_text(query)
        if not _is_ascii(q) and q in self.alias_to_master:
            return dict(self.alias_to_master[q], match_score=1.0)

        cleaned = strip_brand_noise(strip_classifier_prefix(q))
        # "(GÓI)", "(HỘP)", "(200GR)" describe the package, not the ingredient.
        core = _PARENTHETICAL_RE.sub(" ", cleaned)
        q_acc = self._informative_tokens(core) or self._informative_tokens(cleaned)
        if not q_acc:
            return None
        q_un = [strip_vietnamese_accents(t) for t in q_acc]

        candidate_ids: set[int] = set()
        for token in set(q_un):
            candidate_ids.update(self._token_index.get(token, ()))

        query_weight = sum(
            self._idf.get(t, 1.0) * _position_weight(i) for i, t in enumerate(q_un)
        )
        # A "full" alias is entirely present in the query; a "partial" one lacks some of
        # its own words. Full aliases are stronger evidence, so a partial alias only wins
        # by a clear margin and above a higher bar.
        full: list[tuple[tuple[float, int, float, int], _Alias, float]] = []
        best_partial: tuple[tuple[float, int, float, int], _Alias, float] | None = None
        for alias_id in candidate_ids:
            alias = self._aliases[alias_id]
            matched_weight, alias_mass = _ordered_overlap(
                q_acc, q_un, alias, self._idf
            )
            alias_weight = sum(self._idf.get(t, 1.0) for t in alias.un)
            if alias_mass < MIN_ALIAS_COVERAGE * alias_weight:
                continue
            score = 2.0 * matched_weight / (alias_weight + query_weight)
            if score < MIN_MATCH_SCORE:
                continue
            accent_hits = sum(
                1
                for qa, aa in zip(q_acc, alias.acc, strict=False)
                if qa == aa and not _is_ascii(qa)
            )
            popularity = math.log1p(self.master_usage.get(alias.entry["code"], 0))
            candidate = (
                (round(score, 2), accent_hits, popularity, -len(alias.un)),
                alias,
                score,
            )
            if alias_mass >= alias_weight - 1e-9:
                full.append(candidate)
            elif best_partial is None or candidate[0] > best_partial[0]:
                best_partial = candidate

        chosen = max(full, key=lambda c: c[0]) if full else None
        if (
            best_partial is not None
            and best_partial[2] >= MIN_PARTIAL_SCORE
            and (chosen is None or best_partial[2] >= chosen[2] + PARTIAL_MARGIN)
        ):
            chosen = best_partial
        if chosen is None:
            return None
        if self._is_ambiguous(chosen, full):
            return None
        return dict(chosen[1].entry, match_score=round(chosen[2], 3))

    @staticmethod
    def _is_ambiguous(
        chosen: tuple[tuple[float, int, float, int], _Alias, float],
        full: list[tuple[tuple[float, int, float, int], _Alias, float]],
    ) -> bool:
        """True when another ingredient explains a different part of the query as well.

        "xương gà" is neither a pork bone (xương) nor a chicken (gà): two masters that
        share no word and score alike mean the query names something the catalog lacks.
        """
        chosen_alias = chosen[1]
        for _key, alias, score in full:
            if (
                alias.entry["code"] != chosen_alias.entry["code"]
                and set(alias.un).isdisjoint(chosen_alias.un)
                and score >= AMBIGUITY_RATIO * chosen[2]
            ):
                return True
        return False
