"""Seed deterministic local demo data for a fully migrated Sweep Food database."""
# uv run -m src.seed
import asyncio
import hashlib
from collections.abc import Sequence
from datetime import UTC, date, datetime, timedelta
from uuid import UUID, uuid5

from sqlalchemy import inspect
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from src.core.setting import DATABASE_URL, ENV
from src.db import build_async_database_url
from src.helper.pwd_hash import hashing
from src.model import (
    AuthSessionModel,
    Base,
    CookingConsumptionModel,
    CookingSessionModel,
    DeviceRegistrationModel,
    FavoriteMenuItemModel,
    FavoriteMenuModel,
    FavoriteRecipeModel,
    IngredientAliasModel,
    IngredientCategoryModel,
    InventoryBatchModel,
    InventoryLedgerEntryModel,
    MasterIngredientModel,
    MealPlanItemModel,
    MealPlanModel,
    NotificationModel,
    RecipeIngredientModel,
    RecipeModel,
    RecommendationItemModel,
    RecommendationRunModel,
    ShelfLifeRuleModel,
    ShoppingListItemModel,
    ShoppingListModel,
    UserModel,
    UserNotificationPreferenceModel,
)
from src.model.enum_model import (
    AccountStatus,
    CookingConsumptionMode,
    CookingSessionStatus,
    DevicePlatform,
    ExpirationSource,
    InventoryBatchStatus,
    InventoryBatchType,
    InventoryLedgerEventType,
    InventorySource,
    MealPlanItemStatus,
    MealSlot,
    MeasurementUnit,
    NotificationDeliveryStatus,
    NotificationStatus,
    NotificationType,
    RecommendationProviderType,
    ShelfLifeRuleScope,
    ShoppingListStatus,
    StorageMode,
    UserRole,
)

SEED_NAMESPACE = UUID("cbb5fd7e-8934-4e98-8952-572b245e48f4")
REQUIRED_TABLES = frozenset(
    {
        "auth_sessions",
        "cooking_consumptions",
        "cooking_sessions",
        "device_registrations",
        "favorite_menu_items",
        "favorite_menus",
        "favorite_recipes",
        "ingredient_aliases",
        "ingredient_categories",
        "inventory_batches",
        "inventory_ledger_entries",
        "master_ingredients",
        "meal_plan_items",
        "meal_plans",
        "notifications",
        "recommendation_items",
        "recommendation_runs",
        "recipe_ingredients",
        "recipes",
        "shelf_life_rules",
        "shopping_list_items",
        "shopping_lists",
        "user_notification_preferences",
        "users",
    },
)


def seed_id(name: str) -> UUID:
    """Return a stable UUID for a named seed record."""
    return uuid5(SEED_NAMESPACE, name)


def token_hash(value: str) -> str:
    """Return a deterministic digest for fake token data."""
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def load_demo_password() -> str:
    """Read the explicit password shared by the demo accounts."""
    password = "cloudian123"
    if not password:
        raise ValueError(
            "SEED_DEMO_PASSWORD is required; use the approved local test password.",
        )
    return password


def ensure_local_environment() -> None:
    """Reject use of local credentials against a production environment."""
    if ENV not in {"dev", "test"}:
        raise RuntimeError("The demo seed script may run only when ENV is dev or test.")


def get_table_names(connection: Connection) -> set[str]:
    """List database tables through the synchronous connection proxy."""
    return set(inspect(connection).get_table_names())


async def assert_complete_schema(engine: AsyncEngine) -> None:
    """Reject incomplete schemas before the transaction starts."""
    async with engine.connect() as connection:
        table_names = await connection.run_sync(get_table_names)

    missing_tables = sorted(REQUIRED_TABLES - table_names)
    if missing_tables:
        missing = ", ".join(missing_tables)
        raise RuntimeError(
            f"The demo dataset requires every MVP table. Missing tables: {missing}",
        )


async def merge_records(
    session: AsyncSession,
    records: Sequence[Base],
) -> None:
    """Merge one dependency-safe group of stable seed records."""
    for record in records:
        await session.merge(record)
    await session.flush()


