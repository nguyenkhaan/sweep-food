"""Administrator account-management database operations."""

from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from src.model.enum_model import AccountStatus
from src.model.user_model import UserModel
from src.module.admin.admin_dto import BannedUserDTO


class AdminUserNotFoundError(HTTPException):
    """Report an unknown account without changing any state."""

    def __init__(self) -> None:
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User was not found",
        )


class AdminService:
    """Apply administrator-only account state changes."""

    def __init__(self, db_session: AsyncSession) -> None:
        self.db_session = db_session

    async def ban_user(self, user_id: UUID) -> BannedUserDTO:
        """Set one existing account to BANNED."""
        try:
            result = await self.db_session.execute(
                select(UserModel).where(UserModel.id == user_id)
            )
            user = result.scalar_one_or_none()
            if user is None:
                raise AdminUserNotFoundError()
            user.status = AccountStatus.BANNED
            await self.db_session.commit()
            return BannedUserDTO(user_id=user.id, status=user.status)
        except SQLAlchemyError:
            await self.db_session.rollback()
            raise
