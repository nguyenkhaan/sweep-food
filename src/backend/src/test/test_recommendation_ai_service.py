"""Unit tests for AI-backed recommendation orchestration."""

from dataclasses import replace
from datetime import UTC, datetime, timedelta
from decimal import Decimal
from typing import cast
from uuid import UUID, uuid4

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from AI.recommendation.engine import (
    EngineIngredient,
    EngineRankingFeatures,
    EngineRecommendation,
    EngineRescuedItem,
    EngineResult,
    EngineTimings,
    RecommendationEngine,
)
from src.model.enum_model import MeasurementUnit
from src.module.recommendations.recommendation_ai_service import (
    RecommendationAIService,
)
from src.module.recommendations.recommendation_dto import RecommendationRequestDTO

USER_ID = UUID("018f0f90-26e6-7ce7-8f61-8769f9e5b101")
RECIPE_ONE_ID = UUID("018f0f90-26e6-7ce7-8f61-8769f9e5b102")
RECIPE_TWO_ID = UUID("018f0f90-26e6-7ce7-8f61-8769f9e5b103")
UNKNOWN_RECIPE_ID = UUID("018f0f90-26e6-7ce7-8f61-8769f9e5b199")
NOW = datetime(2026, 10, 16, 10, tzinfo=UTC)


def _batch_row(
    quantity: float,
    expires_in: timedelta | None,
    *,
    name: str = "Đùi gà",
    unit: MeasurementUnit = MeasurementUnit.GRAM,
    source_code: str | None = None,
) -> tuple[object, ...]:
    """Build one active-batch query row as `_load_stock` selects it."""
    return (
        uuid4(),
        None,
        name,
        source_code,
        quantity,
        unit,
        None if expires_in is None else NOW + expires_in,
        NOW - timedelta(days=1),
    )


def _empty_result() -> EngineResult:
    return EngineResult(
        status="empty",
        contract_version="2",
        model_version="lgbm-contextual-v3.1.0",
        catalog_revision="catalog-test",
        ranker_model="LightGBM LambdaMART",
        timings=EngineTimings(total_ms=1.0, candidate_ms=1.0, ranker_ms=0.0),
        recommendations=[],
    )


class _Recipe:
    def __init__(self, recipe_id: UUID, name: str) -> None:
        self.id = recipe_id
        self.name = name
        self.media_url = None
        self.estimated_cooking_minutes = 20
        self.default_servings = Decimal(2)
        self.total_calories = Decimal(300)
        self.total_protein_g = Decimal(10)
        self.total_fat_g = Decimal(5)
        self.total_carbs_g = Decimal(30)
        self.total_sugar_g = Decimal(2)
        self.other_nutrients: dict[str, object] = {}


class _Result:
    def __init__(self, value: object) -> None:
        self._value = value

    def scalars(self) -> "_Result":
        return self

    def all(self) -> list[object]:
        return cast(list[object], self._value)


class _Session:
    def __init__(
        self,
        *,
        recipes: list[_Recipe],
        inventory_expiries: list[object] | None = None,
    ) -> None:
        self._values: list[object] = [inventory_expiries or [], recipes]
        self.statements: list[object] = []

    async def execute(self, statement: object) -> _Result:
        self.statements.append(statement)
        return _Result(self._values.pop(0))


class _SequenceSession:
    """Return ordered query results for pantry enrichment tests."""

    def __init__(self, values: list[object]) -> None:
        self._values = values

    async def execute(self, _statement: object) -> _Result:
        return _Result(self._values.pop(0))


class _FakeEngine:
    def __init__(self, response: EngineResult) -> None:
        self.response = response
        self.requests: list[RecommendationRequestDTO] = []

    def recommend(self, request: RecommendationRequestDTO) -> EngineResult:
        self.requests.append(request)
        return self.response


def _engine_item(recipe_id: UUID, rank_score: float) -> EngineRecommendation:
    return EngineRecommendation(
        id=recipe_id,
        name="AI display name",
        rank_score=rank_score,
        ranking_features=EngineRankingFeatures(
            core_coverage=0.8,
            core_missing_count=1.0,
            secondary_coverage=0.7,
            shopping_gap_items=1.0,
            rescue_weight_g=300.0,
            nutrition_confidence=0.9,
            kcal_per_serving=450.0,
            protein_per_serving=25.0,
            prep_complexity=3.2,
        ),
        matched_ingredients=[
            EngineIngredient(
                name="Spinach",
                code="4001",
                required_g=300.0,
            )
        ],
        missing_ingredients=[
            EngineIngredient(
                name="Salt",
                code="13001",
                required_g=5.0,
            )
        ],
        optional_ingredients=[
            EngineIngredient(
                name="Pepper",
                code="13002",
                required_g=1.0,
            )
        ],
        rescued_items=["Spinach"],
        status_badge="ready",
    )


