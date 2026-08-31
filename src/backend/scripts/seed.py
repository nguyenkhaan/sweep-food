"""Seed the minimal catalog bootstrap dataset with transactional natural-key upserts."""

from __future__ import annotations

import argparse
import asyncio
import os
from collections.abc import Callable, Iterable, Mapping
from dataclasses import dataclass, field
from datetime import UTC, datetime
from decimal import Decimal
from typing import TypeVar, cast
from uuid import UUID

from sqlalchemy import Select, func, select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from src.db import build_async_database_url
from src.helper.pwd_hash import compare_hash, hashing
from src.model.enum_model import (
    AccountStatus,
    MeasurementUnit,
    ShelfLifeRuleScope,
    StorageMode,
    UserRole,
)
from src.model.ingredient_alias_model import IngredientAliasModel
from src.model.ingredient_category_model import IngredientCategoryModel
from src.model.master_ingredient_model import MasterIngredientModel
from src.model.recipe_ingredient_model import RecipeIngredientModel
from src.model.recipe_model import RecipeModel
from src.model.shelf_life_rule_model import ShelfLifeRuleModel
from src.model.user_model import UserModel

NameModel = TypeVar("NameModel", IngredientCategoryModel, RecipeModel)


@dataclass(frozen=True)
class AdminSeedConfig:
    """Environment-provided identity for the single bootstrap administrator."""

    name: str
    phone_e164: str
    email: str
    password: str


@dataclass(frozen=True)
class CategorySeed:
    """Natural-keyed category input."""

    key: str
    name: str
    description: str | None


@dataclass(frozen=True)
class NutritionSeed:
    """Approved catalog nutrition values shared by ingredients and recipes."""

    calories: Decimal | None = None
    protein_g: Decimal | None = None
    fat_g: Decimal | None = None
    carbs_g: Decimal | None = None
    sugar_g: Decimal | None = None
    sodium_mg: Decimal | None = None
    other_nutrients: dict[str, object] = field(default_factory=dict)


@dataclass(frozen=True)
class IngredientSeed:
    """Natural-keyed master ingredient input."""

    key: str
    category_key: str
    name: str
    description: str
    canonical_unit: MeasurementUnit
    default_storage_mode: StorageMode | None
    nutrition: NutritionSeed = field(default_factory=NutritionSeed)


@dataclass(frozen=True)
class AliasSeed:
    """Natural-keyed alias input."""

    normalized_alias: str
    alias: str
    ingredient_key: str


@dataclass(frozen=True)
class ShelfLifeRuleSeed:
    """One category- or ingredient-scoped shelf-life input."""

    scope: ShelfLifeRuleScope
    target_key: str
    storage_mode: StorageMode
    min_days: int
    max_days: int
    default_days: int


@dataclass(frozen=True)
class RecipeDetailsSeed:
    """Non-key recipe values kept together for one deterministic upsert."""

    description: str
    instructions: dict[str, object]
    default_servings: Decimal
    estimated_cooking_minutes: int
    estimated_cost: float | None
    nutrition: NutritionSeed = field(default_factory=NutritionSeed)
    tags: dict[str, object] = field(default_factory=dict)


@dataclass(frozen=True)
class RecipeSeed:
    """Natural-keyed recipe input."""

    key: str
    name: str
    details: RecipeDetailsSeed


@dataclass(frozen=True)
class RecipeIngredientSeed:
    """Natural-keyed recipe ingredient input."""

    recipe_key: str
    ingredient_key: str
    required_quantity: Decimal
    unit: MeasurementUnit
    is_optional: bool = False
    preparation_note: str | None = None


@dataclass(frozen=True)
class SeedDataset:
    """The catalog release unit applied atomically by this seed entry point."""

    categories: tuple[CategorySeed, ...]
    ingredients: tuple[IngredientSeed, ...]
    aliases: tuple[AliasSeed, ...]
    shelf_life_rules: tuple[ShelfLifeRuleSeed, ...]
    recipes: tuple[RecipeSeed, ...]
    recipe_ingredients: tuple[RecipeIngredientSeed, ...]


