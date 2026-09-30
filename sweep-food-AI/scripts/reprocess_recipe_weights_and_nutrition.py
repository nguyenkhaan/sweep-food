"""
Reprocess recipe ingredients with role-based and unit-based weight estimation,
recalculate portion nutrition using audited master data, and update recipe rollups.
"""

import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from nlp.nutrition import scale_nutrition, nutrition_value, NUTRITION_FIELDS
ROOT = Path(__file__).resolve().parent.parent

def estimate_role_based_weight(row, master_info):
    raw_l = (row.get("raw_text") or "").strip().lower()
    clean_l = (row.get("cleaned_name") or "").strip().lower()
    category = master_info.get("category_vi", "") if master_info else ""

    # Dry seasonings & spices
    if any(k in raw_l for k in ["tiêu", "muối", "mì chính", "bột ngọt", "ớt bột", "ngũ vị hương", "bột quế", "tai hồi", "hoa hồi", "bột canh", "bột nêm", "hạt nêm"]):
        return 3.0
    
    # Liquid seasonings & oils
    if any(k in raw_l for k in ["dầu ăn", "nước mắm", "nước tương", "xì dầu", "dầu hào", "giấm", "dấm", "mỡ nước", "nước màu"]):
        return 10.0

    # Sugar and sweeteners
    if any(k in raw_l for k in ["đường", "mật ong", "đường phèn", "đường thốt nốt"]):
        return 10.0

    # Alliums & aromatics (garlic, scallions, shallots, ginger, chili, lemongrass)
    if any(k in raw_l for k in ["hành lá", "hành tím", "ngò rí", "rau mùi", "tỏi", "gừng", "sả", "ớt", "rau răm", "hành boa-rô", "thì là", "lá chanh"]):
        return 10.0

    # Role by master category if available
    if category == "Thịt và sản phẩm chế biến" or any(k in raw_l for k in ["thịt", "sườn", "thịt heo", "thịt bò", "thịt gà", "thịt vịt", "gà", "thịt đùi", "ba rọi", "thịt nạc", "giò sống", "xương"]):
        return 150.0

    if category == "Thủy sản và sản phẩm chế biến" or any(k in raw_l for k in ["cá", "tôm", "mực", "cua", "nghêu", "sò", "ốc", "hến", "lươn"]):
        return 150.0

    if category == "Trứng và sản phẩm chế biến" or any(k in raw_l for k in ["trứng", "hột vịt", "trứng gà", "trứng cút"]):
        return 55.0

    if category == "Ngũ cốc và sản phẩm chế biến" or any(k in raw_l for k in ["cơm", "bún", "phở", "mì", "bánh mì", "bánh tráng", "bột gạo", "bột mì", "gạo"]):
        return 100.0

    if category == "Khoai củ và sản phẩm chế biến" or any(k in raw_l for k in ["khoai tây", "khoai lang", "khoai môn", "củ sắn", "khoai mỡ"]):
        return 100.0

    if any(k in raw_l for k in ["đậu hũ", "đậu phụ", "tàu hũ", "đậu hũ ky", "sườn non chay", "thịt chay"]):
        return 100.0

    if category == "Rau, quả, củ dùng làm rau" or any(k in raw_l for k in ["rau", "cải", "cà chua", "dưa leo", "cà rốt", "bắp cải", "su hào", "bí đỏ", "mướp", "khổ qua"]):
        return 80.0

    if any(k in raw_l for k in ["nước lọc", "nước dùng", "nước luộc", "nước dừa"]):
        return 150.0

    if category == "Gia vị, nước chấm" or category == "Dầu, mỡ, bơ":
        return 10.0

    return 10.0


