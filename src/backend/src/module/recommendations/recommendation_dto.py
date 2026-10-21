"""Request and response DTOs for the recommendation boundary."""

from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

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


class RecommendationRankingFeaturesDTO(BaseModel):
    """Contextual feature values returned by SweepFood AI v2."""

    core_coverage: float = Field(ge=0, le=1)
    core_missing_count: float = Field(ge=0)
    secondary_coverage: float = Field(ge=0, le=1)
    shopping_gap_items: float = Field(ge=0)
    rescue_weight_g: float = Field(ge=0)
    nutrition_confidence: float = Field(ge=0, le=1)
    kcal_per_serving: float = Field(ge=0)
    protein_per_serving: float = Field(ge=0)
    prep_complexity: float = Field(ge=0)


class RecommendationIngredientDTO(BaseModel):
    """Describe one recipe ingredient from the AI result."""

    name: str = Field(min_length=1)
    code: str | None = None
    required_g: float = Field(ge=0)


class RecommendationTimingsDTO(BaseModel):
    """AI inference latency split in milliseconds."""

    total_ms: float = Field(ge=0)
    candidate_ms: float = Field(ge=0)
    ranker_ms: float = Field(ge=0)


class RecommendationRecipeSummaryDTO(BaseModel):
    """Display-ready recipe card at the recipe's default serving count."""

    id: UUID
    name: str
    media_url: str | None
    estimated_cooking_minutes: int
    default_servings: Decimal
    nutrition: RecipeNutritionDTO


class RecommendationItemDTO(BaseModel):
    """One catalog-backed recipe in the AI-defined order."""

    recipe_id: UUID
    recipe_name: str
    rank: int = Field(ge=1)
    rank_score: float
    ranking_features: RecommendationRankingFeaturesDTO
    matched_ingredients: list[RecommendationIngredientDTO]
    missing_ingredients: list[RecommendationIngredientDTO]
    optional_ingredients: list[RecommendationIngredientDTO]
    rescued_items: list[str]
    status_badge: str
    explanation: str
    provider: str
    recipe_summary: RecommendationRecipeSummaryDTO | None = None


class RecommendationListResponseDTO(BaseModel):
    """Return ranked, catalog-backed recipe choices."""

    request: RecommendationRequestDTO
    contract_version: str
    model_version: str
    catalog_revision: str
    ranker_model: str
    timings: RecommendationTimingsDTO
    analysis: MockRecommendationAnalysisDTO
    items: list[RecommendationItemDTO]
    warnings: list[str] = Field(default_factory=list)
