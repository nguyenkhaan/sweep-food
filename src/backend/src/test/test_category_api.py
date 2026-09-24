"""Route and service coverage for ingredient categories."""

from collections.abc import AsyncGenerator
from typing import cast
from uuid import UUID

import httpx
import pytest
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src.app import app
from src.middleware.auth_middleware import AuthenticatedUser, require_authentication
from src.model.enum_model import UserRole
from src.model.ingredient_category_model import IngredientCategoryModel
from src.module.category.category_dependency import get_category_service
from src.module.category.category_dto import (
    CategoryDTO,
    CreateCategoryRequestDTO,
    UpdateCategoryRequestDTO,
)
from src.module.category.category_service import CategoryService

USER_ID = UUID("018f0f90-26e6-7ce7-8f61-8769f9e5c101")
CATEGORY_ID = UUID("018f0f90-26e6-7ce7-8f61-8769f9e5c102")


class FakeCategoryService:
    """Provide in-memory category behavior for route tests."""

    def __init__(self) -> None:
        self.category = CategoryDTO(
            id=CATEGORY_ID,
            name="Vegetables",
            description="Fresh produce",
        )
        self.deleted = False

    async def create_category(self, body: CreateCategoryRequestDTO) -> CategoryDTO:
        self.category = CategoryDTO(
            id=CATEGORY_ID,
            name=body.name,
            description=body.description,
        )
        return self.category

    async def list_categories(self) -> list[CategoryDTO]:
        return [] if self.deleted else [self.category]

    async def update_category(
        self,
        category_id: UUID,
        body: UpdateCategoryRequestDTO,
    ) -> CategoryDTO:
        assert category_id == CATEGORY_ID
        values = body.model_dump(exclude_unset=True)
        self.category = CategoryDTO(
            id=CATEGORY_ID,
            name=cast(str, values.get("name", self.category.name)),
            description=cast(
                str | None,
                values.get("description", self.category.description),
            ),
        )
        return self.category

    async def delete_category(self, category_id: UUID) -> None:
        assert category_id == CATEGORY_ID
        self.deleted = True


@pytest.fixture(name="category_routes")
async def _category_routes() -> AsyncGenerator[
    tuple[list[UserRole], FakeCategoryService],
    None,
]:
    roles = [UserRole.ADMIN]
    service = FakeCategoryService()

    async def authenticated_user() -> AuthenticatedUser:
        return AuthenticatedUser(USER_ID, tuple(roles))

    def category_service() -> FakeCategoryService:
        return service

    app.dependency_overrides[require_authentication] = authenticated_user
    app.dependency_overrides[get_category_service] = category_service
    try:
        yield roles, service
    finally:
        app.dependency_overrides.pop(require_authentication, None)
        app.dependency_overrides.pop(get_category_service, None)


@pytest.mark.anyio
async def test_admin_category_crud_preserves_omitted_fields(
    api_client: httpx.AsyncClient,
    category_routes: tuple[list[UserRole], FakeCategoryService],
) -> None:
    roles, service = category_routes
    assert roles == [UserRole.ADMIN]

    created = await api_client.post(
        "/api/categories",
        json={"name": "Proteins", "description": "Protein-rich foods"},
    )
    listed = await api_client.get("/api/categories")
    updated = await api_client.patch(
        f"/api/categories/{CATEGORY_ID}",
        json={"description": "Meat, fish, eggs, and legumes"},
    )
    deleted = await api_client.delete(f"/api/categories/{CATEGORY_ID}")

    assert created.status_code == 201
    assert listed.status_code == 200
    assert listed.json()[0]["name"] == "Proteins"
    assert updated.status_code == 200
    assert updated.json()["name"] == "Proteins"
    assert updated.json()["description"] == "Meat, fish, eggs, and legumes"
    assert deleted.status_code == 204
    assert service.deleted is True


@pytest.mark.anyio
async def test_authenticated_user_can_list_but_cannot_mutate_categories(
    api_client: httpx.AsyncClient,
    category_routes: tuple[list[UserRole], FakeCategoryService],
) -> None:
    roles, _service = category_routes
    roles[:] = [UserRole.USER]

    listed = await api_client.get("/api/categories")
    created = await api_client.post("/api/categories", json={"name": "Dairy"})
    updated = await api_client.patch(
        f"/api/categories/{CATEGORY_ID}",
        json={"name": "Updated"},
    )
    deleted = await api_client.delete(f"/api/categories/{CATEGORY_ID}")

    assert listed.status_code == 200
    assert created.status_code == 403
    assert updated.status_code == 403
    assert deleted.status_code == 403


class FakeResult:
    """Return one queued scalar for a service query."""

    def __init__(self, value: object | None) -> None:
        self.value = value

    def scalar_one_or_none(self) -> object | None:
        return self.value


class FakeDatabase:
    """Provide the minimal transaction surface used by CategoryService."""

    def __init__(self, values: list[object | None]) -> None:
        self.values = iter(values)
        self.deleted: list[object] = []
        self.committed = False
        self.rolled_back = False

    async def execute(self, _statement: object) -> FakeResult:
        return FakeResult(next(self.values))

    async def delete(self, model: object) -> None:
        self.deleted.append(model)

    async def commit(self) -> None:
        self.committed = True

    async def rollback(self) -> None:
        self.rolled_back = True


@pytest.mark.anyio
async def test_category_update_and_hard_delete_preserve_expected_state() -> None:
    category = IngredientCategoryModel(
        id=CATEGORY_ID,
        name="Vegetables",
        description="Fresh produce",
    )
    update_database = FakeDatabase([category])
    updated = await CategoryService(
        cast(AsyncSession, update_database)
    ).update_category(
        CATEGORY_ID,
        UpdateCategoryRequestDTO(name="Produce"),
    )

    assert updated.name == "Produce"
    assert updated.description == "Fresh produce"
    assert update_database.committed is True

    delete_database = FakeDatabase([category, None, None])
    await CategoryService(cast(AsyncSession, delete_database)).delete_category(
        CATEGORY_ID
    )

    assert delete_database.deleted == [category]
    assert delete_database.committed is True


@pytest.mark.anyio
async def test_in_use_category_returns_409_without_deleting() -> None:
    category = IngredientCategoryModel(
        id=CATEGORY_ID,
        name="Vegetables",
        description=None,
    )
    database = FakeDatabase([category, 1])
    service = CategoryService(cast(AsyncSession, database))

    with pytest.raises(HTTPException) as raised:
        await service.delete_category(CATEGORY_ID)

    assert raised.value.status_code == 409
    assert raised.value.detail == "Category is already in use and cannot be deleted"
    assert database.deleted == []
    assert database.committed is False
    assert database.rolled_back is True
