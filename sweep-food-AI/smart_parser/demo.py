"""Demo chạy thử nghiệm Module smart_parser cho SweepFood AI.

Cách dùng:
    python smart_parser/demo.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

# Đảm bảo root repo nằm trong sys.path
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from smart_parser.pantry_parser import get_pantry_parser


def main():
    print("=" * 70)
    print("SWEEPFOOD AI — DEMO SMART_PARSER (4-TIER CULINARY RESOLUTION)")
    print("=" * 70)

    parser = get_pantry_parser()
    print(f"-> Nạp từ điển: {len(parser.alias_to_master):,} từ đồng nghĩa & tên nguyên liệu.")
    print(f"-> Nạp FreshCheck KB: {len(parser.fresh_kb.get('ingredients', {})):,} nguyên liệu chuẩn hóa.")

    # -------------------------------------------------------------------------
    # TEST CASE 1: HÓA ĐƠN SIÊU THỊ OCR (Bách Hóa Xanh / WinMart)
    # -------------------------------------------------------------------------
    print("\n" + "-" * 70)
    print("TEST CASE 1: HÓA ĐƠN SIÊU THỊ OCR")
    print("-" * 70)
    ocr_sample = """
    1. THIT HEO XAY CP KHAY 300G     45.000d
    2. CA DIEU HONG LS 0.70 kg       59.500d
    3. BO RAU MUONG NUOC 500G        15.000d
    4. TUI 10 QUA TRUNG GA TA        32.000d
    """
    print("Văn bản OCR đầu vào:")
    print(ocr_sample.strip())

    items_ocr = parser.parse_input_to_pantry(ocr_sample, prefer_llm=True)
    print(f"\n=> Kết quả trích xuất & làm giàu ({len(items_ocr)} món):")
    for idx, item in enumerate(items_ocr, 1):
        print(f"  #{idx} {item['name']} [Mã FCT: {item['code']}]")
        print(f"     • Khối lượng: {item['quantity_g']}g | Hạn dùng ({item['storage_mode']}): {item['hours_to_expire']} giờ")
        if item.get("freshness_guide"):
            fg = item["freshness_guide"]
            print(f"     • Nhóm hình mẫu: {fg.get('archetype_name')}")
            if fg.get("storage_tips"):
                print(f"     • Mẹo bảo quản: {'; '.join(fg['storage_tips'])}")
        if item.get("nutrition_per_100g"):
            nu = item["nutrition_per_100g"]
            print(f"     • Dinh dưỡng/100g: {nu['energy_kcal']} kcal | Đạm: {nu['protein_g']}g | Béo: {nu['fat_g']}g")

    # -------------------------------------------------------------------------
    # TEST CASE 2: GIỌNG NÓI ĐI CHỢ ASR (Conversational Speech)
    # -------------------------------------------------------------------------
    print("\n" + "-" * 70)
    print("TEST CASE 2: GIỌNG NÓI ĐI CHỢ ASR (Tiếng Việt tự nhiên)")
    print("-" * 70)
    voice_sample = "sáng nay tôi đi chợ mua nửa cân thịt ba rọi với hai lạng tôm biển với ba quả cà chua để ngăn mát"
    print(f"Câu thoại giọng nói: \"{voice_sample}\"")

    items_voice = parser.parse_input_to_pantry(voice_sample, prefer_llm=True)
    print(f"\n=> Kết quả trích xuất & làm giàu ({len(items_voice)} món):")
    for idx, item in enumerate(items_voice, 1):
        print(f"  #{idx} {item['name']} [Mã FCT: {item['code']}]")
        print(f"     • Khối lượng: {item['quantity_g']}g | Hạn dùng ({item['storage_mode']}): {item['hours_to_expire']} giờ")

    # -------------------------------------------------------------------------
    # TEST CASE 3: TỪ ĐỒNG NGHĨA VÙNG MIỀN (Regional Aliases)
    # -------------------------------------------------------------------------
    print("\n" + "-" * 70)
    print("TEST CASE 3: ĐỐI SOÁT TỪ ĐỒNG NGHĨA VÙNG MIỀN (Instant 0ms)")
    print("-" * 70)
    test_aliases = ["ba rọi rút sườn 400g", "cá lóc 1 con", "tàu hũ non 2 bìa", "ngao sống 1 kg"]
    for raw in test_aliases:
        res = parser.parse_input_to_pantry(raw, prefer_llm=False)
        if res:
            it = res[0]
            print(f"  • Input: \"{raw:<25}\" -> Khớp: [{it['code']}] {it['name']} ({it['quantity_g']}g, {it['hours_to_expire']}h)")

    print("\n" + "=" * 70)
    print("HOÀN THÀNH KIỂM THỬ MODULE SMART_PARSER!")
    print("=" * 70)


if __name__ == "__main__":
    main()
