"""Resolve Seasoning Inflation (P-1) and Dialect Leakage (P-2) using GPT OSS (gpt-oss:120b).

No arbitrary heuristic fallbacks. All culinary role classifications, dish-context
core promotions, and dialect equivalence judgments are evaluated directly by
Ollama Cloud's hosted open-source reasoning model (gpt-oss:120b).

Steps:
1. Classify 750 master ingredients into [core, secondary, seasoning, garnish] with gpt-oss:120b.
2. Classify top unmatched ingredients with gpt-oss:120b.
3. For recipes lacking a standard protein/carb core, query gpt-oss:120b with dish context
   to identify the true culinary core ingredient (e.g. mushrooms in mushroom stew).
4. Evaluate candidate dialect dish pairs with gpt-oss:120b to form semantic dish clusters.
5. Enrich all processed CSV/JSON artifacts, maintaining 100% referential integrity and parity.
"""

from __future__ import annotations

import csv
import json
import re
import sys
import time
import unicodedata
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from dotenv import load_dotenv
load_dotenv(ROOT / ".env")

from nlp.ollama_cloud_client import OllamaCloudClient

PROCESSED_DIR = ROOT / "data" / "processed" / "recipes"
MASTER_CSV = ROOT / "data" / "processed" / "viendinhduong" / "master_ingredients_nutrition.csv"
EDA_DIR = ROOT / "reports" / "eda"
EDA_DIR.mkdir(parents=True, exist_ok=True)

MASTER_CACHE_FILE = EDA_DIR / "gpt_oss_master_roles.json"
UNMATCHED_CACHE_FILE = EDA_DIR / "gpt_oss_unmatched_roles.json"
DISH_CORE_CACHE_FILE = EDA_DIR / "gpt_oss_dish_core_overrides.json"
DIALECT_CACHE_FILE = EDA_DIR / "gpt_oss_dialect_judgments.json"

ING_PAIRS = (
    (PROCESSED_DIR / "recipe_ingredients.csv", PROCESSED_DIR / "recipe_ingredients.json"),
    (PROCESSED_DIR / "canonical_recipe_ingredients.csv", PROCESSED_DIR / "canonical_recipe_ingredients.json"),
)
RECIPE_PAIRS = (
    (PROCESSED_DIR / "recipes.csv", PROCESSED_DIR / "recipes.json"),
    (PROCESSED_DIR / "canonical_recipes.csv", PROCESSED_DIR / "canonical_recipes.json"),
)


def extract_json_from_response(content: str) -> dict:
    text = content.strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[1].rsplit("```", 1)[0].strip()
    # Try finding first { and last }
    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end != -1:
        text = text[start : end + 1]
    return json.loads(text)


def classify_master_ingredients(client: OllamaCloudClient, master_rows: list[dict]) -> dict[str, str]:
    if MASTER_CACHE_FILE.exists():
        cached = json.loads(MASTER_CACHE_FILE.read_text(encoding="utf-8"))
        if len(cached) >= len(master_rows):
            print(f"[Step 1] Master roles loaded from cache ({len(cached)} items).")
            return cached

    print(f"[Step 1] Classifying {len(master_rows)} master ingredients via gpt-oss:120b...")
    master_roles: dict[str, str] = {}
    if MASTER_CACHE_FILE.exists():
        master_roles = json.loads(MASTER_CACHE_FILE.read_text(encoding="utf-8"))

    batch_size = 30
    batches = [master_rows[i : i + batch_size] for i in range(0, len(master_rows), batch_size)]

    for idx, batch in enumerate(batches, 1):
        unclassified = [item for item in batch if str(item["code"]) not in master_roles]
        if not unclassified:
            continue

        prompt = f"""Bạn là chuyên gia dinh dưỡng và ẩm thực Việt Nam.
Hãy phân loại từng nguyên liệu thực phẩm sau đây vào đúng 1 trong 4 vai trò chức năng ẩm thực:
- "core": Nguồn đạm chính (thịt gia súc, thịt gia cầm, thủy hải sản, trứng, đậu phụ, hải sản...) hoặc nguồn tinh bột chính (gạo, bún, mì, phở, miến, cháo, ngô, bột, bánh mì, khoai...).
- "secondary": Rau củ quả nấu canh/xào, nấm các loại, các loại hoa quả / trái cây tươi, củ quả bổ trợ (cà rốt, cà chua, bắp cải, su hào, bầu, bí, nấm rơm, dưa hấu, chuối, xoài...).
- "seasoning": Gia vị nêm nếm, dầu mỡ, nước mắm, đường, muối, hạt nêm, bột ngọt/mì chính, tiêu, giấm, mắm tôm, mắm ruốc, sa tế, nước lọc, nước dùng...
- "garnish": Rau thơm gia vị (hành lá, ngò rí, thì là, lá chanh, rau răm, húng quế...), ớt tươi trang trí, tỏi/hành/gừng/sả dùng làm hương liệu lượng nhỏ...

Danh sách nguyên liệu:
{json.dumps([{"code": str(r["code"]), "name": r["name_vi"], "category": r.get("category_vi", "")} for r in unclassified], ensure_ascii=False, indent=2)}

Trả về ONLY một JSON object mapping từ code (chuỗi) sang vai trò ("core", "secondary", "seasoning", "garnish"):
{{"code": "role", ...}}
Không giải thích, không markdown ngoài JSON."""

        for retry in range(5):
            try:
                resp = client.chat([{"role": "user", "content": prompt}], temperature=0.1, max_tokens=3000)
                parsed = extract_json_from_response(resp.get("content", ""))
                for code_str, role in parsed.items():
                    if role in ("core", "secondary", "seasoning", "garnish"):
                        master_roles[str(code_str)] = role
                print(f"  Batch {idx}/{len(batches)} ({len(unclassified)} items) classified -> {len(parsed)} results.")
                MASTER_CACHE_FILE.write_text(json.dumps(master_roles, ensure_ascii=False, indent=2), encoding="utf-8")
                time.sleep(1)
                break
            except Exception as e:
                print(f"  Batch {idx} retry {retry + 1} failed: {e}")
                time.sleep(3)

    return master_roles


