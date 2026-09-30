"""Recipe Classifier and Taxonomy Pipeline.

Categorizes recipes across three orthogonal axes:
1. Cooking Method (Phương pháp nấu)
2. Dish Type / Meal Role (Vai trò món ăn)
3. Diet & Audience (Chế độ ăn & Đối tượng)
"""

from __future__ import annotations

import csv
import json
import logging
import re
import sys
from pathlib import Path
from typing import Any

if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger("RecipeClassifier")

WORKSPACE_ROOT = Path(__file__).resolve().parent.parent

RECIPES_JSON = WORKSPACE_ROOT / "data" / "processed" / "recipes" / "recipes.json"
RECIPES_CSV = WORKSPACE_ROOT / "data" / "processed" / "recipes" / "recipes.csv"
ING_JSON = WORKSPACE_ROOT / "data" / "processed" / "recipes" / "recipe_ingredients.json"

INTERIM_RECIPES_JSON = WORKSPACE_ROOT / "data" / "interim" / "recipes_crawled_cleaned.json"
INTERIM_RECIPES_CSV = WORKSPACE_ROOT / "data" / "interim" / "recipes_crawled_cleaned.csv"


METHOD_KEYWORDS: list[tuple[str, list[str]]] = [
    ("Kho", ["kho", "rim", "ram", "om", "khìa"]),
    ("Chiên/Rán", ["chiên", "rán", "chao dầu", "chả giò", "nem rán", "bánh xèo"]),
    ("Xào", ["xào", "rang", "cháy cạnh"]),
    ("Canh/Súp", ["canh", "súp", "soup", "cháo", "lẩu", "tiềm", "hầm", "phở", "bún nước", "bánh canh"]),
    ("Nướng", ["nướng", "quay", "áp chảo", "đút lò"]),
    ("Hấp", ["hấp", "chưng", "đồ xôi", "xôi"]),
    ("Luộc", ["luộc", "chần"]),
    ("Trộn/Gỏi", ["gỏi", "nộm", "salad", "trộn", "bóp thấu"]),
    ("Pha chế", ["sinh tố", "nước ép", "trà", "cà phê", "sữa chua", "nước tắc", "pha"]),
    ("Ngâm/Muối chua", ["ngâm", "muối chua", "dưa chua", "muối dưa"]),
]

DISH_TYPE_KEYWORDS: list[tuple[str, list[str]]] = [
    ("Đồ uống", ["sinh tố", "nước ép", "trà", "cà phê", "sữa hạt", "đá bào"]),
    ("Món tráng miệng", ["chè", "thạch", "kem", "bánh flan", "sữa chua", "bánh ngọt"]),
    ("Món khai vị / Gỏi", ["gỏi", "nộm", "salad", "khai vị"]),
    ("Canh", ["canh"]),
    ("Món ăn vặt", ["bánh tráng", "khoai tây chiên", "bắp rang", "snack", "nem chua rán", "chả cá viên"]),
]

NON_VEG_PATTERNS = [
    "thịt", "bò", "heo", "lợn", "gà", "vịt", "cá", "tôm", "mực", "cua", "ốc",
    "ngao", "sò", "ếch", "bê", "trâu", "chả lụa", "giò lợn", "sườn", "nạc",
    "ba chỉ", "ba rọi", "trứng", "xúc xích", "lạp xưởng", "mắm", "nước mắm"
]

EAT_CLEAN_POSITIVE = [
    "ức gà", "salad", "yến mạch", "gạo lứt", "cải xoăn", "bơ sáp", "khoai lang",
    "hạt chia", "dầu ô liu", "luộc", "hấp", "eat clean", "giảm cân", "healthy"
]


def classify_cooking_method(name: str) -> str:
    n = name.lower()
    for method, kw_list in METHOD_KEYWORDS:
        for kw in kw_list:
            if re.search(r"\b" + re.escape(kw) + r"\b", n):
                return method
    return "Khác"


def classify_dish_type(name: str, cooking_method: str) -> str:
    n = name.lower()
    for dtype, kw_list in DISH_TYPE_KEYWORDS:
        for kw in kw_list:
            if re.search(r"\b" + re.escape(kw) + r"\b", n):
                return dtype
    if cooking_method == "Canh/Súp":
        if any(w in n for w in ["cháo", "súp", "lẩu", "phở", "bún"]):
            return "Món chính"
        return "Canh"
    return "Món chính"


