"""OpenAI Vision OCR Client for Vietnamese Food Labels and Supermarket Receipts."""

from __future__ import annotations

import asyncio
import datetime
import json
import re
from typing import Any

import httpx

from AI.errors import ExtractionUnavailableError
from AI.extraction.ocr.image_preprocessor import encode_image_to_base64
from AI.extraction.ocr.label_parser import parse_vietnamese_date
from AI.llm.openai_client import OpenAIClient

from src.core.setting import (
    OPENAI_API_KEY,
    OPENAI_BASE_URL,
    OPENAI_OCR_MODEL,
    OPENAI_OCR_REASONING_EFFORT,
    OPENAI_TIMEOUT_SECONDS,
)

# Longest side (px) of the image sent to the OCR model; smaller means fewer image
# tokens and a faster upload, at the cost of legibility for tiny print.
OCR_MAX_DIM = 720

SYSTEM_PROMPT = (
    "You are an OCR system for Vietnamese supermarket food labels and receipts.\n"
    "Read all text in the image (a packaging label or a shopping receipt) and return it as strict JSON.\n\n"
    "ACCURACY RULES:\n"
    "1. name: copy the printed text verbatim, character for character. If it is printed WITHOUT diacritics "
    "(e.g. TOM THE NC, THIT OC MONG TAY, CA BASA MINI, DUI GA GOC TU, CHAN GIO HEO, XUONG HEO CO THIT), "
    "keep it WITHOUT diacritics: never add diacritics or guess words. "
    "If it is printed WITH diacritics (e.g. Đậu rồng vỉ 200g, Chả cá Nha Trang, Má đùi gà), keep them exactly.\n"
    "2. quantity_g: the exact net weight in grams (float). Read the value next to 'KL:', 'KLT:', "
    "'Khối lượng', 'Trọng lượng' or the net weight. Convert kg to grams (x1000): "
    "'0,298 Kg' -> 298.0; '0,384 Kg' -> 384.0; '0.268 kg' -> 268.0; '500g' -> 500.0; '0,748 Kg' -> 748.0. "
    "Never mix up units.\n"
    "3. expiry_date, production_date, hours_to_expire, note: read the expiry date (HSD), the packing/production date "
    "(NĐG/NSX) or the shelf-life window (e.g. '3 ngày kể từ NĐG'). Dates must be DD/MM/YYYY when present. "
    "note must state every HSD and NĐG/NSX value you read (e.g. 'HSD: 02/10/2026 | NĐG: 02/10/2026').\n"
    "4. store_name: the supermarket/store chain if visible (e.g. Bách Hóa Xanh, WinMart, Co.opmart).\n\n"
    "Return ONLY one valid JSON object with this structure:\n"
    "{\n"
    '  "store_name": "store name or null",\n'
    '  "raw_text": "all text read from the image, verbatim, one line per printed line",\n'
    '  "items": [\n'
    "    {\n"
    '      "name": "verbatim raw food name (e.g. TOM THE NC, THIT OC MONG TAY, or Má đùi gà)",\n'
    '      "quantity_g": exact grams (float, e.g. 298.0, 384.0, 500.0, or null),\n'
    '      "expiry_date": "DD/MM/YYYY or null",\n'
    '      "production_date": "DD/MM/YYYY or null",\n'
    '      "hours_to_expire": remaining hours (float, e.g. 48.0, 72.0, or null),\n'
    '      "note": "HSD and NĐG/NSX details (e.g. HSD: 02/10/2026 | NĐG: 02/10/2026)"\n'
    "    }\n"
    "  ]\n"
    "}\n"
)