@dataclass
class SeedReport:
    """Classified outcomes for a seed validation or application run."""

    created: list[str] = field(default_factory=list)
    updated: list[str] = field(default_factory=list)
    unchanged: list[str] = field(default_factory=list)
    rejected: list[str] = field(default_factory=list)

    def add(self, outcome: str, record: str) -> None:
        """Add one classified record outcome."""
        getattr(self, outcome).append(record)

    def summary(self) -> str:
        """Return a secret-free report summary suitable for command output."""
        return (
            f"created={len(self.created)} updated={len(self.updated)} "
            f"unchanged={len(self.unchanged)} rejected={len(self.rejected)}"
        )


@dataclass(frozen=True)
class SeedRunContext:
    """Mutable-operation context shared by all ordered natural-key upserts."""

    session: AsyncSession
    report: SeedReport
    dry_run: bool


class SeedValidationError(ValueError):
    """Expose all rejected seed records without revealing secrets."""

    def __init__(self, report: SeedReport) -> None:
        self.report = report
        details = "; ".join(report.rejected)
        super().__init__(f"Seed validation failed: {details}")


DEFAULT_DATASET = SeedDataset(
    categories=(
        CategorySeed(
            key="leafy-greens",
            name="Leafy greens",
            description="Fresh leafy vegetables.",
        ),
    ),
    ingredients=(
        IngredientSeed(
            key="spinach",
            category_key="leafy-greens",
            name="Spinach",
            description="Fresh leafy spinach.",
            canonical_unit=MeasurementUnit.GRAM,
            default_storage_mode=StorageMode.REFRIGERATED,
            nutrition=NutritionSeed(
                calories=Decimal("23.000"),
                protein_g=Decimal("2.900"),
                fat_g=Decimal("0.400"),
                carbs_g=Decimal("3.600"),
                sugar_g=Decimal("0.400"),
                sodium_mg=Decimal("79.000"),
                other_nutrients={"fiber_g": 2.2},
            ),
        ),
    ),
    aliases=(
        AliasSeed(
            normalized_alias="baby spinach",
            alias="Baby spinach",
            ingredient_key="spinach",
        ),
    ),
    shelf_life_rules=(
        ShelfLifeRuleSeed(
            scope=ShelfLifeRuleScope.CATEGORY,
            target_key="leafy-greens",
            storage_mode=StorageMode.REFRIGERATED,
            min_days=3,
            max_days=5,
            default_days=4,
        ),
        ShelfLifeRuleSeed(
            scope=ShelfLifeRuleScope.INGREDIENT,
            target_key="spinach",
            storage_mode=StorageMode.REFRIGERATED,
            min_days=2,
            max_days=4,
            default_days=3,
        ),
    ),
    recipes=(
        RecipeSeed(
            key="spinach-soup",
            name="Spinach soup",
            details=RecipeDetailsSeed(
                description="A small bootstrap recipe using fresh spinach.",
                instructions={"steps": ["Wash spinach", "Cook for five minutes"]},
                default_servings=Decimal("2.00"),
                estimated_cooking_minutes=15,
                estimated_cost=25000.0,
                nutrition=NutritionSeed(
                    calories=Decimal("46.000"),
                    protein_g=Decimal("5.800"),
                    fat_g=Decimal("0.800"),
                    carbs_g=Decimal("7.200"),
                    sugar_g=Decimal("0.800"),
                    other_nutrients={"fiber_g": 4.4},
                ),
                tags={"values": ["quick", "vegetarian"]},
            ),
        ),
    ),
    recipe_ingredients=(
        RecipeIngredientSeed(
            recipe_key="spinach-soup",
            ingredient_key="spinach",
            required_quantity=Decimal("200.000"),
            unit=MeasurementUnit.GRAM,
        ),
    ),
)