def build_user_records(password_hash: str, now: datetime) -> list[Base]:
    """Create the requested USER and ADMIN accounts."""
    return [
        UserModel(
            id=seed_id("user-cloudian"),
            name="cloudian",
            phone_e164="+84123456789",
            phone_verified_at=now,
            email="cloudian.user@example.test",
            email_verified_at=now,
            password_hash=password_hash,
            role=UserRole.USER,
            status=AccountStatus.ACTIVE,
            preferences={
                "locale": "vi-VN",
                "dietary_preferences": [],
                "maximum_cooking_minutes": 45,
            },
        ),
        UserModel(
            id=seed_id("admin-cloudian"),
            name="cloudian",
            phone_e164="+84123456780",
            phone_verified_at=now,
            email="cloudian.admin@example.test",
            email_verified_at=now,
            password_hash=password_hash,
            role=UserRole.ADMIN,
            status=AccountStatus.ACTIVE,
            preferences={"locale": "vi-VN", "maximum_cooking_minutes": 30},
        ),
    ]


def build_session_records(now: datetime) -> list[Base]:
    """Create one safely hashed refresh session for each account."""
    return [
        AuthSessionModel(
            id=seed_id("session-user"),
            user_id=seed_id("user-cloudian"),
            refresh_token_hash=token_hash("seed-refresh-token-user"),
            token_family_id=seed_id("token-family-user"),
            ip_address="127.0.0.1",
            user_agent="Sweep Food demo user",
            expires_at=now + timedelta(days=30),
            last_used_at=now,
        ),
        AuthSessionModel(
            id=seed_id("session-admin"),
            user_id=seed_id("admin-cloudian"),
            refresh_token_hash=token_hash("seed-refresh-token-admin"),
            token_family_id=seed_id("token-family-admin"),
            ip_address="127.0.0.1",
            user_agent="Sweep Food demo admin",
            expires_at=now + timedelta(days=30),
            last_used_at=now,
        ),
    ]


