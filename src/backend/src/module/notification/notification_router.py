"""Direct FCM tests and authenticated notification-management routes."""

from datetime import datetime
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status

from src.middleware.auth_middleware import AuthenticatedUser, require_authentication
from src.module.notification.notification_dependency import (
    get_notification_service,
    get_production_fcm_service,
)
from src.module.notification.notification_dto import (
    DeviceRegistrationResponseDTO,
    NotificationListResponseDTO,
    NotificationResponseDTO,
    RegisterDeviceRequestDTO,
    SendNotificationRequestDTO,
    SendNotificationResponseDTO,
    UpdateNotificationRequestDTO,
)
from src.module.notification.notification_service import NotificationService
from src.service.fcm_service import (
    FCMInvalidTokenError,
    FCMPermanentError,
    FCMRetryableError,
    FCMService,
)

notification_router = APIRouter(tags=["notifications"])


@notification_router.post(
    "/send-notification",
    response_model=SendNotificationResponseDTO,
    summary="Send an Android notification through Firebase",
)
async def post_send_notification(
    body: SendNotificationRequestDTO,
    fcm_service: Annotated[FCMService, Depends(get_production_fcm_service)],
) -> SendNotificationResponseDTO:
    """Send a direct Android push for manual Firebase integration testing."""
    try:
        result = await fcm_service.send_to_device(
            token=body.device_token,
            title=body.title,
            body=body.body,
            data=body.data,
        )
    except FCMInvalidTokenError as error:
        raise _delivery_http_error(
            status.HTTP_422_UNPROCESSABLE_CONTENT,
            "Firebase rejected the device token",
        ) from error
    except FCMRetryableError as error:
        raise _delivery_http_error(
            status.HTTP_503_SERVICE_UNAVAILABLE,
            "Firebase is temporarily unavailable",
        ) from error
    except FCMPermanentError as error:
        raise _delivery_http_error(
            status.HTTP_502_BAD_GATEWAY,
            "Firebase permanently rejected the notification",
        ) from error
    return SendNotificationResponseDTO(message_id=result.message_id)


@notification_router.post(
    "/send-web-notification",
    response_model=SendNotificationResponseDTO,
    summary="Send a web notification through Firebase",
)
async def post_send_web_notification(
    body: SendNotificationRequestDTO,
    fcm_service: Annotated[FCMService, Depends(get_production_fcm_service)],
) -> SendNotificationResponseDTO:
    """Send a direct Web Push message for manual Firebase integration testing."""
    try:
        result = await fcm_service.send_web_notification(
            token=body.device_token,
            title=body.title,
            body=body.body,
            data=body.data,
        )
    except FCMInvalidTokenError as error:
        raise _delivery_http_error(
            status.HTTP_422_UNPROCESSABLE_CONTENT,
            "Firebase rejected the device token",
        ) from error
    except FCMRetryableError as error:
        raise _delivery_http_error(
            status.HTTP_503_SERVICE_UNAVAILABLE,
            "Firebase is temporarily unavailable",
        ) from error
    except FCMPermanentError as error:
        raise _delivery_http_error(
            status.HTTP_502_BAD_GATEWAY,
            "Firebase permanently rejected the notification",
        ) from error
    return SendNotificationResponseDTO(message_id=result.message_id)


def _delivery_http_error(
    status_code: int,
    detail: str,
) -> HTTPException:
    """Create a client-safe error without exposing provider data or tokens."""
    return HTTPException(status_code=status_code, detail=detail)


@notification_router.post(
    "/users/me/devices",
    response_model=DeviceRegistrationResponseDTO,
    summary="Register an Android FCM device",
)
async def post_device_registration(
    body: RegisterDeviceRequestDTO,
    user: Annotated[AuthenticatedUser, Depends(require_authentication)],
    service: Annotated[NotificationService, Depends(get_notification_service)],
) -> DeviceRegistrationResponseDTO:
    """Create or refresh the current user's FCM registration token."""
    return await service.register_device(user.user_id, body)


@notification_router.delete(
    "/users/me/devices/{device_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Disable an Android FCM device",
)
async def delete_device_registration(
    device_id: UUID,
    user: Annotated[AuthenticatedUser, Depends(require_authentication)],
    service: Annotated[NotificationService, Depends(get_notification_service)],
) -> Response:
    """Disable one device registration owned by the current user."""
    await service.disable_device(user.user_id, device_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@notification_router.get(
    "/notifications",
    response_model=NotificationListResponseDTO,
    summary="List my notifications",
)
async def get_notifications(
    user: Annotated[AuthenticatedUser, Depends(require_authentication)],
    service: Annotated[NotificationService, Depends(get_notification_service)],
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    before: datetime | None = None,
) -> NotificationListResponseDTO:
    """Return a timestamp-cursor page of the caller's notifications."""
    return await service.list_notifications(user.user_id, limit, before)


@notification_router.patch(
    "/notifications/{notification_id}",
    response_model=NotificationResponseDTO,
    summary="Mark my notification read or dismissed",
)
async def patch_notification(
    notification_id: UUID,
    body: UpdateNotificationRequestDTO,
    user: Annotated[AuthenticatedUser, Depends(require_authentication)],
    service: Annotated[NotificationService, Depends(get_notification_service)],
) -> NotificationResponseDTO:
    """Update one notification only when it belongs to the caller."""
    return await service.update_notification(user.user_id, notification_id, body)
