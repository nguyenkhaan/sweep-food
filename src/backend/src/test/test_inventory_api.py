"""Guarded API coverage for Task 4.3 manual inventory batch CRUD."""

from collections.abc import AsyncGenerator
from datetime import UTC, datetime, timedelta
from typing import TypedDict, cast
from unittest.mock import AsyncMock
from uuid import UUID

import httpx
import pytest
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession

from src.app import app
from src.db import get_db_session
from src.middleware.auth_middleware import AuthenticatedUser, require_authentication
from src.model.enum_model import (
    ExpirationSource,
    InventoryBatchStatus,
    InventoryBatchType,
    InventorySource,
    MeasurementUnit,
    ShelfLifeRuleScope,
    StorageMode,
    UserRole,
)
from src.model.ingredient_category_model import IngredientCategoryModel
from src.model.inventory_batch_model import InventoryBatchModel
from src.model.inventory_ledger_entry_model import InventoryLedgerEntryModel
from src.model.master_ingredient_model import MasterIngredientModel
from src.model.shelf_life_rule_model import ShelfLifeRuleModel
from src.model.user_model import UserModel
from src.module.inventory.inventory_dto import CreateInventoryBatchRequestDTO
from src.module.inventory.inventory_service import InventoryService

PRIMARY_USER_ID = UUID("018f0f90-26e6-7ce7-8f61-8769f9e5a031")
OTHER_USER_ID = UUID("018f0f90-26e6-7ce7-8f61-8769f9e5a032")


class InventoryAPIContext(TypedDict):
    """Fixtures needed to assert the guarded API's persisted effects."""

    ingredient_id: str
    category_id: str
    session: AsyncSession


@pytest.fixture(name="inventory_api")
async def _inventory_api(
    database_engine: AsyncEngine,
) -> AsyncGenerator[InventoryAPIContext, None]:
    """Bind routes to a transaction on the guarded isolated test database."""
    async with database_engine.connect() as connection:
        transaction = await connection.begin()
        session = AsyncSession(
            bind=connection,
            expire_on_commit=False,
            join_transaction_mode="create_savepoint",
        )

        async def override_db_session() -> AsyncGenerator[AsyncSession, None]:
            """Supply the guarded transaction to every request dependency."""
            yield session

        async def authenticated_primary_user() -> AuthenticatedUser:
            """Authenticate the primary inventory owner without JWT setup."""
            return AuthenticatedUser(PRIMARY_USER_ID, (UserRole.USER,))

        primary_user = UserModel(
            id=PRIMARY_USER_ID,
            phone_e164="+84910000031",
            password_hash="inventory-api-primary-password-hash",
        )
        other_user = UserModel(
            id=OTHER_USER_ID,
            phone_e164="+84910000032",
            password_hash="inventory-api-other-password-hash",
        )
        category = IngredientCategoryModel(
            name="Inventory API vegetables",
            description="Guarded inventory API category.",
        )
        ingredient = MasterIngredientModel(
            name="Inventory API spinach",
            description="Guarded inventory API ingredient.",
            category=category,
            canonical_unit=MeasurementUnit.GRAM,
        )
        session.add_all([primary_user, other_user, ingredient])
        await session.flush()
        session.add_all(
            [
                ShelfLifeRuleModel(
                    scope=ShelfLifeRuleScope.CATEGORY,
                    category_id=category.id,
                    storage_mode=StorageMode.REFRIGERATED,
                    min_days=5,
                    max_days=5,
                    default_days=5,
                ),
                ShelfLifeRuleModel(
                    scope=ShelfLifeRuleScope.INGREDIENT,
                    master_ingredient_id=ingredient.id,
                    storage_mode=StorageMode.REFRIGERATED,
                    min_days=2,
                    max_days=2,
                    default_days=2,
                ),
            ]
        )
        await session.flush()
        app.dependency_overrides[get_db_session] = override_db_session
        app.dependency_overrides[require_authentication] = authenticated_primary_user
        try:
            yield {
                "ingredient_id": str(ingredient.id),
                "category_id": str(category.id),
                "session": session,
            }
        finally:
            app.dependency_overrides.pop(get_db_session, None)
            app.dependency_overrides.pop(require_authentication, None)
            await session.close()
            await transaction.rollback()


