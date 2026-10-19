"""Vietnamese Culinary Speech NLP Parser."""

from __future__ import annotations

import re
from typing import Any

from AI.extraction.ocr.receipt_parser import (
    FOOD_KNOWLEDGE,
    _lookup_expiry_and_staple,
)

# Spoken aliases mapping common colloquial terms to canonical food names
FOOD_ALIASES: dict[str, str] = {
    "gà": "thịt gà",
    "bò": "thịt bò",
    "heo": "thịt heo",
    "lợn": "thịt heo",
    "trứng": "trứng gà",
    "đậu": "đậu phụ",
    "tôm sú": "tôm",
    "rau": "rau muống",
}

# Spoken number dictionary
NUMBER_WORDS: dict[str, float] = {
    "nửa": 0.5,
    "rưỡi": 0.5,
    "một": 1.0,
    "hai": 2.0,
    "ba": 3.0,
    "bốn": 4.0,
    "năm": 5.0,
    "sáu": 6.0,
    "bảy": 7.0,
    "tám": 8.0,
    "chín": 9.0,
    "mười": 10.0,
    "trăm": 100.0,
}

# Unit multipliers (grams)
UNIT_MULTIPLIERS: dict[str, float] = {
    "cân": 1000.0,
    "ký": 1000.0,
    "kg": 1000.0,
    "kilo": 1000.0,
    "lạng": 100.0,
    "gram": 1.0,
    "gam": 1.0,
    "g": 1.0,
    "bó": 300.0,
    "con": 1200.0,
    "bìa": 100.0,
    "miếng": 100.0,
    "hộp": 500.0,
    "gói": 300.0,
    "túi": 500.0,
    "khay": 400.0,
    "vỉ": 200.0,
    "củ": 150.0,
    "trái": 100.0,
    "quả": 80.0,
}


def parse_spoken_quantity_grams(
    segment: str, food_name: str
) -> tuple[float, bool]:
    """Extracts numeric weight from spoken context around the food item.

    Returns:
        (weight_g, is_extracted_flag)
    """
    s = segment.lower().strip()

    # 1. Look for numeric digit patterns: e.g. "400 gram", "1.5 kg", "3 lạng", "2 quả"
    digit_unit_match = re.search(
        r"(\d+([.,]\d+)?)\s*(gram|g|kg|ký|kilo|cân|lạng|bó|bắp|bìa|con|quả|trái|củ)\b",
        s,
    )
    if digit_unit_match:
        val = float(digit_unit_match.group(1).replace(",", "."))
        u = digit_unit_match.group(3)
        mult = UNIT_MULTIPLIERS.get(u, 1.0)
        return round(val * mult, 1), True

    # 2. Look for explicit compound weight terms: "ký rưỡi" -> 1500g, "nửa cân" -> 500g
    if "ký rưỡi" in s or "cân rưỡi" in s:
        return 1500.0, True
    if "nửa cân" in s or "nửa ký" in s or "nửa kg" in s:
        return 500.0, True
    if "nửa bắp" in s:
        return 200.0, True

    # 3. Look for "X lạng", "X trăm gram", "X quả", etc.
    for num_w, num_val in NUMBER_WORDS.items():
        if f"{num_w} lạng" in s:
            return round(num_val * 100.0, 1), True
        if f"{num_w} trăm gram" in s:
            return round(num_val * 100.0, 1), True
        if f"{num_w} cân" in s or f"{num_w} ký" in s:
            return round(num_val * 1000.0, 1), True
        if f"{num_w} bó" in s:
            return round(num_val * 300.0, 1), True
        if f"{num_w} quả" in s or f"{num_w} trái" in s:
            unit_w = 100.0 if "cà chua" in food_name else 50.0
            return round(num_val * unit_w, 1), True
        if f"{num_w} bìa" in s or f"{num_w} miếng" in s:
            return round(num_val * 120.0, 1), True
        if f"{num_w} con" in s:
            return round(num_val * 1200.0, 1), True
        if f"{num_w} củ" in s:
            return round(num_val * 60.0, 1), True

    # Fallback to domain baseline knowledge
    for key, info in FOOD_KNOWLEDGE.items():
        if key in food_name.lower():
            return float(info["default_w"]), False

    return 250.0, False


def parse_vietnamese_speech(transcript: str) -> list[dict[str, Any]]:
    """Analyzes spoken Vietnamese transcript and returns structured culinary items."""
    t = transcript.lower()
    items: list[dict[str, Any]] = []

    # Combined candidate food list (standard foods + colloquial aliases)
    all_candidates = list(FOOD_KNOWLEDGE.keys()) + list(FOOD_ALIASES.keys())
    # Sort descending by length so longer multi-word phrases match first
    all_candidates = sorted(set(all_candidates), key=len, reverse=True)

    # Find non-overlapping character spans in the transcript
    occupied_spans: list[tuple[int, int]] = []
    matches: list[tuple[int, int, str, str]] = []

    for cand in all_candidates:
        pattern = r"\b" + re.escape(cand) + r"\b"
        for m in re.finditer(pattern, t):
            s, e = m.start(), m.end()
            # Check if span overlaps with any previously accepted longer span
            if not any(
                max(s, occ_s) < min(e, occ_e) for occ_s, occ_e in occupied_spans
            ):
                occupied_spans.append((s, e))
                canonical = FOOD_ALIASES.get(cand, cand)
                matches.append((s, e, cand, canonical))

    # Sort matches chronologically by position in the transcript
    matches.sort(key=lambda x: x[0])

    prev_end = 0
    for idx, (start, end, raw_phrase, canonical_name) in enumerate(matches):
        next_start = matches[idx + 1][0] if idx + 1 < len(matches) else len(t)

        # Context window: text immediately preceding this food, plus text up to next food or conjunction
        context_before = t[prev_end:start].strip()
        if re.search(r"\b(và|với|rồi|kèm|thêm|,)\b", context_before):
            parts = re.split(r"\b(?:và|với|rồi|kèm|thêm|,)\b", context_before)
            context_before = parts[-1].strip()

        context_after = t[end:next_start].strip()
        # Trim context_after at first conjunction if present
        conj_match = re.search(r"\b(và|với|rồi|kèm|thêm|,)\b", context_after)
        if conj_match:
            context_after = context_after[: conj_match.start()].strip()

        local_context = f"{context_before} {raw_phrase} {context_after}".strip()
        prev_end = end

        weight_g, is_extracted = parse_spoken_quantity_grams(
            local_context, canonical_name
        )
        expiry_h, is_staple = _lookup_expiry_and_staple(canonical_name)

        items.append(
            {
                "name": canonical_name.capitalize(),
                "raw_name": raw_phrase,
                "spoken_phrase": local_context,
                "quantity_g": weight_g,
                "quantity_source": "extracted" if is_extracted else "estimated",
                "unit": "g",
                "hours_to_expire": float(expiry_h),
                "is_staple": bool(is_staple),
                "confidence": 0.95,
            }
        )

    return items
