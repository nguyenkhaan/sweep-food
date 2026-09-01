"""Stable, explainable recommendation-provider contract for the MVP."""

from collections.abc import Sequence
from dataclasses import dataclass
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Protocol, runtime_checkable
from uuid import UUID

from src.model.enum_model import MeasurementUnit, RecommendationProviderType
from src.service.fefo_service import FEFOAllocation, FEFOCandidate, FEFOService

_ZERO = Decimal(0)
_ONE = Decimal(1)
_WEIGHT_EXPIRATION = Decimal("0.4")
_WEIGHT_AVAILABILITY = Decimal("0.3")
_WEIGHT_PREFERENCE = Decimal("0.2")
_WEIGHT_PURCHASE = Decimal("0.1")


@dataclass(frozen=True, slots=True)
class RecommendationCriteria:
    """Caller-controlled ranking criteria shared by every provider adapter."""

    servings: Decimal | None = None


@dataclass(frozen=True, slots=True)
class UserRecommendationContext:
    """User data currently available to recommendation providers.

    The MVP profile stores arbitrary JSON.  Only a positive numeric
    ``maximum_cooking_minutes`` value is a represented suitability signal.
    Dietary/disliked-ingredient constraints and nutrition targets have no
    controlled data contract yet, so providers must treat them neutrally.
    """

    user_id: UUID
    preferences: dict[str, object]


@dataclass(frozen=True, slots=True)
class RecipeIngredientCandidate:
    """One catalog ingredient required by a candidate recipe."""

    master_ingredient_id: UUID
    name: str
    required_quantity: Decimal
    unit: MeasurementUnit
    is_optional: bool


@dataclass(frozen=True, slots=True)
class RecommendationCandidate:
    """A seeded recipe and its real catalog requirements."""

    recipe_id: UUID
    name: str
    default_servings: Decimal
    estimated_cooking_minutes: int
    ingredients: tuple[RecipeIngredientCandidate, ...]


@dataclass(frozen=True, slots=True)
class InventorySnapshotBatch:
    """Read-only active inventory data used while ranking recipes."""

    batch_id: UUID
    master_ingredient_id: UUID
    current_quantity: Decimal
    unit: MeasurementUnit
    expires_at: datetime | None
    created_at: datetime


@dataclass(frozen=True, slots=True)
class InventorySnapshot:
    """The caller's live inventory at one evaluation time."""

    batches: tuple[InventorySnapshotBatch, ...]


@dataclass(frozen=True, slots=True)
class MissingIngredient:
    """The remaining purchasable amount for one required ingredient."""

    master_ingredient_id: UUID
    name: str
    required_quantity: Decimal
    available_quantity: Decimal
    missing_quantity: Decimal
    unit: MeasurementUnit


@dataclass(frozen=True, slots=True)
class NearExpiryContribution:
    """A usable FEFO allocation which improved expiration utilization."""

    batch_id: UUID
    master_ingredient_id: UUID
    ingredient_name: str
    allocated_quantity: Decimal
    unit: MeasurementUnit
    expires_at: datetime
    urgency_weight: Decimal


@dataclass(frozen=True, slots=True)
class IngredientAvailability:
    """Per-ingredient source and shortfall details for later API mapping."""

    master_ingredient_id: UUID
    name: str
    required_quantity: Decimal
    available_quantity: Decimal
    missing_quantity: Decimal
    unit: MeasurementUnit


@dataclass(frozen=True, slots=True)
class PreferenceFitExplanation:
    """Explain the represented and neutral preference-fit inputs."""

    serving_suitability: Decimal
    cooking_time_suitability: Decimal
    dietary_suitability: Decimal
    nutrition_suitability: Decimal
    maximum_cooking_minutes: int | None
    neutral_treatments: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class RecommendationExplanation:
    """Structured explanation ready for Task 5.3 response/persistence mapping."""

    ingredient_availability: tuple[IngredientAvailability, ...]
    missing_ingredients: tuple[MissingIngredient, ...]
    near_expiry_contributions: tuple[NearExpiryContribution, ...]
    preference_fit: PreferenceFitExplanation


