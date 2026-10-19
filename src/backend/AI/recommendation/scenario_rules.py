"""Scenario rules and hard constraint filters for recipe recommendation.

Filters candidate recipes based on user health, dietary restrictions, and kitchen context:
- Vegetarian (ăn chay / chay): strict elimination of animal meats, seafood, eggs, lard, fish sauce
- Diabetes (người tiểu đường): sugar < 10g and carbs < 45g per serving
- Hypertension (người cao huyết áp): sodium < 1000mg per serving
- Gout (người bệnh gout): strict elimination of high-purine foods (red meats, seafood, organ meats)
- Low-carb / Keto: carbs <= 20g per serving
- Gastritis (người đau dạ dày): no deep-fried cooking methods
- Data quality safety: exclude nutrition_anomaly_flag and incomplete_flag
"""

from __future__ import annotations

import csv
import re
from functools import lru_cache
from pathlib import Path
from typing import Any

ROOT_DATA = Path(__file__).resolve().parent.parent / "data"
MASTER_CSV = ROOT_DATA / "master_ingredients" / "master_ingredients_nutrition.csv"

ANIMAL_CATEGORIES: frozenset[str] = frozenset({
    "Thịt và sản phẩm chế biến",
    "Thủy sản và sản phẩm chế biến",
    "Trứng và sản phẩm chế biến",
})

ANIMAL_KEYWORDS: list[str] = [
    r"\bthịt\b", r"\bcá\b", r"\btôm\b", r"\bcua\b", r"\bmực\b", r"\bgà\b", r"\bvịt\b",
    r"\bheo\b", r"\blợn\b", r"\bbò\b", r"\btrứng\b", r"\bmỡ lợn\b", r"\bmỡ heo\b",
    r"\bmỡ bò\b", r"\bmỡ gà\b", r"\bmỡ động vật\b", r"\bngao\b", r"\bsò\b",
    r"\bốc\b", r"\bhến\b", r"\bhàu\b", r"\blòng\b", r"\bgan\b", r"\bcật\b", r"\bdạ dày\b",
    r"\bnội tạng\b", r"\bdê\b", r"\bcừu\b", r"\bbê\b", r"\blươn\b", r"\bếch\b",
    r"\bchả lụa\b", r"\bpate\b", r"\blạp xưởng\b", r"\bbò viên\b", r"\bcá viên\b",
    r"\bmắm tôm\b", r"\bmắm tép\b", r"\bmắm cá\b", r"\bmắm ruốc\b", r"\bmắm nêm\b",
]

GOUT_KEYWORDS: list[str] = [
    r"\bbò\b", r"\bbê\b", r"\bcừu\b", r"\bdê\b", r"\bcua\b", r"\bghẹ\b",
    r"\btôm\b", r"\bsò\b", r"\bngao\b", r"\bhàu\b", r"\blòng\b", r"\bgan\b",
    r"\bcật\b", r"\bdạ dày\b", r"\bnội tạng\b",
]

SPICY_KEYWORDS: list[str] = [
    r"\bớt\b", r"\bsa tế\b", r"\btương ớt\b", r"\bớt bột\b", r"\bcà ri\b", r"\bmù tạt\b",
]


@lru_cache(maxsize=1)
def default_master_category_map() -> dict[str, str]:
    """Load default category_vi mapping for master codes from bundle."""
    if not MASTER_CSV.exists():
        return {}
    with MASTER_CSV.open(encoding="utf-8-sig", newline="") as fh:
        return {row["code"]: row.get("category_vi", "") for row in csv.DictReader(fh)}


def _texts(ing: dict[str, Any]) -> tuple[str, str]:
    return (ing.get("cleaned_name") or "").strip().lower(), (ing.get("raw_text") or "").strip().lower()


