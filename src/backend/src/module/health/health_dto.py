"""Response DTOs for health and diagnostics endpoints."""

from typing import Literal

from pydantic import BaseModel


class LivenessResponseDTO(BaseModel):
    """Successful liveness response payload."""

    status: Literal["ok"] = "ok"
    message: str


class AIServiceHealthResponseDTO(BaseModel):
    """Readiness response for the configured Sweep Food AI service."""

    service: Literal["sweep-food-ai"] = "sweep-food-ai"
    status: Literal["ready"] = "ready"
    provider: Literal["SWEEP_FOOD_AI"] = "SWEEP_FOOD_AI"
    latency_ms: float
