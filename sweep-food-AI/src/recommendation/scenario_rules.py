"""Scenario rules shared by the serving hard-filter layer and the synthetic
teacher label.

A pantry query carries ``scenario_type`` (a key of
`life_scenarios.SCENARIO_BY_KEY`) and ``household_size``. Cooking time is not
used: ``estimated_cooking_minutes`` in the data is not reliable enough to rank
on. These functions turn that context plus a recipe into label signals: hard
violations (diet, health, equipment), soft preferences (cooking method, dish
type, energy band) and the teacher grade. They are not model features: the
ranker only sees `contextual_features.FEATURE_COLS`. Unknown scenarios
(``custom``) are neutral: no violation, no preference.
"""

from __future__ import annotations

import csv
import hashlib
import re
from functools import lru_cache
from pathlib import Path
from typing import Any

from src.recommendation.life_scenarios import SCENARIO_BY_KEY

ROOT = Path(__file__).resolve().parents[2]
MASTER_CSV = ROOT / "data" / "processed" / "viendinhduong" / "master_ingredients_nutrition.csv"

# Legacy / shorthand keys sent by clients.
SCENARIO_ALIASES = {
    "an_chay": "an_chay_ram_mung_mot",
    "chay": "an_chay_ram_mung_mot",
    "keto": "an_kieng_keto_lowcarb",
    "lowcarb": "an_kieng_keto_lowcarb",
}

# Cooking methods (recipes.cooking_method) each kitchen can actually execute.
EQUIPMENT_METHODS: dict[str, set[str] | None] = {
    "rice_cooker": {"Luộc", "Hấp", "Canh/Súp", "Kho", "Trộn/Gỏi"},
    "one_burner": {"Luộc", "Hấp", "Canh/Súp", "Kho", "Trộn/Gỏi", "Xào", "Chiên/Rán", "Khác", "Ngâm/Muối chua"},
    "full": None,
}

ANIMAL_CATEGORIES = {
    "Thịt và sản phẩm chế biến",
    "Thủy sản và sản phẩm chế biến",
    "Trứng và sản phẩm chế biến",
}
ANIMAL_KEYWORDS = [
    r"\bthịt\b", r"\bcá\b", r"\btôm\b", r"\bcua\b", r"\bmực\b", r"\bgà\b", r"\bvịt\b",
    r"\bheo\b", r"\blợn\b", r"\bbò\b", r"\btrứng\b", r"\bmỡ lợn\b", r"\bmỡ heo\b",
    r"\bmỡ bò\b", r"\bmỡ gà\b", r"\bmỡ động vật\b", r"\bngao\b", r"\bsò\b",
    r"\bốc\b", r"\bhến\b", r"\bhàu\b", r"\blòng\b", r"\bgan\b", r"\bcật\b", r"\bdạ dày\b",
    r"\bnội tạng\b", r"\bdê\b", r"\bcừu\b", r"\bbê\b", r"\blươn\b", r"\bếch\b",
    r"\bchả lụa\b", r"\bpate\b", r"\blạp xưởng\b", r"\bbò viên\b", r"\bcá viên\b",
    r"\bmắm tôm\b", r"\bmắm tép\b", r"\bmắm cá\b", r"\bmắm ruốc\b", r"\bmắm nêm\b",
]
GOUT_KEYWORDS = [
    r"\bbò\b", r"\bbê\b", r"\bcừu\b", r"\bdê\b", r"\bcua\b", r"\bghẹ\b",
    r"\btôm\b", r"\bsò\b", r"\bngao\b", r"\bhàu\b", r"\blòng\b", r"\bgan\b",
    r"\bcật\b", r"\bdạ dày\b", r"\bnội tạng\b",
]
SPICY_KEYWORDS = [r"\bớt\b", r"\bsa tế\b", r"\btương ớt\b", r"\bớt bột\b", r"\bcà ri\b", r"\bmù tạt\b"]

# Health thresholds per serving (same values as the serving hard-filter layer).
SUGAR_MAX_G = 10.0
DIABETIC_CARBS_MAX_G = 45.0
SODIUM_MAX_MG = 2000.0
LOW_CARB_MAX_G = 20.0
HIGH_PROTEIN_G = 25.0


