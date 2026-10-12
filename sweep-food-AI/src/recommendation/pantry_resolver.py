"""Pantry ingredient resolver for mapping free-text ingredient names to master VDD codes.

Rule: exact-match lookup only (unicodedata NFC normalized, lowercased, collapsed whitespace).
Ambiguity policy: when a normalized key maps to multiple master codes, all codes are kept
in resolved_codes to maximize recall across recipe variants.
Parenthesized inner text in master ingredient names is NOT extracted as separate alias keys.
"""

from __future__ import annotations

import re
import unicodedata
from typing import Any, Iterable, Mapping


def normalize(text: str | None) -> str:
    """Normalize text: unicodedata NFC, lowercase, strip, collapse whitespace."""
    if not text:
        return ""
    norm = unicodedata.normalize("NFC", str(text))
    norm = norm.lower().strip()
    return re.sub(r"\s+", " ", norm)


def _clean_code(code: Any) -> str:
    """Normalize code string, stripping whitespace and trailing '.0'."""
    if code is None:
        return ""
    s = str(code).strip()
    if s.endswith(".0"):
        s = s[:-2]
    if not s or s == "nan":
        return ""
    return s


def build_master_alias_index(master_rows: Any) -> dict[str, tuple[str, ...]]:
    """Build deterministic master alias index from master rows or DataFrame.

    Keys:
      - normalized `name_vi`
      - normalized `name_vi` with parenthesized parts removed
      - every normalized `;`-separated alias
    Values:
      - sorted unique master codes as strings. Deterministic.
    """
    index: dict[str, set[str]] = {}

    if hasattr(master_rows, "to_dict") and callable(master_rows.to_dict):
        records = master_rows.to_dict(orient="records")
    else:
        records = master_rows

    for row in records:
        if isinstance(row, Mapping):
            code_val = row.get("code")
            name_val = row.get("name_vi")
            aliases_val = row.get("aliases")
        else:
            code_val = getattr(row, "code", None)
            name_val = getattr(row, "name_vi", None)
            aliases_val = getattr(row, "aliases", None)

        code_str = _clean_code(code_val)
        if not code_str:
            continue

        keys: set[str] = set()

        if name_val is not None:
            name_str = str(name_val).strip()
            if name_str and name_str != "nan":
                n1 = normalize(name_str)
                if n1:
                    keys.add(n1)
                without_parens = re.sub(r"\(.*?\)", "", name_str)
                n2 = normalize(without_parens)
                if n2:
                    keys.add(n2)

        if aliases_val is not None:
            aliases_str = str(aliases_val).strip()
            if aliases_str and aliases_str != "nan":
                for alias in aliases_str.split(";"):
                    a = normalize(alias)
                    if a:
                        keys.add(a)

        for k in keys:
            if k not in index:
                index[k] = set()
            index[k].add(code_str)

    return {k: tuple(sorted(codes)) for k, codes in sorted(index.items())}


def resolve_pantry_items(
    items: Iterable[dict[str, Any]], index: Mapping[str, tuple[str, ...] | list[str]]
) -> list[dict[str, Any]]:
    """Resolve free-text pantry item names to master ingredient codes.

    Returns new dicts (does not mutate input). For each item adds `resolved_codes`
    = sorted codes for `normalize(item['name'])` (exact key lookup only, no substring/fuzzy),
    or `[]`. Explicit item `code` is kept untouched.
    """
    resolved: list[dict[str, Any]] = []
    for it in items:
        new_it = dict(it)
        name = it.get("name") or ""
        norm_name = normalize(name)
        codes = index.get(norm_name, ())
        new_it["resolved_codes"] = sorted(codes)
        resolved.append(new_it)
    return resolved


def get_effective_codes(item: Mapping[str, Any]) -> set[str]:
    """Return effective master codes for a pantry item: {code} ∪ resolved_codes."""
    codes: set[str] = set()
    raw_code = item.get("code")
    clean_c = _clean_code(raw_code)
    if clean_c:
        codes.add(clean_c)
    for rc in item.get("resolved_codes") or []:
        clean_rc = _clean_code(rc)
        if clean_rc:
            codes.add(clean_rc)
    return codes
