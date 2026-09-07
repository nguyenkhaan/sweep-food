"""Response DTOs for the MVP subscription API."""

from datetime import datetime
from enum import Enum

from pydantic import BaseModel


class SubscriptionPlan(str, Enum):
    """Plans exposed by the stable public subscription response."""

    FREE = "free"
    PREMIUM = "premium"


class SubscriptionResponseDTO(BaseModel):
    """Current account subscription state; MVP always returns free/null."""

    plan: SubscriptionPlan
    expires_at: datetime | None


class PremiumInterestResponseDTO(BaseModel):
    """Confirm that the authenticated user has registered premium interest."""

    registered: bool
