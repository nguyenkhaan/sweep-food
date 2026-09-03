"""Guarded one-time reconciliation for the merged Alembic baseline incident.

This utility deliberately has no target default.  Operators must select one
environment variable and request ``reconcile`` explicitly.  It never invokes
Alembic commands and updates ``alembic_version`` only after a complete schema
fingerprint has passed.
"""

# pylint: disable=line-too-long
# pylint: disable=too-many-lines
# The DDL literals deliberately mirror the approved Alembic operations.  Splitting
# them mechanically would make the executable schema definition harder to audit.

from __future__ import annotations

import argparse
import asyncio
import os
import re
from collections.abc import Awaitable, Callable, Sequence
from dataclasses import dataclass, field
from enum import StrEnum
from typing import Final, Protocol

from sqlalchemy import text
from sqlalchemy.engine import make_url
from sqlalchemy.ext.asyncio import AsyncConnection, AsyncEngine, create_async_engine

from src.db import build_async_database_url

HISTORICAL_ROOT: Final = "446cf3ac3439"
HISTORICAL_E8: Final = "e8f0a4b7d9c1"
CURRENT_HEAD: Final = "7b1f4d2a9c30"
SUPPORTED_START_REVISIONS: Final = frozenset({HISTORICAL_ROOT, HISTORICAL_E8})
ALLOWED_TARGET_ENVIRONMENTS: Final = frozenset(
    {
        "DATABASE_URL",
        "TEST_DATABASE_URL",
        "RECONCILE_ROOT_CLONE_URL",
        "RECONCILE_E8_CLONE_URL",
    }
)


class ReconciliationError(RuntimeError):
    """Raised when a target is unsafe or does not match the approved plan."""


class Mode(StrEnum):
    """Supported utility modes."""

    INSPECT = "inspect"
    RECONCILE = "reconcile"


class ReconciliationPath(StrEnum):
    """The two historical schema layouts approved for repair."""

    ROOT = HISTORICAL_ROOT
    E8 = HISTORICAL_E8
    CURRENT = CURRENT_HEAD


class ObjectKind(StrEnum):
    """PostgreSQL catalog object families used by reconciliation operations."""

    INDEX = "index"
    CONSTRAINT = "constraint"
    COLUMN = "column"
    FUNCTION = "function"
    TRIGGER = "trigger"
    ENUM_VALUE = "enum-value"


class InspectionStatus(StrEnum):
    """Read-only classification of one planned reconciliation operation."""

    ABSENT = "ABSENT — would execute"
    PRESENT_MATCH = "PRESENT_MATCH — would safely skip"
    EXPECTED_OLD_MATCH = "EXPECTED_OLD_MATCH — replacement/removal path valid"
    MISMATCH = "MISMATCH — fail inspect"


@dataclass(frozen=True)
class DefinitionExpectation:
    """A normalized catalog definition required before an operation is skipped."""

    name: str
    kind: ObjectKind
    required_fragments: tuple[str, ...]
    forbidden_fragments: tuple[str, ...] = ()
    exact_check_expression: str | None = None


@dataclass(frozen=True)
class TargetSelection:
    """An explicitly selected, non-fallback database environment variable."""

    environment_name: str
    database_url: str


@dataclass(frozen=True)
class Operation:
    """One schema operation and its catalog fingerprint requirement."""

    name: str
    sql: str
    expectations: tuple[DefinitionExpectation, ...]
    replace_old: tuple[DefinitionExpectation, ...] = ()
    conversion_old: tuple[DefinitionExpectation, ...] = ()


@dataclass(frozen=True)
class OperationInspection:
    """One non-mutating typed catalog result for a planned operation."""

    operation_name: str
    status: InspectionStatus


@dataclass
class InspectionOverlay:
    """Verified virtual post-operation state used only by read-only inspection."""

    present: dict[tuple[ObjectKind, str], DefinitionExpectation] = field(
        default_factory=dict
    )
    absent: set[tuple[ObjectKind, str]] = field(default_factory=set)

    def state_for(
        self, expectation: DefinitionExpectation, actual_state: bool | None
    ) -> bool | None:
        """Return a projected state only after its source was type-verified."""
        key = (expectation.kind, expectation.name)
        if key in self.present:
            return self.present[key] == expectation
        if key in self.absent:
            return None
        return actual_state

    def apply(self, operation: Operation) -> None:
        """Record the verified post-operation catalog state without any DDL."""
        for expectation in operation.replace_old:
            key = (expectation.kind, expectation.name)
            self.present.pop(key, None)
            self.absent.add(key)
        for expectation in operation.expectations:
            key = (expectation.kind, expectation.name)
            self.absent.discard(key)
            self.present[key] = expectation


@dataclass(frozen=True)
class Plan:
    """A deterministic reconciliation path for one accepted starting revision."""

    path: ReconciliationPath
    operations: tuple[Operation, ...]
    inspections: tuple[OperationInspection, ...] = ()


class DatabaseConnection(Protocol):
    """Minimal async interface used by the guarded workflow and unit tests."""

    async def scalar(self, statement: str) -> object:
        """Return one scalar value from a guarded statement."""

    async def rows(self, statement: str) -> Sequence[Sequence[object]]:
        """Return rows from a guarded statement."""

    async def execute(self, statement: str) -> None:
        """Execute one approved reconciliation statement."""


class SqlAlchemyConnection:
    """Adapt an SQLAlchemy connection without exposing its connection URL."""

    def __init__(self, connection: AsyncConnection) -> None:
        """Wrap one already-open SQLAlchemy connection."""
        self._connection = connection

    async def scalar(self, statement: str) -> object:
        """Return one scalar without exposing target identity."""
        return (await self._connection.execute(text(statement))).scalar_one()

    async def rows(self, statement: str) -> Sequence[Sequence[object]]:
        """Return rows without exposing target identity."""
        return tuple((await self._connection.execute(text(statement))).all())

    async def execute(self, statement: str) -> None:
        """Execute one approved raw DDL batch."""
        # Reconciliation operations intentionally contain tightly coupled DDL.
        # asyncpg only accepts multi-command batches through its simple protocol.
        raw_connection = await self._connection.get_raw_connection()
        driver_connection = raw_connection.driver_connection
        if driver_connection is None:
            raise ReconciliationError("Database driver connection is unavailable.")
        await driver_connection.execute(statement)


def select_target(
    environment_name: str, environment: dict[str, str] | None = None
) -> TargetSelection:
    """Select exactly one configured target; never substitute another target."""
    if environment_name not in ALLOWED_TARGET_ENVIRONMENTS:
        raise ReconciliationError(
            "Target selection is not allowed for this environment variable."
        )
    source = os.environ if environment is None else environment
    database_url = source.get(environment_name)
    if not database_url:
        raise ReconciliationError(
            "The explicitly selected database target is not configured."
        )
    return TargetSelection(environment_name=environment_name, database_url=database_url)


def choose_path(revision: str) -> ReconciliationPath:
    """Return the only allowed path for an inspected Alembic revision."""
    if revision == CURRENT_HEAD:
        return ReconciliationPath.CURRENT
    if revision in SUPPORTED_START_REVISIONS:
        return ReconciliationPath(revision)
    raise ReconciliationError(
        "Database revision is not an approved reconciliation starting state."
    )


