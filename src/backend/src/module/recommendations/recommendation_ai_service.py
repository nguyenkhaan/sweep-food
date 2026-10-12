"""AI-backed recommendation orchestration for authenticated users."""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.model.recipe_model import RecipeModel
from src.module.recommendations.recommendation_dto import (
    MockRecommendationAnalysisDTO,
    RecommendationIngredientDTO,
    RecommendationItemDTO,
    RecommendationListResponseDTO,
    RecommendationRankingFeaturesDTO,
    RecommendationRequestDTO,
    RecommendationTimingsDTO,
)
from src.module.recommendations.recommendation_mapper import to_recipe_summary
from src.service.sweep_food_ai_client import (
    AIRecommendationItemDTO,
    AIRecommendationRequestDTO,
    SweepFoodAIClient,
)


class RecommendationAIService:
    """Forward structured requests and map AI rankings to backend recipes."""

    def __init__(self, db_session: AsyncSession, ai_client: SweepFoodAIClient) -> None:
        self._db_session = db_session
        self._ai_client = ai_client

    async def recommend(
        self,
        _user_id: UUID,
        body: RecommendationRequestDTO,
    ) -> RecommendationListResponseDTO:
        """Return calibrated AI rankings backed by the backend recipe catalog."""
        ai_response = await self._ai_client.recommend(
            AIRecommendationRequestDTO.model_validate(body.model_dump())
        )

        warnings: list[str] = []
        recipes = await self._load_recipes(
            [recommendation.id for recommendation in ai_response.recommendations]
        )
        recipe_by_id = {recipe.id: recipe for recipe in recipes}
        items: list[RecommendationItemDTO] = []
        for recommendation in ai_response.recommendations:
            recipe = recipe_by_id.get(recommendation.id)
            if recipe is None:
                warnings.append(f"UNKNOWN_RECIPE_ID:{recommendation.id}")
                continue
            items.append(
                self._map_recommendation(
                    recommendation,
                    recipe,
                    rank=len(items) + 1,
                )
            )

        return RecommendationListResponseDTO(
            request=body,
            contract_version=ai_response.contract_version,
            model_version=ai_response.model_version,
            catalog_revision=ai_response.catalog_revision,
            ranker_model=ai_response.ranker_model,
            timings=RecommendationTimingsDTO(**ai_response.timings.model_dump()),
            analysis=MockRecommendationAnalysisDTO(
                intent="meal_recommendation",
                summary=(
                    "Recommendations were ranked from the supplied pantry and "
                    "preferences."
                ),
                is_mock=False,
            ),
            items=items,
            warnings=warnings,
        )

    async def _load_recipes(self, recipe_ids: list[UUID]) -> list[RecipeModel]:
        if not recipe_ids:
            return []
        result = await self._db_session.execute(
            select(RecipeModel).where(RecipeModel.id.in_(recipe_ids))
        )
        return list(result.scalars().all())

    @staticmethod
    def _map_recommendation(
        recommendation: AIRecommendationItemDTO,
        recipe: RecipeModel,
        *,
        rank: int,
    ) -> RecommendationItemDTO:
        return RecommendationItemDTO(
            recipe_id=recipe.id,
            recipe_name=recipe.name,
            rank=rank,
            rank_score=recommendation.rank_score,
            ranking_features=RecommendationRankingFeaturesDTO(
                **recommendation.ranking_features.model_dump()
            ),
            matched_ingredients=[
                RecommendationIngredientDTO(**item.model_dump())
                for item in recommendation.matched_ingredients
            ],
            missing_ingredients=[
                RecommendationIngredientDTO(**item.model_dump())
                for item in recommendation.missing_ingredients
            ],
            optional_ingredients=[
                RecommendationIngredientDTO(**item.model_dump())
                for item in recommendation.optional_ingredients
            ],
            rescued_items=recommendation.rescued_items,
            status_badge=recommendation.status_badge,
            explanation="AI-ranked from pantry availability, expiry, and shopping gaps.",
            provider="SWEEP_FOOD_AI",
            recipe_summary=to_recipe_summary(recipe),
        )
