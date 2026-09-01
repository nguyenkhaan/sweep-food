"""Unit tests for shelf-life resolution and freshness calculation."""

from datetime import UTC, datetime, timedelta
from uuid import UUID
from zoneinfo import ZoneInfo

import pytest

from src.model.enum_model import ExpirationSource, ShelfLifeRuleScope, StorageMode
from src.service.shelf_life_service import (
    PRODUCT_TIMEZONE,
    ExistingExpiration,
    ExpirationResolution,
    FreshnessState,
    ShelfLifeEstimationContext,
    ShelfLifeRule,
    calculate_freshness,
    resolve_expiration,
    resolve_shelf_life_rule,
)

INGREDIENT_ID = UUID("00000000-0000-0000-0000-000000000001")
CATEGORY_ID = UUID("00000000-0000-0000-0000-000000000002")
OTHER_INGREDIENT_ID = UUID("00000000-0000-0000-0000-000000000003")


def _ingredient_rule(
    *,
    storage_mode: StorageMode = StorageMode.REFRIGERATED,
    default_days: int = 2,
) -> ShelfLifeRule:
    return ShelfLifeRule(
        scope=ShelfLifeRuleScope.INGREDIENT,
        master_ingredient_id=INGREDIENT_ID,
        storage_mode=storage_mode,
        default_days=default_days,
    )


def _category_rule(
    *,
    storage_mode: StorageMode = StorageMode.REFRIGERATED,
    default_days: int = 5,
) -> ShelfLifeRule:
    return ShelfLifeRule(
        scope=ShelfLifeRuleScope.CATEGORY,
        category_id=CATEGORY_ID,
        storage_mode=storage_mode,
        default_days=default_days,
    )


def test_ingredient_rule_overrides_category_rule_for_matching_storage_mode() -> None:
    """Ingredient rules take the documented precedence over category rules."""
    rule = resolve_shelf_life_rule(
        [_category_rule(), _ingredient_rule()],
        master_ingredient_id=INGREDIENT_ID,
        category_id=CATEGORY_ID,
        storage_mode=StorageMode.REFRIGERATED,
    )
    assert rule == _ingredient_rule()


def test_category_rule_is_used_when_no_ingredient_rule_matches() -> None:
    """Category fallback remains available for another ingredient in that category."""
    rule = resolve_shelf_life_rule(
        [_ingredient_rule(), _category_rule()],
        master_ingredient_id=OTHER_INGREDIENT_ID,
        category_id=CATEGORY_ID,
        storage_mode=StorageMode.REFRIGERATED,
    )
    assert rule == _category_rule()


def test_storage_mode_must_match_exactly() -> None:
    """A refrigerated rule must not estimate a frozen batch."""
    resolution = resolve_expiration(
        ExistingExpiration(None, ExpirationSource.UNKNOWN),
        ShelfLifeEstimationContext(
            stored_at=datetime(2026, 9, 1, 8, tzinfo=UTC),
            purchased_at=datetime(2026, 8, 31, 8, tzinfo=UTC),
            master_ingredient_id=INGREDIENT_ID,
            category_id=CATEGORY_ID,
            storage_mode=StorageMode.FROZEN,
        ),
        rules=[_ingredient_rule(), _category_rule()],
    )
    assert resolution.expires_at is None
    assert resolution.source is ExpirationSource.UNKNOWN
    assert resolution.shelf_life_rule is None


def test_manufacturer_expiration_is_never_replaced_by_estimation() -> None:
    """Manufacturer input remains authoritative even when a rule is present."""
    manufacturer_expiration = datetime(2026, 9, 30, 17, 0, tzinfo=UTC)
    resolution = resolve_expiration(
        ExistingExpiration(manufacturer_expiration, ExpirationSource.MANUFACTURER),
        ShelfLifeEstimationContext(
            stored_at=datetime(2026, 9, 1, 8, tzinfo=UTC),
            purchased_at=None,
            master_ingredient_id=INGREDIENT_ID,
            category_id=CATEGORY_ID,
            storage_mode=StorageMode.REFRIGERATED,
        ),
        rules=[_ingredient_rule(default_days=2)],
    )
    assert resolution.expires_at == manufacturer_expiration
    assert resolution.source is ExpirationSource.MANUFACTURER
    assert resolution.shelf_life_rule is None


