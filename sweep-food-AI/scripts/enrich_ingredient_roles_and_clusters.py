"""Enrich dataset with ingredient roles and dialect dish clusters (P-1, P-2).

Rationale
---------
P-1 (Seasoning Inflation):
  55.2% of recipes have >= 50% basic seasonings and aromatics.
  Adds `ingredient_role` (core, secondary, seasoning, garnish) to ingredient
  files and `core_ingredients_count` to recipe files. This enables recommender
  systems to require core ingredient coverage (e.g. user must have beef for
  beef dishes, not just salt and oil).

P-2 (Dialect Invariance & Leakage-Free Splitting):
  Identifies regional Vietnamese dialect synonyms (lợn <-> heo, ba chỉ <-> ba rọi,
  cuộn <-> cuốn, móng giò <-> chân giò, đậu phụ <-> đậu hũ...) and groups them
  into stable `dish_cluster_id`s. GroupKFold / GroupShuffleSplit on this cluster ID
  guarantees 0 train/test leakage.

Deterministic and idempotent.
"""

from __future__ import annotations

import csv
import json
import re
import sys
import unicodedata
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PROCESSED_DIR = ROOT / "data" / "processed" / "recipes"
MASTER_CSV = ROOT / "data" / "processed" / "viendinhduong" / "master_ingredients_nutrition.csv"
REPORT_CLUSTERS = ROOT / "reports" / "eda" / "dish_dialect_clusters.json"
REPORT_ROLES = ROOT / "reports" / "eda" / "ingredient_roles_summary.json"

ING_PAIRS = (
    (PROCESSED_DIR / "recipe_ingredients.csv", PROCESSED_DIR / "recipe_ingredients.json"),
    (PROCESSED_DIR / "canonical_recipe_ingredients.csv", PROCESSED_DIR / "canonical_recipe_ingredients.json"),
)
RECIPE_PAIRS = (
    (PROCESSED_DIR / "recipes.csv", PROCESSED_DIR / "recipes.json"),
    (PROCESSED_DIR / "canonical_recipes.csv", PROCESSED_DIR / "canonical_recipes.json"),
)

SEAFOOD_KW = [
    'cá', 'tôm', 'mực', 'cua', 'nghêu', 'sò', 'ốc', 'hến', 'lươn', 'hàu',
    'bạch tuộc', 'ghẹ', 'tép', 'chả cá', 'cá viên', 'tôm viên', 'cá hồi', 'cá ngừ'
]
MEAT_KW = [
    'thịt', 'sườn', 'ba chỉ', 'ba rọi', 'gà', 'vịt', 'bò', 'heo', 'lợn',
    'trứng', 'chả lụa', 'giò sống', 'giò lụa', 'xúc xích', 'lạp xưởng',
    'gan', 'mề', 'lòng', 'cật', 'chim', 'cút', 'dê', 'cừu', 'bò viên'
]
CARB_PLANT_KW = [
    'đậu hũ', 'đậu phụ', 'tàu hũ', 'đậu hủ', 'tàu hủ ky', 'phù trúc',
    'cơm', 'gạo', 'bún', 'mì', 'miến', 'phở', 'nui', 'cháo', 'xôi',
    'bánh tráng', 'bột gạo', 'bột mì', 'bánh phở', 'bánh canh', 'khoai tây', 'khoai lang'
]
ALL_CORE_KW = SEAFOOD_KW + MEAT_KW + CARB_PLANT_KW

AROMATICS_KEYWORDS = [
    'hành lá', 'hành hoa', 'ngò', 'rau mùi', 'rau răm', 'thì là', 'lá chanh',
    'húng', 'tía tô', 'kinh giới', 'lá lốt', 'lá mơ', 'ngò gai', 'mùi tàu',
    'tỏi', 'hành tím', 'hành củ', 'hành khô', 'sả', 'gừng', 'ớt tươi', 'ớt hiểm', 'ớt sừng', 'tiêu xanh'
]

CORE_CATS = {
    'Thịt và sản phẩm chế biến',
    'Thủy sản và sản phẩm chế biến',
    'Trứng và sản phẩm chế biến',
    'Ngũ cốc và sản phẩm chế biến',
}
SEASONING_CATS = {
    'Gia vị, nước chấm',
    'Dầu, mỡ, bơ',
}

DIALECT_MAP = [
    (r'\bthịt lợn\b', 'thịt heo'),
    (r'\blợn\b', 'heo'),
    (r'\bba chỉ\b', 'ba rọi'),
    (r'\bgiò lụa\b', 'chả lụa'),
    (r'\bdạ dày\b', 'bao tử'),
    (r'\bmóng giò\b', 'chân giò'),
    (r'\bcuộn\b', 'cuốn'),
    (r'\brán\b', 'chiên'),
    (r'\bum\b', 'om'),
    (r'\bđậu phụ\b', 'đậu hũ'),
    (r'\bđậu hủ\b', 'đậu hũ'),
    (r'\btàu hũ\b', 'đậu hũ'),
    (r'\bmướp đắng\b', 'khổ qua'),
    (r'\bdọc mùng\b', 'bạc hà'),
    (r'\brau mùi\b', 'ngò rí'),
    (r'\bmùi tàu\b', 'ngò gai'),
    (r'\btrái\b', 'quả'),
]


