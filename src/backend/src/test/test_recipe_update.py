"""Focused coverage for recipe updates."""

from decimal import Decimal
from unittest.mock import AsyncMock
from uuid import UUID

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.model.recipe_model import RecipeModel
from src.module.recipes.recipe_dto import (
    RecipeDetailDTO,
    RecipeNutritionDTO,
    UpdateRecipeRequestDTO,
)
from src.module.recipes.recipe_service import RecipeService


@pytest.mark.anyio
async def test_update_recipe_changes_only_submitted_fields(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Apply explicit fields, including nullable values, and commit once."""
    recipe_id = UUID("018f0f90-26e6-7ce7-8f61-8769f9e5a099")
    recipe = RecipeModel(
        id=recipe_id,
        name="Old soup",
        description="Keep this description",
        estimated_cost=25_000,
    )
    expected = RecipeDetailDTO(
        id=recipe_id,
        name="Updated soup",
        description=recipe.description,
        media_url=None,
        default_servings=Decimal("2.00"),
        estimated_cooking_minutes=15,
        estimated_cost=None,
        tags={},
        servings=Decimal("2.00"),
        instructions={"steps": []},
        nutrition=RecipeNutritionDTO(
            calories=None,
            protein_g=None,
            fat_g=None,
            carbs_g=None,
            sugar_g=None,
            other_nutrients={},
        ),
        ingredients=[],
    )
    session = AsyncMock(spec=AsyncSession)
    service = RecipeService(session)
    find_recipe = AsyncMock(return_value=recipe)
    get_recipe = AsyncMock(return_value=expected)
    monkeypatch.setattr(service, "_find_recipe", find_recipe)
    monkeypatch.setattr(service, "get_recipe", get_recipe)

    response = await service.update_recipe(
        recipe_id,
        UpdateRecipeRequestDTO(name="  Updated soup  ", estimated_cost=None),
    )

    assert response is expected
    assert recipe.name == "Updated soup"
    assert recipe.description == "Keep this description"
    assert recipe.estimated_cost is None
    find_recipe.assert_awaited_once_with(recipe_id, lock=True)
    session.commit.assert_awaited_once_with()
    session.rollback.assert_not_awaited()
    get_recipe.assert_awaited_once_with(recipe_id, None)
