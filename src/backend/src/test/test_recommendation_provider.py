"""Small tests for the deterministic mock recommendation response."""

from decimal import Decimal
from typing import cast
from uuid import UUID

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.module.recommendations.recommendation_dto import RecommendationRequestDTO
from src.module.recommendations.recommendation_service import RecommendationService


class FakeRecipe:
    """Contain only the public recipe fields used by a mock ranking."""

    id: UUID
    name: str
    default_servings: Decimal
    estimated_cooking_minutes: int

    def __init__(self, recipe_id: UUID, name: str) -> None:
        self.id = recipe_id
        self.name = name
        self.default_servings = Decimal(2)
        self.estimated_cooking_minutes = 20


class FakeScalarResult:
    """Expose the scalar collection returned by a recipe query."""

    def __init__(self, recipes: list[FakeRecipe]) -> None:
        self.recipes = recipes

    def all(self) -> list[FakeRecipe]:
        """Return the supplied recipe records."""
        return self.recipes


class FakeResult:
    """Provide the SQLAlchemy scalar result shape used by the service."""

    def __init__(self, recipes: list[FakeRecipe]) -> None:
        self.recipes = recipes

    def scalars(self) -> FakeScalarResult:
        """Return the recipe collection wrapper."""
        return FakeScalarResult(self.recipes)


class FakeSession:
    """Return seeded-like recipe records without database I/O."""

    async def execute(self, _statement: object) -> FakeResult:
        """Return the deterministic test recipes."""
        return FakeResult(
            [
                FakeRecipe(UUID("018f0f90-26e6-7ce7-8f61-8769f9e5b102"), "Soup"),
                FakeRecipe(UUID("018f0f90-26e6-7ce7-8f61-8769f9e5b103"), "Rice"),
            ]
        )


@pytest.mark.anyio
async def test_mock_recommendations_are_ranked_and_keep_real_recipe_ids() -> None:
    """Mock scores remain deterministic while recipes come from the catalog query."""
    service = RecommendationService(cast(AsyncSession, FakeSession()))

    response = await service.recommend(
        UUID("018f0f90-26e6-7ce7-8f61-8769f9e5b101"),
        RecommendationRequestDTO(request="Món nhanh"),
    )

    assert [item.rank for item in response.items] == [1, 2]
    assert response.items[0].recipe_name == "Soup"
    assert response.items[0].provider == "MOCK"
