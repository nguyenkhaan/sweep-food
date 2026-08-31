"""Minimal Firebase Messaging types used by Sweep Food."""

from firebase_admin import App
from firebase_admin.exceptions import FirebaseError

class Notification:
    title: str | None
    body: str | None
    def __init__(
        self,
        title: str | None = None,
        body: str | None = None,
        image: str | None = None,
    ) -> None: ...

class AndroidNotification:
    def __init__(self, *, channel_id: str | None = None) -> None: ...

class AndroidConfig:
    def __init__(
        self,
        *,
        priority: str | None = None,
        notification: AndroidNotification | None = None,
    ) -> None: ...

class WebpushNotification:
    title: str | None
    body: str | None
    def __init__(
        self,
        title: str | None = None,
        body: str | None = None,
    ) -> None: ...

class WebpushConfig:
    notification: WebpushNotification | None
    def __init__(
        self,
        *,
        notification: WebpushNotification | None = None,
    ) -> None: ...

class Message:
    data: dict[str, str] | None
    notification: Notification | None
    webpush: WebpushConfig | None
    token: str | None
    fid: str | None
    def __init__(
        self,
        data: dict[str, str] | None = None,
        notification: Notification | None = None,
        android: AndroidConfig | None = None,
        webpush: WebpushConfig | None = None,
        token: str | None = None,
        fid: str | None = None,
    ) -> None: ...

class UnregisteredError(FirebaseError):
    def __init__(
        self,
        message: str,
        cause: Exception | None = None,
        http_response: object | None = None,
    ) -> None: ...

class QuotaExceededError(FirebaseError):
    def __init__(
        self,
        message: str,
        cause: Exception | None = None,
        http_response: object | None = None,
    ) -> None: ...

class SenderIdMismatchError(FirebaseError):
    def __init__(
        self,
        message: str,
        cause: Exception | None = None,
        http_response: object | None = None,
    ) -> None: ...

class ThirdPartyAuthError(FirebaseError):
    def __init__(
        self,
        message: str,
        cause: Exception | None = None,
        http_response: object | None = None,
    ) -> None: ...

def send(message: Message, dry_run: bool = False, app: App | None = None) -> str: ...
