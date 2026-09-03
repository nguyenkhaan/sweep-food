"""Authenticated mock recommendation route."""

from typing import Annotated

from fastapi import APIRouter, Depends

from src.middleware.auth_middleware import AuthenticatedUser, require_authentication
from src.module.recommendations.recommendation_dependency import (
    get_recommendation_service,
)
from src.module.recommendations.recommendation_dto import (
    RecommendationListResponseDTO,
    RecommendationRequestDTO,
)
from src.module.recommendations.recommendation_service import RecommendationService

recommendation_router = APIRouter(prefix="/recommendations", tags=["recommendations"])


@recommendation_router.post("", response_model=RecommendationListResponseDTO)
async def post_recommendations(
    body: RecommendationRequestDTO,
    user: Annotated[AuthenticatedUser, Depends(require_authentication)],
    service: Annotated[RecommendationService, Depends(get_recommendation_service)],
) -> RecommendationListResponseDTO:
    """Return catalog-backed mock results for one authenticated user request."""
    return await service.recommend(user.user_id, body)
