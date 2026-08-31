"""Request and response DTOs for cooking APIs."""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator

from src.model.enum_model import (
    CookingConsumptionMode,
    CookingSessionStatus,
    InventoryBatchType,
    MeasurementUnit,
    StorageMode,
)


class CookingPreviewRequestDTO(BaseModel):
    """Select one planned meal for a read-only cooking preview."""

    model_config = ConfigDict(extra="forbid")

    meal_plan_item_id: UUID


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


class CreateCookingSessionRequestDTO(BaseModel):
    """Create a planned cooking session before any inventory deduction."""

    model_config = ConfigDict(extra="forbid")

    meal_plan_item_id: UUID


class CookingSessionDTO(BaseModel):
    """Safe public data for a planned or completed cooking session."""

    id: UUID
    recipe_id: UUID
    meal_plan_item_id: UUID | None
    servings: float
    status: CookingSessionStatus
    consumption_mode: CookingConsumptionMode | None
    nutrition_snapshot: dict[str, object]
    completed_at: datetime | None


class CookingConsumptionInputDTO(BaseModel):
    """One user-confirmed batch selection for custom completion modes."""

    recipe_ingredient_id: UUID
    inventory_batch_id: UUID
    quantity: float | None = Field(default=None, gt=0)


class CompleteCookingSessionRequestDTO(BaseModel):
    """Confirm a planned session with the desired actual-consumption mode."""

    consumption_mode: CookingConsumptionMode
    consumptions: list[CookingConsumptionInputDTO] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_consumptions(self) -> CompleteCookingSessionRequestDTO:
        """Require mode-appropriate custom inputs without accepting duplicates."""
        requires_matches = self.consumption_mode in {
            CookingConsumptionMode.CUSTOM,
            CookingConsumptionMode.USE_ALL_MATCHED,
        }
        if requires_matches and not self.consumptions:
            raise ValueError(
                "This consumption mode requires at least one matched batch"
            )
        if not requires_matches and self.consumptions:
            raise ValueError("EXACT and HALF calculate FEFO allocations automatically")
        if self.consumption_mode is CookingConsumptionMode.CUSTOM and any(
            item.quantity is None for item in self.consumptions
        ):
            raise ValueError("CUSTOM consumption requires a quantity for every batch")
        if self.consumption_mode is CookingConsumptionMode.USE_ALL_MATCHED and any(
            item.quantity is not None for item in self.consumptions
        ):
            raise ValueError("USE_ALL_MATCHED must not include custom quantities")
        batch_ids = [item.inventory_batch_id for item in self.consumptions]
        if len(batch_ids) != len(set(batch_ids)):
            raise ValueError("Each matched inventory batch may appear only once")
        return self


class CookingConsumptionDTO(BaseModel):
    """One persisted actual consumption in a completed cooking session."""

    recipe_ingredient_id: UUID | None
    inventory_batch_id: UUID
    quantity: float
    unit: MeasurementUnit


class UpdatedInventoryBatchDTO(BaseModel):
    """The balance and status of one batch after cooking deduction."""

    inventory_batch_id: UUID
    current_quantity: float
    unit: MeasurementUnit
    status: str


class CookingCompletionResponseDTO(BaseModel):
    """The idempotent result of an atomically completed cooking session."""

    session: CookingSessionDTO
    consumptions: list[CookingConsumptionDTO]
    updated_batches: list[UpdatedInventoryBatchDTO]


class CreateCookedLeftoverRequestDTO(BaseModel):
    """Request to create a cooked food leftover batch from a completed session."""

    model_config = ConfigDict(extra="forbid")

    quantity: float = Field(gt=0)
    unit: MeasurementUnit
    storage_mode: StorageMode = StorageMode.REFRIGERATED
    expires_at: datetime | None = None
    note: str | None = None


class CookedLeftoverResponseDTO(BaseModel):
    """Response shape for a created cooked-food leftover batch."""

    batch_id: UUID
    cooking_session_id: UUID
    batch_type: InventoryBatchType
    quantity: float
    unit: MeasurementUnit
    storage_mode: StorageMode
    expires_at: datetime | None
    created_at: datetime


class CookingHistorySummaryDTO(BaseModel):
    """Summary of one completed cooking session in history list."""

    session_id: UUID
    recipe_id: UUID
    recipe_name: str
    servings: float
    status: CookingSessionStatus
    completed_at: datetime | None


class CookingHistoryListResponseDTO(BaseModel):
    """Paginated or listed cooking history entries."""

    items: list[CookingHistorySummaryDTO]


class CookingHistoryDetailResponseDTO(BaseModel):
    """Detailed view of a completed cooking session, consumptions, and leftover batch."""

    session: CookingSessionDTO
    recipe_id: UUID
    recipe_name: str
    consumptions: list[CookingConsumptionDTO]
    leftover_batch_id: UUID | None
    completed_at: datetime | None

