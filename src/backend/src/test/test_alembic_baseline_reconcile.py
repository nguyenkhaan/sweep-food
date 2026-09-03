"""Static/unit coverage for the guarded baseline reconciliation utility."""

# pylint: disable=line-too-long
# pylint: disable=too-many-lines
# The table-driven fake catalog cases intentionally remain colocated with the
# reconciliation utility they statically verify.

from __future__ import annotations

import asyncio
from collections.abc import Mapping, Sequence
from typing import cast

import pytest
from sqlalchemy.engine import make_url
from sqlalchemy.ext.asyncio import AsyncConnection

import scripts.alembic_baseline_reconcile as reconciliation_tool
from scripts.alembic_baseline_reconcile import (
    CURRENT_HEAD,
    HISTORICAL_E8,
    HISTORICAL_ROOT,
    DefinitionExpectation,
    InspectionStatus,
    ObjectKind,
    Operation,
    OperationInspection,
    Plan,
    ReconciliationError,
    ReconciliationPath,
    SqlAlchemyConnection,
    _apply_operation,
    _definition_state,
    _old_expectations_for,
    _tool_async_database_url,
    adopt_revision,
    assert_no_preflight_violations,
    build_plan,
    choose_path,
    inspect,
    reconcile,
    select_target,
)

CHECK_CONSTRAINT_NAMES = frozenset(
    {
        "recipe_default_servings_positive",
        "shelf_life_rule_min_days_nonnegative",
        "shelf_life_rule_max_days_nonnegative",
        "shelf_life_rule_default_days_nonnegative",
        "shelf_life_rule_max_days_at_least_min_days",
        "shelf_life_rule_default_days_in_range",
        "shelf_life_rule_scope_matches_target",
        "inventory_batch_status_quantity_consistent",
        "inventory_batch_source_type_consistent",
        "inventory_ledger_entry_nonnegative_balances",
        "inventory_batch_custom_name_nonblank",
        "inventory_batch_active_quantity_positive",
        "inventory_batch_depleted_quantity_zero",
        "inventory_batch_expiration_source_matches_date",
        "inventory_batch_source_matches_cooking_session",
    }
)


class FakeConnection:
    """A no-network connection double that records attempted statements."""

    def __init__(
        self,
        revision: str,
        scalar_values: Sequence[object] = (),
        definitions: Mapping[str, str] | None = None,
        mutations: Mapping[str, Mapping[str, str]] | None = None,
        removals: Mapping[str, Sequence[str]] | None = None,
    ) -> None:
        """Create a fake with deterministic scalar responses."""
        self.revision = revision
        self.scalar_values = list(scalar_values)
        self.definitions = dict(definitions or {})
        self.mutations = dict(mutations or {})
        self.removals = dict(removals or {})
        self.executed: list[str] = []

    async def scalar(self, statement: str) -> object:
        """Record and return a scalar response."""
        self.executed.append(statement)
        if self.scalar_values:
            return self.scalar_values.pop(0)
        return False

    async def rows(self, statement: str) -> Sequence[Sequence[object]]:
        """Return rows by query purpose, never revision-shaped catalog data."""
        self.executed.append(statement)
        if "version_num FROM alembic_version" in statement:
            return ((self.revision,),)
        for name, definition in self.definitions.items():
            if "." in name:
                table, column = name.split(".", maxsplit=1)
                if (
                    f"relname='{table}'" in statement
                    and f"attname='{column}'" in statement
                ):
                    return ((definition,),)
            if f"'{name}'" in statement:
                return ((definition,),)
        return ()

    async def execute(self, statement: str) -> None:
        """Record an attempted DDL or metadata statement."""
        self.executed.append(statement)
        for name in self.removals.get(statement, ()):
            self.definitions.pop(name, None)
        self.definitions.update(self.mutations.get(statement, {}))


class FakeRawDriverConnection:
    """A no-network asyncpg simple-protocol double."""

    def __init__(self) -> None:
        """Start with no recorded commands."""
        self.statements: list[str] = []

    async def execute(self, statement: str) -> None:
        """Record one simple-protocol batch."""
        self.statements.append(statement)


class FakeRawConnection:
    """Expose the fake driver's simple-protocol connection."""

    def __init__(self, driver_connection: FakeRawDriverConnection) -> None:
        """Wrap one fake driver connection."""
        self.driver_connection = driver_connection


class FakeAsyncConnection:
    """Minimal SQLAlchemy raw-connection provider for adapter tests."""

    def __init__(self, raw_connection: FakeRawConnection) -> None:
        """Store the raw connection returned to the adapter."""
        self._raw_connection = raw_connection

    async def get_raw_connection(self) -> FakeRawConnection:
        """Return the fake raw connection without any network activity."""
        return self._raw_connection


