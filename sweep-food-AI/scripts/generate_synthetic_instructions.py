"""Generate copyright-clean, synthetic step-by-step cooking instructions for
canonical recipes using Ollama Cloud (gpt-oss:120b).

Workflow:
1. Reads canonical recipes and their structured ingredients (pure facts: name,
   cooking_method, dish_type, estimated_cooking_minutes, default_servings, and
   cleaned ingredient names + quantities).
2. Sends a structured factual prompt to gpt-oss:120b on Ollama Cloud.
3. Validates the generated JSON schema (step numbers, titles, contents).
4. Saves incrementally to an append-only JSONL cache (resumable after interruption).
5. Exports the compiled results to
   data/processed/recipes/canonical_recipe_instructions_synthetic.json.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import time
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from nlp.ollama_cloud_client import OllamaCloudClient

CANONICAL_RECIPES_JSON = ROOT / "data" / "processed" / "recipes" / "canonical_recipes.json"
CANONICAL_INGS_JSON = ROOT / "data" / "processed" / "recipes" / "canonical_recipe_ingredients.json"
CACHE_JSONL = ROOT / "data" / "interim" / "synthetic_instructions_cache.jsonl"
FINAL_OUTPUT_JSON = ROOT / "data" / "processed" / "recipes" / "canonical_recipe_instructions_synthetic.json"

SYSTEM_PROMPT = """Bạn là chuyên gia ẩm thực Việt Nam. Nhiệm vụ của bạn là viết các bước nấu ăn (instructions) cho một món ăn Việt Nam dựa HOÀN TOÀN vào các dữ liệu facts đã cung cấp.

YÊU CẦU BẮT BUỘC:
1. KHÔNG được thêm nguyên liệu lạ không có trong danh sách đã cho.
2. Các bước phải rõ ràng, ngắn gọn, tuần tự chuẩn ẩm thực Việt Nam (gồm 3-5 bước: Sơ chế -> Ướp/Phi thơm -> Nấu/Kho/Xào/Hấp -> Hoàn thành).
3. Đảm bảo thời gian nấu và thao tác phù hợp với thông tin đã cho.
4. Trả về định dạng JSON thuần túy (không kèm giải thích ngoài), cấu trúc là một mảng JSON:
[
  {
    "step": 1,
    "title": "Tên bước ngắn gọn",
    "content": "Nội dung chi tiết từng thao tác..."
  }
]"""


def build_user_prompt(recipe: dict[str, Any], ingredients: list[dict[str, Any]]) -> str:
    name = recipe.get("name") or recipe.get("canonical_dish_name", "")
    method = recipe.get("cooking_method", "Nấu")
    dish_type = recipe.get("dish_type", "Món chính")
    time_min = recipe.get("estimated_cooking_minutes", 30)
    servings = recipe.get("default_servings", 4)

    ing_lines = []
    for i in ingredients:
        n = i.get("cleaned_name") or i.get("raw_text", "")
        q = i.get("required_quantity") or ""
        u = i.get("unit_vi") or ""
        qty_str = f"{q} {u}".strip()
        if qty_str:
            ing_lines.append(f"  + {n}: {qty_str}")
        else:
            ing_lines.append(f"  + {n}")

    ings_text = "\n".join(ing_lines) if ing_lines else "  + Các gia vị thông dụng"

    return f"""Hãy viết các bước nấu cho món ăn sau:
