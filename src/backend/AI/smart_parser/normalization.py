"""Text normalization, diacritics removal, brand stripping, and unit conversions."""

from __future__ import annotations

import re
import unicodedata

CLASSIFIER_PREFIX_REGEX = re.compile(
    r"^(?:bó|bo|quả|qua|trái|trai|củ|cu|con|miếng|mieng|lát|lat|đĩa|dia|khay|vỉ|vi|hộp|hop|túi|tui|bắp|bap|bìa|bia|gói|goi|nải|nai|chùm|chum|cây|cay)\s+",
    re.IGNORECASE,
)

BRAND_NOISE_REGEX = re.compile(
    r"\b(?:c\.p|cp|vissan|meat\s*deli|g\s*kitchen|ba\s*huân|vinmart|winmart|bhx|ls|kg|gr?|gram)\b",
    re.IGNORECASE,
)

# Preparation / presentation phrases that describe how an item is sold, not what it is.
PREPARATION_NOISE_REGEX = re.compile(
    r"\b(?:làm\s+sạch|lam\s+sach|cắt\s+khúc|cat\s+khuc|cắt\s+lát|cat\s+lat|"
    r"nguyên\s+con|nguyen\s+con|đông\s+lạnh|dong\s+lanh|nhập\s+khẩu|nhap\s+khau)\b",
    re.IGNORECASE,
)

QUANTITY_UNIT_PATTERN = re.compile(
    r"(?:(\d+(?:[.,]\d+)?)\s*(kg|kí|ký|ki|ky|g|gr|gram|lạng|lang|cân|can|quả|qua|trái|trai|bó|bo|củ|cu|con|bìa|bia|hộp|hop|vỉ|vi|khay|gói|goi)?|"
    r"(nửa)\s*(cân|kg|kí|ký|lạng))",
    re.IGNORECASE,
)

DEFAULT_UNIT_WEIGHTS_G: dict[str, float] = {
    "quả": 80.0,
    "qua": 80.0,
    "trái": 80.0,
    "trai": 80.0,
    "bó": 350.0,
    "bo": 350.0,
    "củ": 150.0,
    "cu": 150.0,
    "con": 700.0,
    "bìa": 150.0,
    "bia": 150.0,
    "miếng": 150.0,
    "mieng": 150.0,
    "lát": 50.0,
    "lat": 50.0,
    "khay": 400.0,
    "vỉ": 400.0,
    "vi": 400.0,
    "hộp": 300.0,
    "hop": 300.0,
    "túi": 500.0,
    "tui": 500.0,
    "bắp": 250.0,
    "bap": 250.0,
    "gói": 200.0,
    "goi": 200.0,
}

# Specific ingredient unit overrides
FOOD_UNIT_OVERRIDES_G: dict[str, dict[str, float]] = {
    "cà chua": {"quả": 75.0, "qua": 75.0, "trái": 75.0, "trai": 75.0},
    "ca chua": {"quả": 75.0, "qua": 75.0, "trái": 75.0, "trai": 75.0},
    "trứng": {"quả": 60.0, "qua": 60.0, "trái": 60.0, "trai": 60.0},
    "trung": {"quả": 60.0, "qua": 60.0, "trái": 60.0, "trai": 60.0},
    "trứng gà": {"quả": 60.0, "qua": 60.0, "trái": 60.0, "trai": 60.0},
    "trung ga": {"quả": 60.0, "qua": 60.0, "trái": 60.0, "trai": 60.0},
    "trứng vịt": {"quả": 70.0, "qua": 70.0, "trái": 70.0, "trai": 70.0},
    "trung vit": {"quả": 70.0, "qua": 70.0, "trái": 70.0, "trai": 70.0},
    "chanh": {"quả": 40.0, "qua": 40.0, "trái": 40.0, "trai": 40.0},
    "ớt": {"quả": 10.0, "qua": 10.0, "trái": 10.0, "trai": 10.0},
    "ot": {"quả": 10.0, "qua": 10.0, "trái": 10.0, "trai": 10.0},
    "hành tây": {"củ": 150.0, "cu": 150.0},
    "hanh tay": {"củ": 150.0, "cu": 150.0},
    "khoai tây": {"củ": 150.0, "cu": 150.0},
    "khoai tay": {"củ": 150.0, "cu": 150.0},
    "cà rốt": {"củ": 120.0, "cu": 120.0},
    "ca rot": {"củ": 120.0, "cu": 120.0},
    "bắp cải": {"bắp": 600.0, "bap": 600.0, "cây": 600.0, "cay": 600.0},
    "bap cai": {"bắp": 600.0, "bap": 600.0, "cây": 600.0, "cay": 600.0},
    "rau muống": {"bó": 500.0, "bo": 500.0},
    "rau muong": {"bó": 500.0, "bo": 500.0},
}


def strip_vietnamese_accents(text: str) -> str:
    """Convert Vietnamese text to unaccented lowercase (e.g. 'cá điêu hồng' -> 'ca dieu hong')."""
    if not text:
        return ""
    norm = unicodedata.normalize("NFD", text)
    res = "".join(c for c in norm if unicodedata.category(c) != "Mn")
    return res.replace("đ", "d").replace("Đ", "D").strip().lower()


