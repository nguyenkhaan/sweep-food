"""Authenticated cooking preview, completion, leftover, and history API routes."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Header, status

from src.middleware.auth_middleware import AuthenticatedUser, require_authentication
from src.module.cooking.cooking_dependency import get_cooking_service
from src.module.cooking.cooking_dto import (
    CompleteCookingSessionRequestDTO,
    CookedLeftoverResponseDTO,
    CookingCompletionResponseDTO,
    CookingHistoryDetailResponseDTO,
    CookingHistoryListResponseDTO,
    CookingPreviewRequestDTO,
    CookingPreviewResponseDTO,
    CookingSessionDTO,
    CreateCookedLeftoverRequestDTO,
    CreateCookingSessionRequestDTO,
)
from src.module.cooking.cooking_service import CookingService

cooking_router = APIRouter(prefix="/cooking", tags=["cooking"])


@cooking_router.post(
    "/preview",
    response_model=CookingPreviewResponseDTO,
    summary="Preview cooking allocation",
    description=(
        "Derive recipe and servings from an owned meal-plan item, then propose FEFO "
        "batch deductions without writing inventory, ledger, or cooking-session data."
    ),
)
async def post_cooking_preview(
    body: CookingPreviewRequestDTO,
    user: Annotated[AuthenticatedUser, Depends(require_authentication)],
    service: Annotated[CookingService, Depends(get_cooking_service)],
) -> CookingPreviewResponseDTO:
    """Return an ownership-safe, read-only preview for one planned meal."""
    return await service.preview(user.user_id, body)


@cooking_router.post(
    "/sessions",
    response_model=CookingSessionDTO,
    status_code=status.HTTP_201_CREATED,
    summary="Create a planned cooking session",
    description=(
        "Derive recipe and servings from an owned meal-plan item, then create a "
        "cooking session without deducting inventory. Use the returned session ID "
        "when confirming completion."
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


@cooking_router.post(
    "/sessions/{session_id}/leftovers",
    response_model=CookedLeftoverResponseDTO,
    status_code=status.HTTP_201_CREATED,
    summary="Create a cooked-food leftover batch",
    description=(
        "Save remaining cooked food from a completed cooking session as a new "
        "COOKED_FOOD inventory batch with optional expiry and note."
    ),
)
async def post_cooked_leftover(
    session_id: UUID,
    body: CreateCookedLeftoverRequestDTO,
    user: Annotated[AuthenticatedUser, Depends(require_authentication)],
    service: Annotated[CookingService, Depends(get_cooking_service)],
) -> CookedLeftoverResponseDTO:
    """Create a leftover batch linked to a completed cooking session."""
    return await service.create_leftover(user.user_id, session_id, body)


@cooking_router.get(
    "/history",
    response_model=CookingHistoryListResponseDTO,
    summary="List cooking history",
    description=(
        "Return all completed cooking sessions for the authenticated user, "
        "ordered by most recently completed."
    ),
)
async def get_cooking_history(
    user: Annotated[AuthenticatedUser, Depends(require_authentication)],
    service: Annotated[CookingService, Depends(get_cooking_service)],
) -> CookingHistoryListResponseDTO:
    """Return the user's completed cooking session history."""
    return await service.get_cooking_history(user.user_id)


@cooking_router.get(
    "/history/{session_id}",
    response_model=CookingHistoryDetailResponseDTO,
    summary="Get cooking history detail",
    description=(
        "Return one completed cooking session with its recipe, "
        "consumption records, and linked leftover batch."
    ),
)
async def get_cooking_history_detail(
    session_id: UUID,
    user: Annotated[AuthenticatedUser, Depends(require_authentication)],
    service: Annotated[CookingService, Depends(get_cooking_service)],
) -> CookingHistoryDetailResponseDTO:
    """Return detail of one completed cooking session for the authenticated user."""
    return await service.get_cooking_history_detail(user.user_id, session_id)
