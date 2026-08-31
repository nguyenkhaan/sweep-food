"""Request and response DTOs for seeded recipe reads."""

from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel

from src.model.enum_model import MeasurementUnit


class RecipeNutritionDTO(BaseModel):
    """Serving-scaled denormalized nutrition for a recipe."""

    calories: Decimal | None
    protein_g: Decimal | None
    fat_g: Decimal | None
    carbs_g: Decimal | None
    sugar_g: Decimal | None
    other_nutrients: dict[str, object]


class RecipeListItemDTO(BaseModel):
    """Compact seeded recipe card returned by browse and search."""

    id: UUID
    name: str
    description: str
    media_url: str | None
    default_servings: Decimal
    estimated_cooking_minutes: int
    estimated_cost: float | None
    tags: dict[str, object]


class RecipeIngredientDTO(BaseModel):
    """One serving-scaled recipe ingredient with canonical catalog identity."""

    recipe_ingredient_id: UUID
    master_ingredient_id: UUID
    name: str
    required_quantity: Decimal
    unit: MeasurementUnit
    is_optional: bool
    preparation_note: str | None


class RecipeDetailDTO(RecipeListItemDTO):
    """Full seeded recipe details, scaled for the requested serving count."""

    servings: Decimal
    instructions: dict[str, object]
    nutrition: RecipeNutritionDTO
    ingredients: list[RecipeIngredientDTO]


class RecipeListResponseDTO(BaseModel):
    """A stable page of searchable seeded recipes."""

    items: list[RecipeListItemDTO]
    total: int
    page: int
    per_page: int