@lru_cache(maxsize=1)
def master_category_map() -> dict[str, str]:
    with MASTER_CSV.open(encoding="utf-8", newline="") as fh:
        return {row["code"]: row["category_vi"] for row in csv.DictReader(fh)}


def scenario_profile(scenario_type: str | None) -> dict[str, Any] | None:
    key = (scenario_type or "").strip().lower()
    key = SCENARIO_ALIASES.get(key, key)
    return SCENARIO_BY_KEY.get(key)


def _texts(ing: dict[str, Any]) -> tuple[str, str]:
    return (ing.get("cleaned_name") or "").strip().lower(), (ing.get("raw_text") or "").strip().lower()


def has_animal_ingredients(recipe_ings: list[dict[str, Any]], categories: dict[str, str] | None = None) -> bool:
    categories = master_category_map() if categories is None else categories
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
        if categories.get(code, "") in ANIMAL_CATEGORIES:
            return True
        for pat in ANIMAL_KEYWORDS:
            if re.search(pat, clean_n) or re.search(pat, raw_t):
                return True
        if ("nước mắm" in clean_n or "nước mắm" in raw_t) and "chay" not in clean_n and "chay" not in raw_t:
            return True
        if re.search(r"\bmỡ\b", clean_n) and not ("khoai" in clean_n or "xà lách" in clean_n or "hành" in clean_n):
            return True
    return False


def has_gout_forbidden_ingredients(recipe_ings: list[dict[str, Any]], categories: dict[str, str] | None = None) -> bool:
    categories = master_category_map() if categories is None else categories
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
        if categories.get(code, "") in {"Thịt và sản phẩm chế biến", "Thủy sản và sản phẩm chế biến"}:
            return True
        for pat in GOUT_KEYWORDS:
            if re.search(pat, clean_n) or re.search(pat, raw_t):
                return True
    return False


def is_spicy(recipe_ings: list[dict[str, Any]]) -> bool:
    for ing in recipe_ings:
        clean_n, raw_t = _texts(ing)
        if any(re.search(p, clean_n) or re.search(p, raw_t) for p in SPICY_KEYWORDS):
            if "ớt chuông" in clean_n or "ớt chuông" in raw_t:
                continue
            return True
    return False


def _num(value: Any, default: float = 0.0) -> float:
    try:
        f = float(value)
        return f if f == f else default
    except (TypeError, ValueError):
        return default


def hard_violations(profile: dict[str, Any] | None, recipe: dict[str, Any],
                    recipe_ings: list[dict[str, Any]]) -> list[str]:
    """Reasons this recipe is unacceptable for the scenario (empty = acceptable)."""
    if not profile:
        return []
    reasons = []
    method = (recipe.get("cooking_method") or "").strip()
    allowed = EQUIPMENT_METHODS.get(profile.get("equipment", "full"))
    if allowed is not None and method not in allowed:
        reasons.append(f"equipment:{method}")
    if profile.get("diet") == "vegetarian":
        tags = (recipe.get("diet_tags") or "").lower()
        if "ăn chay" not in tags or has_animal_ingredients(recipe_ings):
            reasons.append("vegetarian")
    health = set(profile.get("health") or [])
    if "low_sugar" in health and (_num(recipe.get("sugar_g_per_serving")) >= SUGAR_MAX_G
                                  or _num(recipe.get("carbs_per_serving")) >= DIABETIC_CARBS_MAX_G):
        reasons.append("low_sugar")
    if "low_sodium" in health and _num(recipe.get("sodium_mg_per_serving")) >= SODIUM_MAX_MG:
        reasons.append("low_sodium")
    if "gout" in health and has_gout_forbidden_ingredients(recipe_ings):
        reasons.append("gout")
    if "low_carb" in health and _num(recipe.get("carbs_per_serving")) > LOW_CARB_MAX_G:
        reasons.append("low_carb")
    if "gentle_stomach" in health and method == "Chiên/Rán":
        reasons.append("gentle_stomach")
    return reasons


def method_preference(profile: dict[str, Any] | None, recipe: dict[str, Any],
                      recipe_ings: list[dict[str, Any]]) -> float:
    """+1 preferred cooking method, -1 avoided (incl. spicy when the scenario
    rules spice out), 0 neutral."""
    if not profile:
        return 0.0
    method = (recipe.get("cooking_method") or "").strip()
    score = 0.0
    if method in (profile.get("avoid_methods") or []):
        score -= 1.0
    elif method in (profile.get("prefer_methods") or []):
        score += 1.0
    if "no_spicy" in (profile.get("health") or []) and is_spicy(recipe_ings):
        score -= 1.0
    return max(-1.0, min(1.0, score))


