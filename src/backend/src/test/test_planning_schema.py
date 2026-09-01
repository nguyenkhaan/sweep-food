"""PostgreSQL integration coverage for Task 5.1 planning persistence."""

from collections.abc import AsyncGenerator
from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from typing import Any, cast
from uuid import UUID, uuid4

import pytest
from sqlalchemy import (
    ForeignKeyConstraint,
    Index,
    Table,
    UniqueConstraint,
    inspect,
    select,
)
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession
from sqlalchemy.orm import Mapper

from src.model.enum_model import (
    MealPlanItemStatus,
    MealSlot,
    MeasurementUnit,
    RecommendationProviderType,
    ShoppingListStatus,
)
from src.model.favorite_menu_item_model import FavoriteMenuItemModel
from src.model.favorite_menu_model import FavoriteMenuModel
from src.model.favorite_recipe_model import FavoriteRecipeModel
from src.model.ingredient_category_model import IngredientCategoryModel
from src.model.master_ingredient_model import MasterIngredientModel
from src.model.meal_plan_item_model import MealPlanItemModel
from src.model.meal_plan_model import MealPlanModel
from src.model.recipe_model import RecipeModel
from src.model.recommendation_item_model import RecommendationItemModel
from src.model.recommendation_run_model import RecommendationRunModel
from src.model.shopping_list_item_model import ShoppingListItemModel
from src.model.shopping_list_model import ShoppingListModel
from src.model.user_model import UserModel


@pytest.fixture(name="planning_session")
async def _planning_session(
    database_engine: AsyncEngine,
) -> AsyncGenerator[AsyncSession, None]:
    """Yield a savepoint-backed session and roll back every test's data."""
    async with database_engine.connect() as connection:
        transaction = await connection.begin()
        session = AsyncSession(
            bind=connection,
            expire_on_commit=False,
            join_transaction_mode="create_savepoint",
        )
        try:
            yield session
        finally:
            await session.close()
            await transaction.rollback()


def _unique_value(prefix: str) -> str:
    """Return a test-local value that cannot collide with another invocation."""
    return f"{prefix}-{uuid4().hex}"


def _user() -> UserModel:
    """Build the minimum valid user that owns planning records."""
    return UserModel(
        phone_e164=f"+84{uuid4().int % 10**10:010d}",
        password_hash="schema-test-password-hash",
    )


def _recipe() -> RecipeModel:
    """Build the minimum valid recipe for planning references."""
    return RecipeModel(
        name=_unique_value("Planning recipe"),
        description="Planning schema test recipe.",
        instructions={"steps": []},
        default_servings=Decimal("2.00"),
        estimated_cooking_minutes=15,
        tags={"values": []},
    )


@dataclass(frozen=True)
class PlanningContext:
    """Persisted prerequisite records for one planning schema scenario."""

    user: UserModel
    recipe: RecipeModel
    ingredient: MasterIngredientModel


async def _planning_context(session: AsyncSession) -> PlanningContext:
    """Create the user, recipe, and ingredient required by planning rows."""
    user = _user()
    category = IngredientCategoryModel(name=_unique_value("Planning category"))
    recipe = _recipe()
    session.add_all([user, category, recipe])
    await session.flush()
    ingredient = MasterIngredientModel(
        name=_unique_value("Planning ingredient"),
        description="Planning schema test ingredient.",
        category_id=category.id,
        canonical_unit=MeasurementUnit.GRAM,
    )
    session.add(ingredient)
    await session.flush()
    return PlanningContext(user=user, recipe=recipe, ingredient=ingredient)


def _meal_plan(user_id: UUID) -> MealPlanModel:
    """Build a bounded plan used to test date and slot invariants."""
    return MealPlanModel(
        user_id=user_id,
        name="Schema plan",
        starts_on=date(2026, 9, 7),
        ends_on=date(2026, 9, 13),
    )


