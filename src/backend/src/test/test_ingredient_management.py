"""Route and service checks for ingredient management."""

from collections.abc import AsyncGenerator
from datetime import UTC, datetime
from decimal import Decimal
from uuid import UUID

import httpx
import pytest
from fastapi import HTTPException

from src.app import app
from src.middleware.auth_middleware import AuthenticatedUser, require_authentication
from src.model.enum_model import (
    ExpirationSource,
    InventoryBatchStatus,
    InventoryBatchType,
    InventorySource,
    MeasurementUnit,
    StorageMode,
    UserRole,
)
from src.module.catalog.catalog_dto import (
    IngredientCategoryDTO,
    IngredientDetailDTO,
    IngredientNutritionDTO,
)
from src.module.ingredient.ingredient_dependency import get_ingredient_service
from src.module.ingredient.ingredient_dto import (
    AssignIngredientCategoryDTO,
    UpdateIngredientDefaultStorageDTO,
    UpdateIngredientDTO,
)
from src.module.inventory.inventory_dto import (
    FreshnessState,
    InventoryBatchDTO,
    MoveInventoryBatchRequestDTO,
)

USER_ID = UUID("018f0f90-26e6-7ce7-8f61-8769f9e5b101")
INGREDIENT_ID = UUID("018f0f90-26e6-7ce7-8f61-8769f9e5b103")
CATEGORY_ID = UUID("018f0f90-26e6-7ce7-8f61-8769f9e5b104")
BATCH_ID = UUID("018f0f90-26e6-7ce7-8f61-8769f9e5b105")
NOW = datetime(2026, 9, 1, tzinfo=UTC)


def _ingredient(
    *, name: str = "Spinach", mode: StorageMode | None = None
) -> IngredientDetailDTO:
    return IngredientDetailDTO(
        id=INGREDIENT_ID,
        name=name,
        category=IngredientCategoryDTO(id=CATEGORY_ID, name="Vegetables"),
        default_unit=MeasurementUnit.GRAM,
        default_storage_mode=mode,
        aliases=[],
        description=None,
        default_media_url=None,
        nutrition=IngredientNutritionDTO(
            calories=Decimal(23),
            protein_g=None,
            fat_g=None,
            carbs_g=None,
            sugar_g=None,
            sodium_mg=None,
            other_nutrients={},
        ),
        shelf_life_rules=[],
    )


class FakeIngredientService:
    """Expose the route contract without a database connection."""

    async def update_ingredient(
        self, ingredient_id: UUID, body: UpdateIngredientDTO
    ) -> IngredientDetailDTO:
        assert ingredient_id == INGREDIENT_ID
        return _ingredient(name=body.name or "Spinach")

    async def delete_ingredient(self, ingredient_id: UUID) -> None:
        assert ingredient_id == INGREDIENT_ID

    async def update_default_storage(
        self, ingredient_id: UUID, body: UpdateIngredientDefaultStorageDTO
    ) -> IngredientDetailDTO:
        assert ingredient_id == INGREDIENT_ID
        return _ingredient(mode=body.default_storage_mode)

    async def update_category(
        self, ingredient_id: UUID, body: AssignIngredientCategoryDTO
    ) -> IngredientDetailDTO:
        assert ingredient_id == INGREDIENT_ID
        if body.category_id != CATEGORY_ID:
            raise HTTPException(status_code=404, detail="Category not found")
        return _ingredient()

    async def move_inventory_batch(
        self,
        user_id: UUID,
        batch_id: UUID,
        body: MoveInventoryBatchRequestDTO,
        key: str,
    ) -> InventoryBatchDTO:
        assert user_id == USER_ID
        assert batch_id == BATCH_ID
        assert body.storage_mode is StorageMode.FROZEN
        assert key == "move-ingredient-1"
        return InventoryBatchDTO(
            id=BATCH_ID,
            master_ingredient_id=INGREDIENT_ID,
            custom_name=None,
            ingredient_name="Spinach",
            batch_type=InventoryBatchType.RAW_INGREDIENT,
            initial_quantity=500.0,
            current_quantity=500.0,
            unit=MeasurementUnit.GRAM,
            storage_mode=StorageMode.FROZEN,
            status=InventoryBatchStatus.ACTIVE,
            purchased_at=NOW,
            packaged_at=None,
            stored_at=NOW,
            expires_at=NOW,
            expiration_source=ExpirationSource.MANUFACTURER,
            freshness=FreshnessState.SAFE,
            unit_cost=None,
            note=None,
            media_url=None,
            source=InventorySource.MANUAL,
            source_cooking_session_id=None,
            created_at=NOW,
            updated_at=NOW,
            archived_at=None,
        )