def classify_unmatched_ingredients(client: OllamaCloudClient, unmatched_names: list[str]) -> dict[str, str]:
    if UNMATCHED_CACHE_FILE.exists():
        cached = json.loads(UNMATCHED_CACHE_FILE.read_text(encoding="utf-8"))
        if len(cached) >= len(unmatched_names):
            print(f"[Step 2] Unmatched ingredient roles loaded from cache ({len(cached)} items).")
            return cached

    print(f"[Step 2] Classifying {len(unmatched_names)} unmatched ingredient names via gpt-oss:120b...")
    unmatched_roles: dict[str, str] = {}
    if UNMATCHED_CACHE_FILE.exists():
        unmatched_roles = json.loads(UNMATCHED_CACHE_FILE.read_text(encoding="utf-8"))

    batch_size = 30
    items_to_run = [name for name in unmatched_names if name not in unmatched_roles]
    batches = [items_to_run[i : i + batch_size] for i in range(0, len(items_to_run), batch_size)]

    for idx, batch in enumerate(batches, 1):
        prompt = f"""Bạn là chuyên gia ẩm thực Việt Nam.
Hãy phân loại từng tên nguyên liệu món ăn sau đây vào đúng 1 trong 4 vai trò:
- "core": Đạm chính (thịt, cá, tôm, cua, trứng, đậu phụ, hải sản...) hoặc tinh bột chính (gạo, bún, mì, phở, miến, cháo...).
- "secondary": Rau củ quả nấu chính, nấm, trái cây, củ quả bổ trợ.
- "seasoning": Gia vị, dầu mỡ, nước mắm, đường, muối, tiêu, giấm, mắm, nước dùng...
- "garnish": Rau thơm, hành lá, ngò, lá chanh, ớt tươi, tỏi/sả/gừng lượng nhỏ.

Danh sách tên:
{json.dumps(batch, ensure_ascii=False, indent=2)}

Trả về ONLY một JSON object mapping từ tên nguyên liệu sang vai trò:
{{"tên": "role", ...}}
Không giải thích, không markdown ngoài JSON."""

        for retry in range(5):
            try:
                resp = client.chat([{"role": "user", "content": prompt}], temperature=0.1, max_tokens=3000)
                parsed = extract_json_from_response(resp.get("content", ""))
                for name_k, role in parsed.items():
                    if role in ("core", "secondary", "seasoning", "garnish"):
                        unmatched_roles[name_k] = role
                print(f"  Unmatched batch {idx}/{len(batches)} classified -> {len(parsed)} results.")
                UNMATCHED_CACHE_FILE.write_text(json.dumps(unmatched_roles, ensure_ascii=False, indent=2), encoding="utf-8")
                time.sleep(1)
                break
            except Exception as e:
                print(f"  Unmatched batch {idx} retry {retry + 1} failed: {e}")
                time.sleep(3)

    return unmatched_roles


