"""Authenticated read-only cooking preview API route."""

from typing import Annotated

from fastapi import APIRouter, Depends

from src.middleware.auth_middleware import AuthenticatedUser, require_authentication
from src.module.cooking.cooking_dependency import get_cooking_service
from src.module.cooking.cooking_dto import (
    CookingPreviewRequestDTO,
    CookingPreviewResponseDTO,
)
from src.module.cooking.cooking_service import CookingService

cooking_router = APIRouter(prefix="/cooking", tags=["cooking"])


@cooking_router.post(
    "/preview",
    response_model=CookingPreviewResponseDTO,
    summary="Preview cooking allocation",
    description=(
        "Scale a recipe and propose FEFO batch deductions without writing inventory, "
        "ledger, or cooking-session data."
    ),
)
async def post_cooking_preview(
    body: CookingPreviewRequestDTO,
    user: Annotated[AuthenticatedUser, Depends(require_authentication)],
    service: Annotated[CookingService, Depends(get_cooking_service)],
) -> CookingPreviewResponseDTO:
    """Return an ownership-safe, read-only cooking proposal."""
    return await service.preview(user.user_id, body)
