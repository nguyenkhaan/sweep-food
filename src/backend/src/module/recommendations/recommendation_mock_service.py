"""Temporary deterministic recommendation response adapter.

It is intentionally isolated from Task 5.2's real provider. A later service
can implement ``RecommendationResponseService`` without changing route DTOs.
"""

from collections.abc import Sequence
from dataclasses import dataclass
from datetime import UTC, datetime
from decimal import Decimal
from typing import Protocol, TypeAlias
from uuid import UUID

from src.middleware.auth_middleware import AuthenticatedUser
from src.model.enum_model import MeasurementUnit
from src.module.recipes.recipe_dto import RecipeListItemDTO
from src.module.recommendations.recommendation_dto import (
    RecommendationExplanationDTO,
    RecommendationIngredientAvailabilityDTO,
    RecommendationItemDTO,
    RecommendationListResponseDTO,
    RecommendationMissingIngredientDTO,
    RecommendationNearExpiryContributionDTO,
    RecommendationPreferenceFitExplanationDTO,
    RecommendationRequestDTO,
    RecommendationScoreComponentsDTO,
)

_MOCK_TIME = datetime(2026, 9, 5, tzinfo=UTC)
_REQUIRED_QUANTITY = Decimal(200)
_FixtureSource: TypeAlias = tuple[
    int,
    str,
    int,
    list[str],
    str,
    tuple[str, str, str, str],
    str,
    str,
    bool,
]


class RecommendationResponseService(Protocol):
    """Application boundary for HTTP recommendation response generation."""

    async def recommend(
        self, user: AuthenticatedUser, request: RecommendationRequestDTO
    ) -> RecommendationListResponseDTO:
        """Return ranked recommendations without changing public DTOs."""


@dataclass(frozen=True, slots=True)
class _MockDefinition:
    """Static source data used only by the temporary contract adapter."""

    recipe: RecipeListItemDTO
    ranking: tuple[int, Decimal, tuple[Decimal, Decimal, Decimal, Decimal]]
    ingredient: tuple[UUID, str, Decimal, UUID | None]


def _recipe(index: int, name: str, minutes: int, tags: list[str]) -> RecipeListItemDTO:
    """Build one basic recipe card with deterministic test-only identifiers."""
    return RecipeListItemDTO(
        id=UUID(f"10000000-0000-0000-0000-{index:012d}"),
        name=name,
        description=f"A practical {name.lower()} recipe.",
        media_url=None,
        default_servings=Decimal("2.00"),
        estimated_cooking_minutes=minutes,
        estimated_cost=40000.0 + index * 2500.0,
        tags={"values": tags},
    )


def _definition(source: _FixtureSource) -> _MockDefinition:
    """Build a typed fixture definition from concise constant source values."""
    (
        index,
        name,
        minutes,
        tags,
        score,
        components,
        ingredient_name,
        missing_quantity,
        has_near_expiry,
    ) = source
    return _MockDefinition(
        recipe=_recipe(index, name, minutes, tags),
        ranking=(
            index,
            Decimal(score),
            (
                Decimal(components[0]),
                Decimal(components[1]),
                Decimal(components[2]),
                Decimal(components[3]),
            ),
        ),
        ingredient=(
            UUID(f"20000000-0000-0000-0000-{index:012d}"),
            ingredient_name,
            Decimal(missing_quantity),
            (
                UUID(f"30000000-0000-0000-0000-{index:012d}")
                if has_near_expiry
                else None
            ),
        ),
    )


_MOCK_ITEMS: tuple[_MockDefinition, ...] = (
    _definition(
        (
            1,
            "Spinach and tofu soup",
            20,
            ["vegetarian", "quick"],
            "0.869",
            ("0.95", "0.88", "0.75", "0.75"),
            "Spinach",
            "50",
            True,
        )
    ),
    _definition(
        (
            2,
            "Ginger chicken rice bowl",
            30,
            ["high-protein", "quick"],
            "0.787",
            ("0.80", "0.84", "0.75", "0.65"),
            "Chicken breast",
            "80",
            True,
        )
    ),
    _definition(
        (
            3,
            "Tomato basil pasta",
            25,
            ["vegetarian", "quick"],
            "0.706",
            ("0.62", "0.76", "0.80", "0.70"),
            "Tomatoes",
            "100",
            False,
        )
    ),
    _definition(
        (
            4,
            "Roasted vegetable quinoa",
            40,
            ["vegetarian", "whole-grain"],
            "0.646",
            ("0.55", "0.67", "0.80", "0.65"),
            "Zucchini",
            "120",
            False,
        )
    ),
    _definition(
        (
            5,
            "Lentil vegetable curry",
            30,
            ["vegetarian", "high-fiber"],
            "0.608",
            ("0.48", "0.62", "0.80", "0.70"),
            "Red lentils",
            "100",
            False,
        )
    ),
)


