"""High-Throughput Batch Compound Ingredient Splitter.

Extracts all distinct UNMATCHED cleaned_name terms from recipe_ingredients.csv,
sends them in batches of 30 to Ollama Cloud (gpt-oss:120b) using 8-10 concurrent
worker threads across all 13 API keys, and saves a deterministic, audit-traceable
mapping to data/interim/unmatched_split_map.json.
"""

from __future__ import annotations

import argparse
import concurrent.futures
import csv
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

ING_CSV = ROOT / "data" / "processed" / "recipes" / "recipe_ingredients.csv"
OUTPUT_MAP_JSON = ROOT / "data" / "interim" / "unmatched_split_map.json"
CACHE_JSONL = ROOT / "data" / "interim" / "unmatched_split_cache.jsonl"

SYSTEM_PROMPT = """Bạn là Chuyên gia Ngôn ngữ Ẩm thực Việt Nam. Nhiệm vụ của bạn là phân tách các cụm nguyên liệu nấu ăn bị dính/ghép lỗi (compound ingredients) thành các nguyên liệu đơn lập (atomic ingredients) chuẩn xác.

QUY TẮC BẮT BUỘC:
1. Nếu là nguyên liệu ghép chứa 2 hoặc nhiều nguyên liệu khác nhau (vd: "muối đường" -> ["muối", "đường"]; "hành tím tỏi" -> ["hành tím", "tỏi"]; "tiêu dầu ăn" -> ["tiêu", "dầu ăn"]; "rau om ngò gai" -> ["rau om", "ngò gai"]): BẮT BUỘC TÁCH THÀNH MẢNG CÁC NGUYÊN LIỆU ĐƠN LẬP.
2. Nếu là nguyên liệu bị lỗi lặp từ của parser (vd: "cải cải bó xôi" -> ["cải bó xôi"]; "lá chúc lá" -> ["lá chúc"]): SỬA LẠI THÀNH 1 TÊN NGUYÊN LIỆU CHUẨN.
3. Nếu là nguyên liệu đơn chuẩn bình thường (vd: "sữa tươi" -> ["sữa tươi"]; "thịt ếch" -> ["thịt ếch"]; "rau dền" -> ["rau dền"]): GIỮ NGUYÊN TRONG MẢNG 1 PHẦN TỬ.
4. Nếu là từ ngữ chung chung không phải nguyên liệu cụ thể (vd: "gia vị nêm nếm", "vừa đủ", "tùy ý", "rau thơm các loại"): Trả về mảng rỗng [].
5. Tên nguyên liệu tách ra phải chuẩn tiếng Việt tự nhiên, không kèm số lượng, không kèm từ nối "và", "với".

ĐỊNH DẠNG ĐẦU RA:
Trả về DUY NHẤT một JSON Object dạng key-value, KHÔNG bọc markdown ```json:
{
  "tên_gốc_1": ["nguyên_liệu_1", "nguyên_liệu_2"],
  "tên_gốc_2": ["nguyên_liệu_chuẩn"]
}"""

FILE_LOCK = threading.Lock()
PRINT_LOCK = threading.Lock()


def load_cache() -> dict[str, list[str]]:
    cache = {}
    if CACHE_JSONL.exists():
        with open(CACHE_JSONL, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    obj = json.loads(line)
                    cache[obj["term"]] = obj["parts"]
                except Exception:
                    continue
    return cache


def append_cache_batch(items: dict[str, list[str]]) -> None:
    CACHE_JSONL.parent.mkdir(parents=True, exist_ok=True)
    with FILE_LOCK:
        with open(CACHE_JSONL, "a", encoding="utf-8") as f:
            for term, parts in items.items():
                f.write(json.dumps({"term": term, "parts": parts}, ensure_ascii=False) + "\n")


def compile_final_map() -> None:
    cache = load_cache()
    OUTPUT_MAP_JSON.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_MAP_JSON, "w", encoding="utf-8") as f:
        json.dump(cache, f, ensure_ascii=False, indent=2)
    with PRINT_LOCK:
        print(f"[Export] Compiled {len(cache):,} split terms into {OUTPUT_MAP_JSON.relative_to(ROOT)}")


def clean_json_response(content: str) -> dict[str, list[str]]:
    content = content.strip()
    if content.startswith("```"):
        content = re.sub(r"^```(?:json)?\n?", "", content)
        content = re.sub(r"\n?```$", "", content)
    content = content.strip()
    m = re.search(r"\{.*\}", content, re.DOTALL)
    if m:
        content = m.group(0)

    data = json.loads(content)
    if not isinstance(data, dict):
        raise ValueError("Expected JSON dict")

    clean_dict = {}
    for k, v in data.items():
        if isinstance(v, list):
            clean_dict[str(k).strip()] = [str(x).strip() for x in v if str(x).strip()]
        elif isinstance(v, str) and v.strip():
            clean_dict[str(k).strip()] = [v.strip()]
    return clean_dict