def test_estimation_uses_stored_at_before_purchased_at() -> None:
    """The documented stored-at then purchased-at fallback is deterministic."""
    stored_at = datetime(2026, 9, 3, 9, tzinfo=UTC)
    resolution = resolve_expiration(
        ExistingExpiration(None, ExpirationSource.UNKNOWN),
        ShelfLifeEstimationContext(
            stored_at=stored_at,
            purchased_at=datetime(2026, 9, 1, 9, tzinfo=UTC),
            master_ingredient_id=INGREDIENT_ID,
            category_id=CATEGORY_ID,
            storage_mode=StorageMode.REFRIGERATED,
        ),
        rules=[_ingredient_rule(default_days=2)],
    )
    assert resolution.expires_at == stored_at + timedelta(days=2)
    assert resolution.source is ExpirationSource.ESTIMATED


def test_no_rule_or_base_date_produces_unknown_expiration() -> None:
    """Unavailable required estimation data leaves expiration unknown."""
    no_rule = resolve_expiration(
        ExistingExpiration(None, ExpirationSource.UNKNOWN),
        ShelfLifeEstimationContext(
            stored_at=datetime(2026, 9, 1, 9, tzinfo=UTC),
            purchased_at=None,
            master_ingredient_id=INGREDIENT_ID,
            category_id=CATEGORY_ID,
            storage_mode=StorageMode.REFRIGERATED,
        ),
        rules=[],
    )
    no_base_date = resolve_expiration(
        ExistingExpiration(None, ExpirationSource.UNKNOWN),
        ShelfLifeEstimationContext(
            stored_at=None,
            purchased_at=None,
            master_ingredient_id=INGREDIENT_ID,
            category_id=CATEGORY_ID,
            storage_mode=StorageMode.REFRIGERATED,
        ),
        rules=[_ingredient_rule()],
    )
    assert (
        no_rule
        == no_base_date
        == ExpirationResolution(
            None,
            ExpirationSource.UNKNOWN,
            None,
        )
    )


@pytest.mark.parametrize(
    ("expires_at", "expected"),
    [
        (
            datetime(2026, 9, 1, 7, 59, 59, tzinfo=PRODUCT_TIMEZONE),
            FreshnessState.EXPIRED,
        ),
        (
            datetime(2026, 9, 1, 8, 0, tzinfo=PRODUCT_TIMEZONE),
            FreshnessState.EXPIRING_SOON,
        ),
        (
            datetime(2026, 9, 4, 8, 0, tzinfo=PRODUCT_TIMEZONE),
            FreshnessState.EXPIRING_SOON,
        ),
        (
            datetime(2026, 9, 4, 8, 0, 1, tzinfo=PRODUCT_TIMEZONE),
            FreshnessState.SAFE,
        ),
        (None, FreshnessState.UNKNOWN),
    ],
)
def test_freshness_uses_documented_boundaries(
    expires_at: datetime | None,
    expected: FreshnessState,
) -> None:
    """Past, exact-warning-window, future, and absent dates are distinct."""
    assert (
        calculate_freshness(
            expires_at,
            now=datetime(2026, 9, 1, 8, tzinfo=PRODUCT_TIMEZONE),
            warning_days=3,
        )
        is expected
    )


def test_freshness_converts_utc_instants_to_asia_ho_chi_minh() -> None:
    """An equivalent UTC instant observes the same local configured window."""
    assert (
        calculate_freshness(
            datetime(2026, 9, 4, 1, tzinfo=UTC),
            now=datetime(2026, 9, 1, 1, tzinfo=UTC),
            warning_days=3,
        )
        is FreshnessState.EXPIRING_SOON
    )


def test_freshness_rejects_naive_timestamps() -> None:
    """Timezone assumptions are never made silently at the domain boundary."""
    with pytest.raises(ValueError, match="now must be timezone-aware"):
        naive_now = datetime(2026, 9, 1, 8, tzinfo=UTC).replace(tzinfo=None)
        calculate_freshness(
            None,
            now=naive_now,
            warning_days=3,
        )


def test_fixed_product_timezone_is_asia_ho_chi_minh() -> None:
    """Keep the product timezone explicit and insulated from host settings."""
    assert PRODUCT_TIMEZONE == ZoneInfo("Asia/Ho_Chi_Minh")
