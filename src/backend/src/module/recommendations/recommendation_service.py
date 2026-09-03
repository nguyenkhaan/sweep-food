"""Catalog-backed mock response for the future recommendation AI boundary."""

from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.model.recipe_model import RecipeModel
from src.module.recommendations.recommendation_dto import (
    MockRecommendationAnalysisDTO,
    RecommendationItemDTO,
    RecommendationListResponseDTO,
    RecommendationRequestDTO,
    RecommendationScoreComponentsDTO,
)


class RecommendationService:
    """Return deterministic mock rankings using real seeded recipe identities."""

    def __init__(self, db_session: AsyncSession) -> None:
        self.db_session = db_session

    async def recommend(
        self,
        _user_id: UUID,
        body: RecommendationRequestDTO,
    ) -> RecommendationListResponseDTO:
        """Read up to five recipes without persisting the user's free-text request."""
        result = await self.db_session.execute(
            select(RecipeModel)
            .order_by(func.lower(RecipeModel.name), RecipeModel.id)
            .limit(5),
        )
        recipes = list(result.scalars().all())
        return RecommendationListResponseDTO(
            request=body.request,
            analysis=MockRecommendationAnalysisDTO(
                intent="meal_recommendation",
                summary=(
                    "Mock analysis is active while the production AI provider "
                    "is being integrated."
                ),
                is_mock=True,
            ),
            items=[self._to_item(recipe, rank) for rank, recipe in enumerate(recipes, 1)],
        )

    @staticmethod
    def _to_item(recipe: RecipeModel, rank: int) -> RecommendationItemDTO:
        """Map one real catalog recipe to a stable mock ranking response."""
        expiration_utilization = max(0.5, 0.9 - (rank - 1) * 0.08)
        availability = max(0.5, 0.85 - (rank - 1) * 0.07)
        preference_fit = 0.75
        purchase_minimization = max(0.5, 0.8 - (rank - 1) * 0.05)
        score = (
            0.4 * expiration_utilization
            + 0.3 * availability
            + 0.2 * preference_fit
            + 0.1 * purchase_minimization
        )
        return RecommendationItemDTO(
            recipe_id=recipe.id,
            recipe_name=recipe.name,
            rank=rank,
            score=round(score, 3),
            score_components=RecommendationScoreComponentsDTO(
                expiration_utilization=expiration_utilization,
                availability=availability,
                preference_fit=preference_fit,
                purchase_minimization=purchase_minimization,
            ),
            missing_ingredients=[],
            near_expiry_ingredients=[],
            explanation=(
                "Mock score preserves the E/A/P/U response contract; live inventory "
                "analysis will be supplied by the production AI provider."
            ),
            provider="MOCK",
            model_version="mock-v1",
        )