def test_supported_revisions_choose_distinct_paths() -> None:
    """Each accepted revision selects one deterministic path."""
    assert choose_path(HISTORICAL_ROOT) is ReconciliationPath.ROOT
    assert choose_path(HISTORICAL_E8) is ReconciliationPath.E8
    assert choose_path(CURRENT_HEAD) is ReconciliationPath.CURRENT


def test_sqlalchemy_adapter_uses_simple_protocol_for_ddl_batches() -> None:
    """Approved multi-command DDL avoids asyncpg prepared-statement parsing."""
    driver_connection = FakeRawDriverConnection()
    connection = SqlAlchemyConnection(
        cast(
            AsyncConnection,
            FakeAsyncConnection(FakeRawConnection(driver_connection)),
        )
    )
    statement = "ALTER TABLE example ADD COLUMN value integer; CREATE INDEX example_value ON example (value);"
    asyncio.run(connection.execute(statement))
    assert driver_connection.statements == [statement]


def test_unknown_revision_is_rejected() -> None:
    """Unknown historical state fails closed."""
    with pytest.raises(ReconciliationError):
        choose_path("unknown-revision")


def test_target_selection_never_falls_back() -> None:
    """The requested target does not fall back to another setting."""
    with pytest.raises(ReconciliationError):
        select_target("TEST_DATABASE_URL", {"DATABASE_URL": "postgresql://unused"})


@pytest.mark.parametrize(
    "target_environment",
    ("RECONCILE_ROOT_CLONE_URL", "RECONCILE_E8_CLONE_URL"),
)
def test_clone_target_is_explicit_and_has_no_fallback(
    target_environment: str,
) -> None:
    """Each disposable clone is accepted only when its own setting is present."""
    with pytest.raises(ReconciliationError):
        select_target(target_environment, {"DATABASE_URL": "postgresql://unused"})
    target = select_target(
        target_environment,
        {target_environment: "postgresql://clone-only"},
    )
    assert target.environment_name == target_environment


def test_tool_async_url_normalizes_postgresql_options_for_asyncpg() -> None:
    """The async driver receives SSL but never unsupported URI-only options."""
    url = _tool_async_database_url(
        "postgresql://user:password@example.invalid/database?channel_binding=require&sslmode=require"
    )
    query = make_url(url).query
    assert "channel_binding" not in query
    assert "sslmode" not in query
    assert query["ssl"] == "require"


def test_tool_async_url_rejects_conflicting_ssl_options() -> None:
    """Conflicting standard and asyncpg SSL options fail without connecting."""
    with pytest.raises(ReconciliationError):
        _tool_async_database_url(
            "postgresql://user:password@example.invalid/database?sslmode=require&ssl=disable"
        )


def test_target_selection_does_not_echo_sensitive_value() -> None:
    """Target selection errors and results do not contain its URL."""
    secret_url = "postgresql://secret-user:secret-password@example.invalid/private"
    target = select_target("DATABASE_URL", {"DATABASE_URL": secret_url})
    assert target.environment_name == "DATABASE_URL"
    assert secret_url not in repr(target.environment_name)


def test_plans_are_intentionally_different() -> None:
    """The root and E8 paths contain only their approved deltas."""
    root_names = {
        operation.name for operation in build_plan(ReconciliationPath.ROOT).operations
    }
    e8_names = {
        operation.name for operation in build_plan(ReconciliationPath.E8).operations
    }
    assert "catalog-numeric-types" in root_names
    assert "catalog-numeric-types" not in e8_names
    assert "replace-e8-default-servings-check" in e8_names
    assert "replace-e8-guards" in e8_names
    assert "replace-e8-guards" not in root_names


def test_adoption_requires_final_verification() -> None:
    """A caller cannot update revision metadata without verification."""
    connection = FakeConnection(HISTORICAL_ROOT)
    with pytest.raises(ReconciliationError):
        asyncio.run(adopt_revision(connection, final_fingerprint_verified=False))
    assert not any(
        "UPDATE alembic_version" in statement for statement in connection.executed
    )


def test_preflight_violation_aborts() -> None:
    """Any non-zero aggregate preflight result stops the workflow."""
    connection = FakeConnection(HISTORICAL_ROOT, [1])
    with pytest.raises(ReconciliationError):
        asyncio.run(assert_no_preflight_violations(connection, ReconciliationPath.E8))


def test_mismatched_start_fingerprint_aborts_before_mutation() -> None:
    """Unexpected historical objects stop before reconciliation DDL."""
    connection = FakeConnection(HISTORICAL_ROOT, [True])
    with pytest.raises(ReconciliationError):
        asyncio.run(reconcile(connection, confirm=True))
    assert not any(
        "ALTER " in statement or "CREATE " in statement
        for statement in connection.executed
    )


def test_current_revision_is_verification_only() -> None:
    """Current revision runs validation only and never adopts metadata."""
    root_operations = build_plan(ReconciliationPath.ROOT).operations
    connection = FakeConnection(
        CURRENT_HEAD,
        [True] * 11 + [False, 4, True],
        definitions=_definitions_for_final_expectations(root_operations),
    )
    plan = asyncio.run(reconcile(connection, confirm=True))
    assert plan.path is ReconciliationPath.CURRENT
    assert not any(
        "UPDATE alembic_version" in statement for statement in connection.executed
    )