@pytest.fixture(name="ingredient_routes")
async def _ingredient_routes() -> AsyncGenerator[list[UserRole], None]:
    roles = [UserRole.ADMIN]

    async def authenticated_user() -> AuthenticatedUser:
        return AuthenticatedUser(USER_ID, tuple(roles))

    def ingredient_service() -> FakeIngredientService:
        return FakeIngredientService()

    app.dependency_overrides[require_authentication] = authenticated_user
    app.dependency_overrides[get_ingredient_service] = ingredient_service
    try:
        yield roles
    finally:
        app.dependency_overrides.pop(require_authentication, None)
        app.dependency_overrides.pop(get_ingredient_service, None)


@pytest.mark.anyio
async def test_admin_updates_and_deletes_master_ingredient(
    api_client: httpx.AsyncClient, ingredient_routes: list[UserRole]
) -> None:
    assert ingredient_routes == [UserRole.ADMIN]
    update = await api_client.patch(
        f"/api/ingredients/{INGREDIENT_ID}", json={"name": "Baby spinach"}
    )
    storage = await api_client.patch(
        f"/api/ingredients/{INGREDIENT_ID}/default-storage-mode",
        json={"default_storage_mode": "REFRIGERATED"},
    )
    category = await api_client.patch(
        f"/api/ingredients/{INGREDIENT_ID}/category",
        json={"category_id": str(CATEGORY_ID)},
    )
    delete = await api_client.delete(f"/api/ingredients/{INGREDIENT_ID}")

    assert update.status_code == 200
    assert update.json()["name"] == "Baby spinach"
    assert storage.status_code == 200
    assert storage.json()["default_storage_mode"] == "REFRIGERATED"
    assert category.status_code == 200
    assert delete.status_code == 204


@pytest.mark.anyio
async def test_user_cannot_mutate_catalog_and_can_move_owned_batch(
    api_client: httpx.AsyncClient, ingredient_routes: list[UserRole]
) -> None:
    ingredient_routes[:] = [UserRole.USER]
    assert (
        await api_client.patch(
            f"/api/ingredients/{INGREDIENT_ID}", json={"name": "New"}
        )
    ).status_code == 403
    assert (
        await api_client.delete(f"/api/ingredients/{INGREDIENT_ID}")
    ).status_code == 403
    assert (
        await api_client.patch(
            f"/api/ingredients/{INGREDIENT_ID}/category",
            json={"category_id": str(CATEGORY_ID)},
        )
    ).status_code == 403
    assert (
        await api_client.patch(
            f"/api/ingredients/{INGREDIENT_ID}/default-storage-mode",
            json={"default_storage_mode": "FROZEN"},
        )
    ).status_code == 403
    moved = await api_client.patch(
        f"/api/ingredients/inventory-batches/{BATCH_ID}/storage-mode",
        headers={"Idempotency-Key": "move-ingredient-1"},
        json={"storage_mode": "FROZEN", "reason": "Moved to freezer"},
    )
    assert moved.status_code == 200
    assert moved.json()["storage_mode"] == "FROZEN"


@pytest.mark.anyio
async def test_missing_category_and_invalid_input_are_rejected(
    api_client: httpx.AsyncClient, ingredient_routes: list[UserRole]
) -> None:
    assert ingredient_routes == [UserRole.ADMIN]
    missing = await api_client.patch(
        f"/api/ingredients/{INGREDIENT_ID}/category", json={"category_id": str(USER_ID)}
    )
    invalid = await api_client.patch(f"/api/ingredients/{INGREDIENT_ID}", json={})
    assert missing.status_code == 404
    assert missing.json()["detail"] == "Category not found"
    assert invalid.status_code == 422
