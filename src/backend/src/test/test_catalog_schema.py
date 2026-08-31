"""PostgreSQL integration coverage for catalog and recipe schema invariants."""

from collections.abc import AsyncGenerator
from decimal import Decimal
from uuid import UUID, uuid4

import pytest
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession
from sqlalchemy.orm import selectinload

from src.model.enum_model import MeasurementUnit, ShelfLifeRuleScope, StorageMode
from src.model.ingredient_alias_model import IngredientAliasModel
from src.model.ingredient_category_model import IngredientCategoryModel
from src.model.master_ingredient_model import MasterIngredientModel
from src.model.recipe_ingredient_model import RecipeIngredientModel
from src.model.recipe_model import RecipeModel
from src.model.shelf_life_rule_model import ShelfLifeRuleModel


@pytest.fixture(name="catalog_session")
async def _catalog_session(
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


def _unique_name(prefix: str) -> str:
    """Return a test-local name that cannot collide with another test invocation."""
    return f"{prefix}-{uuid4().hex}"


def _recipe(name: str, servings: Decimal = Decimal("2.00")) -> RecipeModel:
    """Build the minimum valid recipe for schema tests."""
    return RecipeModel(
        name=name,
        description="Schema-test recipe.",
        instructions={"steps": []},
        default_servings=servings,
        estimated_cooking_minutes=10,
        tags={"values": []},
    )


def _ingredient(name: str, category_id: UUID) -> MasterIngredientModel:
    """Build the minimum valid master ingredient for schema tests."""
    return MasterIngredientModel(
        name=name,
        description="Schema-test ingredient.",
        category_id=category_id,
        canonical_unit=MeasurementUnit.GRAM,
    )


def _configure_database_target_guard(
    monkeypatch: pytest.MonkeyPatch,
    application_url: str,
    test_url: str,
) -> None:
    """Configure the real target guard with synthetic URLs without connecting."""
    monkeypatch.delenv("TEST_DATABASE_GUARD_APPLICATION_URL", raising=False)
    monkeypatch.setenv("TEST_DATABASE_URL", test_url)
    monkeypatch.setattr("test.conftest.DATABASE_URL", application_url)


def _guard_error(request: pytest.FixtureRequest) -> str:
    """Capture the real guard's generic failure message without a connection."""
    with pytest.raises(pytest.fail.Exception) as error:
        request.getfixturevalue("isolated_database_url")
    return str(error.value)


@pytest.mark.parametrize(
    ("application_url", "test_url"),
    [
        (
            "postgresql://application:password@db.example.test:5432/catalog",
            "postgresql://application:password@db.example.test:5432/catalog",
        ),
        (
            "postgresql://application:password@db.example.test:5432/catalog?sslmode=require",
            "postgresql://test-user:other-password@DB.EXAMPLE.TEST/catalog?sslmode=disable",
        ),
        (
            (
                "postgresql://application:password@"
                "ep-calm-tree-123456.us-east-2.aws.neon.tech/catalog"
            ),
            (
                "postgresql://test-user:other-password@"
                "ep-calm-tree-123456-pooler.us-east-2.aws.neon.tech:5432/catalog"
            ),
        ),
    ],
)
def test_database_target_guard_rejects_equivalent_targets(
    monkeypatch: pytest.MonkeyPatch,
    request: pytest.FixtureRequest,
    application_url: str,
    test_url: str,
) -> None:
    """Reject raw-identical, normalized-identical, and pooled Neon targets."""
    _configure_database_target_guard(monkeypatch, application_url, test_url)
    message = _guard_error(request)

    assert message == "Database integration configuration is invalid."
    for detail in ("application", "password", "db.example", "catalog", "sslmode"):
        assert detail not in message


def test_database_target_guard_accepts_distinct_neon_targets(
    monkeypatch: pytest.MonkeyPatch,
    request: pytest.FixtureRequest,
) -> None:
    """Accept two distinct Neon branch endpoints without opening a connection."""
    _configure_database_target_guard(
        monkeypatch,
        (
            "postgresql://application:password@"
            "ep-calm-tree-123456.us-east-2.aws.neon.tech/catalog"
        ),
        (
            "postgresql://test-user:other-password@"
            "ep-still-lake-654321-pooler.us-east-2.aws.neon.tech/catalog"
        ),
    )
    request.getfixturevalue("isolated_database_url")


def test_database_target_guard_supports_a_guarded_test_child(
    monkeypatch: pytest.MonkeyPatch,
    request: pytest.FixtureRequest,
) -> None:
    """Keep the original application target for comparison after child URL replacement."""
    application_url = (
        "postgresql://application:password@"
        "ep-calm-tree-123456.us-east-2.aws.neon.tech/catalog"
    )
    test_url = (
        "postgresql://test-user:other-password@"
        "ep-still-lake-654321-pooler.us-east-2.aws.neon.tech/catalog"
    )
    _configure_database_target_guard(monkeypatch, test_url, test_url)
    monkeypatch.setenv("TEST_DATABASE_GUARD_APPLICATION_URL", application_url)

    request.getfixturevalue("isolated_database_url")


@pytest.mark.parametrize(
    "test_url",
    [
        "postgresql://test-user:password@/catalog",
        "postgresql://test-user:password@db.example.test",
        "not-a-database-url",
    ],
)
def test_database_target_guard_rejects_malformed_urls(
    monkeypatch: pytest.MonkeyPatch,
    request: pytest.FixtureRequest,
    test_url: str,
) -> None:
    """Reject malformed or incomplete targets without exposing their components."""
    _configure_database_target_guard(
        monkeypatch,
        "postgresql://application:password@db.example.test/catalog",
        test_url,
    )
    message = _guard_error(request)

    assert message == "Database integration configuration is invalid."
    assert "test-user" not in message
    assert "password" not in message


@pytest.mark.anyio
async def test_case_insensitive_catalog_uniqueness(
    catalog_session: AsyncSession,
) -> None:
    """Enforce category, recipe, and within-category ingredient uniqueness."""
    category_name = _unique_name("Vegetables")
    recipe_name = _unique_name("Tomato soup")
    category = IngredientCategoryModel(name=category_name)
    other_category = IngredientCategoryModel(name=_unique_name("Other"))
    recipe = _recipe(recipe_name)
    catalog_session.add_all([category, other_category, recipe])
    await catalog_session.flush()
    ingredient_name = _unique_name("Tomato")
    catalog_session.add(_ingredient(ingredient_name, category.id))
    await catalog_session.flush()

    for record in (
        IngredientCategoryModel(name=category_name.upper()),
        _recipe(recipe_name.upper()),
        _ingredient(ingredient_name.upper(), category.id),
    ):
        with pytest.raises(IntegrityError):
            async with catalog_session.begin_nested():
                catalog_session.add(record)
                await catalog_session.flush()

    catalog_session.add(_ingredient(ingredient_name.upper(), other_category.id))
    await catalog_session.flush()


@pytest.mark.anyio
async def test_recipe_positive_constraints_and_foreign_keys(
    catalog_session: AsyncSession,
) -> None:
    """Reject non-positive recipe values and invalid recipe-ingredient foreign keys."""
    with pytest.raises(IntegrityError):
        async with catalog_session.begin_nested():
            catalog_session.add(_recipe(_unique_name("Zero servings"), Decimal("0.00")))
            await catalog_session.flush()

    category = IngredientCategoryModel(name=_unique_name("Produce"))
    recipe = _recipe(_unique_name("Salad"))
    catalog_session.add_all([category, recipe])
    await catalog_session.flush()
    ingredient = _ingredient(_unique_name("Lettuce"), category.id)
    catalog_session.add(ingredient)
    await catalog_session.flush()

    for recipe_id, master_ingredient_id, quantity in (
        (recipe.id, ingredient.id, Decimal("0.000")),
        (uuid4(), ingredient.id, Decimal("1.000")),
        (recipe.id, uuid4(), Decimal("1.000")),
    ):
        with pytest.raises(IntegrityError):
            async with catalog_session.begin_nested():
                catalog_session.add(
                    RecipeIngredientModel(
                        recipe_id=recipe_id,
                        master_ingredient_id=master_ingredient_id,
                        required_quantity=quantity,
                        unit=MeasurementUnit.GRAM,
                        is_optional=False,
                    ),
                )
                await catalog_session.flush()


@pytest.mark.anyio
async def test_shelf_life_constraints_reject_invalid_ranges_and_targets(
    catalog_session: AsyncSession,
) -> None:
    """Exercise every range and scope/target check at the database boundary."""
    category = IngredientCategoryModel(name=_unique_name("Protein"))
    catalog_session.add(category)
    await catalog_session.flush()
    ingredient = _ingredient(_unique_name("Tofu"), category.id)
    catalog_session.add(ingredient)
    await catalog_session.flush()

    invalid_rules = (
        (ShelfLifeRuleScope.INGREDIENT, ingredient.id, None, -1, 2, 1),
        (ShelfLifeRuleScope.INGREDIENT, ingredient.id, None, 0, -1, 0),
        (ShelfLifeRuleScope.INGREDIENT, ingredient.id, None, 0, 1, -1),
        (ShelfLifeRuleScope.INGREDIENT, ingredient.id, None, 3, 2, 2),
        (ShelfLifeRuleScope.INGREDIENT, ingredient.id, None, 1, 3, 4),
        (ShelfLifeRuleScope.INGREDIENT, None, category.id, 1, 3, 2),
        (ShelfLifeRuleScope.INGREDIENT, None, None, 1, 3, 2),
        (ShelfLifeRuleScope.CATEGORY, ingredient.id, None, 1, 3, 2),
        (ShelfLifeRuleScope.CATEGORY, ingredient.id, category.id, 1, 3, 2),
    )
    for (
        scope,
        master_ingredient_id,
        category_id,
        min_days,
        max_days,
        default_days,
    ) in invalid_rules:
        with pytest.raises(IntegrityError):
            async with catalog_session.begin_nested():
                catalog_session.add(
                    ShelfLifeRuleModel(
                        scope=scope,
                        master_ingredient_id=master_ingredient_id,
                        category_id=category_id,
                        storage_mode=StorageMode.REFRIGERATED,
                        min_days=min_days,
                        max_days=max_days,
                        default_days=default_days,
                    ),
                )
                await catalog_session.flush()


@pytest.mark.anyio
async def test_numeric_values_round_trip_as_decimal(
    catalog_session: AsyncSession,
) -> None:
    """Persist approved Numeric values without a float conversion or precision loss."""
    category = IngredientCategoryModel(name=_unique_name("Numeric"))
    recipe = _recipe(_unique_name("Numeric recipe"), Decimal("2.50"))
    catalog_session.add_all([category, recipe])
    await catalog_session.flush()
    ingredient = _ingredient(_unique_name("Numeric ingredient"), category.id)
    ingredient.calories = Decimal("12.345")
    ingredient.protein_g = Decimal("6.789")
    recipe.total_calories = Decimal("30.125")
    recipe.total_protein_g = Decimal("9.876")
    catalog_session.add(ingredient)
    await catalog_session.flush()
    recipe_ingredient = RecipeIngredientModel(
        recipe_id=recipe.id,
        master_ingredient_id=ingredient.id,
        required_quantity=Decimal("123.456"),
        unit=MeasurementUnit.GRAM,
        is_optional=False,
    )
    catalog_session.add(recipe_ingredient)
    await catalog_session.flush()
    ingredient_id, recipe_id, recipe_ingredient_id = (
        ingredient.id,
        recipe.id,
        recipe_ingredient.id,
    )
    catalog_session.expunge_all()

    stored_ingredient = await catalog_session.get(MasterIngredientModel, ingredient_id)
    stored_recipe = await catalog_session.get(RecipeModel, recipe_id)
    stored_recipe_ingredient = await catalog_session.get(
        RecipeIngredientModel,
        recipe_ingredient_id,
    )
    assert stored_ingredient is not None
    assert stored_recipe is not None
    assert stored_recipe_ingredient is not None
    assert stored_ingredient.calories == Decimal("12.345")
    assert stored_recipe.default_servings == Decimal("2.50")
    assert stored_recipe.total_protein_g == Decimal("9.876")
    assert stored_recipe_ingredient.required_quantity == Decimal("123.456")


@pytest.mark.anyio
async def test_catalog_relationships_are_bidirectional(
    catalog_session: AsyncSession,
) -> None:
    """Persist and load the six catalog/recipe model relationships."""
    category = IngredientCategoryModel(name=_unique_name("Relationships"))
    ingredient = MasterIngredientModel(
        name=_unique_name("Ingredient"),
        description="Relationship-test ingredient.",
        canonical_unit=MeasurementUnit.GRAM,
        category=category,
    )
    alias = IngredientAliasModel(
        alias=_unique_name("Alias"),
        normalized_alias=_unique_name("alias").lower(),
        master_ingredient=ingredient,
    )
    ingredient_rule = ShelfLifeRuleModel(
        scope=ShelfLifeRuleScope.INGREDIENT,
        master_ingredient=ingredient,
        storage_mode=StorageMode.REFRIGERATED,
        min_days=1,
        max_days=3,
        default_days=2,
    )
    category_rule = ShelfLifeRuleModel(
        scope=ShelfLifeRuleScope.CATEGORY,
        category=category,
        storage_mode=StorageMode.DRY_SHELF,
        min_days=10,
        max_days=20,
        default_days=15,
    )
    recipe = _recipe(_unique_name("Relationship recipe"))
    recipe_ingredient = RecipeIngredientModel(
        recipe=recipe,
        master_ingredient=ingredient,
        required_quantity=Decimal("100.000"),
        unit=MeasurementUnit.GRAM,
        is_optional=False,
    )
    catalog_session.add_all([alias, ingredient_rule, category_rule, recipe_ingredient])
    await catalog_session.flush()
    category_id, recipe_id = category.id, recipe.id
    catalog_session.expunge_all()

    stored_category = await catalog_session.scalar(
        select(IngredientCategoryModel)
        .where(IngredientCategoryModel.id == category_id)
        .options(
            selectinload(IngredientCategoryModel.master_ingredients).selectinload(
                MasterIngredientModel.aliases,
            ),
            selectinload(IngredientCategoryModel.shelf_life_rules),
        ),
    )
    stored_recipe = await catalog_session.scalar(
        select(RecipeModel)
        .where(RecipeModel.id == recipe_id)
        .options(
            selectinload(RecipeModel.recipe_ingredients).selectinload(
                RecipeIngredientModel.master_ingredient,
            ),
        ),
    )
    assert stored_category is not None
    assert stored_recipe is not None
    assert stored_category.master_ingredients[0].aliases[0].alias == alias.alias
    assert len(stored_category.shelf_life_rules) == 1
    assert (
        stored_recipe.recipe_ingredients[0].master_ingredient.category_id == category_id
    )
