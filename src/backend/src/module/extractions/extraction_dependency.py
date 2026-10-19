"""Dependencies for extraction endpoints."""

from __future__ import annotations

from AI.extraction.service import get_ai_extraction_service
from src.module.extractions.extraction_service import ExtractionService


def get_extraction_service() -> ExtractionService:
    """Create an extraction service backed by in-process AI extraction service."""
    return ExtractionService(ai_service=get_ai_extraction_service())
