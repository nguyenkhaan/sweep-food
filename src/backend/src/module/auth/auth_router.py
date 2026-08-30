"""Phone/password authentication and session API routes."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Request, Response, status
from fastapi.responses import PlainTextResponse

from src.middleware.auth_middleware import AuthenticatedUser, require_authentication
from src.module.auth.auth_dependency import get_auth_service
from src.module.auth.auth_dto import (
    AccessTokenDTO,
    AuthSessionDTO,
    LoginRequestDTO,
    LogoutRequestDTO,
    MessageResponseDTO,
    OTPIssueResponseDTO,
    PasswordOTPRequestDTO,
    RefreshTokenRequestDTO,
    RegisterRequestDTO,
    TokenPairDTO,
    VerifyPasswordRequestDTO,
    VerifyRegisterRequestDTO,
)
from src.module.auth.auth_service import AuthService

auth_router = APIRouter(prefix="/auth", tags=["auth"])


def get_user_agent(request: Request) -> str | None:
    """Return the client user-agent header when it is present."""
    return request.headers.get("User-Agent")


@auth_router.post("/register", response_model=OTPIssueResponseDTO)
async def post_register(
    body: RegisterRequestDTO,
    service: Annotated[AuthService, Depends(get_auth_service)],
) -> OTPIssueResponseDTO:
    """Create an unverified user and issue a registration OTP."""
    return await service.register(body)


@auth_router.post("/register/resend-otp", response_model=OTPIssueResponseDTO)
async def post_resend_register_otp(
    body: PasswordOTPRequestDTO,
    service: Annotated[AuthService, Depends(get_auth_service)],
) -> OTPIssueResponseDTO:
    """Issue a replacement OTP for an existing unverified registration."""
    return await service.resend_register_otp(body.phone)


@auth_router.post("/verify/register", response_class=PlainTextResponse)
async def post_verify_register(
    body: VerifyRegisterRequestDTO,
    service: Annotated[AuthService, Depends(get_auth_service)],
) -> str:
    """Verify registration OTP and return a plain-text acknowledgement."""
    await service.verify_register(body)
    return "verify account successfully"


@auth_router.post("/password/reset", response_model=OTPIssueResponseDTO)
async def post_password_reset(
    body: PasswordOTPRequestDTO,
    service: Annotated[AuthService, Depends(get_auth_service)],
) -> OTPIssueResponseDTO:
    """Issue the OTP required to reset a password."""
    return await service.request_password_reset(body)


@auth_router.post(
    "/password/change",
    response_model=OTPIssueResponseDTO,
)
async def post_password_change(
    user: Annotated[AuthenticatedUser, Depends(require_authentication)],
    service: Annotated[AuthService, Depends(get_auth_service)],
) -> OTPIssueResponseDTO:
    """Issue a password-change OTP for the authenticated user."""
    return await service.request_password_change(user.user_id)


@auth_router.post("/verify/change-password", response_model=MessageResponseDTO)
async def post_verify_change_password(
    body: VerifyPasswordRequestDTO,
    service: Annotated[AuthService, Depends(get_auth_service)],
) -> MessageResponseDTO:
    """Verify a password OTP, replace the password, and revoke sessions."""
    await service.verify_change_password(body)
    return MessageResponseDTO(message="Password changed successfully")


@auth_router.post("/login", response_model=TokenPairDTO)
async def post_login(
    body: LoginRequestDTO,
    request: Request,
    service: Annotated[AuthService, Depends(get_auth_service)],
) -> TokenPairDTO:
    """Sign in an active account using its phone and password."""
    return await service.login(body, get_user_agent(request))


@auth_router.post("/token/refresh", response_model=AccessTokenDTO)
async def post_token_refresh(
    body: RefreshTokenRequestDTO,
    service: Annotated[AuthService, Depends(get_auth_service)],
) -> AccessTokenDTO:
    """Issue a new access JWT from a valid refresh JWT."""
    return await service.refresh_access_token(body.refresh_token)


@auth_router.post("/logout", response_class=PlainTextResponse)
async def post_logout(
    body: LogoutRequestDTO,
    user: Annotated[AuthenticatedUser, Depends(require_authentication)],
    service: Annotated[AuthService, Depends(get_auth_service)],
) -> str:
    """Revoke the caller's refresh session and confirm logout as plain text."""
    await service.logout(user.user_id, body.refresh_token)
    return "Logout successfully"


@auth_router.get(
    "/sessions",
    response_model=list[AuthSessionDTO],
)
async def get_sessions(
    user: Annotated[AuthenticatedUser, Depends(require_authentication)],
    service: Annotated[AuthService, Depends(get_auth_service)],
) -> list[AuthSessionDTO]:
    """List active sessions that belong to the caller."""
    return await service.list_sessions(user.user_id)


@auth_router.delete(
    "/sessions/{session_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_session(
    session_id: UUID,
    user: Annotated[AuthenticatedUser, Depends(require_authentication)],
    service: Annotated[AuthService, Depends(get_auth_service)],
) -> Response:
    """Revoke one active session owned by the caller."""
    await service.revoke_session(user.user_id, session_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
