"""Role-based authorization dependency factory."""

from collections.abc import Callable
from typing import Annotated

from fastapi import Depends, HTTPException, status

from src.middleware.auth_middleware import AuthenticatedUser, require_authentication
from src.model.enum_model import UserRole


def require_role(
    *allowed_roles: UserRole,
) -> Callable[[AuthenticatedUser], AuthenticatedUser]:
    """Require the authenticated user to hold at least one allowed role."""
    if not allowed_roles:
        raise ValueError("At least one role is required")

    def verify_role(
        principal: Annotated[
            AuthenticatedUser,
            Depends(require_authentication),
        ],
    ) -> AuthenticatedUser:
        if not set(principal.roles).intersection(allowed_roles):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient role",
            )
        return principal

    return verify_role