def _index_operation() -> Operation:
    """Return one small typed operation used to exercise restart semantics."""
    return Operation(
        "index",
        "CREATE INDEX example_index ON example_table (owner_id)",
        (DefinitionExpectation("example_index", ObjectKind.INDEX, ("owner_id",)),),
    )


def _check_expectation() -> DefinitionExpectation:
    """Return one exact approved CHECK expectation for normalization tests."""
    return DefinitionExpectation(
        "inventory_ledger_entry_nonnegative_balances",
        ObjectKind.CONSTRAINT,
        (),
        exact_check_expression="quantity_before >= 0 AND quantity_after >= 0",
    )


def _install_one_operation_plan(
    monkeypatch: pytest.MonkeyPatch, operation: Operation
) -> None:
    """Replace only the operation plan while preserving production inspection."""

    _install_operation_plan(monkeypatch, (operation,))


def _install_operation_plan(
    monkeypatch: pytest.MonkeyPatch, operations: tuple[Operation, ...]
) -> None:
    """Replace only a plan's operations while preserving production inspection."""

    def build_one_operation_plan(path: ReconciliationPath) -> Plan:
        """Return the selected path with focused typed operations."""
        return Plan(path, operations)

    monkeypatch.setattr(reconciliation_tool, "build_plan", build_one_operation_plan)


def _numeric_conversion_operation() -> Operation:
    """Return the production root numeric conversion operation."""
    return next(
        operation
        for operation in build_plan(ReconciliationPath.ROOT).operations
        if operation.name == "catalog-numeric-types"
    )


def _definitions_for_expectations(
    expectations: Sequence[DefinitionExpectation],
) -> dict[str, str]:
    """Build exact fake catalog rows from simple typed column expectations."""
    return {
        expectation.name: expectation.required_fragments[0]
        for expectation in expectations
    }


def _definitions_for_final_expectations(
    operations: Sequence[Operation],
) -> dict[str, str]:
    """Build fake catalog rows for every final expectation in a plan."""
    return {
        expectation.name: (
            expectation.exact_check_expression
            if expectation.exact_check_expression is not None
            else " ".join(expectation.required_fragments)
        )
        for operation in operations
        for expectation in operation.expectations
    }


def test_absent_object_executes_and_verifies_new_definition() -> None:
    """An absent typed object runs once and must appear with its definition."""
    operation = _index_operation()
    connection = FakeConnection(
        HISTORICAL_ROOT,
        mutations={
            operation.sql: {
                "example_index": "CREATE INDEX example_index ON example_table (owner_id)"
            }
        },
    )
    asyncio.run(_apply_operation(connection, operation))
    assert connection.executed.count(operation.sql) == 1


def test_matching_existing_object_is_skipped() -> None:
    """A matching definition proves a completed operation can be skipped."""
    operation = _index_operation()
    connection = FakeConnection(
        HISTORICAL_ROOT,
        definitions={
            "example_index": "CREATE INDEX example_index ON example_table (owner_id)"
        },
    )
    asyncio.run(_apply_operation(connection, operation))
    assert operation.sql not in connection.executed


def test_mismatched_index_fails_before_mutation() -> None:
    """A different index key fails closed and prevents execution."""
    operation = _index_operation()
    connection = FakeConnection(
        HISTORICAL_ROOT,
        definitions={
            "example_index": "CREATE INDEX example_index ON example_table (other_id)"
        },
    )
    with pytest.raises(ReconciliationError):
        asyncio.run(_apply_operation(connection, operation))
    assert operation.sql not in connection.executed


def test_restart_mismatch_stops_later_operations() -> None:
    """A mismatched completed object prevents all remaining restart work."""
    first = _index_operation()
    second = Operation(
        "second",
        "CREATE INDEX second_index ON example_table (owner_id)",
        (DefinitionExpectation("second_index", ObjectKind.INDEX, ("owner_id",)),),
    )
    connection = FakeConnection(
        HISTORICAL_ROOT,
        definitions={
            "example_index": "CREATE INDEX example_index ON example_table (wrong_id)"
        },
    )
    with pytest.raises(ReconciliationError):
        asyncio.run(_apply_operation(connection, first))
    assert second.sql not in connection.executed


