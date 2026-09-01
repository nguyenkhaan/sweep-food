"""Unit tests for exact compatible-unit conversions."""

from decimal import Decimal

import pytest

from src.model.enum_model import MeasurementUnit
from src.service.unit_conversion_service import (
    IncompatibleUnitError,
    are_units_compatible,
    convert_quantity,
)


@pytest.mark.parametrize(
    ("quantity", "source_unit", "target_unit", "expected"),
    [
        (
            Decimal("1.234"),
            MeasurementUnit.KG,
            MeasurementUnit.GRAM,
            Decimal("1234.000"),
        ),
        (
            Decimal("1234.000"),
            MeasurementUnit.GRAM,
            MeasurementUnit.KG,
            Decimal("1.234"),
        ),
        (
            Decimal("1.250"),
            MeasurementUnit.LITER,
            MeasurementUnit.ML,
            Decimal("1250.000"),
        ),
        (
            Decimal("1250.000"),
            MeasurementUnit.ML,
            MeasurementUnit.LITER,
            Decimal("1.250"),
        ),
    ],
)
def test_convert_quantity_preserves_exact_decimal_values(
    quantity: Decimal,
    source_unit: MeasurementUnit,
    target_unit: MeasurementUnit,
    expected: Decimal,
) -> None:
    """Mass and volume conversions retain Decimal precision and scale."""
    assert convert_quantity(quantity, source_unit, target_unit) == expected


def test_convert_quantity_rejects_incompatible_groups() -> None:
    """Mass, volume, and unsupported units never silently cross-convert."""
    assert not are_units_compatible(MeasurementUnit.GRAM, MeasurementUnit.LITER)
    assert not are_units_compatible(MeasurementUnit.PIECE, MeasurementUnit.PACK)
    with pytest.raises(IncompatibleUnitError, match="Cannot convert GRAM to LITER"):
        convert_quantity(Decimal(1), MeasurementUnit.GRAM, MeasurementUnit.LITER)


def test_convert_quantity_rejects_binary_float_input() -> None:
    """Float input cannot silently alter Decimal catalog quantities."""
    with pytest.raises(TypeError, match="quantity must be a Decimal"):
        convert_quantity(1.1, MeasurementUnit.GRAM, MeasurementUnit.KG)  # type: ignore[arg-type]