@dataclass(frozen=True, slots=True)
class RecommendationRequest:
    """One complete caller-owned evaluation request for any provider adapter."""

    user_context: UserRecommendationContext
    inventory_snapshot: InventorySnapshot
    candidate_recipes: Sequence[RecommendationCandidate]
    criteria: RecommendationCriteria
    limit: int
    now: datetime


@dataclass(frozen=True, slots=True)
class RecommendationScoreComponents:
    """The normalized E/A/P/U components used by every ranked result."""

    expiration_utilization: Decimal
    availability: Decimal
    preference_fit: Decimal
    purchase_minimization: Decimal


@dataclass(frozen=True, slots=True)
class RankedRecommendation:
    """A provider-independent, deterministic recommendation result."""

    recipe_id: UUID
    recipe_name: str
    provider: RecommendationProviderType
    model_version: str | None
    score_components: RecommendationScoreComponents
    missing_ingredients: tuple[MissingIngredient, ...]
    explanation: RecommendationExplanation

    @property
    def expiration_utilization_score(self) -> Decimal:
        """Return normalized E for persistence and API mapping."""
        return self.score_components.expiration_utilization

    @property
    def availability_score(self) -> Decimal:
        """Return normalized A for persistence and API mapping."""
        return self.score_components.availability

    @property
    def preference_fit_score(self) -> Decimal:
        """Return normalized P for persistence and API mapping."""
        return self.score_components.preference_fit

    @property
    def purchase_minimization_score(self) -> Decimal:
        """Return normalized U for persistence and API mapping."""
        return self.score_components.purchase_minimization

    @property
    def total_score(self) -> Decimal:
        """Return exactly ``0.4E + 0.3A + 0.2P + 0.1U``."""
        return (
            _WEIGHT_EXPIRATION * self.expiration_utilization_score
            + _WEIGHT_AVAILABILITY * self.availability_score
            + _WEIGHT_PREFERENCE * self.preference_fit_score
            + _WEIGHT_PURCHASE * self.purchase_minimization_score
        )


@dataclass(frozen=True, slots=True)
class _IngredientEvaluation:
    """Private ingredients-level scoring result used to assemble one recipe."""

    availability: IngredientAvailability
    missing_ingredient: MissingIngredient | None
    expiration_score: Decimal
    near_expiry_contributions: tuple[NearExpiryContribution, ...]


@runtime_checkable
class RecommendationProvider(Protocol):
    """Contract a future XGBoost/LightGBM provider must implement unchanged."""

    provider_type: RecommendationProviderType
    model_version: str | None

    def recommend(self, request: RecommendationRequest) -> list[RankedRecommendation]:
        """Rank the supplied snapshot without mutating caller-owned state."""