def classify_diet_tags(name: str, ing_names: list[str], calories: float | None) -> list[str]:
    tags: list[str] = []
    n = name.lower()
    combined = (n + " " + " ".join(ing_names)).lower()

    # 1. Vegetarian
    is_vegan_title = any(k in n for k in ["chay", "thuần chay"])
    has_animal_ing = any(re.search(r"\b" + re.escape(pat) + r"\b", combined) for pat in NON_VEG_PATTERNS)
    if is_vegan_title or not has_animal_ing:
        tags.append("Ăn chay")

    # 2. Eat Clean / Diet
    has_clean_words = any(k in combined for k in EAT_CLEAN_POSITIVE)
    low_cal = (calories is not None) and (0 < calories <= 550)
    if (has_clean_words or low_cal) and not any(k in n for k in ["chiên ngập dầu", "mỡ hành"]):
        tags.append("Eat Clean / Giảm cân")

    # 3. Kids / Child-friendly
    if any(k in n for k in ["cháo", "súp", "cho bé", "ăn dặm", "trẻ em", "viên chiên", "bánh xèo"]):
        tags.append("Món cho trẻ em")

    # 4. Family Meals
    if not any(k in n for k in ["sinh tố", "nước ép", "trà", "cà phê"]):
        tags.append("Món cơm gia đình")

    return tags if tags else ["Món cơm gia đình"]


def run_classification():
    with open(RECIPES_JSON, "r", encoding="utf-8") as f:
        recipes = json.load(f)
    with open(ING_JSON, "r", encoding="utf-8") as f:
        ingredients = json.load(f)

    recipe_ing_map: dict[str, list[str]] = {}
    for ing in ingredients:
        r_id = ing["recipe_id"]
        c_name = ing.get("cleaned_name") or ""
        recipe_ing_map.setdefault(r_id, []).append(c_name)

    for r in recipes:
        name = r["name"]
        method = classify_cooking_method(name)
        dtype = classify_dish_type(name, method)
        ing_list = recipe_ing_map.get(r["id"], [])
        cal = r.get("total_calories")
        cal_val = float(cal) if cal and str(cal).isdigit() else None
        diet_tags = classify_diet_tags(name, ing_list, cal_val)

        r["cooking_method"] = method
        r["dish_type"] = dtype
        r["diet_tags"] = diet_tags
        r["tags"] = [method, dtype] + [t for t in diet_tags if t not in (method, dtype)]

    with open(RECIPES_JSON, "w", encoding="utf-8") as f:
        json.dump(recipes, f, ensure_ascii=False, indent=2)

    with open(RECIPES_CSV, "r", encoding="utf-8-sig") as f:
        fieldnames = csv.DictReader(f).fieldnames

    with open(RECIPES_CSV, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in recipes:
            writer.writerow({
                "id": r["id"],
                "name": r["name"],
                "source_platform": r.get("source_platform", ""),
                "source_url": r.get("source_url", ""),
                "default_servings": r.get("default_servings", 4.0),
                "estimated_cooking_minutes": r.get("estimated_cooking_minutes", 30),
                "cooking_method": r.get("cooking_method", ""),
                "dish_type": r.get("dish_type", ""),
                "diet_tags": "; ".join(r.get("diet_tags", [])) if isinstance(r.get("diet_tags"), list) else r.get("diet_tags", ""),
                "total_calories": r.get("total_calories", ""),
                "total_protein_g": r.get("total_protein_g", ""),
                "total_fat_g": r.get("total_fat_g", ""),
                "total_carbs_g": r.get("total_carbs_g", ""),
                "ingredients_count": r.get("ingredients_count", 0),
            })

    # Sync to interim
    with open(INTERIM_RECIPES_JSON, "w", encoding="utf-8") as f:
        json.dump(recipes, f, ensure_ascii=False, indent=2)
    shutil.copy2(RECIPES_CSV, INTERIM_RECIPES_CSV)
    logger.info("Classification completed and synced.")


if __name__ == "__main__":
    run_classification()