def _expectation(
    name: str,
    kind: ObjectKind,
    *fragments: str,
    forbidden: tuple[str, ...] = (),
    exact_check_expression: str | None = None,
) -> DefinitionExpectation:
    """Create a normalized PostgreSQL catalog expectation."""
    return DefinitionExpectation(
        name,
        kind,
        tuple(fragment.lower() for fragment in fragments),
        tuple(fragment.lower() for fragment in forbidden),
        exact_check_expression,
    )


def _operation(
    name: str,
    sql: str,
    _legacy_kind: str,
    *_legacy_fragments: str,
) -> Operation:
    """Build an operation with typed postcondition and replacement checks."""
    return Operation(
        name,
        sql,
        _expectations_for(name),
        _old_expectations_for(name),
        _conversion_old_expectations_for(name),
    )


# pylint: disable=too-many-return-statements,too-many-branches
# Each branch is an explicit approved-operation mapping; a registry would obscure
# the direct correspondence between reconciliation DDL and its fingerprint.
def _expectations_for(operation_name: str) -> tuple[DefinitionExpectation, ...]:
    """Return exact target catalog definitions for every approved operation."""
    index = ObjectKind.INDEX
    constraint = ObjectKind.CONSTRAINT
    column = ObjectKind.COLUMN
    if operation_name == "catalog-category-functional-unique":
        return (
            _expectation(
                "uq_ingredient_categories_name_lower", index, "unique", "lower(name)"
            ),
        )
    if operation_name == "catalog-recipe-functional-unique":
        return (_expectation("uq_recipes_name_lower", index, "unique", "lower(name)"),)
    if operation_name == "catalog-indexes":
        return tuple(
            _expectation(name, index, *fragments)
            for name, *fragments in (
                ("ix_master_ingredients_category_id", "category_id"),
                (
                    "uq_master_ingredients_category_name_lower",
                    "unique",
                    "category_id",
                    "lower(name)",
                ),
                ("ix_recipe_ingredients_recipe_id", "recipe_id"),
                ("ix_recipe_ingredients_master_ingredient_id", "master_ingredient_id"),
            )
        )
    if operation_name == "catalog-numeric-types":
        return tuple(
            _expectation(name, column, definition)
            for name, definition in (
                ("master_ingredients.calories", "numeric(12,3)|false"),
                ("master_ingredients.protein_g", "numeric(12,3)|false"),
                ("master_ingredients.fat_g", "numeric(12,3)|false"),
                ("master_ingredients.carbs_g", "numeric(12,3)|false"),
                ("master_ingredients.sugar_g", "numeric(12,3)|false"),
                ("master_ingredients.sodium_mg", "numeric(12,3)|false"),
                ("recipes.default_servings", "numeric(6,2)|true"),
                ("recipes.total_calories", "numeric(12,3)|false"),
                ("recipes.total_protein_g", "numeric(12,3)|false"),
                ("recipes.total_fat_g", "numeric(12,3)|false"),
                ("recipes.total_carbs_g", "numeric(12,3)|false"),
                ("recipes.total_sugar_g", "numeric(12,3)|false"),
                ("recipe_ingredients.required_quantity", "numeric(12,3)|true"),
            )
        )
    if operation_name == "catalog-checks":
        return (
            _expectation(
                "recipe_default_servings_positive",
                constraint,
                exact_check_expression="default_servings > 0",
            ),
            _expectation(
                "shelf_life_rule_min_days_nonnegative",
                constraint,
                exact_check_expression="min_days >= 0",
            ),
            _expectation(
                "shelf_life_rule_max_days_nonnegative",
                constraint,
                exact_check_expression="max_days >= 0",
            ),
            _expectation(
                "shelf_life_rule_default_days_nonnegative",
                constraint,
                exact_check_expression="default_days >= 0",
            ),
            _expectation(
                "shelf_life_rule_max_days_at_least_min_days",
                constraint,
                exact_check_expression="max_days >= min_days",
            ),
            _expectation(
                "shelf_life_rule_default_days_in_range",
                constraint,
                exact_check_expression="default_days BETWEEN min_days AND max_days",
            ),
            _expectation(
                "shelf_life_rule_scope_matches_target",
                constraint,
                exact_check_expression="(scope = 'INGREDIENT'::shelf_life_rule_scope AND master_ingredient_id IS NOT NULL AND category_id IS NULL) OR (scope = 'CATEGORY'::shelf_life_rule_scope AND category_id IS NOT NULL AND master_ingredient_id IS NULL)",
            ),
        )
    if operation_name == "notification-query-indexes":
        return tuple(
            _expectation(name, index, *fragments)
            for name, *fragments in (
                ("ix_device_registrations_user_enabled", "user_id", "is_enabled"),
                ("ix_notifications_user_created_at", "user_id", "created_at"),
                (
                    "ix_notifications_delivery_scheduled",
                    "delivery_status",
                    "scheduled_at",
                ),
                ("ix_inventory_batches_status_expires_at", "status", "expires_at"),
            )
        )
    if operation_name == "ledger-event-values":
        return tuple(
            _expectation(name, ObjectKind.ENUM_VALUE, name)
            for name in ("MANUAL_CONSUMPTION", "METADATA_UPDATED", "MOVED", "ARCHIVED")
        )
    if operation_name == "ledger-reason-column":
        return (
            _expectation(
                "inventory_ledger_entries.reason", column, "character varying|false"
            ),
        )
    if operation_name == "phase4-inventory-checks":
        return (
            _expectation(
                "inventory_batch_status_quantity_consistent",
                constraint,
                exact_check_expression="(status = 'ACTIVE' AND current_quantity > 0 AND archived_at IS NULL) OR (status IN ('DEPLETED', 'DISCARDED') AND current_quantity = 0 AND archived_at IS NULL) OR (status = 'ARCHIVED' AND archived_at IS NOT NULL)",
            ),
            _expectation(
                "inventory_batch_source_type_consistent",
                constraint,
                exact_check_expression="(batch_type = 'RAW_INGREDIENT' AND source = 'MANUAL' AND source_cooking_session_id IS NULL) OR (batch_type = 'COOKED_FOOD' AND source = 'LEFTOVER' AND source_cooking_session_id IS NOT NULL)",
            ),
        )
    if operation_name in {"phase4-query-indexes", "rename-e8-indexes"}:
        return tuple(
            _expectation(name, index, *fragments)
            for name, *fragments in (
                (
                    "ix_inventory_batches_user_fefo",
                    "user_id",
                    "status",
                    "expires_at",
                    "created_at",
                ),
                (
                    "ix_inventory_batches_user_ingredient",
                    "user_id",
                    "master_ingredient_id",
                ),
                ("ix_inventory_batches_user_storage", "user_id", "storage_mode"),
                (
                    "ix_inventory_ledger_batch_created",
                    "inventory_batch_id",
                    "created_at",
                ),
                ("ix_inventory_ledger_user_created", "user_id", "created_at"),
            )
        )
    if operation_name == "ledger-idempotency":
        return (
            _expectation(
                "uq_inventory_ledger_idempotent_batch_event",
                constraint,
                "unique",
                "user_id",
                "idempotency_key",
                "inventory_batch_id",
                "event_type",
            ),
            _expectation(
                "uq_inventory_ledger_initial_stock_key",
                index,
                "unique",
                "initial_stock",
                "idempotency_key",
            ),
        )
    if operation_name == "ledger-immutability":
        return (
            _expectation(
                "reject_inventory_ledger_mutation",
                ObjectKind.FUNCTION,
                "raise exception",
                "immutable",
            ),
            _expectation(
                "inventory_ledger_entries_immutable",
                ObjectKind.TRIGGER,
                "before update or delete",
                "reject_inventory_ledger_mutation",
            ),
        )
    if operation_name == "replace-e8-default-servings-check":
        return (
            _expectation(
                "recipe_default_servings_positive",
                constraint,
                exact_check_expression="default_servings > 0",
            ),
        )
    return ()


