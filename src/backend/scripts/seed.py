"""Seed the minimal catalog bootstrap dataset with transactional natural-key upserts."""

from __future__ import annotations

import argparse
import asyncio
import importlib
import os
import sys
from collections.abc import Callable, Iterable, Mapping
from datetime import UTC, datetime
from decimal import Decimal
from pathlib import Path
from typing import TYPE_CHECKING, TypeVar, cast
from uuid import UUID

from sqlalchemy import Select, func, select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

if TYPE_CHECKING:
    from scripts.seed_data import DEFAULT_DATASET
    from scripts.seed_types import (
        AdminSeedConfig,
        AliasSeed,
        CategorySeed,
        IngredientSeed,
        NutritionSeed,
        RecipeIngredientSeed,
        RecipeSeed,
        SeedDataset,
        SeedReport,
        SeedRunContext,
        ShelfLifeRuleSeed,
    )
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
else:
    if __package__ is None:
        sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    _seed_data = importlib.import_module("scripts.seed_data")
    _seed_types = importlib.import_module("scripts.seed_types")
    DEFAULT_DATASET = _seed_data.DEFAULT_DATASET
    AdminSeedConfig = _seed_types.AdminSeedConfig
    AliasSeed = _seed_types.AliasSeed
    CategorySeed = _seed_types.CategorySeed
    IngredientSeed = _seed_types.IngredientSeed
    NutritionSeed = _seed_types.NutritionSeed
    RecipeIngredientSeed = _seed_types.RecipeIngredientSeed
    RecipeSeed = _seed_types.RecipeSeed
    SeedDataset = _seed_types.SeedDataset
    SeedReport = _seed_types.SeedReport
    SeedRunContext = _seed_types.SeedRunContext
    ShelfLifeRuleSeed = _seed_types.ShelfLifeRuleSeed
    _db = importlib.import_module("src.db")
    _pwd_hash = importlib.import_module("src.helper.pwd_hash")
    _enums = importlib.import_module("src.model.enum_model")
    _ingredient_alias = importlib.import_module("src.model.ingredient_alias_model")
    _ingredient_category = importlib.import_module(
        "src.model.ingredient_category_model"
    )
    _master_ingredient = importlib.import_module("src.model.master_ingredient_model")
    _recipe_ingredient = importlib.import_module("src.model.recipe_ingredient_model")
    _recipe = importlib.import_module("src.model.recipe_model")
    _shelf_life_rule = importlib.import_module("src.model.shelf_life_rule_model")
    _user = importlib.import_module("src.model.user_model")
    build_async_database_url = _db.build_async_database_url
    compare_hash = _pwd_hash.compare_hash
    hashing = _pwd_hash.hashing
    AccountStatus = _enums.AccountStatus
    MeasurementUnit = _enums.MeasurementUnit
    ShelfLifeRuleScope = _enums.ShelfLifeRuleScope
    StorageMode = _enums.StorageMode
    UserRole = _enums.UserRole
    IngredientAliasModel = _ingredient_alias.IngredientAliasModel
    IngredientCategoryModel = _ingredient_category.IngredientCategoryModel
    MasterIngredientModel = _master_ingredient.MasterIngredientModel
    RecipeIngredientModel = _recipe_ingredient.RecipeIngredientModel
    RecipeModel = _recipe.RecipeModel
    ShelfLifeRuleModel = _shelf_life_rule.ShelfLifeRuleModel
    UserModel = _user.UserModel

__all__ = [
    "DEFAULT_DATASET",
    "AdminSeedConfig",
    "NutritionSeed",
    "RecipeIngredientSeed",
    "SeedDataset",
    "SeedValidationError",
    "reconcile_recipe_nutrition",
    "seed_dataset",
    "validate_seed_input",
]

NameModel = TypeVar("NameModel", IngredientCategoryModel, RecipeModel)


class SeedValidationError(ValueError):
    """Expose all rejected seed records without revealing secrets."""

    def __init__(self, report: SeedReport) -> None:
        self.report = report
        details = "; ".join(report.rejected)
        super().__init__(f"Seed validation failed: {details}")


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
        {item.key: item for item in dataset.ingredients},
        report,
    )
    _validate_recipe_nutrition(dataset, report)

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
    ingredients: Mapping[str, IngredientSeed],
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
        _validate_recipe_ingredient_record(record, recipe_keys, ingredients, report)


