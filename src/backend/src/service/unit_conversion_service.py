"""Exact conversions between documented compatible measurement units."""

from decimal import Decimal
from enum import Enum

from src.model.enum_model import MeasurementUnit


class UnitGroup(str, Enum):
    """Groups with a common base unit and exact conversion factor."""

    MASS = "MASS"
    VOLUME = "VOLUME"


class IncompatibleUnitError(ValueError):
    """Raised when a quantity has no documented automatic conversion."""


_UNIT_GROUPS: dict[MeasurementUnit, UnitGroup] = {
    MeasurementUnit.GRAM: UnitGroup.MASS,
    MeasurementUnit.KG: UnitGroup.MASS,
    MeasurementUnit.ML: UnitGroup.VOLUME,
    MeasurementUnit.LITER: UnitGroup.VOLUME,
}
_TO_BASE_UNIT: dict[MeasurementUnit, Decimal] = {
    MeasurementUnit.GRAM: Decimal(1),
    MeasurementUnit.KG: Decimal(1000),
    MeasurementUnit.ML: Decimal(1),
    MeasurementUnit.LITER: Decimal(1000),
}


def unit_group(unit: MeasurementUnit) -> UnitGroup | None:
    """Return the automatic-conversion group for ``unit``, if one exists."""
    return _UNIT_GROUPS.get(unit)


def are_units_compatible(
    source_unit: MeasurementUnit,
    target_unit: MeasurementUnit,
) -> bool:
    """Return whether the documented conversion contract permits the pair."""
    if source_unit is target_unit:
        return True
    source_group = unit_group(source_unit)
    return source_group is not None and source_group is unit_group(target_unit)


def convert_quantity(
    quantity: Decimal,
    source_unit: MeasurementUnit,
    target_unit: MeasurementUnit,
) -> Decimal:
    """Convert a Decimal quantity exactly, rejecting unsupported unit pairs.

    Float inputs are intentionally rejected.  Constructing a Decimal from a
    binary float would introduce an unrequested approximation into catalog
    quantities that are otherwise represented as Decimal values.
    """
    if not isinstance(quantity, Decimal):
        raise TypeError("quantity must be a Decimal")
    if source_unit is target_unit:
        return quantity
    if not are_units_compatible(source_unit, target_unit):
        raise IncompatibleUnitError(
            f"Cannot convert {source_unit.value} to {target_unit.value}",
        )
    return quantity * _TO_BASE_UNIT[source_unit] / _TO_BASE_UNIT[target_unit]
