"""High-level in-process AI Extraction Service facade."""

from __future__ import annotations

import logging
from typing import Any

from AI.extraction.asr.groq_whisper import GroqWhisperClient
from AI.extraction.asr.speech_parser import parse_vietnamese_speech
from AI.extraction.ocr.label_parser import FoodLabelParser
from AI.extraction.ocr.openai_vision_ocr import OpenAIVisionOCR
from AI.extraction.ocr.receipt_parser import parse_receipt_text
from AI.extraction.pantry_parser import CatalogPantryParser, PantryItemMatcher

logger = logging.getLogger(__name__)

_GLOBAL_EXTRACTION_SERVICE: AIExtractionService | None = None


class AIExtractionService:
    """Coordinates image OCR, voice ASR, and master ingredient enrichment."""

    def __init__(
        self,
        *,
        ocr_client: OpenAIVisionOCR | None = None,
        whisper_client: GroqWhisperClient | None = None,
        label_parser: FoodLabelParser | None = None,
        pantry_parser: PantryItemMatcher | None = None,
    ) -> None:
        self.ocr_client = ocr_client or OpenAIVisionOCR()
        self.whisper_client = whisper_client or GroqWhisperClient()
        self.label_parser = label_parser or FoodLabelParser()
        self.pantry_parser = pantry_parser or CatalogPantryParser()

    async def process_receipt_input(
        self,
        image_bytes: bytes,
        filename: str = "receipt.jpg",
    ) -> dict[str, Any]:
        """Process receipt or food packaging label image via OpenAI Vision OCR and enrich items."""
        ocr_res = await self.ocr_client.recognize_image_bytes(image_bytes)

        raw_items = ocr_res.get("items", [])
        raw_text = str(ocr_res.get("raw_text") or "")
        store_name = ocr_res.get("store_name")

        # If LLM extracted structured items, enrich them
        if raw_items:
            enriched_items = [
                self.pantry_parser.enrich_item(item) for item in raw_items
            ]
            return {
                "status": "success",
                "source": ocr_res.get("source", "openai_vision"),
                "engine": ocr_res.get("engine", "OpenAI"),
                "store_name": store_name,
                "raw_text": raw_text,
                "items_count": len(enriched_items),
                "items": enriched_items,
            }

        # Fallback parsing on raw text if no items directly structured by LLM
        if raw_text.strip():
            raw_lower = raw_text.lower()
            label_indicators = [
                "klt", "hsd", "nsx", "ndg", "nđg", "đơn giá", "don gia",
                "kl:", "k.l:", "trọng lượng", "trong luong", "khối lượng", "khoi luong",
                "hạn sử dụng", "han su dung", "ngày đóng gói", "ngay dong goi", "bao bì",
            ]
            if any(k in raw_lower for k in label_indicators):
                parsed_label = self.label_parser.parse_label_text(raw_text)
                fallback_items = [parsed_label]
            else:
                fallback_items = parse_receipt_text(raw_text)

            enriched_items = [
                self.pantry_parser.enrich_item(it) for it in fallback_items
            ]
            return {
                "status": "success",
                "source": "text_fallback",
                "engine": ocr_res.get("engine", "OpenAI"),
                "store_name": store_name,
                "raw_text": raw_text,
                "items_count": len(enriched_items),
                "items": enriched_items,
            }

        return {
            "status": "success",
            "source": ocr_res.get("source", "openai_vision"),
            "engine": ocr_res.get("engine", "OpenAI"),
            "store_name": store_name,
            "raw_text": raw_text,
            "items_count": 0,
            "items": [],
        }

    async def process_voice_input(
        self,
        audio_bytes: bytes | None = None,
        transcript: str | None = None,
        filename: str = "audio.wav",
    ) -> dict[str, Any]:
        """Process spoken Vietnamese audio upload or direct text transcript and enrich items."""
        effective_transcript = ""
        engine_used = "direct_transcript"

        if audio_bytes:
            asr_res = await self.whisper_client.transcribe_audio_bytes(
                audio_bytes, filename=filename
            )
            effective_transcript = str(asr_res.get("transcript") or "").strip()
            engine_used = str(asr_res.get("engine") or "groq_whisper_turbo")
        elif transcript:
            effective_transcript = transcript.strip()

        if not effective_transcript:
            return {
                "status": "success",
                "engine": engine_used,
                "transcript": "",
                "items_count": 0,
                "items": [],
            }

        parsed_items = parse_vietnamese_speech(effective_transcript)
        enriched_items = [
            self.pantry_parser.enrich_item(it) for it in parsed_items
        ]

        return {
            "status": "success",
            "engine": engine_used,
            "transcript": effective_transcript,
            "items_count": len(enriched_items),
            "items": enriched_items,
        }


def build_ai_extraction_service(
    *,
    pantry_matcher: PantryItemMatcher | None = None,
    ocr_client: OpenAIVisionOCR | None = None,
    whisper_client: GroqWhisperClient | None = None,
) -> AIExtractionService:
    """Construct an AIExtractionService, loading catalog snapshot if matcher not supplied."""
    if pantry_matcher is None:
        try:
            from AI.catalog.snapshot import load_snapshot_from_bundle

            snapshot = load_snapshot_from_bundle()
            pantry_matcher = CatalogPantryParser(
                master_alias_index=snapshot.master_alias_index,
                master_by_code=snapshot.master_by_code,
            )
        except (OSError, ValueError, KeyError) as exc:
            logger.warning(
                "Could not load catalog snapshot for AI extraction: %s", exc
            )
            pantry_matcher = CatalogPantryParser()

    return AIExtractionService(
        ocr_client=ocr_client,
        whisper_client=whisper_client,
        pantry_parser=pantry_matcher,
    )


def get_ai_extraction_service() -> AIExtractionService:
    """Return cached process-wide AIExtractionService singleton."""
    global _GLOBAL_EXTRACTION_SERVICE
    if _GLOBAL_EXTRACTION_SERVICE is None:
        _GLOBAL_EXTRACTION_SERVICE = build_ai_extraction_service()
    return _GLOBAL_EXTRACTION_SERVICE