def build_catalog_records() -> list[Base]:
    """Create catalog, shelf-life, recipe, and recipe-ingredient records."""
    vegetable_category_id = seed_id("category-vegetables")
    protein_category_id = seed_id("category-proteins")
    dairy_category_id = seed_id("category-dairy")
    grain_category_id = seed_id("category-grains")
    spinach_id = seed_id("ingredient-spinach")
    chicken_id = seed_id("ingredient-chicken-breast")
    milk_id = seed_id("ingredient-fresh-milk")
    rice_id = seed_id("ingredient-rice")

    return [
        IngredientCategoryModel(
            id=vegetable_category_id,
            name="Vegetables",
            description="Fresh leafy vegetables.",
        ),
        IngredientCategoryModel(
            id=protein_category_id,
            name="Proteins",
            description="Fresh animal protein.",
        ),
        IngredientCategoryModel(
            id=dairy_category_id,
            name="Dairy",
            description="Refrigerated dairy products.",
        ),
        IngredientCategoryModel(
            id=grain_category_id,
            name="Grains",
            description="Shelf-stable grain products.",
        ),
        MasterIngredientModel(
            id=spinach_id,
            name="Spinach",
            description="Fresh leafy spinach.",
            category_id=vegetable_category_id,
            canonical_unit=MeasurementUnit.GRAM,
            calories=23.0,
            protein_g=2.9,
            fat_g=0.4,
            carbs_g=3.6,
            sugar_g=0.4,
            sodium_mg=79.0,
            other_nutrients={"fiber_g": 2.2},
            default_storage_mode=StorageMode.REFRIGERATED,
        ),
        MasterIngredientModel(
            id=chicken_id,
            name="Chicken breast",
            description="Boneless raw chicken breast.",
            category_id=protein_category_id,
            canonical_unit=MeasurementUnit.GRAM,
            calories=165.0,
            protein_g=31.0,
            fat_g=3.6,
            carbs_g=0.0,
            sugar_g=0.0,
            sodium_mg=74.0,
            other_nutrients={"cholesterol_mg": 85.0},
            default_storage_mode=StorageMode.REFRIGERATED,
        ),
        MasterIngredientModel(
            id=milk_id,
            name="Fresh milk",
            description="Pasteurized cow milk.",
            category_id=dairy_category_id,
            canonical_unit=MeasurementUnit.ML,
            calories=61.0,
            protein_g=3.2,
            fat_g=3.3,
            carbs_g=4.8,
            sugar_g=4.8,
            sodium_mg=43.0,
            other_nutrients={"calcium_mg": 113.0},
            default_storage_mode=StorageMode.REFRIGERATED,
        ),
        MasterIngredientModel(
            id=rice_id,
            name="Rice",
            description="Dry white rice.",
            category_id=grain_category_id,
            canonical_unit=MeasurementUnit.GRAM,
            calories=130.0,
            protein_g=2.4,
            fat_g=0.3,
            carbs_g=28.7,
            sugar_g=0.1,
            sodium_mg=1.0,
            other_nutrients={"fiber_g": 0.4},
            default_storage_mode=StorageMode.DRY_SHELF,
        ),
        IngredientAliasModel(
            id=seed_id("alias-spinach"),
            master_ingredient_id=spinach_id,
            alias="Rau bina",
            normalized_alias="rau bina",
        ),
        IngredientAliasModel(
            id=seed_id("alias-chicken"),
            master_ingredient_id=chicken_id,
            alias="Ức gà",
            normalized_alias="uc ga",
        ),
        IngredientAliasModel(
            id=seed_id("alias-milk"),
            master_ingredient_id=milk_id,
            alias="Sữa tươi",
            normalized_alias="sua tuoi",
        ),
        IngredientAliasModel(
            id=seed_id("alias-rice"),
            master_ingredient_id=rice_id,
            alias="Gạo trắng",
            normalized_alias="gao trang",
        ),
        ShelfLifeRuleModel(
            id=seed_id("shelf-life-spinach"),
            scope=ShelfLifeRuleScope.INGREDIENT,
            master_ingredient_id=spinach_id,
            storage_mode=StorageMode.REFRIGERATED,
            min_days=3,
            max_days=5,
            default_days=4,
        ),
        ShelfLifeRuleModel(
            id=seed_id("shelf-life-chicken"),
            scope=ShelfLifeRuleScope.INGREDIENT,
            master_ingredient_id=chicken_id,
            storage_mode=StorageMode.REFRIGERATED,
            min_days=2,
            max_days=3,
            default_days=2,
        ),
        ShelfLifeRuleModel(
            id=seed_id("shelf-life-milk"),
            scope=ShelfLifeRuleScope.INGREDIENT,
            master_ingredient_id=milk_id,
            storage_mode=StorageMode.REFRIGERATED,
            min_days=3,
            max_days=5,
            default_days=4,
        ),
        ShelfLifeRuleModel(
            id=seed_id("shelf-life-rice"),
            scope=ShelfLifeRuleScope.INGREDIENT,
            master_ingredient_id=rice_id,
            storage_mode=StorageMode.DRY_SHELF,
            min_days=180,
            max_days=365,
            default_days=270,
        ),
        RecipeModel(
            id=seed_id("recipe-spinach-soup"),
            name="Spinach soup",
            description="Quick light soup with fresh spinach.",
            instructions={"steps": ["Wash spinach", "Cook for five minutes"]},
            default_servings=2.0,
            estimated_cooking_minutes=15,
            estimated_cost=25000.0,
            total_calories=46.0,
            total_protein_g=5.8,
            total_fat_g=0.8,
            total_carbs_g=7.2,
            total_sugar_g=0.8,
            other_nutrients={"fiber_g": 4.4},
            tags={"values": ["quick", "vegetarian"]},
        ),
        RecipeModel(
            id=seed_id("recipe-grilled-chicken"),
            name="Grilled chicken breast",
            description="Simple high-protein chicken breast.",
            instructions={"steps": ["Season chicken", "Grill until cooked"]},
            default_servings=2.0,
            estimated_cooking_minutes=25,
            estimated_cost=75000.0,
            total_calories=330.0,
            total_protein_g=62.0,
            total_fat_g=7.2,
            total_carbs_g=0.0,
            total_sugar_g=0.0,
            other_nutrients={"sodium_mg": 148.0},
            tags={"values": ["high-protein", "quick"]},
        ),
        RecipeModel(
            id=seed_id("recipe-milk-smoothie"),
            name="Fresh milk smoothie",
            description="A quick chilled milk drink.",
            instructions={"steps": ["Chill milk", "Blend and serve"]},
            default_servings=2.0,
            estimated_cooking_minutes=5,
            estimated_cost=18000.0,
            total_calories=122.0,
            total_protein_g=6.4,
            total_fat_g=6.6,
            total_carbs_g=9.6,
            total_sugar_g=9.6,
            other_nutrients={"calcium_mg": 226.0},
            tags={"values": ["breakfast", "quick"]},
        ),
        RecipeModel(
            id=seed_id("recipe-steamed-rice"),
            name="Steamed rice",
            description="Basic cooked white rice.",
            instructions={"steps": ["Rinse rice", "Steam until tender"]},
            default_servings=2.0,
            estimated_cooking_minutes=30,
            estimated_cost=12000.0,
            total_calories=260.0,
            total_protein_g=4.8,
            total_fat_g=0.6,
            total_carbs_g=57.4,
            total_sugar_g=0.2,
            other_nutrients={"fiber_g": 0.8},
            tags={"values": ["staple", "vegetarian"]},
        ),
        RecipeIngredientModel(
            id=seed_id("recipe-ingredient-spinach"),
            recipe_id=seed_id("recipe-spinach-soup"),
            master_ingredient_id=spinach_id,
            required_quantity=200.0,
            unit=MeasurementUnit.GRAM,
            is_optional=False,
        ),
        RecipeIngredientModel(
            id=seed_id("recipe-ingredient-chicken"),
            recipe_id=seed_id("recipe-grilled-chicken"),
            master_ingredient_id=chicken_id,
            required_quantity=300.0,
            unit=MeasurementUnit.GRAM,
            is_optional=False,
        ),
        RecipeIngredientModel(
            id=seed_id("recipe-ingredient-milk"),
            recipe_id=seed_id("recipe-milk-smoothie"),
            master_ingredient_id=milk_id,
            required_quantity=500.0,
            unit=MeasurementUnit.ML,
            is_optional=False,
        ),
        RecipeIngredientModel(
            id=seed_id("recipe-ingredient-rice"),
            recipe_id=seed_id("recipe-steamed-rice"),
            master_ingredient_id=rice_id,
            required_quantity=300.0,
            unit=MeasurementUnit.GRAM,
            is_optional=False,
        ),
    ]


