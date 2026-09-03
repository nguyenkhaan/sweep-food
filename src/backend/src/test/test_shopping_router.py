"""API-contract tests for shopping lists and inventory-synchronised check-off."""

from collections.abc import AsyncGenerator
from datetime import UTC, datetime
from typing import cast
from uuid import UUID

import httpx
import pytest

from src.app import app
from src.db import get_db_session
from src.middleware.auth_middleware import AuthenticatedUser, require_authentication
from src.model.enum_model import (
    MeasurementUnit,
    ShoppingListStatus,
    StorageMode,
    UserRole,
)
from src.module.shopping_lists.shopping_dependency import get_shopping_service
from src.module.shopping_lists.shopping_dto import (
    CreateShoppingItemRequestDTO,
    GenerateShoppingListRequestDTO,
    ShoppingListDTO,
    ShoppingListItemDTO,
    UpdateShoppingListItemRequestDTO,
)

USER_ID = UUID("018f0f90-26e6-7ce7-8f61-8769f9e5b101")
PLAN_ID = UUID("018f0f90-26e6-7ce7-8f61-8769f9e5b102")
LIST_ID = UUID("018f0f90-26e6-7ce7-8f61-8769f9e5b103")
ITEM_ID = UUID("018f0f90-26e6-7ce7-8f61-8769f9e5b104")
INGREDIENT_ID = UUID("018f0f90-26e6-7ce7-8f61-8769f9e5b105")
NOW = datetime(2026, 9, 7, 9, 0, tzinfo=UTC)


def _item() -> ShoppingListItemDTO:
    return ShoppingListItemDTO(
        id=ITEM_ID,
        master_ingredient_id=INGREDIENT_ID,
        custom_name=None,
        name="Spinach",
        required_quantity=200.0,
        available_quantity=50.0,
        missing_quantity=150.0,
        unit=MeasurementUnit.GRAM,
        estimated_cost=None,
        is_checked=False,
        is_generated=True,
        source_recipe_ids=[],
        inventory_batch_id=None,
    )


def _list() -> ShoppingListDTO:
    return ShoppingListDTO(
        id=LIST_ID,
        meal_plan_id=PLAN_ID,
        status=ShoppingListStatus.ACTIVE,
        generated_at=NOW,
        items=[_item()],
    )


class FakeShoppingService:
    """Verify route contracts without replacing database service behaviour tests."""

    async def generate(
        self,
        user_id: UUID,
        body: GenerateShoppingListRequestDTO,
        idempotency_key: str,
    ) -> ShoppingListDTO:
        assert user_id == USER_ID
        assert body.meal_plan_id == PLAN_ID
        assert idempotency_key == "generate-1"
        return _list()

    async def get(self, user_id: UUID, list_id: UUID) -> ShoppingListDTO:
        assert user_id == USER_ID
        assert list_id == LIST_ID
        return _list()

    async def add_item(
        self,
        user_id: UUID,
        list_id: UUID,
        body: CreateShoppingItemRequestDTO,
        idempotency_key: str,
    ) -> ShoppingListItemDTO:
        assert user_id == USER_ID
        assert list_id == LIST_ID
        assert body.master_ingredient_id == INGREDIENT_ID
        assert idempotency_key == "add-1"
        return _item()

    async def update_item(
        self,
        user_id: UUID,
        list_id: UUID,
        item_id: UUID,
        body: UpdateShoppingListItemRequestDTO,
        idempotency_key: str,
    ) -> ShoppingListItemDTO:
        assert user_id == USER_ID
        assert list_id == LIST_ID
        assert item_id == ITEM_ID
        assert body.checked is True
        assert body.purchase is not None
        assert body.purchase.storage_mode is StorageMode.REFRIGERATED
        assert idempotency_key == "check-1"
        return _item()

    async def remove_item(
        self, user_id: UUID, list_id: UUID, item_id: UUID, idempotency_key: str
    ) -> None:
        assert user_id == USER_ID
        assert list_id == LIST_ID
        assert item_id == ITEM_ID
        assert idempotency_key == "delete-1"