def process_batch(
    batch: list[str],
    batch_idx: int,
    total_batches: int,
    client: OllamaCloudClient,
    stats: dict[str, Any]
) -> bool:
    user_prompt = f"Hãy phân tách danh sách các cụm nguyên liệu sau thành các nguyên liệu đơn lập:\n{json.dumps(batch, ensure_ascii=False, indent=2)}"
    t0 = time.time()

    for attempt in range(3):
        try:
            res = client.chat([
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt}
            ], temperature=0.1, max_tokens=4096)

            parsed = clean_json_response(res["content"])
            # Ensure all terms in batch are present
            for term in batch:
                if term not in parsed:
                    # fallback: term itself if not split
                    parsed[term] = [term]

            append_cache_batch(parsed)

            with stats["lock"]:
                stats["completed"] += len(batch)
                stats["batches_done"] += 1
                curr = stats["batches_done"]
                elapsed = time.time() - stats["start_time"]
                speed = curr / max(elapsed, 1e-3)
                eta_m = int(((total_batches - curr) / max(speed, 1e-3)) // 60)

            with PRINT_LOCK:
                print(f"[{curr:>3}/{total_batches}] [ETA {eta_m:>2}m] Batch of {len(batch)} terms parsed OK ({time.time() - t0:.1f}s)")

            return True
        except Exception as e:
            if attempt == 2:
                with stats["lock"]:
                    stats["failed"] += len(batch)
                with PRINT_LOCK:
                    print(f"[ERR] Batch {batch_idx} failed: {e}")
                time.sleep(2.0)
            else:
                client.rotate_key()
                time.sleep(1.0)

    return False


def main() -> None:
    parser = argparse.ArgumentParser(description="Batch Compound Ingredient Splitter")
    parser.add_argument("--batch-size", type=int, default=30, help="Terms per LLM call (default: 30)")
    parser.add_argument("--workers", type=int, default=8, help="Concurrent threads (default: 8)")
    parser.add_argument("--limit", type=int, default=0, help="Limit number of terms to process (0 for all)")
    parser.add_argument("--compile-only", action="store_true", help="Only compile cache to final JSON")
    args = parser.parse_args()

    if args.compile_only:
        compile_final_map()
        return

    print("Loading UNMATCHED ingredients from recipe_ingredients.csv...")
    with open(ING_CSV, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        unmatched_rows = [
            r for r in reader
            if not (r.get("master_ingredient_code") or "").strip()
            or (r.get("match_method") or "").strip().upper() == "UNMATCHED"
        ]

    cache = load_cache()
    print(f"Total UNMATCHED rows in dataset: {len(unmatched_rows):,}")
    print(f"Existing cache has {len(cache):,} split terms.")

    from collections import Counter
    freq = Counter((r.get("cleaned_name") or "").strip().lower() for r in unmatched_rows)
    # Remove empty or already cached
    terms_to_do = [t for t, cnt in freq.most_common() if t and t not in cache]

    if args.limit > 0:
        terms_to_do = terms_to_do[:args.limit]

    total_terms = len(terms_to_do)
    print(f"Targeting {total_terms:,} terms across {args.workers} workers...")
    if not terms_to_do:
        print("Nothing to process.")
        compile_final_map()
        return

    # Chunk into batches
    batches = [terms_to_do[i:i + args.batch_size] for i in range(0, total_terms, args.batch_size)]
    total_batches = len(batches)
    print(f"Created {total_batches:,} batches of up to {args.batch_size} terms each.")

    keys = load_keys()
    print(f"Loaded {len(keys)} Ollama Cloud keys.")

    clients = [OllamaCloudClient() for _ in range(args.workers)]
    for idx, c in enumerate(clients):
        c._key_index = idx % len(keys)

    stats = {
        "completed": 0,
        "failed": 0,
        "batches_done": 0,
        "start_time": time.time(),
        "lock": threading.Lock(),
    }

    print("=" * 80)
    print(f"STARTING COMPOUND SPLITTING ON {total_terms:,} TERMS ({total_batches} BATCHES)")
    print("=" * 80)

    def worker_fn(tuple_args):
        b_idx, batch_items = tuple_args
        t_id = threading.get_ident() % len(clients)
        client = clients[t_id]
        return process_batch(batch_items, b_idx, total_batches, client, stats)

    tasks = list(enumerate(batches, start=1))

    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as executor:
        futures = [executor.submit(worker_fn, t) for t in tasks]
        concurrent.futures.wait(futures)

    print("\n" + "=" * 80)
    print(f"RUN FINISHED: {stats['completed']:,} terms processed in {time.time() - stats['start_time']:.1f}s.")
    print("=" * 80)
    compile_final_map()


if __name__ == "__main__":
    main()
