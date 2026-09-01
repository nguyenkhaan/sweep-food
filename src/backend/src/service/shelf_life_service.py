"""Pure shelf-life resolution and freshness calculation for inventory batches."""

from collections.abc import Iterable
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from uuid import UUID
from zoneinfo import ZoneInfo

from src.model.enum_model import ExpirationSource, ShelfLifeRuleScope, StorageMode

PRODUCT_TIMEZONE = ZoneInfo("Asia/Ho_Chi_Minh")


class FreshnessState(str, Enum):
    """Computed expiration state; this value is never persisted on a batch."""

    EXPIRED = "EXPIRED"
    EXPIRING_SOON = "EXPIRING_SOON"
    SAFE = "SAFE"
    UNKNOWN = "UNKNOWN"


@dataclass(frozen=True, slots=True)
class ShelfLifeRule:
    """The rule fields required for deterministic domain resolution."""

    scope: ShelfLifeRuleScope
    storage_mode: StorageMode
    default_days: int
    master_ingredient_id: UUID | None = None
    category_id: UUID | None = None


@dataclass(frozen=True, slots=True)
class ExpirationResolution:
    """The effective expiration and the rule used to derive it, if any."""

    expires_at: datetime | None
    source: ExpirationSource
    shelf_life_rule: ShelfLifeRule | None


@dataclass(frozen=True, slots=True)
class ExistingExpiration:
    """A batch expiration value and the authority that supplied it."""

    expires_at: datetime | None
    source: ExpirationSource


@dataclass(frozen=True, slots=True)
class ShelfLifeEstimationContext:
    """Inputs permitted by the documented shelf-life estimation fallback."""

    stored_at: datetime | None
    purchased_at: datetime | None
    master_ingredient_id: UUID | None
    category_id: UUID | None
    storage_mode: StorageMode


def resolve_shelf_life_rule(
    rules: Iterable[ShelfLifeRule],
    *,
    master_ingredient_id: UUID | None,
    category_id: UUID | None,
    storage_mode: StorageMode,
) -> ShelfLifeRule | None:
    """Resolve an exact-storage rule, preferring ingredient over category.

    A duplicate matching rule is invalid input.  The database prevents it,
    but rejecting it here keeps the pure service deterministic for callers
    that have not yet persisted their rules.
    """
    ingredient_matches: list[ShelfLifeRule] = []
    category_matches: list[ShelfLifeRule] = []
    for rule in rules:
        _validate_rule(rule)
        if rule.storage_mode is not storage_mode:
            continue
        if (
            rule.scope is ShelfLifeRuleScope.INGREDIENT
            and rule.master_ingredient_id == master_ingredient_id
            and master_ingredient_id is not None
        ):
            ingredient_matches.append(rule)
        elif (
            rule.scope is ShelfLifeRuleScope.CATEGORY
            and rule.category_id == category_id
            and category_id is not None
        ):
            category_matches.append(rule)
    return _one_matching_rule(ingredient_matches) or _one_matching_rule(
        category_matches,
    )


def resolve_expiration(
    existing: ExistingExpiration,
    context: ShelfLifeEstimationContext,
    rules: Iterable[ShelfLifeRule],
) -> ExpirationResolution:
    """Preserve authoritative dates or estimate from the documented fallback.

    Manufacturer and user-override dates cannot be recalculated.  For an
    unknown or previous estimate, use an ingredient rule first, then a
    category rule, only for the requested storage mode, and only from
    ``stored_at`` or (when absent) ``purchased_at``.
    """
    _require_aware_optional(existing.expires_at, "existing.expires_at")
    _require_aware_optional(context.stored_at, "context.stored_at")
    _require_aware_optional(context.purchased_at, "context.purchased_at")
    if existing.source in {
        ExpirationSource.MANUFACTURER,
        ExpirationSource.USER_OVERRIDE,
    }:
        if existing.expires_at is None:
            raise ValueError(f"{existing.source.value} requires expires_at")
        return ExpirationResolution(existing.expires_at, existing.source, None)

    base_at = context.stored_at or context.purchased_at
    if base_at is None:
        return ExpirationResolution(None, ExpirationSource.UNKNOWN, None)
    rule = resolve_shelf_life_rule(
        rules,
        master_ingredient_id=context.master_ingredient_id,
        category_id=context.category_id,
        storage_mode=context.storage_mode,
    )
    if rule is None:
        return ExpirationResolution(None, ExpirationSource.UNKNOWN, None)
    return ExpirationResolution(
        expires_at=base_at + timedelta(days=rule.default_days),
        source=ExpirationSource.ESTIMATED,
        shelf_life_rule=rule,
    )


def calculate_freshness(
    expires_at: datetime | None,
    *,
    now: datetime,
    warning_days: int,
) -> FreshnessState:
    """Classify freshness in the fixed product timezone at exact boundaries."""
    _require_aware(now, "now")
    _require_aware_optional(expires_at, "expires_at")
    if isinstance(warning_days, bool) or warning_days < 0:
        raise ValueError("warning_days must be a non-negative integer")
    if expires_at is None:
        return FreshnessState.UNKNOWN

    local_now = now.astimezone(PRODUCT_TIMEZONE)
    local_expiration = expires_at.astimezone(PRODUCT_TIMEZONE)
    if local_expiration < local_now:
        return FreshnessState.EXPIRED
    if local_expiration <= local_now + timedelta(days=warning_days):
        return FreshnessState.EXPIRING_SOON
    return FreshnessState.SAFE


def _one_matching_rule(matches: list[ShelfLifeRule]) -> ShelfLifeRule | None:
    """Return one unambiguous rule, rejecting invalid duplicate domain input."""
    if len(matches) > 1:
        raise ValueError("Multiple shelf-life rules match one target and storage mode")
    return matches[0] if matches else None


def _validate_rule(rule: ShelfLifeRule) -> None:
    """Defend the service boundary with the documented rule invariants."""
    if isinstance(rule.default_days, bool) or rule.default_days < 0:
        raise ValueError("default_days must be a non-negative integer")
    ingredient_targeted = rule.master_ingredient_id is not None
    category_targeted = rule.category_id is not None
    if ingredient_targeted == category_targeted:
        raise ValueError("Shelf-life rules require exactly one target")
    if (rule.scope is ShelfLifeRuleScope.INGREDIENT) != ingredient_targeted:
        raise ValueError("Shelf-life rule scope must match its target")


def _require_aware_optional(value: datetime | None, name: str) -> None:
    """Require timezone-aware optional timestamps at the service boundary."""
    if value is not None:
        _require_aware(value, name)


def _require_aware(value: datetime, name: str) -> None:
    """Reject naive timestamps instead of silently assigning a timezone."""
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError(f"{name} must be timezone-aware")
