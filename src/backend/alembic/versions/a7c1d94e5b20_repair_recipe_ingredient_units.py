"""repair recipe ingredient units and seasoning flags

Revision ID: a7c1d94e5b20
Revises: e2b4f68a10cd
Create Date: 2026-10-22
"""

from collections.abc import Sequence

from alembic import op

revision: str = "a7c1d94e5b20"
down_revision: str | Sequence[str] | None = "e2b4f68a10cd"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

_NUMERIC = r"'^[0-9]+(\.[0-9]+)?$'"


def upgrade() -> None:
    """Store unmeasurable counts by estimated grams and flag seasoning lines."""
    op.execute(
        f"""
        UPDATE recipe_ingredients
        SET required_quantity = (ai_attributes->>'estimated_weight_g')::numeric,
            unit = 'GRAM'
        WHERE unit = 'OTHER'
          AND ai_attributes->>'estimated_weight_g' ~ {_NUMERIC}
          AND (ai_attributes->>'estimated_weight_g')::numeric > 0
        """
    )
    op.execute(
        """
        UPDATE recipe_ingredients
        SET is_optional = true
        WHERE lower(ai_attributes->>'ingredient_role') = 'seasoning'
        """
    )


def downgrade() -> None:
    """Data repair is not reversible: original placeholder quantities are lost."""