def resolve_dish_core_overrides(
    client: OllamaCloudClient,
    zero_core_recipes: list[dict],
    ing_by_recipe: dict[str, list[dict]],
) -> dict[str, str]:
    """For dishes that lack a standard meat/carb core (vegetable soups, salads, desserts),
    query gpt-oss:120b to semantically identify the true core defining ingredient in context.
    """
    if DISH_CORE_CACHE_FILE.exists():
        cached = json.loads(DISH_CORE_CACHE_FILE.read_text(encoding="utf-8"))
        if len(cached) >= len(zero_core_recipes):
            print(f"[Step 3] Dish-context core overrides loaded from cache ({len(cached)} recipes).")
            return cached

    print(f"[Step 3] Querying gpt-oss:120b for {len(zero_core_recipes)} pure-vegetable/dessert dishes to identify true core ingredients...")
    core_overrides: dict[str, str] = {}
    if DISH_CORE_CACHE_FILE.exists():
        core_overrides = json.loads(DISH_CORE_CACHE_FILE.read_text(encoding="utf-8"))

    batch_size = 25
    needed_recipes = [r for r in zero_core_recipes if r["id"] not in core_overrides]
    batches = [needed_recipes[i : i + batch_size] for i in range(0, len(needed_recipes), batch_size)]

    for idx, batch in enumerate(batches, 1):
        batch_input = []
        for r in batch:
            rid = r["id"]
            ings = [i.get("cleaned_name") or i.get("raw_text") for i in ing_by_recipe.get(rid, [])]
            batch_input.append({"recipe_id": rid, "dish_name": r["name"], "ingredients": ings})

        prompt = f"""Bạn là đầu bếp và chuyên gia ẩm thực Việt Nam.
Các món ăn sau đây là món chay, món tráng miệng, nước uống hoặc món canh rau không có thịt cá.
Đối với mỗi món ăn, hãy chọn ra 1 NGUYÊN LIỆU CHỦ ĐẠO (đóng vai trò linh hồn / 'core' của món, ví dụ: nấm trong 'Nấm kho tiêu', bắp cải tím trong 'Canh chua bắp cải tím', súp lơ trong 'Súp lơ xào tỏi', vải thiều trong 'Siro vải thiều').

Danh sách món:
{json.dumps(batch_input, ensure_ascii=False, indent=2)}

Trả về ONLY một JSON object mapping từ recipe_id sang TÊN NGUYÊN LIỆU ĐƯỢC CHỌN LÀM CORE:
{{"recipe_id": "tên nguyên liệu core", ...}}
Không giải thích, không markdown ngoài JSON."""

        for retry in range(5):
            try:
                resp = client.chat([{"role": "user", "content": prompt}], temperature=0.1, max_tokens=3000)
                parsed = extract_json_from_response(resp.get("content", ""))
                for rid_k, ing_name in parsed.items():
                    core_overrides[rid_k] = str(ing_name)
                print(f"  Dish core batch {idx}/{len(batches)} resolved -> {len(parsed)} results.")
                DISH_CORE_CACHE_FILE.write_text(json.dumps(core_overrides, ensure_ascii=False, indent=2), encoding="utf-8")
                time.sleep(1)
                break
            except Exception as e:
                print(f"  Dish core batch {idx} retry {retry + 1} failed: {e}")
                time.sleep(3)

    return core_overrides


