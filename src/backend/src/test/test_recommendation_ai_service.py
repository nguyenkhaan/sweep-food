"""Unit tests for AI-backed recommendation orchestration."""

from datetime import UTC, datetime, timedelta
from decimal import Decimal
from typing import cast
from uuid import UUID

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.model.enum_model import MeasurementUnit
from src.module.recommendations.recommendation_ai_service import (
    RecommendationAIService,
)
from src.module.recommendations.recommendation_dto import RecommendationRequestDTO
from src.service.sweep_food_ai_client import (
    AIRecommendationItemDTO,
    AIRecommendationRequestDTO,
    AIRecommendationResponseDTO,
    AIRecommendationScoreComponentsDTO,
    SweepFoodAIClient,
)

USER_ID = UUID("018f0f90-26e6-7ce7-8f61-8769f9e5b101")
INGREDIENT_ID = UUID("018f0f90-26e6-7ce7-8f61-8769f9e5b110")
RECIPE_ONE_ID = UUID("018f0f90-26e6-7ce7-8f61-8769f9e5b102")
RECIPE_TWO_ID = UUID("018f0f90-26e6-7ce7-8f61-8769f9e5b103")
UNKNOWN_RECIPE_ID = UUID("018f0f90-26e6-7ce7-8f61-8769f9e5b199")


class _Batch:
    def __init__(
        self,
        batch_id: UUID,
        *,
        quantity: float,
        unit: MeasurementUnit,
        expires_at: datetime | None,
        master_ingredient_id: UUID | None = INGREDIENT_ID,
        custom_name: str | None = None,
    ) -> None:
        self.id = batch_id
        self.current_quantity = quantity
        self.unit = unit
        self.expires_at = expires_at
        self.master_ingredient_id = master_ingredient_id
        self.custom_name = custom_name


class _Ingredient:
    name = "Spinach"


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

    def scalar_one_or_none(self) -> object:
        return self._value

    def all(self) -> list[tuple[_Batch, _Ingredient | None]]:
        return cast(list[tuple[_Batch, _Ingredient | None]], self._value)

    def scalars(self) -> "_Result":
        return self

    def __iter__(self) -> object:
        return iter(cast(list[object], self._value))


class _Session:
    def __init__(
        self,
        *,
        preferences: dict[str, object],
        inventory: list[tuple[_Batch, _Ingredient | None]],
        recipes: list[_Recipe],
    ) -> None:
        self._results = iter(
            [_Result(preferences), _Result(inventory), _Result(recipes)]
        )
        self.statements: list[object] = []

    async def execute(self, statement: object) -> _Result:
        self.statements.append(statement)
        return next(self._results)


class _AIClient:
    def __init__(self, response: AIRecommendationResponseDTO) -> None:
        self.response = response
        self.requests: list[AIRecommendationRequestDTO] = []

    async def recommend(
        self, request: AIRecommendationRequestDTO
    ) -> AIRecommendationResponseDTO:
        self.requests.append(request)
        return self.response


def _ai_item(recipe_id: UUID, score: float) -> AIRecommendationItemDTO:
    return AIRecommendationItemDTO(
        id=recipe_id,
        name="AI display name",
        score=score,
        score_components=AIRecommendationScoreComponentsDTO(
            expiration_utilization=0.8,
            availability=0.7,
            preference_fit=1.0,
            purchase_minimization=0.6,
        ),
        missing_ingredients=[],
        rescued_items=["Spinach"],
    )


@pytest.mark.anyio
async def test_recommendation_uses_user_pantry_and_preserves_ai_order() -> None:
    now = datetime.now(UTC)
    unsupported_id = UUID("018f0f90-26e6-7ce7-8f61-8769f9e5b120")
    session = _Session(
        preferences={
            "household_size": 2,
            "max_cooking_time_min": 25,
            "allergies": ["peanut"],
            "preferred_cuisines": ["Vietnamese"],
        },
        inventory=[
            (
                _Batch(
                    UUID("018f0f90-26e6-7ce7-8f61-8769f9e5b111"),
                    quantity=100,
                    unit=MeasurementUnit.GRAM,
                    expires_at=now + timedelta(hours=12),
                ),
                _Ingredient(),
            ),
            (
                _Batch(
                    UUID("018f0f90-26e6-7ce7-8f61-8769f9e5b112"),
                    quantity=0.5,
                    unit=MeasurementUnit.KG,
                    expires_at=now - timedelta(hours=1),
                ),
                _Ingredient(),
            ),
            (
                _Batch(
                    unsupported_id,
                    quantity=1,
                    unit=MeasurementUnit.LITER,
                    expires_at=None,
                    master_ingredient_id=None,
                    custom_name="Milk",
                ),
                None,
            ),
        ],
        recipes=[
            _Recipe(RECIPE_ONE_ID, "Backend soup"),
            _Recipe(RECIPE_TWO_ID, "Backend salad"),
        ],
    )
    ai_client = _AIClient(
        AIRecommendationResponseDTO(
            status="success",
            model_version="xgboost-test",
            catalog_revision="catalog-test",
            recommendations=[
                _ai_item(RECIPE_TWO_ID, 0.9),
                _ai_item(UNKNOWN_RECIPE_ID, 0.8),
                _ai_item(RECIPE_ONE_ID, 0.7),
            ],
        )
    )
    service = RecommendationAIService(
        cast(AsyncSession, session),
        cast(SweepFoodAIClient, ai_client),
    )

    response = await service.recommend(
        USER_ID,
        RecommendationRequestDTO(request="Món nhanh"),
    )

    request = ai_client.requests[0]
    assert len(request.items) == 1
    assert request.items[0].quantity_g == 600
    assert request.items[0].hours_to_expire == 0
    assert request.items[0].code == str(INGREDIENT_ID)
    assert request.household_size == 2
    assert request.max_cooking_time_min == 25
    assert request.allergies == ["peanut"]
    assert [item.recipe_id for item in response.items] == [
        RECIPE_TWO_ID,
        RECIPE_ONE_ID,
    ]
    assert response.items[0].recipe_name == "Backend salad"
    assert response.items[0].provider == "SWEEP_FOOD_AI"
    assert response.analysis.is_mock is False
    assert f"UNSUPPORTED_UNIT:{unsupported_id}:LITER" in response.warnings
    assert f"UNKNOWN_RECIPE_ID:{UNKNOWN_RECIPE_ID}" in response.warnings
    assert "inventory_batches.user_id" in str(session.statements[1])


@pytest.mark.anyio
async def test_empty_pantry_and_empty_ai_result_are_explicit() -> None:
    session = _Session(preferences={}, inventory=[], recipes=[])
    ai_client = _AIClient(
        AIRecommendationResponseDTO(
            status="empty",
            model_version="xgboost-test",
            catalog_revision="catalog-test",
            recommendations=[],
        )
    )
    service = RecommendationAIService(
        cast(AsyncSession, session),
        cast(SweepFoodAIClient, ai_client),
    )

    response = await service.recommend(
        USER_ID,
        RecommendationRequestDTO(request="Tối nay ăn gì?"),
    )

    assert ai_client.requests[0].items == []
    assert response.items == []
    assert response.analysis.is_mock is False
    assert len(session.statements) == 2
