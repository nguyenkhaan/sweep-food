"""Guarded PostgreSQL integration coverage for the catalog seed entry point."""

from collections.abc import AsyncGenerator
from dataclasses import replace
from decimal import Decimal
from typing import cast

import pytest
from sqlalchemy import Select, select
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession
from sqlalchemy.sql.functions import count

from scripts.seed import (
    DEFAULT_DATASET,
    AdminSeedConfig,
    RecipeIngredientSeed,
    SeedDataset,
    SeedValidationError,
    seed_dataset,
)
from src.model.enum_model import MeasurementUnit
from src.model.ingredient_alias_model import IngredientAliasModel
from src.model.ingredient_category_model import IngredientCategoryModel
from src.model.master_ingredient_model import MasterIngredientModel
from src.model.recipe_model import RecipeModel
from src.model.user_model import UserModel


@pytest.fixture(name="seed_session")
async def _seed_session(
    database_engine: AsyncEngine,
) -> AsyncGenerator[AsyncSession, None]:
    """Run each integration test inside an isolated outer transaction."""
    async with (
        database_engine.connect() as connection,
        AsyncSession(
            bind=connection,
            expire_on_commit=False,
        ) as session,
    ):
        yield session
        await session.rollback()


@pytest.fixture(name="seed_config")
def _seed_config() -> AdminSeedConfig:
    """Supply test-only administrator identity without reading or logging secrets."""
    return AdminSeedConfig(
        name="Seed Test Administrator",
        phone_e164="+84123456701",
        email="seed-admin@example.test",
        password="test-seed-password",
    )


@pytest.fixture(name="seed_dataset_input")
def _seed_dataset_input() -> SeedDataset:
    """Use a small deterministic catalog dataset for all seed integration tests."""
    return replace(
        DEFAULT_DATASET,
        categories=(
            replace(
                DEFAULT_DATASET.categories[0],
                key="seed-test-leafy-greens",
                name="Seed test leafy greens",
            ),
        ),
        ingredients=(
            replace(
                DEFAULT_DATASET.ingredients[0],
                key="seed-test-spinach",
                category_key="seed-test-leafy-greens",
                name="Seed test spinach",
            ),
        ),
        aliases=(
            replace(
                DEFAULT_DATASET.aliases[0],
                normalized_alias="seed test baby spinach",
                alias="Seed test baby spinach",
                ingredient_key="seed-test-spinach",
            ),
        ),
        shelf_life_rules=tuple(
            replace(
                rule,
                target_key=(
                    "seed-test-spinach"
                    if rule.scope.value == "INGREDIENT"
                    else "seed-test-leafy-greens"
                ),
            )
            for rule in DEFAULT_DATASET.shelf_life_rules
        ),
        recipes=(
            replace(
                DEFAULT_DATASET.recipes[0],
                key="seed-test-spinach-soup",
                name="Seed test spinach soup",
            ),
        ),
        recipe_ingredients=(
            replace(
                DEFAULT_DATASET.recipe_ingredients[0],
                recipe_key="seed-test-spinach-soup",
                ingredient_key="seed-test-spinach",
                required_quantity=Decimal("200.000"),
            ),
        ),
    )


async def _count_rows(session: AsyncSession, statement: Select[tuple[int]]) -> int:
    """Count scoped test data without relying on global database state."""
    return cast(int, await session.scalar(statement))


