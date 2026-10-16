"""Unit and route contracts for persisted FreshCheck batch assessments."""

from collections.abc import Sequence
from datetime import UTC, datetime
from types import SimpleNamespace
from typing import cast
from uuid import UUID

import httpx
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.app import app
from src.db import get_db_session
from src.middleware.auth_middleware import AuthenticatedUser, require_authentication
from src.model.enum_model import (
    ExpirationSource,
    MeasurementUnit,
    StorageMode,
    UserRole,
)
from src.model.freshcheck_assessment_model import FreshCheckAssessmentModel
from src.model.inventory_ledger_entry_model import InventoryLedgerEntryModel
from src.module.freshness.freshness_dependency import get_freshness_assessment_service
from src.module.freshness.freshness_dto import (
    FreshnessAssessmentRequestDTO,
    FreshnessAssessmentResponseDTO,
)
from src.module.freshness.freshness_service import (
    FreshCheckAssessmentInputError,
    FreshCheckMappingUnavailableError,
    FreshnessAssessmentService,
)
from src.module.inventory.inventory_service import InventoryBatchNotFoundError

BATCH_ID = UUID("00000000-0000-0000-0000-000000000010")
MASTER_INGREDIENT_ID = UUID("00000000-0000-0000-0000-000000000011")
USER_ID = UUID("00000000-0000-0000-0000-000000000012")
NOW = datetime(2026, 10, 16, 10, tzinfo=UTC)


class FakeScalarResult:
    """Expose the scalar result shape consumed by the KB repository."""

    def __init__(self, rows: Sequence[object]) -> None:
        self._rows = list(rows)

    def all(self) -> list[object]:
        """Return configured ORM-like rows."""
        return self._rows


class FakeTransaction:
    """Track the transaction scope used by one assessment."""

    def __init__(self, session: "FakeAssessmentSession") -> None:
        self._session = session

    async def __aenter__(self) -> None:
        self._session.transaction_count += 1

    async def __aexit__(self, exc_type: object, exc: object, traceback: object) -> None:
        self._session.committed = exc_type is None


class FakeExecuteResult:
    """Return the one locked batch configured for a service call."""

    def __init__(self, batch: object | None) -> None:
        self._batch = batch

    def scalar_one_or_none(self) -> object | None:
        """Mirror SQLAlchemy's ownership-constrained lookup result."""
        return self._batch


class FakeAssessmentSession:
    """Minimal async-session fake for assessment unit tests."""

    def __init__(
        self,
        *,
        batch: object | None,
        mapping: object | None = None,
        existing: object | None = None,
    ) -> None:
        self.batch = batch
        self.mapping = mapping or SimpleNamespace(freshcheck_ingredient_id="rau_muong")
        self.existing = existing
        self.added: list[object] = []
        self.committed = False
        self.executed: list[object] = []
        self.transaction_count = 0
        self._scalar_calls = 0
        self._scalars_calls = 0

    def begin(self) -> FakeTransaction:
        """Start the transaction that must contain every mutation."""
        return FakeTransaction(self)

    async def execute(self, statement: object) -> FakeExecuteResult:
        """Capture the locked batch lookup."""
        self.executed.append(statement)
        return FakeExecuteResult(self.batch)

    async def scalar(self, _statement: object) -> object | None:
        """Return existing assessment, active KB, then reviewed mapping."""
        values = (self.existing, SimpleNamespace(kb_version="0.3.0"), self.mapping)
        value = values[self._scalar_calls]
        self._scalar_calls += 1
        return value

    async def scalars(self, _statement: object) -> FakeScalarResult:
        """Return the active archetype and ingredient rows."""
        rows = (
            [
                SimpleNamespace(
                    archetype_id="LEAFY_VEG",
                    sensory_tiers={
                        "tier_1_fresh": {"score_range": [8, 10]},
                        "tier_2_acceptable": {"score_range": [5, 7.99]},
                        "tier_3_warning": {"score_range": [1, 4.99]},
                        "tier_4_spoiled": {"score_range": [0, 0.99]},
                    },
                    inspection_rubric=[
                        {
                            "axis": "appearance",
                            "question_vi": "Lá có còn tươi không?",
                            "options": [
                                {"value": "fresh", "label_vi": "Tươi"},
                                {
                                    "value": "spoiled",
                                    "label_vi": "Hỏng",
                                    "hard_stop": True,
                                    "reason_vi": "Có dấu hiệu hỏng",
                                },
                            ],
                        }
                    ],
                    preservation_protocols={"prep": ["Rửa trước khi dùng"]},
                )
            ]
            if self._scalars_calls == 0
            else [
                SimpleNamespace(
                    freshcheck_ingredient_id="rau_muong",
                    archetype_id="LEAFY_VEG",
                    base_shelf_life_hours={"fridge_2_4c": 72},
                )
            ]
        )
        self._scalars_calls += 1
        return FakeScalarResult(rows)

    def add(self, instance: object) -> None:
        """Stage an immutable assessment or its paired audit record."""
        self.added.append(instance)

    async def flush(self) -> None:
        """Match the service persistence boundary."""


