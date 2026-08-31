"""Reusable FEFO allocation and compatible-unit conversion logic."""

from dataclasses import dataclass
from datetime import UTC, datetime
from uuid import UUID

from src.model.enum_model import MeasurementUnit

_MASS_UNITS_IN_GRAMS: dict[MeasurementUnit, float] = {
    MeasurementUnit.GRAM: 1.0,
    MeasurementUnit.KG: 1000.0,
}
_VOLUME_UNITS_IN_MILLILITERS: dict[MeasurementUnit, float] = {
    MeasurementUnit.ML: 1.0,
    MeasurementUnit.LITER: 1000.0,
}
_QUANTITY_EPSILON = 1e-9


@dataclass(frozen=True, slots=True)
class FEFOCandidate:
    """A batch considered for one recipe-ingredient allocation."""

    batch_id: UUID
    current_quantity: float
    unit: MeasurementUnit
    expires_at: datetime | None
    created_at: datetime


@dataclass(frozen=True, slots=True)
class FEFOAllocation:
    """A proposed deduction expressed in both recipe and batch units."""

    batch_id: UUID
    recipe_quantity: float
    recipe_unit: MeasurementUnit
    batch_quantity: float
    batch_unit: MeasurementUnit
    expires_at: datetime | None


@dataclass(frozen=True, slots=True)
class FEFOAllocationResult:
    """An allocation proposal and batches excluded from it with an explanation."""

    allocations: list[FEFOAllocation]
    missing_quantity: float
    expired_candidates: list[FEFOCandidate]
    unknown_expiration_candidates: list[FEFOCandidate]
    incompatible_candidates: list[FEFOCandidate]


class FEFOService:
    """Allocate compatible active batches by first-expired, first-out order."""

    def allocate(
        self,
        required_quantity: float,
        required_unit: MeasurementUnit,
        candidates: list[FEFOCandidate],
        now: datetime,
    ) -> FEFOAllocationResult:
        """Return a read-only allocation proposal for one required ingredient."""
        expired_candidates, non_expired_candidates = self._split_expired(
            candidates,
            now,
        )
        compatible_candidates, incompatible_candidates = self._split_compatible(
            non_expired_candidates,
            required_unit,
        )
        unknown_expiration_candidates = [
            candidate
            for candidate in compatible_candidates
            if candidate.expires_at is None
        ]
        allocations, missing_quantity = self._allocate_compatible_candidates(
            required_quantity,
            required_unit,
            compatible_candidates,
        )
        return FEFOAllocationResult(
            allocations=allocations,
            missing_quantity=missing_quantity,
            expired_candidates=expired_candidates,
            unknown_expiration_candidates=unknown_expiration_candidates,
            incompatible_candidates=incompatible_candidates,
        )

    def _split_expired(
        self,
        candidates: list[FEFOCandidate],
        now: datetime,
    ) -> tuple[list[FEFOCandidate], list[FEFOCandidate]]:
        expired: list[FEFOCandidate] = []
        non_expired: list[FEFOCandidate] = []
        for candidate in candidates:
            if candidate.expires_at is not None and candidate.expires_at < now:
                expired.append(candidate)
            else:
                non_expired.append(candidate)
        return expired, non_expired

    def _split_compatible(
        self,
        candidates: list[FEFOCandidate],
        required_unit: MeasurementUnit,
    ) -> tuple[list[FEFOCandidate], list[FEFOCandidate]]:
        compatible: list[FEFOCandidate] = []
        incompatible: list[FEFOCandidate] = []
        for candidate in candidates:
            if are_units_compatible(candidate.unit, required_unit):
                compatible.append(candidate)
            else:
                incompatible.append(candidate)
        return compatible, incompatible

    def _allocate_compatible_candidates(
        self,
        required_quantity: float,
        required_unit: MeasurementUnit,
        candidates: list[FEFOCandidate],
    ) -> tuple[list[FEFOAllocation], float]:
        remaining_quantity = required_quantity
        allocations: list[FEFOAllocation] = []
        for candidate in sorted(candidates, key=self._candidate_sort_key):
            if remaining_quantity <= _QUANTITY_EPSILON:
                break
            available_recipe_quantity = convert_quantity(
                candidate.current_quantity,
                candidate.unit,
                required_unit,
            )
            allocated_recipe_quantity = min(
                remaining_quantity,
                available_recipe_quantity,
            )
            if allocated_recipe_quantity <= _QUANTITY_EPSILON:
                continue
            allocations.append(
                FEFOAllocation(
                    batch_id=candidate.batch_id,
                    recipe_quantity=allocated_recipe_quantity,
                    recipe_unit=required_unit,
                    batch_quantity=convert_quantity(
                        allocated_recipe_quantity,
                        required_unit,
                        candidate.unit,
                    ),
                    batch_unit=candidate.unit,
                    expires_at=candidate.expires_at,
                )
            )
            remaining_quantity -= allocated_recipe_quantity
        return allocations, max(0.0, remaining_quantity)

    @staticmethod
    def _candidate_sort_key(
        candidate: FEFOCandidate,
    ) -> tuple[bool, datetime, datetime]:
        fallback_expiry = datetime.max.replace(tzinfo=UTC)
        return (
            candidate.expires_at is None,
            candidate.expires_at or fallback_expiry,
            candidate.created_at,
        )


def are_units_compatible(
    source_unit: MeasurementUnit,
    target_unit: MeasurementUnit,
) -> bool:
    """Return whether quantities convert without a custom ingredient factor."""
    if source_unit == target_unit:
        return True
    return (
        source_unit in _MASS_UNITS_IN_GRAMS and target_unit in _MASS_UNITS_IN_GRAMS
    ) or (
        source_unit in _VOLUME_UNITS_IN_MILLILITERS
        and target_unit in _VOLUME_UNITS_IN_MILLILITERS
    )


def convert_quantity(
    quantity: float,
    source_unit: MeasurementUnit,
    target_unit: MeasurementUnit,
) -> float:
    """Convert mass or volume quantities and reject incompatible unit groups."""
    if source_unit == target_unit:
        return quantity
    if source_unit in _MASS_UNITS_IN_GRAMS and target_unit in _MASS_UNITS_IN_GRAMS:
        return (
            quantity
            * _MASS_UNITS_IN_GRAMS[source_unit]
            / _MASS_UNITS_IN_GRAMS[target_unit]
        )
    if (
        source_unit in _VOLUME_UNITS_IN_MILLILITERS
        and target_unit in _VOLUME_UNITS_IN_MILLILITERS
    ):
        return (
            quantity
            * _VOLUME_UNITS_IN_MILLILITERS[source_unit]
            / _VOLUME_UNITS_IN_MILLILITERS[target_unit]
        )
    raise ValueError(f"Cannot convert {source_unit.value} to {target_unit.value}")
