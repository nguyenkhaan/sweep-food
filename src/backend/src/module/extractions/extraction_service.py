"""Extraction service: validate media input and map typed AI responses."""

import logging
from collections.abc import Iterable
from datetime import date
from typing import Any
from uuid import UUID, uuid4

from fastapi import UploadFile
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from AI.errors import ImageNotSupportedError
from AI.extraction.service import (
    AIExtractionService,
    get_ai_extraction_service,
)
from src.core.setting import (
    EXTRACTION_ALLOWED_AUDIO_TYPES,
    EXTRACTION_ALLOWED_IMAGE_TYPES,
    EXTRACTION_MAX_AUDIO_SIZE,
    EXTRACTION_MAX_IMAGE_SIZE,
)
from src.model.ingredient_category_model import IngredientCategoryModel
from src.model.master_ingredient_model import MasterIngredientModel
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

LOGGER = logging.getLogger(__name__)


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


def normalize_catalog_code(raw_code: object) -> str | None:
    """Normalize AI catalog codes such as ``7018.0`` to the stored source code."""
    if raw_code is None:
        return None
    code = str(raw_code).strip().removesuffix(".0")
    return code or None


_normalize_catalog_code = normalize_catalog_code

class ExtractionService:
    """Validate uploads, call in-process AI extraction, and map response DTOs."""

    def __init__(
        self,
        session: AsyncSession,
        ai_service: AIExtractionService | None = None,
    ) -> None:
        self._session = session
        self._ai_service = ai_service or get_ai_extraction_service()

    async def _master_info_by_code(
        self, items: Iterable[dict[str, Any]]
    ) -> dict[str, tuple[UUID, str | None]]:
        """Resolve AI catalog codes to (master_id, category_name) in one query."""
        codes = {
            code
            for item in items
            if (code := normalize_catalog_code(item.get("code"))) is not None
        }
        if not codes:
            return {}
        stmt = (
            select(
                MasterIngredientModel.source_code,
                MasterIngredientModel.id,
                IngredientCategoryModel.name,
            )
            .outerjoin(
                IngredientCategoryModel,
                MasterIngredientModel.category_id == IngredientCategoryModel.id,
            )
            .where(MasterIngredientModel.source_code.in_(codes))
        )
        rows = await self._session.execute(stmt)
        result: dict[str, tuple[UUID, str | None]] = {}
        for row in rows.all():
            if len(row) >= 3:
                code, master_id, category = row[0], row[1], row[2]
            else:
                code, master_id, category = row[0], row[1], None
            result[str(code)] = (master_id, category)
        return result

    async def _master_ids_by_code(
        self, items: Iterable[dict[str, Any]]
    ) -> dict[str, UUID]:
        """Resolve AI catalog codes to master ingredient ids in one query."""
        info = await self._master_info_by_code(items)
        return {code: master_id for code, (master_id, _) in info.items()}

    async def _process_image(
        self, content: bytes, filename: str
    ) -> dict[str, Any]:
        """Run guarded OCR; an off-topic image becomes a client-facing 422."""
        try:
            return await self._ai_service.process_receipt_input(
                image_bytes=content, filename=filename
            )
        except ImageNotSupportedError as error:
            raise ExtractionValidationError(
                "Image is not a food label, food packaging or an invoice: "
                f"{error.message}"
            ) from error

    async def extract_ocr_label(self, file: UploadFile) -> ExtractionResponse:
        """Extract one product label without inventing missing fields."""
        content = await file.read()
        _validate_image(file, content)
        result = await self._process_image(content, file.filename or "label")
        items = result.get("items", [])
        raw_text = str(result.get("raw_text") or "")
        if not items:
            return ExtractionResponse(
                request_id=uuid4(),
                status=ExtractionStatus.FAILED,
                provider="SWEEP_FOOD_AI",
                raw_text=raw_text,
                fields=ExtractionFields(),
                confidence={},
                warnings=["NO_ITEMS_EXTRACTED"],
            )

        master_info = await self._master_info_by_code(items[:1])
        item = items[0]
        matched_info = master_info.get(
            normalize_catalog_code(item.get("code")) or ""
        )
        master_id = matched_info[0] if matched_info else None
        category = matched_info[1] if matched_info else None
        warnings: list[str] = []
        quantity = (
            item.get("quantity_g")
            if item.get("quantity_source") == "extracted"
            else None
        )
        if quantity is None:
            warnings.append("QUANTITY_NOT_EXTRACTED")
        packaged_at = _normalize_date(item.get("production_date"))
        if packaged_at is None:
            warnings.append("PRODUCTION_DATE_NOT_EXTRACTED")
        expires_at = _normalize_date(item.get("expiry_date"))
        if expires_at is None:
            warnings.append("EXPIRY_DATE_NOT_EXTRACTED")
        elif item.get("expiry_check") == "suspicious":
            warnings.append("EXPIRY_DATE_SUSPICIOUS")
        item_conf = item.get("confidence")
        confidence = (
            {"ingredient_name": item_conf} if item_conf is not None else {}
        )
        if item_conf is None:
            warnings.append("CONFIDENCE_NOT_AVAILABLE")

        return ExtractionResponse(
            request_id=uuid4(),
            status=(
                ExtractionStatus.PARTIAL if warnings else ExtractionStatus.SUCCEEDED
            ),
            provider="SWEEP_FOOD_AI",
            raw_text=raw_text,
            fields=ExtractionFields(
                ingredient_name=item.get("name"),
                raw_name=item.get("raw_name"),
                master_ingredient_id=master_id,
                category=category,
                quantity=quantity,
                unit="GRAM" if quantity is not None else None,
                packaged_at=packaged_at,
                expires_at=expires_at,
            ),
            confidence=confidence,
            warnings=warnings,
        )

    async def extract_ocr_invoice(
        self, file: UploadFile
    ) -> InvoiceExtractionResponse:
        """Return the provable subset of the current generic OCR response."""
        content = await file.read()
        _validate_image(file, content)
        result = await self._process_image(content, file.filename or "invoice")
        items = result.get("items", [])
        master_info = await self._master_info_by_code(items)
        raw_text = str(result.get("raw_text") or "")
        vendor_name = result.get("store_name")
        line_items: list[InvoiceLineItem] = []
        for item in items:
            matched = master_info.get(
                normalize_catalog_code(item.get("code")) or ""
            )
            line_items.append(
                InvoiceLineItem(
                    name=item["name"],
                    raw_name=item.get("raw_name"),
                    master_ingredient_id=matched[0] if matched else None,
                    category=matched[1] if matched else None,
                    quantity=(
                        item.get("quantity_g")
                        if item.get("quantity_source") == "extracted"
                        else None
                    ),
                    unit=(
                        "GRAM"
                        if item.get("quantity_g") is not None
                        and item.get("quantity_source") == "extracted"
                        else None
                    ),
                )
            )
        warnings = ["INVOICE_FINANCIAL_FIELDS_NOT_AVAILABLE"]
        if not line_items:
            warnings.append("NO_ITEMS_EXTRACTED")
        LOGGER.info(
            "AI invoice OCR mapped item_count=%s has_raw_text=%s warnings=%s",
            len(line_items),
            bool(raw_text.strip()),
            warnings,
        )

        return InvoiceExtractionResponse(
            request_id=uuid4(),
            status=ExtractionStatus.PARTIAL,
            provider="SWEEP_FOOD_AI",
            raw_text=raw_text,
            fields=InvoiceExtractionFields(
                line_items=line_items,
                vendor_name=vendor_name,
            ),
            confidence={},
            warnings=warnings,
        )

    async def extract_asr(self, file: UploadFile) -> ExtractionResponse:
        """Map the first spoken ingredient and report any omitted items."""
        content = await file.read()
        _validate_audio(file, content)
        result = await self._ai_service.process_voice_input(
            audio_bytes=content,
            filename=file.filename or "audio.wav",
        )
        return await self._map_first_item(
            result.get("items", []), str(result.get("transcript") or "")
        )

    async def extract_text(self, text: str) -> ExtractionResponse:
        """Match typed text to the catalog and map the first ingredient."""
        result = await self._ai_service.process_text_input(text)
        return await self._map_first_item(result.get("items", []), text)

    async def _map_first_item(
        self, items: list[dict[str, Any]], raw_text: str
    ) -> ExtractionResponse:
        """Map the first parsed ingredient and report any omitted items."""
        if not items:
            return ExtractionResponse(
                request_id=uuid4(),
                status=ExtractionStatus.FAILED,
                provider="SWEEP_FOOD_AI",
                raw_text=raw_text,
                fields=ExtractionFields(),
                confidence={},
                warnings=["NO_ITEMS_EXTRACTED"],
            )

        master_info = await self._master_info_by_code(items[:1])
        item = items[0]
        matched_info = master_info.get(
            normalize_catalog_code(item.get("code")) or ""
        )
        master_id = matched_info[0] if matched_info else None
        category = matched_info[1] if matched_info else None
        warnings: list[str] = []
        if len(items) > 1:
            warnings.append("ADDITIONAL_ITEMS_OMITTED")
        quantity = (
            item.get("quantity_g")
            if item.get("quantity_source") == "extracted"
            else None
        )
        if quantity is None:
            warnings.append("QUANTITY_NOT_EXTRACTED")
        item_conf = item.get("confidence")
        confidence = (
            {"ingredient_name": item_conf} if item_conf is not None else {}
        )
        if item_conf is None:
            warnings.append("CONFIDENCE_NOT_AVAILABLE")

        return ExtractionResponse(
            request_id=uuid4(),
            status=(
                ExtractionStatus.PARTIAL if warnings else ExtractionStatus.SUCCEEDED
            ),
            provider="SWEEP_FOOD_AI",
            raw_text=raw_text,
            fields=ExtractionFields(
                ingredient_name=item.get("name"),
                raw_name=item.get("raw_name"),
                master_ingredient_id=master_id,
                category=category,
                quantity=quantity,
                unit="GRAM" if quantity is not None else None,
            ),
            confidence=confidence,
            warnings=warnings,
        )


def extract_barcode(barcode: str) -> BarcodeExtractionResponse:
    """Return a mock barcode product lookup."""
    return mock_barcode_lookup(barcode)