def _batch(*, manufacturer_expiry: bool = False) -> SimpleNamespace:
    """Build one owned raw-ingredient batch with stable time inputs."""
    return SimpleNamespace(
        id=BATCH_ID,
        user_id=USER_ID,
        master_ingredient_id=MASTER_INGREDIENT_ID,
        storage_mode=StorageMode.REFRIGERATED,
        purchased_at=datetime(2026, 10, 15, 10, tzinfo=UTC),
        stored_at=None,
        expires_at=(
            datetime(2026, 10, 20, 10, tzinfo=UTC) if manufacturer_expiry else None
        ),
        expiration_source=(
            ExpirationSource.MANUFACTURER
            if manufacturer_expiry
            else ExpirationSource.UNKNOWN
        ),
        current_quantity=1.0,
        unit=MeasurementUnit.KG,
    )


def _service(session: FakeAssessmentSession) -> FreshnessAssessmentService:
    """Build the assessment service with the fake async session."""
    return FreshnessAssessmentService(cast(AsyncSession, session))


@pytest.mark.anyio
async def test_assessment_persists_expiry_and_zero_delta_audit_in_one_transaction() -> (
    None
):
    """A numeric assessment safely applies its lower-bound expiry exactly once."""
    batch = _batch()
    session = FakeAssessmentSession(batch=batch)

    response = await _service(session).assess_batch(
        USER_ID,
        BATCH_ID,
        FreshnessAssessmentRequestDTO(answers={"appearance": "fresh"}),
        "assessment-1",
        now=NOW,
    )

    assert session.committed is True
    assert session.transaction_count == 1
    assert "FOR UPDATE" in str(session.executed[0])
    assert batch.expiration_source is ExpirationSource.ESTIMATED
    assert batch.expires_at == response.expires_at
    assert batch.expires_at is not None and batch.expires_at > NOW
    assert isinstance(session.added[0], FreshCheckAssessmentModel)
    assert isinstance(session.added[1], InventoryLedgerEntryModel)
    assert session.added[1].quantity_delta == 0.0


@pytest.mark.anyio
async def test_assessment_never_overrides_manufacturer_expiry() -> None:
    """Printed manufacturer expiry wins over FreshCheck's calculated estimate."""
    batch = _batch(manufacturer_expiry=True)
    session = FakeAssessmentSession(batch=batch)

    response = await _service(session).assess_batch(
        USER_ID,
        BATCH_ID,
        FreshnessAssessmentRequestDTO(answers={"appearance": "fresh"}),
        "assessment-2",
        now=NOW,
    )

    assert response.expires_at == datetime(2026, 10, 20, 10, tzinfo=UTC)
    assert batch.expiration_source is ExpirationSource.MANUFACTURER
    assert session.added[0].applied_expires_at is None


@pytest.mark.anyio
async def test_hard_stop_sets_expiry_without_discarding_quantity() -> None:
    """A safety hard-stop expires the batch but never changes its balance."""
    batch = _batch()
    session = FakeAssessmentSession(batch=batch)

    response = await _service(session).assess_batch(
        USER_ID,
        BATCH_ID,
        FreshnessAssessmentRequestDTO(answers={"appearance": "spoiled"}),
        "assessment-3",
        now=NOW,
    )

    assert response.blocked is True
    assert batch.expires_at == NOW
    assert batch.current_quantity == 1.0
    assert session.added[1].quantity_delta == 0.0


@pytest.mark.anyio
async def test_assessment_hides_unowned_or_unknown_batch() -> None:
    """Owner-scoped locking returns the normal inventory 404 for other users."""
    session = FakeAssessmentSession(batch=None)

    with pytest.raises(InventoryBatchNotFoundError):
        await _service(session).assess_batch(
            USER_ID,
            BATCH_ID,
            FreshnessAssessmentRequestDTO(),
            "assessment-4",
            now=NOW,
        )

    assert session.added == []


@pytest.mark.anyio
async def test_assessment_rejects_unknown_mapping_without_persistence() -> None:
    """Only reviewed mappings may produce a persisted FreshCheck assessment."""
    session = FakeAssessmentSession(batch=_batch(), mapping=None)
    session.mapping = None

    with pytest.raises(FreshCheckMappingUnavailableError):
        await _service(session).assess_batch(
            USER_ID,
            BATCH_ID,
            FreshnessAssessmentRequestDTO(),
            "assessment-5",
            now=NOW,
        )

    assert session.added == []


@pytest.mark.anyio
async def test_assessment_rejects_an_answer_outside_the_active_rubric() -> None:
    """An unknown sensory value cannot silently become a fresh default decision."""
    session = FakeAssessmentSession(batch=_batch())

    with pytest.raises(FreshCheckAssessmentInputError):
        await _service(session).assess_batch(
            USER_ID,
            BATCH_ID,
            FreshnessAssessmentRequestDTO(answers={"appearance": "unexpected"}),
            "assessment-invalid-answer",
            now=NOW,
        )

    assert session.added == []