def load_admin_seed_config(environ: dict[str, str] | None = None) -> AdminSeedConfig:
    """Read all administrator identity values from the process environment."""
    values = os.environ if environ is None else environ
    missing = [
        name
        for name in (
            "SEED_ADMIN_NAME",
            "SEED_ADMIN_PHONE_E164",
            "SEED_ADMIN_EMAIL",
            "SEED_ADMIN_PASSWORD",
        )
        if not values.get(name)
    ]
    if missing:
        raise ValueError(f"Missing required seed configuration: {', '.join(missing)}")
    return AdminSeedConfig(
        name=values["SEED_ADMIN_NAME"],
        phone_e164=values["SEED_ADMIN_PHONE_E164"],
        email=values["SEED_ADMIN_EMAIL"],
        password=values["SEED_ADMIN_PASSWORD"],
    )


def validate_seed_input(dataset: SeedDataset, config: AdminSeedConfig) -> SeedReport:
    """Validate all references and values before an application transaction writes."""
    report = SeedReport()
    _validate_admin(config, report)
    _validate_unique_keys("category", (item.key for item in dataset.categories), report)
    _validate_unique_keys(
        "ingredient", (item.key for item in dataset.ingredients), report
    )
    _validate_unique_keys("recipe", (item.key for item in dataset.recipes), report)
    category_keys = {item.key for item in dataset.categories}
    ingredient_keys = {item.key for item in dataset.ingredients}
    recipe_keys = {item.key for item in dataset.recipes}

    _validate_ingredients(dataset.ingredients, category_keys, report)

    _validate_aliases(dataset.aliases, ingredient_keys, report)

    _validate_shelf_life_rules(
        dataset.shelf_life_rules,
        category_keys,
        ingredient_keys,
        report,
    )

    _validate_recipes(dataset.recipes, report)

    _validate_recipe_ingredients(
        dataset.recipe_ingredients,
        recipe_keys,
        ingredient_keys,
        report,
    )

    if report.rejected:
        raise SeedValidationError(report)
    return report


def _validate_ingredients(
    records: tuple[IngredientSeed, ...],
    category_keys: set[str],
    report: SeedReport,
) -> None:
    """Validate master ingredient references, units, storage, and nutrition."""
    for ingredient in records:
        if ingredient.category_key not in category_keys:
            report.add(
                "rejected",
                f"ingredient:{ingredient.key} references category:{ingredient.category_key}",
            )
        if not isinstance(ingredient.canonical_unit, MeasurementUnit):
            report.add(
                "rejected", f"ingredient:{ingredient.key} has invalid canonical unit"
            )
        if ingredient.default_storage_mode is not None and not isinstance(
            ingredient.default_storage_mode,
            StorageMode,
        ):
            report.add(
                "rejected", f"ingredient:{ingredient.key} has invalid storage mode"
            )
        _validate_nutrition(ingredient.key, _ingredient_nutrition(ingredient), report)


def _validate_aliases(
    records: tuple[AliasSeed, ...],
    ingredient_keys: set[str],
    report: SeedReport,
) -> None:
    """Validate unique aliases and their master ingredient references."""
    aliases: set[str] = set()
    for alias in records:
        if alias.normalized_alias in aliases:
            report.add("rejected", f"alias:{alias.normalized_alias} is duplicated")
        aliases.add(alias.normalized_alias)
        if alias.ingredient_key not in ingredient_keys:
            report.add(
                "rejected",
                f"alias:{alias.normalized_alias} references ingredient:{alias.ingredient_key}",
            )


def _validate_shelf_life_rules(
    records: tuple[ShelfLifeRuleSeed, ...],
    category_keys: set[str],
    ingredient_keys: set[str],
    report: SeedReport,
) -> None:
    """Validate rule target scope, storage mode, and allowed day range."""
    for rule in records:
        _validate_rule_target(rule, category_keys, ingredient_keys, report)
        if not isinstance(rule.storage_mode, StorageMode):
            report.add(
                "rejected", f"shelf-life:{rule.target_key} has invalid storage mode"
            )
        _validate_rule_days(rule, report)


