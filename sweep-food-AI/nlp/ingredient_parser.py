"""Vietnamese Ingredient Text Parser.

Extracts structured quantity, measurement unit, raw ingredient name,
and preparation notes from unstructured recipe ingredient strings.
"""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass
from typing import Any


@dataclass
class ParsedIngredient:
    raw_text: str
    quantity: float | None
    unit: str | None
    canonical_unit: str | None
    name: str
    preparation_note: str | None
    is_optional: bool

    def to_dict(self) -> dict[str, Any]:
        return {
            "raw_text": self.raw_text,
            "quantity": self.quantity,
            "unit": self.unit,
            "canonical_unit": self.canonical_unit,
            "name": self.name,
            "preparation_note": self.preparation_note,
            "is_optional": self.is_optional,
        }


# Unicode fraction mapping
UNICODE_FRACTIONS = {
    "½": 0.5,
    "⅓": 0.333,
    "⅔": 0.667,
    "¼": 0.25,
    "¾": 0.75,
    "⅕": 0.2,
    "⅖": 0.4,
    "⅗": 0.6,
    "⅘": 0.8,
    "⅙": 0.167,
    "⅚": 0.833,
    "⅛": 0.125,
    "⅜": 0.375,
    "⅝": 0.625,
    "⅞": 0.875,
}

# Unit mapping to canonical MeasurementUnit
CANONICAL_UNIT_MAP = {
    # Mass
    "kg": "KG",
    "kí": "KG",
    "kilogram": "KG",
    "kilo": "KG",
    "g": "GRAM",
    "gr": "GRAM",
    "gram": "GRAM",
    "gam": "GRAM",
    "lạng": "GRAM",  # 1 lạng = 100g, handled in quantity multiplier
    "lb": "LB",
    "lbs": "LB",
    "pound": "LB",
    "pounds": "LB",
    # Volume
    "l": "LITER",
    "lít": "LITER",
    "liter": "LITER",
    "ml": "ML",
    "mililit": "ML",
    # Discrete
    "quả": "PIECE",
    "trái": "PIECE",
    "củ": "PIECE",
    "cây": "PIECE",
    "bắp": "PIECE",
    "búp": "PIECE",
    "con": "PIECE",
    "tép": "PIECE",
    "nhánh": "PIECE",
    "cọng": "PIECE",
    "lát": "PIECE",
    "miếng": "PIECE",
    "khúc": "PIECE",
    "lá": "PIECE",
    "tai": "PIECE",
    "bó": "PACK",
    "nắm": "PIECE",
    "gói": "PACK",
    "hộp": "PACK",
    "lon": "PACK",
    "bịch": "PACK",
    "túi": "PACK",
    # Spoons / Culinary
    "muỗng cà phê": "OTHER",
    "thìa cà phê": "OTHER",
    "mcf": "OTHER",
    "tsp": "OTHER",
    "muỗng canh": "OTHER",
    "thìa canh": "OTHER",
    "muỗng súp": "OTHER",
    "thìa súp": "OTHER",
    "tbsp": "OTHER",
    "muỗng": "OTHER",
    "thìa": "OTHER",
    "chén": "OTHER",
    "bát": "OTHER",
    "tách": "OTHER",
    "ly": "OTHER",
    "nhúm": "OTHER",
    "chút": "OTHER",
    "ít": "OTHER",
}

# Sorted unit list by length descending to match multi-word units first
SORTED_UNITS = sorted(CANONICAL_UNIT_MAP.keys(), key=len, reverse=True)
UNITS_REGEX_PATTERN = r"\b(" + "|".join(re.escape(u) for u in SORTED_UNITS) + r")\b"


