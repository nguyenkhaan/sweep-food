"""Request and response DTOs for the mock recommendation boundary."""

from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator

from src.model.enum_model import MeasurementUnit


class RecommendationRequestDTO(BaseModel):
    """Accept the free-text request that a future AI provider will interpret."""

    model_config = ConfigDict(extra="forbid")

    request: str = Field(min_length=1, max_length=1000)

    @field_validator("request")
    @classmethod
    def validate_request(cls, value: str) -> str:
        """Trim the user request and reject blank content."""
        normalized = value.strip()
        if not normalized:
            raise ValueError("request must not be blank")
        return normalized


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


class RecommendationListResponseDTO(BaseModel):
    """Return the mock analysis and three to five selectable recipe choices."""

    request: str
    analysis: MockRecommendationAnalysisDTO
    items: list[RecommendationItemDTO]