class RuleBasedRecommendationProvider:
    """Database-backed deterministic ``RULE_BASED_MVP`` scoring adapter."""

    provider_type = RecommendationProviderType.RULE_BASED_MVP
    model_version: str | None = "rule-based-mvp-v1"

    def __init__(self, fefo_service: FEFOService, near_expiry_days: int = 3) -> None:
        if near_expiry_days <= 0:
            raise ValueError("near_expiry_days must be positive")
        self.fefo_service = fefo_service
        self.near_expiry_days = near_expiry_days

    def recommend(self, request: RecommendationRequest) -> list[RankedRecommendation]:
        """Score seeded recipe candidates from a live, read-only inventory snapshot."""
        if request.limit <= 0:
            raise ValueError("limit must be positive")
        batches_by_ingredient = self._batches_by_ingredient(request.inventory_snapshot)
        ranked = [
            self._evaluate_candidate(request, candidate, batches_by_ingredient)
            for candidate in request.candidate_recipes
        ]
        return sorted(
            ranked,
            key=lambda item: (
                -item.total_score,
                len(item.missing_ingredients),
                -item.expiration_utilization_score,
                str(item.recipe_id),
            ),
        )[: request.limit]

    def _evaluate_candidate(
        self,
        request: RecommendationRequest,
        candidate: RecommendationCandidate,
        batches_by_ingredient: dict[UUID, tuple[InventorySnapshotBatch, ...]],
    ) -> RankedRecommendation:
        servings = request.criteria.servings or candidate.default_servings
        if servings <= _ZERO:
            raise ValueError("servings must be positive")
        scale = servings / candidate.default_servings
        required_ingredients = [
            ingredient
            for ingredient in candidate.ingredients
            if not ingredient.is_optional
        ]
        evaluations = [
            self._evaluate_ingredient(
                ingredient,
                scale,
                batches_by_ingredient.get(ingredient.master_ingredient_id, ()),
                request.now,
            )
            for ingredient in required_ingredients
        ]
        requirement_count = Decimal(len(required_ingredients))
        availability_score = self._mean(
            sum(
                (
                    self._ratio(
                        evaluation.availability.available_quantity,
                        evaluation.availability.required_quantity,
                    )
                    for evaluation in evaluations
                ),
                start=_ZERO,
            ),
            requirement_count,
        )
        expiration_score = self._mean(
            sum(
                (evaluation.expiration_score for evaluation in evaluations),
                start=_ZERO,
            ),
            requirement_count,
        )
        missing_ingredients = [
            evaluation.missing_ingredient
            for evaluation in evaluations
            if evaluation.missing_ingredient is not None
        ]
        purchase_score = self._purchase_score(
            missing_count=len(missing_ingredients),
            requirement_count=requirement_count,
        )
        preference_fit, preference_explanation = self._preference_fit(
            request.user_context,
            candidate,
        )
        return RankedRecommendation(
            recipe_id=candidate.recipe_id,
            recipe_name=candidate.name,
            provider=self.provider_type,
            model_version=self.model_version,
            score_components=RecommendationScoreComponents(
                expiration_utilization=expiration_score,
                availability=availability_score,
                preference_fit=preference_fit,
                purchase_minimization=purchase_score,
            ),
            missing_ingredients=tuple(missing_ingredients),
            explanation=RecommendationExplanation(
                ingredient_availability=tuple(
                    evaluation.availability for evaluation in evaluations
                ),
                missing_ingredients=tuple(missing_ingredients),
                near_expiry_contributions=tuple(
                    contribution
                    for evaluation in evaluations
                    for contribution in evaluation.near_expiry_contributions
                ),
                preference_fit=preference_explanation,
            ),
        )

    def _evaluate_ingredient(
        self,
        ingredient: RecipeIngredientCandidate,
        scale: Decimal,
        batches: Sequence[InventorySnapshotBatch],
        now: datetime,
    ) -> _IngredientEvaluation:
        required_quantity = ingredient.required_quantity * scale
        allocation_result = self.fefo_service.allocate(
            float(required_quantity),
            ingredient.unit,
            [self._to_fefo_candidate(batch) for batch in batches],
            now,
        )
        missing_quantity = max(
            _ZERO,
            Decimal(str(allocation_result.missing_quantity)),
        )
        availability = IngredientAvailability(
            master_ingredient_id=ingredient.master_ingredient_id,
            name=ingredient.name,
            required_quantity=required_quantity,
            available_quantity=max(_ZERO, required_quantity - missing_quantity),
            missing_quantity=missing_quantity,
            unit=ingredient.unit,
        )
        expiration_score, contributions = self._near_expiry_score(
            ingredient=ingredient,
            required_quantity=required_quantity,
            allocations=allocation_result.allocations,
            now=now,
        )
        missing_ingredient = (
            MissingIngredient(
                master_ingredient_id=availability.master_ingredient_id,
                name=availability.name,
                required_quantity=availability.required_quantity,
                available_quantity=availability.available_quantity,
                missing_quantity=availability.missing_quantity,
                unit=availability.unit,
            )
            if missing_quantity > _ZERO
            else None
        )
        return _IngredientEvaluation(
            availability=availability,
            missing_ingredient=missing_ingredient,
            expiration_score=expiration_score,
            near_expiry_contributions=tuple(contributions),
        )

    @staticmethod
    def _batches_by_ingredient(
        inventory_snapshot: InventorySnapshot,
    ) -> dict[UUID, tuple[InventorySnapshotBatch, ...]]:
        grouped: dict[UUID, list[InventorySnapshotBatch]] = {}
        for batch in inventory_snapshot.batches:
            if batch.current_quantity > _ZERO:
                grouped.setdefault(batch.master_ingredient_id, []).append(batch)
        return {
            ingredient_id: tuple(batches) for ingredient_id, batches in grouped.items()
        }

    @staticmethod
    def _to_fefo_candidate(batch: InventorySnapshotBatch) -> FEFOCandidate:
        return FEFOCandidate(
            batch_id=batch.batch_id,
            current_quantity=float(batch.current_quantity),
            unit=batch.unit,
            expires_at=batch.expires_at,
            created_at=batch.created_at,
        )

    def _near_expiry_score(
        self,
        *,
        ingredient: RecipeIngredientCandidate,
        required_quantity: Decimal,
        allocations: Sequence[FEFOAllocation],
        now: datetime,
    ) -> tuple[Decimal, list[NearExpiryContribution]]:
        weighted_quantity = _ZERO
        contributions: list[NearExpiryContribution] = []
        for allocation in allocations:
            if allocation.expires_at is None:
                continue
            urgency_weight = self._urgency_weight(allocation.expires_at, now)
            if urgency_weight <= _ZERO:
                continue
            allocation_quantity = Decimal(str(allocation.recipe_quantity))
            weighted_quantity += allocation_quantity * urgency_weight
            contributions.append(
                NearExpiryContribution(
                    batch_id=allocation.batch_id,
                    master_ingredient_id=ingredient.master_ingredient_id,
                    ingredient_name=ingredient.name,
                    allocated_quantity=allocation_quantity,
                    unit=ingredient.unit,
                    expires_at=allocation.expires_at,
                    urgency_weight=urgency_weight,
                )
            )
        return self._ratio(weighted_quantity, required_quantity), contributions

    def _urgency_weight(self, expires_at: datetime, now: datetime) -> Decimal:
        """Return [0, 1] urgency for a usable batch in the warning window."""
        window_seconds = Decimal(
            str(timedelta(days=self.near_expiry_days).total_seconds())
        )
        remaining_seconds = Decimal(str((expires_at - now).total_seconds()))
        if remaining_seconds < _ZERO or remaining_seconds > window_seconds:
            return _ZERO
        return _ONE - (remaining_seconds / window_seconds)

    @staticmethod
    def _ratio(numerator: Decimal, denominator: Decimal) -> Decimal:
        if denominator <= _ZERO:
            return _ZERO
        return min(_ONE, max(_ZERO, numerator / denominator))

    @staticmethod
    def _mean(total: Decimal, count: Decimal) -> Decimal:
        return RuleBasedRecommendationProvider._ratio(total, count)

    @staticmethod
    def _purchase_score(missing_count: int, requirement_count: Decimal) -> Decimal:
        if requirement_count <= _ZERO:
            return _ONE
        return _ONE - RuleBasedRecommendationProvider._ratio(
            Decimal(missing_count),
            requirement_count,
        )

    @staticmethod
    def _preference_fit(
        user_context: UserRecommendationContext,
        candidate: RecommendationCandidate,
    ) -> tuple[Decimal, PreferenceFitExplanation]:
        raw_maximum = user_context.preferences.get("maximum_cooking_minutes")
        maximum_cooking_minutes = (
            raw_maximum
            if isinstance(raw_maximum, int)
            and not isinstance(raw_maximum, bool)
            and raw_maximum > 0
            else None
        )
        cooking_time_suitability = (
            _ONE
            if maximum_cooking_minutes is None
            or candidate.estimated_cooking_minutes <= maximum_cooking_minutes
            else _ZERO
        )
        components = (_ONE, cooking_time_suitability, _ONE, _ONE)
        score = sum(components, start=_ZERO) / Decimal(len(components))
        return score, PreferenceFitExplanation(
            serving_suitability=_ONE,
            cooking_time_suitability=cooking_time_suitability,
            dietary_suitability=_ONE,
            nutrition_suitability=_ONE,
            maximum_cooking_minutes=maximum_cooking_minutes,
            neutral_treatments=(
                "Serving requests scale every seeded recipe, so serving fit is neutral.",
                "Dietary/disliked-ingredient constraints are not stored; dietary fit is neutral.",
                "No nutrition target is stored, so nutrition fit is neutral.",
            ),
        )