def _manual_payload(ingredient_id: str, **overrides: object) -> dict[str, object]:
    """Build a valid master-backed manual batch request."""
    stored_at = datetime.now(UTC) - timedelta(days=1)
    payload: dict[str, object] = {
        "master_ingredient_id": ingredient_id,
        "quantity": 1.5,
        "unit": "KG",
        "storage_mode": "REFRIGERATED",
        "purchased_at": stored_at.isoformat(),
        "stored_at": stored_at.isoformat(),
        "unit_cost": 20_000.0,
        "note": "fresh batch",
        "media_url": "https://example.test/inventory.jpg",
    }
    payload.update(overrides)
    return payload


def _response_datetime(value: str) -> datetime:
    """Parse FastAPI's canonical UTC ``Z`` response timestamps for assertions."""
    return datetime.fromisoformat(value)


@pytest.mark.anyio
async def test_manual_batch_crud_expiration_filters_and_pagination(
    api_client: httpx.AsyncClient,
    inventory_api: InventoryAPIContext,
) -> None:
    """Exercise the complete owner CRUD path and calculated response metadata."""
    manufacturer_expiration = datetime.now(UTC) + timedelta(days=10)
    manufacturer_response = await api_client.post(
        "/api/inventory/batches",
        json=_manual_payload(
            inventory_api["ingredient_id"],
            manufacturer_expires_at=manufacturer_expiration.isoformat(),
        ),
    )
    assert manufacturer_response.status_code == 201
    manufacturer_batch = manufacturer_response.json()
    assert manufacturer_batch["expiration_source"] == "MANUFACTURER"
    assert (
        _response_datetime(manufacturer_batch["expires_at"]) == manufacturer_expiration
    )
    assert manufacturer_batch["applied_shelf_life_rule"] is None
    assert manufacturer_batch["initial_quantity"] == 1.5
    assert manufacturer_batch["current_quantity"] == 1.5
    ledger_entry = await inventory_api["session"].scalar(
        select(InventoryLedgerEntryModel).where(
            InventoryLedgerEntryModel.inventory_batch_id == manufacturer_batch["id"],
        )
    )
    assert ledger_entry is not None
    assert ledger_entry.quantity_before == 0
    assert ledger_entry.quantity_delta == 1.5
    assert ledger_entry.quantity_after == 1.5

    estimated_stored_at = datetime.now(UTC) - timedelta(days=3)
    estimated_response = await api_client.post(
        "/api/inventory/batches",
        json=_manual_payload(
            inventory_api["ingredient_id"],
            stored_at=estimated_stored_at.isoformat(),
        ),
    )
    assert estimated_response.status_code == 201
    estimated_batch = estimated_response.json()
    assert estimated_batch["expiration_source"] == "ESTIMATED"
    assert _response_datetime(estimated_batch["expires_at"]) == (
        estimated_stored_at + timedelta(days=2)
    )
    assert estimated_batch["applied_shelf_life_rule"] == {
        "scope": "INGREDIENT",
        "storage_mode": "REFRIGERATED",
        "default_days": 2,
    }

    override_expiration = datetime.now(UTC) + timedelta(days=1)
    override_response = await api_client.post(
        "/api/inventory/batches",
        json=_manual_payload(
            inventory_api["ingredient_id"],
            expiration_override_at=override_expiration.isoformat(),
        ),
    )
    assert override_response.status_code == 201
    override_batch = override_response.json()
    assert override_batch["expiration_source"] == "USER_OVERRIDE"
    assert _response_datetime(override_batch["expires_at"]) == override_expiration

    custom_response = await api_client.post(
        "/api/inventory/batches",
        json={
            "custom_name": "  Homemade sauce  ",
            "quantity": 2,
            "unit": "PACK",
            "storage_mode": "DRY_SHELF",
        },
    )
    assert custom_response.status_code == 201
    custom_batch = custom_response.json()
    assert custom_batch["custom_name"] == "Homemade sauce"
    assert custom_batch["expiration_source"] == "UNKNOWN"
    assert custom_batch["freshness_state"] == "UNKNOWN"

    page_one = await api_client.get(
        "/api/inventory/batches",
        params={"page": 1, "per_page": 2},
    )
    repeated_page_one = await api_client.get(
        "/api/inventory/batches",
        params={"page": 1, "per_page": 2},
    )
    page_two = await api_client.get(
        "/api/inventory/batches",
        params={"page": 2, "per_page": 2},
    )
    assert page_one.status_code == 200
    assert page_one.json()["total"] == 4
    assert page_one.json()["items"] == repeated_page_one.json()["items"]
    assert {item["id"] for item in page_one.json()["items"]}.isdisjoint(
        {item["id"] for item in page_two.json()["items"]},
    )
    filtered = await api_client.get(
        "/api/inventory/batches",
        params={
            "master_ingredient_id": inventory_api["ingredient_id"],
            "category_id": inventory_api["category_id"],
            "storage_mode": "REFRIGERATED",
        },
    )
    assert filtered.status_code == 200
    assert filtered.json()["total"] == 3
    unknowns = await api_client.get(
        "/api/inventory/batches",
        params={"freshness_state": "UNKNOWN"},
    )
    assert unknowns.status_code == 200
    assert [item["id"] for item in unknowns.json()["items"]] == [custom_batch["id"]]

    detail = await api_client.get(f"/api/inventory/batches/{estimated_batch['id']}")
    assert detail.status_code == 200
    assert detail.json()["id"] == estimated_batch["id"]
    update = await api_client.patch(
        f"/api/inventory/batches/{estimated_batch['id']}",
        json={"note": "updated", "storage_mode": "FROZEN"},
    )
    assert update.status_code == 200
    assert update.json()["note"] == "updated"
    assert update.json()["expiration_source"] == "UNKNOWN"
    assert update.json()["expires_at"] is None
    prohibited_patch = await api_client.patch(
        f"/api/inventory/batches/{estimated_batch['id']}",
        json={"initial_quantity": 10, "current_quantity": 10, "status": "DISCARDED"},
    )
    assert prohibited_patch.status_code == 422
    override_update = await api_client.patch(
        f"/api/inventory/batches/{override_batch['id']}",
        json={"storage_mode": "FROZEN"},
    )
    assert override_update.status_code == 200
    assert override_update.json()["expiration_source"] == "USER_OVERRIDE"
    assert (
        _response_datetime(override_update.json()["expires_at"]) == override_expiration
    )

    archive = await api_client.delete(
        f"/api/inventory/batches/{manufacturer_batch['id']}"
    )
    assert archive.status_code == 204
    assert not archive.content
    archived_ledger_entry = await inventory_api["session"].get(
        InventoryLedgerEntryModel,
        ledger_entry.id,
    )
    assert archived_ledger_entry is not None
    assert archived_ledger_entry.quantity_after == 1.5
    active_list = await api_client.get("/api/inventory/batches")
    assert manufacturer_batch["id"] not in {
        item["id"] for item in active_list.json()["items"]
    }
    archived_list = await api_client.get(
        "/api/inventory/batches", params={"status": "ARCHIVED"}
    )
    assert [item["id"] for item in archived_list.json()["items"]] == [
        manufacturer_batch["id"]
    ]