def _old_expectations_for(operation_name: str) -> tuple[DefinitionExpectation, ...]:
    """Return old definitions that must match before intentional replacement."""
    if operation_name == "catalog-category-functional-unique":
        return (
            _expectation(
                "ingredient_categories_name_key",
                ObjectKind.CONSTRAINT,
                "unique(name)",
                forbidden=("deferrable",),
            ),
        )
    if operation_name == "catalog-recipe-functional-unique":
        return (
            _expectation(
                "recipes_name_key",
                ObjectKind.CONSTRAINT,
                "unique(name)",
                forbidden=("deferrable",),
            ),
        )
    if operation_name == "rename-e8-indexes":
        return tuple(
            _expectation(name, ObjectKind.INDEX, *fragments)
            for name, *fragments in (
                (
                    "ix_inventory_batches_user_status_expires_at_created_at",
                    "user_id",
                    "status",
                    "expires_at",
                    "created_at",
                ),
                (
                    "ix_inventory_batches_user_master_ingredient_id",
                    "user_id",
                    "master_ingredient_id",
                ),
                ("ix_inventory_batches_user_storage_mode", "user_id", "storage_mode"),
                (
                    "ix_inventory_ledger_entries_inventory_batch_id_created_at",
                    "inventory_batch_id",
                    "created_at",
                ),
                (
                    "ix_inventory_ledger_entries_user_id_created_at",
                    "user_id",
                    "created_at",
                ),
            )
        )
    if operation_name == "replace-e8-idempotency":
        return (
            _expectation(
                "uq_inventory_ledger_entries_idempotency_context",
                ObjectKind.INDEX,
                "unique",
                "idempotency_key",
            ),
        )
    if operation_name == "replace-e8-guards":
        return (
            _expectation(
                "inventory_ledger_entries_batch_owner_fk",
                ObjectKind.CONSTRAINT,
                "foreignkey(inventory_batch_id,user_id)referencesinventory_batches(id,user_id)",
                forbidden=("ondeletecascade", "onupdatecascade", "deferrable"),
            ),
            _expectation(
                "inventory_ledger_entry_nonnegative_balances",
                ObjectKind.CONSTRAINT,
                exact_check_expression="quantity_before >= 0 AND quantity_after >= 0",
            ),
            _expectation(
                "inventory_batch_custom_name_nonblank",
                ObjectKind.CONSTRAINT,
                exact_check_expression="custom_name IS NULL OR btrim(custom_name) <> ''",
            ),
            _expectation(
                "inventory_batch_active_quantity_positive",
                ObjectKind.CONSTRAINT,
                exact_check_expression="status <> 'ACTIVE'::inventory_batch_status OR current_quantity > 0",
            ),
            _expectation(
                "inventory_batch_depleted_quantity_zero",
                ObjectKind.CONSTRAINT,
                exact_check_expression="status <> 'DEPLETED'::inventory_batch_status OR current_quantity = 0",
            ),
            _expectation(
                "inventory_batch_expiration_source_matches_date",
                ObjectKind.CONSTRAINT,
                exact_check_expression="(expiration_source = 'UNKNOWN'::expiration_source AND expires_at IS NULL) OR (expiration_source <> 'UNKNOWN'::expiration_source AND expires_at IS NOT NULL)",
            ),
            _expectation(
                "inventory_batch_source_matches_cooking_session",
                ObjectKind.CONSTRAINT,
                exact_check_expression="(source = 'MANUAL'::inventory_source AND source_cooking_session_id IS NULL) OR (source = 'LEFTOVER'::inventory_source AND batch_type = 'COOKED_FOOD'::inventory_batch_type AND source_cooking_session_id IS NOT NULL)",
            ),
            _expectation(
                "uq_inventory_batches_id_user_id",
                ObjectKind.CONSTRAINT,
                "unique(id,user_id)",
            ),
            _expectation(
                "inventory_ledger_entries_reject_mutation",
                ObjectKind.FUNCTION,
                "immutable",
            ),
            _expectation(
                "inventory_ledger_entries_immutable", ObjectKind.TRIGGER, "immutable"
            ),
        )
    if operation_name == "replace-e8-default-servings-check":
        return (
            _expectation(
                "recipe_default_servings_positive",
                ObjectKind.CONSTRAINT,
                exact_check_expression="(default_servings)::double precision > (0)::double precision",
            ),
        )
    return ()


def _conversion_old_expectations_for(
    operation_name: str,
) -> tuple[DefinitionExpectation, ...]:
    """Return exact old states permitted for approved in-place conversions."""
    if operation_name == "catalog-numeric-types":
        return tuple(
            _expectation(name, ObjectKind.COLUMN, definition)
            for name, definition in (
                ("master_ingredients.calories", "doubleprecision|false"),
                ("master_ingredients.protein_g", "doubleprecision|false"),
                ("master_ingredients.fat_g", "doubleprecision|false"),
                ("master_ingredients.carbs_g", "doubleprecision|false"),
                ("master_ingredients.sugar_g", "doubleprecision|false"),
                ("master_ingredients.sodium_mg", "doubleprecision|false"),
                ("recipes.default_servings", "doubleprecision|true"),
                ("recipes.total_calories", "doubleprecision|false"),
                ("recipes.total_protein_g", "doubleprecision|false"),
                ("recipes.total_fat_g", "doubleprecision|false"),
                ("recipes.total_carbs_g", "doubleprecision|false"),
                ("recipes.total_sugar_g", "doubleprecision|false"),
                ("recipe_ingredients.required_quantity", "doubleprecision|true"),
            )
        )
    return ()


