"""Typed domain exceptions for AI extraction, LLM, and multimodal processing."""

from __future__ import annotations


class ExtractionError(Exception):
    """Base exception for all AI extraction and LLM errors."""

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message


class ExtractionUnavailableError(ExtractionError):
    """Raised when the AI provider is offline, unreachable, or missing credentials."""


class ExtractionTimeoutError(ExtractionError):
    """Raised when an AI provider request times out."""


class ExtractionBadResponseError(ExtractionError):
    """Raised when an AI provider returns an invalid or unparseable response."""


class AudioPreprocessingError(ExtractionError):
    """Raised when audio conversion or preprocessing fails (e.g. missing ffmpeg)."""
