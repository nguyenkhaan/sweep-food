"""Response DTOs for administrator account operations."""

from uuid import UUID

from pydantic import BaseModel

from src.model.enum_model import AccountStatus


class BannedUserDTO(BaseModel):
    """Account identity and status after an administrator ban."""

    user_id: UUID
    status: AccountStatus
