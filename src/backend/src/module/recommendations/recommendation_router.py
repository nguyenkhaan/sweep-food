"""Authenticated recommendation API contract route."""

from typing import Annotated

from fastapi import APIRouter, Depends

from src.middleware.auth_middleware import AuthenticatedUser, require_authentication
from src.module.recommendations.recommendation_dependency import (
    get_recommendation_response_service,
)
from src.module.recommendations.recommendation_dto import (
    RecommendationListResponseDTO,
    RecommendationRequestDTO,
)
from src.module.recommendations.recommendation_mock_service import (
    RecommendationResponseService,
)

recommendation_router = APIRouter(prefix="/recommendations", tags=["recommendations"])


@recommendation_router.post(
    "",
    response_model=RecommendationListResponseDTO,
    summary="Return ranked recipe recommendations",
    description=(
        "Return three to five explainable ranked recipes for the authenticated user."
    ),
)
async def post_recommendations(
    body: RecommendationRequestDTO,
    user: Annotated[AuthenticatedUser, Depends(require_authentication)],
    service: Annotated[
        RecommendationResponseService,
        Depends(get_recommendation_response_service),
    ],
) -> RecommendationListResponseDTO:
    """Return the currently configured recommendation response adapter result."""
    return await service.recommend(user, body)
