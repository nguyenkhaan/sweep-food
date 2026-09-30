"""Production Recipe Step Restructuring & De-compilation Engine (High-Throughput Multi-Threaded).

Uses Ollama Cloud (gpt-oss:120b) to transform raw crawl data into professional,
app-ready, sensory-enriched recipes at scale across all 13 API keys concurrently:

1. N CÁCH LÀM 1 MÓN -> CHỌN 1 CÁCH HAY NHẤT:
   Khi bài viết giới thiệu nhiều cách làm của CÙNG 1 MÓN (vd: "2 cách làm chè đậu xanh",
   "3 cách làm dừa tắc", "2 cách ướp nọng heo"), CHỌN DUY NHẤT 1 CÁCH LÀM HAY NHẤT,
   NGON NHẤT, CHUẨN VỊ NHẤT. Bỏ các cách phụ sơ sài, trả về đúng 1 recipe hoàn chỉnh.
2. NHIỀU MÓN KHÁC NHAU -> TÁCH MÓN:
   Chỉ tách bài viết thành nhiều recipe khi bài viết chứa các món ăn HOÀN TOÀN KHÁC NHAU
   (vd: "3 món từ măng cụt: gỏi gà, sinh tố, chè").
3. SENSORY & FLAVOR EXCELLENCE:
   Giữ và trau chuốt cảm quan, màu sắc, hương thơm, vị giác trong `sensory_profile` và
   trong các bước nấu.
4. CHI TIẾT & CHUẨN KỸ THUẬT:
   Bổ sung đầy đủ thao tác kỹ thuật, mẹo đầu bếp (`chef_tips`), thời gian (`duration_minutes`)
   và mức nhiệt (`heat_level`).
5. HIGH-THROUGHPUT CONCURRENCY:
   Distributes load across 8-10 worker threads concurrently using all 13 Ollama Cloud keys,
   with atomic JSONL checkpointing and periodic auto-compilation.
"""

from __future__ import annotations

import argparse
import ast
import concurrent.futures
import json
import re
import sys
import threading
import time
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from nlp.ollama_cloud_client import OllamaCloudClient, load_keys

RAW_RECIPES_PATH = ROOT / "data" / "raw" / "recipes_raw_scraped.json"
CACHE_JSONL = ROOT / "data" / "interim" / "restructured_recipes_cache.jsonl"
OUTPUT_JSON = ROOT / "data" / "processed" / "recipes" / "recipes_restructured_detailed.json"

