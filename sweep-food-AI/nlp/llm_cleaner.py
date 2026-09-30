"""Vietnamese Culinary Ingredient Text Sanitizer powered by Small LLM (3-5B).

Uses Qwen2.5-3B-Instruct (or compatible 3B-5B model) on NVIDIA RTX 4060 GPU
to split compound ingredients, clean culinary terms, and translate units (tbsp, tsp, cup, lbs...)
into natural, user-friendly Vietnamese culinary units (muỗng canh, muỗng cà phê, chén, g...).
"""

from __future__ import annotations

import json
import logging
import re
import sys
import unicodedata
from pathlib import Path
from typing import Any

# Ensure UTF-8 output
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

logger = logging.getLogger("llm_cleaner")

try:
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False


SYSTEM_PROMPT = """Bạn là trợ lý AI chuyên gia về dữ liệu ẩm thực Việt Nam.
Nhiệm vụ của bạn là chuẩn hóa danh sách các dòng nguyên liệu nấu ăn thô thu thập từ website thành dữ liệu JSON có cấu trúc rõ ràng, thân thiện với người nấu ăn tại Việt Nam.

Quy tắc bắt buộc:
1. TÁCH DÒNG GỘP:
   - Nếu một dòng chứa nhiều nguyên liệu (ví dụ: '1 ít gia vị: mắm, muối, tiêu, tỏi băm' hoặc 'Hành ngò 1 ít'), phải tách thành từng nguyên liệu riêng biệt (hành lá, ngò rí, nước mắm, muối...).
2. VIỆT HÓA ĐƠN VỊ ĐỊNH LƯỢNG:
   - Chuyển 'tbsp', 'M', 'muỗng súp', 'thìa canh' -> 'muỗng canh'
   - Chuyển 'tsp', 'm', 'mcf', 'thìa cà phê' -> 'muỗng cà phê'
   - Chuyển 'cup', 'tách' -> 'chén / cốc'
   - Chuyển 'lb', 'lbs', 'pound' -> 'g' (nhân 453.6 và làm tròn)
   - Chuyển 'lạng' -> 'g' (nhân 100)
   - Các đơn vị tiếng Việt tự nhiên: 'kg', 'g', 'lít', 'ml', 'trái', 'củ', 'tép', 'nhánh', 'bó', 'lát', 'gói', 'vừa đủ / chút ít'.
3. CHUẨN HÓA TÊN & BỎ THƯƠNG HIỆU:
   - Bỏ các nhãn hiệu thương mại như 'AJI-NO-MOTO', 'Aji-ngon', 'Knorr', 'Maggi', 'Chinsu', 'Nam Ngư', bỏ ký hiệu ® ™.
   - Bỏ từ thừa như 'loại 1', 'tươi ngon', 'hảo hạng'.
   - Đưa về tên ẩm thực thông dụng: 'thơm / dứa' -> 'dứa', 'bột xá xíu' -> 'gia vị xá xíu', 'nước tương' -> 'nước tương'.
4. GHI CHÚ SƠ CHẾ: Trích xuất cách sơ chế vào 'preparation_note' (ví dụ: 'băm nhỏ', 'thái lát', 'bóc vỏ', 'luộc chín').

Định dạng trả về duy nhất là một mảng JSON hợp lệ, KHÔNG kèm lời giải thích:
[
  {
    "name": "tên nguyên liệu sạch",
    "quantity": 1.0,
    "unit_vi": "muỗng canh",
    "canonical_unit": "MUONG_CANH",
    "preparation_note": "băm nhỏ"
  }
]
"""

