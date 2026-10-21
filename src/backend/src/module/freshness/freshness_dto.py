"""Request and response contracts for FreshCheck APIs."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator

from src.model.enum_model import StorageMode


class FreshnessQuestionOptionDTO(BaseModel):
    """One selectable sensory answer supplied by the active FreshCheck KB."""

    value: str = Field(min_length=1)
    label_vi: str = Field(min_length=1)


class FreshnessQuestionDTO(BaseModel):
    """One rubric axis and its safe default answer."""

    axis: str = Field(min_length=1)
    question_vi: str = Field(min_length=1)
    options: tuple[FreshnessQuestionOptionDTO, ...] = Field(min_length=1)
    default: str = Field(min_length=1)


class FreshnessQuestionsResponseDTO(BaseModel):
    """The active KB rubric for one reviewed catalog ingredient mapping."""

    kb_version: str
    freshcheck_ingredient_id: str
    archetype_id: str
    questions: tuple[FreshnessQuestionDTO, ...]


class FreshnessAssessmentRequestDTO(BaseModel):
    """Optional newer batch facts and the user's sensory answers."""

    model_config = ConfigDict(extra="forbid")

    purchased_at: datetime | None = None
    storage_mode: StorageMode | None = None
    answers: dict[str, str] = Field(default_factory=dict)

    @field_validator("purchased_at")
    @classmethod
    def validate_purchased_at(cls, value: datetime | None) -> datetime | None:
        """Reject a local timestamp whose freshness window is ambiguous."""
        if value is not None and (value.tzinfo is None or value.utcoffset() is None):
            raise ValueError("Datetime values must include a timezone")
        return value

    @field_validator("answers")
    @classmethod
    def validate_answer_shape(cls, value: dict[str, str]) -> dict[str, str]:
        """Bound request size before matching answers against the active rubric."""
        if len(value) > 20:
            raise ValueError("At most 20 sensory answers are allowed")
        if any(
            not axis.strip() or len(axis) > 64 or not answer.strip() or len(answer) > 64
            for axis, answer in value.items()
        ):
            raise ValueError(
                "Sensory answers must be non-blank and at most 64 characters"
            )
        return value


class FreshnessPreviewRequestDTO(FreshnessAssessmentRequestDTO):
    """Sensory answers for an ingredient that is not stored in inventory yet."""

    master_ingredient_id: UUID
    storage_mode: StorageMode


class FreshnessResultDTO(BaseModel):
    """The deterministic FreshCheck decision shared by previews and assessments."""

    kb_version: str
    freshcheck_ingredient_id: str
    archetype_id: str | None
    blocked: bool
    tier: str | None
    score: float | None
    remaining_hours_min: float | None
    remaining_hours_max: float | None
    remaining_days_min: int | None
    remaining_days_max: int | None
    reason_code: str | None
    reasons_vi: tuple[str, ...]
    storage_tips_vi: tuple[str, ...]
    claims: tuple[str, ...]
    rule_version: str
    expires_at: datetime | None


class FreshnessAssessmentResponseDTO(FreshnessResultDTO):
    """The immutable FreshCheck result and any expiry safely applied to its batch."""

    assessment_id: UUID
    batch_id: UUID


class FreshnessPreviewResponseDTO(FreshnessResultDTO):
    """A non-persisted FreshCheck result; `expires_at` is the estimate to apply."""