@pytest.mark.parametrize(
    ("expectation", "definition"),
    (
        (
            DefinitionExpectation(
                "expected_check",
                ObjectKind.CONSTRAINT,
                (),
                exact_check_expression="quantity > 0",
            ),
            "CHECK (( quantity > 0 ))",
        ),
        (
            DefinitionExpectation(
                "entries.expected_numeric",
                ObjectKind.COLUMN,
                ("numeric(12,3)|false",),
            ),
            "numeric(12,3)|false",
        ),
        (
            DefinitionExpectation("expected_enum", ObjectKind.ENUM_VALUE, ("value",)),
            "VALUE",
        ),
        (
            DefinitionExpectation(
                "expected_function",
                ObjectKind.FUNCTION,
                ("raiseexception", "immutable"),
            ),
            "CREATE FUNCTION expected_function() RETURNS trigger AS $$ BEGIN RAISE EXCEPTION 'immutable'; END; $$ LANGUAGE plpgsql",
        ),
        (
            DefinitionExpectation(
                "expected_trigger",
                ObjectKind.TRIGGER,
                ("beforeupdateordelete", "expected_function"),
            ),
            "CREATE TRIGGER expected_trigger BEFORE UPDATE OR DELETE ON entries FOR EACH ROW EXECUTE FUNCTION expected_function()",
        ),
        (
            DefinitionExpectation(
                "canonical_trigger",
                ObjectKind.TRIGGER,
                ("beforeupdateordelete", "expected_function"),
            ),
            "CREATE TRIGGER canonical_trigger BEFORE DELETE OR UPDATE ON entries FOR EACH ROW EXECUTE FUNCTION expected_function()",
        ),
        (
            DefinitionExpectation(
                "expected_fk",
                ObjectKind.CONSTRAINT,
                ("foreignkey(batch_id,user_id)referencesbatches(id,user_id)",),
            ),
            "FOREIGN KEY (batch_id, user_id) REFERENCES batches(id, user_id)",
        ),
    ),
)
def test_typed_equivalent_definitions_pass(
    expectation: DefinitionExpectation, definition: str
) -> None:
    """Every catalog family used by the tool accepts a normalized match."""
    connection = FakeConnection(
        HISTORICAL_ROOT, definitions={expectation.name: definition}
    )
    assert asyncio.run(_definition_state(connection, expectation)) is True


@pytest.mark.parametrize(
    ("expectation", "definition"),
    (
        (
            DefinitionExpectation(
                "entries.column", ObjectKind.COLUMN, ("numeric(12,3)|false",)
            ),
            "numeric(10,3)|false",
        ),
        (
            DefinitionExpectation(
                "entries.column", ObjectKind.COLUMN, ("numeric(12,3)|false",)
            ),
            "numeric(12,2)|false",
        ),
        (
            DefinitionExpectation(
                "entries.column", ObjectKind.COLUMN, ("numeric(12,3)|false",)
            ),
            "numeric(12,3)|true",
        ),
        (
            DefinitionExpectation("function", ObjectKind.FUNCTION, ("immutable",)),
            "CREATE FUNCTION function() RETURNS trigger AS $$ BEGIN RETURN NEW; END; $$ LANGUAGE plpgsql",
        ),
        (
            DefinitionExpectation(
                "trigger", ObjectKind.TRIGGER, ("reject_inventory_ledger_mutation",)
            ),
            "CREATE TRIGGER trigger BEFORE UPDATE ON entries EXECUTE FUNCTION old_function()",
        ),
        (
            DefinitionExpectation(
                "fk",
                ObjectKind.CONSTRAINT,
                ("foreignkey(batch_id,user_id)referencesbatches(id,user_id)",),
                ("ondeletecascade",),
            ),
            "FOREIGN KEY (batch_id, user_id) REFERENCES other_batches(id, user_id) ON DELETE CASCADE",
        ),
    ),
)
def test_typed_mismatched_definitions_fail(
    expectation: DefinitionExpectation, definition: str
) -> None:
    """Names alone never make a typed schema object equivalent."""
    connection = FakeConnection(
        HISTORICAL_ROOT, definitions={expectation.name: definition}
    )
    assert asyncio.run(_definition_state(connection, expectation)) is False


@pytest.mark.parametrize(
    "definition",
    (
        "quantity_before >= 0 AND quantity_after >= 0",
        "CHECK ( quantity_before >= 0 AND quantity_after >= 0 )",
        "CHECK (((quantity_before >= 0 AND quantity_after >= 0)))",
    ),
)
def test_exact_check_expression_accepts_only_wrapper_equivalents(
    definition: str,
) -> None:
    """Whitespace and complete catalog wrappers do not change an approved CHECK."""
    expectation = _check_expectation()
    connection = FakeConnection(
        HISTORICAL_ROOT, definitions={expectation.name: definition}
    )
    assert asyncio.run(_definition_state(connection, expectation)) is True