@pytest.mark.anyio
async def test_recommendation_uses_user_pantry_and_preserves_ai_order() -> None:
    session = _Session(
        recipes=[
            _Recipe(RECIPE_ONE_ID, "Backend soup"),
            _Recipe(RECIPE_TWO_ID, "Backend salad"),
        ],
    )
    fake_engine = _FakeEngine(
        EngineResult(
            status="success",
            contract_version="2",
            model_version="lgbm-contextual-v3.1.0",
            catalog_revision="catalog-test",
            ranker_model="LightGBM LambdaMART",
            timings=EngineTimings(
                total_ms=20.1,
                candidate_ms=2.3,
                ranker_ms=4.8,
            ),
            recommendations=[
                _engine_item(RECIPE_TWO_ID, 1.9),
                _engine_item(UNKNOWN_RECIPE_ID, 1.8),
                _engine_item(RECIPE_ONE_ID, 1.7),
            ],
        )
    )
    service = RecommendationAIService(
        cast(AsyncSession, session),
        cast(RecommendationEngine, fake_engine),
    )

    response = await service.recommend(
        USER_ID,
        RecommendationRequestDTO(
            items=[
                {
                    "name": "Spinach",
                    "code": "4001",
                    "quantity_g": 600,
                    "hours_to_expire": 0,
                }
            ],
            household_size=2,
            allergies=["peanut"],
        ),
    )

    assert len(fake_engine.requests) == 1
    request = fake_engine.requests[0]
    assert len(request.items) == 1
    assert request.items[0].quantity_g == 600
    assert request.items[0].hours_to_expire == 0
    assert request.items[0].code == "4001"
    assert request.household_size == 2
    assert request.allergies == ["peanut"]
    assert [item.recipe_id for item in response.items] == [
        RECIPE_TWO_ID,
        RECIPE_ONE_ID,
    ]
    assert response.items[0].recipe_name == "Backend salad"
    assert response.items[0].rank_score == 1.9
    assert response.items[0].matched_ingredients[0].code == "4001"
    assert response.items[0].missing_ingredients[0].required_g == 5.0
    assert response.items[0].optional_ingredients[0].name == "Pepper"
    assert response.items[0].provider == "SWEEP_FOOD_AI"
    assert response.contract_version == "2"
    assert response.ranker_model == "LightGBM LambdaMART"
    assert response.analysis.is_mock is False
    assert f"UNKNOWN_RECIPE_ID:{UNKNOWN_RECIPE_ID}" in response.warnings
    assert len(session.statements) == 2


@pytest.mark.anyio
async def test_empty_pantry_and_empty_ai_result_are_explicit() -> None:
    session = _Session(recipes=[])
    fake_engine = _FakeEngine(
        EngineResult(
            status="empty",
            contract_version="2",
            model_version="lgbm-contextual-v3.1.0",
            catalog_revision="catalog-test",
            ranker_model="LightGBM LambdaMART",
            timings=EngineTimings(
                total_ms=1.0,
                candidate_ms=1.0,
                ranker_ms=0.0,
            ),
            recommendations=[],
        )
    )
    service = RecommendationAIService(
        cast(AsyncSession, session),
        cast(RecommendationEngine, fake_engine),
    )

    response = await service.recommend(
        USER_ID,
        RecommendationRequestDTO(items=[]),
    )

    assert fake_engine.requests[0].items == []
    assert response.items == []
    assert response.analysis.is_mock is False
    assert len(session.statements) == 0


@pytest.mark.anyio
async def test_recommendation_uses_the_earliest_saved_batch_expiry() -> None:
    """The engine receives server-derived urgency instead of a stale client value."""
    now = NOW
    session = _SequenceSession(
        [[_batch_row(600, timedelta(hours=12, minutes=30), name="Spinach")]]
    )
    fake_engine = _FakeEngine(
        EngineResult(
            status="empty",
            contract_version="2",
            model_version="lgbm-contextual-v3.1.0",
            catalog_revision="catalog-test",
            ranker_model="LightGBM LambdaMART",
            timings=EngineTimings(
                total_ms=1.0,
                candidate_ms=1.0,
                ranker_ms=0.0,
            ),
            recommendations=[],
        )
    )
    service = RecommendationAIService(
        cast(AsyncSession, session),
        cast(RecommendationEngine, fake_engine),
        clock=lambda: now,
    )

    response = await service.recommend(
        USER_ID,
        RecommendationRequestDTO(
            items=[
                {
                    "name": "Spinach",
                    "quantity_g": 600,
                    "hours_to_expire": 999,
                }
            ]
        ),
    )

    assert fake_engine.requests[0].items[0].hours_to_expire == 12.5
    assert response.request.items[0].hours_to_expire == 12.5