def build_planning_records(today: date, now: datetime) -> list[Base]:
    """Create recommendation, meal-plan, and cooking-session test records."""
    user_plan_id = seed_id("meal-plan-user")
    admin_plan_id = seed_id("meal-plan-admin")
    user_run_id = seed_id("recommendation-run-user")
    admin_run_id = seed_id("recommendation-run-admin")
    return [
        RecommendationRunModel(
            id=user_run_id,
            user_id=seed_id("user-cloudian"),
            criteria={"servings": 2, "meal_slot": "DINNER"},
            provider=RecommendationProviderType.RULE_BASED_MVP,
            model_version="seed-v1",
            summary="Prioritizes expiring milk and available chicken.",
        ),
        RecommendationRunModel(
            id=admin_run_id,
            user_id=seed_id("admin-cloudian"),
            criteria={"servings": 2, "meal_slot": "LUNCH"},
            provider=RecommendationProviderType.RULE_BASED_MVP,
            model_version="seed-v1",
            summary="Prioritizes shelf-stable rice.",
        ),
        MealPlanModel(
            id=user_plan_id,
            user_id=seed_id("user-cloudian"),
            name="Cloudian weekly meals",
            starts_on=today,
            ends_on=today + timedelta(days=6),
        ),
        MealPlanModel(
            id=admin_plan_id,
            user_id=seed_id("admin-cloudian"),
            name="Admin sample meals",
            starts_on=today,
            ends_on=today + timedelta(days=6),
        ),
        MealPlanItemModel(
            id=seed_id("meal-plan-item-user-milk"),
            meal_plan_id=user_plan_id,
            recipe_id=seed_id("recipe-milk-smoothie"),
            recommendation_run_id=user_run_id,
            planned_for=today,
            meal_slot=MealSlot.BREAKFAST,
            servings=2.0,
            status=MealPlanItemStatus.COMPLETED,
        ),
        MealPlanItemModel(
            id=seed_id("meal-plan-item-user-chicken"),
            meal_plan_id=user_plan_id,
            recipe_id=seed_id("recipe-grilled-chicken"),
            recommendation_run_id=user_run_id,
            planned_for=today + timedelta(days=1),
            meal_slot=MealSlot.DINNER,
            servings=2.0,
            status=MealPlanItemStatus.PLANNED,
        ),
        MealPlanItemModel(
            id=seed_id("meal-plan-item-admin-rice"),
            meal_plan_id=admin_plan_id,
            recipe_id=seed_id("recipe-steamed-rice"),
            recommendation_run_id=admin_run_id,
            planned_for=today,
            meal_slot=MealSlot.LUNCH,
            servings=2.0,
            status=MealPlanItemStatus.PLANNED,
        ),
        MealPlanItemModel(
            id=seed_id("meal-plan-item-admin-spinach"),
            meal_plan_id=admin_plan_id,
            recipe_id=seed_id("recipe-spinach-soup"),
            recommendation_run_id=admin_run_id,
            planned_for=today + timedelta(days=2),
            meal_slot=MealSlot.DINNER,
            servings=2.0,
            status=MealPlanItemStatus.SKIPPED,
        ),
        CookingSessionModel(
            id=seed_id("cooking-session-user-milk"),
            user_id=seed_id("user-cloudian"),
            recipe_id=seed_id("recipe-milk-smoothie"),
            meal_plan_item_id=seed_id("meal-plan-item-user-milk"),
            servings=2.0,
            status=CookingSessionStatus.COMPLETED,
            consumption_mode=CookingConsumptionMode.EXACT,
            nutrition_snapshot={"calories": 122.0, "protein_g": 6.4},
            idempotency_key="seed-cooking-user-milk",
            completed_at=now,
        ),
        CookingSessionModel(
            id=seed_id("cooking-session-admin-rice"),
            user_id=seed_id("admin-cloudian"),
            recipe_id=seed_id("recipe-steamed-rice"),
            meal_plan_item_id=seed_id("meal-plan-item-admin-rice"),
            servings=2.0,
            status=CookingSessionStatus.PLANNED,
            nutrition_snapshot={"calories": 260.0, "carbs_g": 57.4},
            idempotency_key="seed-cooking-admin-rice",
        ),
    ]


