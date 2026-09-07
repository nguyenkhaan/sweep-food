"""Metadata checks for the immutable waste-reduction evidence table."""

from typing import cast

from sqlalchemy import Table

from src.model.waste_reduction_event_model import WasteReductionEventModel


def test_waste_reduction_event_metadata_has_the_required_evidence_keys() -> None:
    """The model keeps one snapshot per ledger and the period query index."""
    table = cast(Table, WasteReductionEventModel.__table__)
    unique_constraints = {constraint.name for constraint in table.constraints}
    index_names = {index.name for index in table.indexes}

    assert "uq_waste_event_ledger" in unique_constraints
    assert "ix_waste_events_user_consumed_at" in index_names
    assert table.c.mass_kg.nullable is True
    assert table.c.expires_at_snapshot.nullable is True