APP_SYSTEM_PROMPT = """Bạn là Bếp trưởng Điều hành & Chuyên gia Cấu trúc Dữ liệu Ẩm thực cho ứng dụng SweepFood.

NHIỆM VỤ CỦA BẠN:
Tiếp nhận dữ liệu thu thập thô của một bài viết nấu ăn, chọn lọc và tái cấu trúc thành công thức chuẩn mực, thơm ngon, đậm đà cảm quan, tối ưu cho ứng dụng di động.

QUY TẮC QUAN TRỌNG HÀNG ĐẦU:

1. QUY TẮC "N CÁCH LÀM CÙNG 1 MÓN" -> CHỌN 1 CÁCH HAY NHẤT:
   - Nếu bài viết là "N cách làm của CÙNG 1 món ăn" (ví dụ: "2 cách làm chè đậu xanh nha đam", "3 cách làm dừa tắc", "2 cách ướp nọng heo nướng", "3 cách nấu canh sầu riêng"...):
     -> BẮT BUỘC CHỌN DUY NHẤT 1 CÁCH LÀM HAY NHẤT, NGON NHẤT, ĐẦY ĐỦ VÀ CHUẨN VỊ NHẤT!
     -> KHÔNG tách thành 2 hay 3 recipe biến thể na ná nhau (tránh rườm rà, tránh lỗi dữ liệu và loãng app).
     -> Nhặt đúng các nguyên liệu của cách làm được chọn (bỏ nguyên liệu thừa của các cách kia).
     -> Đặt tên món chuẩn xác, xóa bỏ chữ "2 cách", "3 cách", "Cách 1", "Cách 2" (vd: "Chè đậu xanh nha đam nước cốt dừa").
     -> Trả về mảng JSON chứa ĐÚNG 1 RECIPE duy nhất!

2. QUY TẮC "BÀI TỔNG HỢP CÁC MÓN KHÁC NHAU" -> TÁCH MÓN:
   - CHỈ tách thành nhiều recipe khi bài viết chứa các món ăn HOÀN TOÀN KHÁC NHAU (ví dụ: "3 món từ măng cụt: Gỏi gà măng cụt, Sinh tố măng cụt, Chè măng cụt"). Mỗi món là một loại món độc lập.

3. GIỮ VÀ NÂNG TẦM MIÊU TẢ HƯƠNG VỊ, MÀU SẮC, CẢM QUAN (SENSORY & FLAVOR EXCELLENCE):
   - Tuyệt đối KHÔNG BỎ miêu tả hương vị, màu sắc, cảm quan.
   - Trích xuất vào trường "sensory_profile" đầy đủ:
     + "appearance": Màu sắc, hình thức bắt mắt của món.
     + "taste": Vị giác chủ đạo (chua cay mặn ngọt hài hòa, đậm đà...).
     + "aroma": Mùi hương dậy mùi đặc trưng khi nấu và khi dọn ăn.
     + "texture": Cảm giác nhai (giòn sần sật, mềm mọng, sánh mịn, tan trên đầu lưỡi...).
   - Trong các bước nấu, lồng ghép dấu hiệu nhận biết chín trực quan (visual cues: "thịt xém vàng cạnh", "nước sốt keo lại sền sệt").

4. BỔ SUNG ĐẦY ĐỦ THAO TÁC & MẸO ĐẦU BẾP (CULINARY COMPLETION):
   - Tự động bổ sung các thao tác nấu nướng còn thiếu trong bài gốc (thời gian ướp, phi thơm gia vị, kỹ thuật canh lửa).
   - Thêm trường "chef_tips" chia sẻ bí quyết giúp món ăn đạt điểm 10 chất lượng.

5. CÁC BƯỚC NẤU CHI TIẾT (STEP-BY-STEP COOKING):
   - "step": Số thứ tự từ 1..N.
   - "title": Tên bước gãy gọn (bắt đầu bằng động từ: "Sơ chế nguyên liệu", "Ướp gia vị", "Nấu chè", "Trình bày"...).
   - "content": Hướng dẫn chi tiết, rõ ràng, dễ làm theo.
   - "duration_minutes": Thời gian thao tác/nấu (phút).
   - "heat_level": Mức lửa ("lửa lớn", "lửa vừa", "lửa nhỏ", "lửa liu riu", hoặc null).

ĐỊNH DẠNG ĐẦU RA:
Chỉ trả về DUY NHẤT một mảng JSON các recipe, KHÔNG bọc markdown ```json, KHÔNG kèm lời dẫn ngoài:
[
  {
    "dish_name": "Tên món ăn hoàn chỉnh",
    "dish_type": "Món chính / Khai vị / Tráng miệng / Đồ uống",
    "cooking_method": "Kho / Xào / Luộc / Hấp / Chiên / Nấu...",
    "estimated_cooking_minutes": 35,
    "default_servings": 4,
    "sensory_profile": {
      "appearance": "...",
      "taste": "...",
      "aroma": "...",
      "texture": "..."
    },
    "chef_tips": "...",
    "ingredients": [
      {"name": "tên nguyên liệu", "quantity": "định lượng số", "unit": "đơn vị"}
    ],
    "steps": [
      {
        "step": 1,
        "title": "Tên bước",
        "content": "...",
        "duration_minutes": 10,
        "heat_level": null
      }
    ]
  }
]"""

FILE_LOCK = threading.Lock()
PRINT_LOCK = threading.Lock()


def parse_raw_field(val: Any) -> Any:
    if isinstance(val, (list, dict)):
        return val
    if not isinstance(val, str):
        return []
    s = val.strip()
    try:
        return json.loads(s)
    except Exception:
        pass
    try:
        return ast.literal_eval(s)
    except Exception:
        pass
    return s