def reprocess():
    ing_csv_path = ROOT / "data" / "processed" / "recipes" / "recipe_ingredients.csv"
    ing_json_path = ROOT / "data" / "processed" / "recipes" / "recipe_ingredients.json"
    recipes_csv_path = ROOT / "data" / "processed" / "recipes" / "recipes.csv"
    recipes_json_path = ROOT / "data" / "processed" / "recipes" / "recipes.json"
    master_path = ROOT / "data" / "processed" / "viendinhduong" / "master_ingredients_nutrition.csv"

    with open(master_path, "r", encoding="utf-8-sig") as f:
        master_dict = {row["code"].strip(): row for row in csv.DictReader(f) if row.get("code")}

    with open(ing_csv_path, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        ing_fieldnames = reader.fieldnames
        ing_rows = list(reader)

    adjusted_weights = 0

    for row in ing_rows:
        method = row.get("match_method", "").strip().upper()
        code = row.get("master_ingredient_code", "").strip()
        m_info = master_dict.get(code) if code in master_dict else None

        # UNMATCHED invariant check
        if method == "UNMATCHED":
            row["master_ingredient_code"] = ""
            row["master_ingredient_name"] = ""
            # A leftover numeric confidence from a since-rejected or since-
            # cleared candidate must not survive alongside a row asserting
            # "no master link" -- see scripts/fix_unmatched_invariants.py.
            row["match_confidence"] = None
            # Unknown, not a measured zero: nlp/nutrition.py's missing semantics
            # (blank/None/NaN) apply here too. csv.DictWriter renders None as an
            # empty CSV cell; json.dump renders it as null.
            row["calories"] = None
            row["protein_g"] = None
            row["fat_g"] = None
            row["carbs_g"] = None
            continue

        # Check if row has missing quantity
        has_qty = bool(row.get("required_quantity", "").strip())
        current_w = nutrition_value(row.get("estimated_weight_g"))

        if not has_qty and current_w in (10.0, None):
            new_w = estimate_role_based_weight(row, m_info)
            if new_w != current_w:
                row["estimated_weight_g"] = str(round(new_w, 1))
                adjusted_weights += 1
                current_w = new_w

        # Recalculate nutrition using audited master data and accurate weight
        if m_info and current_w and current_w > 0:
            ratio = current_w / 100.0
            for field, source in NUTRITION_FIELDS.items():
                master_val = m_info.get(source)
                scaled = scale_nutrition(master_val, ratio, 1)
                row[field] = "" if scaled is None else str(scaled)

    print(f"Adjusted role-based weights for {adjusted_weights} ingredient rows.")

    with open(ing_csv_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=ing_fieldnames)
        writer.writeheader()
        writer.writerows(ing_rows)

    with open(ing_json_path, "w", encoding="utf-8") as f:
        json.dump(ing_rows, f, ensure_ascii=False, indent=2)

    # Recalculate recipe rollups
    recipe_totals = {}
    recipe_missing = {}

    for row in ing_rows:
        rid = row["recipe_id"]
        if rid not in recipe_totals:
            recipe_totals[rid] = {"calories": 0.0, "protein": 0.0, "fat": 0.0, "carbs": 0.0, "count": 0}
            recipe_missing[rid] = 0
        recipe_totals[rid]["count"] += 1
        
        cal = nutrition_value(row.get("calories"))
        p = nutrition_value(row.get("protein_g"))
        fat = nutrition_value(row.get("fat_g"))
        c = nutrition_value(row.get("carbs_g"))

        if cal is None:
            recipe_missing[rid] += 1
        else:
            recipe_totals[rid]["calories"] += cal
        if p is not None:
            recipe_totals[rid]["protein"] += p
        if fat is not None:
            recipe_totals[rid]["fat"] += fat
        if c is not None:
            recipe_totals[rid]["carbs"] += c

    with open(recipes_csv_path, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        recipe_fieldnames = reader.fieldnames
        recipe_rows = list(reader)

    for r in recipe_rows:
        rid = r["id"]
        if rid in recipe_totals:
            t = recipe_totals[rid]
            r["total_calories"] = str(round(t["calories"], 1))
            r["total_protein_g"] = str(round(t["protein"], 1))
            r["total_fat_g"] = str(round(t["fat"], 1))
            r["total_carbs_g"] = str(round(t["carbs"], 1))
            r["ingredients_count"] = str(t["count"])

    with open(recipes_csv_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=recipe_fieldnames)
        writer.writeheader()
        writer.writerows(recipe_rows)

    # Update recipes JSON with metadata
    json_recipe_data = []
    for r in recipe_rows:
        rid = r["id"]
        rec_copy = dict(r)
        miss_cnt = recipe_missing.get(rid, 0)
        tot_cnt = int(r.get("ingredients_count") or 1)
        if miss_cnt == 0:
            rec_copy["nutrition_status"] = "COMPLETE"
        elif miss_cnt / max(tot_cnt, 1) < 0.3:
            rec_copy["nutrition_status"] = "PARTIAL"
        else:
            rec_copy["nutrition_status"] = "INCOMPLETE"
        rec_copy["missing_nutrition_count"] = miss_cnt
        json_recipe_data.append(rec_copy)

    with open(recipes_json_path, "w", encoding="utf-8") as f:
        json.dump(json_recipe_data, f, ensure_ascii=False, indent=2)

    print(f"Updated {len(recipe_rows)} recipes with fresh nutrition rollups and completeness flags.")

if __name__ == "__main__":
    reprocess()
