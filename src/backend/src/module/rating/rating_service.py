"""User rating persistence and admin aggregate reads."""

from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from src.model.user_feedback_model import UserFeedbackModel
from src.module.rating.rating_dto import (
    RatingAverageResponseDTO,
    RatingDTO,
    RatingFeedbackListResponseDTO,
    RatingFeedbackRequestDTO,
)


class RatingService:
    """Append feedback and expose stable administrative rating summaries."""

    def __init__(self, db_session: AsyncSession) -> None:
        self.db_session = db_session

    async def create_rating(
        self,
        user_id: UUID,
        rating: float,
        body: RatingFeedbackRequestDTO | None,
    ) -> RatingDTO:
        """Append one rating, using empty feedback when no body was supplied."""
        feedback = UserFeedbackModel(
            user_id=user_id,
            rating=rating,
            feedback=body.feedback if body is not None else "",
        )
        try:
            self.db_session.add(feedback)
            await self.db_session.commit()
        except SQLAlchemyError:
            await self.db_session.rollback()
            raise
        return self._to_dto(feedback)

    async def list_feedback(
        self,
        limit: int,
        offset: int,
    ) -> RatingFeedbackListResponseDTO:
        """Return an aggregate and stable newest-first page for administrators."""
        try:
            summary = (
                await self.db_session.execute(
                    select(
                        func.count(UserFeedbackModel.id),
                        func.avg(UserFeedbackModel.rating),
                    )
                )
            ).one()
            feedback = (
                (
                    await self.db_session.execute(
                        select(UserFeedbackModel)
                        .order_by(
                            UserFeedbackModel.created_at.desc(),
                            UserFeedbackModel.id.desc(),
                        )
                        .limit(limit)
                        .offset(offset)
                    )
                )
                .scalars()
                .all()
            )
        except SQLAlchemyError:
            await self.db_session.rollback()
            raise
        average = float(summary[1]) if summary[1] is not None else None
        return RatingFeedbackListResponseDTO(
            average_rating=average,
            items=[self._to_dto(item) for item in feedback],
            total=int(summary[0]),
            limit=limit,
            offset=offset,
        )

    async def get_average(self) -> RatingAverageResponseDTO:
        """Return the application-wide average or null for an empty table."""
        try:
            average = (
                await self.db_session.execute(
                    select(func.avg(UserFeedbackModel.rating))
                )
            ).scalar_one()
        except SQLAlchemyError:
            await self.db_session.rollback()
            raise
        return RatingAverageResponseDTO(
            average_rating=float(average) if average is not None else None,
        )

    @staticmethod
    def _to_dto(feedback: UserFeedbackModel) -> RatingDTO:
        return RatingDTO(
            id=feedback.id,
            user_id=feedback.user_id,
            rating=feedback.rating,
            feedback=feedback.feedback,
            created_at=feedback.created_at,
        )
