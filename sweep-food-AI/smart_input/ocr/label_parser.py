"""Parser for Supermarket Food Labels and Packaging (Bách Hóa Xanh, WinMart, Co.opmart).

Extracts:
- Product name (e.g., Cải thìa sạch Bách Hóa Xanh, Thịt ba rọi heo C.P)
- Net weight in grams (converted from kg or g)
- Expiry date (HSD / Best before) & computed hours_to_expire
- Production date (NSX) & Origin
"""

from __future__ import annotations

import datetime
import re
from typing import Any, Optional


BHX_DEFAULT_HOURS = {
    "rau": 72.0,       # 3 days
    "cải": 72.0,
    "cà chua": 96.0,
    "thịt": 48.0,      # 2 days fresh meat
    "heo": 48.0,
    "bò": 48.0,
    "gà": 48.0,
    "cá": 36.0,        # 1.5 days fresh fish
    "tôm": 36.0,
    "nấm": 72.0,
    "trứng": 240.0,    # 10 days
    "đậu": 48.0,
    "hành": 120.0,
    "tỏi": 360.0,
}


def parse_vietnamese_date(date_str: str) -> Optional[datetime.date]:
    """Parse Vietnamese date string (DD/MM/YYYY or DD-MM-YYYY or DD/MM/YY)."""
    clean = date_str.strip().replace("-", "/").replace(".", "/")
    parts = clean.split("/")
    if len(parts) != 3:
        return None
    try:
        day = int(parts[0])
        month = int(parts[1])
        year = int(parts[2])
        if year < 100:
            year += 2000
        return datetime.date(year, month, day)
    except Exception:
        return None


def calculate_hours_until_expiry(expiry_date: datetime.date, ref_date: Optional[datetime.date] = None) -> float:
    """Calculate hours remaining from ref_date until expiry_date."""
    ref = ref_date or datetime.date.today()
    delta = (expiry_date - ref).total_seconds() / 3600.0
    # If already past, keep at 0 or small minimum
    return max(0.0, round(delta, 1))