def _meal_plan_item(
    meal_plan_id: UUID,
    recipe_id: UUID,
    planned_for: date,
    meal_slot: MealSlot,
    **values: float | UUID | None,
) -> MealPlanItemModel:
    """Build one planned recipe selection."""
    return MealPlanItemModel(
        meal_plan_id=meal_plan_id,
        recipe_id=recipe_id,
        recommendation_run_id=cast(UUID | None, values.get("recommendation_run_id")),
        planned_for=planned_for,
        meal_slot=meal_slot,
        servings=cast(float, values.get("servings", 2.0)),
        status=MealPlanItemStatus.PLANNED,
    )


async def _assert_integrity_error(session: AsyncSession, record: object) -> None:
    """Assert one model insert is rejected without losing the outer transaction."""
    with pytest.raises(IntegrityError):
        async with session.begin_nested():
            session.add(cast(Any, record))
            await session.flush()


def _table(model: object) -> Table:
    """Return typed table metadata for a declarative model."""
    return cast(Table, cast(Any, model).__table__)


def _table_relationships_are_bidirectional(model: object) -> None:
    """Assert every Task 5.1 relationship advertises its reverse attribute."""
    mapper = cast(Mapper[Any], inspect(cast(Any, model)))
    for relationship in mapper.relationships:
        assert relationship.back_populates is not None


def test_planning_models_have_required_relationships_indexes_and_foreign_keys() -> None:
    """Expose typed, bidirectional ORM links and the planning query indexes."""
    models = (
        UserModel,
        RecipeModel,
        MasterIngredientModel,
        RecommendationRunModel,
        RecommendationItemModel,
        MealPlanModel,
        MealPlanItemModel,
        FavoriteRecipeModel,
        FavoriteMenuModel,
        FavoriteMenuItemModel,
        ShoppingListModel,
        ShoppingListItemModel,
    )
    for model in models:
        _table_relationships_are_bidirectional(model)

    expected_indexes: dict[object, set[str]] = {
        RecommendationRunModel: {"ix_recommendation_runs_user_created_at"},
        RecommendationItemModel: {"ix_recommendation_items_recipe_id"},
        MealPlanModel: {"ix_meal_plans_user_starts_on"},
        MealPlanItemModel: {
            "ix_meal_plan_items_plan_planned_for",
            "ix_meal_plan_items_recipe_id",
            "ix_meal_plan_items_recommendation_run_id",
        },
        FavoriteRecipeModel: {"ix_favorite_recipes_recipe_id"},
        FavoriteMenuModel: {"ix_favorite_menus_user_created_at"},
        FavoriteMenuItemModel: {"ix_favorite_menu_items_recipe_id"},
        ShoppingListModel: {"ix_shopping_lists_user_status"},
        ShoppingListItemModel: {
            "ix_shopping_list_items_list_id",
            "ix_shopping_list_items_master_ingredient_id",
        },
    }
    for indexed_model, names in expected_indexes.items():
        index_names = {
            index.name
            for index in _table(indexed_model).indexes
            if isinstance(index, Index)
        }
        assert names <= index_names

    required_foreign_keys: dict[object, set[str]] = {
        RecommendationRunModel: {"users"},
        RecommendationItemModel: {"recommendation_runs", "recipes"},
        MealPlanModel: {"users"},
        MealPlanItemModel: {"meal_plans", "recipes", "recommendation_runs"},
        FavoriteRecipeModel: {"users", "recipes"},
        FavoriteMenuModel: {"users"},
        FavoriteMenuItemModel: {"favorite_menus", "recipes"},
        ShoppingListModel: {"users", "meal_plans"},
        ShoppingListItemModel: {"shopping_lists", "master_ingredients"},
    }
    for fk_model, target_tables in required_foreign_keys.items():
        foreign_key_targets = {
            foreign_key.target_fullname.split(".")[0]
            for constraint in _table(fk_model).constraints
            if isinstance(constraint, ForeignKeyConstraint)
            for foreign_key in constraint.elements
        }
        assert target_tables <= foreign_key_targets

    favorite_recipe_uniques = {
        tuple(column.name for column in constraint.columns)
        for constraint in _table(FavoriteRecipeModel).constraints
        if isinstance(constraint, UniqueConstraint)
    }
    favorite_menu_item_uniques = {
        tuple(column.name for column in constraint.columns)
        for constraint in _table(FavoriteMenuItemModel).constraints
        if isinstance(constraint, UniqueConstraint)
    }
    assert ("user_id", "recipe_id") in favorite_recipe_uniques
    assert ("favorite_menu_id", "recipe_id") in favorite_menu_item_uniques
    assert "position" not in _table(FavoriteMenuItemModel).columns


