"""API contract tests for authenticated inventory routes."""

from datetime import UTC, datetime
from typing import cast
from uuid import UUID

import httpx
import pytest

from src.app import app
from src.db import get_db_session
from src.middleware.auth_middleware import AuthenticatedUser, require_authentication
from src.model.enum_model import (
    ExpirationSource,
    InventoryBatchStatus,
    InventoryBatchType,
    InventoryLedgerEventType,
    InventorySource,
    MeasurementUnit,
    StorageMode,
    UserRole,
)
from src.module.inventory.inventory_dependency import get_inventory_service
from src.module.inventory.inventory_dto import (
    FreshnessState,
    InventoryBatchDTO,
    InventoryBatchListResponseDTO,
    InventoryBatchQueryDTO,
    InventoryBatchSummaryDTO,
    InventoryLedgerEntryDTO,
    InventoryLedgerListResponseDTO,
    InventoryLedgerQueryDTO,
    InventorySummaryResponseDTO,
)

USER_ID = UUID("018f0f90-26e6-7ce7-8f61-8769f9e5b101")
BATCH_ID = UUID("018f0f90-26e6-7ce7-8f61-8769f9e5b102")
INGREDIENT_ID = UUID("018f0f90-26e6-7ce7-8f61-8769f9e5b103")
LEDGER_ID = UUID("018f0f90-26e6-7ce7-8f61-8769f9e5b104")
NOW = datetime(2026, 9, 1, 9, 0, tzinfo=UTC)


def _batch(*, quantity: float = 500.0) -> InventoryBatchDTO:
    return InventoryBatchDTO(
        id=BATCH_ID,
        master_ingredient_id=INGREDIENT_ID,
        custom_name=None,
        ingredient_name="Spinach",
        batch_type=InventoryBatchType.RAW_INGREDIENT,
        initial_quantity=500.0,
        current_quantity=quantity,
        unit=MeasurementUnit.GRAM,
        storage_mode=StorageMode.REFRIGERATED,
        status=InventoryBatchStatus.ACTIVE,
        purchased_at=NOW,
        packaged_at=None,
        stored_at=NOW,
        expires_at=NOW,
        expiration_source=ExpirationSource.MANUFACTURER,
        freshness=FreshnessState.EXPIRING_SOON,
        unit_cost=25000.0,
        note=None,
        media_url=None,
        source=InventorySource.MANUAL,
        source_cooking_session_id=None,
        created_at=NOW,
        updated_at=NOW,
        archived_at=None,
    )


class FakeInventoryService:
    """Return deterministic values while route wiring is exercised."""

    async def create_batch(
        self, user_id: UUID, _body: object, key: str
    ) -> InventoryBatchDTO:
        """Return a created batch for route contract verification."""
        assert user_id == USER_ID
        assert key == "create-1"
        return _batch()

    async def list_batches(
        self, user_id: UUID, _query: InventoryBatchQueryDTO
    ) -> InventoryBatchListResponseDTO:
        """Return one stable batch page."""
        assert user_id == USER_ID
        assert _query.batch_status is InventoryBatchStatus.ACTIVE
        assert _query.storage_mode is StorageMode.REFRIGERATED
        return InventoryBatchListResponseDTO(
            items=[_batch()], total=1, page=1, per_page=20
        )

    async def get_batch(self, user_id: UUID, batch_id: UUID) -> InventoryBatchDTO:
        """Return one owned batch."""
        assert user_id == USER_ID
        assert batch_id == BATCH_ID
        return _batch()

    async def update_batch(
        self, _user_id: UUID, _batch_id: UUID, _body: object, _key: str
    ) -> InventoryBatchDTO:
        """Return updated metadata without persistence."""
        return _batch()

    async def archive_batch(
        self,
        _user_id: UUID,
        _batch_id: UUID,
        key: str,
        reason: str,
    ) -> None:
        """Accept an archive request."""
        assert key == "archive-1"
        assert reason == "No longer tracking"

    async def adjust_batch(
        self, _user_id: UUID, _batch_id: UUID, _body: object, key: str
    ) -> InventoryBatchDTO:
        """Return the deterministic adjusted balance."""
        assert key == "adjust-1"
        return _batch(quantity=300.0)

    async def consume_batch(
        self, _user_id: UUID, _batch_id: UUID, _body: object, key: str
    ) -> InventoryBatchDTO:
        """Return the deterministic manually consumed balance."""
        assert key == "consume-1"
        return _batch(quantity=200.0)

    async def move_batch(
        self, _user_id: UUID, _batch_id: UUID, _body: object, key: str
    ) -> InventoryBatchDTO:
        """Accept a storage move request."""
        assert key == "move-1"
        return _batch()

    async def get_summary(self, user_id: UUID) -> InventorySummaryResponseDTO:
        """Return one aggregate inventory row."""
        assert user_id == USER_ID
        return InventorySummaryResponseDTO(
            items=[
                InventoryBatchSummaryDTO(
                    master_ingredient_id=INGREDIENT_ID,
                    custom_name=None,
                    ingredient_name="Spinach",
                    quantity=0.5,
                    unit=MeasurementUnit.KG,
                    batch_count=1,
                    expiring_soon_count=1,
                    expired_count=0,
                )
            ]
        )

    async def list_ledger(
        self, user_id: UUID, _query: InventoryLedgerQueryDTO
    ) -> InventoryLedgerListResponseDTO:
        """Return one immutable ledger page."""
        assert user_id == USER_ID
        assert _query.batch_id == BATCH_ID
        assert _query.event_type is InventoryLedgerEventType.INITIAL_STOCK
        return InventoryLedgerListResponseDTO(
            items=[
                InventoryLedgerEntryDTO(
                    id=LEDGER_ID,
                    inventory_batch_id=BATCH_ID,
                    event_type=InventoryLedgerEventType.INITIAL_STOCK,
                    quantity_before=0.0,
                    quantity_delta=500.0,
                    quantity_after=500.0,
                    unit=MeasurementUnit.GRAM,
                    cooking_session_id=None,
                    idempotency_key="create-1",
                    reason="Manual batch creation",
                    created_at=NOW,
                )
            ],
            total=1,
            page=1,
            per_page=20,
        )


