"""Parser for Supermarket Food Labels and Packaging (Bách Hóa Xanh, WinMart, Co.opmart)."""

from __future__ import annotations

import datetime
import re
from typing import Any

from AI.extraction.ocr.receipt_parser import remove_accents

BHX_DEFAULT_HOURS: dict[str, float] = {
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


def parse_vietnamese_date(date_str: str) -> datetime.date | None:
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
    except (ValueError, TypeError, IndexError):
        return None


def calculate_hours_until_expiry(
    expiry_date: datetime.date,
    ref_date: datetime.date | None = None,
) -> float:
    """Calculate hours remaining from ref_date until expiry_date."""
    ref = ref_date or datetime.date.today()
    delta = (expiry_date - ref).total_seconds() / 3600.0
    return max(0.0, round(delta, 1))


class FoodLabelParser:
    """Parses text from supermarket packaging stickers and product labels."""

    def parse_label_text(
        self,
        text: str,
        ref_date: datetime.date | None = None,
    ) -> dict[str, Any]:
        """Parse raw text extracted from a food label sticker.

        Returns structured item info:
        - name: str
        - quantity_g: float
        - quantity_source: str ("extracted" or "estimated")
        - hours_to_expire: float
        - expiry_date: str | None
        - production_date: str | None
        - expiry_check: str | None ("ok" or "suspicious")
        - raw_text: str
        """
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        full_text = " ".join(lines)

        # 1. Extract Expiry Date (HSD / Hạn sử dụng / EXP)
        expiry_date_str: str | None = None
        expiry_date_obj: datetime.date | None = None
        hsd_match = re.search(
            r"(?:HSD|Hạn\s*sử\s*dụng|han\s*su\s*dung|EXP|Hạn\s*dùng|han\s*dung|Sử\s*dụng\s*trước|su\s*dung\s*truoc)[\s:]*([0-9]{1,2}[/.-][0-9]{1,2}[/.-][0-9]{2,4})",
            full_text,
            re.IGNORECASE,
        )
        if hsd_match:
            expiry_date_str = hsd_match.group(1).replace("-", "/").replace(".", "/")
            expiry_date_obj = parse_vietnamese_date(expiry_date_str)

        # Relative days format: "HSD: 3 ngày kể từ NSX/NĐG"
        rel_hsd_match = re.search(
            r"(?:HSD|Hạn\s*dùng|han\s*dung)[\s:.]*([0-9]+)\s*(?:ngày|ngay)",
            full_text,
            re.IGNORECASE,
        )
        rel_days = int(rel_hsd_match.group(1)) if rel_hsd_match else None

        # 2. Extract Production / Packaging Date (NSX / NĐG / Ngày đóng gói)
        nsx_match = re.search(
            r"(?:NSX|NĐG|NDG|[0-9a-zA-Z]*N[ĐD]G|Ngày\s*đóng\s*gói|ngay\s*dong\s*goi|dong\s*goi|Ngày\s*sản\s*xuất|ngay\s*san\s*xuat)[\s:]*([0-9]{1,2}[/.-][0-9]{1,2}[/.-][0-9]{2,4})",
            full_text,
            re.IGNORECASE,
        )
        nsx_str = (
            nsx_match.group(1).replace("-", "/").replace(".", "/")
            if nsx_match
            else None
        )
        nsx_date_obj = parse_vietnamese_date(nsx_str) if nsx_str else None

        # Compute expiry date from packaging date + relative days if direct HSD is missing
        if not expiry_date_obj and rel_days and nsx_date_obj:
            expiry_date_obj = nsx_date_obj + datetime.timedelta(days=rel_days)
            expiry_date_str = expiry_date_obj.strftime("%d/%m/%Y")

        # 3. Extract Weight / Net Content (KLT / Trọng lượng / KL / TL)
        weight_g = 500.0  # Default standard pack weight
        is_extracted_qty = False
        weight_match = re.search(
            r"(?:KLT|Khối\s*lượng\s*tịnh|khoi\s*luong\s*tinh|Trọng\s*lượng|trong\s*luong|KL|TL)[\s:]*([0-9]+(?:[.,][0-9]+)?)\s*(kg|ks|km|ka|k9|kp|g|gam|gram)?",
            full_text,
            re.IGNORECASE,
        )
        if weight_match:
            val_str = weight_match.group(1).replace(",", ".")
            raw_unit = (weight_match.group(2) or "").lower()
            try:
                val = float(val_str)
                if raw_unit in ("kg", "ks", "km", "ka", "k9", "kp") or (
                    val < 5.0 and raw_unit != "g"
                ):
                    weight_g = round(val * 1000.0, 1)
                else:
                    weight_g = round(val, 1)
                is_extracted_qty = True
            except ValueError:
                pass
        else:
            # Fallback regex for weight standalone (e.g., "500g", "0.450 kg", "0.268 ks")
            stand_weight = re.search(
                r"\b([0-9]+(?:[.,][0-9]+)?)\s*(kg|ks|km|ka|k9|kp|g|gam)\b",
                full_text,
                re.IGNORECASE,
            )
            if stand_weight:
                val_str = stand_weight.group(1).replace(",", ".")
                raw_unit = stand_weight.group(2).lower()
                try:
                    val = float(val_str)
                    if raw_unit in ("kg", "ks", "km", "ka", "k9", "kp") or (
                        val < 5.0 and raw_unit != "g"
                    ):
                        weight_g = round(val * 1000.0, 1)
                    else:
                        weight_g = round(val, 1)
                    is_extracted_qty = True
                except ValueError:
                    pass
            else:
                dec_match = re.search(r"\b(0[.,][0-9]{2,3})\b", full_text)
                if dec_match:
                    try:
                        val = float(dec_match.group(1).replace(",", "."))
                        weight_g = round(val * 1000.0, 1)
                        is_extracted_qty = True
                    except ValueError:
                        pass

        # 4. Extract Product Name
        product_name = self._extract_product_name(lines)

        # 5. Compute Hours to Expire & Expiry Check
        hours_to_expire = 72.0
        expiry_check: str | None = None
        now_date = ref_date or datetime.date.today()
        if expiry_date_obj:
            hours_to_expire = calculate_hours_until_expiry(expiry_date_obj, ref_date)
            if expiry_date_obj < now_date:
                expiry_check = "suspicious"
            else:
                expiry_check = "ok"
        elif rel_days:
            hours_to_expire = float(rel_days * 24)
            expiry_check = "ok"
        else:
            # Estimate from product keywords
            name_lower = product_name.lower()
            for kw, hrs in BHX_DEFAULT_HOURS.items():
                if kw in name_lower:
                    hours_to_expire = hrs
                    break

        unacc_full = remove_accents(full_text)
        is_bhx = "bach hoa xanh" in unacc_full or "bhx" in unacc_full

        return {
            "name": product_name,
            "quantity_g": weight_g,
            "quantity_source": "extracted" if is_extracted_qty else "estimated",
            "hours_to_expire": hours_to_expire,
            "expiry_date": expiry_date_str,
            "production_date": nsx_str,
            "expiry_check": expiry_check,
            "store": "Bách Hóa Xanh" if is_bhx else "Siêu thị",
            "raw_text": text,
        }

    def _extract_product_name(self, lines: list[str]) -> str:
        """Find the most plausible food product name in the label lines."""
        store_banners = [
            "bach hoa xanh", "winmart", "co.opmart", "coopmart", "lotte mart",
            "sieu thi", "tops market", "thit tuoi moi ngay",
            "cp", "c.p", "c.p.", "japfa", "yapfa", "minifood", "vissan", "cj", "meatdeli",
            "cong ty", "cty", "chi nhanh", "phuong", "quan", "khong su dung hang het hsd",
            "huong dan su dung", "thanh phan", "bao quan", "so tu cong bo", "thoi han su dung",
        ]

        culinary_keywords = [
            "thịt", "thit", "cá", "ca", "gà", "ga", "heo", "bò", "bo", "tôm", "tom",
            "ốc", "oc", "mề", "me", "đùi", "dui", "cánh", "canh", "chân", "chan",
            "xương", "xuong", "chả", "cha", "cải", "cai", "rau", "đậu", "dau",
            "dưa", "dua", "sả", "sa", "nấm", "nam", "hành", "hanh", "tỏi", "toi",
            "ớt", "ot", "basa", "nục", "nuc", "sò", "so", "bánh", "banh", "cốt lết", "cot let",
        ]

        candidates: list[tuple[str, bool]] = []
        for line in lines:
            line_clean = line.strip(" -:•|/\"'")
            if len(line_clean) < 3:
                continue
            line_unaccented = remove_accents(line_clean).lower()

            # Skip pure numbers, prices, barcodes
            if re.match(r"^[0-9.,;:/\s\-+()]+$", line_clean):
                continue

            # Skip metadata lines
            if any(
                b in line_unaccented
                for b in [
                    "hsd", "nsx", "klt", "tl:", "kl:", "don gia", "thanh tien",
                    "bao quan", "huong dan", "xuat xu", "han su dung", "dong goi",
                    "truy xuat", "ma qr", "thanh phan",
                ]
            ):
                continue

            # Skip pure store banner or brand lines
            is_banner = False
            for sb in store_banners:
                if (
                    line_unaccented == sb
                    or line_unaccented.startswith(sb + " ")
                    or line_unaccented.endswith(" " + sb)
                ):
                    rem = line_unaccented.replace(sb, "").strip(" -:•|/().")
                    if len(rem) < 3 or any(sb2 in rem for sb2 in store_banners):
                        is_banner = True
                        break
            if is_banner:
                continue

            # Clean brand prefixes / suffixes (e.g. "CP CHAN GIO HEO C.P" -> "CHAN GIO HEO")
            cleaned_line = re.sub(
                r"^(?:siêu thị\s*|sieu thi\s*)?(?:bách hóa xanh|bach hoa xanh|winmart|coopmart)\s*[-:]*\s*",
                "",
                line_clean,
                flags=re.IGNORECASE,
            )
            cleaned_line = re.sub(
                r"^(?:cp|c\.p\.?|japfa|yapfa|minifood)\s*[-:]*\s*",
                "",
                cleaned_line,
                flags=re.IGNORECASE,
            )
            cleaned_line = re.sub(
                r"\s*[-:]*\s*(?:cp|c\.p\.?|japfa|yapfa|minifood)$",
                "",
                cleaned_line,
                flags=re.IGNORECASE,
            )

            # Clean frequent OCR errors
            cleaned_line = re.sub(
                r"\bTHỨT SỐ LONG\b", "THỊT SÒ LÔNG", cleaned_line, flags=re.IGNORECASE
            )
            cleaned_line = re.sub(
                r"\bJUONG\b", "XƯƠNG", cleaned_line, flags=re.IGNORECASE
            )
            cleaned_line = re.sub(
                r"\bBANHBAT\b", "BÁNH BAO", cleaned_line, flags=re.IGNORECASE
            )
            cleaned_line = re.sub(
                r"\bLất Heo\b", "Thịt Heo Lát", cleaned_line, flags=re.IGNORECASE
            )
            cleaned_line = re.sub(
                r"\bTOM THE NC\b", "TÔM THẺ NÕN", cleaned_line, flags=re.IGNORECASE
            )

            if len(cleaned_line) >= 3:
                c_unacc = remove_accents(cleaned_line).lower()
                has_culinary = any(ck in c_unacc for ck in culinary_keywords)
                candidates.append((cleaned_line, has_culinary))

        if candidates:
            for text_cand, has_cul in candidates:
                if has_cul:
                    return text_cand
            return candidates[0][0]

        return "Rau củ Bách Hóa Xanh"
