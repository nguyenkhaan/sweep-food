"""FastAPI dependency wiring for notification APIs."""

from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.setting import get_env_var
from src.db import get_db_session
from src.module.notification.notification_service import (
    FernetTokenCipher,
    NotificationService,
)
from src.service.fcm_service import FCMService, build_fcm_service


async def get_notification_service(
    db_session: Annotated[AsyncSession, Depends(get_db_session)],
) -> NotificationService:
    """Build a request-scoped notification service from environment secrets."""
    return NotificationService(
        db_session=db_session,
        token_cipher=FernetTokenCipher(get_env_var("FCM_TOKEN_ENCRYPTION_KEY")),
    )


async def get_production_fcm_service() -> FCMService:
    """Build the real Firebase adapter for direct manual-test deliveries."""
    return build_fcm_service(
        project_id=get_env_var("FIREBASE_PROJECT_ID"),
        credential_path=get_env_var("GOOGLE_APPLICATION_CREDENTIALS"),
    )