def dish_preference(profile: dict[str, Any] | None, recipe: dict[str, Any]) -> float:
    if not profile or not profile.get("prefer_dish"):
        return 0.0
    return 1.0 if (recipe.get("dish_type") or "").strip() in profile["prefer_dish"] else 0.0


def kcal_target_gap(profile: dict[str, Any] | None, recipe: dict[str, Any]) -> float:
    """Distance outside the scenario energy band, as a fraction of the band edge."""
    if not profile:
        return 0.0
    kcal = _num(recipe.get("calories_per_serving"), -1.0)
    if kcal <= 0:
        return 0.0
    lo, hi = profile.get("kcal_band", (250, 750))
    if kcal < lo:
        return round(min(2.0, (lo - kcal) / lo), 4)
    if kcal > hi:
        return round(min(2.0, (kcal - hi) / hi), 4)
    return 0.0


def scenario_signals(pantry: dict[str, Any], recipe: dict[str, Any],
                     recipe_ings: list[dict[str, Any]]) -> dict[str, float]:
    """Scenario signals used by the teacher label (not fed to the ranker)."""
    profile = scenario_profile(pantry.get("scenario_type"))
    return {
        "hard_violation": 1.0 if hard_violations(profile, recipe, recipe_ings) else 0.0,
        "method_preference": method_preference(profile, recipe, recipe_ings),
        "dish_preference": dish_preference(profile, recipe),
        "kcal_target_gap": kcal_target_gap(profile, recipe),
    }


GAP_WEIGHT = {"tight": 0.12, "normal": 0.07, "generous": 0.04}


def teacher_score(profile: dict[str, Any] | None, feats: dict[str, float]) -> float:
    """Continuous scenario utility behind the training grades.

    `feats` = pantry features (`FEATURE_COLS`) merged with `scenario_signals`.
    Profile weights (budget, rescue priority, protein goal, beginner cook) and
    the scenario signals are invisible to the ranker.
    """
    profile = profile or {}
    budget = profile.get("budget", "normal")
    s = 0.45 * feats["core_coverage"] + 0.15 * feats["secondary_coverage"]
    s -= GAP_WEIGHT.get(budget, 0.07) * min(feats["shopping_gap_items"], 6.0)
    s += profile.get("rescue_weight", 0.15) * min(feats["rescue_weight_g"] / 200.0, 1.0)
    s += 0.12 * feats["method_preference"] + 0.08 * feats["dish_preference"]
    s -= 0.15 * min(feats["kcal_target_gap"], 1.5)
    s += 0.05 * feats["nutrition_confidence"]
    if profile.get("high_protein") and feats["protein_per_serving"] >= HIGH_PROTEIN_G:
        s += 0.10
    if profile.get("beginner"):
        s -= 0.04 * max(0.0, feats["prep_complexity"] - 3.0)
    return s


def teacher_grade(profile: dict[str, Any] | None, feats: dict[str, float]) -> int:
    """Graded relevance 0-3 for one (pantry, recipe) pair."""
    if feats["hard_violation"] >= 1.0:
        return 0
    profile = profile or {}
    missing = feats["core_missing_count"]
    if profile.get("no_shopping") and missing >= 1:
        return 0
    s = teacher_score(profile, feats)
    grade = 3 if s >= 0.55 else 2 if s >= 0.35 else 1 if s >= 0.15 else 0
    if missing >= 2:
        grade = min(grade, 1)
    elif missing >= 1:
        grade = min(grade, 1 if profile.get("budget") == "tight" else 2)
    return grade


def noisy_grade(grade: int, key: str, rate: float = 0.08) -> int:
    """Deterministic annotator disagreement: shift one grade with probability `rate`."""
    h = int.from_bytes(hashlib.sha256(key.encode("utf-8")).digest()[:8], "big")
    u = (h % 1_000_000) / 1_000_000
    if u >= rate:
        return grade
    step = 1 if (h >> 21) & 1 else -1
    return max(0, min(3, grade + step))
