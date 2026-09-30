"""Authenticated experimental extraction API routes."""

from typing import Annotated, Any

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status

from src.core.exceptions import ErrorResponseDTO
from src.middleware.auth_middleware import AuthenticatedUser, require_authentication
from src.module.extractions.extraction_dependency import get_extraction_service
from src.module.extractions.extraction_dto import (
    BarcodeExtractionResponse,
    ExtractionResponse,
    InvoiceExtractionResponse,
)
from src.module.extractions.extraction_service import (
    ExtractionService,
    ExtractionValidationError,
    extract_barcode,
)

extraction_router = APIRouter(prefix="/extractions", tags=["extractions"])
EXTRACTION_VALIDATION_RESPONSES: dict[int | str, dict[str, Any]] = {
    status.HTTP_502_BAD_GATEWAY: {"model": ErrorResponseDTO},
    status.HTTP_503_SERVICE_UNAVAILABLE: {"model": ErrorResponseDTO},
    status.HTTP_504_GATEWAY_TIMEOUT: {"model": ErrorResponseDTO},
    status.HTTP_422_UNPROCESSABLE_CONTENT: {"model": ErrorResponseDTO},
}


@extraction_router.post(
    "/ocr/label",
    response_model=ExtractionResponse,
    summary="Extract product label from image",
    description=(
        "Accept a product label image and return extracted ingredient "
        "fields. No inventory records are created."
    ),
    responses=EXTRACTION_VALIDATION_RESPONSES,
)
async def post_ocr_label(
    file: Annotated[UploadFile, File()],
    _user: Annotated[AuthenticatedUser, Depends(require_authentication)],
    service: Annotated[ExtractionService, Depends(get_extraction_service)],
) -> ExtractionResponse:
    """Extract ingredient information from a product label image."""
    try:
        return await service.extract_ocr_label(file)
    except ExtractionValidationError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=exc.detail,
        ) from exc


@extraction_router.post(
    "/ocr/invoice",
    response_model=InvoiceExtractionResponse,
    summary="Extract invoice line items from image",
    description=(
        "Accept an invoice image and return extracted line items. "
        "No inventory records are created."
    ),
    responses=EXTRACTION_VALIDATION_RESPONSES,
)
async def post_ocr_invoice(
    file: Annotated[UploadFile, File()],
    _user: Annotated[AuthenticatedUser, Depends(require_authentication)],
    service: Annotated[ExtractionService, Depends(get_extraction_service)],
) -> InvoiceExtractionResponse:
    """Extract line items from an invoice image."""
    try:
        return await service.extract_ocr_invoice(file)
    except ExtractionValidationError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=exc.detail,
        ) from exc


@extraction_router.post(
    "/asr",
    response_model=ExtractionResponse,
    summary="Transcribe voice and extract ingredient fields",
    description=(
        "Accept an audio file and return transcription with parsed "
        "ingredient fields. No inventory records are created."
    ),
    responses=EXTRACTION_VALIDATION_RESPONSES,
)
async def post_asr(
    file: Annotated[UploadFile, File()],
    _user: Annotated[AuthenticatedUser, Depends(require_authentication)],
    service: Annotated[ExtractionService, Depends(get_extraction_service)],
) -> ExtractionResponse:
    """Transcribe audio and extract ingredient fields."""
    try:
        return await service.extract_asr(file)
    except ExtractionValidationError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=exc.detail,
        ) from exc


@extraction_router.post(
    "/barcode",
    response_model=BarcodeExtractionResponse,
    summary="Look up product by barcode",
    description=(
        "Accept a barcode value and return product metadata. "
        "No inventory records are created."
    ),
)
async def post_barcode(
    barcode: str,
    _user: Annotated[AuthenticatedUser, Depends(require_authentication)],
) -> BarcodeExtractionResponse:
    """Look up product information by barcode value."""
    return extract_barcode(barcode)