@pytest.mark.parametrize(
    "definition",
    (
        "CHECK (quantity_before > 0 AND quantity_after >= 0)",
        "CHECK (quantity_before >= 0 AND quantity_after >= 1)",
        "CHECK (balance_before >= 0 AND quantity_after >= 0)",
        "CHECK (quantity_before >= 0 OR quantity_after >= 0)",
        "CHECK ((quantity_before >= 0 AND quantity_after >= 0) OR override_ok)",
        "CHECK ((quantity_before >= 0 AND quantity_after >= 0) AND audit_ok)",
        "CHECK (quantity_before >= 0 AND quantity_after >= 0 OR override_ok)",
    ),
)
def test_exact_check_expression_rejects_changed_predicates(definition: str) -> None:
    """Operators, values, columns, grouping, and extra logic fail closed."""
    expectation = _check_expectation()
    connection = FakeConnection(
        HISTORICAL_ROOT, definitions={expectation.name: definition}
    )
    assert asyncio.run(_definition_state(connection, expectation)) is False


def test_historical_e8_check_mismatch_blocks_removal_and_adoption() -> None:
    """An E8 CHECK must match its historical full expression before removal."""
    old_check = next(
        expectation
        for expectation in _old_expectations_for("replace-e8-guards")
        if expectation.name == "inventory_batch_active_quantity_positive"
    )
    operation = Operation(
        "replace-e8-check",
        "DROP CONSTRAINT inventory_batch_active_quantity_positive",
        (DefinitionExpectation("replacement", ObjectKind.INDEX, ("current_key",)),),
        (old_check,),
    )
    connection = FakeConnection(
        HISTORICAL_E8,
        definitions={
            old_check.name: "CHECK (status <> 'ACTIVE'::inventory_batch_status "
            "AND current_quantity > 0)"
        },
    )
    with pytest.raises(ReconciliationError):
        asyncio.run(_apply_operation(connection, operation))
    assert operation.sql not in connection.executed
    assert not any(
        "UPDATE alembic_version" in statement for statement in connection.executed
    )


def test_e8_same_named_historical_check_is_replaced_with_current_definition() -> None:
    """A double-cast historical check is replaced only after exact verification."""
    operation = next(
        operation
        for operation in build_plan(ReconciliationPath.E8).operations
        if operation.name == "replace-e8-default-servings-check"
    )
    old_check = operation.replace_old[0]
    new_check = operation.expectations[0]
    connection = FakeConnection(
        HISTORICAL_E8,
        definitions={
            old_check.name: "CHECK (((default_servings)::double precision > "
            "(0)::double precision))"
        },
        removals={operation.sql: (old_check.name,)},
        mutations={
            operation.sql: {new_check.name: "CHECK ((default_servings > (0)::numeric))"}
        },
    )
    asyncio.run(_apply_operation(connection, operation))
    assert connection.executed.count(operation.sql) == 1
    assert asyncio.run(_definition_state(connection, new_check)) is True


@pytest.mark.parametrize(
    ("name", "definition"),
    (
        (
            "inventory_ledger_entry_nonnegative_balances",
            (
                "CHECK (((quantity_before >= (0)::double precision) AND "
                "(quantity_after >= (0)::double precision)))"
            ),
        ),
        (
            "inventory_batch_custom_name_nonblank",
            (
                "CHECK (((custom_name IS NULL) OR "
                "(btrim((custom_name)::text) <> ''::text)))"
            ),
        ),
        (
            "inventory_batch_active_quantity_positive",
            (
                "CHECK (((status <> 'ACTIVE'::inventory_batch_status) OR "
                "(current_quantity > (0)::double precision)))"
            ),
        ),
        (
            "inventory_batch_depleted_quantity_zero",
            (
                "CHECK (((status <> 'DEPLETED'::inventory_batch_status) OR "
                "(current_quantity = (0)::double precision)))"
            ),
        ),
        (
            "inventory_batch_expiration_source_matches_date",
            (
                "CHECK ((((expiration_source = 'UNKNOWN'::expiration_source) AND "
                "(expires_at IS NULL)) OR ((expiration_source <> "
                "'UNKNOWN'::expiration_source) AND (expires_at IS NOT NULL))))"
            ),
        ),
        (
            "inventory_batch_source_matches_cooking_session",
            (
                "CHECK ((((source = 'MANUAL'::inventory_source) AND "
                "(source_cooking_session_id IS NULL)) OR ((source = "
                "'LEFTOVER'::inventory_source) AND (batch_type = "
                "'COOKED_FOOD'::inventory_batch_type) AND "
                "(source_cooking_session_id IS NOT NULL))))"
            ),
        ),
    ),
)
def test_historical_e8_check_catalog_rendering_is_exactly_equivalent(
    name: str, definition: str
) -> None:
    """Only approved PostgreSQL rendering changes preserve an E8 CHECK match."""
    expectation = next(
        expectation
        for expectation in _old_expectations_for("replace-e8-guards")
        if expectation.name == name
    )
    connection = FakeConnection(HISTORICAL_E8, definitions={name: definition})
    assert asyncio.run(_definition_state(connection, expectation)) is True