def _validate_rule_target(
    rule: ShelfLifeRuleSeed,
    category_keys: set[str],
    ingredient_keys: set[str],
    report: SeedReport,
) -> None:
    """Validate the one target permitted by the shelf-life rule's scope."""
    if not isinstance(rule.scope, ShelfLifeRuleScope):
        report.add("rejected", f"shelf-life:{rule.target_key} has invalid scope")
        return
    target_keys = (
        ingredient_keys
        if rule.scope is ShelfLifeRuleScope.INGREDIENT
        else category_keys
    )
    if rule.target_key not in target_keys:
        report.add("rejected", f"shelf-life:{rule.target_key} has an unknown target")


def _validate_rule_days(rule: ShelfLifeRuleSeed, report: SeedReport) -> None:
    """Validate non-negative ordered shelf-life day values."""
    days = (rule.min_days, rule.max_days, rule.default_days)
    if not all(isinstance(day, int) for day in days) or (
        min(days) < 0
        or rule.max_days < rule.min_days
        or not rule.min_days <= rule.default_days <= rule.max_days
    ):
        report.add("rejected", f"shelf-life:{rule.target_key} has an invalid day range")


def _validate_recipes(records: tuple[RecipeSeed, ...], report: SeedReport) -> None:
    """Validate positive serving values and approved nutrition values."""
    for recipe in records:
        if not _is_valid_positive_numeric(recipe.details.default_servings, 6, 2):
            report.add(
                "rejected", f"recipe:{recipe.key} has non-positive default servings"
            )
        _validate_nutrition(recipe.key, _recipe_nutrition(recipe), report)


def _validate_recipe_ingredients(
    records: tuple[RecipeIngredientSeed, ...],
    recipe_keys: set[str],
    ingredient_keys: set[str],
    report: SeedReport,
) -> None:
    """Validate natural keys, references, units, and positive recipe quantities."""
    natural_keys: set[tuple[str, str, str | None]] = set()
    for record in records:
        natural_key = (
            record.recipe_key,
            record.ingredient_key,
            record.preparation_note,
        )
        if natural_key in natural_keys:
            report.add(
                "rejected",
                f"recipe-ingredient:{record.recipe_key}/{record.ingredient_key} is duplicated",
            )
        natural_keys.add(natural_key)
        _validate_recipe_ingredient_record(record, recipe_keys, ingredient_keys, report)


def _validate_recipe_ingredient_record(
    record: RecipeIngredientSeed,
    recipe_keys: set[str],
    ingredient_keys: set[str],
    report: SeedReport,
) -> None:
    """Validate one recipe ingredient's dependency and quantity values."""
    if record.recipe_key not in recipe_keys:
        report.add(
            "rejected", f"recipe-ingredient references recipe:{record.recipe_key}"
        )
    if record.ingredient_key not in ingredient_keys:
        report.add(
            "rejected",
            f"recipe-ingredient references ingredient:{record.ingredient_key}",
        )
    if not isinstance(record.unit, MeasurementUnit):
        report.add(
            "rejected", f"recipe-ingredient:{record.recipe_key} has invalid unit"
        )
    if not _is_valid_positive_numeric(record.required_quantity, 12, 3):
        report.add(
            "rejected",
            "recipe-ingredient:"
            f"{record.recipe_key}/{record.ingredient_key} has non-positive quantity",
        )


