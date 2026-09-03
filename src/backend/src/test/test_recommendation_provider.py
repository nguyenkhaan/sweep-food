"""Focused Task 5.2 coverage for deterministic rule-based recommendations."""

from collections.abc import Sequence
from datetime import UTC, datetime, timedelta
from decimal import Decimal
from typing import cast
from uuid import UUID

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.model.enum_model import (
    ExpirationSource,
    InventoryBatchStatus,
    InventoryBatchType,
    InventorySource,
    MeasurementUnit,
    RecommendationProviderType,
    StorageMode,
)
from src.model.inventory_batch_model import InventoryBatchModel
from src.model.master_ingredient_model import MasterIngredientModel
from src.model.recipe_ingredient_model import RecipeIngredientModel
from src.model.recipe_model import RecipeModel
from src.model.user_model import UserModel
from src.module.recommendations.recommendation_provider import (
    InventorySnapshot,
    InventorySnapshotBatch,
    RankedRecommendation,
    RecipeIngredientCandidate,
    RecommendationCandidate,
    RecommendationCriteria,
    RecommendationProvider,
    RecommendationRequest,
    RuleBasedRecommendationProvider,
    UserRecommendationContext,
)
from src.module.recommendations.recommendation_service import RecommendationService
from src.service.fefo_service import FEFOService

NOW = datetime(2026, 9, 2, 9, 0, tzinfo=UTC)
USER_ID = UUID("00000000-0000-0000-0000-000000000001")
SPINACH_ID = UUID("00000000-0000-0000-0000-000000000011")
CHICKEN_ID = UUID("00000000-0000-0000-0000-000000000012")
RECIPE_A_ID = UUID("00000000-0000-0000-0000-000000000101")
RECIPE_B_ID = UUID("00000000-0000-0000-0000-000000000102")
RECIPE_C_ID = UUID("00000000-0000-0000-0000-000000000103")


def _ingredient(
    ingredient_id: UUID,
    name: str,
    quantity: str = "100",
) -> RecipeIngredientCandidate:
    return RecipeIngredientCandidate(
        master_ingredient_id=ingredient_id,
        name=name,
        required_quantity=Decimal(quantity),
        unit=MeasurementUnit.GRAM,
        is_optional=False,
    )


def _recipe(
    recipe_id: UUID,
    *ingredients: RecipeIngredientCandidate,
    cooking_minutes: int = 20,
) -> RecommendationCandidate:
    return RecommendationCandidate(
        recipe_id=recipe_id,
        name=f"Recipe {recipe_id.int}",
        default_servings=Decimal(2),
        estimated_cooking_minutes=cooking_minutes,
        ingredients=ingredients,
    )


def _batch(
    batch_id: int,
    ingredient_id: UUID,
    quantity: str,
    expires_at: datetime | None,
) -> InventorySnapshotBatch:
    return InventorySnapshotBatch(
        batch_id=UUID(int=batch_id),
        master_ingredient_id=ingredient_id,
        current_quantity=Decimal(quantity),
        unit=MeasurementUnit.GRAM,
        expires_at=expires_at,
        created_at=NOW - timedelta(days=1),
    )


def _provider() -> RuleBasedRecommendationProvider:
    return RuleBasedRecommendationProvider(FEFOService(), near_expiry_days=3)


def _recommend(
    recipes: Sequence[RecommendationCandidate],
    batches: Sequence[InventorySnapshotBatch] = (),
    *,
    preferences: dict[str, object] | None = None,
) -> list[RankedRecommendation]:
    return _provider().recommend(
        RecommendationRequest(
            user_context=UserRecommendationContext(USER_ID, preferences or {}),
            inventory_snapshot=InventorySnapshot(tuple(batches)),
            candidate_recipes=recipes,
            criteria=RecommendationCriteria(servings=Decimal(2)),
            limit=10,
            now=NOW,
        ),
    )


def test_components_are_normalized_and_total_uses_the_exact_weighted_formula() -> None:
    """E/A/P/U always stay in [0, 1] and preserve the specified Decimal formula."""
    result = _recommend(
        [_recipe(RECIPE_A_ID, _ingredient(SPINACH_ID, "Spinach"))],
        [_batch(1, SPINACH_ID, "50", NOW + timedelta(days=1))],
        preferences={"maximum_cooking_minutes": 10},
    )[0]

    components = (
        result.expiration_utilization_score,
        result.availability_score,
        result.preference_fit_score,
        result.purchase_minimization_score,
    )
    assert all(Decimal(0) <= component <= Decimal(1) for component in components)
    assert result.total_score == (
        Decimal("0.4") * result.expiration_utilization_score
        + Decimal("0.3") * result.availability_score
        + Decimal("0.2") * result.preference_fit_score
        + Decimal("0.1") * result.purchase_minimization_score
    )
    assert result.preference_fit_score == Decimal("0.75")
    assert result.explanation.preference_fit.neutral_treatments