class OpenAIVisionOCR:
    """Async OpenAI Vision OCR client using httpx."""

    def __init__(
        self,
        *,
        api_key: str | None = None,
        base_url: str | None = None,
        model: str | None = None,
        reasoning_effort: str | None = None,
        timeout: float | None = None,
        http_client: httpx.AsyncClient | None = None,
        openai_client: OpenAIClient | None = None,
    ) -> None:
        self.api_key = api_key if api_key is not None else OPENAI_API_KEY
        self.base_url = (base_url or OPENAI_BASE_URL).rstrip("/")
        self.model = model or OPENAI_OCR_MODEL
        self.reasoning_effort = (
            reasoning_effort
            if reasoning_effort is not None
            else OPENAI_OCR_REASONING_EFFORT
        )
        self.timeout = (
            timeout if timeout is not None else float(OPENAI_TIMEOUT_SECONDS)
        )
        self._client = http_client
        self.openai_client = openai_client or OpenAIClient(
            api_key=self.api_key,
            base_url=self.base_url,
            model=self.model,
            timeout=self.timeout,
            http_client=http_client,
        )
    def _parse_llm_json(self, response_text: str) -> dict[str, Any]:
        """Extract and parse JSON block from LLM completion text."""

        # Check ```json ... ``` markdown block
        m = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", response_text, re.DOTALL)
        if m:
            try:
                return json.loads(m.group(1))
            except (json.JSONDecodeError, ValueError):
                pass

        # Check raw json object { ... }
        m2 = re.search(r"(\{.*\})", response_text, re.DOTALL)
        if m2:
            try:
                return json.loads(m2.group(1))
            except (json.JSONDecodeError, ValueError):
                pass

        try:
            return json.loads(response_text)
        except (json.JSONDecodeError, ValueError):
            return {"raw_text": response_text, "items": []}

    async def recognize_image_bytes(
        self,
        image_bytes: bytes,
        max_dim: int = OCR_MAX_DIM,
        ref_date: datetime.date | None = None,
    ) -> dict[str, Any]:
        """Perform preprocessing and call OpenAI Chat Completions API with image input."""
        if not self.api_key or not self.api_key.strip():
            raise ExtractionUnavailableError(
                "OpenAI API key is missing or not configured."
            )

        b64_str, stats = await asyncio.to_thread(
            encode_image_to_base64, image_bytes, max_dim=max_dim
        )
        data_url = f"data:image/webp;base64,{b64_str}"

        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": SYSTEM_PROMPT},
                    {
                        "type": "image_url",
                        "image_url": {"url": data_url},
                    },
                ],
            }
        ]
        content = await self.openai_client.create_chat_completion(
            messages=messages,
            model=self.model,
            max_completion_tokens=4096,
            reasoning_effort=self.reasoning_effort or None,
            response_format={"type": "json_object"},
            timeout=self.timeout,
        )
        parsed_data = self._parse_llm_json(content)
        raw_text = parsed_data.get("raw_text", "") or content
        store_name = parsed_data.get("store_name")
        items = parsed_data.get("items", [])

        clean_items: list[dict[str, Any]] = []
        now_date = ref_date or datetime.date.today()

        for it in items:
            name = str(it.get("name") or "").strip()
            if not name or len(name) < 2:
                continue

            raw_q = it.get("quantity_g")
            is_extracted = False
            q_g: float | None = None
            if raw_q is not None:
                try:
                    if isinstance(raw_q, str):
                        raw_q = float(
                            raw_q.replace("g", "")
                            .replace("kg", "")
                            .replace(",", ".")
                            .strip()
                        )
                    parsed_val = float(raw_q)
                    if 0.0 < parsed_val < 5.0:  # kg -> g
                        q_g = round(parsed_val * 1000.0, 1)
                    else:
                        q_g = round(parsed_val, 1)
                    is_extracted = True
                except (ValueError, TypeError):
                    q_g = None

            hrs: float | None = None
            try:
                if it.get("hours_to_expire") is not None:
                    hrs = float(it["hours_to_expire"])
            except (ValueError, TypeError):
                hrs = None

            exp_date_str = it.get("expiry_date")
            prod_date_str = it.get("production_date")
            note = str(it.get("note") or "").strip()
            if not note and exp_date_str:
                note = f"HSD: {exp_date_str}"

            # Evaluate expiry check
            expiry_check: str | None = None
            if exp_date_str:
                exp_date = parse_vietnamese_date(exp_date_str)
                if exp_date is not None:
                    expiry_check = "suspicious" if exp_date < now_date else "ok"

            clean_items.append(
                {
                    "name": name,
                    "raw_name": name,
                    "quantity_g": q_g if q_g is not None else 500.0,
                    "quantity_source": ("extracted" if is_extracted else "estimated"),
                    "expiry_date": exp_date_str,
                    "production_date": prod_date_str,
                    "hours_to_expire": hrs or 72.0,
                    "expiry_check": expiry_check,
                    "note": note,
                    "confidence": 0.95,
                }
            )

        return {
            "status": "success",
            "source": "openai_vision",
            "engine": f"OpenAI ({self.model})",
            "store_name": store_name,
            "raw_text": raw_text,
            "items_count": len(clean_items),
            "items": clean_items,
            "preprocess_stats": stats,
        }

    async def aclose(self) -> None:
        """Close the shared HTTP connection pool owned by this client."""
        await self.openai_client.aclose()