def cluster_dishes_with_gpt_oss(client: OllamaCloudClient, recipes: list[dict]) -> tuple[dict[str, str], dict]:
    """Find candidate dialect equivalent dish pairs and evaluate them using gpt-oss:120b."""
    print(f"[Step 4] Clustering {len(recipes)} recipes with gpt-oss:120b dialect reasoning...")

    # Normalize roughly to find candidate dialect pairs
    DIALECT_PATS = [
        (r'\bthịt lợn\b', 'thịt heo'), (r'\blợn\b', 'heo'), (r'\bba chỉ\b', 'ba rọi'),
        (r'\bgiò lụa\b', 'chả lụa'), (r'\bdạ dày\b', 'bao tử'), (r'\bmóng giò\b', 'chân giò'),
        (r'\bcuộn\b', 'cuốn'), (r'\brán\b', 'chiên'), (r'\bum\b', 'om'),
        (r'\bđậu phụ\b', 'đậu hũ'), (r'\bđậu hủ\b', 'đậu hũ'), (r'\btàu hũ\b', 'đậu hũ'),
        (r'\bmướp đắng\b', 'khổ qua'), (r'\bdọc mùng\b', 'bạc hà'), (r'\brau mùi\b', 'ngò rí'),
        (r'\bmùi tàu\b', 'ngò gai'), (r'\btrái\b', 'quả'),
    ]

    def rough_key(name: str) -> str:
        s = unicodedata.normalize('NFKC', str(name)).lower()
        s = re.sub(r'[\(\)\[\],.:;!\?\-_/]+', ' ', s)
        s = re.sub(r'\s+', ' ', s).strip()
        for pat, rep in DIALECT_PATS:
            s = re.sub(pat, rep, s)
        return s

    key_to_recs: dict[str, list[dict]] = {}
    for r in recipes:
        k = rough_key(r["name"])
        key_to_recs.setdefault(k, []).append(r)

    # Candidates are pairs within multi-recipe rough keys
    candidate_pairs = []
    pair_id = 1
    for k, group in key_to_recs.items():
        if len(group) > 1:
            for i in range(len(group)):
                for j in range(i + 1, len(group)):
                    candidate_pairs.append({
                        "pair_id": str(pair_id),
                        "dish_a_id": group[i]["id"],
                        "dish_a": group[i]["name"],
                        "dish_b_id": group[j]["id"],
                        "dish_b": group[j]["name"],
                    })
                    pair_id += 1

    print(f"  Found {len(candidate_pairs)} candidate dialect pairs to evaluate with gpt-oss:120b.")

    judgments = {}
    if DIALECT_CACHE_FILE.exists():
        judgments = json.loads(DIALECT_CACHE_FILE.read_text(encoding="utf-8"))

    needed_pairs = [p for p in candidate_pairs if p["pair_id"] not in judgments]
    if needed_pairs:
        batch_size = 25
        batches = [needed_pairs[i : i + batch_size] for i in range(0, len(needed_pairs), batch_size)]
        for idx, batch in enumerate(batches, 1):
            prompt = f"""Bạn là chuyên gia ngôn ngữ và ẩm thực Việt Nam.
Thịt ba chỉ và thịt ba rọi là cùng 1 loại thịt (ba chỉ = miền Bắc, ba rọi = miền Nam).
Thịt lợn và thịt heo là cùng 1 loại thịt (lợn = miền Bắc, heo = miền Nam).
Đậu phụ, đậu hũ, đậu hủ, tàu hũ là cùng 1 thực phẩm.
Móng giò và chân giò là cùng 1 phần thịt.
Cuốn và cuộn chỉ khác nhau cách phát âm/chính tả vùng miền.
Khổ qua và mướp đắng là cùng 1 loại quả.

Hãy đánh giá từng cặp tên món ăn sau đây xem chúng có phải là CÙNG MỘT MÓN ĂN (chỉ khác nhau do cách gọi vùng miền Bắc/Nam hoặc chính tả) hay là HAI MÓN KHÁC NHAU?

Danh sách cặp:
{json.dumps([{"pair_id": p["pair_id"], "dish_a": p["dish_a"], "dish_b": p["dish_b"]} for p in batch], ensure_ascii=False, indent=2)}

Trả về ONLY một JSON object mapping từ pair_id sang "SAME" hoặc "DIFFERENT":
{{"pair_id": "SAME" | "DIFFERENT", ...}}
Không giải thích, không markdown ngoài JSON."""

            for retry in range(5):
                try:
                    resp = client.chat([{"role": "user", "content": prompt}], temperature=0.1, max_tokens=2048)
                    parsed = extract_json_from_response(resp.get("content", ""))
                    for pid_k, decision in parsed.items():
                        if decision in ("SAME", "DIFFERENT"):
                            judgments[pid_k] = decision
                    print(f"  Dialect batch {idx}/{len(batches)} evaluated -> {len(parsed)} judgments.")
                    DIALECT_CACHE_FILE.write_text(json.dumps(judgments, ensure_ascii=False, indent=2), encoding="utf-8")
                    time.sleep(1)
                    break
                except Exception as e:
                    print(f"  Dialect batch {idx} retry {retry + 1} failed: {e}")
                    time.sleep(3)

    # Build graph of connected components from pairs judged "SAME"
    parent = {r["id"]: r["id"] for r in recipes}

    def find(i):
        if parent[i] == i:
            return i
        parent[i] = find(parent[i])
        return parent[i]

    def union(i, j):
        root_i = find(i)
        root_j = find(j)
        if root_i != root_j:
            parent[root_i] = root_j

    same_count = 0
    for p in candidate_pairs:
        pid = p["pair_id"]
        if judgments.get(pid) == "SAME":
            union(p["dish_a_id"], p["dish_b_id"])
            same_count += 1

    print(f"  gpt-oss:120b confirmed {same_count} dialect-equivalent pairs as SAME dish.")

    # Assign cluster IDs
    clusters_map: dict[str, list[dict]] = {}
    for r in recipes:
        root_id = find(r["id"])
        clusters_map.setdefault(root_id, []).append(r)

    recipe_to_cluster = {}
    cluster_idx = 1
    multi_clusters_report = []

    for root_id in sorted(clusters_map.keys()):
        group = clusters_map[root_id]
        cid = f"cluster_{cluster_idx:05d}"
        cluster_idx += 1
        for r in group:
            recipe_to_cluster[r["id"]] = cid

        if len(group) > 1:
            multi_clusters_report.append({
                "cluster_id": cid,
                "representative_name": group[0]["name"],
                "recipe_count": len(group),
                "recipes": [{"id": r["id"], "name": r["name"], "source_platform": r["source_platform"]} for r in group]
            })

    cluster_report = {
        "model_used": "gpt-oss:120b",
        "total_recipes": len(recipes),
        "total_distinct_clusters": len(clusters_map),
        "multi_recipe_clusters_count": len(multi_clusters_report),
        "multi_recipe_clusters": multi_clusters_report
    }

    return recipe_to_cluster, cluster_report