def clean_json_response(content: str) -> list[dict[str, Any]]:
    content = content.strip()
    if content.startswith("```"):
        content = re.sub(r"^```(?:json)?\n?", "", content)
        content = re.sub(r"\n?```$", "", content)
    content = content.strip()
    m = re.search(r"\[\s*\{.*\}\s*\]", content, re.DOTALL)
    if m:
        content = m.group(0)

    data = json.loads(content)
    if not isinstance(data, list):
        if isinstance(data, dict):
            data = [data]
        else:
            raise ValueError(f"Expected JSON list, got {type(data).__name__}")

    cleaned_recipes = []
    for r in data:
        if not isinstance(r, dict):
            continue
        dish_name = str(r.get("dish_name") or "").strip()
        if not dish_name:
            continue
        cleaned_recipes.append({
            "dish_name": dish_name,
            "dish_type": str(r.get("dish_type") or "Món chính").strip(),
            "cooking_method": str(r.get("cooking_method") or "Nấu").strip(),
            "estimated_cooking_minutes": int(r.get("estimated_cooking_minutes") or 30),
            "default_servings": float(r.get("default_servings") or 4),
            "sensory_profile": r.get("sensory_profile", {}),
            "chef_tips": str(r.get("chef_tips") or "").strip(),
            "ingredients": r.get("ingredients", []),
            "steps": r.get("steps", []),
        })

    if not cleaned_recipes:
        raise ValueError("No valid recipes found in parsed output.")
    return cleaned_recipes


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
                    if "source_url" in obj and "recipes" in obj:
                        cache[obj["source_url"]] = obj["recipes"]
                except Exception:
                    continue
    return cache


def append_cache(source_url: str, raw_title: str, platform: str, recipes: list[dict[str, Any]]) -> None:
    CACHE_JSONL.parent.mkdir(parents=True, exist_ok=True)
    with FILE_LOCK:
        with open(CACHE_JSONL, "a", encoding="utf-8") as f:
            f.write(json.dumps({
                "source_url": source_url,
                "raw_title": raw_title,
                "platform": platform,
                "recipes_count": len(recipes),
                "recipes": recipes,
                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            }, ensure_ascii=False) + "\n")


def compile_final_output() -> None:
    with FILE_LOCK:
        cache = load_cache()
        OUTPUT_JSON.parent.mkdir(parents=True, exist_ok=True)
        all_flattened = []
        for src_url, rec_list in cache.items():
            for r in rec_list:
                item = dict(r)
                item["source_url"] = src_url
                all_flattened.append(item)

        with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
            json.dump(all_flattened, f, ensure_ascii=False, indent=2)
    with PRINT_LOCK:
        print(f"[Export] Compiled {len(all_flattened):,} standalone recipes (from {len(cache):,} source URLs) into {OUTPUT_JSON.relative_to(ROOT)}")