def test_near_expiry_usable_stock_raises_expiration_score_and_rank() -> None:
    """A usable near-expiry FEFO allocation raises E and ranks its recipe first."""
    spinach_recipe = _recipe(RECIPE_A_ID, _ingredient(SPINACH_ID, "Spinach"))
    chicken_recipe = _recipe(RECIPE_B_ID, _ingredient(CHICKEN_ID, "Chicken"))

    ranked = _recommend(
        [chicken_recipe, spinach_recipe],
        [
            _batch(1, SPINACH_ID, "100", NOW + timedelta(days=1)),
            _batch(2, CHICKEN_ID, "100", NOW + timedelta(days=10)),
        ],
    )

    assert ranked[0].recipe_id == RECIPE_A_ID
    assert (
        ranked[0].expiration_utilization_score > ranked[1].expiration_utilization_score
    )
    assert ranked[0].explanation.near_expiry_contributions[0].batch_id == UUID(int=1)


def test_greater_ingredient_availability_raises_availability_score_and_rank() -> None:
    """Available usable quantity changes A and the resulting deterministic order."""
    spinach_recipe = _recipe(RECIPE_A_ID, _ingredient(SPINACH_ID, "Spinach"))
    chicken_recipe = _recipe(RECIPE_B_ID, _ingredient(CHICKEN_ID, "Chicken"))

    ranked = _recommend(
        [chicken_recipe, spinach_recipe],
        [_batch(1, SPINACH_ID, "100", NOW + timedelta(days=10))],
    )

    assert ranked[0].recipe_id == RECIPE_A_ID
    assert ranked[0].availability_score == Decimal(1)
    assert ranked[1].availability_score == Decimal(0)


def test_additional_missing_requirements_reduce_purchase_minimization() -> None:
    """U is the inverse normalized count of incomplete required ingredients."""
    one_missing = _recipe(RECIPE_A_ID, _ingredient(SPINACH_ID, "Spinach"))
    two_missing = _recipe(
        RECIPE_B_ID,
        _ingredient(SPINACH_ID, "Spinach"),
        _ingredient(CHICKEN_ID, "Chicken"),
    )

    ranked = {
        item.recipe_id: item
        for item in _recommend(
            [one_missing, two_missing],
            [_batch(1, SPINACH_ID, "100", NOW + timedelta(days=10))],
        )
    }

    assert ranked[RECIPE_A_ID].purchase_minimization_score == Decimal(1)
    assert ranked[RECIPE_B_ID].purchase_minimization_score == Decimal("0.5")


def test_expired_stock_does_not_improve_scores_or_near_expiry_explanation() -> None:
    """Expired inventory is passed to FEFO but excluded from all useful amounts."""
    result = _recommend(
        [_recipe(RECIPE_A_ID, _ingredient(SPINACH_ID, "Spinach"))],
        [_batch(1, SPINACH_ID, "100", NOW - timedelta(seconds=1))],
    )[0]

    assert result.availability_score == Decimal(0)
    assert result.expiration_utilization_score == Decimal(0)
    assert result.purchase_minimization_score == Decimal(0)
    assert not result.explanation.near_expiry_contributions


def test_missing_ingredient_quantities_are_correct_after_unit_compatible_fefo_allocation() -> (
    None
):
    """The result exposes exact requirements, usable availability, and shortfall."""
    result = _recommend(
        [_recipe(RECIPE_A_ID, _ingredient(SPINACH_ID, "Spinach"))],
        [_batch(1, SPINACH_ID, "25", NOW + timedelta(days=5))],
    )[0]

    missing = result.missing_ingredients[0]
    assert missing.master_ingredient_id == SPINACH_ID
    assert missing.required_quantity == Decimal(100)
    assert missing.available_quantity == Decimal(25)
    assert missing.missing_quantity == Decimal(75)
    assert missing.unit is MeasurementUnit.GRAM


def test_ties_are_deterministic_by_recipe_id_after_documented_tie_breaks() -> None:
    """Identical scores, missing counts, and E resolve to the lexical UUID order."""
    ranked = _recommend(
        [
            _recipe(RECIPE_C_ID, _ingredient(SPINACH_ID, "Spinach")),
            _recipe(RECIPE_A_ID, _ingredient(SPINACH_ID, "Spinach")),
        ],
    )

    assert [item.recipe_id for item in ranked] == [RECIPE_A_ID, RECIPE_C_ID]


