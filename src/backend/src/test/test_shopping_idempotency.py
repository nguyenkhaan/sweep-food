"""Focused unit coverage for persisted shopping-mutation replay semantics."""

from types import SimpleNamespace
from typing import cast
from uuid import UUID

import pytest
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src.model.enum_model import MeasurementUnit, ShoppingListStatus
from src.model.master_ingredient_model import MasterIngredientModel
from src.model.shopping_list_item_model import ShoppingListItemModel
from src.model.shopping_list_model import ShoppingListModel
from src.model.shopping_mutation_receipt_model import ShoppingMutationReceiptModel
from src.module.inventory.inventory_service import InventoryService
from src.module.shopping_lists.shopping_dto import (
    CreateShoppingItemRequestDTO,
    UpdateShoppingListItemRequestDTO,
)
from src.module.shopping_lists.shopping_service import ShoppingService

USER_ID = UUID("018f0f90-26e6-7ce7-8f61-8769f9e5b101")
LIST_ID = UUID("018f0f90-26e6-7ce7-8f61-8769f9e5b103")
ITEM_ID = UUID("018f0f90-26e6-7ce7-8f61-8769f9e5b104")


class _ScalarResult:
    def __init__(self, value: ShoppingMutationReceiptModel | None) -> None:
        self.value = value

    def scalar_one_or_none(self) -> ShoppingMutationReceiptModel | None:
        return self.value


class _ReceiptSession:
    def __init__(self, receipt: ShoppingMutationReceiptModel | None = None) -> None:
        self.receipt = receipt
        self.added: list[object] = []

    async def execute(self, _statement: object) -> _ScalarResult:
        return _ScalarResult(self.receipt)

    def add(self, instance: object) -> None:
        self.added.append(instance)


class _AddItemSession(_ReceiptSession):
    def __init__(self) -> None:
        super().__init__()
        self.committed = False

    async def flush(self) -> None:
        for instance in self.added:
            if isinstance(instance, ShoppingListItemModel):
                instance.id = ITEM_ID

    async def commit(self) -> None:
        self.committed = True

    async def rollback(self) -> None:
        return None


class _AddItemService(ShoppingService):
    async def _find_list(
        self, user_id: UUID, list_id: UUID, *, lock: bool
    ) -> ShoppingListModel:
        assert user_id == USER_ID
        assert list_id == LIST_ID
        assert lock is True
        return cast(
            ShoppingListModel,
            SimpleNamespace(id=LIST_ID, status=ShoppingListStatus.ACTIVE),
        )

    async def _find_receipt(self, request: object) -> None:
        assert request is not None

    async def _find_ingredient(
        self, ingredient_id: UUID | None
    ) -> MasterIngredientModel | None:
        assert ingredient_id is None
        return None


def _service(session: _ReceiptSession) -> ShoppingService:
    return ShoppingService(
        cast(AsyncSession, session),
        cast(InventoryService, object()),
    )


def _create_item_body() -> CreateShoppingItemRequestDTO:
    return CreateShoppingItemRequestDTO(
        custom_name="Rice",
        quantity=1,
        unit=MeasurementUnit.PIECE,
    )


def test_receipt_request_uses_canonical_path_and_stable_payload_hashes() -> None:
    """Query strings do not enter scope and omitted differs from explicit null."""
    request = ShoppingService._receipt_request(
        USER_ID,
        "POST",
        f"/api/shopping-lists/{LIST_ID}/items?ignored=true",
        "add-key",
        _create_item_body(),
    )
    omitted = ShoppingService._receipt_request(
        USER_ID,
        "PATCH",
        f"/api/shopping-lists/{LIST_ID}/items/{ITEM_ID}",
        "update-key",
        UpdateShoppingListItemRequestDTO(checked=False),
    )
    explicit_null = ShoppingService._receipt_request(
        USER_ID,
        "PATCH",
        f"/api/shopping-lists/{LIST_ID}/items/{ITEM_ID}",
        "update-key",
        UpdateShoppingListItemRequestDTO.model_validate({"estimated_cost": None}),
    )

    assert request.request_path == f"/api/shopping-lists/{LIST_ID}/items"
    assert len(request.key_hash) == 64
    assert omitted.request_fingerprint != explicit_null.request_fingerprint


@pytest.mark.anyio
async def test_receipt_lookup_replays_only_the_matching_raw_key_and_payload() -> None:
    """A matching hash alone never replays a different raw key or body."""
    request = ShoppingService._receipt_request(
        USER_ID,
        "POST",
        f"/api/shopping-lists/{LIST_ID}/items",
        "add-key",
        _create_item_body(),
    )
    receipt = ShoppingMutationReceiptModel(
        user_id=USER_ID,
        method=request.method,
        request_path=request.request_path,
        idempotency_key="different-raw-key",
        key_hash=request.key_hash,
        request_fingerprint=request.request_fingerprint,
        response_status=201,
        response_body={"id": str(ITEM_ID)},
    )

    with pytest.raises(HTTPException, match="Idempotency key") as error:
        await _service(_ReceiptSession(receipt))._find_receipt(request)

    assert error.value.status_code == 409


def test_record_receipt_keeps_204_as_sql_null_body() -> None:
    """A successful delete is stored without JSON null or a private DTO."""
    session = _ReceiptSession()
    request = ShoppingService._receipt_request(
        USER_ID,
        "DELETE",
        f"/api/shopping-lists/{LIST_ID}/items/{ITEM_ID}",
        "delete-key",
        None,
    )

    _service(session)._record_receipt(request, 204, None)

    receipt = cast(ShoppingMutationReceiptModel, session.added[0])
    assert receipt.response_status == 204
    assert receipt.response_body is None


@pytest.mark.anyio
async def test_add_item_snapshots_the_assigned_item_id_with_its_receipt() -> None:
    """The first add response and receipt refer to the same persisted item UUID."""
    session = _AddItemSession()
    service = _AddItemService(
        cast(AsyncSession, session),
        cast(InventoryService, object()),
    )

    result = await service.add_item(USER_ID, LIST_ID, _create_item_body(), "add-key")

    receipt = next(
        instance
        for instance in session.added
        if isinstance(instance, ShoppingMutationReceiptModel)
    )
    assert result.body.id == ITEM_ID
    assert receipt.response_body == result.body.model_dump(mode="json")
    assert session.committed is True
