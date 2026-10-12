"""Unit tests for AI-backed recommendation orchestration."""

from decimal import Decimal
from typing import cast
from uuid import UUID

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.module.recommendations.recommendation_ai_service import (
    RecommendationAIService,
)
from src.module.recommendations.recommendation_dto import RecommendationRequestDTO
from src.service.sweep_food_ai_client import (
    AIRecommendationIngredientDTO,
    AIRecommendationItemDTO,
    AIRecommendationRankingFeaturesDTO,
    AIRecommendationRequestDTO,
    AIRecommendationResponseDTO,
    AIRecommendationTimingsDTO,
    SweepFoodAIClient,
)

USER_ID = UUID("018f0f90-26e6-7ce7-8f61-8769f9e5b101")
RECIPE_ONE_ID = UUID("018f0f90-26e6-7ce7-8f61-8769f9e5b102")
RECIPE_TWO_ID = UUID("018f0f90-26e6-7ce7-8f61-8769f9e5b103")
UNKNOWN_RECIPE_ID = UUID("018f0f90-26e6-7ce7-8f61-8769f9e5b199")


class _Recipe:
    def __init__(self, recipe_id: UUID, name: str) -> None:
        self.id = recipe_id
        self.name = name
        self.media_url = None
        self.estimated_cooking_minutes = 20
        self.default_servings = Decimal(2)
        self.total_calories = Decimal(300)
        self.total_protein_g = Decimal(10)
        self.total_fat_g = Decimal(5)
        self.total_carbs_g = Decimal(30)
        self.total_sugar_g = Decimal(2)
        self.other_nutrients: dict[str, object] = {}


class _Result:
    def __init__(self, value: object) -> None:
        self._value = value

    def scalars(self) -> "_Result":
        return self

    def all(self) -> list[_Recipe]:
        return cast(list[_Recipe], self._value)


class _Session:
    def __init__(
        self,
        *,
        recipes: list[_Recipe],
    ) -> None:
        self._result = _Result(recipes)
        self.statements: list[object] = []

    async def execute(self, statement: object) -> _Result:
        self.statements.append(statement)
        return self._result


class _AIClient:
    def __init__(self, response: AIRecommendationResponseDTO) -> None:
        self.response = response
        self.requests: list[AIRecommendationRequestDTO] = []

    async def recommend(
        self, request: AIRecommendationRequestDTO
    ) -> AIRecommendationResponseDTO:
        self.requests.append(request)
        return self.response


def _ai_item(recipe_id: UUID, rank_score: float) -> AIRecommendationItemDTO:
    return AIRecommendationItemDTO(
        id=recipe_id,
        name="AI display name",
        rank_score=rank_score,
        ranking_features=AIRecommendationRankingFeaturesDTO(
            core_coverage=0.8,
            core_missing_count=1,
            secondary_coverage=0.7,
            shopping_gap_items=1,
            rescue_weight_g=300,
            nutrition_confidence=0.9,
            kcal_per_serving=450,
            protein_per_serving=25,
            prep_complexity=3.2,
        ),
        matched_ingredients=[
            AIRecommendationIngredientDTO(
                name="Spinach",
                code="4001",
                required_g=300,
            )
        ],
        missing_ingredients=[
            AIRecommendationIngredientDTO(
                name="Salt",
                code="13001",
                required_g=5,
            )
        ],
        optional_ingredients=[
            AIRecommendationIngredientDTO(
                name="Pepper",
                code="13002",
                required_g=1,
            )
        ],
        rescued_items=["Spinach"],
        status_badge="ready",
    )


@pytest.mark.anyio
async def test_recommendation_uses_user_pantry_and_preserves_ai_order() -> None:
    session = _Session(
        recipes=[
            _Recipe(RECIPE_ONE_ID, "Backend soup"),
            _Recipe(RECIPE_TWO_ID, "Backend salad"),
        ],
    )
    ai_client = _AIClient(
        AIRecommendationResponseDTO(
            status="success",
            contract_version="2",
            model_version="lgbm-contextual-v1",
            catalog_revision="catalog-test",
            ranker_model="LightGBM LambdaMART",
            timings=AIRecommendationTimingsDTO(
                total_ms=20.1,
                candidate_ms=2.3,
                ranker_ms=4.8,
            ),
            recommendations=[
                _ai_item(RECIPE_TWO_ID, 1.9),
                _ai_item(UNKNOWN_RECIPE_ID, 1.8),
                _ai_item(RECIPE_ONE_ID, 1.7),
            ],
        )
    )
    service = RecommendationAIService(
        cast(AsyncSession, session),
        cast(SweepFoodAIClient, ai_client),
    )

    response = await service.recommend(
        USER_ID,
        RecommendationRequestDTO(
            items=[
                {
                    "name": "Spinach",
                    "code": "4001",
                    "quantity_g": 600,
                    "hours_to_expire": 0,
                }
            ],
            household_size=2,
            max_cooking_time_min=25,
            allergies=["peanut"],
        ),
    )

    request = ai_client.requests[0]
    assert len(request.items) == 1
    assert request.items[0].quantity_g == 600
    assert request.items[0].hours_to_expire == 0
    assert request.items[0].code == "4001"
    assert request.household_size == 2
    assert request.max_cooking_time_min == 25
    assert request.allergies == ["peanut"]
    assert [item.recipe_id for item in response.items] == [
        RECIPE_TWO_ID,
        RECIPE_ONE_ID,
    ]
    assert response.items[0].recipe_name == "Backend salad"
    assert response.items[0].rank_score == 1.9
    assert response.items[0].matched_ingredients[0].code == "4001"
    assert response.items[0].missing_ingredients[0].required_g == 5
    assert response.items[0].optional_ingredients[0].name == "Pepper"
    assert response.items[0].provider == "SWEEP_FOOD_AI"
    assert response.contract_version == "2"
    assert response.ranker_model == "LightGBM LambdaMART"
    assert response.analysis.is_mock is False
    assert f"UNKNOWN_RECIPE_ID:{UNKNOWN_RECIPE_ID}" in response.warnings
    assert len(session.statements) == 1


@pytest.mark.anyio
async def test_empty_pantry_and_empty_ai_result_are_explicit() -> None:
    session = _Session(recipes=[])
    ai_client = _AIClient(
        AIRecommendationResponseDTO(
            status="empty",
            contract_version="2",
            model_version="lgbm-contextual-v1",
            catalog_revision="catalog-test",
            ranker_model="LightGBM LambdaMART",
            timings=AIRecommendationTimingsDTO(
                total_ms=1,
                candidate_ms=1,
                ranker_ms=0,
            ),
            recommendations=[],
        )
    )
    service = RecommendationAIService(
        cast(AsyncSession, session),
        cast(SweepFoodAIClient, ai_client),
    )

    response = await service.recommend(
        USER_ID,
        RecommendationRequestDTO(items=[]),
    )

    assert ai_client.requests[0].items == []
    assert response.items == []
    assert response.analysis.is_mock is False
    assert len(session.statements) == 0