def load_master_categories() -> dict[str, str]:
    with open(MASTER_CSV, "r", encoding="utf-8-sig") as f:
        return {r["code"].strip(): r.get("category_vi", "").strip() for r in csv.DictReader(f) if r.get("code")}


def dialect_normalize(name: str) -> str:
    s = unicodedata.normalize('NFKC', str(name)).lower()
    s = re.sub(r'[\(\)\[\],.:;!\?\-_/]+', ' ', s)
    s = re.sub(r'\s+', ' ', s).strip()
    for pat, rep in DIALECT_MAP:
        s = re.sub(pat, rep, s)
    return s


def assign_ingredient_roles(rows: list[dict], master_cats: dict[str, str]) -> tuple[list[dict], dict]:
    # First pass: rule-based assignment
    for row in rows:
        code = (row.get("master_ingredient_code") or "").strip().replace(".0", "")
        cat = master_cats.get(code, "")
        name = (row.get("cleaned_name") or "").lower()

        if cat in SEASONING_CATS:
            row["ingredient_role"] = "seasoning"
            continue
        if any(k in name for k in ['nước mắm', 'hạt nêm', 'bột ngọt', 'mì chính', 'muối', 'đường', 'tiêu', 'dầu ăn', 'nước tương', 'xì dầu', 'dầu hào', 'giấm', 'nước màu', 'sa tế', 'mắm tôm', 'mắm ruốc', 'bột quế', 'hoa hồi', 'ngũ vị hương', 'nước lọc', 'nước dùng', 'dầu mè']):
            row["ingredient_role"] = "seasoning"
            continue

        if any(k in name for k in AROMATICS_KEYWORDS):
            try:
                w_val = float(row.get("estimated_weight_g") or 10.0)
            except (ValueError, TypeError):
                w_val = 10.0
            if w_val <= 60.0:
                row["ingredient_role"] = "garnish"
                continue
            else:
                row["ingredient_role"] = "secondary"
                continue

        if cat in CORE_CATS or any(k in name for k in ALL_CORE_KW):
            row["ingredient_role"] = "core"
            continue

        row["ingredient_role"] = "secondary"

    # Second pass: ensure every recipe has >= 1 core ingredient
    by_recipe: dict[str, list[dict]] = {}
    for r in rows:
        by_recipe.setdefault(r["recipe_id"], []).append(r)

    promoted_count = 0
    for rid, ings in by_recipe.items():
        has_core = any(i["ingredient_role"] == "core" for i in ings)
        if not has_core:
            # Promote the heaviest non-seasoning ingredient
            candidates = [i for i in ings if i["ingredient_role"] != "seasoning"]
            if not candidates:
                candidates = ings
            best = max(candidates, key=lambda x: float(x.get("estimated_weight_g") or 0.0))
            best["ingredient_role"] = "core"
            promoted_count += 1

    dist = Counter(r["ingredient_role"] for r in rows)
    core_per_recipe = {
        rid: sum(1 for i in ings if i["ingredient_role"] == "core")
        for rid, ings in by_recipe.items()
    }

    summary = {
        "total_ingredient_rows": len(rows),
        "role_distribution": dict(dist.most_common()),
        "role_percentages": {k: round(v / len(rows) * 100, 2) for k, v in dist.most_common()},
        "promoted_zero_core_recipes": promoted_count,
        "recipes_with_at_least_one_core": len(core_per_recipe),
        "median_core_ingredients_per_recipe": sorted(core_per_recipe.values())[len(core_per_recipe) // 2],
    }
    return rows, core_per_recipe, summary


def generate_clusters(recipes: list[dict]) -> tuple[dict[str, str], dict]:
    key_to_recipes: dict[str, list[dict]] = {}
    for r in recipes:
        key = dialect_normalize(r["name"])
        key_to_recipes.setdefault(key, []).append(r)

    recipe_to_cluster: dict[str, str] = {}
    cluster_report = {
        "total_recipes": len(recipes),
        "total_distinct_clusters": len(key_to_recipes),
        "multi_recipe_clusters_count": sum(1 for group in key_to_recipes.values() if len(group) > 1),
        "multi_recipe_clusters": [],
    }

    cluster_idx = 1
    # Sort keys for deterministic cluster numbering
    for key in sorted(key_to_recipes.keys()):
        group = key_to_recipes[key]
        cid = f"cluster_{cluster_idx:05d}"
        cluster_idx += 1
        for r in group:
            recipe_to_cluster[r["id"]] = cid

        if len(group) > 1:
            cluster_report["multi_recipe_clusters"].append({
                "cluster_id": cid,
                "cluster_normalized_name": key,
                "recipe_count": len(group),
                "recipes": [
                    {
                        "id": r["id"],
                        "name": r["name"],
                        "source_platform": r["source_platform"],
                    }
                    for r in group
                ],
            })

    return recipe_to_cluster, cluster_report


def update_ingredient_file_pair(csv_path: Path, json_path: Path, rows: list[dict]) -> None:
    with open(csv_path, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        fields = list(reader.fieldnames)

    if "ingredient_role" not in fields:
        # Insert before canonical_recipe_id or append
        if "canonical_recipe_id" in fields:
            idx = fields.index("canonical_recipe_id")
            fields.insert(idx, "ingredient_role")
        else:
            fields.append("ingredient_role")

    with open(csv_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)

    with open(json_path, "r", encoding="utf-8") as f:
        json_rows = json.load(f)
    by_id = {r["id"]: r["ingredient_role"] for r in rows}
    for jr in json_rows:
        jr["ingredient_role"] = by_id.get(jr.get("id"), "secondary")

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(json_rows, f, ensure_ascii=False, indent=2)


def update_recipe_file_pair(
    csv_path: Path,
    json_path: Path,
    core_per_recipe: dict[str, int],
    recipe_to_cluster: dict[str, str],
) -> None:
    with open(csv_path, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        fields = list(reader.fieldnames)
        rows = list(reader)

    new_cols = ["core_ingredients_count", "dish_cluster_id"]
    for col in new_cols:
        if col not in fields:
            if "canonical_recipe_id" in fields:
                idx = fields.index("canonical_recipe_id")
                fields.insert(idx, col)
            else:
                fields.append(col)

    for r in rows:
        rid = r["id"]
        r["core_ingredients_count"] = str(core_per_recipe.get(rid, 1))
        r["dish_cluster_id"] = recipe_to_cluster.get(rid, "")

    with open(csv_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)

    with open(json_path, "r", encoding="utf-8") as f:
        json_rows = json.load(f)
    for jr in json_rows:
        rid = jr.get("id")
        jr["core_ingredients_count"] = core_per_recipe.get(rid, 1)
        jr["dish_cluster_id"] = recipe_to_cluster.get(rid, "")

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(json_rows, f, ensure_ascii=False, indent=2)


def main() -> None:
    master_cats = load_master_categories()

    # 1. Process ingredients
    sample_csv = ING_PAIRS[0][0]
    with open(sample_csv, "r", encoding="utf-8-sig") as f:
        ing_rows = list(csv.DictReader(f))

    ing_rows, core_per_recipe, role_summary = assign_ingredient_roles(ing_rows, master_cats)

    for csv_path, json_path in ING_PAIRS:
        # Load specific rows to preserve order/fields
        with open(csv_path, "r", encoding="utf-8-sig") as f:
            pair_rows = list(csv.DictReader(f))
        pair_rows, _, _ = assign_ingredient_roles(pair_rows, master_cats)
        update_ingredient_file_pair(csv_path, json_path, pair_rows)
        print(f"Updated {csv_path.name}: added ingredient_role to {len(pair_rows):,} rows.")

    REPORT_ROLES.parent.mkdir(parents=True, exist_ok=True)
    with open(REPORT_ROLES, "w", encoding="utf-8") as f:
        json.dump(role_summary, f, ensure_ascii=False, indent=2)
    print(f"Role Summary -> {REPORT_ROLES.relative_to(ROOT)}")

    # 2. Process recipes & clusters
    sample_recipe_csv = RECIPE_PAIRS[0][0]
    with open(sample_recipe_csv, "r", encoding="utf-8-sig") as f:
        recipe_rows = list(csv.DictReader(f))

    recipe_to_cluster, cluster_report = generate_clusters(recipe_rows)

    for csv_path, json_path in RECIPE_PAIRS:
        update_recipe_file_pair(csv_path, json_path, core_per_recipe, recipe_to_cluster)
        print(f"Updated {csv_path.name}: added core_ingredients_count and dish_cluster_id to {len(recipe_rows):,} recipes.")

    REPORT_CLUSTERS.parent.mkdir(parents=True, exist_ok=True)
    with open(REPORT_CLUSTERS, "w", encoding="utf-8") as f:
        json.dump(cluster_report, f, ensure_ascii=False, indent=2)
    print(f"Clusters Report -> {REPORT_CLUSTERS.relative_to(ROOT)}")
    print(f"  Identified {cluster_report['multi_recipe_clusters_count']} dialect multi-recipe clusters across {len(recipe_rows)} recipes.")


if __name__ == "__main__":
    main()
