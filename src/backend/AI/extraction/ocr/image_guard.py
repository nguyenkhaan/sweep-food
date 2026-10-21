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
    "You are an input filter for the OCR pipeline of a food-management app.\n"
    "Classify the image as exactly ONE category:\n"
    '- "food_label": a label or packaging of a food product or cooking ingredient '
    "(supermarket weigh-price tag, box, bag or tray label; may show product name, weight, expiry/production dates).\n"
    '- "invoice": a purchase receipt or invoice (supermarket, market, shop) listing items.\n'
    '- "other": anything else (people, scenery, cooked dishes, screens, documents that are not purchase receipts, '
    "non-food packaging such as cosmetics/medicine/household goods, unreadable blurry or blank images).\n"
    "Choose food_label or invoice only when certain; if in doubt choose other.\n"
    'Return ONLY JSON: {"category": "food_label|invoice|other", '
    '"confidence": number from 0 to 1, "reason": "one short sentence in Vietnamese"}.'
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
            max_completion_tokens=128,
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
