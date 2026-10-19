"""Tier 3 LLM extraction using shared OpenAIClient with graceful degradation."""

from __future__ import annotations

import json
import logging
from typing import Any

import httpx

from AI.errors import ExtractionError
from AI.llm.openai_client import OpenAIClient
from src.core.setting import OPENAI_LLM_MODEL

logger = logging.getLogger(__name__)

LLM_SYSTEM_PROMPT = (
    "Bạn là Chuyên gia Trích xuất Nguyên liệu Ẩm thực cho SweepFood AI.\n"
    "Nhiệm vụ: Phân tích đoạn văn bản đầu vào (từ hóa đơn siêu thị OCR, giọng nói đi chợ, hoặc người dùng gõ) "
    "thành danh sách các nguyên liệu thực phẩm để lưu vào Tủ Lạnh.\n\n"
    "QUY TẮC BẮT BUỘC:\n"
    "1. Trích xuất từng món nguyên liệu riêng biệt. Bỏ qua giá tiền, thuế, mã vạch, túi nilon.\n"
    "2. Tách sạch thương hiệu siêu thị (CP, Vissan, Meat Deli...) và quy cách đóng gói (khay, vỉ, hộp).\n"
    "3. Quy đổi định lượng về đơn vị Gram (quantity_g) là số thực:\n"
    "   - 1 kg = 1000g, 1 lạng = 100g, nửa cân = 500g\n"
    "   - Nếu là số lượng quả/bó: ước lượng gram (1 quả cà chua ~ 75g, 1 bó rau ~ 350g, 1 quả trứng ~ 60g).\n"
    "4. Phán đoán storage_mode: 'fridge_2_4c' (ngăn mát), 'freezer_-18c' (ngăn đá), hoặc 'room_temp_25_30c' (nhiệt độ phòng cho hành, tỏi, củ).\n\n"
    "Trả về DUY NHẤT một khối JSON hợp lệ theo cấu trúc:\n"
    "{\n"
    '  "items": [\n'
    "    {\n"
    '      "name": "tên nguyên liệu sạch tiếng Việt",\n'
    '      "quantity_g": 300.0,\n'
    '      "storage_mode": "fridge_2_4c"\n'
    "    }\n"
    "  ]\n"
    "}\n"
)


class LLMExtractor:
    """Extracts structured culinary items using OpenAI chat completions."""

    def __init__(
        self,
        *,
        openai_client: OpenAIClient | None = None,
        model: str | None = None,
    ) -> None:
        self.openai_client = openai_client or OpenAIClient(
            model=model or OPENAI_LLM_MODEL
        )
        self.model = model or OPENAI_LLM_MODEL

    async def aextract_items(self, text: str) -> list[dict[str, Any]]:
        """Call OpenAI chat completion and parse structured items.

        Degrades gracefully to an empty list on timeout, rate limit (429),
        network disconnect, malformed JSON, or missing keys. Never raises.
        """
        if not text or not text.strip():
            return []

        user_content = f"VĂN BẢN ĐẦU VÀO:\n\"\"\"{text.strip()}\"\"\""
        messages = [
            {"role": "system", "content": LLM_SYSTEM_PROMPT},
            {"role": "user", "content": user_content},
        ]

        try:
            data = await self.openai_client.create_chat_completion_json(
                messages=messages,
                model=self.model,
                max_completion_tokens=4096,
            )

            raw_items: list[Any] = []
            if isinstance(data, dict):
                raw_items = data.get("items") or data.get("ingredients") or []
            elif isinstance(data, list):
                raw_items = data

            if not isinstance(raw_items, list):
                logger.warning(
                    "LLM extraction returned invalid structure (%s), falling back",
                    type(raw_items).__name__,
                )
                return []

            cleaned_items: list[dict[str, Any]] = []
            for it in raw_items:
                if not isinstance(it, dict):
                    continue
                name = str(it.get("name") or "").strip()
                if not name or len(name) < 2:
                    continue

                raw_qty = it.get("quantity_g")
                try:
                    qty_g = float(raw_qty) if raw_qty is not None else 200.0
                except (ValueError, TypeError):
                    qty_g = 200.0

                storage_mode = str(it.get("storage_mode") or "fridge_2_4c")
                if storage_mode not in ("fridge_2_4c", "freezer_-18c", "room_temp_25_30c"):
                    storage_mode = "fridge_2_4c"

                cleaned_items.append(
                    {
                        "name": name,
                        "raw_text": name,
                        "quantity_g": round(max(1.0, qty_g), 1),
                        "storage_mode": storage_mode,
                    }
                )

            return cleaned_items

        except ExtractionError as exc:
            # Typed warning with exception class name only; never log user text or prompt
            logger.warning(
                "LLM tier extraction failed due to %s, falling back to heuristic tier",
                type(exc).__name__,
            )
            return []
        except (KeyError, ValueError, TypeError, json.JSONDecodeError, httpx.HTTPError) as exc:
            logger.warning(
                "LLM tier extraction encountered unexpected %s, falling back to heuristic tier",
                type(exc).__name__,
            )
            return []
