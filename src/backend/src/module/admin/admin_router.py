"""Administrator-only account management routes."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends

from src.middleware.auth_middleware import AuthenticatedUser
from src.middleware.role_middleware import require_role
from src.model.enum_model import UserRole
from src.module.admin.admin_dependency import get_admin_service
from src.module.admin.admin_dto import BannedUserDTO
from src.module.admin.admin_service import AdminService

admin_router = APIRouter(prefix="/admin", tags=["admin"])


@admin_router.patch(
    "/user/banned/{user_id}",
    response_model=BannedUserDTO,
)
async def patch_banned_user(
    user_id: UUID,
    _admin: Annotated[AuthenticatedUser, Depends(require_role(UserRole.ADMIN))],
    service: Annotated[AdminService, Depends(get_admin_service)],
) -> BannedUserDTO:
    """Ban one existing user account."""
    return await service.ban_user(user_id)
