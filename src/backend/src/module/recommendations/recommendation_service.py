"""Catalog-backed mock response for the future recommendation AI boundary."""

from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.model.recipe_model import RecipeModel
from src.module.recommendations.recommendation_dto import (
    MockRecommendationAnalysisDTO,
    RecommendationItemDTO,
    RecommendationListResponseDTO,
    RecommendationRankingFeaturesDTO,
    RecommendationRequestDTO,
    RecommendationTimingsDTO,
)
from src.module.recommendations.recommendation_mapper import to_recipe_summary


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
            request=body,
            contract_version="2",
            model_version="mock-v2",
            catalog_revision="mock-catalog",
            ranker_model="Deterministic Mock",
            timings=RecommendationTimingsDTO(
                total_ms=0,
                candidate_ms=0,
                ranker_ms=0,
            ),
            analysis=MockRecommendationAnalysisDTO(
                intent="meal_recommendation",
                summary=(
                    "Mock analysis is active while the production AI provider "
                    "is being integrated."
                ),
                is_mock=True,
            ),
            items=[
                self._to_item(recipe, rank) for rank, recipe in enumerate(recipes, 1)
            ],
        )

    @staticmethod
    def _to_item(recipe: RecipeModel, rank: int) -> RecommendationItemDTO:
        """Map one real catalog recipe to a stable mock ranking response."""
        return RecommendationItemDTO(
            recipe_id=recipe.id,
            recipe_name=recipe.name,
            rank=rank,
            rank_score=float(6 - rank),
            ranking_features=RecommendationRankingFeaturesDTO(
                core_coverage=0,
                core_missing_count=0,
                secondary_coverage=0,
                shopping_gap_items=0,
                rescue_weight_g=0,
                nutrition_confidence=0,
                kcal_per_serving=0,
                protein_per_serving=0,
                prep_complexity=0,
            ),
            matched_ingredients=[],
            missing_ingredients=[],
            optional_ingredients=[],
            rescued_items=[],
            status_badge="mock",
            explanation="Deterministic mock ordering; no AI inference was performed.",
            provider="MOCK",
            recipe_summary=to_recipe_summary(recipe),
        )
