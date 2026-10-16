"""OpenAI Vision OCR backend (default provider since 16/10/2026).

Reuses the preprocessing, OCR_PROMPT and JSON parsing of GroqVisionOCR and only
swaps the API call. Chosen after comparing 5 models on 25 real Bách Hóa Xanh
labels: gpt-6.1-sol with reasoning_effort="medium" left 24/25 labels needing no
correction, invented no dates and never returned an expiry later than the label.
Smaller OpenAI models misread rotated dates such as "2.10.2026" as 21/10.

Environment:
    OPENAI_API_KEY        required (environment or project .env)
    OPENAI_OCR_MODEL      default "gpt-6.1-sol"
    OPENAI_OCR_REASONING  default "medium" ("low" misread 2 dates in one test run)
"""

from __future__ import annotations

import os
from typing import Optional

from smart_input.ocr.groq_vision_ocr import GroqVisionOCR, _get_api_key

try:
    from openai import OpenAI
    HAS_OPENAI = True
except ImportError:
    HAS_OPENAI = False

DEFAULT_OPENAI_OCR_MODEL = "gpt-6.1-sol"
DEFAULT_OPENAI_OCR_REASONING = "medium"


class OpenAIVisionOCR(GroqVisionOCR):
    """OpenAI Vision OCR; same pipeline as GroqVisionOCR, different API call."""

    provider_name = "OpenAI"
    source_name = "openai_vision"
    api_key_name = "OPENAI_API_KEY"

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        reasoning_effort: Optional[str] = None,
    ):
        self.api_key = api_key or _get_api_key(self.api_key_name)
        self.model = model or os.environ.get("OPENAI_OCR_MODEL") or DEFAULT_OPENAI_OCR_MODEL
        self.reasoning_effort = (
            reasoning_effort or os.environ.get("OPENAI_OCR_REASONING") or DEFAULT_OPENAI_OCR_REASONING
        )
        self.client = None
        if HAS_OPENAI and self.api_key:
            self.client = OpenAI(api_key=self.api_key)

    def _connect(self) -> None:
        self.api_key = _get_api_key(self.api_key_name)
        if HAS_OPENAI and self.api_key:
            self.client = OpenAI(api_key=self.api_key)

    def _call_model(self, prompt: str, b64_str: str) -> str:
        assert self.client is not None
        completion = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {"url": f"data:image/webp;base64,{b64_str}"}},
                    ],
                }
            ],
            # Room for reasoning tokens on top of the JSON answer (~350 tokens).
            max_completion_tokens=4096,
            reasoning_effort=self.reasoning_effort,
        )
        return completion.choices[0].message.content or ""
