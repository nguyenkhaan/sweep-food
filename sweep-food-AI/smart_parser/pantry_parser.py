"""Culinary Entity Resolution & Pantry Ingestion Parser (Module Độc Lập).

Module này xử lý chuyển đổi dữ liệu thô từ 3 nguồn:
1. Gõ tay (User manual typing)
2. OCR Hóa đơn / Tem nhãn siêu thị (Bách Hóa Xanh, WinMart)
3. Giọng nói ẩm thực ASR (Voice speech transcripts)

Thành dữ liệu Tủ Lạnh chuẩn hóa:
- Mã nguyên liệu Viện Dinh Dưỡng (`code`)
- Tên món chuẩn (`name`)
- Khối lượng gram quy đổi (`quantity_g`)
- Hạn dùng theo nhiệt độ (`hours_to_expire` & `storage_mode`)
- Mẹo bảo quản và dấu hiệu nhận biết tươi/hỏng từ FreshCheck KB (`freshness_guide`)
- Dinh dưỡng calo/macro (`nutrition`)
- Vai trò ẩm thực (`role`) và cờ gia vị bếp (`is_staple`)
"""

from __future__ import annotations

import json
import re
import time
import unicodedata
from pathlib import Path
from typing import Any

def strip_vietnamese_accents(s: str) -> str:
    """Converts Vietnamese text to unaccented lowercase (e.g. 'cá điêu hồng' -> 'ca dieu hong')."""
    norm = unicodedata.normalize("NFD", s)
    res = "".join(c for c in norm if unicodedata.category(c) != "Mn")
    return res.replace("đ", "d").replace("Đ", "D").strip().lower()

ROOT_DIR = Path(__file__).resolve().parent.parent
MASTER_CSV = ROOT_DIR / "data" / "processed" / "viendinhduong" / "master_ingredients_nutrition.csv"
FRESH_KB_JSON = ROOT_DIR / "data_freshness" / "build" / "freshcheck_kb.json"

_PARSER_INSTANCE: PantryEntityParser | None = None