def has_animal_ingredients(
    recipe_ings: list[dict[str, Any]],
    categories: dict[str, str] | None = None,
) -> bool:
    """Return True if any recipe ingredient contains animal meat, seafood, eggs, or animal fat."""
    cat_map = default_master_category_map() if categories is None else categories
    for ing in recipe_ings:
        clean_n, raw_t = _texts(ing)
        code = str(ing.get("master_ingredient_code") or "").strip()
        if "chay" in clean_n or "chay" in raw_t:
            continue
        if "nấm" in clean_n or "nấm" in raw_t:
            continue
        if "đậu phụ" in clean_n or "tàu hũ" in clean_n or "đậu hũ" in clean_n:
            continue
        if "tép tỏi" in clean_n or "tép tỏi" in raw_t:
            clean_n = clean_n.replace("tép tỏi", "")
            raw_t = raw_t.replace("tép tỏi", "")
        if "khoai mỡ" in clean_n or "xà lách mỡ" in clean_n:
            clean_n = clean_n.replace("khoai mỡ", "").replace("xà lách mỡ", "")
        if cat_map.get(code, "") in ANIMAL_CATEGORIES:
            return True
        for pat in ANIMAL_KEYWORDS:
            if re.search(pat, clean_n) or re.search(pat, raw_t):
                return True
        if ("nước mắm" in clean_n or "nước mắm" in raw_t) and "chay" not in clean_n and "chay" not in raw_t:
            return True
        if re.search(r"\bmỡ\b", clean_n) and not ("khoai" in clean_n or "xà lách" in clean_n or "hành" in clean_n):
            return True
    return False


def has_gout_forbidden_ingredients(
    recipe_ings: list[dict[str, Any]],
    categories: dict[str, str] | None = None,
) -> bool:
    """Return True if recipe contains high-purine ingredients forbidden for gout patients."""
    cat_map = default_master_category_map() if categories is None else categories
    for ing in recipe_ings:
        clean_n, raw_t = _texts(ing)
        code = str(ing.get("master_ingredient_code") or "").strip()
        if "chay" in clean_n or "chay" in raw_t:
            continue
        if "tép tỏi" in clean_n or "tép tỏi" in raw_t:
            clean_n = clean_n.replace("tép tỏi", "")
            raw_t = raw_t.replace("tép tỏi", "")
        if "bắp cải" in clean_n or "bắp ngô" in clean_n:
            clean_n = clean_n.replace("bắp cải", "").replace("bắp ngô", "")
        if cat_map.get(code, "") in {"Thịt và sản phẩm chế biến", "Thủy sản và sản phẩm chế biến"}:
            return True
        for pat in GOUT_KEYWORDS:
            if re.search(pat, clean_n) or re.search(pat, raw_t):
                return True
    return False


def is_spicy(recipe_ings: list[dict[str, Any]]) -> bool:
    """Return True if recipe contains strong spicy ingredients."""
    for ing in recipe_ings:
        clean_n, raw_t = _texts(ing)
        if any(re.search(p, clean_n) or re.search(p, raw_t) for p in SPICY_KEYWORDS):
            if "ớt chuông" in clean_n or "ớt chuông" in raw_t:
                continue
            return True
    return False


def filter_candidate(
    cand: dict[str, Any],
    scenario: str,
    recipe_ings: list[dict[str, Any]],
    categories: dict[str, str] | None = None,
) -> bool:
    """Return True if candidate passes data-quality and scenario hard filters."""
    # a. Data Quality Safety Filter
    if str(cand.get("nutrition_anomaly_flag", "0")) in ("1", "true", "True") or cand.get("nutrition_anomaly_flag") in (1, True):
        return False
    if str(cand.get("incomplete_flag", "0")) in ("1", "true", "True") or cand.get("incomplete_flag") in (1, True):
        return False

    # b. Scenario Constraint Filter
    if scenario in ("an_chay_ram_mung_mot", "an_chay", "chay") or "chay" in scenario:
        diet_tags = (cand.get("diet_tags") or "").lower()
        if "ăn chay" not in diet_tags:
            return False
        if has_animal_ingredients(recipe_ings, categories):
            return False
    elif scenario == "nguoi_tieu_duong":
        sugar = float(cand.get("sugar_g_per_serving") or 0.0)
        carbs = float(cand.get("carbs_per_serving") or 0.0)
        if sugar >= 10.0 or carbs >= 45.0:
            return False
    elif scenario == "nguoi_cao_huyet_ap":
        sodium = float(cand.get("sodium_mg_per_serving") or 0.0)
        servings = max(1.0, float(cand.get("default_servings") or 4.0))
        tot_sodium_per_serv = float(cand.get("total_sodium_mg") or 0.0) / servings
        if sodium >= 1000.0 or tot_sodium_per_serv >= 1000.0:
            return False
    elif scenario == "nguoi_benh_gout":
        if has_gout_forbidden_ingredients(recipe_ings, categories):
            return False
    elif scenario in ("an_kieng_keto_lowcarb", "keto", "lowcarb"):
        carbs = float(cand.get("carbs_per_serving") or 0.0)
        if carbs > 20.0:
            return False
    elif scenario == "nguoi_dau_da_day":
        method = (cand.get("cooking_method") or "").strip().lower()
        if method in ("chiên/rán", "chiên", "rán"):
            return False

    return True
