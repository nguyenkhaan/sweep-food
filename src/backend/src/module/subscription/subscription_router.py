"""Authenticated MVP Subscription HTTP routes."""

from typing import Annotated

from fastapi import APIRouter, Depends

from src.middleware.auth_middleware import AuthenticatedUser, require_authentication
from src.module.subscription.subscription_dependency import get_subscription_service
from src.module.subscription.subscription_dto import (
    PremiumInterestResponseDTO,
    SubscriptionResponseDTO,
)
from src.module.subscription.subscription_service import SubscriptionService

subscription_router = APIRouter(prefix="/subscription", tags=["subscription"])


@subscription_router.get("", response_model=SubscriptionResponseDTO)
async def get_subscription(
    user: Annotated[AuthenticatedUser, Depends(require_authentication)],
    service: Annotated[SubscriptionService, Depends(get_subscription_service)],
) -> SubscriptionResponseDTO:
    """Return the authenticated user's fixed MVP subscription state."""
    _ = user
    return service.get_subscription()


@subscription_router.post(
    "/premium-interest",
    response_model=PremiumInterestResponseDTO,
)
async def post_premium_interest(
    user: Annotated[AuthenticatedUser, Depends(require_authentication)],
    service: Annotated[SubscriptionService, Depends(get_subscription_service)],
) -> PremiumInterestResponseDTO:
    """Persist the current user's interest without changing access or plan state."""
    return await service.register_premium_interest(user.user_id)
