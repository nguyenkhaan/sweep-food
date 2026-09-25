"""Authenticated rating submission and administrator read routes."""

from typing import Annotated

from fastapi import APIRouter, Body, Depends, Query, status

from src.middleware.auth_middleware import AuthenticatedUser, require_authentication
from src.middleware.role_middleware import require_role
from src.model.enum_model import UserRole
from src.module.rating.rating_dependency import get_rating_service
from src.module.rating.rating_dto import (
    RatingAverageResponseDTO,
    RatingDTO,
    RatingFeedbackListResponseDTO,
    RatingFeedbackRequestDTO,
)
from src.module.rating.rating_service import RatingService

rating_router = APIRouter(prefix="/rating", tags=["rating"])


@rating_router.post(
    "",
    response_model=RatingDTO,
    status_code=status.HTTP_201_CREATED,
)
async def post_rating(
    user: Annotated[AuthenticatedUser, Depends(require_authentication)],
    service: Annotated[RatingService, Depends(get_rating_service)],
    rating: Annotated[
        float,
        Query(ge=1, le=5, allow_inf_nan=False),
    ],
    body: Annotated[RatingFeedbackRequestDTO | None, Body()] = None,
) -> RatingDTO:
    """Append one rating for the authenticated user."""
    return await service.create_rating(user.user_id, rating, body)


@rating_router.get(
    "/admin/feedback",
    response_model=RatingFeedbackListResponseDTO,
)
async def get_admin_feedback(
    _admin: Annotated[AuthenticatedUser, Depends(require_role(UserRole.ADMIN))],
    service: Annotated[RatingService, Depends(get_rating_service)],
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> RatingFeedbackListResponseDTO:
    """Return a stable page of feedback and the overall average to administrators."""
    return await service.list_feedback(limit, offset)


@rating_router.get(
    "/admin/average",
    response_model=RatingAverageResponseDTO,
)
async def get_admin_average(
    _admin: Annotated[AuthenticatedUser, Depends(require_role(UserRole.ADMIN))],
    service: Annotated[RatingService, Depends(get_rating_service)],
) -> RatingAverageResponseDTO:
    """Return only the application-wide average to administrators."""
    return await service.get_average()
