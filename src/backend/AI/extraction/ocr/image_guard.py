"""Cheap vision guard that rejects images which are not food labels or invoices."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
from enum import Enum

import httpx

from AI.errors import ExtractionBadResponseError, ExtractionUnavailableError
from AI.extraction.ocr.image_preprocessor import encode_image_to_base64
from AI.llm.openai_client import OpenAIClient
from src.core.setting import (
    OPENAI_API_KEY,
    OPENAI_BASE_URL,
    OPENAI_OCR_GUARD_MODEL,
    OPENAI_TIMEOUT_SECONDS,
)

GUARD_MAX_DIM = 768

GUARD_PROMPT = (
    "Bạn là bộ lọc đầu vào cho hệ thống OCR của ứng dụng quản lý thực phẩm.\n"
    "Phân loại ảnh thành đúng MỘT loại:\n"
    '- "food_label": tem nhãn / bao bì sản phẩm thực phẩm hoặc nguyên liệu nấu ăn '
    "(tem cân giá siêu thị, nhãn hộp, túi, vỉ; có thể chứa tên sản phẩm, khối lượng, HSD, NSX).\n"
    '- "invoice": hóa đơn / biên lai mua hàng (siêu thị, chợ, cửa hàng), có danh sách mặt hàng.\n'
    '- "other": mọi thứ còn lại (ảnh người, phong cảnh, món ăn đã nấu, màn hình, giấy tờ, '
    "tài liệu không phải hóa đơn mua hàng, bao bì không phải thực phẩm như mỹ phẩm/thuốc/đồ gia dụng, "
    "ảnh mờ không đọc được, ảnh trống).\n"
    "Chỉ chọn food_label hoặc invoice khi chắc chắn; nghi ngờ thì chọn other.\n"
    'Trả về DUY NHẤT JSON: {"category": "food_label|invoice|other", '
    '"confidence": số từ 0 đến 1, "reason": "một câu ngắn tiếng Việt"}.'
)


class ImageCategory(str, Enum):
    """Image categories the guard can assign."""

    FOOD_LABEL = "food_label"
    INVOICE = "invoice"
    OTHER = "other"


@dataclass(frozen=True)
class GuardVerdict:
    """Guard classification of one image."""

    category: ImageCategory
    confidence: float
    reason: str

    @property
    def accepted(self) -> bool:
        """Whether the image may be sent to the OCR model."""
        return self.category is not ImageCategory.OTHER


class OpenAIImageGuard:
    """Classify an image before the expensive OCR call."""

    def __init__(
        self,
        *,
        api_key: str | None = None,
        base_url: str | None = None,
        model: str | None = None,
        timeout: float | None = None,
        http_client: httpx.AsyncClient | None = None,
        openai_client: OpenAIClient | None = None,
    ) -> None:
        self.api_key = api_key if api_key is not None else OPENAI_API_KEY
        self.model = model or OPENAI_OCR_GUARD_MODEL
        self.timeout = timeout if timeout is not None else float(OPENAI_TIMEOUT_SECONDS)
        self.openai_client = openai_client or OpenAIClient(
            api_key=self.api_key,
            base_url=(base_url or OPENAI_BASE_URL).rstrip("/"),
            model=self.model,
            timeout=self.timeout,
            http_client=http_client,
        )

    async def classify(self, image_bytes: bytes) -> GuardVerdict:
        """Return the guard verdict for one image."""
        if not self.api_key or not self.api_key.strip():
            raise ExtractionUnavailableError(
                "OpenAI API key is missing or not configured."
            )
        b64_str, _stats = await asyncio.to_thread(
            encode_image_to_base64, image_bytes, max_dim=GUARD_MAX_DIM
        )
        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": GUARD_PROMPT},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/webp;base64,{b64_str}",
                            "detail": "low",
                        },
                    },
                ],
            }
        ]
        payload = await self.openai_client.create_chat_completion_json(
            messages,
            model=self.model,
            max_completion_tokens=200,
            timeout=self.timeout,
        )
        return _parse_verdict(payload)

    async def aclose(self) -> None:
        """Close the shared HTTP connection pool owned by this client."""
        await self.openai_client.aclose()


def _parse_verdict(payload: object) -> GuardVerdict:
    """Validate the guard model output; an unreadable answer is a provider error."""
    if not isinstance(payload, dict):
        raise ExtractionBadResponseError("Image guard returned a non-object response.")
    try:
        category = ImageCategory(str(payload.get("category", "")).strip().lower())
    except ValueError as error:
        raise ExtractionBadResponseError(
            "Image guard returned an unknown category."
        ) from error
    raw_confidence = payload.get("confidence")
    confidence = (
        float(raw_confidence)
        if isinstance(raw_confidence, (int, float)) and not isinstance(raw_confidence, bool)
        else 0.0
    )
    return GuardVerdict(
        category=category,
        confidence=min(max(confidence, 0.0), 1.0),
        reason=str(payload.get("reason") or "").strip(),
    )
