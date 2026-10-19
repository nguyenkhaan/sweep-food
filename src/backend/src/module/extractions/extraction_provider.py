"""Mock extraction providers that return deterministic sample data."""

from uuid import uuid4

from src.module.extractions.extraction_dto import (
    BarcodeExtractionResponse,
    BarcodeProductFields,
    ExtractionStatus,
)


def mock_barcode_lookup(barcode: str) -> BarcodeExtractionResponse:
    """Return a mock barcode product lookup result."""
    if barcode == "unknown-barcode":
        return BarcodeExtractionResponse(
            request_id=uuid4(),
            status=ExtractionStatus.FAILED,
            provider="MOCK_BARCODE",
            raw_text=f"No mock product found for barcode {barcode}",
            fields=BarcodeProductFields(barcode=barcode),
            confidence={},
            warnings=["No mock product was found for this barcode."],
            persisted=False,
        )
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
