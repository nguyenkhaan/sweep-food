"""Tier 4 entity enrichment with FreshCheck KB expiry, storage guide, and nutrition."""

from __future__ import annotations

import logging
from typing import Any

from AI.smart_parser.matching import PantryMatcher

logger = logging.getLogger(__name__)

STAPLE_CATEGORIES = frozenset({"Gia vị, nước chấm", "Dầu, mỡ, bơ"})
STAPLE_KEYWORDS = frozenset(
    {"muối", "tiêu", "đường", "nước mắm", "dầu ăn", "hạt nêm", "mì chính", "bột ngọt", "giấm", "tỏi khô", "hành khô"}
)


class PantryEnricher:
    """Enriches raw extracted food entities with master metadata and FreshCheck guidelines."""

    def __init__(
        self,
        matcher: PantryMatcher,
        fresh_kb: dict[str, Any] | None = None,
    ) -> None:
        self.matcher = matcher
        self.fresh_kb = fresh_kb or matcher.fresh_kb

    def enrich_item(self, raw_item: dict[str, Any]) -> dict[str, Any]:
        """Enrich raw item entity with master ingredient code, nutrition, shelf life, and freshness tips."""
        raw_name = str(raw_item.get("name") or raw_item.get("raw_name") or raw_item.get("raw_text") or "").strip()
        matched = self.matcher.resolve_master_ingredient(raw_name)

        code = raw_item.get("code") or (matched["code"] if matched else None)
        canonical_name = (
            matched["name"]
            if matched
            else (raw_name.capitalize() if raw_name else "Nguyên liệu")
        )
        category = (
            matched.get("category")
            if matched
            else str(raw_item.get("category") or "")
        )

        try:
            qty_g = float(raw_item.get("quantity_g") or 200.0)
        except (ValueError, TypeError):
            qty_g = 200.0

        storage_mode = str(raw_item.get("storage_mode") or "fridge_2_4c")
        if storage_mode not in ("fridge_2_4c", "freezer_-18c", "room_temp_25_30c"):
            storage_mode = "fridge_2_4c"

        # Tra cứu hạn dùng và mẹo bảo quản theo nhiệt độ trong FreshCheck KB
        try:
            default_hours = float(raw_item.get("hours_to_expire") or 48.0)
        except (ValueError, TypeError):
            default_hours = 48.0

        shelf_hours = default_hours
        freshness_info: dict[str, Any] | None = raw_item.get("freshness_guide")

        if self.fresh_kb:
            raw_lower = raw_name.lower()
            canonical_lower = canonical_name.lower()
            for f_data in self.fresh_kb.get("ingredients", {}).values():
                f_code = str(f_data.get("code") or "").strip()
                matches_code = bool(code and f_code == str(code).strip())
                matches_name = any(
                    n.lower() in raw_lower
                    or raw_lower in n.lower()
                    or n.lower() in canonical_lower
                    for n in f_data.get("names_vi", [])
                )

                if matches_code or matches_name:
                    shelf_spec = f_data.get("base_shelf_life_hours", {}).get(storage_mode)
                    if shelf_spec and shelf_spec.get("value") is not None:
                        try:
                            shelf_hours = float(shelf_spec["value"])
                        except (ValueError, TypeError):
                            pass

                    arch_id = f_data.get("archetype")
                    if arch_id:
                        arch = self.fresh_kb.get("archetypes", {}).get(arch_id, {})
                        freshness_info = {
                            "archetype": arch_id,
                            "archetype_name": arch.get("name_vi") or arch_id,
                            "storage_tips": arch.get("preservation_protocols", {}).get("prep", [])[:2],
                            "bad_practices": arch.get("preservation_protocols", {}).get("bad", [])[:1],
                        }
                    break

        is_staple = raw_item.get("is_staple")
        if is_staple is None:
            is_staple = category in STAPLE_CATEGORIES or any(
                k in canonical_name.lower() for k in STAPLE_KEYWORDS
            )

        nutrition = (
            matched.get("nutrition")
            if matched
            else raw_item.get("nutrition") or raw_item.get("nutrition_per_100g")
        )

        qty_source = raw_item.get("quantity_source") or "estimated"

        return {
            "name": canonical_name,
            "raw_name": raw_name,
            "raw_text": raw_name,
            "code": code,
            "category": category or None,
            "quantity_g": round(qty_g, 1),
            "quantity_source": qty_source,
            "hours_to_expire": round(shelf_hours, 1),
            "storage_mode": storage_mode,
            "expiry_date": raw_item.get("expiry_date"),
            "production_date": raw_item.get("production_date"),
            "expiry_check": raw_item.get("expiry_check"),
            "expiry_check_reason": raw_item.get("expiry_check_reason"),
            "note": raw_item.get("note"),
            "confidence": raw_item.get("confidence", 0.95),
            "is_staple": bool(is_staple),
            "nutrition": nutrition,
            "nutrition_per_100g": nutrition,
            "freshness_guide": freshness_info,
        }