@pytest.mark.anyio
async def test_recommendation_persistence_enforces_ownership_rank_and_scores(
    planning_session: AsyncSession,
) -> None:
    """Persist provider/version and component scores, and reject invalid ownership/rank."""
    context = await _planning_context(planning_session)
    await _assert_integrity_error(
        planning_session,
        RecommendationRunModel(
            user_id=uuid4(),
            criteria={},
            provider=RecommendationProviderType.RULE_BASED_MVP,
        ),
    )

    recommendation_run = RecommendationRunModel(
        user_id=context.user.id,
        criteria={"days": 7},
        provider=RecommendationProviderType.RULE_BASED_MVP,
        model_version="v1",
        summary="Schema test run",
    )
    planning_session.add(recommendation_run)
    await planning_session.flush()
    recommendation_item = RecommendationItemModel(
        recommendation_run_id=recommendation_run.id,
        recipe_id=context.recipe.id,
        rank=1,
        total_score=0.9,
        expiration_utilization_score=0.4,
        availability_score=0.3,
        preference_fit_score=0.1,
        purchase_minimization_score=0.1,
        explanation={"reason": "schema test"},
    )
    planning_session.add(recommendation_item)
    await planning_session.flush()
    assert recommendation_run.provider is RecommendationProviderType.RULE_BASED_MVP
    assert recommendation_run.model_version == "v1"
    assert recommendation_item.total_score == pytest.approx(0.9)
    assert recommendation_item.expiration_utilization_score == pytest.approx(0.4)
    assert recommendation_item.recipe_id == context.recipe.id
    await _assert_integrity_error(
        planning_session,
        RecommendationItemModel(
            recommendation_run_id=recommendation_run.id,
            recipe_id=context.recipe.id,
            rank=1,
            total_score=0.8,
            expiration_utilization_score=0.3,
            availability_score=0.2,
            preference_fit_score=0.2,
            purchase_minimization_score=0.1,
            explanation={},
        ),
    )


@pytest.mark.anyio
async def test_meal_plan_persistence_enforces_range_slots_and_servings(
    planning_session: AsyncSession,
) -> None:
    """Reject invalid plan dates and slots while allowing a repeated recipe later."""
    context = await _planning_context(planning_session)
    await _assert_integrity_error(
        planning_session,
        MealPlanModel(
            user_id=context.user.id,
            starts_on=date(2026, 9, 8),
            ends_on=date(2026, 9, 7),
        ),
    )

    meal_plan = _meal_plan(context.user.id)
    planning_session.add(meal_plan)
    await planning_session.flush()
    for invalid_item in (
        _meal_plan_item(
            meal_plan.id,
            context.recipe.id,
            date(2026, 9, 6),
            MealSlot.BREAKFAST,
        ),
        _meal_plan_item(
            meal_plan.id,
            context.recipe.id,
            date(2026, 9, 8),
            MealSlot.BREAKFAST,
            servings=0.0,
        ),
    ):
        await _assert_integrity_error(planning_session, invalid_item)

    breakfast = _meal_plan_item(
        meal_plan.id,
        context.recipe.id,
        date(2026, 9, 8),
        MealSlot.BREAKFAST,
    )
    another_day = _meal_plan_item(
        meal_plan.id,
        context.recipe.id,
        date(2026, 9, 9),
        MealSlot.BREAKFAST,
    )
    planning_session.add_all([breakfast, another_day])
    await planning_session.flush()
    assert breakfast.recipe_id == another_day.recipe_id == context.recipe.id
    await _assert_integrity_error(
        planning_session,
        _meal_plan_item(
            meal_plan.id,
            context.recipe.id,
            date(2026, 9, 8),
            MealSlot.BREAKFAST,
        ),
    )
    with pytest.raises(IntegrityError):
        async with planning_session.begin_nested():
            meal_plan.ends_on = date(2026, 9, 8)
            await planning_session.flush()
    await planning_session.refresh(meal_plan)


