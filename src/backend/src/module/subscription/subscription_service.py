"""MVP subscription reads and idempotent premium-interest persistence."""

from uuid import UUID

from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from src.model.premium_interest_model import PremiumInterestModel
from src.module.subscription.subscription_dto import (
    PremiumInterestResponseDTO,
    SubscriptionPlan,
    SubscriptionResponseDTO,
)


class SubscriptionService:
    """Serve the fixed MVP plan and persist one interest row per user."""

    def __init__(self, db_session: AsyncSession) -> None:
        """Store the request-scoped transaction used for interest registration."""
        self.db_session = db_session

    def get_subscription(self) -> SubscriptionResponseDTO:
        """Return the fixed MVP plan without reading interest registration state."""
        return SubscriptionResponseDTO(
            plan=SubscriptionPlan.FREE,
            expires_at=None,
        )

    async def register_premium_interest(
        self,
        user_id: UUID,
    ) -> PremiumInterestResponseDTO:
        """Insert once by user primary key while preserving the first registration time."""
        statement = (
            insert(PremiumInterestModel)
            .values(user_id=user_id)
            .on_conflict_do_nothing(index_elements=[PremiumInterestModel.user_id])
        )
        try:
            await self.db_session.execute(statement)
            await self.db_session.commit()
        except SQLAlchemyError:
            await self.db_session.rollback()
            raise
        return PremiumInterestResponseDTO(registered=True)
