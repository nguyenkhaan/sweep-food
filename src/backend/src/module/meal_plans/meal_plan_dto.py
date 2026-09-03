"""Request and response DTOs for meal-plan persistence."""

from datetime import date
from math import isfinite
from uuid import UUID
from datetime import datetime 
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from src.model.enum_model import MealPlanItemStatus, MealSlot


class CreateMealPlanRequestDTO(BaseModel):
    """Create one bounded personal meal plan."""

    model_config = ConfigDict(extra="forbid")

    name: str | None = Field(default=None, min_length=1, max_length=255)
    starts_on: date
    ends_on: date

    @model_validator(mode="after")
    def validate_range(self) -> "CreateMealPlanRequestDTO":
        """Reject an inverted planning range before it reaches the database."""
        if self.starts_on > self.ends_on:
            raise ValueError("starts_on must not be after ends_on")
        return self


class CreateMealPlanItemRequestDTO(BaseModel):
    """Add a seeded recipe to one dated meal slot."""

    model_config = ConfigDict(extra="forbid")

    recipe_id: UUID
    planned_for: date
    meal_slot: MealSlot
    servings: float = Field(gt=0)
    recommendation_run_id: UUID | None = None

    @field_validator("servings")
    @classmethod
    def validate_servings(cls, value: float) -> float:
        """Keep quantities suitable for the float persistence column."""
        if not isfinite(value):
            raise ValueError("servings must be finite")
        return value


class UpdateMealPlanItemRequestDTO(BaseModel):
    """Replace or reschedule one existing meal-plan slot."""

    model_config = ConfigDict(extra="forbid")

    recipe_id: UUID | None = None
    planned_for: date | None = None
    meal_slot: MealSlot | None = None
    servings: float | None = Field(default=None, gt=0)

    @field_validator("servings")
    @classmethod
    def validate_servings(cls, value: float | None) -> float | None:
        """Reject non-finite updates that database floats would retain."""
        if value is not None and not isfinite(value):
            raise ValueError("servings must be finite")
        return value

    @model_validator(mode="after")
    def validate_change(self) -> "UpdateMealPlanItemRequestDTO":
        """Require an actual replacement or rescheduling change."""
        if not self.model_fields_set:
            raise ValueError("Provide at least one item field to update")
        return self


class MealPlanItemDTO(BaseModel):
    """Public state of one selected meal."""

    id: UUID
    recipe_id: UUID
    recipe_name: str
    recommendation_run_id: UUID | None
    planned_for: date
    meal_slot: MealSlot
    servings: float
    status: MealPlanItemStatus


class MealPlanViewDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    name: str | None
    starts_on: date
    ends_on: date
    created_at: datetime
    updated_at: datetime

class MealPlanDTO(BaseModel):
    """Public state of a user's meal plan and its ordered slots."""

    id: UUID
    name: str | None
    starts_on: date
    ends_on: date
    items: list[MealPlanItemDTO]
