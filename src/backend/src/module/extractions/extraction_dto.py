"""Request and response DTOs for experimental extraction APIs."""

from __future__ import annotations

from enum import Enum
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class ExtractionStatus(str, Enum):
    """Outcome of an extraction attempt."""

    SUCCEEDED = "SUCCEEDED"
    FAILED = "FAILED"
    PARTIAL = "PARTIAL"


class ExtractionFields(BaseModel):
    """Structured fields extracted from OCR or ASR input."""

    model_config = ConfigDict(extra="forbid")

    ingredient_name: str | None = None
    quantity: float | None = None
    unit: str | None = None
    packaged_at: str | None = None
    expires_at: str | None = None
    price: float | None = None
    currency: str | None = None
    barcode: str | None = None


class ExtractionResponse(BaseModel):
    """Common envelope returned by all extraction endpoints."""

    model_config = ConfigDict(extra="forbid")

    request_id: UUID
    status: ExtractionStatus
    provider: str
    raw_text: str
    fields: ExtractionFields
    confidence: dict[str, float]
    warnings: list[str]
    persisted: bool = False


class InvoiceLineItem(BaseModel):
    """One extracted invoice line item."""

    model_config = ConfigDict(extra="forbid")

    name: str | None = None
    quantity: float | None = None
    unit: str | None = None
    unit_price: float | None = None
    total_price: float | None = None


class InvoiceExtractionFields(BaseModel):
    """Fields returned by invoice OCR extraction."""

    model_config = ConfigDict(extra="forbid")

    line_items: list[InvoiceLineItem]
    total_amount: float | None = None
    currency: str | None = None
    invoice_date: str | None = None
    vendor_name: str | None = None


class InvoiceExtractionResponse(BaseModel):
    """Common envelope for invoice OCR extraction."""

    model_config = ConfigDict(extra="forbid")

    request_id: UUID
    status: ExtractionStatus
    provider: str
    raw_text: str
    fields: InvoiceExtractionFields
    confidence: dict[str, float]
    warnings: list[str]
    persisted: bool = False


class BarcodeProductFields(BaseModel):
    """Product fields returned by barcode lookup."""

    model_config = ConfigDict(extra="forbid")

    barcode: str
    product_name: str | None = None
    brand: str | None = None
    category: str | None = None
    ingredient_name: str | None = None
    quantity: float | None = None
    unit: str | None = None
    expires_at: str | None = None
    price: float | None = None
    currency: str | None = None


class BarcodeExtractionResponse(BaseModel):
    """Common envelope for barcode lookup extraction."""

    model_config = ConfigDict(extra="forbid")

    request_id: UUID
    status: ExtractionStatus
    provider: str
    raw_text: str
    fields: BarcodeProductFields
    confidence: dict[str, float]
    warnings: list[str]
    persisted: bool = False