@pytest.mark.anyio
async def test_manual_batch_rejects_invalid_inputs_and_cross_user_access(
    api_client: httpx.AsyncClient,
    inventory_api: InventoryAPIContext,
) -> None:
    """Reject malformed fields and hide another user's batch on every operation."""
    invalid_payloads = [
        _manual_payload(
            inventory_api["ingredient_id"],
            custom_name="Duplicate identity",
        ),
        _manual_payload(inventory_api["ingredient_id"], quantity=0),
        _manual_payload(inventory_api["ingredient_id"], unit="ML"),
        _manual_payload(
            inventory_api["ingredient_id"],
            manufacturer_expires_at=datetime.now(UTC).isoformat(),
            expiration_override_at=datetime.now(UTC).isoformat(),
        ),
        _manual_payload(inventory_api["ingredient_id"], status="ARCHIVED"),
        {
            "master_ingredient_id": "018f0f90-26e6-7ce7-8f61-8769f9e5a099",
            "quantity": 1,
            "unit": "GRAM",
            "storage_mode": "REFRIGERATED",
        },
    ]
    for payload in invalid_payloads:
        response = await api_client.post("/api/inventory/batches", json=payload)
        assert response.status_code == 422

    foreign_batch = InventoryBatchModel(
        user_id=OTHER_USER_ID,
        custom_name="Other user's batch",
        batch_type=InventoryBatchType.RAW_INGREDIENT,
        initial_quantity=1,
        current_quantity=1,
        unit=MeasurementUnit.PIECE,
        storage_mode=StorageMode.DRY_SHELF,
        status=InventoryBatchStatus.ACTIVE,
        expiration_source=ExpirationSource.UNKNOWN,
        source=InventorySource.MANUAL,
    )
    inventory_api["session"].add(foreign_batch)
    await inventory_api["session"].flush()
    for method, url, kwargs in (
        ("get", f"/api/inventory/batches/{foreign_batch.id}", {}),
        (
            "patch",
            f"/api/inventory/batches/{foreign_batch.id}",
            {"json": {"note": "no"}},
        ),
        ("delete", f"/api/inventory/batches/{foreign_batch.id}", {}),
    ):
        response = await getattr(api_client, method)(url, **kwargs)
        assert response.status_code == 404