class VietnameseIngredientParser:
    """Parser for Vietnamese recipe ingredient text lines."""

    def __init__(self) -> None:
        self.unit_regex = re.compile(UNITS_REGEX_PATTERN, re.IGNORECASE)

    def normalize_text(self, text: str) -> str:
        """Clean whitespace and Unicode normalization."""
        text = unicodedata.normalize("NFC", text)
        text = re.sub(r"\s+", " ", text).strip()
        return text

    def parse_fraction(self, s: str) -> float | None:
        """Parse fractions like '1/2', '1 1/2', or Unicode '½'."""
        s = s.strip()
        for uchar, uval in UNICODE_FRACTIONS.items():
            if uchar in s:
                s = s.replace(uchar, f" {uval} ")

        # Match '1 1/2'
        mixed_match = re.match(r"^(\d+)\s+(\d+)\s*/\s*(\d+)$", s)
        if mixed_match:
            whole, num, den = mixed_match.groups()
            return float(whole) + float(num) / float(den)

        # Match '1/2'
        frac_match = re.match(r"^(\d+)\s*/\s*(\d+)$", s)
        if frac_match:
            num, den = frac_match.groups()
            return float(num) / float(den)

        # Match decimal or integer
        try:
            return float(s.replace(",", "."))
        except ValueError:
            return None

    def parse(self, text: str) -> ParsedIngredient:
        """Parse a single raw ingredient string."""
        raw_text = text.strip()
        cleaned = self.normalize_text(raw_text)

        # 1. Check optionality
        is_optional = False
        optional_keywords = ["tùy thích", "tùy chọn", "nếu có", "nếu thích", "trang trí", "nêm nếm vừa ăn"]
        for kw in optional_keywords:
            if kw in cleaned.lower():
                is_optional = True
                cleaned = re.sub(rf"\b{re.escape(kw)}\b", "", cleaned, flags=re.IGNORECASE)

        # 2. Extract preparation note in parentheses: e.g. "thịt heo (thái mỏng)"
        prep_note = None
        paren_match = re.search(r"\((.*?)\)", cleaned)
        if paren_match:
            prep_note = paren_match.group(1).strip()
            cleaned = re.sub(r"\(.*?\)", "", cleaned).strip()

        # Check preparation note after comma or hyphen
        if not prep_note and ("," in cleaned or " - " in cleaned):
            parts = re.split(r",|\s-\s", cleaned, 1)
            candidate_note = parts[1].strip()
            # If the second part has no digits or units, it's likely a prep note
            if not re.search(r"\d", candidate_note) and len(candidate_note.split()) <= 5:
                prep_note = candidate_note
                cleaned = parts[0].strip()

        # 3. Extract quantity: leading numbers or ranges e.g. "300g", "1-2 quả", "1/2 muỗng"
        quantity = None
        qty_unit_prefix_pattern = (
            r"^([0-9\.,\s\/\-–½⅓⅔¼¾⅕⅖⅗⅘⅙⅚⅛⅜⅝⅞]+)\s*"
        )
        match_qty = re.match(qty_unit_prefix_pattern, cleaned)

        unit_str = None
        canonical_unit = None
        remaining_name = cleaned

        if match_qty:
            qty_part = match_qty.group(1).strip()
            # Handle range: e.g. "1-2" -> average 1.5
            range_match = re.match(r"^(\d+(?:[\.,]\d+)?)\s*[-–]\s*(\d+(?:[\.,]\d+)?)$", qty_part)
            if range_match:
                low = float(range_match.group(1).replace(",", "."))
                high = float(range_match.group(2).replace(",", "."))
                quantity = (low + high) / 2.0
            else:
                quantity = self.parse_fraction(qty_part)

            remaining_name = cleaned[match_qty.end():].strip()

        # 4. Check for Unit in the remaining text or at the beginning
        # Check if unit is at the very beginning of remaining_name
        unit_match = self.unit_regex.match(remaining_name)
        if unit_match:
            unit_str = unit_match.group(1).lower()
            remaining_name = remaining_name[unit_match.end():].strip()
        else:
            # Check unit anywhere in the remaining text if quantity was at the end e.g. "thịt heo 300g"
            trailing_match = re.search(
                r"\s+([0-9\.,\s\/\-½⅓⅔¼¾]+)\s*(" + "|".join(re.escape(u) for u in SORTED_UNITS) + r")?$",
                remaining_name,
                re.IGNORECASE,
            )
            if trailing_match and quantity is None:
                quantity = self.parse_fraction(trailing_match.group(1))
                if trailing_match.group(2):
                    unit_str = trailing_match.group(2).lower()
                remaining_name = remaining_name[:trailing_match.start()].strip()

        # Resolve canonical unit
        if unit_str:
            canonical_unit = CANONICAL_UNIT_MAP.get(unit_str, "OTHER")
            # Special multiplier: 1 lạng = 100g
            if unit_str == "lạng" and quantity is not None:
                quantity = quantity * 100.0
                canonical_unit = "GRAM"

        # 5. Clean final ingredient name
        # Strip leading prepositions: "của", "từ", "khoảng", "khoảng chừng"
        remaining_name = re.sub(r"^(khoảng|chừng|tầm)\s+", "", remaining_name, flags=re.IGNORECASE)
        remaining_name = re.sub(r"^(của|cho)\s+", "", remaining_name, flags=re.IGNORECASE)
        remaining_name = remaining_name.strip(" :-.,")

        return ParsedIngredient(
            raw_text=raw_text,
            quantity=quantity,
            unit=unit_str,
            canonical_unit=canonical_unit,
            name=remaining_name,
            preparation_note=prep_note,
            is_optional=is_optional,
        )

    def parse_batch(self, texts: list[str], max_workers: int | None = None) -> list[ParsedIngredient]:
        """Parse a batch of raw ingredient strings in parallel or vectorized."""
        if not texts:
            return []

        # For small to medium lists, list comprehension is fastest in Python
        if len(texts) < 100 or max_workers == 1:
            return [self.parse(t) for t in texts]

        # Multi-threaded parsing for very large recipe datasets (e.g. > 1000 items)
        from concurrent.futures import ThreadPoolExecutor

        workers = max_workers or 4
        with ThreadPoolExecutor(max_workers=workers) as executor:
            return list(executor.map(self.parse, texts))
