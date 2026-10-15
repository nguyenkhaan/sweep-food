"""Unit checks for the versioned FreshCheck catalog mapping schema."""

from sqlalchemy import ForeignKeyConstraint, UniqueConstraint

from src.model.freshcheck_mapping_model import MasterIngredientFreshCheckMappingModel


def test_mapping_model_scopes_catalog_links_to_a_freshcheck_version() -> None:
    """A master ingredient has one reviewed mapping per KB version."""
    table = MasterIngredientFreshCheckMappingModel.__table__
    composite_foreign_keys = {
        foreign_key.name: tuple(foreign_key.column_keys)
        for foreign_key in table.constraints
        if isinstance(foreign_key, ForeignKeyConstraint)
    }
    unique_constraints = {
        tuple(constraint.columns.keys())
        for constraint in table.constraints
        if isinstance(constraint, UniqueConstraint)
    }

    assert composite_foreign_keys[
        "fk_master_ingredient_freshcheck_mappings_ingredient"
    ] == ("kb_version", "freshcheck_ingredient_id")
    assert ("master_ingredient_id", "kb_version") in unique_constraints
    assert table.c.master_ingredient_id.nullable is False
    assert table.c.kb_version.nullable is False
    assert table.c.freshcheck_ingredient_id.nullable is False