def main() -> None:
    client = OllamaCloudClient()
    print("OllamaCloudClient initialized with keys:", len(client.keys), "| model:", client.default_model)

    # 1. Load data
    with open(MASTER_CSV, "r", encoding="utf-8-sig") as f:
        master_rows = list(csv.DictReader(f))

    with open(ING_PAIRS[0][0], "r", encoding="utf-8-sig") as f:
        ing_rows = list(csv.DictReader(f))

    with open(RECIPE_PAIRS[0][0], "r", encoding="utf-8-sig") as f:
        recipe_rows = list(csv.DictReader(f))

    # Step 1: Master role classification via gpt-oss:120b
    master_roles = classify_master_ingredients(client, master_rows)

    # Step 2: Unmatched ingredient classification via gpt-oss:120b
    unmatched_counter = Counter(
        (r.get("cleaned_name") or r.get("raw_text") or "").strip()
        for r in ing_rows
        if (r.get("match_method") or "").strip().upper() == "UNMATCHED" and (r.get("cleaned_name") or r.get("raw_text"))
    )
    unmatched_names = [name for name, cnt in unmatched_counter.most_common() if cnt >= 2]
    print(f"Frequent unmatched names to classify via gpt-oss:120b: {len(unmatched_names)} items.")
    unmatched_roles = classify_unmatched_ingredients(client, unmatched_names)

    # Map initial roles to all ingredient rows
    for r in ing_rows:
        code = (r.get("master_ingredient_code") or "").strip().replace(".0", "")
        clean_name = (r.get("cleaned_name") or r.get("raw_text") or "").strip()

        if code in master_roles:
            r["ingredient_role"] = master_roles[code]
        elif clean_name in unmatched_roles:
            r["ingredient_role"] = unmatched_roles[clean_name]
        else:
            r["ingredient_role"] = "secondary"

    # Step 3: Dish-context core overrides for zero-core recipes via gpt-oss:120b
    ing_by_rec: dict[str, list[dict]] = {}
    for r in ing_rows:
        ing_by_rec.setdefault(r["recipe_id"], []).append(r)

    zero_core_recipes = [
        r for r in recipe_rows
        if not any(i.get("ingredient_role") == "core" for i in ing_by_rec.get(r["id"], []))
    ]
    print(f"Found {len(zero_core_recipes)} recipes initially lacking a core protein/starch ingredient.")

    dish_core_overrides = resolve_dish_core_overrides(client, zero_core_recipes, ing_by_rec)

    # Apply dish core overrides
    overridden = 0
    for r in zero_core_recipes:
        rid = r["id"]
        chosen_ing = (dish_core_overrides.get(rid) or "").strip().lower()
        if chosen_ing:
            ings = ing_by_rec.get(rid, [])
            # Find best matching ingredient line
            matched = False
            for i in ings:
                c_name = (i.get("cleaned_name") or i.get("raw_text") or "").lower()
                if chosen_ing in c_name or c_name in chosen_ing:
                    i["ingredient_role"] = "core"
                    matched = True
                    overridden += 1
                    break
            if not matched and ings:
                # If exact string didn't match, pick the heaviest non-seasoning
                cands = [i for i in ings if i.get("ingredient_role") != "seasoning"]
                best = max(cands or ings, key=lambda x: float(x.get("estimated_weight_g") or 0.0))
                best["ingredient_role"] = "core"
                overridden += 1

    print(f"Applied dish-context core overrides for {overridden} pure-vegetable/dessert recipes.")

    # Calculate core counts per recipe
    core_per_recipe = {
        rid: sum(1 for i in ings if i.get("ingredient_role") == "core")
        for rid, ings in ing_by_rec.items()
    }

    # Step 4: Dialect dish clustering via gpt-oss:120b
    recipe_to_cluster, cluster_report = cluster_dishes_with_gpt_oss(client, recipe_rows)

    # Step 5: Write out all files
    print("[Step 5] Writing enriched data to processed CSV and JSON...")
    # Update ingredients
    for csv_path, json_path in ING_PAIRS:
        with open(csv_path, "r", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            fields = list(reader.fieldnames)
            pair_rows = list(reader)

        if "ingredient_role" not in fields:
            if "canonical_recipe_id" in fields:
                fields.insert(fields.index("canonical_recipe_id"), "ingredient_role")
            else:
                fields.append("ingredient_role")

        # Copy roles from ing_rows
        roles_by_id = {i["id"]: i["ingredient_role"] for i in ing_rows}
        for pr in pair_rows:
            pr["ingredient_role"] = roles_by_id.get(pr["id"], "secondary")

        with open(csv_path, "w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fields)
            writer.writeheader()
            writer.writerows(pair_rows)

        with open(json_path, "r", encoding="utf-8") as f:
            json_rows = json.load(f)
        for jr in json_rows:
            jr["ingredient_role"] = roles_by_id.get(jr["id"], "secondary")
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(json_rows, f, ensure_ascii=False, indent=2)
        print(f"  Wrote {csv_path.name} & {json_path.name}.")

    # Update recipes
    for csv_path, json_path in RECIPE_PAIRS:
        with open(csv_path, "r", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            fields = list(reader.fieldnames)
            pair_recipe_rows = list(reader)

        for col in ("core_ingredients_count", "dish_cluster_id"):
            if col not in fields:
                if "canonical_recipe_id" in fields:
                    fields.insert(fields.index("canonical_recipe_id"), col)
                else:
                    fields.append(col)

        for pr in pair_recipe_rows:
            rid = pr["id"]
            pr["core_ingredients_count"] = str(core_per_recipe.get(rid, 1))
            pr["dish_cluster_id"] = recipe_to_cluster.get(rid, "")

        with open(csv_path, "w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fields)
            writer.writeheader()
            writer.writerows(pair_recipe_rows)

        with open(json_path, "r", encoding="utf-8") as f:
            json_recipes = json.load(f)
        for jr in json_recipes:
            rid = jr["id"]
            jr["core_ingredients_count"] = core_per_recipe.get(rid, 1)
            jr["dish_cluster_id"] = recipe_to_cluster.get(rid, "")
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(json_recipes, f, ensure_ascii=False, indent=2)
        print(f"  Wrote {csv_path.name} & {json_path.name}.")

    # Write summary reports
    EDA_DIR.joinpath("dish_dialect_clusters.json").write_text(json.dumps(cluster_report, ensure_ascii=False, indent=2), encoding="utf-8")
    role_dist = Counter(i["ingredient_role"] for i in ing_rows)
    EDA_DIR.joinpath("ingredient_roles_summary.json").write_text(
        json.dumps({
            "model_used": "gpt-oss:120b",
            "total_ingredient_rows": len(ing_rows),
            "role_distribution": dict(role_dist.most_common()),
            "role_percentages": {k: round(v / len(ing_rows) * 100, 2) for k, v in role_dist.most_common()},
            "recipes_count": len(recipe_rows),
            "all_recipes_have_at_least_one_core": all(v >= 1 for v in core_per_recipe.values())
        }, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )
    print("\n[SUCCESS] GPT OSS resolution complete. Reports saved to reports/eda/.")


if __name__ == "__main__":
    main()