def _validate_recipe_ingredient_record(
    record: RecipeIngredientSeed,
    recipe_keys: set[str],
    ingredients: Mapping[str, IngredientSeed],
    report: SeedReport,
) -> None:
    """Validate one recipe ingredient's dependency and quantity values."""
    if record.recipe_key not in recipe_keys:
        report.add(
            "rejected", f"recipe-ingredient references recipe:{record.recipe_key}"
        )
    if record.ingredient_key not in ingredients:
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

    ingredient = ingredients.get(record.ingredient_key)
    if ingredient is not None and not _are_units_compatible(
        record.unit, ingredient.canonical_unit
    ):
        report.add(
            "rejected",
            "recipe-ingredient:"
            f"{record.recipe_key}/{record.ingredient_key} has an incompatible unit",
        )


def _validate_recipe_nutrition(dataset: SeedDataset, report: SeedReport) -> None:
    """Reject declared recipe totals that disagree with computable ingredients."""
    calculated = reconcile_recipe_nutrition(dataset)
    for recipe in dataset.recipes:
        expected = calculated.get(recipe.key)
        if expected is not None and not _nutrition_matches(
            recipe.details.nutrition, expected
        ):
            report.add("rejected", f"recipe:{recipe.key} nutrition does not reconcile")


def reconcile_recipe_nutrition(
    dataset: SeedDataset,
) -> dict[str, NutritionSeed]:
    """Calculate recipe totals when every ingredient has usable mass nutrition."""
    ingredients = {item.key: item for item in dataset.ingredients}
    calculated: dict[str, NutritionSeed] = {}
    for recipe in dataset.recipes:
        recipe_ingredients = tuple(
            item for item in dataset.recipe_ingredients if item.recipe_key == recipe.key
        )
        nutrition = _calculate_recipe_nutrition(recipe_ingredients, ingredients)
        if nutrition is not None:
            calculated[recipe.key] = nutrition
    return calculated


def _calculate_recipe_nutrition(
    recipe_ingredients: tuple[RecipeIngredientSeed, ...],
    ingredients: Mapping[str, IngredientSeed],
) -> NutritionSeed | None:
    """Return a mass-based nutrition total, or None when a value is unavailable."""
    if not recipe_ingredients:
        return None
    totals = [Decimal(0) for _ in range(5)]
    for recipe_ingredient in recipe_ingredients:
        ingredient = ingredients.get(recipe_ingredient.ingredient_key)
        if ingredient is None:
            return None
        grams = _quantity_in_grams(recipe_ingredient)
        nutrition_values = _ingredient_recipe_nutrition(ingredient)
        if grams is None or any(value is None for value in nutrition_values):
            return None
        multiplier = grams / Decimal(100)
        for index, value in enumerate(nutrition_values):
            totals[index] += cast(Decimal, value) * multiplier
    return NutritionSeed(
        calories=totals[0],
        protein_g=totals[1],
        fat_g=totals[2],
        carbs_g=totals[3],
        sugar_g=totals[4],
    )


def _quantity_in_grams(record: RecipeIngredientSeed) -> Decimal | None:
    """Convert a supported mass recipe quantity to grams for nutrition calculation."""
    if record.unit is MeasurementUnit.GRAM:
        return record.required_quantity
    if record.unit is MeasurementUnit.KG:
        return record.required_quantity * Decimal(1000)
    return None


def _ingredient_recipe_nutrition(
    ingredient: IngredientSeed,
) -> tuple[Decimal | None, ...]:
    """Return the five nutrition totals that the recipe model can store directly."""
    return (
        ingredient.nutrition.calories,
        ingredient.nutrition.protein_g,
        ingredient.nutrition.fat_g,
        ingredient.nutrition.carbs_g,
        ingredient.nutrition.sugar_g,
    )


def _nutrition_matches(expected: NutritionSeed, actual: NutritionSeed) -> bool:
    """Compare all denormalized recipe nutrition fields exactly as seeded."""
    return _recipe_nutrition_values(expected) == _recipe_nutrition_values(actual)


def _recipe_nutrition_values(
    nutrition: NutritionSeed,
) -> tuple[Decimal | None, ...]:
    """Return the denormalized nutrition fields persisted on recipes."""
    return (
        nutrition.calories,
        nutrition.protein_g,
        nutrition.fat_g,
        nutrition.carbs_g,
        nutrition.sugar_g,
    )


def _are_units_compatible(
    left: MeasurementUnit,
    right: MeasurementUnit,
) -> bool:
    """Return whether recipe and canonical units are equal or in one unit group."""
    mass_units = {MeasurementUnit.GRAM, MeasurementUnit.KG}
    volume_units = {MeasurementUnit.ML, MeasurementUnit.LITER}
    return (
        left == right
        or (left in mass_units and right in mass_units)
        or (left in volume_units and right in volume_units)
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