class FoodLabelParser:
    """Parses text from supermarket packaging stickers and product labels."""

    def parse_label_text(self, text: str, ref_date: Optional[datetime.date] = None) -> dict[str, Any]:
        """Parse raw text extracted from a food label sticker.

        Returns structured item info:
        - name: str
        - quantity_g: float
        - hours_to_expire: float
        - expiry_date: str | None
        - packaging_date: str | None
        - raw_matched_text: str
        """
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        full_text = " ".join(lines)

        # 1. Extract Expiry Date (HSD / Hạn sử dụng / EXP)
        expiry_date_str = None
        expiry_date_obj = None
        hsd_match = re.search(
            r'(?:HSD|Hạn\s*sử\s*dụng|han\s*su\s*dung|EXP|Hạn\s*dùng|han\s*dung|Sử\s*dụng\s*trước|su\s*dung\s*truoc)[\s:]*([0-9]{1,2}[/.-][0-9]{1,2}[/.-][0-9]{2,4})',
            full_text,
            re.IGNORECASE,
        )
        if hsd_match:
            expiry_date_str = hsd_match.group(1).replace("-", "/").replace(".", "/")
            expiry_date_obj = parse_vietnamese_date(expiry_date_str)

        # Relative days format: "HSD: 3 ngày kể từ NSX"
        rel_hsd_match = re.search(
            r'(?:HSD|Hạn\s*dùng|han\s*dung)[\s:]*([0-9]+)\s*(?:ngày|ngay)',
            full_text,
            re.IGNORECASE,
        )
        rel_days = int(rel_hsd_match.group(1)) if rel_hsd_match else None

        # 2. Extract Production Date (NSX / Ngày đóng gói)
        nsx_match = re.search(
            r'(?:NSX|Ngày\s*đóng\s*gói|ngay\s*dong\s*goi|dong\s*goi|Ngày\s*sản\s*xuất|ngay\s*san\s*xuat)[\s:]*([0-9]{1,2}[/.-][0-9]{1,2}[/.-][0-9]{2,4})',
            full_text,
            re.IGNORECASE,
        )
        nsx_str = nsx_match.group(1).replace("-", "/").replace(".", "/") if nsx_match else None

        # 3. Extract Weight / Net Content (KLT / Trọng lượng / KL / TL)
        weight_g = 500.0  # Default standard pack weight
        quantity_source = "estimated"
        weight_match = re.search(
            r'(?:KLT|Khối\s*lượng\s*tịnh|khoi\s*luong\s*tinh|Trọng\s*lượng|trong\s*luong|KL|TL)[\s:]*([0-9]+(?:[.,][0-9]+)?)\s*(kg|g|gam|gram)?',
            full_text,
            re.IGNORECASE,
        )
        if weight_match:
            val_str = weight_match.group(1).replace(",", ".")
            unit = (weight_match.group(2) or "g").lower()
            try:
                val = float(val_str)
                if unit == "kg":
                    weight_g = round(val * 1000.0, 1)
                else:
                    weight_g = round(val, 1)
                quantity_source = "extracted"
            except ValueError:
                pass
        else:
            # Fallback regex for weight standalone (e.g., "500g" or "0.450 kg")
            stand_weight = re.search(r'\b([0-9]+(?:[.,][0-9]+)?)\s*(kg|g|gam)\b', full_text, re.IGNORECASE)
            if stand_weight:
                val_str = stand_weight.group(1).replace(",", ".")
                unit = stand_weight.group(2).lower()
                try:
                    val = float(val_str)
                    weight_g = round(val * 1000.0 if unit == "kg" else val, 1)
                    quantity_source = "extracted"
                except ValueError:
                    pass

        # 4. Extract Product Name
        # Typical header lines: "BÁCH HÓA XANH", "SIÊU THỊ BÁCH HÓA XANH", "CÔNG TY CP THỰC PHẨM..."
        # The product name is usually the prominent title line after the supermarket header.
        product_name = self._extract_product_name(lines)

        # 5. Compute Hours to Expire
        hours_to_expire = 72.0
        if expiry_date_obj:
            hours_to_expire = calculate_hours_until_expiry(expiry_date_obj, ref_date)
        elif rel_days:
            hours_to_expire = float(rel_days * 24)
        else:
            # Estimate from product keywords
            name_lower = product_name.lower()
            for kw, hrs in BHX_DEFAULT_HOURS.items():
                if kw in name_lower:
                    hours_to_expire = hrs
                    break

        from smart_input.ocr.receipt_parser import remove_accents
        unacc_full = remove_accents(full_text)
        is_bhx = "bach hoa xanh" in unacc_full or "bhx" in unacc_full

        return {
            "name": product_name,
            "quantity_g": weight_g,
            "quantity_source": quantity_source,
            "hours_to_expire": hours_to_expire,
            "expiry_date": expiry_date_str,
            "production_date": nsx_str,
            "store": "Bách Hóa Xanh" if is_bhx else "Siêu thị",
            "raw_text": text,
        }

    def _extract_product_name(self, lines: list[str]) -> str:
        """Find the most plausible food product name in the label lines."""
        from smart_input.ocr.receipt_parser import remove_accents

        store_banners = [
            "bach hoa xanh", "winmart", "co.opmart", "coopmart", "lotte mart",
            "sieu thi", "tops market", "thit tuoi moi ngay",
        ]

        candidates = []
        for line in lines:
            line_clean = line.strip()
            if len(line_clean) < 3:
                continue
            line_unaccented = remove_accents(line_clean)

            # Skip metadata lines
            if any(b in line_unaccented for b in [
                "hsd", "nsx", "klt", "tl:", "kl:", "don gia", "thanh tien",
                "bao quan", "huong dan", "xuat xu", "han su dung", "dong goi"
            ]):
                continue

            # Skip pure store banner lines (e.g., "SIEU THI BACH HOA XANH" or "BACH HOA XANH - THIT TUOI MOI NGAY")
            is_banner = False
            for sb in store_banners:
                if sb in line_unaccented:
                    rem = line_unaccented.replace(sb, "").strip(" -:•|/")
                    if len(rem) < 3 or any(sb2 in rem for sb2 in store_banners):
                        is_banner = True
                        break
            if is_banner:
                continue

            # Remove store prefix if present (e.g. "Bách Hóa Xanh - Cải Thìa Sạch")
            cleaned_line = re.sub(
                r'^(?:siêu thị\s*|sieu thi\s*)?(?:bách hóa xanh|bach hoa xanh|winmart|coopmart)\s*[-:]*\s*',
                '',
                line_clean,
                flags=re.IGNORECASE
            )
            if len(cleaned_line) >= 3:
                candidates.append(cleaned_line)

        if candidates:
            return candidates[0]
        return "Rau củ Bách Hóa Xanh"