def normalize_text(text: str | None) -> str:
    """Normalize text: Unicode NFC, lowercased, stripped, and collapsed whitespace."""
    if not text:
        return ""
    norm = unicodedata.normalize("NFC", str(text))
    norm = norm.lower().strip()
    return re.sub(r"\s+", " ", norm)


def strip_classifier_prefix(text: str) -> str:
    """Remove leading Vietnamese noun classifiers (e.g. '3 quả cà chua' or 'bó rau muống')."""
    return CLASSIFIER_PREFIX_REGEX.sub("", text).strip()


def strip_brand_noise(text: str) -> str:
    """Remove brand names, packaging/preparation phrases and unit noise from a label."""
    cleaned = BRAND_NOISE_REGEX.sub("", PREPARATION_NOISE_REGEX.sub("", text))
    return re.sub(r"\s+", " ", cleaned).strip()


def detect_storage_mode(text: str) -> str:
    """Infer target storage compartment from natural Vietnamese text cues."""
    norm = normalize_text(text)
    if any(k in norm for k in ["ngăn đá", "tủ đông", "cấp đông", "đông lạnh", "freezer"]):
        return "freezer_-18c"
    if any(k in norm for k in ["nhiệt độ phòng", "ngoài trời", "để ngoài", "nhiệt độ thường", "bếp"]):
        return "room_temp_25_30c"
    return "fridge_2_4c"


def parse_quantity_and_clean_name(
    raw_name: str, fallback_g: float = 200.0
) -> tuple[str, float, str]:
    """Parse numeric quantity, determine gram equivalent, and return cleaned food name.

    Returns:
        tuple of (cleaned_name, quantity_g, quantity_source)
    """
    text = raw_name.strip()
    qty_g: float | None = None
    qty_source = "estimated"

    # 1. Check 'nửa cân' / 'nửa kg' / 'nửa lạng'
    m_nua = re.search(r"nửa\s*(cân|kg|kí|ký|lạng)", text, re.IGNORECASE)
    if m_nua:
        unit = m_nua.group(1).lower()
        if unit in ("cân", "kg", "kí", "ký"):
            qty_g = 500.0
        elif unit == "lạng":
            qty_g = 50.0
        qty_source = "extracted"
        text = text[: m_nua.start()] + " " + text[m_nua.end() :]

    # 2. Check standard number + unit pattern: e.g. 500g, 0.5 kg, 2 lạng, 3 quả
    if qty_g is None:
        m_qty = re.search(
            r"(\d+(?:[.,]\d+)?)\s*(kg|kí|ký|ki|ky|g|gr|gram|lạng|lang|cân|can|quả|qua|trái|trai|bó|bo|củ|cu|con|bìa|bia|hộp|hop|vỉ|vi|khay|gói|goi)?\b",
            text,
            re.IGNORECASE,
        )
        if m_qty:
            raw_val_str = m_qty.group(1).replace(",", ".")
            try:
                val = float(raw_val_str)
                unit = (m_qty.group(2) or "").lower()
                if unit in ("kg", "kí", "ký", "cân"):
                    qty_g = val * 1000.0
                    qty_source = "extracted"
                elif unit == "lạng":
                    qty_g = val * 100.0
                    qty_source = "extracted"
                elif unit in ("g", "gr", "gram"):
                    qty_g = val
                    qty_source = "extracted"
                elif unit in DEFAULT_UNIT_WEIGHTS_G:
                    # Item count to estimated gram
                    base_unit_weight = DEFAULT_UNIT_WEIGHTS_G[unit]
                    # Check overrides for known foods
                    lowered = text.lower()
                    unacc_lowered = strip_vietnamese_accents(lowered)
                    for food_key, overrides in FOOD_UNIT_OVERRIDES_G.items():
                        if (food_key in lowered or food_key in unacc_lowered) and unit in overrides:
                            base_unit_weight = overrides[unit]
                            break
                    qty_g = round(val * base_unit_weight, 1)
                    qty_source = "estimated"
                elif 0.0 < val <= 5.0 and not unit:
                    # Likely kg in supermarket OCR (e.g. '0.70' or '0,298')
                    qty_g = round(val * 1000.0, 1)
                    qty_source = "extracted"
                else:
                    qty_g = val
                    qty_source = "extracted"

                text = text[: m_qty.start()] + " " + text[m_qty.end() :]
            except ValueError:
                pass

    if qty_g is None or qty_g <= 0.0:
        qty_g = fallback_g
        qty_source = "estimated"

    # Clean remaining string
    cleaned = strip_classifier_prefix(text)
    cleaned = strip_brand_noise(cleaned)
    cleaned = re.sub(r"[^\w\s\u00C0-\u1EF9]", " ", cleaned)
    cleaned = re.sub(r"\s+", " ", cleaned).strip()

    return cleaned or raw_name.strip(), round(qty_g, 1), qty_source