@pytest.mark.anyio
async def test_failed_initial_stock_commit_rolls_back_batch_and_ledger(
    inventory_api: InventoryAPIContext,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A commit failure cannot leave either half of manual batch creation behind."""
    service = InventoryService(inventory_api["session"])
    request = CreateInventoryBatchRequestDTO.model_validate(
        _manual_payload(inventory_api["ingredient_id"]),
    )
    original_commit = inventory_api["session"].commit
    monkeypatch.setattr(
        inventory_api["session"],
        "commit",
        AsyncMock(side_effect=SQLAlchemyError("commit failed")),
    )
    with pytest.raises(SQLAlchemyError, match="commit failed"):
        await service.create_batch(PRIMARY_USER_ID, request)
    monkeypatch.setattr(inventory_api["session"], "commit", original_commit)
    assert (
        await inventory_api["session"].scalar(
            select(InventoryBatchModel).where(
                InventoryBatchModel.user_id == PRIMARY_USER_ID,
                InventoryBatchModel.note == "fresh batch",
            )
        )
        is None
    )
    assert (
        await inventory_api["session"].scalar(
            select(InventoryLedgerEntryModel).where(
                InventoryLedgerEntryModel.user_id == PRIMARY_USER_ID,
                InventoryLedgerEntryModel.event_type == "INITIAL_STOCK",
            )
        )
        is None
    )


def test_inventory_openapi_documents_crud_request_response_and_filters() -> None:
    """Expose the public manual-batch contract in OpenAPI with bearer auth."""
    app.openapi_schema = None
    schema = app.openapi()
    paths = cast(dict[str, object], schema["paths"])
    batches_path = cast(dict[str, object], paths["/api/inventory/batches"])
    batch_path = cast(dict[str, object], paths["/api/inventory/batches/{batch_id}"])
    assert set(batches_path) == {"get", "post"}
    assert set(batch_path) == {"get", "patch", "delete"}
    list_operation = cast(dict[str, object], batches_path["get"])
    create_operation = cast(dict[str, object], batches_path["post"])
    for operation in (
        list_operation,
        create_operation,
        cast(dict[str, object], batch_path["get"]),
        cast(dict[str, object], batch_path["patch"]),
        cast(dict[str, object], batch_path["delete"]),
    ):
        assert operation["security"] == [{"BearerAuth": []}]
    parameters = cast(list[dict[str, object]], list_operation["parameters"])
    assert {parameter["name"] for parameter in parameters} == {
        "master_ingredient_id",
        "category_id",
        "storage_mode",
        "status",
        "freshness_state",
        "expires_from",
        "expires_to",
        "page",
        "per_page",
    }
    components = cast(dict[str, object], schema["components"])
    schemas = cast(dict[str, dict[str, object]], components["schemas"])
    create_schema = schemas["CreateInventoryBatchRequestDTO"]
    create_properties = cast(dict[str, object], create_schema["properties"])
    assert set(create_properties) >= {
        "master_ingredient_id",
        "custom_name",
        "quantity",
        "unit",
        "storage_mode",
        "manufacturer_expires_at",
        "expiration_override_at",
    }
    response_schema = schemas["InventoryBatchDTO"]
    response_properties = cast(dict[str, object], response_schema["properties"])
    assert set(response_properties) >= {
        "expiration_source",
        "freshness_state",
        "applied_shelf_life_rule",
    }
