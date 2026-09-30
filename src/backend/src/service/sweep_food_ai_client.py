"""Typed HTTP boundary for the internal SweepFood AI service."""

from collections.abc import AsyncGenerator
from dataclasses import dataclass
from types import TracebackType
from typing import Literal, Self, TypeVar
from uuid import UUID

import httpx
from pydantic import BaseModel, ConfigDict, Field, ValidationError

from src.core.setting import (
    AI_ASR_TIMEOUT_SECONDS,
    AI_BASE_URL,
    AI_CONNECT_TIMEOUT_SECONDS,
    AI_OCR_TIMEOUT_SECONDS,
    AI_RECOMMEND_TIMEOUT_SECONDS,
)


class SweepFoodAIError(Exception):
    """Base class for failures while calling the internal AI service."""


class SweepFoodAIUnavailableError(SweepFoodAIError):
    """Raised when the AI service cannot be reached."""


class SweepFoodAITimeoutError(SweepFoodAIError):
    """Raised when the AI service exceeds an operation timeout."""


class SweepFoodAIBadResponseError(SweepFoodAIError):
    """Raised when the AI service returns an unusable response."""


class AIHealthResponseDTO(BaseModel):
    """Fields required to consider the AI process ready."""

    model_config = ConfigDict(extra="ignore")

    warmed_up: bool
    device_name: str
    xgb_device: str
    ocr_device: str


class AIOcrItemDTO(BaseModel):
    """One item returned by the AI OCR boundary."""

    model_config = ConfigDict(extra="ignore")

    name: str = Field(min_length=1)
    quantity_g: float | None = Field(default=None, gt=0)
    confidence: float | None = Field(default=None, ge=0, le=1)
    expiry_date: str | None = None
    production_date: str | None = None
    quantity_source: str | None = None


class AIOcrResponseDTO(BaseModel):
    """Validated AI OCR response used by backend mappers."""

    model_config = ConfigDict(extra="ignore")

    status: Literal["success"]
    source: str | None = None
    engine: str | None = None
    store_name: str | None = None
    raw_text: str
    items: list[AIOcrItemDTO]


class AIAsrItemDTO(BaseModel):
    """One ingredient parsed from an AI speech transcript."""

    model_config = ConfigDict(extra="ignore")

    name: str = Field(min_length=1)
    quantity_g: float | None = Field(default=None, gt=0)
    confidence: float | None = Field(default=None, ge=0, le=1)
    quantity_source: str | None = None


class AIAsrResponseDTO(BaseModel):
    """Validated AI ASR response used by backend mappers."""

    model_config = ConfigDict(extra="ignore")

    status: Literal["success"]
    engine: str
    transcript: str
    items: list[AIAsrItemDTO]


class AIPantryItemDTO(BaseModel):
    """One authenticated inventory item sent to recommendation inference."""

    model_config = ConfigDict(extra="forbid")

    name: str = Field(min_length=1)
    code: str | None = None
    quantity_g: float = Field(default=200, gt=0)
    hours_to_expire: float | None = None
    is_staple: bool = False


class AIRecommendationRequestDTO(BaseModel):
    """Structured recommendation request assembled by the backend."""

    model_config = ConfigDict(extra="forbid")

    items: list[AIPantryItemDTO]
    household_size: float = Field(default=4, gt=0)
    max_cooking_time_min: float = Field(default=45, gt=0)
    scenario_type: str = "custom"
    dietary_restrictions: list[str] = Field(default_factory=list)
    allergies: list[str] = Field(default_factory=list)
    disliked_ingredients: list[str] = Field(default_factory=list)
    preferred_cuisines: list[str] = Field(default_factory=list)


class AIRecommendationIngredientDTO(BaseModel):
    """One matched or missing ingredient in an AI recommendation."""

    model_config = ConfigDict(extra="ignore")

    name: str = Field(min_length=1)
    code: str | None = None
    required_g: float = Field(gt=0)


class AIRecommendationScoreComponentsDTO(BaseModel):
    """Calibrated recommendation signals returned by AI."""

    model_config = ConfigDict(extra="forbid")

    expiration_utilization: float = Field(ge=0, le=1)
    availability: float = Field(ge=0, le=1)
    preference_fit: float = Field(ge=0, le=1)
    purchase_minimization: float = Field(ge=0, le=1)


class AIRecommendationItemDTO(BaseModel):
    """One ranked AI recipe result."""

    model_config = ConfigDict(extra="ignore")

    id: UUID
    name: str = Field(min_length=1)
    score: float = Field(ge=0, le=1)
    score_components: AIRecommendationScoreComponentsDTO
    missing_ingredients: list[AIRecommendationIngredientDTO]
    rescued_items: list[str]


class AIRecommendationResponseDTO(BaseModel):
    """Validated recommendation envelope returned by AI."""

    model_config = ConfigDict(extra="ignore")

    status: Literal["success", "empty"]
    model_version: str = Field(min_length=1)
    catalog_revision: str = Field(min_length=1)
    recommendations: list[AIRecommendationItemDTO]