def process_single_recipe(
    item: tuple[int, int, dict[str, Any]],
    client: OllamaCloudClient,
    stats: dict[str, Any],
) -> bool:
    idx, total, r = item
    url = r.get("source_url") or r.get("title")
    title = r.get("title", "")
    plat = r.get("source_platform", "")
    raw_ings = parse_raw_field(r.get("raw_ingredients"))
    raw_inst = parse_raw_field(r.get("instructions"))

    user_prompt = f"""Hãy phân tích bài viết sau:
- Tiêu đề gốc: {title}
- Nguồn thu thập: {plat}
- Nguyên liệu gốc thu thập:
{json.dumps(raw_ings, ensure_ascii=False) if isinstance(raw_ings, (list, dict)) else raw_ings}
- Các bước gốc thu thập:
{json.dumps(raw_inst, ensure_ascii=False) if isinstance(raw_inst, (list, dict)) else raw_inst}

ÁP DỤNG ĐÚNG QUY TẮC:
- Nếu là nhiều cách làm của CÙNG 1 món ăn: CHỌN ĐÚNG 1 CÁCH HAY NHẤT, NGON NHẤT (trả về mảng 1 recipe duy nhất).
- Chỉ tách nhiều recipe khi là các món ăn HOÀN TOÀN KHÁC NHAU.
- Đầy đủ cảm quan (appearance, taste, aroma, texture), mẹo đầu bếp, thời gian và mức nhiệt."""

    t0 = time.time()
    for attempt in range(3):
        try:
            res = client.chat([
                {"role": "system", "content": APP_SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt}
            ], temperature=0.2, max_tokens=8192)

            recipes = clean_json_response(res["content"])
            append_cache(url, title, plat, recipes)

            with stats["lock"]:
                stats["completed"] += 1
                curr = stats["completed"]
                dish_names = [d["dish_name"] for d in recipes]
                elapsed = time.time() - stats["start_time"]
                speed = curr / max(elapsed, 1e-3)
                eta_s = (total - curr) / max(speed, 1e-3)
                eta_m = int(eta_s // 60)
                pct = curr / total * 100

            with PRINT_LOCK:
                print(f"[{curr:>4}/{total}] ({pct:5.1f}%) [ETA {eta_m:>3}m] {title[:32]:32} -> {len(recipes)} dish: {dish_names} ({time.time() - t0:.1f}s)")

            # Periodic compilation every 50 recipes
            if curr % 50 == 0:
                compile_final_output()

            return True
        except Exception as e:
            if attempt == 2:
                with stats["lock"]:
                    stats["failed"] += 1
                with PRINT_LOCK:
                    print(f"[ERR] Failed {title[:35]}: {e}")
                time.sleep(2.0)
            else:
                client.rotate_key()
                time.sleep(1.0)

    return False


def main() -> None:
    parser = argparse.ArgumentParser(description="High-Throughput Recipe Restructuring Engine")
    parser.add_argument("--limit", type=int, default=0, help="Number of raw recipes to process (0 for all)")
    parser.add_argument("--workers", type=int, default=8, help="Concurrent worker threads (default: 8)")
    parser.add_argument("--compilations-only", action="store_true", help="Only process multi-dish compilation articles")
    parser.add_argument("--compile-only", action="store_true", help="Compile cache into final JSON without calling API")
    args = parser.parse_args()

    if args.compile_only:
        compile_final_output()
        return

    print("Loading raw recipes...")
    with open(RAW_RECIPES_PATH, "r", encoding="utf-8") as f:
        raw_recipes = json.load(f)

    cache = load_cache()
    print(f"Loaded {len(raw_recipes):,} raw recipes. Cache contains {len(cache):,} processed articles.")

    todo = []
    compilation_re = re.compile(r"^\s*(\d+|top\s*\d+|gợi\s*ý\s*\d+|tổng\s*hợp\s*\d*)\s*(cách|món)|\b(2|3|4|5)\s*(cách|món)", re.IGNORECASE)

    for r in raw_recipes:
        url = r.get("source_url") or r.get("title")
        if not url or url in cache:
            continue
        title = r.get("title", "")
        if args.compilations_only and not compilation_re.search(title):
            continue
        todo.append(r)

    if args.limit > 0:
        todo = todo[:args.limit]

    total_todo = len(todo)
    print(f"\nTargeting {total_todo:,} recipes across {args.workers} concurrent workers...")
    if not todo:
        print("Nothing to process.")
        compile_final_output()
        return

    keys = load_keys()
    print(f"Loaded {len(keys)} Ollama Cloud keys for concurrency.")

    # Create thread-local clients each initialized with a specific key offset
    clients = [OllamaCloudClient() for _ in range(args.workers)]
    for idx, c in enumerate(clients):
        c._key_index = idx % len(keys)

    stats = {
        "completed": 0,
        "failed": 0,
        "start_time": time.time(),
        "lock": threading.Lock(),
    }

    # Queue items with assigned client by worker index
    tasks = [(idx, total_todo, r) for idx, r in enumerate(todo, start=1)]

    def worker_wrapper(task_tuple):
        # Assign client based on thread ID or task index
        t_id = threading.get_ident() % len(clients)
        client = clients[t_id]
        return process_single_recipe(task_tuple, client, stats)

    print("=" * 80)
    print(f"STARTING MULTI-THREADED SCAN OF {total_todo:,} RECIPES (workers={args.workers})")
    print("=" * 80)

    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as executor:
        futures = [executor.submit(worker_wrapper, t) for t in tasks]
        concurrent.futures.wait(futures)

    print("\n" + "=" * 80)
    print(f"RUN FINISHED: {stats['completed']:,} completed, {stats['failed']} failed in {time.time() - stats['start_time']:.1f}s.")
    print("=" * 80)
    compile_final_output()


if __name__ == "__main__":
    main()