@pytest.mark.anyio
async def test_seed_is_idempotent_and_reports_unchanged_records(
    seed_session: AsyncSession,
    seed_config: AdminSeedConfig,
    seed_dataset_input: SeedDataset,
) -> None:
    """The second natural-key run changes no row count and reports no new records."""
    first = await seed_dataset(seed_session, seed_config, seed_dataset_input)
    second = await seed_dataset(seed_session, seed_config, seed_dataset_input)

    assert first.summary() == "created=8 updated=0 unchanged=0 rejected=0"
    assert second.summary() == "created=0 updated=0 unchanged=8 rejected=0"
    assert (
        await _count_rows(
            seed_session,
            select(count())
            .select_from(UserModel)
            .where(
                UserModel.phone_e164 == seed_config.phone_e164,
            ),
        )
        == 1
    )
    assert (
        await _count_rows(
            seed_session,
            select(count())
            .select_from(IngredientCategoryModel)
            .where(
                IngredientCategoryModel.name == seed_dataset_input.categories[0].name,
            ),
        )
        == 1
    )
    assert (
        await _count_rows(
            seed_session,
            select(count())
            .select_from(MasterIngredientModel)
            .where(
                MasterIngredientModel.name == seed_dataset_input.ingredients[0].name,
            ),
        )
        == 1
    )
    assert (
        await _count_rows(
            seed_session,
            select(count())
            .select_from(IngredientAliasModel)
            .where(
                IngredientAliasModel.normalized_alias
                == seed_dataset_input.aliases[0].normalized_alias,
            ),
        )
        == 1
    )
    assert (
        await _count_rows(
            seed_session,
            select(count())
            .select_from(RecipeModel)
            .where(
                RecipeModel.name == seed_dataset_input.recipes[0].name,
            ),
        )
        == 1
    )


@pytest.mark.anyio
async def test_seed_dry_run_reports_changes_without_writes(
    seed_session: AsyncSession,
    seed_config: AdminSeedConfig,
    seed_dataset_input: SeedDataset,
) -> None:
    """Dry-run classifies intended inserts but leaves all matching data absent."""
    created_report = await seed_dataset(
        seed_session,
        seed_config,
        seed_dataset_input,
        dry_run=True,
    )
    changed_dataset = replace(
        seed_dataset_input,
        recipes=(
            replace(
                seed_dataset_input.recipes[0],
                details=replace(
                    seed_dataset_input.recipes[0].details,
                    description="This change must remain a dry-run only.",
                ),
            ),
        ),
    )
    await seed_dataset(seed_session, seed_config, seed_dataset_input)
    updated_report = await seed_dataset(
        seed_session,
        seed_config,
        changed_dataset,
        dry_run=True,
    )

    assert created_report.summary() == "created=8 updated=0 unchanged=0 rejected=0"
    assert updated_report.summary() == "created=0 updated=1 unchanged=7 rejected=0"
    stored_recipe = await seed_session.scalar(
        select(RecipeModel).where(
            RecipeModel.name == seed_dataset_input.recipes[0].name,
        ),
    )
    assert stored_recipe is not None
    assert (
        stored_recipe.description == seed_dataset_input.recipes[0].details.description
    )


@pytest.mark.anyio
async def test_invalid_seed_rejects_before_any_partial_write(
    seed_session: AsyncSession,
    seed_config: AdminSeedConfig,
    seed_dataset_input: SeedDataset,
) -> None:
    """Broken unit/reference input has an actionable report and writes no rows."""
    broken_ingredient = RecipeIngredientSeed(
        recipe_key="seed-test-spinach-soup",
        ingredient_key="unknown-ingredient",
        required_quantity=Decimal("200.000"),
        unit=cast(MeasurementUnit, "INVALID"),
    )
    broken_dataset = replace(
        seed_dataset_input, recipe_ingredients=(broken_ingredient,)
    )

    with pytest.raises(SeedValidationError) as error:
        await seed_dataset(seed_session, seed_config, broken_dataset, dry_run=True)

    assert "invalid unit" in str(error.value)
    assert "unknown-ingredient" in str(error.value)
    assert error.value.report.rejected
    assert (
        await _count_rows(
            seed_session,
            select(count())
            .select_from(UserModel)
            .where(
                UserModel.phone_e164 == seed_config.phone_e164,
            ),
        )
        == 0
    )
    assert (
        await _count_rows(
            seed_session,
            select(count())
            .select_from(IngredientCategoryModel)
            .where(
                IngredientCategoryModel.name == seed_dataset_input.categories[0].name,
            ),
        )
        == 0
    )
    assert (
        await _count_rows(
            seed_session,
            select(count())
            .select_from(RecipeModel)
            .where(
                RecipeModel.name == seed_dataset_input.recipes[0].name,
            ),
        )
        == 0
    )
