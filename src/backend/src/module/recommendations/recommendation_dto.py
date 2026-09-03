"""Stable request and response DTOs for the recommendations endpoint."""

from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from src.model.enum_model import MealSlot, MeasurementUnit
from src.module.recipes.recipe_dto import RecipeListItemDTO


class RecommendationFiltersDTO(BaseModel):
    """Supported recipe-candidate filters for recommendation requests."""

    model_config = ConfigDict(extra="forbid")

    tag: str | None = Field(default=None, min_length=1, max_length=100)
    max_cooking_minutes: int | None = Field(default=None, ge=1)


class RecommendationRequestDTO(BaseModel):
    """Criteria for one ranked recipe recommendation request."""

    model_config = ConfigDict(extra="forbid")

    servings: Decimal | None = Field(
        default=None,
        gt=0,
        max_digits=6,
        decimal_places=2,
    )
    target_date: date | None = None
    meal_slot: MealSlot | None = None
    limit: int = Field(default=5, ge=3, le=5)
    filters: RecommendationFiltersDTO = Field(default_factory=RecommendationFiltersDTO)


class RecommendationScoreComponentsDTO(BaseModel):
    """Normalized E/A/P/U values used to calculate a recommendation score."""

    expiration_utilization: Decimal = Field(ge=0, le=1)
    availability: Decimal = Field(ge=0, le=1)
    preference_fit: Decimal = Field(ge=0, le=1)
    purchase_minimization: Decimal = Field(ge=0, le=1)


class RecommendationMissingIngredientDTO(BaseModel):
    """One required ingredient not fully covered by usable inventory."""

    master_ingredient_id: UUID
    name: str
    required_quantity: Decimal
    available_quantity: Decimal
    missing_quantity: Decimal
    unit: MeasurementUnit


class RecommendationIngredientAvailabilityDTO(BaseModel):
    """Coverage metadata for one required recipe ingredient."""

    master_ingredient_id: UUID
    name: str
    required_quantity: Decimal
    available_quantity: Decimal
    missing_quantity: Decimal
    unit: MeasurementUnit


class RecommendationNearExpiryContributionDTO(BaseModel):
    """One near-expiry batch contribution represented in an explanation."""

    batch_id: UUID
    master_ingredient_id: UUID
    ingredient_name: str
    allocated_quantity: Decimal
    unit: MeasurementUnit
    expires_at: datetime
    urgency_weight: Decimal = Field(ge=0, le=1)


class RecommendationPreferenceFitExplanationDTO(BaseModel):
    """Preference-fit inputs represented in the recommendation explanation."""

    serving_suitability: Decimal = Field(ge=0, le=1)
    cooking_time_suitability: Decimal = Field(ge=0, le=1)
    dietary_suitability: Decimal = Field(ge=0, le=1)
    nutrition_suitability: Decimal = Field(ge=0, le=1)
    maximum_cooking_minutes: int | None
    neutral_treatments: list[str]


class RecommendationExplanationDTO(BaseModel):
    """Structured, provider-independent reason a recipe was ranked."""

    ingredient_availability: list[RecommendationIngredientAvailabilityDTO]
    near_expiry_contributions: list[RecommendationNearExpiryContributionDTO]
    preference_fit: RecommendationPreferenceFitExplanationDTO


class RecommendationItemDTO(BaseModel):
    """One ranked recipe and its explainable score metadata."""

    recipe_id: UUID
    recipe: RecipeListItemDTO
    rank: int = Field(ge=1)
    score: Decimal = Field(ge=0, le=1)
    score_components: RecommendationScoreComponentsDTO
    available_ratio: Decimal = Field(ge=0, le=1)
    missing_ingredients: list[RecommendationMissingIngredientDTO]
    expiring_batches_used: list[UUID]
    explanation: RecommendationExplanationDTO
    provider: str = Field(min_length=1, max_length=100)
    model_version: str | None = Field(default=None, max_length=100)


class RecommendationListResponseDTO(BaseModel):
    """The compact, ranked recommendation response returned to clients."""

    items: list[RecommendationItemDTO] = Field(max_length=5)
