"""Minimal Firebase exception hierarchy used by Sweep Food."""

class FirebaseError(Exception):
    def __init__(
        self,
        code: str,
        message: str,
        cause: Exception | None = None,
        http_response: object | None = None,
    ) -> None: ...

class ResourceExhaustedError(FirebaseError):
    def __init__(
        self,
        message: str,
        cause: Exception | None = None,
        http_response: object | None = None,
    ) -> None: ...

class UnavailableError(FirebaseError):
    def __init__(
        self,
        message: str,
        cause: Exception | None = None,
        http_response: object | None = None,
    ) -> None: ...

class InternalError(FirebaseError):
    def __init__(
        self,
        message: str,
        cause: Exception | None = None,
        http_response: object | None = None,
    ) -> None: ...
