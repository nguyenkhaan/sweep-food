"""Schema contract tests for Phase 4 inventory persistence guards."""

from typing import cast

from sqlalchemy import CheckConstraint, Index, Table, UniqueConstraint

from src.model.inventory_batch_model import InventoryBatchModel
from src.model.inventory_ledger_entry_model import InventoryLedgerEntryModel


def test_inventory_batch_schema_enforces_lifecycle_and_fefo_indexes() -> None:
    """Database metadata guards valid balances and ownership-first FEFO queries."""
    table = cast(Table, InventoryBatchModel.__table__)
    constraints = {
        str(constraint.name)
        for constraint in table.constraints
        if isinstance(constraint, CheckConstraint) and constraint.name is not None
    }
    indexes = {
        str(index.name): tuple(str(column.name) for column in index.columns)
        for index in table.indexes
        if isinstance(index, Index) and index.name is not None
    }

    assert "inventory_batch_status_quantity_consistent" in constraints
    assert "inventory_batch_source_type_consistent" in constraints
    assert indexes["ix_inventory_batches_user_fefo"] == (
        "user_id",
        "status",
        "expires_at",
        "created_at",
    )
    assert indexes["ix_inventory_batches_user_ingredient"] == (
        "user_id",
        "master_ingredient_id",
    )
    assert indexes["ix_inventory_batches_user_storage"] == (
        "user_id",
        "storage_mode",
    )


def test_inventory_ledger_schema_supports_audit_and_idempotency() -> None:
    """Ledger metadata retains reasons and rejects duplicate operation records."""
    table = cast(Table, InventoryLedgerEntryModel.__table__)
    unique_constraints = {
        str(constraint.name)
        for constraint in table.constraints
        if isinstance(constraint, UniqueConstraint) and constraint.name is not None
    }
    indexes = {
        str(index.name): tuple(str(column.name) for column in index.columns)
        for index in table.indexes
        if isinstance(index, Index) and index.name is not None
    }

    assert "reason" in table.columns
    assert "uq_inventory_ledger_idempotent_batch_event" in unique_constraints
    assert indexes["ix_inventory_ledger_batch_created"] == (
        "inventory_batch_id",
        "created_at",
    )
    assert indexes["ix_inventory_ledger_user_created"] == (
        "user_id",
        "created_at",
    )