@pytest.fixture(name="inventory_routes")
async def _inventory_routes() -> object:
    fake_service = FakeInventoryService()

    async def get_fake_inventory_service() -> FakeInventoryService:
        return fake_service

    async def get_authenticated_user() -> AuthenticatedUser:
        return AuthenticatedUser(USER_ID, (UserRole.USER,))

    async def get_fake_db_session() -> object:
        yield object()

    app.dependency_overrides[get_inventory_service] = get_fake_inventory_service
    app.dependency_overrides[require_authentication] = get_authenticated_user
    app.dependency_overrides[get_db_session] = get_fake_db_session
    try:
        yield
    finally:
        app.dependency_overrides.pop(get_inventory_service, None)
        app.dependency_overrides.pop(require_authentication, None)
        app.dependency_overrides.pop(get_db_session, None)


@pytest.mark.anyio
async def test_manual_batch_create_list_and_detail_contract(
    api_client: httpx.AsyncClient,
    inventory_routes: object,
) -> None:
    """Manual batches remain independently addressable through authenticated APIs."""
    assert inventory_routes is None
    create_response = await api_client.post(
        "/api/inventory/batches",
        headers={"Idempotency-Key": "create-1"},
        json={
            "master_ingredient_id": str(INGREDIENT_ID),
            "quantity": 500,
            "unit": "GRAM",
            "storage_mode": "REFRIGERATED",
            "purchased_at": NOW.isoformat(),
            "expires_at": NOW.isoformat(),
            "unit_cost": 25000,
        },
    )
    list_response = await api_client.get(
        "/api/inventory/batches",
        params={"status": "ACTIVE", "storage_mode": "REFRIGERATED"},
    )
    detail_response = await api_client.get(f"/api/inventory/batches/{BATCH_ID}")

    assert create_response.status_code == 201
    assert create_response.json()["id"] == str(BATCH_ID)
    assert create_response.json()["expiration_source"] == "MANUFACTURER"
    assert list_response.status_code == 200
    assert list_response.json()["total"] == 1
    assert detail_response.status_code == 200
    assert detail_response.json()["freshness"] == "EXPIRING_SOON"


