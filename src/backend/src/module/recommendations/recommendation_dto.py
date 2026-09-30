"""Request and response DTOs for the recommendation boundary."""

from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from src.model.enum_model import MeasurementUnit
from src.module.recipes.recipe_dto import RecipeNutritionDTO


class RecommendationPantryItemDTO(BaseModel):
    """One pantry item supplied to recommendation inference."""

    model_config = ConfigDict(extra="forbid")

    name: str = Field(min_length=1)
    code: str | None = None
    quantity_g: float = Field(default=200, gt=0)
    hours_to_expire: float | None = None
    is_staple: bool = False


class RecommendationRequestDTO(BaseModel):
    """Mirror the structured request accepted by SweepFood AI."""

    model_config = ConfigDict(extra="forbid")

    items: list[RecommendationPantryItemDTO]
    household_size: float = Field(default=4, gt=0)
    max_cooking_time_min: float = Field(default=45, gt=0)
    scenario_type: str = "custom"
    dietary_restrictions: list[str] = Field(default_factory=list)
    allergies: list[str] = Field(default_factory=list)
    disliked_ingredients: list[str] = Field(default_factory=list)
    preferred_cuisines: list[str] = Field(default_factory=list)


class MockRecommendationAnalysisDTO(BaseModel):
    """Expose the temporary interpretation without claiming AI inference occurred."""

    intent: str
    summary: str
    is_mock: bool


class RecommendationScoreComponentsDTO(BaseModel):
    """Keep the production E/A/P/U explanation shape stable."""

    expiration_utilization: float = Field(ge=0, le=1)
    availability: float = Field(ge=0, le=1)
    preference_fit: float = Field(ge=0, le=1)
    purchase_minimization: float = Field(ge=0, le=1)


class RecommendationMissingIngredientDTO(BaseModel):
    """Describe one ingredient the user would need to buy."""

    master_ingredient_id: UUID | None
    name: str
    quantity: float = Field(gt=0)
    unit: MeasurementUnit


class RecommendationRecipeSummaryDTO(BaseModel):
    """Display-ready recipe card at the recipe's default serving count."""

    id: UUID
    name: str
    media_url: str | None
    estimated_cooking_minutes: int
    default_servings: Decimal
    nutrition: RecipeNutritionDTO


class RecommendationItemDTO(BaseModel):
    """One mock-ranked, catalog-backed recipe choice."""

    recipe_id: UUID
    recipe_name: str
    rank: int = Field(ge=1)
    score: float = Field(ge=0, le=1)
    score_components: RecommendationScoreComponentsDTO
    missing_ingredients: list[RecommendationMissingIngredientDTO]
    near_expiry_ingredients: list[str]
    explanation: str
    provider: str
    model_version: str
    recipe_summary: RecommendationRecipeSummaryDTO | None = None


class RecommendationListResponseDTO(BaseModel):
    """Return ranked, catalog-backed recipe choices."""

    request: RecommendationRequestDTO
    analysis: MockRecommendationAnalysisDTO
    items: list[RecommendationItemDTO]
    warnings: list[str] = Field(default_factory=list)
