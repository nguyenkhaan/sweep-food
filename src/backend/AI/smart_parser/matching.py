"""Multi-tier culinary ingredient matching against master catalog and FreshCheck index."""

from __future__ import annotations

import logging
import re
from collections.abc import Mapping
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
    ) -> None:
        self.master_alias_index = master_alias_index or {}
        self.master_by_code: dict[str, dict[str, Any]] = (
            dict(master_by_code) if master_by_code else {}
        )
        self.fresh_kb = fresh_kb or {}

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
                norm_syn = normalize_text(syn)
                self.alias_to_master[norm_syn] = target_entry
                self.unaccented_to_master[
                    strip_vietnamese_accents(norm_syn)
                ] = target_entry

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

    def resolve_master_ingredient(
        self, query: str
    ) -> dict[str, Any] | None:
        """Resolve a free-text ingredient name using multi-tier matching.

        Tier 1: Exact alias match in normalized dictionary.
        Tier 2:
          - Classifier prefix stripped match
          - Supermarket brand noise stripped match
          - Unaccented match (diacritics removed)
          - Longest word-boundary match (len >= 3)
          - Longest substring match fallback (len >= 4)
        """
        if not query or not query.strip():
            return None

        q = normalize_text(query)

        # Tier 1: Exact match in alias index
        if q in self.alias_to_master:
            return self.alias_to_master[q]

        # Tier 2: Prefix classifier stripped
        stripped = strip_classifier_prefix(q)
        if stripped and stripped in self.alias_to_master:
            return self.alias_to_master[stripped]

        # Tier 2: Brand & supermarket noise stripped
        cleaned_sm = strip_brand_noise(stripped or q)
        if cleaned_sm and cleaned_sm in self.alias_to_master:
            return self.alias_to_master[cleaned_sm]

        # Tier 2: Unaccented match
        unacc_q = strip_vietnamese_accents(cleaned_sm or stripped or q)
        if unacc_q in self.unaccented_to_master:
            return self.unaccented_to_master[unacc_q]

        # Tier 2: Longest word-boundary match
        best_match: dict[str, Any] | None = None
        best_len = 0
        target_str = cleaned_sm or stripped or q

        for alias, entry in self.alias_to_master.items():
            if len(alias) > best_len and len(alias) >= 3 and re.search(
                r"\b" + re.escape(alias) + r"\b", target_str, re.IGNORECASE
            ):
                best_len = len(alias)
                best_match = entry

        if not best_match:
            for unacc_alias, entry in self.unaccented_to_master.items():
                if len(unacc_alias) > best_len and len(unacc_alias) >= 3 and re.search(
                    r"\b" + re.escape(unacc_alias) + r"\b",
                    unacc_q,
                    re.IGNORECASE,
                ):
                    best_len = len(unacc_alias)
                    best_match = entry

        # Fallback substring match if no word-boundary match found
        if not best_match:
            for alias, entry in self.alias_to_master.items():
                if len(alias) > best_len and len(alias) >= 4 and alias in target_str:
                    best_len = len(alias)
                    best_match = entry

        if not best_match:
            for unacc_alias, entry in self.unaccented_to_master.items():
                if len(unacc_alias) > best_len and len(unacc_alias) >= 4 and unacc_alias in unacc_q:
                    best_len = len(unacc_alias)
                    best_match = entry
        return best_match
