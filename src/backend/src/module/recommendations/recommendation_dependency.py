"""Dependencies for the temporary recommendation API contract adapter."""

from src.module.recommendations.recommendation_mock_service import (
    RecommendationResponseService,
    TemporaryMockRecommendationService,
)


def get_recommendation_response_service() -> RecommendationResponseService:
    """Return the temporary adapter until the real integration is available."""
    return TemporaryMockRecommendationService()