class PantryEntityParser:
    def __init__(self):
        self.alias_to_master: dict[str, dict[str, Any]] = {}
        self.unaccented_to_master: dict[str, dict[str, Any]] = {}
        self.master_by_code: dict[str, dict[str, Any]] = {}
        self.fresh_kb: dict[str, Any] = {}
        self._load_master_and_aliases()
        self._load_freshness_kb()

    def _load_master_and_aliases(self) -> None:
        """Nạp từ điển 1.598 nguyên liệu Viện Dinh Dưỡng và lập chỉ mục hơn 15.000 từ đồng nghĩa."""
        if not MASTER_CSV.exists():
            return
        import pandas as pd
        df = pd.read_csv(MASTER_CSV)
        for _, r in df.iterrows():
            c = str(r["code"]).strip()
            name = str(r["name_vi"]).strip()
            entry = {
                "code": c,
                "name": name,
                "category": str(r.get("category_vi") or "").strip(),
                "nutrition": {
                    "energy_kcal": float(r.get("energy_kcal") or 0.0),
                    "protein_g": float(r.get("protein_g") or 0.0),
                    "fat_g": float(r.get("fat_g") or 0.0),
                    "carbs_g": float(r.get("carbs_g") or 0.0),
                }
            }
            self.master_by_code[c] = entry
            self.alias_to_master[name.lower()] = entry
            self.unaccented_to_master[strip_vietnamese_accents(name)] = entry

            # Chỉ mục các từ đồng nghĩa trong cột aliases
            aliases_str = str(r.get("aliases") or "")
            if aliases_str and aliases_str != "nan":
                for a in re.split(r"[,;]+", aliases_str):
                    a_clean = a.strip().lower()
                    if len(a_clean) >= 2:
                        self.alias_to_master[a_clean] = entry
                        self.unaccented_to_master[strip_vietnamese_accents(a_clean)] = entry

    def _load_freshness_kb(self) -> None:
        """Nạp Cơ sở tri thức FreshCheck KB (hạn dùng, mẹo bảo quản theo nhiệt độ)."""
        if not FRESH_KB_JSON.exists():
            return
        try:
            self.fresh_kb = json.loads(FRESH_KB_JSON.read_text(encoding="utf-8"))
            for iid, f_item in self.fresh_kb.get("ingredients", {}).items():
                code = str(f_item.get("code") or "").strip()
                m_entry = self.master_by_code.get(code)
                for name_vi in f_item.get("names_vi", []):
                    n_clean = name_vi.strip().lower()
                    if n_clean not in self.alias_to_master and m_entry:
                        self.alias_to_master[n_clean] = m_entry
        except Exception as e:
            print(f"[smart_parser Warning] Failed loading freshcheck_kb: {e}")

    def resolve_master_ingredient(self, query: str) -> dict[str, Any] | None:
        """Tầng 1 & Tầng 2: So khớp chuỗi nguyên liệu qua 15.000+ từ đồng nghĩa."""
        if not query:
            return None
        q = query.strip().lower()

        # 1. Khớp tuyệt đối trong từ điển đồng nghĩa (0ms)
        if q in self.alias_to_master:
            return self.alias_to_master[q]

        # 2. Cắt từ loại đếm (bó, quả, trái, củ, con, miếng, lát, đĩa...)
        stripped = re.sub(r"^(bó|quả|trái|củ|con|miếng|lát|đĩa|khay|vỉ|hộp|túi)\s+", "", q).strip()
        if stripped in self.alias_to_master:
            return self.alias_to_master[stripped]

        # 3. Lọc bỏ nhiễu thương hiệu & bao bì siêu thị (CP, Vissan, Meat Deli, kg, g...)
        cleaned_sm = re.sub(
            r"\b(cp|vissan|meat\s*deli|g\s*kitchen|ba\s*huân|vinmart|winmart|bhx|ls|kg|gr?|gram)\b",
            "",
            stripped,
            flags=re.I
        ).strip()
        cleaned_sm = re.sub(r"\s+", " ", cleaned_sm).strip()
        if cleaned_sm in self.alias_to_master:
            return self.alias_to_master[cleaned_sm]

        # 4. So khớp không dấu (Unaccented match for OCR typos / all-caps)
        unacc_q = strip_vietnamese_accents(cleaned_sm)
        if unacc_q in self.unaccented_to_master:
            return self.unaccented_to_master[unacc_q]

        # 5. So khớp chuỗi con theo ranh giới từ (Longest Word-Boundary Match)
        best_match = None
        best_len = 0
        for a, entry in self.alias_to_master.items():
            if len(a) >= 3 and re.search(r'\b' + re.escape(a) + r'\b', cleaned_sm, re.IGNORECASE):
                if len(a) > best_len:
                    best_len = len(a)
                    best_match = entry

        for a_unacc, entry in self.unaccented_to_master.items():
            if len(a_unacc) >= 3 and re.search(r'\b' + re.escape(a_unacc) + r'\b', unacc_q, re.IGNORECASE):
                if len(a_unacc) > best_len:
                    best_len = len(a_unacc)
                    best_match = entry

        # Fallback substring nếu không khớp nguyên từ
        if not best_match:
            for a, entry in self.alias_to_master.items():
                if len(a) >= 4 and a in cleaned_sm:
                    if len(a) > best_len:
                        best_len = len(a)
                        best_match = entry

        return best_match

    def enrich_item(self, raw_item: dict[str, Any]) -> dict[str, Any]:
        """Tầng 4: Làm giàu thực thể với mã dinh dưỡng, hạn bảo quản và mẹo kiểm tra tươi/hỏng."""
        raw_name = str(raw_item.get("name") or "").strip()
        matched = self.resolve_master_ingredient(raw_name)

        code = raw_item.get("code") or (matched["code"] if matched else None)
        master_name = matched["name"] if matched else raw_name.capitalize()
        category = matched.get("category", "") if matched else ""

        qty_g = float(raw_item.get("quantity_g") or 200.0)
        storage_mode = raw_item.get("storage_mode") or "fridge_2_4c"

        # Tra cứu hạn dùng và mẹo bảo quản theo nhiệt độ trong FreshCheck KB
        shelf_hours = float(raw_item.get("hours_to_expire") or 48.0)
        freshness_info = None

        if self.fresh_kb:
            for f_id, f_data in self.fresh_kb.get("ingredients", {}).items():
                f_code = str(f_data.get("code") or "").strip()
                if (code and f_code == str(code).strip()) or any(raw_name.lower() in n.lower() for n in f_data.get("names_vi", [])):
                    shelf_spec = f_data.get("base_shelf_life_hours", {}).get(storage_mode)
                    if shelf_spec:
                        shelf_hours = float(shelf_spec.get("value", 48.0))
                    arch_id = f_data.get("archetype")
                    arch = self.fresh_kb.get("archetypes", {}).get(arch_id, {})
                    freshness_info = {
                        "archetype": arch_id,
                        "archetype_name": arch.get("name_vi") or arch_id,
                        "storage_tips": arch.get("preservation_protocols", {}).get("prep", [])[:2],
                        "bad_practices": arch.get("preservation_protocols", {}).get("bad", [])[:1],
                    }
                    break

        is_staple = raw_item.get("is_staple")
        if is_staple is None:
            is_staple = category in ["Gia vị, nước chấm", "Dầu, mỡ, bơ"]

        return {
            "name": master_name,
            "raw_text": raw_name,
            "code": code,
            "quantity_g": round(qty_g, 1),
            "hours_to_expire": round(shelf_hours, 1),
            "storage_mode": storage_mode,
            "is_staple": bool(is_staple),
            "nutrition_per_100g": matched.get("nutrition") if matched else None,
            "freshness_guide": freshness_info,
        }

    def parse_with_llm(self, input_text: str) -> list[dict[str, Any]]:
        """Tầng 3: Gọi LLM gpt-oss:120b-cloud trên Ollama Cloud để trích xuất ngữ cảnh sâu."""
        from nlp.ollama_cloud_client import OllamaCloudClient

        prompt = f"""Bạn là Chuyên gia Trích xuất Nguyên liệu Ẩm thực cho SweepFood AI.
Nhiệm vụ: Phân tích đoạn văn bản đầu vào (từ hóa đơn siêu thị OCR, giọng nói đi chợ, hoặc người dùng gõ) thành danh sách các nguyên liệu thực phẩm để lưu vào Tủ Lạnh.

VĂN BẢN ĐẦU VÀO:
\"\"\"{input_text.strip()}\"\"\"

QUY TẮC BẮT BUỘC:
1. Trích xuất từng món nguyên liệu riêng biệt. Bỏ qua giá tiền, thuế, mã vạch, túi nilon.
2. Tách sạch thương hiệu siêu thị (CP, Vissan, Meat Deli...) và quy cách đóng gói (khay, vỉ, hộp).
3. Quy đổi định lượng về đơn vị Gram (quantity_g) là số thực:
   - 1 kg = 1000g, 1 lạng = 100g, nửa cân = 500g
   - Nếu là số lượng quả/bó: ước lượng gram (1 quả cà chua ~ 75g, 1 bó rau ~ 300g, 1 quả trứng ~ 60g).
4. Phán đoán storage_mode: 'fridge_2_4c' (ngăn mát), 'freezer_-18c' (ngăn đá), hoặc 'room_temp_25_30c' (nhiệt độ phòng cho hành, tỏi, củ).

Trả về DUY NHẤT một mảng JSON các object (không markdown, không lời dẫn ngoài):
[
  {{
    "name": "tên nguyên liệu sạch tiếng Việt",
    "quantity_g": 300.0,
    "storage_mode": "fridge_2_4c"
  }}
]"""

        try:
            client = OllamaCloudClient()
            res = client.chat([{"role": "user", "content": prompt}], max_tokens=1024, temperature=0.1)
            raw = res.get("content") or res.get("reasoning") or ""
            raw = raw.strip()
            if raw.startswith("```"):
                raw = raw.split("\n", 1)[1].rsplit("```", 1)[0].strip()
            start = raw.find("[")
            end = raw.rfind("]")
            if start != -1 and end != -1:
                items = json.loads(raw[start : end + 1])
                if isinstance(items, list):
                    return items
        except Exception as e:
            print(f"[smart_parser Warning] LLM parsing failed or rate-limited: {e}")

        return []

    def parse_input_to_pantry(self, input_text: str, prefer_llm: bool = True) -> list[dict[str, Any]]:
        """Chiến thuật 4 Tầng Tổng thể: Nhận text thô -> Trả về danh sách Pantry Item chuẩn hóa."""
        if not input_text or not input_text.strip():
            return []

        text = input_text.strip()
        parsed_raw_items = []

        # Nhận diện nếu văn bản có cấu trúc phức tạp (nhiều dòng, câu hội thoại giọng nói) -> kích hoạt Tầng 3 LLM
        is_complex = len(text.splitlines()) > 1 or len(text.split()) > 4 or any(
            k in text.lower() for k in ["hôm nay", "đi chợ", "mua", "tủ lạnh", "ngăn mát", "khay", "kg", "đ", "lạng", "cân"]
        )

        if prefer_llm and is_complex:
            parsed_raw_items = self.parse_with_llm(text)

        # Fallback về parser cục bộ nếu LLM bị timeout / rate limit
        if not parsed_raw_items:
            try:
                from smart_input.ocr.receipt_parser import parse_receipt_text
                parsed_raw_items = parse_receipt_text(text)
            except Exception:
                pass

        if not parsed_raw_items:
            try:
                from smart_input.asr.speech_parser import parse_vietnamese_speech
                parsed_raw_items = parse_vietnamese_speech(text)
            except Exception:
                pass

        # Fallback cho input ngắn (ví dụ: "thịt ba rọi 300g")
        if not parsed_raw_items:
            m_qty = re.search(r"(\d+(?:[.,]\d+)?)\s*(kg|g|lạng|cân)?", text, re.I)
            qty_g = 200.0
            clean_str = text
            if m_qty:
                val = float(m_qty.group(1).replace(",", "."))
                unit = (m_qty.group(2) or "g").lower()
                if unit == "kg":
                    qty_g = val * 1000.0
                elif unit in ["lạng"]:
                    qty_g = val * 100.0
                elif unit in ["cân"]:
                    qty_g = val * 1000.0
                else:
                    qty_g = val
                clean_str = text[: m_qty.start()] + text[m_qty.end() :]
            clean_str = re.sub(r"[^\w\s]", " ", clean_str).strip()
            parsed_raw_items = [{"name": clean_str, "quantity_g": qty_g, "storage_mode": "fridge_2_4c"}]

        # Làm giàu toàn bộ items qua Tầng 4
        enriched = []
        for it in parsed_raw_items:
            if it.get("name"):
                enriched.append(self.enrich_item(it))

        return enriched


def get_pantry_parser() -> PantryEntityParser:
    global _PARSER_INSTANCE
    if _PARSER_INSTANCE is None:
        _PARSER_INSTANCE = PantryEntityParser()
    return _PARSER_INSTANCE
