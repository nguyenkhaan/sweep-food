"""Vietnamese Supermarket Receipt NLP & Entity Parser."""

from __future__ import annotations

import re
import unicodedata
from typing import Any


def remove_accents(input_str: str) -> str:
    """Removes Vietnamese accents for robust matching of unaccented thermal receipt print."""
    nfkd = unicodedata.normalize("NFKD", input_str)
    return (
        "".join([c for c in nfkd if not unicodedata.combining(c)])
        .replace("đ", "d")
        .replace("Đ", "D")
        .lower()
    )


# Non-food blacklist for Vietnamese retail receipts (checked on unaccented text)
NON_FOOD_UNACCENTED = [
    "nuoc rua chen", "sunlight", "nuoc lau san", "xa phong", "lifebuoy",
    "bot giat", "nuoc xa", "comfort", "downy", "khan giay", "giay ve sinh",
    "khan uot", "bobby", "tui nilon", "tui tieu chuan", "tui dung", "tui xop",
    "ban chai", "kem danh rang", "dau goi", "sua tam", "dao cao", "pin panasonic",
    "giay cuon", "nuoc tay", "vim", "p/s", "puri", "softly", "sting", "tra xanh 190g",
    "kdr", "loc 10 cuon", "thanh toan", "tien mat", "diem su dung", "tong dai", "ma tra cuu",
    "quy khach", "hoa don", "chinh sach", "hd vat", "tich diem",
]

# Food classification knowledge base with baseline weights and shelf lives
FOOD_KNOWLEDGE: dict[str, dict[str, Any]] = {
    # Fresh Meat & Seafood (24 - 48h)
    "thịt bò": {"default_w": 350.0, "expiry_h": 36.0, "is_staple": False},
    "xương que heo": {"default_w": 600.0, "expiry_h": 36.0, "is_staple": False},
    "xương heo": {"default_w": 600.0, "expiry_h": 36.0, "is_staple": False},
    "sườn heo": {"default_w": 500.0, "expiry_h": 36.0, "is_staple": False},
    "thịt ba chỉ": {"default_w": 400.0, "expiry_h": 36.0, "is_staple": False},
    "ba rọi heo": {"default_w": 400.0, "expiry_h": 36.0, "is_staple": False},
    "thịt heo": {"default_w": 400.0, "expiry_h": 36.0, "is_staple": False},
    "thịt xay": {"default_w": 300.0, "expiry_h": 24.0, "is_staple": False},
    "thịt gà": {"default_w": 500.0, "expiry_h": 36.0, "is_staple": False},
    "ức gà": {"default_w": 400.0, "expiry_h": 36.0, "is_staple": False},
    "cá điêu hồng": {"default_w": 700.0, "expiry_h": 24.0, "is_staple": False},
    "cá hồi": {"default_w": 300.0, "expiry_h": 24.0, "is_staple": False},
    "cá chép": {"default_w": 600.0, "expiry_h": 24.0, "is_staple": False},
    "cá basa": {"default_w": 400.0, "expiry_h": 24.0, "is_staple": False},
    "tôm thẻ": {"default_w": 350.0, "expiry_h": 24.0, "is_staple": False},
    "tôm": {"default_w": 350.0, "expiry_h": 24.0, "is_staple": False},
    "mực ống": {"default_w": 400.0, "expiry_h": 24.0, "is_staple": False},
    "mực": {"default_w": 350.0, "expiry_h": 24.0, "is_staple": False},
    "đậu hũ": {"default_w": 250.0, "expiry_h": 48.0, "is_staple": False},
    "đậu phụ": {"default_w": 250.0, "expiry_h": 48.0, "is_staple": False},
    "trứng gà": {"default_w": 500.0, "expiry_h": 240.0, "is_staple": False},
    "trứng vịt": {"default_w": 600.0, "expiry_h": 240.0, "is_staple": False},
    "trứng cút": {"default_w": 200.0, "expiry_h": 168.0, "is_staple": False},

    # Fresh Vegetables, Tubers & Fruits (48 - 240h)
    "bắp cải thảo": {"default_w": 500.0, "expiry_h": 120.0, "is_staple": False},
    "cải thảo": {"default_w": 500.0, "expiry_h": 120.0, "is_staple": False},
    "bắp cải trắng": {"default_w": 500.0, "expiry_h": 120.0, "is_staple": False},
    "bắp cải": {"default_w": 500.0, "expiry_h": 120.0, "is_staple": False},
    "cải bẹ xanh": {"default_w": 300.0, "expiry_h": 48.0, "is_staple": False},
    "cải ngọt": {"default_w": 250.0, "expiry_h": 48.0, "is_staple": False},
    "cải thìa": {"default_w": 250.0, "expiry_h": 48.0, "is_staple": False},
    "rau muống": {"default_w": 300.0, "expiry_h": 48.0, "is_staple": False},
    "giá sống": {"default_w": 300.0, "expiry_h": 48.0, "is_staple": False},
    "giá đỗ": {"default_w": 300.0, "expiry_h": 48.0, "is_staple": False},
    "bí xanh": {"default_w": 500.0, "expiry_h": 120.0, "is_staple": False},
    "bí đao": {"default_w": 500.0, "expiry_h": 120.0, "is_staple": False},
    "cà chua": {"default_w": 300.0, "expiry_h": 72.0, "is_staple": False},
    "khoai tây": {"default_w": 500.0, "expiry_h": 240.0, "is_staple": False},
    "cà rốt": {"default_w": 250.0, "expiry_h": 144.0, "is_staple": False},
    "dưa leo": {"default_w": 250.0, "expiry_h": 72.0, "is_staple": False},
    "dưa chuột": {"default_w": 250.0, "expiry_h": 72.0, "is_staple": False},
    "dưa hấu": {"default_w": 1500.0, "expiry_h": 168.0, "is_staple": False},
    "táo gala": {"default_w": 500.0, "expiry_h": 168.0, "is_staple": False},
    "táo": {"default_w": 500.0, "expiry_h": 168.0, "is_staple": False},
    "cam sành": {"default_w": 500.0, "expiry_h": 168.0, "is_staple": False},
    "chanh không hạt": {"default_w": 200.0, "expiry_h": 168.0, "is_staple": False},
    "chanh": {"default_w": 200.0, "expiry_h": 168.0, "is_staple": False},
    "cóc lớn": {"default_w": 500.0, "expiry_h": 168.0, "is_staple": False},
    "cóc": {"default_w": 500.0, "expiry_h": 168.0, "is_staple": False},
    "nấm kim châm": {"default_w": 150.0, "expiry_h": 48.0, "is_staple": False},
    "nấm đùi gà": {"default_w": 200.0, "expiry_h": 72.0, "is_staple": False},

    # Prepared foods & bakery
    "bánh giò": {"default_w": 150.0, "expiry_h": 24.0, "is_staple": False},
    "bánh mì": {"default_w": 300.0, "expiry_h": 48.0, "is_staple": False},

    # Seasonings & Staples (Long shelf life: 720h+)
    "hành lá": {"default_w": 50.0, "expiry_h": 48.0, "is_staple": True},
    "hành tây": {"default_w": 250.0, "expiry_h": 168.0, "is_staple": False},
    "hành tím": {"default_w": 100.0, "expiry_h": 360.0, "is_staple": True},
    "tỏi": {"default_w": 100.0, "expiry_h": 480.0, "is_staple": True},
    "gừng": {"default_w": 80.0, "expiry_h": 360.0, "is_staple": True},
    "sả": {"default_w": 100.0, "expiry_h": 120.0, "is_staple": True},
    "ớt": {"default_w": 30.0, "expiry_h": 168.0, "is_staple": True},
    "nước mắm": {"default_w": 500.0, "expiry_h": 720.0, "is_staple": True},
    "dầu ăn": {"default_w": 500.0, "expiry_h": 720.0, "is_staple": True},
    "hạt nêm": {"default_w": 250.0, "expiry_h": 720.0, "is_staple": True},
    "đường": {"default_w": 500.0, "expiry_h": 720.0, "is_staple": True},
    "muối": {"default_w": 500.0, "expiry_h": 720.0, "is_staple": True},
    "tiêu": {"default_w": 50.0, "expiry_h": 720.0, "is_staple": True},
}