@pytest.mark.anyio
async def test_batches_of_one_ingredient_reach_the_engine_as_one_item() -> None:
    """Per-batch entries merge into one item carrying the saved total and expiry."""
    session = _SequenceSession(
        [
            [
                _batch_row(200, timedelta(hours=10), source_code="7001"),
                _batch_row(0.2, timedelta(hours=20), unit=MeasurementUnit.KG),
                _batch_row(200, timedelta(hours=72)),
                _batch_row(300, timedelta(hours=-2)),
            ]
        ]
    )
    fake_engine = _FakeEngine(_empty_result())
    service = RecommendationAIService(
        cast(AsyncSession, session),
        cast(RecommendationEngine, fake_engine),
        clock=lambda: NOW,
    )

    await service.recommend(
        USER_ID,
        RecommendationRequestDTO(
            items=[
                {"name": "Đùi gà", "code": "batch-uuid", "quantity_g": 200},
                {"name": "đùi gà", "quantity_g": 200},
                {"name": "Đùi gà", "quantity_g": 200},
            ]
        ),
    )

    items = fake_engine.requests[0].items
    assert len(items) == 1
    assert items[0].quantity_g == 600
    assert items[0].hours_to_expire == 10
    assert items[0].code == "7001"


@pytest.mark.anyio
async def test_rescued_details_split_the_recipe_need_first_expired_first() -> None:
    """Rescued grams are the part of the need drawn from batches expiring soon."""
    session = _Session(
        recipes=[_Recipe(RECIPE_ONE_ID, "Gà chiên")],
        inventory_expiries=[
            _batch_row(200, timedelta(hours=72)),
            _batch_row(200, timedelta(hours=10)),
            _batch_row(200, timedelta(hours=20)),
        ],
    )
    recommendation = replace(
        _engine_item(RECIPE_ONE_ID, 1.0),
        rescued_items=["Đùi gà", "Đùi gà", "Đùi gà"],
        rescued_requirements=[EngineRescuedItem(name="Đùi gà", required_g=500.0)],
    )
    fake_engine = _FakeEngine(
        replace(_empty_result(), status="success", recommendations=[recommendation])
    )
    service = RecommendationAIService(
        cast(AsyncSession, session),
        cast(RecommendationEngine, fake_engine),
        clock=lambda: NOW,
    )

    response = await service.recommend(
        USER_ID,
        RecommendationRequestDTO(
            items=[{"name": "Đùi gà", "quantity_g": 200}] * 3,
            household_size=4,
        ),
    )

    item = response.items[0]
    assert item.rescued_items == ["Đùi gà"]
    assert len(item.rescued_details) == 1
    detail = item.rescued_details[0]
    assert detail.name == "Đùi gà"
    assert detail.required_g == 500
    assert detail.rescued_g == 400
    assert detail.expiring_g == 400
    assert detail.expires_at == NOW + timedelta(hours=10)


@pytest.mark.anyio
async def test_items_without_saved_stock_keep_client_urgency_for_rescue() -> None:
    """A rescued item absent from inventory uses the request quantity and expiry."""
    session = _Session(recipes=[_Recipe(RECIPE_ONE_ID, "Canh rau")])
    recommendation = replace(
        _engine_item(RECIPE_ONE_ID, 1.0),
        rescued_requirements=[EngineRescuedItem(name="Spinach", required_g=300.0)],
    )
    fake_engine = _FakeEngine(
        replace(_empty_result(), status="success", recommendations=[recommendation])
    )
    service = RecommendationAIService(
        cast(AsyncSession, session),
        cast(RecommendationEngine, fake_engine),
        clock=lambda: NOW,
    )

    response = await service.recommend(
        USER_ID,
        RecommendationRequestDTO(
            items=[{"name": "Spinach", "quantity_g": 200, "hours_to_expire": 6}]
        ),
    )

    detail = response.items[0].rescued_details[0]
    assert detail.rescued_g == 200
    assert detail.expiring_g == 200
    assert detail.expires_at == NOW + timedelta(hours=6)