@pytest.mark.parametrize(
    ("expected_expression", "catalog_definition"),
    (
        (
            "default_servings > 0",
            "CHECK ((default_servings > (0)::numeric))",
        ),
        (
            "default_days BETWEEN min_days AND max_days",
            "CHECK (((default_days >= min_days) AND (default_days <= max_days)))",
        ),
        (
            (
                "(status = 'ACTIVE' AND current_quantity > 0 AND archived_at IS NULL) "
                "OR (status IN ('DEPLETED', 'DISCARDED') AND current_quantity = 0 "
                "AND archived_at IS NULL) OR (status = 'ARCHIVED' AND archived_at "
                "IS NOT NULL)"
            ),
            (
                "CHECK ((((status = 'ACTIVE'::inventory_batch_status) AND "
                "(current_quantity > (0)::double precision) AND (archived_at IS NULL)) "
                "OR ((status = ANY (ARRAY['DEPLETED'::inventory_batch_status, "
                "'DISCARDED'::inventory_batch_status])) AND (current_quantity = "
                "(0)::double precision) AND (archived_at IS NULL)) OR ((status = "
                "'ARCHIVED'::inventory_batch_status) AND (archived_at IS NOT NULL))))"
            ),
        ),
        (
            (
                "(batch_type = 'RAW_INGREDIENT' AND source = 'MANUAL' AND "
                "source_cooking_session_id IS NULL) OR (batch_type = 'COOKED_FOOD' "
                "AND source = 'LEFTOVER' AND source_cooking_session_id IS NOT NULL)"
            ),
            (
                "CHECK ((((batch_type = 'RAW_INGREDIENT'::inventory_batch_type) "
                "AND (source = 'MANUAL'::inventory_source) AND "
                "(source_cooking_session_id IS NULL)) OR ((batch_type = "
                "'COOKED_FOOD'::inventory_batch_type) AND (source = "
                "'LEFTOVER'::inventory_source) AND (source_cooking_session_id "
                "IS NOT NULL))))"
            ),
        ),
    ),
)
def test_current_catalog_check_rendering_is_exactly_equivalent(
    expected_expression: str, catalog_definition: str
) -> None:
    """Only the audited current PostgreSQL CHECK renderings are normalized."""
    expectation = DefinitionExpectation(
        "current_check",
        ObjectKind.CONSTRAINT,
        (),
        exact_check_expression=expected_expression,
    )
    connection = FakeConnection(
        HISTORICAL_ROOT, definitions={expectation.name: catalog_definition}
    )
    assert asyncio.run(_definition_state(connection, expectation)) is True


def test_every_reconciliation_check_uses_an_exact_expression() -> None:
    """No approved current or historical CHECK relies on fragment matching."""
    current_expectations = (
        expectation
        for path in (ReconciliationPath.ROOT, ReconciliationPath.E8)
        for operation in build_plan(path).operations
        for expectation in operation.expectations
    )
    historical_expectations = (
        expectation
        for operation in build_plan(ReconciliationPath.E8).operations
        for expectation in operation.replace_old
    )
    checks = [
        expectation
        for expectation in (*current_expectations, *historical_expectations)
        if expectation.name in CHECK_CONSTRAINT_NAMES
    ]
    assert checks
    assert all(
        expectation.exact_check_expression is not None
        and not expectation.required_fragments
        for expectation in checks
    )