CATALOG_OPERATIONS: Final = (
    _operation(
        "catalog-category-functional-unique",
        "ALTER TABLE ingredient_categories DROP CONSTRAINT ingredient_categories_name_key; "
        "CREATE UNIQUE INDEX uq_ingredient_categories_name_lower ON ingredient_categories (lower(name));",
        "index",
        "unique",
        "lower(name)",
    ),
    _operation(
        "catalog-recipe-functional-unique",
        "ALTER TABLE recipes DROP CONSTRAINT recipes_name_key; "
        "CREATE UNIQUE INDEX uq_recipes_name_lower ON recipes (lower(name));",
        "index",
        "unique",
        "lower(name)",
    ),
    _operation(
        "catalog-indexes",
        "CREATE INDEX ix_master_ingredients_category_id ON master_ingredients (category_id); "
        "CREATE UNIQUE INDEX uq_master_ingredients_category_name_lower ON master_ingredients (category_id, lower(name)); "
        "CREATE INDEX ix_recipe_ingredients_recipe_id ON recipe_ingredients (recipe_id); "
        "CREATE INDEX ix_recipe_ingredients_master_ingredient_id ON recipe_ingredients (master_ingredient_id);",
        "index-batch",
        "catalog indexes",
    ),
    _operation(
        "catalog-numeric-types",
        "ALTER TABLE master_ingredients ALTER COLUMN calories TYPE numeric(12,3) USING calories::numeric(12,3), "
        "ALTER COLUMN protein_g TYPE numeric(12,3) USING protein_g::numeric(12,3), "
        "ALTER COLUMN fat_g TYPE numeric(12,3) USING fat_g::numeric(12,3), "
        "ALTER COLUMN carbs_g TYPE numeric(12,3) USING carbs_g::numeric(12,3), "
        "ALTER COLUMN sugar_g TYPE numeric(12,3) USING sugar_g::numeric(12,3), "
        "ALTER COLUMN sodium_mg TYPE numeric(12,3) USING sodium_mg::numeric(12,3); "
        "ALTER TABLE recipes ALTER COLUMN default_servings TYPE numeric(6,2) USING default_servings::numeric(6,2), "
        "ALTER COLUMN total_calories TYPE numeric(12,3) USING total_calories::numeric(12,3), "
        "ALTER COLUMN total_protein_g TYPE numeric(12,3) USING total_protein_g::numeric(12,3), "
        "ALTER COLUMN total_fat_g TYPE numeric(12,3) USING total_fat_g::numeric(12,3), "
        "ALTER COLUMN total_carbs_g TYPE numeric(12,3) USING total_carbs_g::numeric(12,3), "
        "ALTER COLUMN total_sugar_g TYPE numeric(12,3) USING total_sugar_g::numeric(12,3); "
        "ALTER TABLE recipe_ingredients ALTER COLUMN required_quantity TYPE numeric(12,3) USING required_quantity::numeric(12,3);",
        "columns",
        "numeric(12,3)",
    ),
    _operation(
        "catalog-checks",
        "ALTER TABLE recipes ADD CONSTRAINT recipe_default_servings_positive CHECK (default_servings > 0); "
        "ALTER TABLE shelf_life_rules ADD CONSTRAINT shelf_life_rule_min_days_nonnegative CHECK (min_days >= 0), "
        "ADD CONSTRAINT shelf_life_rule_max_days_nonnegative CHECK (max_days >= 0), "
        "ADD CONSTRAINT shelf_life_rule_default_days_nonnegative CHECK (default_days >= 0), "
        "ADD CONSTRAINT shelf_life_rule_max_days_at_least_min_days CHECK (max_days >= min_days), "
        "ADD CONSTRAINT shelf_life_rule_default_days_in_range CHECK (default_days BETWEEN min_days AND max_days), "
        "ADD CONSTRAINT shelf_life_rule_scope_matches_target CHECK ((scope = 'INGREDIENT'::shelf_life_rule_scope AND master_ingredient_id IS NOT NULL AND category_id IS NULL) OR (scope = 'CATEGORY'::shelf_life_rule_scope AND category_id IS NOT NULL AND master_ingredient_id IS NULL));",
        "constraint-batch",
        "catalog checks",
    ),
)

NOTIFICATION_OPERATIONS: Final = (
    _operation(
        "notification-query-indexes",
        "CREATE INDEX ix_device_registrations_user_enabled ON device_registrations (user_id, is_enabled); "
        "CREATE INDEX ix_notifications_user_created_at ON notifications (user_id, created_at); "
        "CREATE INDEX ix_notifications_delivery_scheduled ON notifications (delivery_status, scheduled_at); "
        "CREATE INDEX ix_inventory_batches_status_expires_at ON inventory_batches (status, expires_at);",
        "index-batch",
        "notification indexes",
    ),
)

PHASE4_OPERATIONS: Final = (
    _operation(
        "ledger-event-values",
        "ALTER TYPE inventory_ledger_event_type ADD VALUE IF NOT EXISTS 'MANUAL_CONSUMPTION'; "
        "ALTER TYPE inventory_ledger_event_type ADD VALUE IF NOT EXISTS 'METADATA_UPDATED'; "
        "ALTER TYPE inventory_ledger_event_type ADD VALUE IF NOT EXISTS 'MOVED'; "
        "ALTER TYPE inventory_ledger_event_type ADD VALUE IF NOT EXISTS 'ARCHIVED';",
        "enum-values",
        "manual_consumption",
        "metadata_updated",
        "moved",
        "archived",
    ),
    _operation(
        "ledger-reason-column",
        "ALTER TABLE inventory_ledger_entries ADD COLUMN reason varchar NULL;",
        "column",
        "character varying",
        "nullable",
    ),
    _operation(
        "phase4-inventory-checks",
        "ALTER TABLE inventory_batches ADD CONSTRAINT inventory_batch_status_quantity_consistent CHECK ((status = 'ACTIVE' AND current_quantity > 0 AND archived_at IS NULL) OR (status IN ('DEPLETED', 'DISCARDED') AND current_quantity = 0 AND archived_at IS NULL) OR (status = 'ARCHIVED' AND archived_at IS NOT NULL)), "
        "ADD CONSTRAINT inventory_batch_source_type_consistent CHECK ((batch_type = 'RAW_INGREDIENT' AND source = 'MANUAL' AND source_cooking_session_id IS NULL) OR (batch_type = 'COOKED_FOOD' AND source = 'LEFTOVER' AND source_cooking_session_id IS NOT NULL));",
        "constraint-batch",
        "phase4 checks",
    ),
    _operation(
        "phase4-query-indexes",
        "CREATE INDEX ix_inventory_batches_user_fefo ON inventory_batches (user_id, status, expires_at, created_at); "
        "CREATE INDEX ix_inventory_batches_user_ingredient ON inventory_batches (user_id, master_ingredient_id); "
        "CREATE INDEX ix_inventory_batches_user_storage ON inventory_batches (user_id, storage_mode); "
        "CREATE INDEX ix_inventory_ledger_batch_created ON inventory_ledger_entries (inventory_batch_id, created_at); "
        "CREATE INDEX ix_inventory_ledger_user_created ON inventory_ledger_entries (user_id, created_at);",
        "index-batch",
        "phase4 indexes",
    ),
    _operation(
        "ledger-idempotency",
        "ALTER TABLE inventory_ledger_entries ADD CONSTRAINT uq_inventory_ledger_idempotent_batch_event UNIQUE (user_id, idempotency_key, inventory_batch_id, event_type); "
        "CREATE UNIQUE INDEX uq_inventory_ledger_initial_stock_key ON inventory_ledger_entries (user_id, idempotency_key) WHERE idempotency_key IS NOT NULL AND event_type = 'INITIAL_STOCK';",
        "idempotency",
        "idempotency",
    ),
    _operation(
        "ledger-immutability",
        "CREATE FUNCTION reject_inventory_ledger_mutation() RETURNS trigger AS $$ BEGIN RAISE EXCEPTION 'inventory ledger entries are immutable'; END; $$ LANGUAGE plpgsql; "
        "CREATE TRIGGER inventory_ledger_entries_immutable BEFORE UPDATE OR DELETE ON inventory_ledger_entries FOR EACH ROW EXECUTE FUNCTION reject_inventory_ledger_mutation();",
        "trigger-function",
        "reject_inventory_ledger_mutation",
    ),
)

