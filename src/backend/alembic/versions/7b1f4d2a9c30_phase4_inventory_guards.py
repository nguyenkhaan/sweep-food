"""Add Phase 4 inventory invariants and immutable-ledger guards.

Revision ID: 7b1f4d2a9c30
Revises: 2ca31dd74ae1
Create Date: 2026-09-01 19:00:00
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "7b1f4d2a9c30"
down_revision: str | Sequence[str] | None = "2ca31dd74ae1"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Add audit context, query indexes, idempotency, and write guards."""
    for event_type in (
        "MANUAL_CONSUMPTION",
        "METADATA_UPDATED",
        "MOVED",
        "ARCHIVED",
    ):
        op.execute(
            f"ALTER TYPE inventory_ledger_event_type "
            f"ADD VALUE IF NOT EXISTS '{event_type}'"
        )
    op.add_column(
        "inventory_ledger_entries",
        sa.Column("reason", sa.String(), nullable=True),
    )
    op.create_check_constraint(
        "inventory_batch_status_quantity_consistent",
        "inventory_batches",
        "(status = 'ACTIVE' AND current_quantity > 0 AND archived_at IS NULL) "
        "OR (status IN ('DEPLETED', 'DISCARDED') "
        "AND current_quantity = 0 AND archived_at IS NULL) "
        "OR (status = 'ARCHIVED' AND archived_at IS NOT NULL)",
    )
    op.create_check_constraint(
        "inventory_batch_source_type_consistent",
        "inventory_batches",
        "(batch_type = 'RAW_INGREDIENT' AND source = 'MANUAL' "
        "AND source_cooking_session_id IS NULL) "
        "OR (batch_type = 'COOKED_FOOD' AND source = 'LEFTOVER' "
        "AND source_cooking_session_id IS NOT NULL)",
    )
    op.create_index(
        "ix_inventory_batches_user_fefo",
        "inventory_batches",
        ["user_id", "status", "expires_at", "created_at"],
    )
    op.create_index(
        "ix_inventory_batches_user_ingredient",
        "inventory_batches",
        ["user_id", "master_ingredient_id"],
    )
    op.create_index(
        "ix_inventory_batches_user_storage",
        "inventory_batches",
        ["user_id", "storage_mode"],
    )
    op.create_unique_constraint(
        "uq_inventory_ledger_idempotent_batch_event",
        "inventory_ledger_entries",
        ["user_id", "idempotency_key", "inventory_batch_id", "event_type"],
    )
    op.create_index(
        "uq_inventory_ledger_initial_stock_key",
        "inventory_ledger_entries",
        ["user_id", "idempotency_key"],
        unique=True,
        postgresql_where=sa.text(
            "idempotency_key IS NOT NULL AND event_type = 'INITIAL_STOCK'"
        ),
    )
    op.create_index(
        "ix_inventory_ledger_batch_created",
        "inventory_ledger_entries",
        ["inventory_batch_id", "created_at"],
    )
    op.create_index(
        "ix_inventory_ledger_user_created",
        "inventory_ledger_entries",
        ["user_id", "created_at"],
    )
    op.execute(
        """
        CREATE FUNCTION reject_inventory_ledger_mutation()
        RETURNS trigger AS $$
        BEGIN
            RAISE EXCEPTION 'inventory ledger entries are immutable';
        END;
        $$ LANGUAGE plpgsql
        """
    )
    op.execute(
        """
        CREATE TRIGGER inventory_ledger_entries_immutable
        BEFORE UPDATE OR DELETE ON inventory_ledger_entries
        FOR EACH ROW EXECUTE FUNCTION reject_inventory_ledger_mutation()
        """
    )


def downgrade() -> None:
    """Remove Phase 4 guards in dependency-safe order."""
    op.execute(
        "DROP TRIGGER IF EXISTS inventory_ledger_entries_immutable "
        "ON inventory_ledger_entries"
    )
    op.execute("DROP FUNCTION IF EXISTS reject_inventory_ledger_mutation()")
    op.drop_index(
        "uq_inventory_ledger_initial_stock_key",
        table_name="inventory_ledger_entries",
    )
    op.drop_constraint(
        "uq_inventory_ledger_idempotent_batch_event",
        "inventory_ledger_entries",
        type_="unique",
    )
    op.execute(
        "ALTER TABLE inventory_ledger_entries "
        "ALTER COLUMN event_type TYPE VARCHAR USING event_type::text"
    )
    op.execute(
        "UPDATE inventory_ledger_entries SET event_type = 'MANUAL_ADJUSTMENT' "
        "WHERE event_type = 'MANUAL_CONSUMPTION'"
    )
    op.execute(
        "UPDATE inventory_ledger_entries SET event_type = 'CORRECTION' "
        "WHERE event_type IN ('METADATA_UPDATED', 'MOVED', 'ARCHIVED')"
    )
    op.execute("DROP TYPE inventory_ledger_event_type")
    op.execute(
        "CREATE TYPE inventory_ledger_event_type AS ENUM "
        "('INITIAL_STOCK', 'MANUAL_ADJUSTMENT', 'COOKING_CONSUMPTION', "
        "'DISCARDED', 'LEFTOVER_CREATED', 'CORRECTION')"
    )
    op.execute(
        "ALTER TABLE inventory_ledger_entries ALTER COLUMN event_type "
        "TYPE inventory_ledger_event_type "
        "USING event_type::inventory_ledger_event_type"
    )
    op.drop_index(
        "ix_inventory_ledger_user_created",
        table_name="inventory_ledger_entries",
    )
    op.drop_index(
        "ix_inventory_ledger_batch_created",
        table_name="inventory_ledger_entries",
    )
    op.drop_index(
        "ix_inventory_batches_user_storage",
        table_name="inventory_batches",
    )
    op.drop_index(
        "ix_inventory_batches_user_ingredient",
        table_name="inventory_batches",
    )
    op.drop_index(
        "ix_inventory_batches_user_fefo",
        table_name="inventory_batches",
    )
    op.drop_constraint(
        "inventory_batch_source_type_consistent",
        "inventory_batches",
        type_="check",
    )
    op.drop_constraint(
        "inventory_batch_status_quantity_consistent",
        "inventory_batches",
        type_="check",
    )
    op.drop_column("inventory_ledger_entries", "reason")