# Precompile list sorted by unaccented keyword length descending
FOOD_KNOWLEDGE_LIST = sorted(
    [(name, remove_accents(name), meta) for name, meta in FOOD_KNOWLEDGE.items()],
    key=lambda x: len(x[1]),
    reverse=True,
)


def _lookup_expiry_and_staple(food_name: str) -> tuple[float, bool]:
    """Finds estimated hours until expiration and staple status."""
    fn = food_name.lower().strip()
    for name, meta in FOOD_KNOWLEDGE.items():
        if name in fn:
            return meta["expiry_h"], meta["is_staple"]
    return 72.0, False


def _normalize_ocr_line(line: str) -> str:
    """Corrects frequent character confusions in receipt font scans."""
    t = line.strip()
    t = re.sub(r"\b0K\b", "0 KG", t, flags=re.IGNORECASE)
    t = re.sub(r"\b0\.(\d{2,3})K\b", r"0.\1 KG", t, flags=re.IGNORECASE)
    t = re.sub(r"\bO\b", "0", t)
    t = re.sub(r"\bl\b", "1", t)
    t = re.sub(r"\bI\b", "1", t)
    t = re.sub(r"\b(\d+)[oO]g\b", r"\1 0g", t)
    t = re.sub(r"\b(\d+)g0\b", r"\1 gói", t, flags=re.IGNORECASE)
    t = re.sub(r"\bgoi\b", "gói", t, flags=re.IGNORECASE)
    t = re.sub(r"\s+", " ", t)
    return t


def _is_non_food(text: str) -> bool:
    unacc = remove_accents(text)
    return any(p in unacc for p in NON_FOOD_UNACCENTED)


