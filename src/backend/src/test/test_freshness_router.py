"""Unit and route contracts for the mapped FreshCheck questions API."""

from collections.abc import Sequence
from types import SimpleNamespace
from typing import cast
from uuid import UUID

import httpx
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.app import app
from src.db import get_db_session
from src.middleware.auth_middleware import AuthenticatedUser, require_authentication
from src.model.enum_model import UserRole
from src.module.freshness.freshness_dependency import get_freshness_questions_service
from src.module.freshness.freshness_dto import (
    FreshnessQuestionDTO,
    FreshnessQuestionOptionDTO,
    FreshnessQuestionsResponseDTO,
)
from src.module.freshness.freshness_service import (
    FreshCheckKBUnavailableHTTPError,
    FreshCheckMappingUnavailableError,
    FreshnessQuestionService,
)

MASTER_INGREDIENT_ID = UUID("00000000-0000-0000-0000-000000000001")
USER_ID = UUID("00000000-0000-0000-0000-000000000002")


class FakeScalarResult:
    """Expose the scalar result shape consumed by the KB repository."""

    def __init__(self, rows: Sequence[object]) -> None:
        self._rows = list(rows)

    def all(self) -> list[object]:
        """Return the configured ORM-like rows."""
        return self._rows


class FakeFreshCheckSession:
    """Return an active release, its rows, and an optional reviewed mapping."""

    def __init__(self, active_version: object | None, mapping: object | None) -> None:
        self._active_version = active_version
        self._mapping = mapping
        self._active_version_loaded = False
        self._scalars_calls = 0

    async def scalar(self, _statement: object) -> object | None:
        """Return the active KB first, then the mapping lookup result."""
        if not self._active_version_loaded:
            self._active_version_loaded = True
            return self._active_version
        return self._mapping

    async def scalars(self, _statement: object) -> FakeScalarResult:
        """Return the archetype and ingredient rows for the active release."""
        rows = (
            [
                SimpleNamespace(
                    archetype_id="LEAFY_VEG",
                    sensory_tiers={},
                    inspection_rubric=[
                        {
                            "axis": "appearance",
                            "question_vi": "Lá có còn tươi không?",
                            "options": [
                                {"value": "fresh", "label_vi": "Tươi"},
                                {"value": "wilted", "label_vi": "Héo"},
                            ],
                        }
                    ],
                    preservation_protocols={},
                )
            ]
            if self._scalars_calls == 0
            else [
                SimpleNamespace(
                    freshcheck_ingredient_id="rau_muong",
                    archetype_id="LEAFY_VEG",
                    base_shelf_life_hours={},
                )
            ]
        )
        self._scalars_calls += 1
        return FakeScalarResult(rows)


def _service(*, mapping_present: bool = True) -> FreshnessQuestionService:
    """Build the service around a release containing one mapped ingredient."""
    active_version = SimpleNamespace(kb_version="0.3.0")
    reviewed_mapping = (
        SimpleNamespace(freshcheck_ingredient_id="rau_muong")
        if mapping_present
        else None
    )
    session = FakeFreshCheckSession(active_version, reviewed_mapping)
    return FreshnessQuestionService(cast(AsyncSession, session))


@pytest.mark.anyio
async def test_questions_use_the_active_reviewed_mapping() -> None:
    """The response exposes the active KB rubric through a reviewed catalog mapping."""
    response = await _service().questions(MASTER_INGREDIENT_ID)

    assert response.kb_version == "0.3.0"
    assert response.freshcheck_ingredient_id == "rau_muong"
    assert response.archetype_id == "LEAFY_VEG"
    assert response.questions[0].axis == "appearance"
    assert response.questions[0].default == "fresh"


@pytest.mark.anyio
async def test_questions_reject_an_unmapped_master_ingredient() -> None:
    """Unmapped catalog ingredients never receive an inferred numeric rubric."""
    with pytest.raises(FreshCheckMappingUnavailableError):
        await _service(mapping_present=False).questions(MASTER_INGREDIENT_ID)


@pytest.mark.anyio
async def test_questions_reject_when_no_kb_is_active() -> None:
    """FreshCheck fails independently when the database has no active release."""
    session = FakeFreshCheckSession(None, None)
    service = FreshnessQuestionService(cast(AsyncSession, session))

    with pytest.raises(FreshCheckKBUnavailableHTTPError):
        await service.questions(MASTER_INGREDIENT_ID)


