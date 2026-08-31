"""Authenticated read-only cooking preview API route."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Header, status

from src.middleware.auth_middleware import AuthenticatedUser, require_authentication
from src.module.cooking.cooking_dependency import get_cooking_service
from src.module.cooking.cooking_dto import (
    CompleteCookingSessionRequestDTO,
    CookingCompletionResponseDTO,
    CookingPreviewRequestDTO,
    CookingPreviewResponseDTO,
    CookingSessionDTO,
    CreateCookingSessionRequestDTO,
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


@cooking_router.post(
    "/sessions",
    response_model=CookingSessionDTO,
    status_code=status.HTTP_201_CREATED,
    summary="Create a planned cooking session",
    description=(
        "Create a user-owned cooking session without deducting inventory. "
        "Use the returned session ID when confirming completion."
    ),
)
async def post_cooking_session(
    body: CreateCookingSessionRequestDTO,
    user: Annotated[AuthenticatedUser, Depends(require_authentication)],
    service: Annotated[CookingService, Depends(get_cooking_service)],
) -> CookingSessionDTO:
    """Create a planned cooking session for the authenticated user."""
    return await service.create_session(user.user_id, body)


@cooking_router.post(
    "/sessions/{session_id}/complete",
    response_model=CookingCompletionResponseDTO,
    summary="Complete a cooking session",
    description=(
        "Revalidate and lock FEFO batches, then atomically record consumption, "
        "inventory deductions, and immutable ledger entries."
    ),
)
async def post_complete_cooking_session(
    session_id: UUID,
    body: CompleteCookingSessionRequestDTO,
    user: Annotated[AuthenticatedUser, Depends(require_authentication)],
    service: Annotated[CookingService, Depends(get_cooking_service)],
    idempotency_key: Annotated[str, Header(alias="Idempotency-Key", min_length=1)],
) -> CookingCompletionResponseDTO:
    """Complete a cooking session exactly once for one idempotency key."""
    return await service.complete_session(
        user.user_id,
        session_id,
        idempotency_key,
        body,
    )