def build_inventory_records(now: datetime) -> list[Base]:
    """Create raw inventory plus a traceable cooked leftover batch."""
    return [
        InventoryBatchModel(
            id=seed_id("batch-user-milk"),
            user_id=seed_id("user-cloudian"),
            master_ingredient_id=seed_id("ingredient-fresh-milk"),
            batch_type=InventoryBatchType.RAW_INGREDIENT,
            initial_quantity=2.0,
            current_quantity=1.5,
            unit=MeasurementUnit.LITER,
            storage_mode=StorageMode.REFRIGERATED,
            status=InventoryBatchStatus.ACTIVE,
            purchased_at=now - timedelta(days=2),
            packaged_at=now - timedelta(days=3),
            stored_at=now - timedelta(days=2),
            expires_at=now + timedelta(days=1),
            expiration_source=ExpirationSource.MANUFACTURER,
            unit_cost=36000.0,
            note="Use soon for FEFO and notification tests.",
            source=InventorySource.MANUAL,
        ),
        InventoryBatchModel(
            id=seed_id("batch-user-chicken"),
            user_id=seed_id("user-cloudian"),
            master_ingredient_id=seed_id("ingredient-chicken-breast"),
            batch_type=InventoryBatchType.RAW_INGREDIENT,
            initial_quantity=1.0,
            current_quantity=1.0,
            unit=MeasurementUnit.KG,
            storage_mode=StorageMode.REFRIGERATED,
            status=InventoryBatchStatus.ACTIVE,
            purchased_at=now,
            stored_at=now,
            expires_at=now + timedelta(days=2),
            expiration_source=ExpirationSource.ESTIMATED,
            unit_cost=95000.0,
            note="Estimated shelf life from the chicken rule.",
            source=InventorySource.MANUAL,
        ),
        InventoryBatchModel(
            id=seed_id("batch-user-leftover"),
            user_id=seed_id("user-cloudian"),
            custom_name="Fresh milk smoothie leftover",
            batch_type=InventoryBatchType.COOKED_FOOD,
            initial_quantity=1.0,
            current_quantity=1.0,
            unit=MeasurementUnit.PACK,
            storage_mode=StorageMode.REFRIGERATED,
            status=InventoryBatchStatus.ACTIVE,
            stored_at=now,
            expires_at=now + timedelta(days=1),
            expiration_source=ExpirationSource.USER_OVERRIDE,
            note="Created from the completed smoothie session.",
            source=InventorySource.LEFTOVER,
            source_cooking_session_id=seed_id("cooking-session-user-milk"),
        ),
    ]


