"""Turn 2: LLM Quality Audit & Verification of Compound Ingredient Splits.

Reviews all multi-part splits and potential under-splits generated in Turn 1 using
gpt-oss:120b on Ollama Cloud:
1. Catches over-splitting: recombines any single compound noun that was mistakenly
   split into parts (e.g. "nước dừa" mistakenly split into "nước" + "dừa").
2. Validates legitimate splits: confirms genuine multi-ingredient compounds
   ("muối đường" -> ["muối", "đường"], "hành tím tỏi" -> ["hành tím", "tỏi"]).
3. Produces the final verified mapping: data/interim/unmatched_split_map_audited.json
   and an audit diff report: reports/eda/unmatched_split_audit_diff.json.
"""

from __future__ import annotations

import argparse
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

INPUT_MAP_JSON = ROOT / "data" / "interim" / "unmatched_split_map.json"
AUDITED_MAP_JSON = ROOT / "data" / "interim" / "unmatched_split_map_audited.json"
DIFF_REPORT_JSON = ROOT / "reports" / "eda" / "unmatched_split_audit_diff.json"

AUDIT_SYSTEM_PROMPT = """Bạn là Chuyên gia Kiểm định & Giám sát Dữ liệu Ẩm thực (Culinary Data Quality Auditor).

NHIỆM VỤ CỦA BẠN:
Kiểm tra và soát lỗi (Audit) danh sách các nguyên liệu đã được phân tách từ Turn 1.

QUY TẮC THẨM ĐỊNH BẮT BUỘC:
1. PHÁT HIỆN & SỬA LỖI TÁCH SAI (OVER-SPLITTING):
   - Nếu một cụm là MỘT NGUYÊN LIỆU ĐƠN nhưng bị tách nhầm thành 2 từ (ví dụ: "nước dừa" bị tách thành ["nước", "dừa"]; "cá lóc" bị tách thành ["cá", "lóc"]; "đậu bắp" bị tách thành ["đậu", "bắp"]): BẮT BUỘC SỬA LẠI THÀNH MỘT NGUYÊN LIỆU ĐƠN ["nước dừa"], ["cá lóc"], ["đậu bắp"].
2. XÁC NHẬN TÁCH ĐÚNG (VALID MULTI-INGREDIENT):
   - Nếu thực sự là 2 hoặc nhiều nguyên liệu độc lập ghép lại (ví dụ: "muối đường" -> ["muối", "đường"]; "hành tím tỏi" -> ["hành tím", "tỏi"]; "tiêu dầu ăn" -> ["tiêu", "dầu ăn"]): XÁC NHẬN GIỮ NGUYÊN.
3. PHÁT HIỆN BỎ SÓT (UNDER-SPLITTING):
   - Nếu từ gốc chứa 2 nguyên liệu rõ ràng mà Turn 1 chưa tách: BẮT BUỘC TÁCH.
4. LOẠI BỎ TỪ RÁC:
   - Các từ không phải đồ ăn ("vừa đủ", "gia vị nêm") nếu còn sót -> loại bỏ ra mảng rỗng [].

ĐỊNH DẠNG ĐẦU RA:
Trả về DUY NHẤT một JSON Object dạng key-value (tên_gốc -> danh_sách_đã_thẩm_định), KHÔNG bọc markdown ```json:
{
  "tên_gốc_1": ["nguyên_liệu_chuẩn_1", "nguyên_liệu_chuẩn_2"],
  "tên_gốc_2": ["nguyên_liệu_đơn_đã_gộp"]
}"""

FILE_LOCK = threading.Lock()
PRINT_LOCK = threading.Lock()


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


def process_audit_batch(
    batch_items: list[tuple[str, list[str]]],
    batch_idx: int,
    total_batches: int,
    client: OllamaCloudClient,
    audited_results: dict[str, list[str]],
    stats: dict[str, Any]
) -> bool:
    payload_input = {k: v for k, v in batch_items}
    user_prompt = f"Hãy thẩm định và soát lỗi danh sách phân tách nguyên liệu sau:\n{json.dumps(payload_input, ensure_ascii=False, indent=2)}"
    t0 = time.time()

    for attempt in range(3):
        try:
            res = client.chat([
                {"role": "system", "content": AUDIT_SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt}
            ], temperature=0.1, max_tokens=4096)

            parsed = clean_json_response(res["content"])
            with FILE_LOCK:
                for k, v in batch_items:
                    audited_results[k] = parsed.get(k, v)

            with stats["lock"]:
                stats["batches_done"] += 1
                curr = stats["batches_done"]
                elapsed = time.time() - stats["start_time"]
                speed = curr / max(elapsed, 1e-3)
                eta_s = int((total_batches - curr) / max(speed, 1e-3))

            with PRINT_LOCK:
                print(f"[Audit {curr:>2}/{total_batches}] [ETA {eta_s:>2}s] Batch of {len(batch_items)} items audited OK ({time.time() - t0:.1f}s)")

            return True
        except Exception as e:
            if attempt == 2:
                with stats["lock"]:
                    stats["failed"] += len(batch_items)
                with PRINT_LOCK:
                    print(f"[ERR] Audit batch {batch_idx} failed: {e}")
                # Fallback to original Turn 1 values
                with FILE_LOCK:
                    for k, v in batch_items:
                        audited_results[k] = v
            else:
                client.rotate_key()
                time.sleep(1.0)

    return False