async def seed_dataset(
    session: AsyncSession,
    config: AdminSeedConfig,
    dataset: SeedDataset = DEFAULT_DATASET,
    *,
    dry_run: bool = False,
) -> SeedReport:
    """Validate and apply one release dataset inside the caller's transaction."""
    validate_seed_input(dataset, config)
    report = SeedReport()
    context = SeedRunContext(session=session, report=report, dry_run=dry_run)
    async with session.begin_nested():
        await _upsert_admin(context, config)
        categories = await _upsert_categories(context, dataset.categories)
        ingredients = await _upsert_ingredients(
            context, dataset.ingredients, categories
        )
        await _upsert_aliases(context, dataset.aliases, ingredients)
        await _upsert_shelf_life_rules(
            context,
            dataset.shelf_life_rules,
            categories,
            ingredients,
        )
        recipes = await _upsert_recipes(context, dataset.recipes)
        await _upsert_recipe_ingredients(
            context,
            dataset.recipe_ingredients,
            recipes,
            ingredients,
        )
    return report


async def seed_database(
    database_url: str,
    config: AdminSeedConfig,
    dataset: SeedDataset = DEFAULT_DATASET,
    *,
    dry_run: bool = False,
) -> SeedReport:
    """Apply one complete seed release in one transaction and dispose its engine."""
    engine = create_async_engine(
        build_async_database_url(database_url), pool_pre_ping=True
    )
    session_factory = async_sessionmaker(engine, expire_on_commit=False)
    try:
        async with session_factory() as session, session.begin():
            return await seed_dataset(session, config, dataset, dry_run=dry_run)
    finally:
        await engine.dispose()


def _validate_admin(config: AdminSeedConfig, report: SeedReport) -> None:
    """Validate non-secret administrator identity fields."""
    if not config.name.strip():
        report.add("rejected", "admin has an empty name")
    if not config.phone_e164.startswith("+") or not config.phone_e164[1:].isdigit():
        report.add("rejected", "admin has an invalid E.164 phone")
    if "@" not in config.email or not config.email.strip():
        report.add("rejected", "admin has an invalid email")
    if not config.password:
        report.add("rejected", "admin password is missing")


def _validate_unique_keys(
    record_type: str,
    keys: Iterable[str],
    report: SeedReport,
) -> None:
    """Reject duplicate source keys before resolving references."""
    observed: set[str] = set()
    for key in keys:
        if not key or key in observed:
            report.add(
                "rejected", f"{record_type}:{key or '<empty>'} is duplicated or empty"
            )
        observed.add(key)


def _validate_nutrition(
    record_key: str,
    values: Iterable[Decimal | None],
    report: SeedReport,
) -> None:
    """Reject nutrition values that cannot use the approved Numeric policy."""
    for value in values:
        if value is not None and not _is_valid_numeric(value, 12, 3):
            report.add("rejected", f"record:{record_key} has invalid nutrition")
            return


def _is_valid_positive_numeric(value: object, precision: int, scale: int) -> bool:
    """Return whether a Numeric value is finite, in-range, and strictly positive."""
    return (
        isinstance(value, Decimal)
        and value > 0
        and _is_valid_numeric(value, precision, scale)
    )


def _is_valid_numeric(value: object, precision: int, scale: int) -> bool:
    """Return whether a Decimal fits PostgreSQL NUMERIC precision and scale exactly."""
    if not isinstance(value, Decimal) or not value.is_finite():
        return False
    exponent = cast(int, value.as_tuple().exponent)
    fractional_digits = max(-exponent, 0)
    upper_bound = Decimal(10) ** (precision - scale)
    return fractional_digits <= scale and abs(value) < upper_bound


def _ingredient_nutrition(item: IngredientSeed) -> tuple[Decimal | None, ...]:
    """Return the numeric nutrition fields from one master ingredient."""
    return (
        item.nutrition.calories,
        item.nutrition.protein_g,
        item.nutrition.fat_g,
        item.nutrition.carbs_g,
        item.nutrition.sugar_g,
        item.nutrition.sodium_mg,
    )


def _recipe_nutrition(item: RecipeSeed) -> tuple[Decimal | None, ...]:
    """Return the numeric nutrition fields from one recipe."""
    return (
        item.details.nutrition.calories,
        item.details.nutrition.protein_g,
        item.details.nutrition.fat_g,
        item.details.nutrition.carbs_g,
        item.details.nutrition.sugar_g,
    )