E8_REPLACEMENT_OPERATIONS: Final = (
    _operation(
        "replace-e8-default-servings-check",
        "ALTER TABLE recipes DROP CONSTRAINT recipe_default_servings_positive; "
        "ALTER TABLE recipes ADD CONSTRAINT recipe_default_servings_positive "
        "CHECK (default_servings > 0);",
        "replace-e8-default-servings-check",
    ),
    _operation(
        "rename-e8-indexes",
        "ALTER INDEX ix_inventory_batches_user_status_expires_at_created_at RENAME TO ix_inventory_batches_user_fefo; "
        "ALTER INDEX ix_inventory_batches_user_master_ingredient_id RENAME TO ix_inventory_batches_user_ingredient; "
        "ALTER INDEX ix_inventory_batches_user_storage_mode RENAME TO ix_inventory_batches_user_storage; "
        "ALTER INDEX ix_inventory_ledger_entries_inventory_batch_id_created_at RENAME TO ix_inventory_ledger_batch_created; "
        "ALTER INDEX ix_inventory_ledger_entries_user_id_created_at RENAME TO ix_inventory_ledger_user_created;",
        "rename-indexes",
        "phase4 indexes",
    ),
    _operation(
        "replace-e8-guards",
        "ALTER TABLE inventory_ledger_entries DROP CONSTRAINT inventory_ledger_entries_batch_owner_fk, DROP CONSTRAINT inventory_ledger_entry_nonnegative_balances; "
        "ALTER TABLE inventory_batches DROP CONSTRAINT inventory_batch_custom_name_nonblank, DROP CONSTRAINT inventory_batch_active_quantity_positive, DROP CONSTRAINT inventory_batch_depleted_quantity_zero, DROP CONSTRAINT inventory_batch_expiration_source_matches_date, DROP CONSTRAINT inventory_batch_source_matches_cooking_session, DROP CONSTRAINT uq_inventory_batches_id_user_id; "
        "DROP TRIGGER inventory_ledger_entries_immutable ON inventory_ledger_entries; DROP FUNCTION inventory_ledger_entries_reject_mutation();",
        "remove-e8-only",
        "obsolete e8 guards absent",
    ),
    _operation(
        "replace-e8-idempotency",
        "DROP INDEX uq_inventory_ledger_entries_idempotency_context;",
        "remove-e8-idempotency",
        "old partial idempotency absent",
    ),
)


def build_plan(path: ReconciliationPath) -> Plan:
    """Build the approved deterministic operation set for one path."""
    if path is ReconciliationPath.ROOT:
        return Plan(
            path, CATALOG_OPERATIONS + NOTIFICATION_OPERATIONS + PHASE4_OPERATIONS
        )
    if path is ReconciliationPath.E8:
        return Plan(
            path,
            NOTIFICATION_OPERATIONS
            + (PHASE4_OPERATIONS[0], PHASE4_OPERATIONS[1], PHASE4_OPERATIONS[2])
            + E8_REPLACEMENT_OPERATIONS[:2]
            + (PHASE4_OPERATIONS[3], PHASE4_OPERATIONS[4])
            + E8_REPLACEMENT_OPERATIONS[2:]
            + (PHASE4_OPERATIONS[5],),
        )
    return Plan(path, ())


async def read_revision(connection: DatabaseConnection) -> str:
    """Read exactly one Alembic revision or fail closed."""
    revisions = await connection.rows(
        "SELECT version_num FROM alembic_version ORDER BY version_num"
    )
    if (
        len(revisions) != 1
        or len(revisions[0]) != 1
        or not isinstance(revisions[0][0], str)
    ):
        raise ReconciliationError("Alembic state must contain exactly one revision.")
    return revisions[0][0]


async def assert_no_preflight_violations(
    connection: DatabaseConnection, path: ReconciliationPath
) -> None:
    """Run approved aggregate-only data preflights before any mutation."""
    checks = [
        "SELECT count(*) FROM (SELECT lower(name) FROM ingredient_categories GROUP BY lower(name) HAVING count(*) > 1) duplicates",
        "SELECT count(*) FROM (SELECT lower(name) FROM recipes GROUP BY lower(name) HAVING count(*) > 1) duplicates",
        "SELECT count(*) FROM (SELECT category_id, lower(name) FROM master_ingredients GROUP BY category_id, lower(name) HAVING count(*) > 1) duplicates",
        "SELECT count(*) FROM recipes WHERE default_servings <= 0",
        "SELECT count(*) FROM shelf_life_rules WHERE min_days < 0 OR max_days < 0 OR default_days < 0 OR max_days < min_days OR default_days NOT BETWEEN min_days AND max_days",
        "SELECT count(*) FROM inventory_batches WHERE NOT ((status = 'ACTIVE' AND current_quantity > 0 AND archived_at IS NULL) OR (status IN ('DEPLETED', 'DISCARDED') AND current_quantity = 0 AND archived_at IS NULL) OR (status = 'ARCHIVED' AND archived_at IS NOT NULL))",
        "SELECT count(*) FROM inventory_batches WHERE NOT ((batch_type = 'RAW_INGREDIENT' AND source = 'MANUAL' AND source_cooking_session_id IS NULL) OR (batch_type = 'COOKED_FOOD' AND source = 'LEFTOVER' AND source_cooking_session_id IS NOT NULL))",
        "SELECT count(*) FROM (SELECT user_id, idempotency_key, inventory_batch_id, event_type FROM inventory_ledger_entries WHERE idempotency_key IS NOT NULL GROUP BY user_id, idempotency_key, inventory_batch_id, event_type HAVING count(*) > 1) duplicates",
        "SELECT count(*) FROM (SELECT user_id, idempotency_key FROM inventory_ledger_entries WHERE idempotency_key IS NOT NULL AND event_type = 'INITIAL_STOCK' GROUP BY user_id, idempotency_key HAVING count(*) > 1) duplicates",
    ]
    if path is ReconciliationPath.ROOT:
        checks.extend(_numeric_preflight_checks())
    for statement in checks:
        result = await connection.scalar(statement)
        if not isinstance(result, int) or result != 0:
            raise ReconciliationError(
                "Data compatibility preflight reported violations."
            )


def _numeric_preflight_checks() -> list[str]:
    specs: list[tuple[str, str, int, int]] = [
        ("master_ingredients", column, 3, 1_000_000_000)
        for column in (
            "calories",
            "protein_g",
            "fat_g",
            "carbs_g",
            "sugar_g",
            "sodium_mg",
        )
    ]
    specs.extend(
        ("recipes", column, 3, 1_000_000_000)
        for column in (
            "total_calories",
            "total_protein_g",
            "total_fat_g",
            "total_carbs_g",
            "total_sugar_g",
        )
    )
    specs.extend(
        (
            ("recipes", "default_servings", 2, 10_000),
            ("recipe_ingredients", "required_quantity", 3, 1_000_000_000),
        )
    )
    return [
        f"SELECT count(*) FROM {table} WHERE {column} IS NOT NULL AND ({column} IN ('NaN'::double precision, 'Infinity'::double precision, '-Infinity'::double precision) OR abs({column}) >= {bound} OR {column} IS DISTINCT FROM round({column}::numeric, {scale})::double precision)"
        for table, column, scale, bound in specs
    ]