class _FutureModelProvider:
    """A stand-in ML adapter proving the service depends only on the protocol."""

    provider_type = RecommendationProviderType.XGBOOST
    model_version: str | None = "future-xgboost-v1"

    def recommend(self, request: RecommendationRequest) -> list[RankedRecommendation]:
        """Return the same empty response shape as a future trained model."""
        del request
        return []


def test_provider_contract_accepts_a_future_xgboost_or_lightgbm_adapter() -> None:
    """The caller requires the shared protocol, not a rule-based concrete class."""
    future_provider = _FutureModelProvider()

    assert isinstance(future_provider, RecommendationProvider)
    service = RecommendationService(cast(AsyncSession, object()), future_provider)
    assert service.provider is future_provider


class _FakeResult:
    """Minimal chainable async SQLAlchemy-result stand-in."""

    def __init__(self, value: object) -> None:
        """Keep one queued result payload."""
        self.value = value

    def scalar_one_or_none(self) -> object:
        """Return the scalar payload used by the user lookup."""
        return self.value

    def tuples(self) -> "_FakeResult":
        """Expose the joined recipe rows."""
        return self

    def all(
        self,
    ) -> list[tuple[RecipeModel, RecipeIngredientModel, MasterIngredientModel]]:
        """Return the queued rows for either query shape in this focused fake."""
        return cast(
            list[tuple[RecipeModel, RecipeIngredientModel, MasterIngredientModel]],
            self.value,
        )

    def scalars(self) -> "_FakeResult":
        """Expose the queued batch rows."""
        return self


class _FakeSession:
    """Read-only fake which records query calls and any accidental commit."""

    def __init__(self, results: list[_FakeResult]) -> None:
        """Queue deterministic results for the provider-loading service."""
        self.results = results
        self.statements: list[object] = []
        self.commit_calls = 0

    async def execute(self, statement: object) -> _FakeResult:
        """Record a query and return its queued result."""
        self.statements.append(statement)
        return self.results.pop(0)

    async def commit(self) -> None:
        """Record a forbidden write operation for the read-only assertion."""
        self.commit_calls += 1


@pytest.mark.anyio
async def test_service_loads_orm_recipes_and_live_inventory_without_mutating_it() -> (
    None
):
    """Task 5.2 orchestrates actual ORM data and does not start a persistence flow."""
    user = UserModel(
        id=USER_ID,
        phone_e164="+84123456789",
        password_hash="hash",
        preferences={},
    )
    recipe = RecipeModel(
        id=RECIPE_A_ID,
        name="Spinach recipe",
        description="test",
        instructions={"steps": []},
        default_servings=Decimal(2),
        estimated_cooking_minutes=10,
        tags={"values": []},
    )
    ingredient = MasterIngredientModel(
        id=SPINACH_ID,
        name="Spinach",
        description="test",
        category_id=UUID(int=99),
        canonical_unit=MeasurementUnit.GRAM,
    )
    recipe_ingredient = RecipeIngredientModel(
        recipe_id=recipe.id,
        master_ingredient_id=ingredient.id,
        required_quantity=Decimal(100),
        unit=MeasurementUnit.GRAM,
        is_optional=False,
    )
    inventory_batch = InventoryBatchModel(
        id=UUID(int=1),
        user_id=USER_ID,
        master_ingredient_id=SPINACH_ID,
        custom_name=None,
        batch_type=InventoryBatchType.RAW_INGREDIENT,
        initial_quantity=100.0,
        current_quantity=100.0,
        unit=MeasurementUnit.GRAM,
        storage_mode=StorageMode.REFRIGERATED,
        status=InventoryBatchStatus.ACTIVE,
        expires_at=NOW + timedelta(days=1),
        expiration_source=ExpirationSource.MANUFACTURER,
        source=InventorySource.MANUAL,
        created_at=NOW - timedelta(days=1),
        updated_at=NOW,
    )
    database = _FakeSession(
        [
            _FakeResult(user),
            _FakeResult([(recipe, recipe_ingredient, ingredient)]),
            _FakeResult([inventory_batch]),
        ],
    )
    service = RecommendationService(cast(AsyncSession, database), _provider())

    result = await service.recommend(
        USER_ID,
        RecommendationCriteria(servings=Decimal(2)),
        limit=3,
        now=NOW,
    )

    assert result[0].recipe_id == RECIPE_A_ID
    assert result[0].availability_score == Decimal(1)
    assert len(database.statements) == 3
    assert database.commit_calls == 0