async def _upsert_admin(
    context: SeedRunContext,
    config: AdminSeedConfig,
) -> None:
    """Upsert the administrator by its environment-provided phone identity."""
    existing = await context.session.scalar(
        select(UserModel).where(UserModel.phone_e164 == config.phone_e164),
    )
    label = "admin"
    if existing is None:
        context.report.add("created", label)
        if not context.dry_run:
            context.session.add(
                UserModel(
                    name=config.name,
                    phone_e164=config.phone_e164,
                    phone_verified_at=datetime.now(UTC),
                    email=config.email,
                    email_verified_at=datetime.now(UTC),
                    password_hash=hashing(config.password),
                    role=UserRole.ADMIN,
                    status=AccountStatus.ACTIVE,
                    preferences={},
                ),
            )
            await context.session.flush()
        return

    values_changed = any(
        (
            existing.name != config.name,
            existing.email != config.email,
            existing.role is not UserRole.ADMIN,
            existing.status is not AccountStatus.ACTIVE,
            existing.phone_verified_at is None,
            existing.email_verified_at is None,
            not compare_hash(config.password, existing.password_hash),
        ),
    )
    context.report.add("updated" if values_changed else "unchanged", label)
    if values_changed and not context.dry_run:
        existing.name = config.name
        existing.email = config.email
        existing.phone_verified_at = existing.phone_verified_at or datetime.now(UTC)
        existing.email_verified_at = existing.email_verified_at or datetime.now(UTC)
        existing.role = UserRole.ADMIN
        existing.status = AccountStatus.ACTIVE
        if not compare_hash(config.password, existing.password_hash):
            existing.password_hash = hashing(config.password)
        await context.session.flush()


async def _upsert_categories(
    context: SeedRunContext,
    records: tuple[CategorySeed, ...],
) -> dict[str, IngredientCategoryModel | None]:
    """Upsert categories by case-insensitive name and return source-key mappings."""
    result: dict[str, IngredientCategoryModel | None] = {}
    for item in records:
        existing = await context.session.scalar(
            _lower_name_query(IngredientCategoryModel, item.name)
        )
        label = f"category:{item.key}"
        values_changed = existing is not None and (
            existing.name != item.name or existing.description != item.description
        )
        if existing is None:
            context.report.add("created", label)
            if not context.dry_run:
                existing = IngredientCategoryModel(
                    name=item.name,
                    description=item.description,
                )
                context.session.add(existing)
                await context.session.flush()
        else:
            context.report.add("updated" if values_changed else "unchanged", label)
            if values_changed and not context.dry_run:
                existing.name = item.name
                existing.description = item.description
                await context.session.flush()
        result[item.key] = existing
    return result


async def _upsert_ingredients(
    context: SeedRunContext,
    records: tuple[IngredientSeed, ...],
    categories: dict[str, IngredientCategoryModel | None],
) -> dict[str, MasterIngredientModel | None]:
    """Upsert master ingredients by category and case-insensitive name."""
    result: dict[str, MasterIngredientModel | None] = {}
    for item in records:
        category = categories[item.category_key]
        existing = (
            None
            if category is None
            else await context.session.scalar(
                select(MasterIngredientModel).where(
                    MasterIngredientModel.category_id == category.id,
                    func.lower(MasterIngredientModel.name) == item.name.casefold(),
                ),
            )
        )
        label = f"ingredient:{item.key}"
        values = _ingredient_values(item, category.id if category is not None else None)
        if existing is None:
            context.report.add("created", label)
            if not context.dry_run:
                existing = MasterIngredientModel(**values)
                context.session.add(existing)
                await context.session.flush()
        else:
            changed = _has_changes(existing, values)
            context.report.add("updated" if changed else "unchanged", label)
            if changed and not context.dry_run:
                _assign(existing, values)
                await context.session.flush()
        result[item.key] = existing
    return result