async def assert_start_fingerprint(
    connection: DatabaseConnection, path: ReconciliationPath
) -> None:
    """Reject a revision whose catalog does not match its approved historical shape."""
    expected_absent: tuple[str, ...] = (
        "ix_device_registrations_user_enabled",
        "ix_notifications_user_created_at",
        "ix_notifications_delivery_scheduled",
        "ix_inventory_batches_status_expires_at",
    )
    if path is ReconciliationPath.ROOT:
        expected_absent += (
            "uq_ingredient_categories_name_lower",
            "inventory_batch_status_quantity_consistent",
        )
    else:
        expected_absent += (
            "inventory_batch_status_quantity_consistent",
            "ix_inventory_batches_user_fefo",
        )
    for object_name in expected_absent:
        result = await connection.scalar(_object_exists_sql(object_name))
        if result is not False:
            raise ReconciliationError(
                "Starting schema fingerprint does not match the approved historical state."
            )


async def assert_final_fingerprint(connection: DatabaseConnection) -> None:
    """Require all target objects and the current trigger/function before adoption."""
    expected = (
        "uq_ingredient_categories_name_lower",
        "uq_recipes_name_lower",
        "ix_device_registrations_user_enabled",
        "ix_notifications_user_created_at",
        "ix_notifications_delivery_scheduled",
        "ix_inventory_batches_status_expires_at",
        "inventory_batch_status_quantity_consistent",
        "inventory_batch_source_type_consistent",
        "uq_inventory_ledger_idempotent_batch_event",
        "uq_inventory_ledger_initial_stock_key",
        "reject_inventory_ledger_mutation",
    )
    for object_name in expected:
        result = await connection.scalar(_object_exists_sql(object_name))
        if result is not True:
            raise ReconciliationError("Final schema fingerprint is incomplete.")
    old_function = await connection.scalar(
        _object_exists_sql("inventory_ledger_entries_reject_mutation")
    )
    if old_function is not False:
        raise ReconciliationError(
            "Final schema fingerprint retains an obsolete E8 function."
        )
    ledger_values = await connection.scalar(
        "SELECT count(*) FROM pg_enum enum_value "
        "JOIN pg_type enum_type ON enum_type.oid = enum_value.enumtypid "
        "WHERE enum_type.typname = 'inventory_ledger_event_type' "
        "AND enum_value.enumlabel IN ('MANUAL_CONSUMPTION', 'METADATA_UPDATED', 'MOVED', 'ARCHIVED')"
    )
    if ledger_values != 4:
        raise ReconciliationError(
            "Final schema fingerprint is missing current ledger event values."
        )
    reason_column = await connection.scalar(
        "SELECT EXISTS (SELECT 1 FROM information_schema.columns "
        "WHERE table_schema = current_schema() AND table_name = 'inventory_ledger_entries' "
        "AND column_name = 'reason' AND is_nullable = 'YES' "
        "AND data_type = 'character varying')"
    )
    if reason_column is not True:
        raise ReconciliationError(
            "Final schema fingerprint is missing the nullable ledger reason column."
        )


async def assert_final_typed_catalog(connection: DatabaseConnection) -> None:
    """Require every final reconciliation object to match its typed definition."""
    for operation in build_plan(ReconciliationPath.ROOT).operations:
        final_states = await _all_definition_states(connection, operation.expectations)
        if not all(state is True for state in final_states):
            raise ReconciliationError(
                f"Final typed catalog verification failed for {operation.name}."
            )
        replaced_states = await _all_definition_states(
            connection, operation.replace_old
        )
        if any(state is not None for state in replaced_states):
            raise ReconciliationError(
                f"Final typed catalog retains an obsolete object from {operation.name}."
            )


async def assert_e8_replacements_ready(connection: DatabaseConnection) -> None:
    """Confirm replacements exist before E8-only objects may be removed."""
    required = (
        "inventory_batch_status_quantity_consistent",
        "inventory_batch_source_type_consistent",
        "ix_inventory_batches_user_fefo",
        "ix_inventory_ledger_batch_created",
        "uq_inventory_ledger_idempotent_batch_event",
        "uq_inventory_ledger_initial_stock_key",
    )
    for object_name in required:
        if await connection.scalar(_object_exists_sql(object_name)) is not True:
            raise ReconciliationError(
                "E8 replacement schema is incomplete; obsolete objects remain protected."
            )


def _object_exists_sql(object_name: str) -> str:
    safe_name = object_name.replace("'", "''")
    return (
        "SELECT EXISTS (SELECT 1 FROM pg_class WHERE relname = '"
        f"{safe_name}' UNION ALL SELECT 1 FROM pg_constraint WHERE conname = '{safe_name}' "
        f"UNION ALL SELECT 1 FROM pg_proc WHERE proname = '{safe_name}')"
    )


async def adopt_revision(
    connection: DatabaseConnection, final_fingerprint_verified: bool
) -> None:
    """Adopt current head only after the caller has verified the final schema."""
    if not final_fingerprint_verified:
        raise ReconciliationError(
            "Revision adoption requires a verified final schema fingerprint."
        )
    await connection.execute(
        f"UPDATE alembic_version SET version_num = '{CURRENT_HEAD}'"
    )


def _definition_sql(expectation: DefinitionExpectation) -> str:
    """Return a catalog query yielding one normalized definition or no row."""
    name = expectation.name.replace("'", "''")
    if expectation.kind is ObjectKind.INDEX:
        return f"SELECT pg_get_indexdef(indexrelid) FROM pg_index JOIN pg_class ON pg_class.oid=indexrelid WHERE relname='{name}'"
    if expectation.kind is ObjectKind.CONSTRAINT:
        return f"SELECT pg_get_constraintdef(oid) FROM pg_constraint WHERE conname='{name}'"
    if expectation.kind is ObjectKind.COLUMN:
        table, column = name.split(".", maxsplit=1)
        return f"SELECT replace(pg_catalog.format_type(a.atttypid,a.atttypmod),' ','') || '|' || a.attnotnull FROM pg_attribute a JOIN pg_class c ON c.oid=a.attrelid WHERE c.relname='{table}' AND a.attname='{column}' AND a.attnum>0 AND NOT a.attisdropped"
    if expectation.kind is ObjectKind.FUNCTION:
        return f"SELECT pg_get_functiondef(oid) FROM pg_proc WHERE proname='{name}'"
    if expectation.kind is ObjectKind.TRIGGER:
        return f"SELECT pg_get_triggerdef(tg.oid) FROM pg_trigger tg WHERE tg.tgname='{name}' AND NOT tg.tgisinternal"
    return f"SELECT enumlabel FROM pg_enum JOIN pg_type ON pg_type.oid=enumtypid WHERE typname='inventory_ledger_event_type' AND enumlabel='{name}'"


async def _definition_state(
    connection: DatabaseConnection, expectation: DefinitionExpectation
) -> bool | None:
    """Return ``None`` when absent, otherwise whether the definition matches."""
    rows = await connection.rows(_definition_sql(expectation))
    if not rows:
        return None
    if len(rows) != 1 or len(rows[0]) != 1 or not isinstance(rows[0][0], str):
        return False
    definition = _normalize_definition(rows[0][0])
    if expectation.exact_check_expression is not None:
        return _normalize_check_expression(rows[0][0]) == _normalize_check_expression(
            expectation.exact_check_expression
        )
    return all(
        _normalize_definition(fragment) in definition
        for fragment in expectation.required_fragments
    ) and not any(
        _normalize_definition(fragment) in definition
        for fragment in expectation.forbidden_fragments
    )


