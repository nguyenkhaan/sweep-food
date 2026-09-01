"""Read-only seeded recipe query service."""

from decimal import Decimal
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.elements import ColumnElement
from sqlalchemy.sql.functions import count

from src.model.master_ingredient_model import MasterIngredientModel
from src.model.recipe_ingredient_model import RecipeIngredientModel
from src.model.recipe_model import RecipeModel
from src.module.recipes.recipe_dto import (
    RecipeDetailDTO,
    RecipeIngredientDTO,
    RecipeListItemDTO,
    RecipeListResponseDTO,
    RecipeNutritionDTO,
)


class RecipeNotFoundError(HTTPException):
    """Return a safe not-found response for an unknown seeded recipe."""

    def __init__(self) -> None:
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recipe was not found",
        )


class RecipeService:
    """Load and serving-scale seeded recipes without public mutation behavior."""

    def __init__(self, db_session: AsyncSession) -> None:
        self.db_session = db_session

    async def list_recipes(
        self,
        *,
        query: str | None,
        tag: str | None,
        max_cooking_minutes: int | None,
        page: int,
        per_page: int,
    ) -> RecipeListResponseDTO:
        """Browse seeded recipes using deterministic filtering and ordering."""
        filters = self._filters(
            query=query,
            tag=tag,
            max_cooking_minutes=max_cooking_minutes,
        )
        count_statement = select(count()).select_from(RecipeModel)
        statement = (
            select(RecipeModel)
            .order_by(func.lower(RecipeModel.name), RecipeModel.id)
            .offset((page - 1) * per_page)
            .limit(per_page)
        )
        if filters:
            count_statement = count_statement.where(*filters)
            statement = statement.where(*filters)
        total = int((await self.db_session.execute(count_statement)).scalar_one())
        recipes = list((await self.db_session.execute(statement)).scalars().all())
        return RecipeListResponseDTO(
            items=[self._to_list_item(recipe) for recipe in recipes],
            total=total,
            page=page,
            per_page=per_page,
        )

    async def get_recipe(
        self,
        recipe_id: UUID,
        servings: Decimal | None,
    ) -> RecipeDetailDTO:
        """Return a recipe's scaled nutrition and sorted ingredient requirements."""
        recipe = await self._find_recipe(recipe_id)
        actual_servings = servings if servings is not None else recipe.default_servings
        scale = actual_servings / recipe.default_servings
        ingredients = await self._find_recipe_ingredients(recipe.id)
        return RecipeDetailDTO(
            **self._to_list_item(recipe).model_dump(),
            servings=actual_servings,
            instructions=recipe.instructions,
            nutrition=self._scaled_nutrition(recipe, scale),
            ingredients=[
                RecipeIngredientDTO(
                    recipe_ingredient_id=recipe_ingredient.id,
                    master_ingredient_id=ingredient.id,
                    name=ingredient.name,
                    required_quantity=recipe_ingredient.required_quantity * scale,
                    unit=recipe_ingredient.unit,
                    is_optional=recipe_ingredient.is_optional,
                    preparation_note=recipe_ingredient.preparation_note,
                )
                for recipe_ingredient, ingredient in ingredients
            ],
        )

    async def _find_recipe(self, recipe_id: UUID) -> RecipeModel:
        """Fetch one seeded recipe or raise a safe not-found response."""
        recipe = (
            await self.db_session.execute(
                select(RecipeModel).where(RecipeModel.id == recipe_id),
            )
        ).scalar_one_or_none()
        if recipe is None:
            raise RecipeNotFoundError()
        return recipe

    async def _find_recipe_ingredients(
        self,
        recipe_id: UUID,
    ) -> list[tuple[RecipeIngredientModel, MasterIngredientModel]]:
        """Fetch ingredients in the seed-defined creation order."""
        result = await self.db_session.execute(
            select(RecipeIngredientModel, MasterIngredientModel)
            .join(
                MasterIngredientModel,
                MasterIngredientModel.id == RecipeIngredientModel.master_ingredient_id,
            )
            .where(RecipeIngredientModel.recipe_id == recipe_id)
            .order_by(RecipeIngredientModel.created_at, RecipeIngredientModel.id),
        )
        return list(result.tuples().all())

    @staticmethod
    def _filters(
        *,
        query: str | None,
        tag: str | None,
        max_cooking_minutes: int | None,
    ) -> list[ColumnElement[bool]]:
        """Build case-insensitive text, tag, and cooking-time filters."""
        filters: list[ColumnElement[bool]] = []
        if query is not None and (normalized_query := query.strip().casefold()):
            filters.append(
                func.lower(RecipeModel.name).like(f"%{normalized_query}%"),
            )
        if tag is not None and (normalized_tag := tag.strip().casefold()):
            filters.append(RecipeModel.tags["values"].contains([normalized_tag]))
        if max_cooking_minutes is not None:
            filters.append(RecipeModel.estimated_cooking_minutes <= max_cooking_minutes)
        return filters

    @staticmethod
    def _to_list_item(recipe: RecipeModel) -> RecipeListItemDTO:
        """Map a loaded ORM recipe to its public browse representation."""
        return RecipeListItemDTO(
            id=recipe.id,
            name=recipe.name,
            description=recipe.description,
            media_url=recipe.media_url,
            default_servings=recipe.default_servings,
            estimated_cooking_minutes=recipe.estimated_cooking_minutes,
            estimated_cost=recipe.estimated_cost,
            tags=recipe.tags,
        )

    @staticmethod
    def _scaled_nutrition(recipe: RecipeModel, scale: Decimal) -> RecipeNutritionDTO:
        """Scale numeric nutrition values while retaining nonnumeric JSON metadata."""
        return RecipeNutritionDTO(
            calories=RecipeService._scale_decimal(recipe.total_calories, scale),
            protein_g=RecipeService._scale_decimal(recipe.total_protein_g, scale),
            fat_g=RecipeService._scale_decimal(recipe.total_fat_g, scale),
            carbs_g=RecipeService._scale_decimal(recipe.total_carbs_g, scale),
            sugar_g=RecipeService._scale_decimal(recipe.total_sugar_g, scale),
            other_nutrients={
                nutrient: RecipeService._scale_json_value(value, scale)
                for nutrient, value in recipe.other_nutrients.items()
            },
        )

    @staticmethod
    def _scale_decimal(value: Decimal | None, scale: Decimal) -> Decimal | None:
        """Scale one nullable database numeric value exactly."""
        return value * scale if value is not None else None

    @staticmethod
    def _scale_json_value(value: object, scale: Decimal) -> object:
        """Scale a numeric supplemental nutrient while preserving other JSON data."""
        if isinstance(value, int | float | Decimal):
            return float(Decimal(str(value)) * scale)
        return value