@pytest.mark.anyio
async def test_inventory_mutation_summary_and_ledger_contract(
    api_client: httpx.AsyncClient,
    inventory_routes: object,
) -> None:
    """Metadata, quantity, summary, and history routes share one batch contract."""
    assert inventory_routes is None
    update = await api_client.patch(
        f"/api/inventory/batches/{BATCH_ID}",
        headers={"Idempotency-Key": "update-1"},
        json={"note": "Keep chilled", "reason": "Label checked"},
    )
    adjustment = await api_client.post(
        f"/api/inventory/batches/{BATCH_ID}/adjustments",
        headers={"Idempotency-Key": "adjust-1"},
        json={
            "event_type": "MANUAL_ADJUSTMENT",
            "quantity_delta": -200,
            "reason": "Used for lunch",
        },
    )
    move = await api_client.post(
        f"/api/inventory/batches/{BATCH_ID}/move",
        headers={"Idempotency-Key": "move-1"},
        json={"storage_mode": "FROZEN", "reason": "Moved to freezer"},
    )
    consumption = await api_client.post(
        f"/api/inventory/batches/{BATCH_ID}/consume",
        headers={"Idempotency-Key": "consume-1"},
        json={"quantity": 100, "reason": "Snack"},
    )
    summary = await api_client.get("/api/inventory/summary")
    ledger = await api_client.get(
        "/api/inventory/ledger",
        params={"batch_id": str(BATCH_ID), "event_type": "INITIAL_STOCK"},
    )
    archive = await api_client.delete(
        f"/api/inventory/batches/{BATCH_ID}",
        headers={
            "Idempotency-Key": "archive-1",
            "X-Reason": "No longer tracking",
        },
    )

    assert update.status_code == 200
    assert adjustment.status_code == 200
    assert adjustment.json()["current_quantity"] == 300.0
    assert move.status_code == 200
    assert consumption.status_code == 200
    assert consumption.json()["current_quantity"] == 200.0
    assert summary.status_code == 200
    assert summary.json()["items"][0]["quantity"] == 0.5
    assert ledger.status_code == 200
    assert ledger.json()["items"][0]["reason"] == "Manual batch creation"
    assert archive.status_code == 204


@pytest.mark.anyio
async def test_inventory_create_requires_exactly_one_ingredient_identity(
    api_client: httpx.AsyncClient,
    inventory_routes: object,
) -> None:
    """A batch cannot ambiguously reference both catalog and custom ingredients."""
    assert inventory_routes is None
    response = await api_client.post(
        "/api/inventory/batches",
        headers={"Idempotency-Key": "create-2"},
        json={
            "master_ingredient_id": str(INGREDIENT_ID),
            "custom_name": "My spinach",
            "quantity": 1,
            "unit": "KG",
            "storage_mode": "REFRIGERATED",
        },
    )

    assert response.status_code == 422


@pytest.mark.anyio
async def test_inventory_routes_require_authentication(
    api_client: httpx.AsyncClient,
    inventory_routes: object,
) -> None:
    """Inventory data is unavailable without a valid access token."""
    assert inventory_routes is None
    app.dependency_overrides.pop(require_authentication, None)

    response = await api_client.get("/api/inventory/batches")

    assert response.status_code == 401


def test_inventory_openapi_documents_all_phase4_routes() -> None:
    """OpenAPI exposes the approved Inventory contract and idempotency headers."""
    app.openapi_schema = None
    paths = cast(dict[str, object], app.openapi()["paths"])
    expected_paths = {
        "/api/inventory/batches",
        "/api/inventory/batches/{batch_id}",
        "/api/inventory/batches/{batch_id}/adjustments",
        "/api/inventory/batches/{batch_id}/consume",
        "/api/inventory/batches/{batch_id}/move",
        "/api/inventory/summary",
        "/api/inventory/ledger",
    }

    assert expected_paths <= set(paths)
    create = cast(dict[str, object], paths["/api/inventory/batches"])
    create_operation = cast(dict[str, object], create["post"])
    parameters = cast(list[dict[str, object]], create_operation["parameters"])
    assert any(
        parameter["name"] == "Idempotency-Key"
        and parameter["in"] == "header"
        and parameter["required"] is True
        for parameter in parameters
    )
    assert create_operation["security"] == [{"BearerAuth": []}]

    for path, method in (
        ("/api/inventory/batches/{batch_id}", "patch"),
        ("/api/inventory/batches/{batch_id}", "delete"),
        ("/api/inventory/batches/{batch_id}/consume", "post"),
        ("/api/inventory/batches/{batch_id}/move", "post"),
    ):
        operation = cast(
            dict[str, object], cast(dict[str, object], paths[path])[method]
        )
        operation_parameters = cast(list[dict[str, object]], operation["parameters"])
        assert any(
            parameter["name"] == "Idempotency-Key" and parameter["required"] is True
            for parameter in operation_parameters
        )