class StubFreshnessQuestionService:
    """Return a controlled API result without a database dependency."""

    def __init__(self, result: FreshnessQuestionsResponseDTO | Exception) -> None:
        self._result = result

    async def questions(
        self, _master_ingredient_id: UUID
    ) -> FreshnessQuestionsResponseDTO:
        """Return the configured response or raise its domain error."""
        if isinstance(self._result, Exception):
            raise self._result
        return self._result


def _questions_response() -> FreshnessQuestionsResponseDTO:
    """Build one valid mapped rubric response for route testing."""
    return FreshnessQuestionsResponseDTO(
        kb_version="0.3.0",
        freshcheck_ingredient_id="rau_muong",
        archetype_id="LEAFY_VEG",
        questions=(
            FreshnessQuestionDTO(
                axis="appearance",
                question_vi="Lá có còn tươi không?",
                options=(
                    FreshnessQuestionOptionDTO(value="fresh", label_vi="Tươi"),
                    FreshnessQuestionOptionDTO(value="wilted", label_vi="Héo"),
                ),
                default="fresh",
            ),
        ),
    )


@pytest.fixture(name="freshness_routes")
def _freshness_routes(freshness_database_session: object) -> object:
    """Install authenticated route dependencies for API contract tests."""

    async def authenticated_user() -> AuthenticatedUser:
        return AuthenticatedUser(USER_ID, (UserRole.USER,))

    async def mapped_service() -> StubFreshnessQuestionService:
        return StubFreshnessQuestionService(_questions_response())

    app.dependency_overrides[require_authentication] = authenticated_user
    app.dependency_overrides[get_freshness_questions_service] = mapped_service
    try:
        yield None
    finally:
        app.dependency_overrides.pop(require_authentication, None)
        app.dependency_overrides.pop(get_freshness_questions_service, None)


@pytest.fixture(name="freshness_database_session")
def _freshness_database_session() -> object:
    """Avoid starting an application database for route-only contract tests."""

    async def database_session() -> object:
        yield object()

    app.dependency_overrides[get_db_session] = database_session
    try:
        yield None
    finally:
        app.dependency_overrides.pop(get_db_session, None)


@pytest.mark.anyio
async def test_questions_route_requires_authentication(
    api_client: httpx.AsyncClient,
    freshness_database_session: object,
) -> None:
    """The questions route rejects an anonymous request before accessing FreshCheck."""
    assert freshness_database_session is None
    response = await api_client.get(
        "/api/freshness/questions",
        params={"master_ingredient_id": str(MASTER_INGREDIENT_ID)},
    )

    assert response.status_code == 401


@pytest.mark.anyio
async def test_questions_route_returns_a_mapped_rubric(
    api_client: httpx.AsyncClient,
    freshness_routes: object,
) -> None:
    """The route returns an active mapped rubric with a default answer per axis."""
    assert freshness_routes is None
    response = await api_client.get(
        "/api/freshness/questions",
        params={"master_ingredient_id": str(MASTER_INGREDIENT_ID)},
    )

    assert response.status_code == 200
    assert response.json()["freshcheck_ingredient_id"] == "rau_muong"


@pytest.mark.anyio
async def test_questions_route_returns_mapping_error(
    api_client: httpx.AsyncClient,
    freshness_routes: object,
) -> None:
    """The route exposes the required mapping-unavailable domain code."""
    assert freshness_routes is None

    async def unmapped_service() -> StubFreshnessQuestionService:
        return StubFreshnessQuestionService(FreshCheckMappingUnavailableError())

    app.dependency_overrides[get_freshness_questions_service] = unmapped_service
    response = await api_client.get(
        "/api/freshness/questions",
        params={"master_ingredient_id": str(MASTER_INGREDIENT_ID)},
    )

    assert response.status_code == 422
    assert response.json()["detail"] == "MAPPING_UNAVAILABLE"


@pytest.mark.anyio
async def test_questions_route_rejects_an_invalid_master_ingredient_id(
    api_client: httpx.AsyncClient,
    freshness_routes: object,
) -> None:
    """The query parameter accepts only UUID catalog identities."""
    assert freshness_routes is None
    response = await api_client.get(
        "/api/freshness/questions",
        params={"master_ingredient_id": "not-a-uuid"},
    )

    assert response.status_code == 422


def test_questions_route_openapi_declares_bearer_auth() -> None:
    """The API contract advertises BearerAuth on the questions route."""
    app.openapi_schema = None
    schema = app.openapi()
    operation = schema["paths"]["/api/freshness/questions"]["get"]

    assert operation["security"] == [{"BearerAuth": []}]
