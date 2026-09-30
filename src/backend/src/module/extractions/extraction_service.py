"""Extraction service: validate media input and map typed AI responses."""

from datetime import date
from uuid import uuid4

from fastapi import UploadFile

from src.core.setting import (
    EXTRACTION_ALLOWED_AUDIO_TYPES,
    EXTRACTION_ALLOWED_IMAGE_TYPES,
    EXTRACTION_MAX_AUDIO_SIZE,
    EXTRACTION_MAX_IMAGE_SIZE,
)
from src.module.extractions.extraction_dto import (
    BarcodeExtractionResponse,
    ExtractionFields,
    ExtractionResponse,
    ExtractionStatus,
    InvoiceExtractionFields,
    InvoiceExtractionResponse,
    InvoiceLineItem,
)
from src.module.extractions.extraction_provider import mock_barcode_lookup
from src.service.sweep_food_ai_client import SweepFoodAIClient


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
    if not content:
        raise ExtractionValidationError("Image file is empty")
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
    if not content:
        raise ExtractionValidationError("Audio file is empty")
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


def _normalize_date(raw_date: str | None) -> str | None:
    """Convert supported OCR date formats to the public ISO date format."""
    if raw_date is None:
        return None
    try:
        if "/" not in raw_date:
            return date.fromisoformat(raw_date).isoformat()
        day, month, year = (int(part) for part in raw_date.split("/"))
        if year < 100:
            year += 2000
        return date(year, month, day).isoformat()
    except (TypeError, ValueError):
        return None


class ExtractionService:
    """Validate uploads, call the AI service, and map its typed responses."""

    def __init__(self, ai_client: SweepFoodAIClient) -> None:
        self._ai_client = ai_client

    async def extract_ocr_label(self, file: UploadFile) -> ExtractionResponse:
        """Extract one product label without inventing missing fields."""
        content = await file.read()
        _validate_image(file, content)
        result = await self._ai_client.extract_ocr(
            filename=file.filename or "label",
            content=content,
            content_type=file.content_type,
        )
        if not result.items:
            return ExtractionResponse(
                request_id=uuid4(),
                status=ExtractionStatus.FAILED,
                provider="SWEEP_FOOD_AI",
                raw_text=result.raw_text,
                fields=ExtractionFields(),
                confidence={},
                warnings=["NO_ITEMS_EXTRACTED"],
            )

        item = result.items[0]
        warnings: list[str] = []
        quantity = item.quantity_g if item.quantity_source == "extracted" else None
        if quantity is None:
            warnings.append("QUANTITY_NOT_EXTRACTED")
        packaged_at = _normalize_date(item.production_date)
        if packaged_at is None:
            warnings.append("PRODUCTION_DATE_NOT_EXTRACTED")
        expires_at = _normalize_date(item.expiry_date)
        if expires_at is None:
            warnings.append("EXPIRY_DATE_NOT_EXTRACTED")
        confidence = (
            {"ingredient_name": item.confidence} if item.confidence is not None else {}
        )
        if item.confidence is None:
            warnings.append("CONFIDENCE_NOT_AVAILABLE")

        return ExtractionResponse(
            request_id=uuid4(),
            status=ExtractionStatus.PARTIAL if warnings else ExtractionStatus.SUCCEEDED,
            provider="SWEEP_FOOD_AI",
            raw_text=result.raw_text,
            fields=ExtractionFields(
                ingredient_name=item.name,
                quantity=quantity,
                unit="GRAM" if quantity is not None else None,
                packaged_at=packaged_at,
                expires_at=expires_at,
            ),
            confidence=confidence,
            warnings=warnings,
        )

    async def extract_ocr_invoice(self, file: UploadFile) -> InvoiceExtractionResponse:
        """Return the provable subset of the current generic OCR response."""
        content = await file.read()
        _validate_image(file, content)
        result = await self._ai_client.extract_ocr(
            filename=file.filename or "invoice",
            content=content,
            content_type=file.content_type,
        )
        line_items = [
            InvoiceLineItem(
                name=item.name,
                quantity=(
                    item.quantity_g if item.quantity_source == "extracted" else None
                ),
                unit=(
                    "GRAM"
                    if item.quantity_g is not None
                    and item.quantity_source == "extracted"
                    else None
                ),
            )
            for item in result.items
        ]
        warnings = ["INVOICE_FINANCIAL_FIELDS_NOT_AVAILABLE"]
        if not line_items:
            warnings.append("NO_ITEMS_EXTRACTED")

        return InvoiceExtractionResponse(
            request_id=uuid4(),
            status=ExtractionStatus.PARTIAL,
            provider="SWEEP_FOOD_AI",
            raw_text=result.raw_text,
            fields=InvoiceExtractionFields(
                line_items=line_items,
                vendor_name=result.store_name,
            ),
            confidence={},
            warnings=warnings,
        )

    async def extract_asr(self, file: UploadFile) -> ExtractionResponse:
        """Map the first spoken ingredient and report any omitted items."""
        content = await file.read()
        _validate_audio(file, content)
        result = await self._ai_client.extract_asr(
            filename=file.filename or "audio",
            content=content,
            content_type=file.content_type,
        )
        if not result.items:
            return ExtractionResponse(
                request_id=uuid4(),
                status=ExtractionStatus.FAILED,
                provider="SWEEP_FOOD_AI",
                raw_text=result.transcript,
                fields=ExtractionFields(),
                confidence={},
                warnings=["NO_ITEMS_EXTRACTED"],
            )

        item = result.items[0]
        warnings: list[str] = []
        if len(result.items) > 1:
            warnings.append("ADDITIONAL_ITEMS_OMITTED")
        quantity = item.quantity_g if item.quantity_source == "spoken" else None
        if quantity is None:
            warnings.append("QUANTITY_NOT_SPOKEN")
        confidence = (
            {"ingredient_name": item.confidence} if item.confidence is not None else {}
        )

        return ExtractionResponse(
            request_id=uuid4(),
            status=ExtractionStatus.PARTIAL if warnings else ExtractionStatus.SUCCEEDED,
            provider="SWEEP_FOOD_AI",
            raw_text=result.transcript,
            fields=ExtractionFields(
                ingredient_name=item.name,
                quantity=quantity,
                unit="GRAM" if quantity is not None else None,
            ),
            confidence=confidence,
            warnings=warnings,
        )


def extract_barcode(barcode: str) -> BarcodeExtractionResponse:
    """Return a mock barcode product lookup."""
    return mock_barcode_lookup(barcode)