- Tên món: {name}
- Phương pháp nấu: {method}
- Phân loại: {dish_type}
- Thời gian nấu dự kiến: {time_min} phút
- Khẩu phần: {servings} người
- Danh sách nguyên liệu:
{ings_text}"""


def clean_json_response(content: str) -> list[dict[str, Any]]:
    content = content.strip()
    if content.startswith("```"):
        content = re.sub(r"^```(?:json)?\n?", "", content)
        content = re.sub(r"\n?```$", "", content)
    content = content.strip()

    # Find JSON array if embedded
    m = re.search(r"\[\s*\{.*\}\s*\]", content, re.DOTALL)
    if m:
        content = m.group(0)

    data = json.loads(content)
    if not isinstance(data, list):
        raise ValueError(f"Expected JSON list, got {type(data).__name__}")

    cleaned_steps = []
    for idx, item in enumerate(data, start=1):
        if not isinstance(item, dict):
            continue
        cleaned_steps.append({
            "step": int(item.get("step") or idx),
            "title": str(item.get("title") or f"Bước {idx}").strip(),
            "content": str(item.get("content") or "").strip(),
        })

    if not (1 <= len(cleaned_steps) <= 10):
        raise ValueError(f"Unreasonable step count: {len(cleaned_steps)}")

    return cleaned_steps


def load_cache() -> dict[str, list[dict[str, Any]]]:
    cache = {}
    if CACHE_JSONL.exists():
        with open(CACHE_JSONL, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    obj = json.loads(line)
                    if "recipe_id" in obj and "instructions" in obj:
                        cache[obj["recipe_id"]] = obj["instructions"]
                except Exception:
                    continue
    return cache


def append_cache(recipe_id: str, recipe_name: str, instructions: list[dict[str, Any]]) -> None:
    CACHE_JSONL.parent.mkdir(parents=True, exist_ok=True)
    with open(CACHE_JSONL, "a", encoding="utf-8") as f:
        f.write(json.dumps({
            "recipe_id": recipe_id,
            "recipe_name": recipe_name,
            "instructions": instructions,
            "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "model": "gpt-oss:120b",
        }, ensure_ascii=False) + "\n")


def compile_final_output() -> None:
    cache = load_cache()
    FINAL_OUTPUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    with open(FINAL_OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(cache, f, ensure_ascii=False, indent=2)
    print(f"Compiled {len(cache):,} recipes into {FINAL_OUTPUT_JSON.relative_to(ROOT)}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate synthetic instructions via Ollama Cloud gpt-oss:120b")
    parser.add_argument("--limit", type=int, default=10, help="Max recipes to process in this run (0 for all)")
    parser.add_argument("--compile-only", action="store_true", help="Only compile cache into final JSON output")
    args = parser.parse_args()

    if args.compile_only:
        compile_final_output()
        return

    print("Loading canonical recipes and ingredients...")
    with open(CANONICAL_RECIPES_JSON, "r", encoding="utf-8") as f:
        recipes = json.load(f)
    with open(CANONICAL_INGS_JSON, "r", encoding="utf-8") as f:
        all_ings = json.load(f)

    ings_by_recipe = {}
    for ing in all_ings:
        rid = ing["recipe_id"]
        ings_by_recipe.setdefault(rid, []).append(ing)

    cache = load_cache()
    print(f"Loaded {len(recipes):,} canonical recipes.")
    print(f"Existing cache has {len(cache):,} generated instructions.")

    todo_recipes = [r for r in recipes if r["id"] not in cache]
    if args.limit > 0:
        todo_recipes = todo_recipes[:args.limit]

    print(f"Targeting {len(todo_recipes):,} recipes in this batch...")
    if not todo_recipes:
        print("Nothing to do!")
        compile_final_output()
        return

    client = OllamaCloudClient()
    success_count = 0
    fail_count = 0

    for idx, r in enumerate(todo_recipes, start=1):
        rid = r["id"]
        rname = r.get("name") or r.get("canonical_dish_name", "")
        r_ings = ings_by_recipe.get(rid, [])

        user_prompt = build_user_prompt(r, r_ings)
        t0 = time.time()
        print(f"[{idx}/{len(todo_recipes)}] Generating: {rname} ({len(r_ings)} ings)...", end=" ", flush=True)

        try:
            res = client.chat([
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt}
            ], temperature=0.2)
            steps = clean_json_response(res["content"])
            append_cache(rid, rname, steps)
            cache[rid] = steps
            success_count += 1
            print(f"OK ({len(steps)} steps, {time.time() - t0:.2f}s)")
        except Exception as e:
            fail_count += 1
            print(f"FAILED ({e})")
            time.sleep(1.0)

    print(f"\nBatch finished: {success_count} succeeded, {fail_count} failed.")
    compile_final_output()


if __name__ == "__main__":
    main()
