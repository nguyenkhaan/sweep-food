"""Response DTOs for health and diagnostics endpoints."""

from typing import Literal

from pydantic import BaseModel


class LivenessResponseDTO(BaseModel):
    """Successful liveness response payload."""

    status: Literal["ok"] = "ok"
    message: str