class TemporaryMockRecommendationService:
    """Serve contract fixtures without provider, AI, database, or inventory access."""

    async def recommend(
        self, user: AuthenticatedUser, request: RecommendationRequestDTO
    ) -> RecommendationListResponseDTO:
        """Return a stable filtered subset of static recommendation data."""
        del user
        return RecommendationListResponseDTO(
            items=[
                _item(item)
                for item in self._filter_items(_MOCK_ITEMS, request)[: request.limit]
            ]
        )

    @staticmethod
    def _filter_items(
        items: Sequence[_MockDefinition], request: RecommendationRequestDTO
    ) -> list[_MockDefinition]:
        """Apply supported filters while retaining the fixed rank order."""
        return [
            item
            for item in items
            if (
                request.filters.tag is None
                or request.filters.tag in _recipe_tags(item.recipe)
            )
            and (
                request.filters.max_cooking_minutes is None
                or item.recipe.estimated_cooking_minutes
                <= request.filters.max_cooking_minutes
            )
        ]


def _item(definition: _MockDefinition) -> RecommendationItemDTO:
    """Map one typed mock definition to the final public response shape."""
    rank, score, components = definition.ranking
    ingredient_id, ingredient_name, missing_quantity, expiring_batch_id = (
        definition.ingredient
    )
    available = _REQUIRED_QUANTITY - missing_quantity
    availability = RecommendationIngredientAvailabilityDTO(
        master_ingredient_id=ingredient_id,
        name=ingredient_name,
        required_quantity=_REQUIRED_QUANTITY,
        available_quantity=available,
        missing_quantity=missing_quantity,
        unit=MeasurementUnit.GRAM,
    )
    near_expiry = _near_expiry(definition)
    return RecommendationItemDTO(
        recipe_id=definition.recipe.id,
        recipe=definition.recipe,
        rank=rank,
        score=score,
        score_components=RecommendationScoreComponentsDTO(
            expiration_utilization=components[0],
            availability=components[1],
            preference_fit=components[2],
            purchase_minimization=components[3],
        ),
        available_ratio=components[1],
        missing_ingredients=_missing(definition, available),
        expiring_batches_used=[] if expiring_batch_id is None else [expiring_batch_id],
        explanation=RecommendationExplanationDTO(
            ingredient_availability=[availability],
            near_expiry_contributions=near_expiry,
            preference_fit=RecommendationPreferenceFitExplanationDTO(
                serving_suitability=Decimal(1),
                cooking_time_suitability=Decimal("0.8"),
                dietary_suitability=Decimal("0.75"),
                nutrition_suitability=Decimal("0.75"),
                maximum_cooking_minutes=None,
                neutral_treatments=[
                    "Dietary and nutrition preferences use neutral defaults when absent."
                ],
            ),
        ),
        provider="CONTRACT_STUB",
        model_version="v1",
    )


def _missing(
    definition: _MockDefinition, available: Decimal
) -> list[RecommendationMissingIngredientDTO]:
    """Return the fixed shortfall representation when the fixture has one."""
    ingredient_id, ingredient_name, missing_quantity, _batch_id = definition.ingredient
    if missing_quantity == 0:
        return []
    return [
        RecommendationMissingIngredientDTO(
            master_ingredient_id=ingredient_id,
            name=ingredient_name,
            required_quantity=_REQUIRED_QUANTITY,
            available_quantity=available,
            missing_quantity=missing_quantity,
            unit=MeasurementUnit.GRAM,
        )
    ]


def _near_expiry(
    definition: _MockDefinition,
) -> list[RecommendationNearExpiryContributionDTO]:
    """Return fixed near-expiry evidence when the fixture represents it."""
    ingredient_id, ingredient_name, _missing_quantity, batch_id = definition.ingredient
    if batch_id is None:
        return []
    return [
        RecommendationNearExpiryContributionDTO(
            batch_id=batch_id,
            master_ingredient_id=ingredient_id,
            ingredient_name=ingredient_name,
            allocated_quantity=Decimal(120),
            unit=MeasurementUnit.GRAM,
            expires_at=_MOCK_TIME,
            urgency_weight=Decimal("0.92"),
        )
    ]


def _recipe_tags(recipe: RecipeListItemDTO) -> list[str]:
    """Read recipe tags defensively from the seeded-recipe public shape."""
    raw_tags = recipe.tags.get("values")
    return (
        [tag for tag in raw_tags if isinstance(tag, str)]
        if isinstance(raw_tags, list)
        else []
    )