def _normalize_definition(definition: str) -> str:
    """Normalize catalog rendering without accepting a changed predicate."""
    return (
        "".join(definition.lower().split())
        .replace("beforedeleteorupdate", "beforeupdateordelete")
        .replace("((", "(")
        .replace("))", ")")
    )


def _normalize_check_expression(definition: str) -> str:
    """Normalize only audited PostgreSQL CHECK rendering differences."""
    normalized = " ".join(definition.lower().split())
    check_body = normalized[5:].strip() if normalized.startswith("check") else ""
    if _is_outer_parenthesized(check_body):
        normalized = check_body[1:-1].strip()
    while _is_outer_parenthesized(normalized):
        normalized = normalized[1:-1].strip()
    normalized = _normalize_between_rendering(normalized)
    normalized = _normalize_string_literal_casts(normalized)
    normalized = _normalize_any_array_rendering(normalized)
    normalized = _strip_redundant_atomic_parentheses(normalized)
    normalized = re.sub(
        r"(?<![a-z0-9_])(-?\d+(?:\.\d+)?)::double\s+precision\b",
        r"\1",
        normalized,
    )
    normalized = re.sub(
        r"(?<![a-z0-9_])(-?\d+(?:\.\d+)?)::numeric\b", r"\1", normalized
    )
    normalized = re.sub(r"(?<![a-z0-9_])([a-z_][a-z0-9_]*)::text\b", r"\1", normalized)
    while _is_outer_parenthesized(normalized):
        normalized = normalized[1:-1].strip()
    return "".join(normalized.split())


def _normalize_between_rendering(expression: str) -> str:
    """Match PostgreSQL's canonical expansion of an approved simple BETWEEN."""
    return re.sub(
        r"\b([a-z_][a-z0-9_]*)\s+between\s+([a-z_][a-z0-9_]*)\s+and\s+([a-z_][a-z0-9_]*)\b",
        r"\1 >= \2 and \1 <= \3",
        expression,
    )


def _normalize_string_literal_casts(expression: str) -> str:
    """Remove PostgreSQL's inferred casts on approved string literals only."""
    return re.sub(r"('(?:[^']|'')*')::[a-z_][a-z0-9_]*\b", r"\1", expression)


def _normalize_any_array_rendering(expression: str) -> str:
    """Normalize PostgreSQL's canonical rendering of an approved IN expression."""
    return re.sub(
        r"\b([a-z_][a-z0-9_]*)\s*=\s*any\s*\(\s*array\s*\[\s*([^\]]+)\s*\]\s*\)",
        r"\1 in (\2)",
        expression,
    )


def _strip_redundant_atomic_parentheses(expression: str) -> str:
    """Strip only non-function parentheses around atoms, never boolean groups."""
    normalized = expression
    while True:
        pairs = _parenthesis_pairs(normalized)
        nested_opens = {opening for opening, _ in pairs}
        removals: set[int] = set()
        for opening, closing in pairs:
            if any(
                opening < inner_opening < closing
                and not _is_function_parenthesis(normalized, inner_opening)
                for inner_opening in nested_opens
            ):
                continue
            content = normalized[opening + 1 : closing]
            if _is_function_parenthesis(
                normalized, opening
            ) or _contains_boolean_operator(content):
                continue
            removals.update((opening, closing))
        if not removals:
            return normalized
        normalized = "".join(
            character
            for index, character in enumerate(normalized)
            if index not in removals
        )


def _is_function_parenthesis(expression: str, opening: int) -> bool:
    """Return whether an opening parenthesis immediately follows an identifier."""
    return bool(opening) and expression[opening - 1].isidentifier()


def _parenthesis_pairs(expression: str) -> tuple[tuple[int, int], ...]:
    """Return balanced parentheses outside SQL string literals, if valid."""
    stack: list[int] = []
    pairs: list[tuple[int, int]] = []
    index = 0
    in_string = False
    while index < len(expression):
        character = expression[index]
        if character == "'":
            if (
                in_string
                and index + 1 < len(expression)
                and expression[index + 1] == "'"
            ):
                index += 2
                continue
            in_string = not in_string
        elif not in_string:
            if character == "(":
                stack.append(index)
            elif character == ")":
                if not stack:
                    return ()
                pairs.append((stack.pop(), index))
        index += 1
    if stack or in_string:
        return ()
    return tuple(pairs)


def _contains_boolean_operator(expression: str) -> bool:
    """Return whether an atomic-parenthesis candidate contains AND or OR."""
    return re.search(r"\b(and|or)\b", expression) is not None


def _is_outer_parenthesized(expression: str) -> bool:
    """Return whether one parenthesis pair safely encloses all of *expression*."""
    if (
        len(expression) < 2
        or not expression.startswith("(")
        or not expression.endswith(")")
    ):
        return False
    depth = 0
    index = 0
    in_string = False
    while index < len(expression):
        character = expression[index]
        if character == "'":
            if (
                in_string
                and index + 1 < len(expression)
                and expression[index + 1] == "'"
            ):
                index += 2
                continue
            in_string = not in_string
        elif not in_string:
            if character == "(":
                depth += 1
            elif character == ")":
                depth -= 1
                if depth == 0 and index != len(expression) - 1:
                    return False
                if depth < 0:
                    return False
        index += 1
    return depth == 0 and not in_string


async def _all_definition_states(
    connection: DatabaseConnection,
    expectations: tuple[DefinitionExpectation, ...],
    overlay: InspectionOverlay | None = None,
) -> tuple[bool | None, ...]:
    """Read every operation definition before deciding whether to execute it."""
    states: list[bool | None] = []
    for expectation in expectations:
        state = await _definition_state(connection, expectation)
        if overlay is not None:
            state = overlay.state_for(expectation, state)
        states.append(state)
    return tuple(states)


async def _classify_operation(
    connection: DatabaseConnection,
    operation: Operation,
    overlay: InspectionOverlay | None = None,
) -> InspectionStatus:
    """Classify an operation using the exact verifier shared with reconciliation."""
    new_states = await _all_definition_states(
        connection, operation.expectations, overlay
    )
    if operation.conversion_old:
        return await _classify_conversion_operation(
            connection, operation, new_states, overlay
        )
    if new_states and all(state is True for state in new_states):
        if operation.replace_old:
            old_states = await _all_definition_states(
                connection, operation.replace_old, overlay
            )
            if any(state is not None for state in old_states):
                return InspectionStatus.MISMATCH
        return InspectionStatus.PRESENT_MATCH
    if operation.replace_old:
        old_states = await _all_definition_states(
            connection, operation.replace_old, overlay
        )
        if _is_approved_old_replacement_state(operation, new_states, old_states):
            return InspectionStatus.EXPECTED_OLD_MATCH
    if any(state is False for state in new_states):
        return InspectionStatus.MISMATCH
    if new_states and any(state is True for state in new_states):
        return InspectionStatus.MISMATCH
    if not operation.replace_old:
        return InspectionStatus.ABSENT
    return InspectionStatus.MISMATCH