async def _upsert_aliases(
    context: SeedRunContext,
    records: tuple[AliasSeed, ...],
    ingredients: dict[str, MasterIngredientModel | None],
) -> None:
    """Upsert aliases by their globally unique normalized text."""
    for item in records:
        ingredient = ingredients[item.ingredient_key]
        existing = await context.session.scalar(
            select(IngredientAliasModel).where(
                IngredientAliasModel.normalized_alias == item.normalized_alias,
            ),
        )
        values = {
            "alias": item.alias,
            "normalized_alias": item.normalized_alias,
            "master_ingredient_id": ingredient.id if ingredient is not None else None,
        }
        await _record_upsert(
            context,
            existing,
            IngredientAliasModel,
            values,
            f"alias:{item.normalized_alias}",
        )


async def _upsert_shelf_life_rules(
    context: SeedRunContext,
    records: tuple[ShelfLifeRuleSeed, ...],
    categories: dict[str, IngredientCategoryModel | None],
    ingredients: dict[str, MasterIngredientModel | None],
) -> None:
    """Upsert shelf-life rules by target and storage-mode natural key."""
    for item in records:
        ingredient = ingredients.get(item.target_key)
        category = categories.get(item.target_key)
        if item.scope is ShelfLifeRuleScope.INGREDIENT:
            existing = (
                None
                if ingredient is None
                else await context.session.scalar(
                    select(ShelfLifeRuleModel).where(
                        ShelfLifeRuleModel.master_ingredient_id == ingredient.id,
                        ShelfLifeRuleModel.storage_mode == item.storage_mode,
                    ),
                )
            )
        else:
            existing = (
                None
                if category is None
                else await context.session.scalar(
                    select(ShelfLifeRuleModel).where(
                        ShelfLifeRuleModel.category_id == category.id,
                        ShelfLifeRuleModel.storage_mode == item.storage_mode,
                    ),
                )
            )
        values = {
            "scope": item.scope,
            "master_ingredient_id": ingredient.id if ingredient is not None else None,
            "category_id": category.id if category is not None else None,
            "storage_mode": item.storage_mode,
            "min_days": item.min_days,
            "max_days": item.max_days,
            "default_days": item.default_days,
        }
        await _record_upsert(
            context,
            existing,
            ShelfLifeRuleModel,
            values,
            f"shelf-life:{item.scope.value}:{item.target_key}:{item.storage_mode.value}",
        )


async def _upsert_recipes(
    context: SeedRunContext,
    records: tuple[RecipeSeed, ...],
) -> dict[str, RecipeModel | None]:
    """Upsert recipes by their case-insensitive names."""
    result: dict[str, RecipeModel | None] = {}
    for item in records:
        existing = await context.session.scalar(
            _lower_name_query(RecipeModel, item.name)
        )
        values = _recipe_values(item)
        await _record_upsert(
            context,
            existing,
            RecipeModel,
            values,
            f"recipe:{item.key}",
        )
        if existing is None and not context.dry_run:
            existing = await context.session.scalar(
                _lower_name_query(RecipeModel, item.name)
            )
        result[item.key] = existing
    return result


async def _upsert_recipe_ingredients(
    context: SeedRunContext,
    records: tuple[RecipeIngredientSeed, ...],
    recipes: dict[str, RecipeModel | None],
    ingredients: dict[str, MasterIngredientModel | None],
) -> None:
    """Upsert recipe ingredients by recipe, ingredient, and preparation note."""
    for item in records:
        recipe = recipes[item.recipe_key]
        ingredient = ingredients[item.ingredient_key]
        existing = None
        if recipe is not None and ingredient is not None:
            statement: Select[tuple[RecipeIngredientModel]] = select(
                RecipeIngredientModel
            ).where(
                RecipeIngredientModel.recipe_id == recipe.id,
                RecipeIngredientModel.master_ingredient_id == ingredient.id,
                RecipeIngredientModel.preparation_note == item.preparation_note,
            )
            existing = await context.session.scalar(statement)
        values = {
            "recipe_id": recipe.id if recipe is not None else None,
            "master_ingredient_id": ingredient.id if ingredient is not None else None,
            "required_quantity": item.required_quantity,
            "unit": item.unit,
            "is_optional": item.is_optional,
            "preparation_note": item.preparation_note,
        }
        await _record_upsert(
            context,
            existing,
            RecipeIngredientModel,
            values,
            f"recipe-ingredient:{item.recipe_key}/{item.ingredient_key}",
        )