@pytest.mark.anyio
async def test_assessment_retry_returns_immutable_result_without_a_second_write() -> (
    None
):
    """A repeated idempotency key replays history without another expiry audit."""
    existing = SimpleNamespace(
        id=UUID("00000000-0000-0000-0000-000000000014"),
        inventory_batch_id=BATCH_ID,
        kb_version="0.3.0",
        freshcheck_ingredient_id="rau_muong",
        rule_version="freshcheck-infer-v1.0",
        outcome={
            "archetype_id": "LEAFY_VEG",
            "blocked": False,
            "tier": "tier_1_fresh",
            "score": 10.0,
            "remaining_hours_min": 24.0,
            "remaining_hours_max": 48.0,
            "remaining_days_min": 1,
            "remaining_days_max": 2,
            "reason_code": None,
            "reasons_vi": [],
            "storage_tips_vi": [],
            "expires_at": NOW.isoformat(),
        },
        claims=["claim-1"],
    )
    batch = _batch()
    batch.expires_at = datetime(2026, 10, 17, 10, tzinfo=UTC)
    session = FakeAssessmentSession(batch=batch, existing=existing)

    response = await _service(session).assess_batch(
        USER_ID,
        BATCH_ID,
        FreshnessAssessmentRequestDTO(),
        "assessment-retry",
        now=NOW,
    )

    assert response.assessment_id == existing.id
    assert response.expires_at == NOW
    assert session.added == []
    assert batch.expiration_source is ExpirationSource.UNKNOWN


class StubAssessmentService:
    """Return a controlled assessment response from the route layer."""

    async def assess_batch(
        self,
        _user_id: UUID,
        _batch_id: UUID,
        _body: FreshnessAssessmentRequestDTO,
        _idempotency_key: str,
    ) -> FreshnessAssessmentResponseDTO:
        """Return a valid persisted assessment contract."""
        return FreshnessAssessmentResponseDTO(
            assessment_id=UUID("00000000-0000-0000-0000-000000000013"),
            batch_id=BATCH_ID,
            kb_version="0.3.0",
            freshcheck_ingredient_id="rau_muong",
            archetype_id="LEAFY_VEG",
            blocked=False,
            tier="tier_1_fresh",
            score=10.0,
            remaining_hours_min=24.0,
            remaining_hours_max=48.0,
            remaining_days_min=1,
            remaining_days_max=2,
            reason_code=None,
            reasons_vi=(),
            storage_tips_vi=(),
            claims=(),
            rule_version="freshcheck-infer-v1.0",
            expires_at=NOW,
        )


@pytest.fixture(name="assessment_routes")
def _assessment_routes() -> object:
    """Install authenticated route dependencies without a database."""

    async def authenticated_user() -> AuthenticatedUser:
        return AuthenticatedUser(USER_ID, (UserRole.USER,))

    async def assessment_service() -> StubAssessmentService:
        return StubAssessmentService()

    async def database_session() -> object:
        yield object()

    app.dependency_overrides[require_authentication] = authenticated_user
    app.dependency_overrides[get_freshness_assessment_service] = assessment_service
    app.dependency_overrides[get_db_session] = database_session
    try:
        yield None
    finally:
        app.dependency_overrides.pop(require_authentication, None)
        app.dependency_overrides.pop(get_freshness_assessment_service, None)
        app.dependency_overrides.pop(get_db_session, None)


@pytest.mark.anyio
async def test_assessment_route_requires_authentication(
    api_client: httpx.AsyncClient,
    assessment_database_session: object,
) -> None:
    """Anonymous callers cannot assess another user's batch."""
    assert assessment_database_session is None
    response = await api_client.post(
        f"/api/freshness/batches/{BATCH_ID}/assessment",
        headers={"Idempotency-Key": "route-1"},
        json={"answers": {}},
    )

    assert response.status_code == 401


@pytest.fixture(name="assessment_database_session")
def _assessment_database_session() -> object:
    """Avoid initializing an application database for the auth-only contract test."""

    async def database_session() -> object:
        yield object()

    app.dependency_overrides[get_db_session] = database_session
    try:
        yield None
    finally:
        app.dependency_overrides.pop(get_db_session, None)


@pytest.mark.anyio
async def test_assessment_route_requires_an_idempotency_key(
    api_client: httpx.AsyncClient,
    assessment_routes: object,
) -> None:
    """The route rejects a write that cannot be safely retried."""
    assert assessment_routes is None
    response = await api_client.post(
        f"/api/freshness/batches/{BATCH_ID}/assessment",
        json={"answers": {}},
    )

    assert response.status_code == 422


@pytest.mark.anyio
async def test_assessment_route_rejects_naive_purchased_at(
    api_client: httpx.AsyncClient,
    assessment_routes: object,
) -> None:
    """Assessment timing must be timezone-aware before it reaches the service."""
    assert assessment_routes is None
    response = await api_client.post(
        f"/api/freshness/batches/{BATCH_ID}/assessment",
        headers={"Idempotency-Key": "route-2"},
        json={"purchased_at": "2026-10-16T10:00:00", "answers": {}},
    )

    assert response.status_code == 422