def main() -> None:
    parser = argparse.ArgumentParser(description="Turn 2: LLM Quality Audit of Split Ingredients")
    parser.add_argument("--batch-size", type=int, default=25, help="Items per audit call (default: 25)")
    parser.add_argument("--workers", type=int, default=8, help="Concurrent threads (default: 8)")
    args = parser.parse_args()

    print("Loading Turn 1 split map from data/interim/unmatched_split_map.json...")
    turn1_map = json.load(open(INPUT_MAP_JSON, encoding="utf-8"))
    print(f"Loaded {len(turn1_map):,} terms from Turn 1.")

    # Target: All multi-part splits (>1) + single parts with conjunctions
    conj_re = re.compile(r"(\b(và|với|hoặc|kèm|cùng)\b|[+/&,])", re.IGNORECASE)
    items_to_audit = []
    for k, v in turn1_map.items():
        if len(v) > 1 or (len(v) == 1 and conj_re.search(k)):
            items_to_audit.append((k, v))

    print(f"Identified {len(items_to_audit):,} items requiring Turn 2 LLM quality audit.")

    batches = [items_to_audit[i:i + args.batch_size] for i in range(0, len(items_to_audit), args.batch_size)]
    total_batches = len(batches)
    print(f"Created {total_batches} audit batches across {args.workers} workers.")

    keys = load_keys()
    clients = [OllamaCloudClient() for _ in range(args.workers)]
    for idx, c in enumerate(clients):
        c._key_index = idx % len(keys)

    audited_subset: dict[str, list[str]] = {}
    stats = {
        "batches_done": 0,
        "failed": 0,
        "start_time": time.time(),
        "lock": threading.Lock(),
    }

    print("=" * 80)
    print(f"STARTING TURN 2 AUDIT ON {len(items_to_audit):,} ITEMS")
    print("=" * 80)

    def worker_fn(args_tuple):
        b_idx, b_items = args_tuple
        t_id = threading.get_ident() % len(clients)
        return process_audit_batch(b_items, b_idx, total_batches, clients[t_id], audited_subset, stats)

    tasks = list(enumerate(batches, start=1))
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as executor:
        futures = [executor.submit(worker_fn, t) for t in tasks]
        concurrent.futures.wait(futures)

    # Merge audited subset into full map
    final_audited_map = dict(turn1_map)
    diffs = []
    for k, new_v in audited_subset.items():
        old_v = turn1_map.get(k, [])
        if new_v != old_v:
            diffs.append({"term": k, "turn1": old_v, "turn2_audited": new_v})
        final_audited_map[k] = new_v

    print("\n" + "=" * 80)
    print(f"TURN 2 AUDIT COMPLETE in {time.time() - stats['start_time']:.1f}s!")
    print(f"  - Total items audited: {len(items_to_audit):,}")
    print(f"  - Adjustments / Corrections made: {len(diffs):,}")
    print("=" * 80)

    AUDITED_MAP_JSON.parent.mkdir(parents=True, exist_ok=True)
    with open(AUDITED_MAP_JSON, "w", encoding="utf-8") as f:
        json.dump(final_audited_map, f, ensure_ascii=False, indent=2)
    print(f"[Saved] Final Audited Split Map -> {AUDITED_MAP_JSON.relative_to(ROOT)}")

    DIFF_REPORT_JSON.parent.mkdir(parents=True, exist_ok=True)
    with open(DIFF_REPORT_JSON, "w", encoding="utf-8") as f:
        json.dump({
            "total_audited": len(items_to_audit),
            "corrections_count": len(diffs),
            "corrections_sample": diffs[:50],
        }, f, ensure_ascii=False, indent=2)
    print(f"[Saved] Audit Diff Report -> {DIFF_REPORT_JSON.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
