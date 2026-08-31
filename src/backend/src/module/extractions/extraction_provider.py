"""Mock extraction providers that return deterministic sample data."""

from uuid import uuid4

from src.module.extractions.extraction_dto import (
    BarcodeExtractionResponse,
    BarcodeProductFields,
    ExtractionFields,
    ExtractionResponse,
    ExtractionStatus,
    InvoiceExtractionFields,
    InvoiceExtractionResponse,
    InvoiceLineItem,
)


def mock_ocr_label(_filename: str) -> ExtractionResponse:
    """Return a mock product label extraction result."""
    return ExtractionResponse(
        request_id=uuid4(),
        status=ExtractionStatus.SUCCEEDED,
        provider="MOCK_OCR",
        raw_text="Mock OCR label output",
        fields=ExtractionFields(
            ingredient_name="Whole Milk",
            quantity=1.0,
            unit="LITER",
            packaged_at="2026-08-28",
            expires_at="2026-09-05",
            price=35000.0,
            currency="VND",
            barcode=None,
        ),
        confidence={"ingredient_name": 0.95, "expires_at": 0.88},
        warnings=[],
        persisted=False,
    )


def mock_ocr_invoice(_filename: str) -> InvoiceExtractionResponse:
    """Return a mock invoice extraction result."""
    return InvoiceExtractionResponse(
        request_id=uuid4(),
        status=ExtractionStatus.SUCCEEDED,
        provider="MOCK_OCR",
        raw_text="Mock OCR invoice output",
        fields=InvoiceExtractionFields(
            line_items=[
                InvoiceLineItem(
                    name="Whole Milk",
                    quantity=2.0,
                    unit="LITER",
                    unit_price=35000.0,
                    total_price=70000.0,
                ),
                InvoiceLineItem(
                    name="Bread",
                    quantity=1.0,
                    unit="PIECE",
                    unit_price=15000.0,
                    total_price=15000.0,
                ),
            ],
            total_amount=85000.0,
            currency="VND",
            invoice_date="2026-08-30",
            vendor_name="Mock Grocery Store",
        ),
        confidence={"line_items": 0.82},
        warnings=[],
        persisted=False,
    )


def mock_asr(_filename: str) -> ExtractionResponse:
    """Return a mock ASR transcription result."""
    return ExtractionResponse(
        request_id=uuid4(),
        status=ExtractionStatus.SUCCEEDED,
        provider="MOCK_ASR",
        raw_text="I need to buy two liters of milk and one loaf of bread",
        fields=ExtractionFields(
            ingredient_name="Milk",
            quantity=2.0,
            unit="LITER",
            packaged_at=None,
            expires_at=None,
            price=None,
            currency=None,
            barcode=None,
        ),
        confidence={"transcript": 0.92, "ingredient_name": 0.78},
        warnings=[],
        persisted=False,
    )


def mock_barcode_lookup(barcode: str) -> BarcodeExtractionResponse:
    """Return a mock barcode product lookup result."""
    return BarcodeExtractionResponse(
        request_id=uuid4(),
        status=ExtractionStatus.SUCCEEDED,
        provider="MOCK_BARCODE",
        raw_text=f"Product found for barcode {barcode}",
        fields=BarcodeProductFields(
            barcode=barcode,
            product_name="Whole Milk",
            brand="Dairy Farm",
            category="Dairy",
            ingredient_name="Whole Milk",
            quantity=1.0,
            unit="LITER",
            expires_at=None,
            price=35000.0,
            currency="VND",
        ),
        confidence={"product_name": 0.90},
        warnings=[],
        persisted=False,
    )
