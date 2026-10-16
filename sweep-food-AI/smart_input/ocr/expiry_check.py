"""Second safety net for OCR label dates, using FreshCheck reference shelf life.

A label's span (expiry_date - production_date) longer than the FreshCheck
reference for that ingredient usually means the model misread the HSD
(e.g. NĐG 1.10, HSD 2.10 read as 4.10). Dates are never changed here: the item
is only flagged so the confirmation screen can ask the user to re-check.
"""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path
from typing import Any, Optional

from smart_input.ocr.groq_vision_ocr import _normalize_date
from smart_parser.pantry_parser import FRESH_KB_JSON, strip_vietnamese_accents

FRESHCHECK_INGREDIENTS_DIR = Path(__file__).resolve().parents[3] / "data_freshness" / "ingredients"

# Labels print whole days, so a span is a multiple of 24h; half a day of slack
# absorbs rounding against non-whole-day references (e.g. 36h) while any whole
# extra day beyond the reference is still flagged (48h ref: 2 days ok, 3 days flagged).
EXPIRY_TOLERANCE_HOURS = 12.0
DEFAULT_STORAGE_MODE = "fridge_2_4c"

_kb_ingredients: Optional[dict[str, dict[str, Any]]] = None


def load_freshcheck_ingredients() -> dict[str, dict[str, Any]]:
    """FreshCheck ingredients from the built release artifact, else the reviewed YAML sources."""
    global _kb_ingredients
    if _kb_ingredients is not None:
        return _kb_ingredients
    ingredients: dict[str, dict[str, Any]] = {}
    try:
        if FRESH_KB_JSON.exists():
            ingredients = json.loads(FRESH_KB_JSON.read_text(encoding="utf-8")).get("ingredients", {})
        elif FRESHCHECK_INGREDIENTS_DIR.is_dir():
            import yaml

            for path in sorted(FRESHCHECK_INGREDIENTS_DIR.glob("*.yaml")):
                for record in yaml.safe_load(path.read_text(encoding="utf-8")) or []:
                    if isinstance(record, dict) and record.get("id"):
                        ingredients[str(record["id"])] = record
    except Exception as e:
        print(f"[expiry_check Warning] Failed loading FreshCheck ingredients: {e}")
        ingredients = {}
    _kb_ingredients = ingredients
    return ingredients


def find_freshcheck_ingredient(
    ingredients: dict[str, dict[str, Any]], code: Any, names: list[str]
) -> Optional[dict[str, Any]]:
    """Match by master code first, then by the longest FreshCheck name found in the item name."""
    code_str = str(code or "").strip()
    if code_str:
        for f_data in ingredients.values():
            if str(f_data.get("code") or "").strip() == code_str:
                return f_data

    queries = [strip_vietnamese_accents(n) for n in names if n and n.strip()]
    best, best_len = None, 0
    for f_data in ingredients.values():
        for name_vi in f_data.get("names_vi", []):
            kb_name = strip_vietnamese_accents(str(name_vi))
            if len(kb_name) < 3 or len(kb_name) <= best_len:
                continue
            if any(q == kb_name or f" {kb_name} " in f" {q} " for q in queries):
                best, best_len = f_data, len(kb_name)
    return best


def _to_date(value: Any) -> Optional[date]:
    normalized = _normalize_date(value)
    if normalized is None:
        return None
    day, month, year = (int(p) for p in normalized.split("/"))
    return date(year, month, day)


def check_label_expiry(
    item: dict[str, Any],
    ingredients: Optional[dict[str, dict[str, Any]]] = None,
    tolerance_hours: float = EXPIRY_TOLERANCE_HOURS,
) -> dict[str, Any]:
    """Return item with expiry_check "ok" / "suspicious" (None when it cannot be checked).

    A suspicious item also gets expiry_check_reason and the reason appended to note.
    """
    result = {**item, "expiry_check": None, "expiry_check_reason": None}
    produced = _to_date(item.get("production_date"))
    expires = _to_date(item.get("expiry_date"))
    if produced is None or expires is None:
        return result

    span_days = (expires - produced).days
    reason = None
    if span_days < 0:
        reason = (
            f"HSD {expires:%d/%m/%Y} sớm hơn ngày sản xuất/đóng gói {produced:%d/%m/%Y}, "
            "có thể đọc nhầm ngày. Kiểm tra lại HSD trên tem."
        )
    else:
        f_data = find_freshcheck_ingredient(
            load_freshcheck_ingredients() if ingredients is None else ingredients,
            item.get("code"),
            [str(item.get("raw_name") or ""), str(item.get("name") or "")],
        )
        storage_mode = item.get("storage_mode") or DEFAULT_STORAGE_MODE
        spec = (f_data or {}).get("base_shelf_life_hours", {}).get(storage_mode) or {}
        if spec.get("value") is None:
            return result
        base_hours = float(spec["value"])
        if span_days * 24.0 > base_hours + tolerance_hours:
            reason = (
                f"HSD đọc được ({expires:%d/%m/%Y}) dài {span_days} ngày kể từ ngày sản xuất/đóng gói "
                f"{produced:%d/%m/%Y}, vượt mốc tham chiếu FreshCheck {base_hours:g} giờ "
                f"(~{base_hours / 24:g} ngày) cho {f_data.get('names_vi', ['nguyên liệu này'])[0]}. "
                "Kiểm tra lại HSD trên tem; nếu tem in đúng như vậy thì giữ nguyên."
            )

    if reason is None:
        result["expiry_check"] = "ok"
        return result
    note = str(item.get("note") or "").strip()
    result["expiry_check"] = "suspicious"
    result["expiry_check_reason"] = reason
    result["note"] = f"{note} | {reason}" if note else reason
    return result
