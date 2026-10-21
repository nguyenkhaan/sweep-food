"""Response DTOs for health and diagnostics endpoints."""

from typing import Literal

from pydantic import BaseModel


class LivenessResponseDTO(BaseModel):
    """Successful liveness response payload."""

    status: Literal["ok"] = "ok"
    message: str


class AIReadinessResponseDTO(BaseModel):
    """Readiness of the AI workloads hosted inside the backend process."""

    status: Literal["ready"] = "ready"
    catalog_revision: str
    recipe_count: int
    ranker_model: str
    model_version: str
    ocr_configured: bool
    asr_configured: bool
    latency_ms: float
