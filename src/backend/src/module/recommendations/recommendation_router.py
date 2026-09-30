"""Authenticated AI recommendation route."""

from typing import Annotated, Any

from fastapi import APIRouter, Depends, status

from src.core.exceptions import ErrorResponseDTO
from src.middleware.auth_middleware import AuthenticatedUser, require_authentication
from src.module.recommendations.recommendation_ai_service import RecommendationAIService
from src.module.recommendations.recommendation_dependency import (
    get_recommendation_service,
)
from src.module.recommendations.recommendation_dto import (
    RecommendationListResponseDTO,
    RecommendationRequestDTO,
)

recommendation_router = APIRouter(prefix="/recommendations", tags=["recommendations"])

_AI_ERROR_RESPONSES: dict[int | str, dict[str, Any]] = {
    status.HTTP_502_BAD_GATEWAY: {"model": ErrorResponseDTO},
    status.HTTP_503_SERVICE_UNAVAILABLE: {"model": ErrorResponseDTO},
    status.HTTP_504_GATEWAY_TIMEOUT: {"model": ErrorResponseDTO},
}


@recommendation_router.post(
    "",
    response_model=RecommendationListResponseDTO,
    responses=_AI_ERROR_RESPONSES,
)
async def post_recommendations(
    body: RecommendationRequestDTO,
    user: Annotated[AuthenticatedUser, Depends(require_authentication)],
    service: Annotated[RecommendationAIService, Depends(get_recommendation_service)],
) -> RecommendationListResponseDTO:
    """Return catalog-backed AI results for one authenticated user request."""
    return await service.recommend(user.user_id, body)
