"""Health and protected dependency demonstration endpoints."""

from typing import Annotated

from fastapi import APIRouter, Depends, status
from fastapi.responses import PlainTextResponse

from src.module import health
from src.middleware.auth_middleware import AuthenticatedUser, require_authentication
from src.middleware.role_middleware import require_role
from src.model.enum_model import UserRole
from src.module.health.health_dependency import get_health_service
from src.module.health.health_dto import LivenessResponseDTO
from src.module.health.health_service import HealthService

health_router = APIRouter(prefix="/health", tags=["health"])
_BEARER_SECURITY: dict[str, list[dict[str, list[str]]]] = {
    "security": [{"BearerAuth": []}],
}


def _authenticated_user_response(user: AuthenticatedUser) -> dict[str, object]:
    """Serialize the minimal current-user data returned by auth dependencies."""
    return {
        "user_id": str(user.user_id),
        "roles": [role.value for role in user.roles],
    }


@health_router.get("/liveness", response_model=LivenessResponseDTO)
async def get_liveness(
    service: Annotated[HealthService, Depends(get_health_service)],
) -> LivenessResponseDTO:
    """Return the service liveness response."""
    return service.get_liveness()


@health_router.get("/error")
async def get_error(
    service: Annotated[HealthService, Depends(get_health_service)],
) -> None:
    """Raise the deliberate error used by the common-error smoke test."""
    service.raise_forced_error()


@health_router.get(
    "/text",
    response_class=PlainTextResponse,
    status_code=status.HTTP_200_OK,
)
async def get_text(
    service: Annotated[HealthService, Depends(get_health_service)],
) -> PlainTextResponse:
    """Return the legacy plain-text health response."""
    return PlainTextResponse(content=service.get_text())


@health_router.get("/test-login", openapi_extra=_BEARER_SECURITY)
async def get_test_login(
    user: Annotated[AuthenticatedUser, Depends(require_authentication)],
) -> dict[str, object]:
    """Return current token identity to manually test JWT authentication."""
    return _authenticated_user_response(user)


@health_router.get("/test-role", openapi_extra=_BEARER_SECURITY)
async def get_test_role(
    user: Annotated[
        AuthenticatedUser,
        Depends(require_role(UserRole.ADMIN)),
    ],
) -> dict[str, object]:
    """Return current identity only when it has the ADMIN role."""
    return _authenticated_user_response(user)

@health_router.get("/test-email") 
async def test_email(
    service = Depends(get_health_service)
): 
    await service.send_email() 
    return "Send email successfully" 