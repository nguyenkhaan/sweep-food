"""Firebase Admin SDK boundary for Android and web push delivery."""

import json
from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path
from typing import Protocol

import firebase_admin
import httpx
from firebase_admin import credentials, messaging
from firebase_admin import exceptions as firebase_exceptions


class FCMProviderError(RuntimeError):
    """Base safe delivery failure without provider payloads or tokens."""


class FCMInvalidTokenError(FCMProviderError):
    """Device registration token is permanently invalid."""


class FCMRetryableError(FCMProviderError):
    """Provider failure may succeed when retried later."""


class FCMPermanentError(FCMProviderError):
    """Provider rejected the message permanently."""


@dataclass(frozen=True, slots=True)
class FCMDeliveryResult:
    """Successful provider delivery metadata."""

    message_id: str


class FirebaseMessagingClient(Protocol):
    """Synchronous Firebase client isolated behind an async application service."""

    def send(self, message: messaging.Message) -> str:
        ... 


def map_firebase_error(
    error: firebase_exceptions.FirebaseError,
) -> FCMProviderError:
    """Map Firebase SDK errors to stable worker delivery outcomes."""
    if isinstance(error, messaging.UnregisteredError):
        return FCMInvalidTokenError("FCM registration token is invalid")
    if isinstance(
        error,
        (
            messaging.QuotaExceededError,
            firebase_exceptions.ResourceExhaustedError,
            firebase_exceptions.UnavailableError,
            firebase_exceptions.InternalError,
        ),
    ):
        return FCMRetryableError("FCM delivery is temporarily unavailable")
    return FCMPermanentError("FCM delivery was permanently rejected")


class FirebaseAdminMessagingClient:
    """Initialize Firebase Admin from environment-selected server credentials."""

    def __init__(self, project_id: str, credential_path: Path) -> None:
        """Create or reuse a named Firebase application without exposing secrets."""
        if not credential_path.is_file():
            raise FileNotFoundError("Firebase credential file was not found")
        app_name = f"sweep-food-fcm-{sha256(project_id.encode()).hexdigest()[:12]}"
        try:
            self._app = firebase_admin.get_app(app_name)
        except ValueError:
            certificate = credentials.Certificate(str(credential_path))
            self._app = firebase_admin.initialize_app(
                certificate,
                {"projectId": project_id},
                name=app_name,
            )

    def send(self, message: messaging.Message) -> str:
        """Send through Firebase Admin and translate only known SDK failures."""
        try:
            return messaging.send(message, app=self._app)
        except firebase_exceptions.FirebaseError as error:
            raise map_firebase_error(error) from error


class WireMockFCMClient:
    """Deterministic local/CI FCM adapter with production-equivalent outcomes."""

    def __init__(
        self,
        base_url: str,
        timeout_seconds: int,
        transport: httpx.BaseTransport | None = None,
    ) -> None:
        """Configure the mock endpoint and optional unit-test transport."""
        self.base_url = base_url
        self.timeout_seconds = timeout_seconds
        self.transport = transport

    def send(self, message: messaging.Message) -> str:
        """Send a sanitized FCM-shaped request and map the mock response."""
        notification = message.notification
        payload = {
            "message": {
                "token": message.token,
                "notification": {
                    "title": notification.title if notification is not None else None,
                    "body": notification.body if notification is not None else None,
                },
                "data": message.data or {},
            },
        }
        try:
            with httpx.Client(
                base_url=self.base_url,
                timeout=self.timeout_seconds,
                transport=self.transport,
            ) as client:
                response = client.post("/mock/fcm", json=payload)
        except (httpx.TimeoutException, httpx.RequestError) as error:
            raise FCMRetryableError("Mock FCM delivery is unavailable") from error
        if response.status_code in {404, 410}:
            raise FCMInvalidTokenError("Mock FCM token is invalid")
        if response.status_code == 429 or response.status_code >= 500:
            raise FCMRetryableError("Mock FCM delivery is temporarily unavailable")
        if response.status_code >= 400:
            raise FCMPermanentError("Mock FCM delivery was rejected")
        try:
            body: object = response.json()
        except json.JSONDecodeError as error:
            raise FCMPermanentError("Mock FCM response was malformed") from error
        if not isinstance(body, dict):
            raise FCMPermanentError("Mock FCM response was malformed")
        message_id = body.get("message_id")
        if not isinstance(message_id, str):
            raise FCMPermanentError("Mock FCM response was malformed")
        return message_id


class FCMService:
    """Build Firebase messages for API and background-worker delivery."""

    def __init__(self, client: FirebaseMessagingClient) -> None:
        """Store the injected Firebase delivery boundary."""
        self.client = client

    async def send_to_device(
        self,
        *,
        token: str,
        title: str,
        body: str,
        data: dict[str, object],
    ) -> FCMDeliveryResult:
        """Send one Android notification with an FCM-compatible data payload."""
        message = messaging.Message(
            token=token,
            notification=messaging.Notification(title=title, body=body),
            data={key: self._stringify(value) for key, value in data.items()},
            android=messaging.AndroidConfig(
                priority="high",
                notification=messaging.AndroidNotification(
                    channel_id="food_expiration",
                ),
            ),
        )
        message_id = self.client.send(message)
        return FCMDeliveryResult(message_id=message_id)

    async def send_web_notification(
        self,
        *,
        token: str,
        title: str,
        body: str,
        data: dict[str, object],
    ) -> FCMDeliveryResult:
        """Send one browser notification through Firebase Web Push."""
        message = messaging.Message(
            token=token,
            data={key: self._stringify(value) for key, value in data.items()},
            webpush=messaging.WebpushConfig(
                notification=messaging.WebpushNotification(
                    title=title,
                    body=body,
                ),
            ),
        )
        message_id = self.client.send(message)
        return FCMDeliveryResult(message_id=message_id)

    @staticmethod
    def _stringify(value: object) -> str:
        """Convert custom FCM data to strings without losing structured values."""
        if isinstance(value, str):
            return value
        return json.dumps(value, ensure_ascii=False, separators=(",", ":"))


def build_fcm_service(project_id: str, credential_path: str) -> FCMService:
    """Build the production Firebase service from environment-derived values."""
    return FCMService(
        FirebaseAdminMessagingClient(
            project_id=project_id,
            credential_path=Path(credential_path),
        ),
    )


def build_wiremock_fcm_service(
    base_url: str,
    timeout_seconds: int,
) -> FCMService:
    """Build the local/CI FCM service from environment-derived values."""
    return FCMService(
        WireMockFCMClient(
            base_url=base_url,
            timeout_seconds=timeout_seconds,
        ),
    )