def test_inspect_reports_matching_typed_object_without_mutation(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Inspect reuses the typed verifier and never executes a planned statement."""
    operation = _index_operation()
    _install_one_operation_plan(monkeypatch, operation)
    connection = FakeConnection(
        HISTORICAL_ROOT,
        definitions={
            "example_index": "CREATE INDEX example_index ON example_table (owner_id)"
        },
    )
    plan = asyncio.run(inspect(connection))
    assert plan.inspections == (
        OperationInspection(operation.name, InspectionStatus.PRESENT_MATCH),
    )
    assert operation.sql not in connection.executed
    assert not any(
        "UPDATE alembic_version" in statement for statement in connection.executed
    )


def test_inspect_reports_absent_typed_object_without_mutation(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """An absent expected object is classified as work, not treated as a match."""
    operation = _index_operation()
    _install_one_operation_plan(monkeypatch, operation)
    connection = FakeConnection(HISTORICAL_ROOT)
    plan = asyncio.run(inspect(connection))
    assert plan.inspections == (
        OperationInspection(operation.name, InspectionStatus.ABSENT),
    )
    assert operation.sql not in connection.executed


def test_inspect_reports_expected_old_replacement_state(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A complete matching E8 old state is safe to inspect as a replacement path."""
    old = DefinitionExpectation("old_index", ObjectKind.INDEX, ("legacy_key",))
    new = DefinitionExpectation("new_index", ObjectKind.INDEX, ("current_key",))
    operation = Operation("replace", "REPLACE INDEX", (new,), (old,))
    _install_one_operation_plan(monkeypatch, operation)
    connection = FakeConnection(
        HISTORICAL_E8,
        definitions={"old_index": "CREATE INDEX old_index ON entries (legacy_key)"},
    )
    plan = asyncio.run(inspect(connection))
    assert plan.inspections == (
        OperationInspection(operation.name, InspectionStatus.EXPECTED_OLD_MATCH),
    )
    assert operation.sql not in connection.executed


def test_inspect_projects_verified_e8_removal_for_later_creation(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Inspect models a verified prior E8 removal without issuing either statement."""
    old = DefinitionExpectation(
        "inventory_ledger_entries_immutable", ObjectKind.TRIGGER, ("old_function",)
    )
    current = DefinitionExpectation(
        "inventory_ledger_entries_immutable", ObjectKind.TRIGGER, ("new_function",)
    )
    remove = Operation("remove-old-trigger", "DROP TRIGGER", (), (old,))
    create = Operation("create-current-trigger", "CREATE TRIGGER", (current,))
    _install_operation_plan(monkeypatch, (remove, create))
    connection = FakeConnection(
        HISTORICAL_E8,
        definitions={
            old.name: "CREATE TRIGGER inventory_ledger_entries_immutable "
            "BEFORE UPDATE ON entries EXECUTE FUNCTION old_function()"
        },
    )
    plan = asyncio.run(inspect(connection))
    assert plan.inspections == (
        OperationInspection(remove.name, InspectionStatus.EXPECTED_OLD_MATCH),
        OperationInspection(create.name, InspectionStatus.ABSENT),
    )
    assert remove.sql not in connection.executed
    assert create.sql not in connection.executed


def test_inspect_accepts_all_approved_old_numeric_definitions(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """All audited historical double-precision columns are a valid root state."""
    operation = _numeric_conversion_operation()
    _install_one_operation_plan(monkeypatch, operation)
    connection = FakeConnection(
        HISTORICAL_ROOT,
        definitions=_definitions_for_expectations(operation.conversion_old),
    )
    plan = asyncio.run(inspect(connection))
    assert plan.inspections == (
        OperationInspection(operation.name, InspectionStatus.EXPECTED_OLD_MATCH),
    )
    assert operation.sql not in connection.executed


def test_inspect_accepts_all_final_numeric_definitions(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """All current numeric definitions make the conversion safely skippable."""
    operation = _numeric_conversion_operation()
    _install_one_operation_plan(monkeypatch, operation)
    connection = FakeConnection(
        HISTORICAL_ROOT,
        definitions=_definitions_for_expectations(operation.expectations),
    )
    plan = asyncio.run(inspect(connection))
    assert plan.inspections == (
        OperationInspection(operation.name, InspectionStatus.PRESENT_MATCH),
    )
    assert operation.sql not in connection.executed


def test_inspect_accepts_valid_interrupted_numeric_conversion(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A restart may continue when every column is independently old or final."""
    operation = _numeric_conversion_operation()
    _install_one_operation_plan(monkeypatch, operation)
    definitions = _definitions_for_expectations(operation.conversion_old)
    definitions[operation.expectations[0].name] = operation.expectations[
        0
    ].required_fragments[0]
    connection = FakeConnection(HISTORICAL_ROOT, definitions=definitions)
    plan = asyncio.run(inspect(connection))
    assert plan.inspections == (
        OperationInspection(operation.name, InspectionStatus.EXPECTED_OLD_MATCH),
    )
    assert operation.sql not in connection.executed


@pytest.mark.parametrize(
    "definition",
    ("integer|false", "doubleprecision|true"),
)
def test_inspect_rejects_unapproved_numeric_conversion_definition(
    monkeypatch: pytest.MonkeyPatch, definition: str
) -> None:
    """A third type or wrong nullability is never accepted as conversion input."""
    operation = _numeric_conversion_operation()
    _install_one_operation_plan(monkeypatch, operation)
    definitions = _definitions_for_expectations(operation.conversion_old)
    definitions[operation.expectations[0].name] = definition
    connection = FakeConnection(HISTORICAL_ROOT, definitions=definitions)
    with pytest.raises(ReconciliationError, match="catalog-numeric-types: MISMATCH"):
        asyncio.run(inspect(connection))
    assert operation.sql not in connection.executed


def test_reconciliation_conversion_reuses_approved_old_definition_guard() -> None:
    """The mutating workflow accepts only old/final column definitions too."""
    operation = _numeric_conversion_operation()
    old_definitions = _definitions_for_expectations(operation.conversion_old)
    final_definitions = _definitions_for_expectations(operation.expectations)
    connection = FakeConnection(
        HISTORICAL_ROOT,
        definitions=old_definitions,
        mutations={operation.sql: final_definitions},
    )
    asyncio.run(_apply_operation(connection, operation))
    assert connection.executed.count(operation.sql) == 1


@pytest.mark.parametrize(
    ("expectation", "definition"),
    (
        (
            DefinitionExpectation("index", ObjectKind.INDEX, ("owner_id",)),
            "CREATE INDEX index ON entries (other_id)",
        ),
        (
            DefinitionExpectation(
                "check",
                ObjectKind.CONSTRAINT,
                (),
                exact_check_expression="quantity_before >= 0 AND quantity_after >= 0",
            ),
            "CHECK (quantity_before > 0 AND quantity_after >= 0)",
        ),
        (
            DefinitionExpectation(
                "fk",
                ObjectKind.CONSTRAINT,
                ("foreignkey(batch_id,user_id)referencesbatches(id,user_id)",),
            ),
            "FOREIGN KEY (batch_id, user_id) REFERENCES other_batches(id, user_id)",
        ),
        (
            DefinitionExpectation("trigger", ObjectKind.TRIGGER, ("current_function",)),
            "CREATE TRIGGER trigger BEFORE UPDATE ON entries EXECUTE FUNCTION old_function()",
        ),
        (
            DefinitionExpectation(
                "function", ObjectKind.FUNCTION, ("raiseexception", "immutable")
            ),
            "CREATE FUNCTION function() RETURNS trigger AS $$ BEGIN RETURN NEW; END; $$ LANGUAGE plpgsql",
        ),
    ),
)
def test_inspect_rejects_mismatched_typed_objects_without_mutation(
    monkeypatch: pytest.MonkeyPatch,
    expectation: DefinitionExpectation,
    definition: str,
) -> None:
    """Inspect fails closed for every typed object family used by these paths."""
    operation = Operation("typed-mismatch", "MUTATING SQL", (expectation,))
    _install_one_operation_plan(monkeypatch, operation)
    connection = FakeConnection(
        HISTORICAL_ROOT, definitions={expectation.name: definition}
    )
    with pytest.raises(ReconciliationError, match="typed-mismatch: MISMATCH"):
        asyncio.run(inspect(connection))
    assert operation.sql not in connection.executed
    assert not any(
        "UPDATE alembic_version" in statement for statement in connection.executed
    )


def test_e8_replacement_removes_old_then_verifies_new() -> None:
    """Expected E8 old state is removed before its typed replacement is accepted."""
    old = DefinitionExpectation("old_index", ObjectKind.INDEX, ("legacy_key",))
    new = DefinitionExpectation("new_index", ObjectKind.INDEX, ("current_key",))
    operation = Operation("replace", "REPLACE INDEX", (new,), (old,))
    connection = FakeConnection(
        HISTORICAL_E8,
        definitions={"old_index": "CREATE INDEX old_index ON entries (legacy_key)"},
        mutations={
            operation.sql: {
                "new_index": "CREATE INDEX new_index ON entries (current_key)"
            }
        },
        removals={operation.sql: ("old_index",)},
    )
    asyncio.run(_apply_operation(connection, operation))
    assert "old_index" not in connection.definitions
    assert connection.definitions["new_index"].endswith("(current_key)")


def test_e8_removal_failure_blocks_replacement_restart() -> None:
    """An old E8 object surviving its removal aborts before later mutations."""
    old = DefinitionExpectation("old_index", ObjectKind.INDEX, ("legacy_key",))
    new = DefinitionExpectation("new_index", ObjectKind.INDEX, ("current_key",))
    operation = Operation("replace", "REPLACE INDEX", (new,), (old,))
    later = "LATER MUTATION"
    connection = FakeConnection(
        HISTORICAL_E8,
        definitions={"old_index": "CREATE INDEX old_index ON entries (legacy_key)"},
        mutations={
            operation.sql: {
                "new_index": "CREATE INDEX new_index ON entries (current_key)"
            }
        },
    )
    with pytest.raises(ReconciliationError):
        asyncio.run(_apply_operation(connection, operation))
    assert later not in connection.executed


def test_hybrid_replacement_state_fails_closed() -> None:
    """Matching new plus remaining old E8 state is an unsafe hybrid."""
    old = DefinitionExpectation("old_index", ObjectKind.INDEX, ("legacy_key",))
    new = DefinitionExpectation("new_index", ObjectKind.INDEX, ("current_key",))
    operation = Operation("replace", "REPLACE INDEX", (new,), (old,))
    connection = FakeConnection(
        HISTORICAL_E8,
        definitions={
            "old_index": "CREATE INDEX old_index ON entries (legacy_key)",
            "new_index": "CREATE INDEX new_index ON entries (current_key)",
        },
    )
    with pytest.raises(ReconciliationError):
        asyncio.run(_apply_operation(connection, operation))
    assert operation.sql not in connection.executed


def test_critical_ddl_matches_current_migration_names() -> None:
    """Critical approved DDL names remain aligned with current migrations."""
    root_sql = "\n".join(
        operation.sql for operation in build_plan(ReconciliationPath.ROOT).operations
    )
    for name in (
        "ix_device_registrations_user_enabled",
        "ix_notifications_user_created_at",
        "ix_notifications_delivery_scheduled",
        "ix_inventory_batches_status_expires_at",
        "reject_inventory_ledger_mutation",
        "uq_inventory_ledger_initial_stock_key",
    ):
        assert name in root_sql