# Vietnamese Unit Dictionary with factor and display text
VIETNAMESE_UNIT_MAP = {
    # Spoons -> muỗng canh / muỗng cà phê
    "tbsp": {"unit": "MUONG_CANH", "unit_vi": "muỗng canh", "factor_ml": 15.0},
    "tablespoon": {"unit": "MUONG_CANH", "unit_vi": "muỗng canh", "factor_ml": 15.0},
    "muỗng canh": {"unit": "MUONG_CANH", "unit_vi": "muỗng canh", "factor_ml": 15.0},
    "thìa canh": {"unit": "MUONG_CANH", "unit_vi": "muỗng canh", "factor_ml": 15.0},
    "muỗng súp": {"unit": "MUONG_CANH", "unit_vi": "muỗng canh", "factor_ml": 15.0},
    "thìa súp": {"unit": "MUONG_CANH", "unit_vi": "muỗng canh", "factor_ml": 15.0},
    "m": {"unit": "MUONG_CA_PHE", "unit_vi": "muỗng cà phê", "factor_ml": 5.0},
    "tsp": {"unit": "MUONG_CA_PHE", "unit_vi": "muỗng cà phê", "factor_ml": 5.0},
    "teaspoon": {"unit": "MUONG_CA_PHE", "unit_vi": "muỗng cà phê", "factor_ml": 5.0},
    "muỗng cà phê": {"unit": "MUONG_CA_PHE", "unit_vi": "muỗng cà phê", "factor_ml": 5.0},
    "thìa cà phê": {"unit": "MUONG_CA_PHE", "unit_vi": "muỗng cà phê", "factor_ml": 5.0},
    "muỗng cafe": {"unit": "MUONG_CA_PHE", "unit_vi": "muỗng cà phê", "factor_ml": 5.0},
    "thìa cafe": {"unit": "MUONG_CA_PHE", "unit_vi": "muỗng cà phê", "factor_ml": 5.0},
    "muỗng cf": {"unit": "MUONG_CA_PHE", "unit_vi": "muỗng cà phê", "factor_ml": 5.0},
    "thìa cf": {"unit": "MUONG_CA_PHE", "unit_vi": "muỗng cà phê", "factor_ml": 5.0},
    "cafe": {"unit": "MUONG_CA_PHE", "unit_vi": "muỗng cà phê", "factor_ml": 5.0},
    "mcf": {"unit": "MUONG_CA_PHE", "unit_vi": "muỗng cà phê", "factor_ml": 5.0},
    "muỗng": {"unit": "MUONG_CANH", "unit_vi": "muỗng canh", "factor_ml": 15.0},
    "thìa": {"unit": "MUONG_CANH", "unit_vi": "muỗng canh", "factor_ml": 15.0},
    # Cups -> chén / cốc
    "cup": {"unit": "CHEN_COC", "unit_vi": "chén / cốc", "factor_ml": 240.0},
    "chén": {"unit": "CHEN_COC", "unit_vi": "chén / cốc", "factor_ml": 200.0},
    "cốc": {"unit": "CHEN_COC", "unit_vi": "chén / cốc", "factor_ml": 250.0},
    "bát": {"unit": "CHEN_COC", "unit_vi": "chén / bát", "factor_ml": 250.0},
    "tách": {"unit": "CHEN_COC", "unit_vi": "tách", "factor_ml": 150.0},
    "ly": {"unit": "CHEN_COC", "unit_vi": "ly", "factor_ml": 250.0},
    # Mass
    "kg": {"unit": "KG", "unit_vi": "kg", "factor_g": 1000.0},
    "kí": {"unit": "KG", "unit_vi": "kg", "factor_g": 1000.0},
    "kilogram": {"unit": "KG", "unit_vi": "kg", "factor_g": 1000.0},
    "g": {"unit": "GRAM", "unit_vi": "g", "factor_g": 1.0},
    "gr": {"unit": "GRAM", "unit_vi": "g", "factor_g": 1.0},
    "gram": {"unit": "GRAM", "unit_vi": "g", "factor_g": 1.0},
    "gam": {"unit": "GRAM", "unit_vi": "g", "factor_g": 1.0},
    "lạng": {"unit": "GRAM", "unit_vi": "g (lạng)", "factor_g": 100.0},
    "lb": {"unit": "GRAM", "unit_vi": "g (quy đổi từ pound)", "factor_g": 453.6},
    "lbs": {"unit": "GRAM", "unit_vi": "g (quy đổi từ pound)", "factor_g": 453.6},
    "pound": {"unit": "GRAM", "unit_vi": "g (quy đổi từ pound)", "factor_g": 453.6},
    # Volume
    "l": {"unit": "LITER", "unit_vi": "lít", "factor_ml": 1000.0},
    "lít": {"unit": "LITER", "unit_vi": "lít", "factor_ml": 1000.0},
    "ml": {"unit": "ML", "unit_vi": "ml", "factor_ml": 1.0},
    # Discrete objects
    "quả": {"unit": "TRAI_QUA", "unit_vi": "quả"},
    "trái": {"unit": "TRAI_QUA", "unit_vi": "trái"},
    "củ": {"unit": "CU", "unit_vi": "củ"},
    "bắp": {"unit": "BAP", "unit_vi": "bắp"},
    "tép": {"unit": "TEP", "unit_vi": "tép"},
    "nhánh": {"unit": "NHANH", "unit_vi": "nhánh"},
    "cọng": {"unit": "NHANH", "unit_vi": "cọng"},
    "cây": {"unit": "CAY", "unit_vi": "cây"},
    "con": {"unit": "CON", "unit_vi": "con"},
    "bó": {"unit": "BO", "unit_vi": "bó"},
    "nắm": {"unit": "BO", "unit_vi": "nắm"},
    "lát": {"unit": "LAT_MIENG", "unit_vi": "lát"},
    "miếng": {"unit": "LAT_MIENG", "unit_vi": "miếng"},
    "khúc": {"unit": "LAT_MIENG", "unit_vi": "khúc"},
    "bánh": {"unit": "PIECE", "unit_vi": "cái / bánh"},
    "cái": {"unit": "PIECE", "unit_vi": "cái"},
    "viên": {"unit": "PIECE", "unit_vi": "viên"},
    "lá": {"unit": "PIECE", "unit_vi": "lá"},
    "tai": {"unit": "PIECE", "unit_vi": "tai"},
    "gói": {"unit": "PACK", "unit_vi": "gói"},
    "hộp": {"unit": "PACK", "unit_vi": "hộp"},
    "lon": {"unit": "PACK", "unit_vi": "lon"},
    "túi": {"unit": "PACK", "unit_vi": "túi"},
    "bịch": {"unit": "PACK", "unit_vi": "bịch"},
    # Qualitative
    "chút": {"unit": "CHUT_IT", "unit_vi": "chút ít"},
    "nhúm": {"unit": "CHUT_IT", "unit_vi": "nhúm"},
    "ít": {"unit": "CHUT_IT", "unit_vi": "chút ít"},
    "vừa đủ": {"unit": "CHUT_IT", "unit_vi": "vừa đủ"},
}


