"""Harden Phase 5 planning and recommendation persistence.

Revision ID: e15d3a9b4c72
Revises: 7b1f4d2a9c30
Create Date: 2026-09-02 03:45:00
"""

from collections.abc import Sequence

from alembic import op

revision: str = "e15d3a9b4c72"
down_revision: str | Sequence[str] | None = "7b1f4d2a9c30"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Add planning query indexes and cross-table date-range enforcement."""
    op.create_index(
        "ix_recommendation_runs_user_created_at",
        "recommendation_runs",
        ["user_id", "created_at"],
    )
    op.create_index(
        "ix_recommendation_items_recipe_id",
        "recommendation_items",
        ["recipe_id"],
    )
    op.create_index(
        "ix_meal_plans_user_starts_on",
        "meal_plans",
        ["user_id", "starts_on"],
    )
    op.create_index(
        "ix_meal_plan_items_plan_planned_for",
        "meal_plan_items",
        ["meal_plan_id", "planned_for"],
    )
    op.create_index(
        "ix_meal_plan_items_recipe_id",
        "meal_plan_items",
        ["recipe_id"],
    )
    op.create_index(
        "ix_meal_plan_items_recommendation_run_id",
        "meal_plan_items",
        ["recommendation_run_id"],
    )
    op.create_index(
        "ix_favorite_recipes_recipe_id",
        "favorite_recipes",
        ["recipe_id"],
    )
    op.create_index(
        "ix_favorite_menus_user_created_at",
        "favorite_menus",
        ["user_id", "created_at"],
    )
    op.create_index(
        "ix_favorite_menu_items_recipe_id",
        "favorite_menu_items",
        ["recipe_id"],
    )
    op.create_index(
        "ix_shopping_lists_user_status",
        "shopping_lists",
        ["user_id", "status"],
    )
    op.create_index(
        "ix_shopping_list_items_list_id",
        "shopping_list_items",
        ["shopping_list_id"],
    )
    op.create_index(
        "ix_shopping_list_items_master_ingredient_id",
        "shopping_list_items",
        ["master_ingredient_id"],
    )
    op.create_check_constraint(
        "shopping_item_custom_name_nonblank",
        "shopping_list_items",
        "custom_name IS NULL OR btrim(custom_name) <> ''",
    )
    op.execute(
        """
        CREATE FUNCTION enforce_meal_plan_item_date_within_plan()
        RETURNS trigger AS $$
        DECLARE
            plan_starts_on date;
            plan_ends_on date;
        BEGIN
            SELECT starts_on, ends_on
            INTO plan_starts_on, plan_ends_on
            FROM meal_plans
            WHERE id = NEW.meal_plan_id;

            IF NEW.planned_for < plan_starts_on OR NEW.planned_for > plan_ends_on THEN
                RAISE EXCEPTION 'meal-plan item date must be within its plan range'
                    USING ERRCODE = '23514';
            END IF;
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql
        """
    )
    op.execute(
        """
        CREATE TRIGGER meal_plan_items_date_within_plan
        BEFORE INSERT OR UPDATE OF meal_plan_id, planned_for ON meal_plan_items
        FOR EACH ROW EXECUTE FUNCTION enforce_meal_plan_item_date_within_plan()
        """
    )
    op.execute(
        """
        CREATE FUNCTION enforce_meal_plan_range_contains_items()
        RETURNS trigger AS $$
        BEGIN
            IF EXISTS (
                SELECT 1
                FROM meal_plan_items
                WHERE meal_plan_id = NEW.id
                  AND (planned_for < NEW.starts_on OR planned_for > NEW.ends_on)
            ) THEN
                RAISE EXCEPTION 'meal-plan range must contain all planned item dates'
                    USING ERRCODE = '23514';
            END IF;
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql
        """
    )
    op.execute(
        """
        CREATE TRIGGER meal_plans_range_contains_items
        BEFORE UPDATE OF starts_on, ends_on ON meal_plans
        FOR EACH ROW EXECUTE FUNCTION enforce_meal_plan_range_contains_items()
        """
    )


def downgrade() -> None:
    """Remove Phase 5 indexes and invariant guards in dependency-safe order."""
    op.execute("DROP TRIGGER IF EXISTS meal_plans_range_contains_items ON meal_plans")
    op.execute("DROP FUNCTION IF EXISTS enforce_meal_plan_range_contains_items()")
    op.execute(
        "DROP TRIGGER IF EXISTS meal_plan_items_date_within_plan ON meal_plan_items"
    )
    op.execute("DROP FUNCTION IF EXISTS enforce_meal_plan_item_date_within_plan()")
    op.drop_constraint(
        "shopping_item_custom_name_nonblank",
        "shopping_list_items",
        type_="check",
    )
    for index_name, table_name in (
        ("ix_shopping_list_items_master_ingredient_id", "shopping_list_items"),
        ("ix_shopping_list_items_list_id", "shopping_list_items"),
        ("ix_shopping_lists_user_status", "shopping_lists"),
        ("ix_favorite_menu_items_recipe_id", "favorite_menu_items"),
        ("ix_favorite_menus_user_created_at", "favorite_menus"),
        ("ix_favorite_recipes_recipe_id", "favorite_recipes"),
        ("ix_meal_plan_items_recommendation_run_id", "meal_plan_items"),
        ("ix_meal_plan_items_recipe_id", "meal_plan_items"),
        ("ix_meal_plan_items_plan_planned_for", "meal_plan_items"),
        ("ix_meal_plans_user_starts_on", "meal_plans"),
        ("ix_recommendation_items_recipe_id", "recommendation_items"),
        ("ix_recommendation_runs_user_created_at", "recommendation_runs"),
    ):
        op.drop_index(index_name, table_name=table_name)
