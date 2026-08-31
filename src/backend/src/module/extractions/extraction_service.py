"""Extraction service: validate media input and delegate to mock providers."""

from fastapi import UploadFile

from src.core.setting import (
    EXTRACTION_ALLOWED_AUDIO_TYPES,
    EXTRACTION_ALLOWED_IMAGE_TYPES,
    EXTRACTION_MAX_AUDIO_SIZE,
    EXTRACTION_MAX_IMAGE_SIZE,
)
from src.module.extractions.extraction_dto import (
    BarcodeExtractionResponse,
    ExtractionResponse,
    InvoiceExtractionResponse,
)
from src.module.extractions.extraction_provider import (
    mock_asr,
    mock_barcode_lookup,
    mock_ocr_invoice,
    mock_ocr_label,
)


class ExtractionValidationError(Exception):
    """Raised when uploaded media fails validation."""

    def __init__(self, detail: str) -> None:
        """Store a client-safe error detail message."""
        self.detail = detail
        super().__init__(detail)


def _parse_allowed_types(raw: str) -> set[str]:
    """Parse a comma-separated allowed MIME type list."""
    return {t.strip() for t in raw.split(",") if t.strip()}


def _validate_image(file: UploadFile, content: bytes) -> None:
    """Reject images that exceed size or type limits."""
    if len(content) > EXTRACTION_MAX_IMAGE_SIZE:
        raise ExtractionValidationError(
            f"Image exceeds maximum size of {EXTRACTION_MAX_IMAGE_SIZE} bytes"
        )
    allowed = _parse_allowed_types(EXTRACTION_ALLOWED_IMAGE_TYPES)
    if file.content_type not in allowed:
        raise ExtractionValidationError(
            f"Image type '{file.content_type}' is not allowed; "
            f"accepted: {', '.join(sorted(allowed))}"
        )


def _validate_audio(file: UploadFile, content: bytes) -> None:
    """Reject audio that exceeds size or type limits."""
    if len(content) > EXTRACTION_MAX_AUDIO_SIZE:
        raise ExtractionValidationError(
            f"Audio exceeds maximum size of {EXTRACTION_MAX_AUDIO_SIZE} bytes"
        )
    allowed = _parse_allowed_types(EXTRACTION_ALLOWED_AUDIO_TYPES)
    if file.content_type not in allowed:
        raise ExtractionValidationError(
            f"Audio type '{file.content_type}' is not allowed; "
            f"accepted: {', '.join(sorted(allowed))}"
        )


async def extract_ocr_label(file: UploadFile) -> ExtractionResponse:
    """Validate and return a mock OCR label extraction."""
    content = await file.read()
    _validate_image(file, content)
    return mock_ocr_label(file.filename or "unknown")


async def extract_ocr_invoice(file: UploadFile) -> InvoiceExtractionResponse:
    """Validate and return a mock OCR invoice extraction."""
    content = await file.read()
    _validate_image(file, content)
    return mock_ocr_invoice(file.filename or "unknown")


async def extract_asr(file: UploadFile) -> ExtractionResponse:
    """Validate and return a mock ASR transcription extraction."""
    content = await file.read()
    _validate_audio(file, content)
    return mock_asr(file.filename or "unknown")


def extract_barcode(barcode: str) -> BarcodeExtractionResponse:
    """Return a mock barcode product lookup."""
    return mock_barcode_lookup(barcode)
