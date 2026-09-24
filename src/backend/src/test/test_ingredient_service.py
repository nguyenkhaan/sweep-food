"""Unit tests for guarded master ingredient mutations."""

from typing import cast
from unittest.mock import AsyncMock
from uuid import UUID

import pytest
from fastapi import HTTPException
from sqlalchemy.dialects import postgresql
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.elements import ClauseElement

from src.model.enum_model import StorageMode
from src.model.master_ingredient_model import MasterIngredientModel
from src.module.catalog.catalog_service import CatalogService
from src.module.ingredient.ingredient_dto import (
    AssignIngredientCategoryDTO,
    UpdateIngredientDefaultStorageDTO,
    UpdateIngredientDTO,
)
from src.module.ingredient.ingredient_service import IngredientService

INGREDIENT_ID = UUID("018f0f90-26e6-7ce7-8f61-8769f9e5b103")
CATEGORY_ID = UUID("018f0f90-26e6-7ce7-8f61-8769f9e5b104")


class FakeResult:
    """Return a queued scalar for a database query."""

    def __init__(self, value: object | None) -> None:
        self.value = value

    def scalar_one_or_none(self) -> object | None:
        return self.value


class FakeDatabase:
    """Record destructive work without touching a PostgreSQL database."""

    def __init__(self, values: list[object | None]) -> None:
        self.values = iter(values)
        self.deleted: list[object] = []
        self.statements: list[object] = []
        self.execute_count = 0
        self.committed = False

    async def execute(self, statement: object) -> FakeResult:
        self.execute_count += 1
        self.statements.append(statement)
        return FakeResult(next(self.values))

    async def delete(self, model: object) -> None:
        self.deleted.append(model)

    async def commit(self) -> None:
        self.committed = True


@pytest.mark.anyio
async def test_missing_category_returns_404_without_committing() -> None:
    ingredient = MasterIngredientModel(id=INGREDIENT_ID, category_id=CATEGORY_ID)
    database = FakeDatabase([ingredient, None])
    service = IngredientService(cast(AsyncSession, database))

    with pytest.raises(HTTPException) as raised:
        await service.update_category(
            INGREDIENT_ID,
            AssignIngredientCategoryDTO(category_id=UUID(int=1)),
        )

    assert raised.value.status_code == 404
    assert raised.value.detail == "Category not found"
    assert ingredient.category_id == CATEGORY_ID
    assert database.committed is False


def _updated_columns(statement: object) -> set[str]:
    """Return columns present in a compiled SQL UPDATE SET clause."""
    sql = str(cast(ClauseElement, statement).compile(dialect=postgresql.dialect()))
    assignments = sql.partition(" SET ")[2].partition(" WHERE ")[0]
    return {
        assignment.partition("=")[0].strip() for assignment in assignments.split(",")
    }


@pytest.mark.anyio
async def test_ingredient_updates_write_only_requested_columns(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Storage, category, and general edits preserve every unrelated column."""
    ingredient = MasterIngredientModel(id=INGREDIENT_ID, category_id=CATEGORY_ID)
    get_ingredient = AsyncMock(return_value=object())
    monkeypatch.setattr(CatalogService, "get_ingredient", get_ingredient)

    general_database = FakeDatabase([ingredient, None])
    await IngredientService(cast(AsyncSession, general_database)).update_ingredient(
        INGREDIENT_ID,
        UpdateIngredientDTO(name="Baby spinach"),
    )

    storage_database = FakeDatabase([ingredient, None])
    await IngredientService(
        cast(AsyncSession, storage_database)
    ).update_default_storage(
        INGREDIENT_ID,
        UpdateIngredientDefaultStorageDTO(
            default_storage_mode=StorageMode.REFRIGERATED
        ),
    )

    category_database = FakeDatabase([ingredient, CATEGORY_ID, None])
    await IngredientService(cast(AsyncSession, category_database)).update_category(
        INGREDIENT_ID,
        AssignIngredientCategoryDTO(category_id=CATEGORY_ID),
    )

    assert _updated_columns(general_database.statements[-1]) == {
        "name",
        "updated_at",
    }
    assert _updated_columns(storage_database.statements[-1]) == {
        "default_storage_mode",
        "updated_at",
    }
    assert _updated_columns(category_database.statements[-1]) == {
        "category_id",
        "updated_at",
    }


@pytest.mark.anyio
async def test_referenced_ingredient_returns_409_without_deleting() -> None:
    ingredient = MasterIngredientModel(id=INGREDIENT_ID, category_id=CATEGORY_ID)
    database = FakeDatabase([ingredient, 1])
    service = IngredientService(cast(AsyncSession, database))

    with pytest.raises(HTTPException) as raised:
        await service.delete_ingredient(INGREDIENT_ID)

    assert raised.value.status_code == 409
    assert database.deleted == []
    assert database.committed is False


@pytest.mark.anyio
async def test_unreferenced_ingredient_and_owned_metadata_are_deleted() -> None:
    ingredient = MasterIngredientModel(id=INGREDIENT_ID, category_id=CATEGORY_ID)
    database = FakeDatabase([ingredient, None, None, None, None, None, None])
    service = IngredientService(cast(AsyncSession, database))

    await service.delete_ingredient(INGREDIENT_ID)

    assert database.execute_count == 7
    assert database.deleted == [ingredient]
    assert database.committed is True
