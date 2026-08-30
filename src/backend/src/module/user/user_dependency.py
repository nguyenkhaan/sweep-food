"""FastAPI dependencies for current-user profile APIs."""

from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.db import get_db_session
from src.module.user.user_service import UserService
from src.service.email_service import EmailService
from src.service.otp_service import OTPService
from src.service.redis_service import redis_service
from src.service.sms_service import WireMockSMSService


async def get_user_service(
    db_session: Annotated[AsyncSession, Depends(get_db_session)],
) -> UserService:
    """Create the request-scoped service for current-user operations."""
    return UserService(
        db_session=db_session,
        otp_service=OTPService(redis_service),
        sms_delivery_service=WireMockSMSService(),
        email_delivery_service=EmailService(),
        pending_contact_store=redis_service,
    )