def _extract_weight_grams(
    line_text: str, default_weight: float
) -> tuple[float, bool]:
    """Extracts numeric weight in grams from line text (supports decimal KG, G, packs).

    Returns:
        (weight_g, is_extracted_flag)
    """
    t = line_text.lower().replace(",", ".")

    # 1. Decimal or whole KG: e.g. "0.45 kg", "1.20 kg", "0.7 kg", "1 kg"
    kg_match = re.search(r"(\d+(\.\d+)?)\s*(kg|kilo|ký|ki|cân)\b", t)
    if kg_match:
        try:
            return round(float(kg_match.group(1)) * 1000.0, 1), True
        except ValueError:
            pass

    # 2. Multi-pack grams: e.g. "2.00 MIENG x 250G"
    pack_match = re.search(r"(\d+(\.\d+)?)\s*.*x\s*(\d+(\.\d+)?)\s*(g|gr|gam)", t)
    if pack_match:
        try:
            cnt = float(pack_match.group(1))
            g_each = float(pack_match.group(3))
            return round(cnt * g_each, 1), True
        except ValueError:
            pass

    # 3. Direct grams: e.g. "500g", "300 gr", "250 gram", "150g"
    g_match = re.search(r"(\d+(\.\d+)?)\s*(g|gr|gam|gram)\b", t)
    if g_match:
        try:
            return round(float(g_match.group(1)), 1), True
        except ValueError:
            pass

    # 4. Egg pack: "HOP 10 QUẢ" -> 10 * 50g = 500g
    egg_match = re.search(r"(\d+)\s*(quả|trái|qua|trai)\b", t)
    if egg_match:
        try:
            cnt = float(egg_match.group(1))
            return round(cnt * 50.0, 1), True
        except ValueError:
            pass

    return default_weight, False


def _find_lookahead_scale_weight(lines: list[str], current_idx: int) -> float | None:
    """Checks the following 1-4 lines for supermarket scale decimal weight (e.g. 0.662, 0,332, 2.102)."""
    for offset in range(1, 5):
        if current_idx + offset >= len(lines):
            break
        look_line = lines[current_idx + offset]

        # Stop if we hit another clearly identifiable food item
        look_unacc = remove_accents(look_line)
        if any(unacc_name in look_unacc for _, unacc_name, _ in FOOD_KNOWLEDGE_LIST[:15]):
            break

        cleaned_look = look_line.replace(",", ".").strip()
        m = re.search(r"\b([0-9]\.[0-9]{3})\b", cleaned_look)
        if m:
            try:
                val = float(m.group(1))
                if 0.05 <= val <= 15.0:
                    return round(val * 1000.0, 1)
            except ValueError:
                pass

    return None


def parse_receipt_text(raw_text: str) -> list[dict[str, Any]]:
    """Parses raw receipt text into clean structured food items."""
    lines = [line.strip() for line in raw_text.splitlines() if line.strip()]
    parsed_items: list[dict[str, Any]] = []
    seen_names: set[str] = set()

    for idx, raw_line in enumerate(lines):
        line = _normalize_ocr_line(raw_line)
        unacc_line = remove_accents(line)

        # Skip receipt headers, footers, total lines, divider lines
        if re.search(
            r"^(winmart|bach hoa|co\.?opmart|hoa don|ngay|gio|sl|d\.?gia|t\.?tien|tong|tien|cam on|phieu|thoi gian|-|=)",
            unacc_line,
        ):
            continue

        # Skip non-food lines
        if _is_non_food(line):
            continue

        # Check for matching food in knowledge base
        matched_standard_name = None
        matched_meta = None
        for std_name, unacc_name, meta in FOOD_KNOWLEDGE_LIST:
            if re.search(r"\b" + re.escape(unacc_name) + r"\b", unacc_line) or unacc_name in unacc_line:
                matched_standard_name = std_name
                matched_meta = meta
                break

        if not matched_standard_name or matched_meta is None:
            continue

        canonical_name = matched_standard_name.capitalize()
        if canonical_name.lower() in seen_names:
            continue
        seen_names.add(canonical_name.lower())

        # First try weight on the same line (e.g. 150g, 500g, 1.2kg)
        weight_g, is_extracted = _extract_weight_grams(line, 0.0)

        # If no explicit weight in line text, lookahead for supermarket register scale weight
        if not is_extracted or weight_g <= 0.0:
            scale_weight = _find_lookahead_scale_weight(lines, idx)
            if scale_weight is not None:
                weight_g = scale_weight
                is_extracted = True
            else:
                weight_g = float(matched_meta["default_w"])
                is_extracted = False

        parsed_items.append({
            "name": canonical_name,
            "raw_receipt_line": raw_line,
            "quantity_g": weight_g,
            "quantity_source": "extracted" if is_extracted else "estimated",
            "unit": "g",
            "hours_to_expire": float(matched_meta["expiry_h"]),
            "is_staple": bool(matched_meta["is_staple"]),
            "confidence": 0.96,
        })

    return parsed_items