_ResponseModel = TypeVar("_ResponseModel", bound=BaseModel)


@dataclass(frozen=True, slots=True)
class _RequestBody:
    """Optional request bodies supported by the AI HTTP boundary."""

    json_payload: dict[str, object] | None = None
    files: dict[str, tuple[str, bytes, str]] | None = None
    data: dict[str, str] | None = None


class SweepFoodAIClient:
    """Call the internal SweepFood AI service and validate its responses."""

    def __init__(
        self,
        *,
        base_url: str = AI_BASE_URL,
        connect_timeout_seconds: int = AI_CONNECT_TIMEOUT_SECONDS,
        transport: httpx.AsyncBaseTransport | None = None,
    ) -> None:
        self._connect_timeout_seconds = connect_timeout_seconds
        self._client = httpx.AsyncClient(base_url=base_url, transport=transport)

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(
        self,
        _exception_type: type[BaseException] | None,
        _exception: BaseException | None,
        _traceback: TracebackType | None,
    ) -> None:
        await self.aclose()

    async def aclose(self) -> None:
        """Close the underlying HTTP connection pool."""
        await self._client.aclose()

    async def check_health(self) -> AIHealthResponseDTO:
        """Return validated AI readiness details."""
        payload = await self._request_payload(
            "GET",
            "/api/system/status",
            timeout_seconds=AI_CONNECT_TIMEOUT_SECONDS,
        )
        return self._validate_payload(AIHealthResponseDTO, payload)

    async def extract_ocr(
        self,
        *,
        filename: str,
        content: bytes,
        content_type: str | None,
    ) -> AIOcrResponseDTO:
        """Upload one image to the AI OCR endpoint."""
        payload = await self._request_payload(
            "POST",
            "/api/smart-input/ocr-upload",
            timeout_seconds=AI_OCR_TIMEOUT_SECONDS,
            body=_RequestBody(
                files={
                    "file": (
                        filename,
                        content,
                        content_type or "application/octet-stream",
                    )
                }
            ),
        )
        return self._validate_payload(AIOcrResponseDTO, payload)

    async def extract_asr(
        self,
        *,
        filename: str,
        content: bytes,
        content_type: str | None,
        engine: str = "groq_whisper",
    ) -> AIAsrResponseDTO:
        """Upload one audio file to the AI ASR endpoint."""
        payload = await self._request_payload(
            "POST",
            "/api/smart-input/asr-upload",
            timeout_seconds=AI_ASR_TIMEOUT_SECONDS,
            body=_RequestBody(
                files={
                    "audio": (
                        filename,
                        content,
                        content_type or "application/octet-stream",
                    )
                },
                data={"engine": engine},
            ),
        )
        return self._validate_payload(AIAsrResponseDTO, payload)

    async def recommend(
        self,
        request: AIRecommendationRequestDTO,
    ) -> AIRecommendationResponseDTO:
        """Send one structured pantry to recommendation inference."""
        payload = await self._request_payload(
            "POST",
            "/api/recommend",
            timeout_seconds=AI_RECOMMEND_TIMEOUT_SECONDS,
            body=_RequestBody(
                json_payload=request.model_dump(),
            ),
        )
        return self._validate_payload(AIRecommendationResponseDTO, payload)

    async def _request_payload(
        self,
        method: Literal["GET", "POST"],
        path: str,
        *,
        timeout_seconds: int,
        body: _RequestBody | None = None,
    ) -> object:
        request_body = body or _RequestBody()
        timeout = httpx.Timeout(
            timeout_seconds,
            connect=self._connect_timeout_seconds,
        )
        try:
            response = await self._client.request(
                method,
                path,
                timeout=timeout,
                json=request_body.json_payload,
                files=request_body.files,
                data=request_body.data,
            )
        except httpx.TimeoutException as error:
            raise SweepFoodAITimeoutError("AI service request timed out") from error
        except httpx.RequestError as error:
            raise SweepFoodAIUnavailableError("AI service is unavailable") from error

        if not response.is_success:
            raise SweepFoodAIBadResponseError("AI service returned an error response")
        try:
            payload: object = response.json()
        except ValueError as error:
            raise SweepFoodAIBadResponseError(
                "AI service returned invalid JSON"
            ) from error
        return payload

    @staticmethod
    def _validate_payload(
        model: type[_ResponseModel],
        payload: object,
    ) -> _ResponseModel:
        try:
            return model.model_validate(payload)
        except ValidationError as error:
            raise SweepFoodAIBadResponseError(
                "AI service response violated its contract"
            ) from error


async def get_sweep_food_ai_client() -> AsyncGenerator[SweepFoodAIClient]:
    """Yield one request-scoped AI client and close its connection pool."""
    async with SweepFoodAIClient() as client:
        yield client