@pytest.fixture(name="shopping_routes")
async def _shopping_routes() -> AsyncGenerator[None, None]:
    service = FakeShoppingService()

    async def get_authenticated_user() -> AuthenticatedUser:
        return AuthenticatedUser(USER_ID, (UserRole.USER,))

    def get_service() -> FakeShoppingService:
        return service

    app.dependency_overrides[require_authentication] = get_authenticated_user
    app.dependency_overrides[get_shopping_service] = get_service
    try:
        yield
    finally:
        app.dependency_overrides.pop(require_authentication, None)
        app.dependency_overrides.pop(get_shopping_service, None)
        app.dependency_overrides.pop(get_db_session, None)


@pytest.mark.anyio
async def test_shopping_routes_manage_a_list_and_forward_purchase_metadata(
    api_client: httpx.AsyncClient,
    shopping_routes: None,
) -> None:
    """All shopping writes require an idempotency key and preserve purchase input."""
    assert shopping_routes is None
    generate = await api_client.post(
        "/api/shopping-lists/generate",
        headers={"Idempotency-Key": "generate-1"},
        json={"meal_plan_id": str(PLAN_ID)},
    )
    detail = await api_client.get(f"/api/shopping-lists/{LIST_ID}")
    add = await api_client.post(
        f"/api/shopping-lists/{LIST_ID}/items",
        headers={"Idempotency-Key": "add-1"},
        json={
            "master_ingredient_id": str(INGREDIENT_ID),
            "quantity": 100,
            "unit": "GRAM",
        },
    )
    check = await api_client.patch(
        f"/api/shopping-lists/{LIST_ID}/items/{ITEM_ID}",
        headers={"Idempotency-Key": "check-1"},
        json={
            "checked": True,
            "purchase": {"storage_mode": "REFRIGERATED"},
        },
    )
    remove = await api_client.delete(
        f"/api/shopping-lists/{LIST_ID}/items/{ITEM_ID}",
        headers={"Idempotency-Key": "delete-1"},
    )

    assert generate.status_code == 201
    assert detail.status_code == 200
    assert add.status_code == 201
    assert check.status_code == 200
    assert remove.status_code == 204


@pytest.mark.anyio
async def test_shopping_routes_reject_invalid_identity_and_check_input(
    api_client: httpx.AsyncClient,
    shopping_routes: None,
) -> None:
    """A manual item has one identity and a first purchase needs storage metadata."""
    assert shopping_routes is None
    identity = await api_client.post(
        f"/api/shopping-lists/{LIST_ID}/items",
        headers={"Idempotency-Key": "invalid-1"},
        json={
            "master_ingredient_id": str(INGREDIENT_ID),
            "custom_name": "Spinach",
            "quantity": 100,
            "unit": "GRAM",
        },
    )
    check = await api_client.patch(
        f"/api/shopping-lists/{LIST_ID}/items/{ITEM_ID}",
        headers={"Idempotency-Key": "invalid-2"},
        json={"checked": True},
    )

    assert identity.status_code == 422
    assert check.status_code == 422


@pytest.mark.anyio
async def test_shopping_routes_require_authentication(
    api_client: httpx.AsyncClient,
    shopping_routes: None,
) -> None:
    """Shopping and inventory-affecting actions require the normal bearer token."""
    assert shopping_routes is None
    app.dependency_overrides.pop(require_authentication, None)

    async def get_unused_db_session() -> AsyncGenerator[object, None]:
        yield object()

    app.dependency_overrides[get_db_session] = get_unused_db_session
    response = await api_client.get(f"/api/shopping-lists/{LIST_ID}")

    assert response.status_code == 401


def test_shopping_openapi_documents_idempotent_mutations() -> None:
    """All shopping write operations expose the required idempotency header."""
    app.openapi_schema = None
    paths = cast(dict[str, object], app.openapi()["paths"])
    generate = cast(dict[str, object], paths["/api/shopping-lists/generate"])["post"]
    parameters = cast(list[dict[str, object]], cast(dict[str, object], generate)["parameters"])

    assert any(
        parameter["name"] == "Idempotency-Key"
        and parameter["in"] == "header"
        and parameter["required"] is True
        for parameter in parameters
    )