class VietnameseLLMIngredientCleaner:
    """Active Small LLM Ingredient Sanitizer running on RTX 4060 GPU."""

    DEFAULT_MODEL = "Qwen/Qwen2.5-3B-Instruct"

    def __init__(
        self,
        model_name: str | None = None,
        device: str | None = None,
        lazy_load: bool = True,
    ) -> None:
        self.model_name = model_name or self.DEFAULT_MODEL
        self.device = device or ("cuda" if (TRANSFORMERS_AVAILABLE and torch.cuda.is_available()) else "cpu")
        self.model = None
        self.tokenizer = None
        self.lazy_load = lazy_load

        if not lazy_load:
            self._load_model()

    def _load_model(self) -> None:
        if not TRANSFORMERS_AVAILABLE or self.device != "cuda":
            logger.warning("CUDA/Transformers unavailable. Using intelligent rule-based sanitizer.")
            return

        if self.model is not None:
            return

        logger.info(f"Loading Small LLM [{self.model_name}] on {self.device} (RTX 4060)...")
        try:
            self.tokenizer = AutoTokenizer.from_pretrained(
                self.model_name,
                trust_remote_code=True,
            )
            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_name,
                torch_dtype=torch.float16,
                device_map="auto",
                trust_remote_code=True,
            )
            logger.info(f"Successfully loaded {self.model_name} onto GPU memory.")
        except Exception as e:
            logger.warning(f"Could not load LLM {self.model_name} ({e}). Falling back to heuristic cleaner.")
            self.model = None
            self.tokenizer = None

    def clean_recipe_ingredients(self, raw_ingredient_lines: list[str]) -> list[dict[str, Any]]:
        """Sanitize a list of raw ingredient strings from a recipe."""
        if not raw_ingredient_lines:
            return []

        # If LLM model is loaded, use LLM generation
        if self.model is not None and self.tokenizer is not None:
            try:
                return self._llm_clean(raw_ingredient_lines)
            except Exception as e:
                logger.error(f"LLM inference error: {e}. Using rule-based fallback.")

        # Fallback to rule-based compound separator & normalizer
        return self._heuristic_clean(raw_ingredient_lines)

    def _llm_clean(self, raw_lines: list[str]) -> list[dict[str, Any]]:
        """Run batched generation through Small LLM."""
        user_content = "Danh sách nguyên liệu thô cần chuẩn hóa:\n"
        for idx, line in enumerate(raw_lines, 1):
            user_content += f"{idx}. {line}\n"

        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_content},
        ]

        text_input = self.tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True,
        )
        model_inputs = self.tokenizer([text_input], return_tensors="pt").to(self.device)

        with torch.no_grad():
            generated_ids = self.model.generate(
                **model_inputs,
                max_new_tokens=1024,
                temperature=0.1,
                top_p=0.9,
                do_sample=False,
            )

        generated_ids = [
            output_ids[len(input_ids):]
            for input_ids, output_ids in zip(model_inputs.input_ids, generated_ids)
        ]
        response = self.tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0]

        match = re.search(r"\[\s*\{.*\}\s*\]", response, re.DOTALL)
        if match:
            try:
                data = json.loads(match.group(0))
                if isinstance(data, list):
                    # Attach raw text and standard units
                    for item in data:
                        u_vi = item.get("unit_vi", "khác")
                        item["unit_vi"] = u_vi
                        item["unit"] = item.get("canonical_unit", "OTHER")
                    return data
            except Exception:
                pass

        return self._heuristic_clean(raw_lines)

    def _heuristic_clean(self, raw_lines: list[str]) -> list[dict[str, Any]]:
        """Intelligent rule-based sanitizer: splits compounds, normalizes culinary terms."""
        cleaned_items: list[dict[str, Any]] = []

        common_spice_words = {
            "muối", "tiêu", "đường", "nước mắm", "dầu ăn", "bột ngọt", "mì chính",
            "hạt nêm", "tỏi", "ớt", "hành", "gừng", "sả", "chanh", "ngò", "rau thơm",
            "nước tương", "xì dầu", "giấm", "dấm", "mè", "vừng", "hành tím", "hành lá",
            "ngò rí", "hành tỏi", "rượu trắng", "dầu hào", "nước cốt chanh", "rau răm"
        }

        for line in raw_lines:
            line_str = unicodedata.normalize("NFC", line.strip())
            if not line_str:
                continue

            # Restore decomposed syllables (e.g. 'tra i' -> 'trái', 'thi t' -> 'thịt')
            decomposed_map = [
                (r"\btra\s+i\b", "trái"),
                (r"\bca\s+chua\b", "cà chua"),
                (r"\bthi\s+t\b", "thịt"),
                (r"\bđâ\s+u\b", "đậu"),
                (r"\bdư\s+a\b", "dừa"),
                (r"\bha\s+nh\b", "hành"),
                (r"\bsươ\s+n\b", "sườn"),
                (r"\bbô\s+t\b", "bột"),
                (r"\bdâ\s+u\b", "dầu"),
                (r"\bđươ\s+ng\b", "đường"),
                (r"\bto\s+i\b", "tỏi"),
                (r"\bnươ\s+c\b", "nước"),
                (r"\bmă\s+m\b", "mắm"),
                (r"\bba\s+ro\s+i\b", "ba rọi"),
                (r"\bba\s+chi\b", "ba chỉ"),
                (r"\bmuô\s+i\b", "muối"),
            ]
            for pat, rep in decomposed_map:
                line_str = re.sub(pat, rep, line_str, flags=re.IGNORECASE)

            # Strip serving prefixes: "Ăn kèm:", "Trang trí:", "Dùng kèm:"
            line_str = re.sub(r"^(?:ăn kèm|trang trí|dùng kèm|kèm theo|topping|nước chấm)\s*:\s*", "", line_str, flags=re.IGNORECASE).strip()

            # Handle 'A hoặc B': choose primary option A
            line_str = re.split(r"\s+hoặc\s+", line_str, flags=re.IGNORECASE)[0].strip()

            # Strip brands and symbols
            line_str = re.sub(r"[\®\™\©]", "", line_str)
            line_str = re.sub(r"\b(aji-no-moto|aji-ngon|knorr|maggi|chinsu|nam ngư|cholimex|đệ nhị|hảo hảo)\b", "", line_str, flags=re.IGNORECASE)

            # 5. Pre-normalize abbreviations
            line_str = re.sub(r"(?i)\b(?:muỗng|thìa)\s*(?:cà\s*phê|cafe|cf|mcf)\b", " muỗng cà phê", line_str)
            line_str = re.sub(r"(?i)\b(?:muỗng|thìa)\s*(?:canh|súp|soup)\b", " muỗng canh", line_str)
            line_str = re.sub(r"(?<=\d)\s*(?:cafe|cf|mcf)\b", " muỗng cà phê", line_str, flags=re.IGNORECASE)
            line_str = re.sub(r"(?<=\d)\s*M\b", " muỗng canh", line_str)
            line_str = re.sub(r"(?<=\d)\s*m\b", " muỗng cà phê", line_str)
            line_str = re.sub(r"(?<=\d)\s*mc\b", " muỗng canh", line_str, flags=re.IGNORECASE)
            line_str = re.sub(r"(?<=\d)\s*tbsp\b", " muỗng canh", line_str, flags=re.IGNORECASE)
            line_str = re.sub(r"(?<=\d)\s*tsp\b", " muỗng cà phê", line_str, flags=re.IGNORECASE)
            line_str = re.sub(r"(?<=\d)\s*cup\b", " chén", line_str, flags=re.IGNORECASE)

            # 6. Replace non-fraction slashes and ingredient-separating dots with commas
            line_str = re.sub(r"(?<=[^\d\s/])\s*/\s*(?=[^\d\s/])", ", ", line_str)
            line_str = re.sub(r"(?<=[a-zA-Zà-ỹÀ-Ỹ])\s*\.\s*(?=[a-zA-Zà-ỹÀ-Ỹ])", ", ", line_str)
            line_str = re.sub(r"(?<=[^\s])\s*(?:Gia vị|Nêm nếm|Topping)\s*:\s*", ", ", line_str, flags=re.IGNORECASE)

            # Normalize 'bắp hạt' -> 'ngô ngọt bắp hạt'
            line_str = re.sub(r"\bbắp hạt\b", "ngô hạt bắp", line_str, flags=re.IGNORECASE)

            # Smart split logic
            # 1. Special split: "Hành ngò" -> "Hành lá", "Ngò rí"
            if re.search(r"\bhành ngò\b", line_str, re.IGNORECASE):
                sub_tail = re.sub(r"\bhành ngò\b", "", line_str, flags=re.IGNORECASE).strip()
                sub_items = [f"hành lá {sub_tail}".strip(), f"ngò rí {sub_tail}".strip()]
            # 2. Special split: "Hành tỏi băm" -> "Hành tím băm", "Tỏi băm"
            elif re.search(r"\bhành\s*tỏi\s*băm\b", line_str, re.IGNORECASE):
                sub_tail = re.sub(r"\bhành\s*tỏi\s*băm\b", "", line_str, flags=re.IGNORECASE).strip()
                sub_items = [f"hành tím băm {sub_tail}".strip(), f"tỏi băm {sub_tail}".strip()]
            else:
                prefix_match = re.match(r"^(?:Gia vị|Nêm nếm|Hỗn hợp|Topping)\s*:\s*(.+)$", line_str, re.IGNORECASE)
                if prefix_match:
                    content = prefix_match.group(1)
                    sub_items = [s.strip() for s in re.split(r"[,;+]", content) if s.strip()]
                else:
                    # Check comma split without breaking decimal commas e.g. 4,5 or 0,5
                    test_line = re.sub(r"(\d+),(\d+)", r"\1.\2", line_str)
                    if "," in test_line:
                        parts = [s.strip() for s in test_line.split(",") if s.strip()]
                        if len(parts) >= 3:
                            sub_items = parts
                        elif len(parts) == 2:
                            p1, p2 = parts[0], parts[1]
                            has_digits_p2 = bool(re.search(r"\d", p2))
                            p2_lower = p2.lower()
                            has_known_spice = any(re.search(rf"\b{re.escape(w)}\b", p2_lower) for w in common_spice_words)
                            is_pure_prep = bool(re.match(r"^(thái|băm|cắt|rửa|để ráo|bào|lột|xắt|chặt|ngâm|đập|bóc|phi thơm)\b", p2_lower)) and not has_known_spice
                            if (has_digits_p2 or has_known_spice) and not is_pure_prep:
                                sub_items = [p1, p2]
                            else:
                                sub_items = [line_str]
                        else:
                            sub_items = [line_str]
                    else:
                        sub_items = [line_str]

            for item_text in sub_items:
                parsed_dict = self._parse_single_item(item_text)
                if parsed_dict:
                    cleaned_items.append(parsed_dict)

        return cleaned_items

    def _parse_single_item(self, text: str, term_map: dict[str, str] | None = None) -> dict[str, Any] | None:
        """Extract name, quantity, unit, and preparation note from a single item string."""
        raw = text.strip()
        if not raw:
            return None

        # Filter out standalone cooking instruction lines
        if re.match(r"^(để ráo|chờ nguội|chần nhanh trong nước|chần qua nước|rửa sạch để ráo)\b", raw, re.IGNORECASE):
            return None

        # Handle 'thơm/ dứa' or 'thơm / dứa'
        raw = re.sub(r"\b(thơm\s*/\s*dứa|dứa\s*/\s*thơm|khóm\s*/\s*dứa)\b", "dứa", raw, flags=re.IGNORECASE)

        # Extract preparation notes in parentheses
        prep_note = None
        prep_match = re.search(r"\((.*?)\)", raw)
        if prep_match:
            prep_note = prep_match.group(1).strip()
            raw = re.sub(r"\(.*?\)", "", raw).strip()

        # Handle numeric ranges: "3-4", "400-500", "100 - 150"
        range_m = re.search(r"(\d+(?:[.,]\d+)?)\s*[-–~]\s*(\d+(?:[.,]\d+)?)", raw)
        if range_m:
            q1 = float(range_m.group(1).replace(",", "."))
            q2 = float(range_m.group(2).replace(",", "."))
            avg_q = round((q1 + q2) / 2.0, 2)
            raw = raw[:range_m.start()] + str(avg_q) + raw[range_m.end():]

        # Check for trailing preparation terms: "băm nhỏ", "thái lát", "bóc vỏ"
        prep_patterns = [
            r"\b(băm nhỏ|băm nhuyễn|băm|thái mỏng|thái lát|thái hạt lựu|thái sợi|cắt khúc|cắt đôi|xắt nhỏ|nướng|luộc|hấp|rang|xào|xé sợi|bóc vỏ|làm sạch)\b"
        ]
        for p in prep_patterns:
            m = re.search(p, raw, re.IGNORECASE)
            if m:
                found_prep = m.group(1)
                prep_note = f"{prep_note}, {found_prep}" if prep_note else found_prep
                raw = re.sub(p, "", raw, flags=re.IGNORECASE).strip()

        # Extract quantity and unit
        sorted_unit_keys = sorted(VIETNAMESE_UNIT_MAP.keys(), key=len, reverse=True)
        unit_regex_fragment = "|".join(re.escape(k) for k in sorted_unit_keys)

        qty = None
        unit = "OTHER"
        unit_vi = "khác"

        combined_pattern = r"(\d+\s*/\s*\d+|\d+(?:[.,]\d+)?|½|¼|¾)\s*(" + unit_regex_fragment + r")\b"
        standalone_pattern = r"(\d+\s*/\s*\d+|\d+(?:[.,]\d+)?|½|¼|¾)\b"

        m_comb = re.search(combined_pattern, raw, re.IGNORECASE)
        match = m_comb if m_comb else re.search(standalone_pattern, raw, re.IGNORECASE)

        name = raw
        if match:
            start, end = match.span()
            groups = match.groups()
            q_str = groups[0] if len(groups) > 0 else None
            u_str = groups[1] if len(groups) > 1 else None

            # parse quantity
            if q_str:
                q_str = q_str.strip()
                if "/" in q_str:
                    parts = q_str.split("/")
                    try:
                        qty = round(float(parts[0]) / float(parts[1]), 3)
                    except Exception:
                        qty = None
                elif q_str == "½":
                    qty = 0.5
                elif q_str == "¼":
                    qty = 0.25
                elif q_str == "¾":
                    qty = 0.75
                else:
                    try:
                        qty = float(q_str.replace(",", "."))
                    except ValueError:
                        qty = None

            # parse unit
            if u_str:
                u_lower = u_str.lower().strip()
                if u_lower in VIETNAMESE_UNIT_MAP:
                    u_info = VIETNAMESE_UNIT_MAP[u_lower]
                    unit = u_info["unit"]
                    unit_vi = u_info["unit_vi"]
                    if u_lower in ("lb", "lbs", "pound") and qty is not None:
                        qty = round(qty * 453.6, 1)
                        unit = "GRAM"
                        unit_vi = "g"
                    elif u_lower == "lạng" and qty is not None:
                        qty = round(qty * 100.0, 1)
                        unit = "GRAM"
                        unit_vi = "g"
                    elif u_lower in ("chút", "ít", "nhúm", "vừa đủ"):
                        qty = None
                        unit = "CHUT_IT"
                        unit_vi = "vừa đủ / chút ít"

            before = raw[:start].strip()
            after = raw[end:].strip()

            # If quantity & unit were in the middle: e.g. "Ớt chuông đỏ 25g Cắt sợi"
            has_before_letters = bool(re.search(r"[a-zA-Zà-ỹÀ-Ỹ]", before))
            if has_before_letters and not re.match(r"^(khoảng|tầm|cỡ|chừng|vài)\b", before, re.IGNORECASE):
                name = before
                if after:
                    prep_note = f"{prep_note}, {after}" if prep_note else after
            else:
                name = after

        # Strip leading numbers
        name = re.sub(r"^\s*\d+(?:[.,]\d+)?\s*", "", name)

        # Protect multi-word nouns from having their trailing parts stripped as units
        protected_multiword_nouns = ["thảo quả", "khổ qua", "lá chúc", "hoa hồi", "bông cải", "cải thảo", "súp lơ", "lá lốt", "lá mơ", "lá chanh"]
        is_protected = any(p in raw.lower() for p in protected_multiword_nouns)

        if not is_protected:
            lone_unit_pattern = r"^\s*(?:muỗng canh|muỗng cà phê|chén|cốc|bát|ly|kg|g|gr|ml|lít|quả|trái|củ|bắp|tép|nhánh|cọng|bó|nắm|gói|hộp|lon|bịch|chút|ít|vừa đủ)\b\s*"
            name = re.sub(lone_unit_pattern, "", name, flags=re.IGNORECASE)
            name = re.sub(r"\s+\b(?:muỗng canh|muỗng cà phê|chén|cốc|bát|ly|kg|g|gr|ml|lít|quả|trái|củ|bắp|tép|nhánh|cọng|bó|nắm|gói|hộp|lon|bịch|chút|ít|vừa đủ)\b\s*$", "", name, flags=re.IGNORECASE)

        # Clean name
        name = re.sub(r"[^\w\s]", " ", name)
        name = re.sub(r"\s+", " ", name).strip().lower()

        # Strip prefixes like 'ít gia vị nêm', 'gia vị nêm', 'gia vị'
        name = re.sub(r"^(?:ít\s+|vài\s+)?(?:gia vị nêm|gia vị|nêm nếm)\s*", "", name, flags=re.IGNORECASE).strip()

        # Strip leftover serving prefixes or 'cafe' at the start
        name = re.sub(r"^(?:ăn kèm|dùng kèm|kèm theo|trang trí)\s*", "", name, flags=re.IGNORECASE).strip()
        name = re.sub(r"^\s*cafe\s+", "", name, flags=re.IGNORECASE).strip()

        # Strip trailing prep actions if they remained in name
        trailing_prep = r"\s+\b(?:cắt|thái|xắt|băm|chặt|ngâm|chần|luộc|nướng|chiên|xào|xé|rửa|ướp|bào|tỉa|khứa)\s+(?:lát|sợi|khúc|nhỏ|mỏng|miếng|nhuyễn|vừa ăn|chữ thập|hạt lựu)?.*$"
        m_tp = re.search(trailing_prep, name, re.IGNORECASE)
        if m_tp and m_tp.start() > 3:
            note_part = name[m_tp.start():].strip()
            prep_note = f"{prep_note}, {note_part}" if prep_note else note_part
            name = name[:m_tp.start()].strip()

        # Apply safe culinary normalization
        safe_phrase_replacements = [
            (r"\bđường cát trắng\b", "đường trắng"),
            (r"\bđường cát\b", "đường trắng"),
            (r"\bđường kính trắng\b", "đường trắng"),
            (r"\bđường tinh luyện\b", "đường trắng"),
            (r"\bthịt ba rọi\b", "thịt ba chỉ"),
            (r"\bthịt nạc dăm\b", "thịt nạc vai"),
            (r"\brau bina\b", "cải bó xôi"),
            (r"\bbó xôi\b", "cải bó xôi"),
            (r"\bhành boa[- ]?rô\b", "tỏi tây"),
            (r"\bnạc thăn\b", "thịt nạc thăn"),
            (r"\bbột nêm\b", "hạt nêm"),
            (r"\bxì dầu\b", "nước tương"),
            (r"\bbột ngọt\b", "mì chính"),
            (r"(?<!rau\s)\bthơm\b", "dứa"),
            (r"(?<!rau\s)\bkhóm\b", "dứa"),
            (r"\bhành tỏi\b", "tỏi"),
            (r"\bmuối\s+hao\s+hao\b", "muối"),
        ]
        for pattern, rep in safe_phrase_replacements:
            name = re.sub(pattern, rep, name, flags=re.IGNORECASE)

        # Standalone 'mắm' -> 'nước mắm' without creating 'nước nước mắm' or corrupting other sauces
        name = re.sub(r"(?<!nước\s)\bmắm\b(?!\s*(tôm|ruốc|nêm|cá|kho|tép|còng|chua))", "nước mắm", name, flags=re.IGNORECASE)

        # Final cleanup
        name = re.sub(r"^(?:ăn kèm|dùng kèm|kèm theo|trang trí)\s*", "", name, flags=re.IGNORECASE).strip()
        name = re.sub(r"^\s*cafe\s+", "", name, flags=re.IGNORECASE).strip()
        name = re.sub(r"\s+", " ", name).strip()
        if not name or name in ("thông dụng", "gia vị", "nêm nếm", "nêm", "gia vị nêm"):
            name = "gia vị"

        # Default unit_vi fallback
        if unit_vi == "khác":
            if unit == "PIECE":
                unit_vi = "trái / cái"
            elif unit == "PACK":
                unit_vi = "gói / hộp"
            elif unit == "CHUT_IT":
                unit_vi = "vừa đủ / chút ít"
            else:
                unit_vi = "phần ăn"

        return {
            "name": name,
            "quantity": qty,
            "unit": unit,
            "unit_vi": unit_vi,
            "preparation_note": prep_note,
            "raw_text": text.strip(),
        }