def _is_approved_old_replacement_state(
    operation: Operation,
    new_states: tuple[bool | None, ...],
    old_states: tuple[bool | None, ...],
) -> bool:
    """Allow exact old definitions, including a same-named replacement object."""
    old_keys = {
        (expectation.kind, expectation.name) for expectation in operation.replace_old
    }
    permitted_new_states = all(
        state is None
        or (state is False and (expectation.kind, expectation.name) in old_keys)
        for expectation, state in zip(operation.expectations, new_states, strict=True)
    )
    return all(state is True for state in old_states) and permitted_new_states


def _obsolete_replacement_states_are_absent(
    operation: Operation, old_states: tuple[bool | None, ...]
) -> bool:
    """Require old objects gone, allowing only a verified same-name replacement."""
    new_keys = {
        (expectation.kind, expectation.name) for expectation in operation.expectations
    }
    return all(
        state is None
        or (state is False and (expectation.kind, expectation.name) in new_keys)
        for expectation, state in zip(operation.replace_old, old_states, strict=True)
    )


async def _classify_conversion_operation(
    connection: DatabaseConnection,
    operation: Operation,
    new_states: tuple[bool | None, ...],
    overlay: InspectionOverlay | None,
) -> InspectionStatus:
    """Accept only approved old/final definitions for an in-place conversion."""
    if len(operation.expectations) != len(operation.conversion_old):
        return InspectionStatus.MISMATCH
    old_states = await _all_definition_states(
        connection, operation.conversion_old, overlay
    )
    for new_state, old_state in zip(new_states, old_states, strict=True):
        if new_state is not True and old_state is not True:
            return InspectionStatus.MISMATCH
    if all(state is True for state in new_states):
        return InspectionStatus.PRESENT_MATCH
    return InspectionStatus.EXPECTED_OLD_MATCH


async def _apply_operation(
    connection: DatabaseConnection, operation: Operation
) -> None:
    """Execute, skip, or fail closed based on every typed object definition."""
    status = await _classify_operation(connection, operation)
    if status is InspectionStatus.MISMATCH:
        raise ReconciliationError("Schema operation state does not match the plan.")
    if status is InspectionStatus.PRESENT_MATCH:
        return
    await connection.execute(operation.sql)
    removed_states = await _all_definition_states(connection, operation.replace_old)
    if not _obsolete_replacement_states_are_absent(operation, removed_states):
        raise ReconciliationError(
            "An obsolete E8 object remains after its approved removal."
        )
    completed_states = await _all_definition_states(connection, operation.expectations)
    if completed_states and not all(state is True for state in completed_states):
        mismatched_names = ", ".join(
            expectation.name
            for expectation, state in zip(
                operation.expectations, completed_states, strict=True
            )
            if state is not True
        )
        raise ReconciliationError(
            f"{operation.name}: approved definitions missing or mismatched: "
            f"{mismatched_names}."
        )


async def reconcile(connection: DatabaseConnection, confirm: bool) -> Plan:
    """Execute the approved workflow, including guarded revision adoption."""
    revision = await read_revision(connection)
    path = choose_path(revision)
    if path is ReconciliationPath.CURRENT:
        await assert_final_fingerprint(connection)
        await assert_final_typed_catalog(connection)
        return build_plan(path)
    if not confirm:
        raise ReconciliationError(
            "Reconciliation execution requires an explicit confirmation flag."
        )
    await assert_start_fingerprint(connection, path)
    await assert_no_preflight_violations(connection, path)
    plan = build_plan(path)
    for operation in plan.operations:
        await _apply_operation(connection, operation)
        if path is ReconciliationPath.E8 and operation.name == "ledger-idempotency":
            await assert_e8_replacements_ready(connection)
    await assert_final_fingerprint(connection)
    await assert_final_typed_catalog(connection)
    await adopt_revision(connection, final_fingerprint_verified=True)
    return plan


async def inspect(connection: DatabaseConnection) -> Plan:
    """Read-only mode: validate revision and report the selected operation plan."""
    revision = await read_revision(connection)
    path = choose_path(revision)
    if path is ReconciliationPath.CURRENT:
        await assert_final_fingerprint(connection)
        await assert_final_typed_catalog(connection)
    else:
        await assert_start_fingerprint(connection, path)
        await assert_no_preflight_violations(connection, path)
    plan = build_plan(path)
    inspections: list[OperationInspection] = []
    overlay = InspectionOverlay()
    for operation in plan.operations:
        status = await _classify_operation(connection, operation, overlay)
        if status is InspectionStatus.MISMATCH:
            raise ReconciliationError(f"{operation.name}: {status.value}")
        inspections.append(OperationInspection(operation.name, status))
        if status is not InspectionStatus.PRESENT_MATCH:
            overlay.apply(operation)
    return Plan(plan.path, plan.operations, tuple(inspections))


async def _run_with_connection(
    target: TargetSelection,
    callback: Callable[[DatabaseConnection], Awaitable[Plan]],
) -> Plan:
    engine: AsyncEngine = create_async_engine(
        _tool_async_database_url(target.database_url), pool_pre_ping=True
    )
    try:
        async with engine.begin() as connection:
            return await callback(SqlAlchemyConnection(connection))
    finally:
        await engine.dispose()


def _tool_async_database_url(database_url: str) -> str:
    """Build an asyncpg URL from supported PostgreSQL URI options only."""
    async_url = make_url(build_async_database_url(database_url))
    sslmode = async_url.query.get("sslmode")
    configured_ssl = async_url.query.get("ssl")
    if sslmode is not None and not isinstance(sslmode, str):
        raise ReconciliationError("Database SSL options are invalid.")
    if configured_ssl is not None and not isinstance(configured_ssl, str):
        raise ReconciliationError("Database SSL options are invalid.")
    if sslmode is not None and configured_ssl not in {None, sslmode}:
        raise ReconciliationError("Database SSL options are incompatible.")
    normalized_url = async_url.difference_update_query(["channel_binding", "sslmode"])
    if sslmode is not None:
        normalized_url = normalized_url.update_query_dict({"ssl": sslmode})
    return normalized_url.render_as_string(hide_password=False)


def _parse_arguments(arguments: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Guarded Alembic baseline reconciliation utility"
    )
    parser.add_argument(
        "--target-env", choices=sorted(ALLOWED_TARGET_ENVIRONMENTS), required=True
    )
    parser.add_argument(
        "--mode", choices=[mode.value for mode in Mode], default=Mode.INSPECT.value
    )
    parser.add_argument("--confirm-reconcile", action="store_true")
    return parser.parse_args(arguments)


def main(arguments: Sequence[str] | None = None) -> int:
    """Run only the explicitly selected mode and emit no connection identity."""
    parsed = _parse_arguments(arguments)
    target = select_target(parsed.target_env)
    mode = Mode(parsed.mode)
    if mode is Mode.INSPECT:
        plan = asyncio.run(_run_with_connection(target, inspect))
    else:
        plan = asyncio.run(
            _run_with_connection(
                target,
                lambda connection: reconcile(connection, parsed.confirm_reconcile),
            )
        )
    for inspection in plan.inspections:
        print(f"operation={inspection.operation_name} status={inspection.status.value}")
    print(f"mode={mode.value} path={plan.path.value} operations={len(plan.operations)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
