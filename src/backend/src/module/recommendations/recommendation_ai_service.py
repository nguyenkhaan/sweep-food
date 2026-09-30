"""AI-backed recommendation orchestration for authenticated users."""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.model.enum_model import MeasurementUnit
from src.model.recipe_model import RecipeModel
from src.module.recommendations.recommendation_dto import (
    MockRecommendationAnalysisDTO,
    RecommendationItemDTO,
    RecommendationListResponseDTO,
    RecommendationMissingIngredientDTO,
    RecommendationRequestDTO,
    RecommendationScoreComponentsDTO,
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
                    model_version=ai_response.model_version,
                )
            )

        return RecommendationListResponseDTO(
            request=body,
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
        model_version: str,
    ) -> RecommendationItemDTO:
        return RecommendationItemDTO(
            recipe_id=recipe.id,
            recipe_name=recipe.name,
            rank=rank,
            score=recommendation.score,
            score_components=RecommendationScoreComponentsDTO(
                **recommendation.score_components.model_dump()
            ),
            missing_ingredients=[
                RecommendationMissingIngredientDTO(
                    master_ingredient_id=_uuid_or_none(item.code),
                    name=item.name,
                    quantity=item.required_g,
                    unit=MeasurementUnit.GRAM,
                )
                for item in recommendation.missing_ingredients
            ],
            near_expiry_ingredients=recommendation.rescued_items,
            explanation=(
                f"Ranked by {model_version} from pantry availability, expiry, "
                "preferences, and missing purchases."
            ),
            provider="SWEEP_FOOD_AI",
            model_version=model_version,
            recipe_summary=to_recipe_summary(recipe),
        )


def _uuid_or_none(value: str | None) -> UUID | None:
    if value is None:
        return None
    try:
        return UUID(value)
    except ValueError:
        return None
