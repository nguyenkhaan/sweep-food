"""Request and response DTOs for user ratings."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class RatingFeedbackRequestDTO(BaseModel):
    """Optional text submitted beside a rating."""

    model_config = ConfigDict(extra="forbid")

    feedback: str = ""


class RatingDTO(BaseModel):
    """One persisted rating submission."""

    id: UUID
    user_id: UUID
    rating: float
    feedback: str
    created_at: datetime


class RatingFeedbackListResponseDTO(BaseModel):
    """Stable admin page with the application-wide average."""

    average_rating: float | None
    items: list[RatingDTO]
    total: int
    limit: int
    offset: int


class RatingAverageResponseDTO(BaseModel):
    """Application-wide average rating."""

    average_rating: float | None
