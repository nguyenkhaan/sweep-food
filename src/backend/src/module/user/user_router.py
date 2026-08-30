"""Authenticated current-user profile and verified-contact API routes."""

from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.responses import PlainTextResponse

from src.middleware.auth_middleware import AuthenticatedUser, require_authentication
from src.module.user.user_dependency import get_user_service
from src.module.user.user_dto import (
    CurrentUserDTO,
    EmailRequestDTO,
    EmailVerificationRequestDTO,
    PhoneRequestDTO,
    PhoneVerificationRequestDTO,
    UpdateUserProfileRequestDTO,
    UserOTPIssueResponseDTO,
    UserProfileDTO,
)
from src.module.user.user_service import UserService

user_router = APIRouter(prefix="/users", tags=["users"])


@user_router.get(
    "/me",
    response_model=CurrentUserDTO,
    summary="Get current identity",
    description="Return the authenticated user's ID and role claims for the frontend.",
)
async def get_current_user(
    user: Annotated[AuthenticatedUser, Depends(require_authentication)],
    service: Annotated[UserService, Depends(get_user_service)],
) -> CurrentUserDTO:
    """Return basic identity extracted from the validated access JWT."""
    return service.get_current_user(user.user_id, [role.value for role in user.roles])


@user_router.get(
    "/profile",
    response_model=UserProfileDTO,
    summary="Get my profile",
    description="Return the authenticated user's profile and verified contact details.",
)
async def get_profile(
    user: Annotated[AuthenticatedUser, Depends(require_authentication)],
    service: Annotated[UserService, Depends(get_user_service)],
) -> UserProfileDTO:
    """Return the authenticated user's full profile."""
    return await service.get_profile(user.user_id)


@user_router.patch(
    "/profile",
    response_model=UserProfileDTO,
    summary="Update my profile",
    description="Update the authenticated user's display name or preferences.",
)
async def patch_profile(
    body: UpdateUserProfileRequestDTO,
    user: Annotated[AuthenticatedUser, Depends(require_authentication)],
    service: Annotated[UserService, Depends(get_user_service)],
) -> UserProfileDTO:
    """Update only fields owned by the authenticated user."""
    return await service.update_profile(user.user_id, body)


@user_router.post(
    "/me/email/request-verification",
    response_model=UserOTPIssueResponseDTO,
    summary="Request email verification",
    description="Send an OTP to add or replace the authenticated user's email address.",
)
async def post_request_email_verification(
    body: EmailRequestDTO,
    user: Annotated[AuthenticatedUser, Depends(require_authentication)],
    service: Annotated[UserService, Depends(get_user_service)],
) -> UserOTPIssueResponseDTO:
    """Issue an OTP for the requested email address."""
    return await service.request_email_verification(user.user_id, body)


@user_router.post(
    "/me/email/verify",
    response_class=PlainTextResponse,
    summary="Verify email",
    description="Verify the OTP for the email address from the prior request and persist it.",
)
async def post_verify_email(
    body: EmailVerificationRequestDTO,
    user: Annotated[AuthenticatedUser, Depends(require_authentication)],
    service: Annotated[UserService, Depends(get_user_service)],
) -> str:
    """Verify the pending email destination for the current user."""
    await service.verify_email(user.user_id, body)
    return "Verify Change Email successfully"


@user_router.post(
    "/me/phone/request-change",
    response_model=UserOTPIssueResponseDTO,
    summary="Request phone change",
    description="Send an OTP to a new phone number for the authenticated user.",
)
async def post_request_phone_change(
    body: PhoneRequestDTO,
    user: Annotated[AuthenticatedUser, Depends(require_authentication)],
    service: Annotated[UserService, Depends(get_user_service)],
) -> UserOTPIssueResponseDTO:
    """Issue an OTP for the new phone destination."""
    return await service.request_phone_change(user.user_id, body)


@user_router.post(
    "/me/phone/confirm-change",
    response_class=PlainTextResponse,
    summary="Confirm phone change",
    description="Verify the OTP for the prior phone-change request and replace the phone number.",
)
async def post_confirm_phone_change(
    body: PhoneVerificationRequestDTO,
    user: Annotated[AuthenticatedUser, Depends(require_authentication)],
    service: Annotated[UserService, Depends(get_user_service)],
) -> str:
    """Verify the pending phone destination for the current user."""
    await service.confirm_phone_change(user.user_id, body)
    return "Verify Change Phone succesfully"
