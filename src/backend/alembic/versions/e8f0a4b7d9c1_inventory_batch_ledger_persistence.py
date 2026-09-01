"""Harden inventory batch and immutable ledger persistence.

Revision ID: e8f0a4b7d9c1
Revises: b7f3e0a1c2d4
Create Date: 2026-09-01 00:00:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "e8f0a4b7d9c1"
down_revision: str | Sequence[str] | None = "b7f3e0a1c2d4"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def _assert_inventory_rows_are_compatible() -> None:
    """Reject pre-existing data that would violate the new inventory contract."""
    op.execute(
        sa.text(
            """
            DO $$
            BEGIN
                IF EXISTS (
                    SELECT 1
                    FROM inventory_batches
                    WHERE custom_name IS NOT NULL
                      AND btrim(custom_name) = ''
                ) THEN
                    RAISE EXCEPTION
                        'Cannot enforce inventory custom-name integrity: blank names exist';
                END IF;

                IF EXISTS (
                    SELECT 1
                    FROM inventory_batches
                    WHERE (status = 'ACTIVE'::inventory_batch_status
                           AND current_quantity <= 0)
                       OR (status = 'DEPLETED'::inventory_batch_status
                           AND current_quantity <> 0)
                ) THEN
                    RAISE EXCEPTION
                        'Cannot enforce inventory batch status integrity';
                END IF;

                IF EXISTS (
                    SELECT 1
                    FROM inventory_batches
                    WHERE (expiration_source = 'UNKNOWN'::expiration_source
                           AND expires_at IS NOT NULL)
                       OR (expiration_source <> 'UNKNOWN'::expiration_source
                           AND expires_at IS NULL)
                ) THEN
                    RAISE EXCEPTION
                        'Cannot enforce inventory expiration integrity: incompatible dates exist';
                END IF;

                IF EXISTS (
                    SELECT 1
                    FROM inventory_batches
                    WHERE (source = 'MANUAL'::inventory_source
                           AND source_cooking_session_id IS NOT NULL)
                       OR (source = 'LEFTOVER'::inventory_source
                           AND (batch_type <> 'COOKED_FOOD'::inventory_batch_type
                                OR source_cooking_session_id IS NULL))
                ) THEN
                    RAISE EXCEPTION
                        'Cannot enforce inventory source integrity: incompatible sources exist';
                END IF;

                IF EXISTS (
                    SELECT 1
                    FROM inventory_ledger_entries
                    WHERE quantity_before < 0
                       OR quantity_after < 0
                ) THEN
                    RAISE EXCEPTION
                        'Cannot enforce inventory ledger integrity: negative balances exist';
                END IF;

                IF EXISTS (
                    SELECT 1
                    FROM inventory_ledger_entries AS entry
                    JOIN inventory_batches AS batch
                      ON batch.id = entry.inventory_batch_id
                    WHERE entry.user_id <> batch.user_id
                ) THEN
                    RAISE EXCEPTION
                        'Cannot enforce inventory ledger ownership: mismatched users exist';
                END IF;

                IF EXISTS (
                    SELECT 1
                    FROM inventory_ledger_entries
                    WHERE idempotency_key IS NOT NULL
                    GROUP BY user_id, idempotency_key, inventory_batch_id, event_type
                    HAVING count(*) > 1
                ) THEN
                    RAISE EXCEPTION
                        'Cannot enforce inventory ledger idempotency: duplicate entries exist';
                END IF;
            END
            $$;
            """,
        ),
    )


def upgrade() -> None:
    """Add Task 4.1 inventory integrity, query indexes, and ledger protection."""
    _assert_inventory_rows_are_compatible()

    op.create_check_constraint(
        "inventory_batch_custom_name_nonblank",
        "inventory_batches",
        "custom_name IS NULL OR btrim(custom_name) <> ''",
    )
    op.create_check_constraint(
        "inventory_batch_active_quantity_positive",
        "inventory_batches",
        "status <> 'ACTIVE'::inventory_batch_status OR current_quantity > 0",
    )
    op.create_check_constraint(
        "inventory_batch_depleted_quantity_zero",
        "inventory_batches",
        "status <> 'DEPLETED'::inventory_batch_status OR current_quantity = 0",
    )
    op.create_check_constraint(
        "inventory_batch_expiration_source_matches_date",
        "inventory_batches",
        "(expiration_source = 'UNKNOWN'::expiration_source AND expires_at IS NULL) "
        "OR (expiration_source <> 'UNKNOWN'::expiration_source "
        "AND expires_at IS NOT NULL)",
    )
    op.create_check_constraint(
        "inventory_batch_source_matches_cooking_session",
        "inventory_batches",
        "(source = 'MANUAL'::inventory_source "
        "AND source_cooking_session_id IS NULL) "
        "OR (source = 'LEFTOVER'::inventory_source "
        "AND batch_type = 'COOKED_FOOD'::inventory_batch_type "
        "AND source_cooking_session_id IS NOT NULL)",
    )
    op.create_index(
        "ix_inventory_batches_user_status_expires_at_created_at",
        "inventory_batches",
        ["user_id", "status", "expires_at", "created_at"],
    )
    op.create_index(
        "ix_inventory_batches_user_master_ingredient_id",
        "inventory_batches",
        ["user_id", "master_ingredient_id"],
    )
    op.create_index(
        "ix_inventory_batches_user_storage_mode",
        "inventory_batches",
        ["user_id", "storage_mode"],
    )
    op.create_unique_constraint(
        "uq_inventory_batches_id_user_id",
        "inventory_batches",
        ["id", "user_id"],
    )

    op.create_check_constraint(
        "inventory_ledger_entry_nonnegative_balances",
        "inventory_ledger_entries",
        "quantity_before >= 0 AND quantity_after >= 0",
    )
    op.create_foreign_key(
        "inventory_ledger_entries_batch_owner_fk",
        "inventory_ledger_entries",
        "inventory_batches",
        ["inventory_batch_id", "user_id"],
        ["id", "user_id"],
    )
    op.create_index(
        "ix_inventory_ledger_entries_inventory_batch_id_created_at",
        "inventory_ledger_entries",
        ["inventory_batch_id", "created_at"],
    )
    op.create_index(
        "ix_inventory_ledger_entries_user_id_created_at",
        "inventory_ledger_entries",
        ["user_id", "created_at"],
    )
    op.create_index(
        "uq_inventory_ledger_entries_idempotency_context",
        "inventory_ledger_entries",
        ["user_id", "idempotency_key", "inventory_batch_id", "event_type"],
        unique=True,
        postgresql_where=sa.text("idempotency_key IS NOT NULL"),
    )

    op.execute(
        sa.text(
            """
            CREATE FUNCTION inventory_ledger_entries_reject_mutation()
            RETURNS trigger
            LANGUAGE plpgsql
            AS $$
            BEGIN
                RAISE EXCEPTION 'inventory ledger entries are immutable'
                    USING ERRCODE = '55000';
            END;
            $$;
            """,
        ),
    )

    op.execute(
        sa.text(
            """
            CREATE TRIGGER inventory_ledger_entries_immutable
            BEFORE UPDATE OR DELETE ON inventory_ledger_entries
            FOR EACH ROW
            EXECUTE FUNCTION inventory_ledger_entries_reject_mutation();
            """,
        ),
    )


def downgrade() -> None:
    """Remove Task 4.1 persistence hardening in dependency-safe order."""
    op.execute(
        sa.text(
            "DROP TRIGGER inventory_ledger_entries_immutable "
            "ON inventory_ledger_entries",
        ),
    )
    op.execute(sa.text("DROP FUNCTION inventory_ledger_entries_reject_mutation()"))

    op.drop_index(
        "uq_inventory_ledger_entries_idempotency_context",
        table_name="inventory_ledger_entries",
    )
    op.drop_index(
        "ix_inventory_ledger_entries_user_id_created_at",
        table_name="inventory_ledger_entries",
    )
    op.drop_index(
        "ix_inventory_ledger_entries_inventory_batch_id_created_at",
        table_name="inventory_ledger_entries",
    )
    op.drop_constraint(
        "inventory_ledger_entries_batch_owner_fk",
        "inventory_ledger_entries",
        type_="foreignkey",
    )
    op.drop_constraint(
        "inventory_ledger_entry_nonnegative_balances",
        "inventory_ledger_entries",
        type_="check",
    )

    op.drop_constraint(
        "uq_inventory_batches_id_user_id",
        "inventory_batches",
        type_="unique",
    )
    op.drop_index(
        "ix_inventory_batches_user_storage_mode",
        table_name="inventory_batches",
    )
    op.drop_index(
        "ix_inventory_batches_user_master_ingredient_id",
        table_name="inventory_batches",
    )
    op.drop_index(
        "ix_inventory_batches_user_status_expires_at_created_at",
        table_name="inventory_batches",
    )
    op.drop_constraint(
        "inventory_batch_source_matches_cooking_session",
        "inventory_batches",
        type_="check",
    )
    op.drop_constraint(
        "inventory_batch_expiration_source_matches_date",
        "inventory_batches",
        type_="check",
    )
    op.drop_constraint(
        "inventory_batch_depleted_quantity_zero",
        "inventory_batches",
        type_="check",
    )
    op.drop_constraint(
        "inventory_batch_active_quantity_positive",
        "inventory_batches",
        type_="check",
    )
    op.drop_constraint(
        "inventory_batch_custom_name_nonblank",
        "inventory_batches",
        type_="check",
    )
