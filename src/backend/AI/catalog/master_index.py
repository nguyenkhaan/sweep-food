"""Pantry ingredient resolver and master alias index.

Provides exact-match lookup from free-text ingredient names to master Viện Dinh Dưỡng codes.
Ambiguity policy: when a normalized key maps to multiple master codes, all codes are kept
in resolved_codes to maximize recall across recipe variants.
"""

from __future__ import annotations

import re
import unicodedata
from collections.abc import Iterable, Mapping
from typing import Any


def normalize(text: str | None) -> str:
    """Normalize text: unicodedata NFC, lowercase, strip, collapse whitespace."""
    if not text:
        return ""
    norm = unicodedata.normalize("NFC", str(text))
    norm = norm.lower().strip()
    return re.sub(r"\s+", " ", norm)


def _clean_code(code: object) -> str:
    """Normalize code string, stripping whitespace and trailing '.0'."""
    if code is None:
        return ""
    s = str(code).strip().removesuffix(".0")
    if not s or s.lower() == "nan":
        return ""
    return s


def build_master_alias_index(
    master_rows: Iterable[Mapping[str, object]] | Any,
) -> dict[str, tuple[str, ...]]:
    """Build deterministic master alias index from master rows or objects.

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
            if name_str and name_str.lower() != "nan":
                n1 = normalize(name_str)
                if n1:
                    keys.add(n1)
                without_parens = re.sub(r"\(.*?\)", "", name_str)
                n2 = normalize(without_parens)
                if n2:
                    keys.add(n2)

        if aliases_val is not None:
            aliases_str = str(aliases_val).strip()
            if aliases_str and aliases_str.lower() != "nan":
                for alias in aliases_str.split(";"):
                    a = normalize(alias)
                    if a:
                        keys.add(a)

        for k in keys:
            if k not in index:
                index[k] = set()
            index[k].add(code_str)

    return {k: tuple(sorted(codes)) for k, codes in sorted(index.items())}


def _quantity(value: object) -> float:
    try:
        return float(value)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return 0.0


def _soonest_hours(first: object, second: object) -> object:
    """Return the smaller known expiry horizon; None means unknown."""
    if first is None:
        return second
    if second is None:
        return first
    return min(float(first), float(second))  # type: ignore[arg-type]


def merge_pantry_items(items: Iterable[Mapping[str, Any]]) -> list[dict[str, Any]]:
    """Merge pantry entries that name the same ingredient into one item.

    Each inventory batch may arrive as its own entry. Entries are keyed by
    `normalize(item['name'])`; a merged item sums `quantity_g`, keeps the soonest
    known `hours_to_expire`, keeps the first non-empty `code`, and stays a staple
    only when every entry is one. First-seen order is kept. Returns new dicts.
    """
    merged: dict[str, dict[str, Any]] = {}
    for it in items:
        key = normalize(it.get("name"))
        current = merged.get(key)
        if current is None:
            merged[key] = dict(it)
            continue
        current["quantity_g"] = _quantity(current.get("quantity_g")) + _quantity(
            it.get("quantity_g")
        )
        current["hours_to_expire"] = _soonest_hours(
            current.get("hours_to_expire"), it.get("hours_to_expire")
        )
        if not _clean_code(current.get("code")) and _clean_code(it.get("code")):
            current["code"] = it.get("code")
        current["is_staple"] = bool(current.get("is_staple")) and bool(
            it.get("is_staple")
        )
    return list(merged.values())


def resolve_pantry_items(
    items: Iterable[dict[str, Any]],
    index: Mapping[str, tuple[str, ...] | list[str]],
) -> list[dict[str, Any]]:
    """Resolve free-text pantry item names to master ingredient codes.

    Returns new dicts (does not mutate input). For each item adds `resolved_codes`
    = sorted codes for `normalize(item['name'])` (exact key lookup only),
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
