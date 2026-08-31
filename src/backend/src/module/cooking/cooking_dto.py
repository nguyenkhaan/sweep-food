"""Request and response DTOs for read-only cooking previews."""

from datetime import datetime
from enum import Enum
from uuid import UUID

from pydantic import BaseModel, Field

from src.model.enum_model import MeasurementUnit


class CookingPreviewRequestDTO(BaseModel):
    """Select a recipe and serving count for a read-only cooking preview."""

    recipe_id: UUID
    servings: float = Field(gt=0)


class ScaledRecipeIngredientDTO(BaseModel):
    """One recipe ingredient scaled to the requested serving count."""

    recipe_ingredient_id: UUID
    master_ingredient_id: UUID
    ingredient_name: str
    required_quantity: float
    unit: MeasurementUnit


class ProposedBatchDeductionDTO(BaseModel):
    """One FEFO deduction proposal without a persistent stock mutation."""

    recipe_ingredient_id: UUID
    master_ingredient_id: UUID
    batch_id: UUID
    quantity: float
    unit: MeasurementUnit
    recipe_quantity: float
    recipe_unit: MeasurementUnit
    expires_at: datetime | None


class MissingIngredientDTO(BaseModel):
    """A scaled recipe quantity not covered by eligible inventory batches."""

    recipe_ingredient_id: UUID
    master_ingredient_id: UUID
    ingredient_name: str
    missing_quantity: float
    unit: MeasurementUnit


class CookingPreviewWarningCode(str, Enum):
    """Warnings that can affect a cooking allocation proposal."""

    EXPIRED_BATCH_EXCLUDED = "EXPIRED_BATCH_EXCLUDED"
    UNKNOWN_EXPIRATION_BATCH = "UNKNOWN_EXPIRATION_BATCH"
    INCOMPATIBLE_UNIT_BATCH = "INCOMPATIBLE_UNIT_BATCH"


class CookingPreviewWarningDTO(BaseModel):
    """A non-blocking reason why a visible batch is not normally preferred."""

    code: CookingPreviewWarningCode
    message: str
    batch_id: UUID
    master_ingredient_id: UUID


class NutritionEstimateDTO(BaseModel):
    """Denormalized recipe nutrition scaled to the requested servings."""

    calories: float | None
    protein_g: float | None
    fat_g: float | None
    carbs_g: float | None
    sugar_g: float | None
    other_nutrients: dict[str, object]


class CookingPreviewResponseDTO(BaseModel):
    """All read-only data needed before a user confirms cooking."""

    recipe_id: UUID
    recipe_name: str
    servings: float
    scaled_ingredients: list[ScaledRecipeIngredientDTO]
    proposed_deductions: list[ProposedBatchDeductionDTO]
    missing_ingredients: list[MissingIngredientDTO]
    nutrition_estimate: NutritionEstimateDTO
    warnings: list[CookingPreviewWarningDTO]