@pytest.mark.anyio
async def test_favorite_and_shopping_persistence_enforces_identity_and_edits(
    planning_session: AsyncSession,
) -> None:
    """Keep favorite memberships unique and shopping items editable and traceable."""
    context = await _planning_context(planning_session)
    meal_plan = _meal_plan(context.user.id)
    planning_session.add(meal_plan)
    await planning_session.flush()
    favorite_recipe = FavoriteRecipeModel(
        user_id=context.user.id,
        recipe_id=context.recipe.id,
    )
    favorite_menu = FavoriteMenuModel(user_id=context.user.id, name="Quick meals")
    planning_session.add_all([favorite_recipe, favorite_menu])
    await planning_session.flush()
    favorite_menu_item = FavoriteMenuItemModel(
        favorite_menu_id=favorite_menu.id,
        recipe_id=context.recipe.id,
    )
    planning_session.add(favorite_menu_item)
    await planning_session.flush()
    for duplicate in (
        FavoriteRecipeModel(user_id=context.user.id, recipe_id=context.recipe.id),
        FavoriteMenuItemModel(
            favorite_menu_id=favorite_menu.id,
            recipe_id=context.recipe.id,
        ),
    ):
        await _assert_integrity_error(planning_session, duplicate)

    shopping_list = ShoppingListModel(
        user_id=context.user.id,
        meal_plan_id=meal_plan.id,
        status=ShoppingListStatus.ACTIVE,
    )
    planning_session.add(shopping_list)
    await planning_session.flush()
    source_metadata = {"recipe_ids": [str(context.recipe.id)], "generated": True}
    shopping_item = ShoppingListItemModel(
        shopping_list_id=shopping_list.id,
        master_ingredient_id=context.ingredient.id,
        custom_name=None,
        required_quantity=100.0,
        available_quantity=25.0,
        missing_quantity=75.0,
        unit=MeasurementUnit.GRAM,
        estimated_cost=12.5,
        is_checked=False,
        source_metadata=source_metadata,
    )
    planning_session.add(shopping_item)
    await planning_session.flush()
    stored_metadata = await planning_session.scalar(
        select(ShoppingListItemModel.source_metadata).where(
            ShoppingListItemModel.id == shopping_item.id
        )
    )
    assert stored_metadata == source_metadata
    for invalid_item in (
        ShoppingListItemModel(
            shopping_list_id=shopping_list.id,
            master_ingredient_id=context.ingredient.id,
            custom_name="Duplicate identity",
            required_quantity=1.0,
            available_quantity=0.0,
            missing_quantity=1.0,
            unit=MeasurementUnit.GRAM,
            is_checked=False,
            source_metadata={},
        ),
        ShoppingListItemModel(
            shopping_list_id=shopping_list.id,
            master_ingredient_id=None,
            custom_name="",
            required_quantity=1.0,
            available_quantity=0.0,
            missing_quantity=1.0,
            unit=MeasurementUnit.GRAM,
            is_checked=False,
            source_metadata={},
        ),
        ShoppingListItemModel(
            shopping_list_id=shopping_list.id,
            master_ingredient_id=None,
            custom_name="Manual item",
            required_quantity=0.0,
            available_quantity=0.0,
            missing_quantity=0.0,
            unit=MeasurementUnit.PIECE,
            is_checked=False,
            source_metadata={},
        ),
    ):
        await _assert_integrity_error(planning_session, invalid_item)
