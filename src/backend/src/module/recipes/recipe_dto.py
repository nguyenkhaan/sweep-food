"""Request and response DTOs for recipes."""

from decimal import Decimal
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator

from src.model.enum_model import MeasurementUnit


class CreateRecipeRequestDTO(BaseModel):
    """Create one recipe while leaving generated fields to the database model."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    name: str = Field(min_length=1)
    description: str = Field(min_length=1)
    instructions: dict[str, object]
    media_url: str | None = Field(default=None, min_length=1, max_length=2048)
    source_platform: str = Field(default="internal", min_length=1, max_length=50)
    source_url: str | None = Field(default=None, min_length=1, max_length=2048)
    default_servings: Decimal = Field(gt=0, max_digits=6, decimal_places=2)
    estimated_cooking_minutes: int = Field(ge=1)
    estimated_cost: float | None = Field(default=None, ge=0, allow_inf_nan=False)
    total_calories: Decimal | None = Field(
        default=None, ge=0, max_digits=12, decimal_places=3, allow_inf_nan=False
    )
    total_protein_g: Decimal | None = Field(
        default=None, ge=0, max_digits=12, decimal_places=3, allow_inf_nan=False
    )
    total_fat_g: Decimal | None = Field(
        default=None, ge=0, max_digits=12, decimal_places=3, allow_inf_nan=False
    )
    total_carbs_g: Decimal | None = Field(
        default=None, ge=0, max_digits=12, decimal_places=3, allow_inf_nan=False
    )
    total_sugar_g: Decimal | None = Field(
        default=None, ge=0, max_digits=12, decimal_places=3, allow_inf_nan=False
    )
    other_nutrients: dict[str, object] = Field(default_factory=dict)
    nutrition_status: Literal["COMPLETE", "PARTIAL", "INCOMPLETE"] = "INCOMPLETE"
    tags: dict[str, object] = Field(default_factory=dict)


class UpdateRecipeRequestDTO(BaseModel):
    """Update only explicitly supplied recipe fields."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    name: str | None = Field(default=None, min_length=1)
    description: str | None = Field(default=None, min_length=1)
    instructions: dict[str, object] | None = None
    media_url: str | None = Field(default=None, min_length=1, max_length=2048)
    source_platform: str | None = Field(default=None, min_length=1, max_length=50)
    source_url: str | None = Field(default=None, min_length=1, max_length=2048)
    default_servings: Decimal | None = Field(
        default=None, gt=0, max_digits=6, decimal_places=2
    )
    estimated_cooking_minutes: int | None = Field(default=None, ge=1)
    estimated_cost: float | None = Field(default=None, ge=0, allow_inf_nan=False)
    total_calories: Decimal | None = Field(
        default=None, ge=0, max_digits=12, decimal_places=3, allow_inf_nan=False
    )
    total_protein_g: Decimal | None = Field(
        default=None, ge=0, max_digits=12, decimal_places=3, allow_inf_nan=False
    )
    total_fat_g: Decimal | None = Field(
        default=None, ge=0, max_digits=12, decimal_places=3, allow_inf_nan=False
    )
    total_carbs_g: Decimal | None = Field(
        default=None, ge=0, max_digits=12, decimal_places=3, allow_inf_nan=False
    )
    total_sugar_g: Decimal | None = Field(
        default=None, ge=0, max_digits=12, decimal_places=3, allow_inf_nan=False
    )
    other_nutrients: dict[str, object] | None = None
    nutrition_status: Literal["COMPLETE", "PARTIAL", "INCOMPLETE"] | None = None
    tags: dict[str, object] | None = None

    @model_validator(mode="after")
    def validate_update(self) -> "UpdateRecipeRequestDTO":
        """Require a change and preserve non-nullable database columns."""
        if not self.model_fields_set:
            raise ValueError("Provide at least one recipe field to update")
        required_fields = {
            "name",
            "description",
            "instructions",
            "source_platform",
            "source_url",
            "default_servings",
            "estimated_cooking_minutes",
            "other_nutrients",
            "nutrition_status",
            "tags",
        }
        if any(
            getattr(self, field_name) is None
            for field_name in self.model_fields_set & required_fields
        ):
            raise ValueError("Non-nullable recipe fields cannot be null")
        return self


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
