"""Harden catalog and recipe constraints and numeric precision.

Revision ID: b7f3e0a1c2d4
Revises: 446cf3ac3439
Create Date: 2026-08-31 00:00:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "b7f3e0a1c2d4"
down_revision: str | Sequence[str] | None = "446cf3ac3439"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

_MASTER_NUTRITION_COLUMNS = (
    "calories",
    "protein_g",
    "fat_g",
    "carbs_g",
    "sugar_g",
    "sodium_mg",
)
_RECIPE_NUTRITION_COLUMNS = (
    "total_calories",
    "total_protein_g",
    "total_fat_g",
    "total_carbs_g",
    "total_sugar_g",
)


def _assert_case_insensitive_uniqueness(table_name: str, column_name: str) -> None:
    """Fail before DDL when a lower-case index would reject existing rows."""
    op.execute(
        sa.text(
            f"""
            DO $$
            BEGIN
                IF EXISTS (
                    SELECT 1
                    FROM {table_name}
                    GROUP BY lower({column_name})
                    HAVING count(*) > 1
                ) THEN
                    RAISE EXCEPTION
                        'Cannot add case-insensitive uniqueness to %.%: duplicates exist',
                        '{table_name}',
                        '{column_name}';
                END IF;
            END
            $$;
            """,
        ),
    )


def _assert_master_ingredient_uniqueness() -> None:
    """Fail before DDL when a category has case-insensitive ingredient duplicates."""
    op.execute(
        sa.text(
            """
            DO $$
            BEGIN
                IF EXISTS (
                    SELECT 1
                    FROM master_ingredients
                    GROUP BY category_id, lower(name)
                    HAVING count(*) > 1
                ) THEN
                    RAISE EXCEPTION
                        'Cannot add case-insensitive master ingredient uniqueness: '
                        'duplicates exist';
                END IF;
            END
            $$;
            """,
        ),
    )


def _assert_lossless_numeric_conversion(
    table_name: str,
    column_name: str,
    scale: int,
    upper_bound: int,
) -> None:
    """Reject non-finite, out-of-range, or rounding-required float values."""
    op.execute(
        sa.text(
            f"""
            DO $$
            BEGIN
                IF EXISTS (
                    SELECT 1
                    FROM {table_name}
                    WHERE {column_name} IS NOT NULL
                      AND (
                          {column_name} IN (
                              'NaN'::double precision,
                              'Infinity'::double precision,
                              '-Infinity'::double precision
                          )
                          OR abs({column_name}) >= {upper_bound}
                          OR {column_name} IS DISTINCT FROM
                              round({column_name}::numeric, {scale})::double precision
                      )
                ) THEN
                    RAISE EXCEPTION
                        'Cannot convert %.% to NUMERIC: a value exceeds precision or scale',
                        '{table_name}',
                        '{column_name}';
                END IF;
            END
            $$;
            """,
        ),
    )


def _convert_to_numeric(
    table_name: str,
    column_name: str,
    precision: int,
    scale: int,
    nullable: bool,
) -> None:
    """Convert a float column after the upgrade preflight has passed."""
    op.alter_column(
        table_name,
        column_name,
        existing_type=sa.Float(),
        type_=sa.Numeric(precision, scale),
        existing_nullable=nullable,
        postgresql_using=f"{column_name}::numeric({precision}, {scale})",
    )


def _convert_to_float(
    table_name: str,
    column_name: str,
    precision: int,
    scale: int,
    nullable: bool,
) -> None:
    """Restore the preceding PostgreSQL double-precision storage type."""
    op.alter_column(
        table_name,
        column_name,
        existing_type=sa.Numeric(precision, scale),
        type_=sa.Float(),
        existing_nullable=nullable,
        postgresql_using=f"{column_name}::double precision",
    )


def upgrade() -> None:
    """Apply catalog integrity and Numeric precision without mutating existing data."""
    _assert_case_insensitive_uniqueness("ingredient_categories", "name")
    _assert_case_insensitive_uniqueness("recipes", "name")
    _assert_master_ingredient_uniqueness()
    for column_name in _MASTER_NUTRITION_COLUMNS:
        _assert_lossless_numeric_conversion(
            "master_ingredients",
            column_name,
            3,
            10**9,
        )
    _assert_lossless_numeric_conversion("recipes", "default_servings", 2, 10**4)
    for column_name in _RECIPE_NUTRITION_COLUMNS:
        _assert_lossless_numeric_conversion("recipes", column_name, 3, 10**9)
    _assert_lossless_numeric_conversion(
        "recipe_ingredients",
        "required_quantity",
        3,
        10**9,
    )

    op.drop_constraint("ingredient_categories_name_key", "ingredient_categories")
    op.drop_constraint("recipes_name_key", "recipes")
    op.create_index(
        "uq_ingredient_categories_name_lower",
        "ingredient_categories",
        [sa.text("lower(name)")],
        unique=True,
    )
    op.create_index(
        "uq_recipes_name_lower",
        "recipes",
        [sa.text("lower(name)")],
        unique=True,
    )
    op.create_index(
        "ix_master_ingredients_category_id",
        "master_ingredients",
        ["category_id"],
    )
    op.create_index(
        "uq_master_ingredients_category_name_lower",
        "master_ingredients",
        ["category_id", sa.text("lower(name)")],
        unique=True,
    )
    op.create_index(
        "ix_recipe_ingredients_recipe_id",
        "recipe_ingredients",
        ["recipe_id"],
    )
    op.create_index(
        "ix_recipe_ingredients_master_ingredient_id",
        "recipe_ingredients",
        ["master_ingredient_id"],
    )

    op.create_check_constraint(
        "recipe_default_servings_positive",
        "recipes",
        "default_servings > 0",
    )
    op.create_check_constraint(
        "shelf_life_rule_min_days_nonnegative",
        "shelf_life_rules",
        "min_days >= 0",
    )
    op.create_check_constraint(
        "shelf_life_rule_max_days_nonnegative",
        "shelf_life_rules",
        "max_days >= 0",
    )
    op.create_check_constraint(
        "shelf_life_rule_default_days_nonnegative",
        "shelf_life_rules",
        "default_days >= 0",
    )
    op.create_check_constraint(
        "shelf_life_rule_max_days_at_least_min_days",
        "shelf_life_rules",
        "max_days >= min_days",
    )
    op.create_check_constraint(
        "shelf_life_rule_default_days_in_range",
        "shelf_life_rules",
        "default_days BETWEEN min_days AND max_days",
    )
    op.create_check_constraint(
        "shelf_life_rule_scope_matches_target",
        "shelf_life_rules",
        "(scope = 'INGREDIENT'::shelf_life_rule_scope "
        "AND master_ingredient_id IS NOT NULL AND category_id IS NULL) "
        "OR (scope = 'CATEGORY'::shelf_life_rule_scope "
        "AND category_id IS NOT NULL AND master_ingredient_id IS NULL)",
    )

    for column_name in _MASTER_NUTRITION_COLUMNS:
        _convert_to_numeric("master_ingredients", column_name, 12, 3, True)
    _convert_to_numeric("recipes", "default_servings", 6, 2, False)
    for column_name in _RECIPE_NUTRITION_COLUMNS:
        _convert_to_numeric("recipes", column_name, 12, 3, True)
    _convert_to_numeric("recipe_ingredients", "required_quantity", 12, 3, False)


def downgrade() -> None:
    """Restore the previous catalog and recipe schema types and constraints."""
    _convert_to_float("recipe_ingredients", "required_quantity", 12, 3, False)
    for column_name in _RECIPE_NUTRITION_COLUMNS:
        _convert_to_float("recipes", column_name, 12, 3, True)
    _convert_to_float("recipes", "default_servings", 6, 2, False)
    for column_name in _MASTER_NUTRITION_COLUMNS:
        _convert_to_float("master_ingredients", column_name, 12, 3, True)

    op.drop_constraint(
        "shelf_life_rule_scope_matches_target",
        "shelf_life_rules",
        type_="check",
    )
    op.drop_constraint(
        "shelf_life_rule_default_days_in_range",
        "shelf_life_rules",
        type_="check",
    )
    op.drop_constraint(
        "shelf_life_rule_max_days_at_least_min_days",
        "shelf_life_rules",
        type_="check",
    )
    op.drop_constraint(
        "shelf_life_rule_default_days_nonnegative",
        "shelf_life_rules",
        type_="check",
    )
    op.drop_constraint(
        "shelf_life_rule_max_days_nonnegative",
        "shelf_life_rules",
        type_="check",
    )
    op.drop_constraint(
        "shelf_life_rule_min_days_nonnegative",
        "shelf_life_rules",
        type_="check",
    )
    op.drop_constraint("recipe_default_servings_positive", "recipes", type_="check")

    op.drop_index(
        "ix_recipe_ingredients_master_ingredient_id",
        table_name="recipe_ingredients",
    )
    op.drop_index("ix_recipe_ingredients_recipe_id", table_name="recipe_ingredients")
    op.drop_index(
        "uq_master_ingredients_category_name_lower",
        table_name="master_ingredients",
    )
    op.drop_index("ix_master_ingredients_category_id", table_name="master_ingredients")
    op.drop_index("uq_recipes_name_lower", table_name="recipes")
    op.drop_index(
        "uq_ingredient_categories_name_lower",
        table_name="ingredient_categories",
    )
    op.create_unique_constraint("recipes_name_key", "recipes", ["name"])
    op.create_unique_constraint(
        "ingredient_categories_name_key",
        "ingredient_categories",
        ["name"],
    )
