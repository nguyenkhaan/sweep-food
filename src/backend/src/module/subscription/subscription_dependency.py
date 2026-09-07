"""FastAPI dependency construction for Subscription routes."""

from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.db import get_db_session
from src.module.subscription.subscription_service import SubscriptionService


async def get_subscription_service(
    db_session: Annotated[AsyncSession, Depends(get_db_session)],
) -> SubscriptionService:
    """Build the request-scoped subscription service."""
    return SubscriptionService(db_session)