async def _record_upsert(
    context: SeedRunContext,
    existing: object | None,
    model_type: Callable[..., object],
    values: Mapping[str, object],
    label: str,
) -> None:
    """Classify and, unless dry-run, persist one natural-keyed model row."""
    if existing is None:
        context.report.add("created", label)
        if not context.dry_run:
            context.session.add(model_type(**values))
            await context.session.flush()
        return
    changed = _has_changes(existing, values)
    context.report.add("updated" if changed else "unchanged", label)
    if changed and not context.dry_run:
        _assign(existing, values)
        await context.session.flush()


def _lower_name_query(
    model_type: type[NameModel],
    name: str,
) -> Select[tuple[NameModel]]:
    """Build the shared lower(name) natural-key lookup for catalog rows."""
    return select(model_type).where(func.lower(model_type.name) == name.casefold())


def _ingredient_values(
    item: IngredientSeed,
    category_id: UUID | None,
) -> dict[str, object]:
    """Map one ingredient seed into mutable ORM fields."""
    return {
        "name": item.name,
        "description": item.description,
        "category_id": category_id,
        "canonical_unit": item.canonical_unit,
        "default_storage_mode": item.default_storage_mode,
        "calories": item.nutrition.calories,
        "protein_g": item.nutrition.protein_g,
        "fat_g": item.nutrition.fat_g,
        "carbs_g": item.nutrition.carbs_g,
        "sugar_g": item.nutrition.sugar_g,
        "sodium_mg": item.nutrition.sodium_mg,
        "other_nutrients": item.nutrition.other_nutrients,
    }


def _recipe_values(item: RecipeSeed) -> dict[str, object]:
    """Map one recipe seed into mutable ORM fields."""
    return {
        "name": item.name,
        "description": item.details.description,
        "instructions": item.details.instructions,
        "default_servings": item.details.default_servings,
        "estimated_cooking_minutes": item.details.estimated_cooking_minutes,
        "estimated_cost": item.details.estimated_cost,
        "total_calories": item.details.nutrition.calories,
        "total_protein_g": item.details.nutrition.protein_g,
        "total_fat_g": item.details.nutrition.fat_g,
        "total_carbs_g": item.details.nutrition.carbs_g,
        "total_sugar_g": item.details.nutrition.sugar_g,
        "other_nutrients": item.details.nutrition.other_nutrients,
        "tags": item.details.tags,
    }


def _has_changes(record: object, values: Mapping[str, object]) -> bool:
    """Return whether any mutable natural-key row value differs from its seed value."""
    return any(getattr(record, key) != value for key, value in values.items())


def _assign(record: object, values: Mapping[str, object]) -> None:
    """Assign mutable seed values to an already-resolved ORM record."""
    for key, value in values.items():
        setattr(record, key, value)


def _parse_arguments() -> argparse.Namespace:
    """Parse the narrowly scoped seed command options."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate and report the dataset without writing rows.",
    )
    return parser.parse_args()


async def _run_command(dry_run: bool) -> SeedReport:
    """Load runtime-only settings and run the seed command once."""
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise ValueError("DATABASE_URL is required for the seed command")
    return await seed_database(
        database_url,
        load_admin_seed_config(),
        dry_run=dry_run,
    )


def main() -> None:
    """Run the seed entry point and print its classified outcome summary."""
    arguments = _parse_arguments()
    try:
        report = asyncio.run(_run_command(arguments.dry_run))
    except SeedValidationError as error:
        print(error.report.summary())
        raise
    print(report.summary())


if __name__ == "__main__":
    main()
