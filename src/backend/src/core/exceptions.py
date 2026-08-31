"""Application-wide HTTP error response handlers."""

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from starlette.exceptions import HTTPException as StarletteHTTPException

from src.service.otp_service import (
    OTPAttemptsCooldownError,
    OTPAttemptsExceededError,
    OTPChallengeNotFoundError,
    OTPDomainError,
    OTPGrantNotFoundError,
    OTPInvalidCodeError,
    OTPPurposeMismatchError,
    OTPRateLimitError,
    OTPResendCooldownError,
)

_OTP_ERROR_RESPONSES: dict[type[OTPDomainError], tuple[int, str]] = {
    OTPChallengeNotFoundError: (
        status.HTTP_400_BAD_REQUEST,
        "OTP was not found or has expired.",
    ),
    OTPPurposeMismatchError: (
        status.HTTP_400_BAD_REQUEST,
        "OTP does not match this operation.",
    ),
    OTPInvalidCodeError: (
        status.HTTP_400_BAD_REQUEST,
        "OTP is invalid.",
    ),
    OTPAttemptsExceededError: (
        status.HTTP_429_TOO_MANY_REQUESTS,
        "OTP verification attempt limit was exceeded.",
    ),
    OTPResendCooldownError: (
        status.HTTP_429_TOO_MANY_REQUESTS,
        "Please wait before requesting another OTP.",
    ),
    OTPRateLimitError: (
        status.HTTP_429_TOO_MANY_REQUESTS,
        "OTP request limit was exceeded.",
    ),
    OTPAttemptsCooldownError: (
        status.HTTP_429_TOO_MANY_REQUESTS,
        "OTP verification is temporarily unavailable.",
    ),
    OTPGrantNotFoundError: (
        status.HTTP_400_BAD_REQUEST,
        "OTP verification has expired or was already used.",
    ),
}


class ErrorResponseDTO(BaseModel):
    """Stable JSON error envelope returned by backend endpoints."""

    status_code: int
    detail: str
    path: str


def create_error_response(
    *,
    status_code: int,
    detail: str,
    path: str,
) -> JSONResponse:
    """Build the shared JSON error response payload."""
    payload = ErrorResponseDTO(
        status_code=status_code,
        detail=detail,
        path=path,
    )
    return JSONResponse(status_code=status_code, content=payload.model_dump())


async def http_exception_handler(
    request: Request,
    exception: Exception,
) -> JSONResponse:
    """Convert FastAPI and Starlette HTTP failures to the shared envelope."""
    if isinstance(exception, StarletteHTTPException):
        return create_error_response(
            status_code=exception.status_code,
            detail=str(exception.detail),
            path=request.url.path,
        )
    return create_error_response(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="Unexpected HTTP exception.",
        path=request.url.path,
    )


async def validation_exception_handler(
    request: Request,
    exception: Exception,
) -> JSONResponse:
    """Return field-specific, non-sensitive request validation feedback."""
    detail = "Input is invalid."
    if isinstance(exception, RequestValidationError):
        is_email_error = any(
            error.get("loc") == ("body", "email") for error in exception.errors()
        )
        if is_email_error:
            detail = "Email must be valid"
        else:
            detail = _format_validation_errors(exception)
    return create_error_response(
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
        detail=detail,
        path=request.url.path,
    )


def _format_validation_errors(exception: RequestValidationError) -> str:
    """Format validation locations and messages without returning submitted values."""
    details = [
        f"{'.'.join(str(part) for part in error['loc'])}: {error['msg']}"
        for error in exception.errors()
    ]
    return "; ".join(details) or "Input is invalid."


async def otp_domain_exception_handler(
    request: Request,
    exception: Exception,
) -> JSONResponse:
    """Translate OTP domain outcomes to stable HTTP client errors."""
    if not isinstance(exception, OTPDomainError):
        return create_error_response(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unexpected OTP exception.",
            path=request.url.path,
        )
    status_code, detail = _OTP_ERROR_RESPONSES.get(
        type(exception),
        (status.HTTP_400_BAD_REQUEST, "OTP request could not be completed."),
    )
    return create_error_response(
        status_code=status_code,
        detail=detail,
        path=request.url.path,
    )


async def unhandled_exception_handler(
    request: Request,
    _exception: Exception,
) -> JSONResponse:
    """Hide unexpected exception details behind a generic HTTP 500 response."""
    return create_error_response(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="Internal server error.",
        path=request.url.path,
    )


def register_exception_handlers(application: FastAPI) -> None:
    """Register all application exception handlers on a FastAPI instance."""
    application.add_exception_handler(StarletteHTTPException, http_exception_handler)
    application.add_exception_handler(
        RequestValidationError, validation_exception_handler
    )
    application.add_exception_handler(OTPDomainError, otp_domain_exception_handler)
    application.add_exception_handler(Exception, unhandled_exception_handler)