def build_activity_records(today: date, now: datetime) -> list[Base]:
    """Create dependent audit, notification, and user-content records."""
    user_id = seed_id("user-cloudian")
    admin_id = seed_id("admin-cloudian")
    user_plan_id = seed_id("meal-plan-user")
    admin_plan_id = seed_id("meal-plan-admin")
    user_run_id = seed_id("recommendation-run-user")
    admin_run_id = seed_id("recommendation-run-admin")
    milk_batch_id = seed_id("batch-user-milk")
    chicken_batch_id = seed_id("batch-user-chicken")
    leftover_batch_id = seed_id("batch-user-leftover")
    return [
        RecommendationItemModel(
            id=seed_id("recommendation-item-user-milk"),
            recommendation_run_id=user_run_id,
            recipe_id=seed_id("recipe-milk-smoothie"),
            rank=1,
            total_score=0.91,
            expiration_utilization_score=0.95,
            availability_score=0.9,
            preference_fit_score=0.8,
            purchase_minimization_score=1.0,
            explanation={"reason": "Uses expiring fresh milk."},
        ),
        RecommendationItemModel(
            id=seed_id("recommendation-item-user-chicken"),
            recommendation_run_id=user_run_id,
            recipe_id=seed_id("recipe-grilled-chicken"),
            rank=2,
            total_score=0.79,
            expiration_utilization_score=0.7,
            availability_score=0.9,
            preference_fit_score=0.8,
            purchase_minimization_score=0.7,
            explanation={"reason": "Chicken is fully available."},
        ),
        RecommendationItemModel(
            id=seed_id("recommendation-item-admin-rice"),
            recommendation_run_id=admin_run_id,
            recipe_id=seed_id("recipe-steamed-rice"),
            rank=1,
            total_score=0.86,
            expiration_utilization_score=0.6,
            availability_score=1.0,
            preference_fit_score=0.9,
            purchase_minimization_score=1.0,
            explanation={"reason": "Rice is available in dry storage."},
        ),
        RecommendationItemModel(
            id=seed_id("recommendation-item-admin-spinach"),
            recommendation_run_id=admin_run_id,
            recipe_id=seed_id("recipe-spinach-soup"),
            rank=2,
            total_score=0.51,
            expiration_utilization_score=0.0,
            availability_score=0.0,
            preference_fit_score=0.9,
            purchase_minimization_score=0.8,
            explanation={"reason": "Spinach must be purchased."},
        ),
        CookingConsumptionModel(
            id=seed_id("cooking-consumption-user-milk-first-half"),
            cooking_session_id=seed_id("cooking-session-user-milk"),
            recipe_ingredient_id=seed_id("recipe-ingredient-milk"),
            inventory_batch_id=milk_batch_id,
            quantity=0.25,
            unit=MeasurementUnit.LITER,
        ),
        CookingConsumptionModel(
            id=seed_id("cooking-consumption-user-milk-second-half"),
            cooking_session_id=seed_id("cooking-session-user-milk"),
            recipe_ingredient_id=seed_id("recipe-ingredient-milk"),
            inventory_batch_id=milk_batch_id,
            quantity=0.25,
            unit=MeasurementUnit.LITER,
        ),
        InventoryLedgerEntryModel(
            id=seed_id("ledger-user-milk-initial"),
            user_id=user_id,
            inventory_batch_id=milk_batch_id,
            event_type=InventoryLedgerEventType.INITIAL_STOCK,
            quantity_before=0.0,
            quantity_delta=2.0,
            quantity_after=2.0,
            unit=MeasurementUnit.LITER,
            idempotency_key="seed-batch-user-milk",
        ),
        InventoryLedgerEntryModel(
            id=seed_id("ledger-user-milk-consumption"),
            user_id=user_id,
            inventory_batch_id=milk_batch_id,
            event_type=InventoryLedgerEventType.COOKING_CONSUMPTION,
            quantity_before=2.0,
            quantity_delta=-0.5,
            quantity_after=1.5,
            unit=MeasurementUnit.LITER,
            cooking_session_id=seed_id("cooking-session-user-milk"),
            idempotency_key="seed-cooking-user-milk",
        ),
        InventoryLedgerEntryModel(
            id=seed_id("ledger-user-chicken-initial"),
            user_id=user_id,
            inventory_batch_id=chicken_batch_id,
            event_type=InventoryLedgerEventType.INITIAL_STOCK,
            quantity_before=0.0,
            quantity_delta=1.0,
            quantity_after=1.0,
            unit=MeasurementUnit.KG,
            idempotency_key="seed-batch-user-chicken",
        ),
        InventoryLedgerEntryModel(
            id=seed_id("ledger-user-leftover-created"),
            user_id=user_id,
            inventory_batch_id=leftover_batch_id,
            event_type=InventoryLedgerEventType.LEFTOVER_CREATED,
            quantity_before=0.0,
            quantity_delta=1.0,
            quantity_after=1.0,
            unit=MeasurementUnit.PACK,
            cooking_session_id=seed_id("cooking-session-user-milk"),
            idempotency_key="seed-leftover-user-milk",
        ),
        ShoppingListModel(
            id=seed_id("shopping-list-user"),
            user_id=user_id,
            meal_plan_id=user_plan_id,
            status=ShoppingListStatus.ACTIVE,
            generated_at=now,
        ),
        ShoppingListModel(
            id=seed_id("shopping-list-admin"),
            user_id=admin_id,
            meal_plan_id=admin_plan_id,
            status=ShoppingListStatus.ACTIVE,
            generated_at=now,
        ),
        ShoppingListItemModel(
            id=seed_id("shopping-item-user-spinach"),
            shopping_list_id=seed_id("shopping-list-user"),
            master_ingredient_id=seed_id("ingredient-spinach"),
            required_quantity=200.0,
            available_quantity=0.0,
            missing_quantity=200.0,
            unit=MeasurementUnit.GRAM,
            estimated_cost=18000.0,
            is_checked=False,
            source_metadata={"recipe_ids": ["recipe-spinach-soup"]},
        ),
        ShoppingListItemModel(
            id=seed_id("shopping-item-user-salt"),
            shopping_list_id=seed_id("shopping-list-user"),
            custom_name="Salt",
            required_quantity=1.0,
            available_quantity=0.0,
            missing_quantity=1.0,
            unit=MeasurementUnit.PACK,
            estimated_cost=10000.0,
            is_checked=True,
            source_metadata={"source": "manual"},
        ),
        ShoppingListItemModel(
            id=seed_id("shopping-item-admin-chicken"),
            shopping_list_id=seed_id("shopping-list-admin"),
            master_ingredient_id=seed_id("ingredient-chicken-breast"),
            required_quantity=300.0,
            available_quantity=0.0,
            missing_quantity=300.0,
            unit=MeasurementUnit.GRAM,
            estimated_cost=30000.0,
            is_checked=False,
            source_metadata={"recipe_ids": ["recipe-grilled-chicken"]},
        ),
        ShoppingListItemModel(
            id=seed_id("shopping-item-admin-milk"),
            shopping_list_id=seed_id("shopping-list-admin"),
            master_ingredient_id=seed_id("ingredient-fresh-milk"),
            required_quantity=500.0,
            available_quantity=0.0,
            missing_quantity=500.0,
            unit=MeasurementUnit.ML,
            estimated_cost=18000.0,
            is_checked=False,
            source_metadata={"recipe_ids": ["recipe-milk-smoothie"]},
        ),
        FavoriteRecipeModel(
            id=seed_id("favorite-user-chicken"),
            user_id=user_id,
            recipe_id=seed_id("recipe-grilled-chicken"),
        ),
        FavoriteRecipeModel(
            id=seed_id("favorite-admin-rice"),
            user_id=admin_id,
            recipe_id=seed_id("recipe-steamed-rice"),
        ),
        FavoriteMenuModel(
            id=seed_id("favorite-menu-user"),
            user_id=user_id,
            name="Cloudian quick meals",
            description="Fast recipes for the main test user.",
        ),
        FavoriteMenuModel(
            id=seed_id("favorite-menu-admin"),
            user_id=admin_id,
            name="Admin staples",
            description="Baseline catalog recipes.",
        ),
        FavoriteMenuItemModel(
            id=seed_id("favorite-menu-item-user-milk"),
            favorite_menu_id=seed_id("favorite-menu-user"),
            recipe_id=seed_id("recipe-milk-smoothie"),
        ),
        FavoriteMenuItemModel(
            id=seed_id("favorite-menu-item-user-chicken"),
            favorite_menu_id=seed_id("favorite-menu-user"),
            recipe_id=seed_id("recipe-grilled-chicken"),
        ),
        FavoriteMenuItemModel(
            id=seed_id("favorite-menu-item-admin-rice"),
            favorite_menu_id=seed_id("favorite-menu-admin"),
            recipe_id=seed_id("recipe-steamed-rice"),
        ),
        FavoriteMenuItemModel(
            id=seed_id("favorite-menu-item-admin-spinach"),
            favorite_menu_id=seed_id("favorite-menu-admin"),
            recipe_id=seed_id("recipe-spinach-soup"),
        ),
        DeviceRegistrationModel(
            id=seed_id("device-user"),
            user_id=user_id,
            fcm_token_hash=token_hash("seed-fcm-token-user"),
            encrypted_fcm_token="seed-encrypted-fcm-token-user",
            platform=DevicePlatform.ANDROID,
            is_enabled=True,
            last_seen_at=now,
        ),
        DeviceRegistrationModel(
            id=seed_id("device-admin"),
            user_id=admin_id,
            fcm_token_hash=token_hash("seed-fcm-token-admin"),
            encrypted_fcm_token="seed-encrypted-fcm-token-admin",
            platform=DevicePlatform.WEB,
            is_enabled=True,
            last_seen_at=now,
        ),
        UserNotificationPreferenceModel(
            id=seed_id("notification-preference-user"),
            user_id=user_id,
            warning_days=2,
            expiring_soon_enabled=True,
            expires_today_enabled=True,
            expired_enabled=True,
            leftover_reminder_enabled=True,
        ),
        UserNotificationPreferenceModel(
            id=seed_id("notification-preference-admin"),
            user_id=admin_id,
            warning_days=3,
            expiring_soon_enabled=True,
            expires_today_enabled=True,
            expired_enabled=False,
            leftover_reminder_enabled=True,
        ),
        NotificationModel(
            id=seed_id("notification-user-milk-expiring"),
            user_id=user_id,
            inventory_batch_id=milk_batch_id,
            type=NotificationType.EXPIRING_SOON,
            title="Milk expires soon",
            body="Fresh milk expires tomorrow.",
            payload={"batch_id": "batch-user-milk"},
            deduplication_key=f"{milk_batch_id}:EXPIRING_SOON:{today.isoformat()}",
            status=NotificationStatus.UNREAD,
            delivery_status=NotificationDeliveryStatus.SENT,
            scheduled_at=now,
            sent_at=now,
            retry_count=0,
        ),
        NotificationModel(
            id=seed_id("notification-user-leftover"),
            user_id=user_id,
            inventory_batch_id=leftover_batch_id,
            type=NotificationType.LEFTOVER_REMINDER,
            title="Use your leftover smoothie",
            body="The cooked-food batch is due tomorrow.",
            payload={"batch_id": "batch-user-leftover"},
            deduplication_key=f"{leftover_batch_id}:LEFTOVER_REMINDER:{today.isoformat()}",
            status=NotificationStatus.READ,
            delivery_status=NotificationDeliveryStatus.SENT,
            scheduled_at=now,
            sent_at=now,
            retry_count=0,
        ),
        NotificationModel(
            id=seed_id("notification-user-chicken-expiring"),
            user_id=user_id,
            inventory_batch_id=chicken_batch_id,
            type=NotificationType.EXPIRING_SOON,
            title="Chicken should be cooked soon",
            body="Chicken breast is within the configured warning window.",
            payload={"batch_id": "batch-user-chicken"},
            deduplication_key=f"{chicken_batch_id}:EXPIRING_SOON:{today.isoformat()}",
            status=NotificationStatus.DISMISSED,
            delivery_status=NotificationDeliveryStatus.RETRYING,
            scheduled_at=now,
            retry_count=1,
        ),
        NotificationModel(
            id=seed_id("notification-admin-rice"),
            user_id=admin_id,
            type=NotificationType.EXPIRES_TODAY,
            title="Admin notification sample",
            body="This record tests a notification without a batch link.",
            payload={"source": "seed"},
            deduplication_key=f"admin:EXPIRES_TODAY:{today.isoformat()}",
            status=NotificationStatus.UNREAD,
            delivery_status=NotificationDeliveryStatus.PENDING,
            scheduled_at=now,
            retry_count=0,
        ),
    ]


async def seed_database() -> tuple[int, int]:
    """Write every demo record in one transaction after schema validation."""
    ensure_local_environment()
    demo_password_hash = hashing(load_demo_password())
    now = datetime.now(UTC)
    engine = create_async_engine(
        build_async_database_url(DATABASE_URL), pool_pre_ping=True
    )
    session_factory = async_sessionmaker(engine, expire_on_commit=False)

    try:
        await assert_complete_schema(engine)
        async with session_factory() as session, session.begin():
            await merge_records(session, build_user_records(demo_password_hash, now))
            await merge_records(session, build_session_records(now))
            await merge_records(session, build_catalog_records())
            await merge_records(session, build_planning_records(now.date(), now))
            await merge_records(session, build_inventory_records(now))
            await merge_records(session, build_activity_records(now.date(), now))
    finally:
        await engine.dispose()

    return len(REQUIRED_TABLES), 73


def main() -> None:
    """Run the local seed command and print its safe completion summary."""
    table_count, record_count = asyncio.run(seed_database())
    print(
        f"Seeded {record_count} deterministic records across {table_count} tables.",
    )


if __name__ == "__main__":
    main()
