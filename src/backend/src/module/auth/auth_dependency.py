"""FastAPI dependencies for authentication endpoints."""

from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.db import get_db_session
from src.module.auth.auth_service import AuthService
from src.service.otp_service import OTPService
from src.service.redis_service import redis_service
from src.service.sms_service import WireMockSMSService


async def get_auth_service(
    db_session: Annotated[AsyncSession, Depends(get_db_session)],
) -> AuthService:
    """Create the request-scoped service with database and OTP dependencies."""
    return AuthService(
        db_session=db_session,
        otp_service=OTPService(redis_service),
        otp_delivery_service=WireMockSMSService(),
    )
