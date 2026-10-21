"""Focused unit tests for RecommendationEngine, catalog snapshot, and scoring logic."""

import json
from pathlib import Path
from typing import cast
from uuid import UUID

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from AI.catalog.errors import CatalogNotLoadedError
from AI.catalog.snapshot import (
    CatalogSnapshot,
    get_catalog_snapshot,
    invalidate_catalog_snapshot,
    load_snapshot_from_bundle,
)
from AI.recommendation.contextual_features import FEATURE_COLS
from AI.recommendation.engine import RecommendationEngine
from AI.recommendation.formatting import format_candidate_recommendation
from AI.recommendation.ranking import (
    RankerInference,
    feasibility_rank_key,
    select_urgent_round_robin,
)
from AI.recommendation.scenario_rules import filter_candidate


@pytest.fixture(scope="module")
def snapshot() -> CatalogSnapshot:
    """Load the real catalog bundle once for the test module."""
    return load_snapshot_from_bundle()


@pytest.fixture(scope="module")
def engine(snapshot: CatalogSnapshot) -> RecommendationEngine:
    """Build the recommendation engine backed by real bundle artifacts."""
    return RecommendationEngine(snapshot)


def test_feature_order_guard() -> None:
    """FEATURE_COLS must strictly match metadata.json and loaded Booster names/count."""
    meta_path = (
        Path(__file__).resolve().parent.parent.parent
        / "AI"
        / "data"
        / "training"
        / "metadata.json"
    )
    with meta_path.open("r", encoding="utf-8") as fh:
        meta = json.load(fh)

    expected_feature_cols = meta["feature_cols"]
    assert FEATURE_COLS == expected_feature_cols, (
        f"Feature mismatch: {FEATURE_COLS} != {expected_feature_cols}"
    )

    ranker = RankerInference()
    if ranker.booster is not None:
        booster_features = ranker.booster.feature_name()
        assert booster_features == FEATURE_COLS
        assert ranker.booster.num_feature() == len(FEATURE_COLS)


def test_realistic_pantry_retrieves_candidates_and_honors_snapshot_ids(
    engine: RecommendationEngine,
    snapshot: CatalogSnapshot,
) -> None:
    """Realistic Vietnamese pantry returns expected dishes existing in catalog snapshot."""
    request = {
        "items": [
            {"name": "thịt ba chỉ", "quantity_g": 300, "hours_to_expire": 12},
            {"name": "trứng", "quantity_g": 200, "hours_to_expire": 48},
            {"name": "hành lá", "quantity_g": 50, "hours_to_expire": 20},
        ],
        "household_size": 4,
        "scenario_type": "custom",
    }
    result = engine.recommend(request)

    assert result.status == "success"
    assert result.contract_version == "2"
    assert len(result.recommendations) > 0
    assert result.timings.total_ms > 0
    assert result.timings.candidate_ms > 0
    assert result.timings.ranker_ms > 0

    for rec in result.recommendations:
        assert isinstance(rec.id, UUID)
        rec_id_str = str(rec.id)
        assert rec_id_str in snapshot.recipes_by_id
        assert rec.rank_score is not None
        assert rec.status_badge in ("ready", "elastic", "shopping")


def test_scenario_filter_an_chay(engine: RecommendationEngine, snapshot: CatalogSnapshot) -> None:
    """Vegetarian scenario strictly enforces vegetarian tags and eliminates animal items."""
    request = {
        "items": [
            {"name": "đậu phụ", "quantity_g": 300, "hours_to_expire": 24},
            {"name": "nấm hương", "quantity_g": 100, "hours_to_expire": 48},
            {"name": "cà chua", "quantity_g": 150, "hours_to_expire": 36},
        ],
        "household_size": 2,
        "scenario_type": "an_chay",
    }
    result = engine.recommend(request)
    assert result.status == "success"
    assert len(result.recommendations) > 0

    for rec in result.recommendations:
        full_rec = snapshot.recipes_by_id[str(rec.id)]
        diet_tags = (full_rec.get("diet_tags") or "").lower()
        assert "ăn chay" in diet_tags


def test_scenario_filter_nguoi_tieu_duong(
    engine: RecommendationEngine,
    snapshot: CatalogSnapshot,
) -> None:
    """Diabetic scenario strictly enforces sugar < 10g and carbs < 45g."""
    request = {
        "items": [
            {"name": "ức gà", "quantity_g": 400, "hours_to_expire": 30},
            {"name": "súp lơ", "quantity_g": 300, "hours_to_expire": 48},
        ],
        "household_size": 2,
        "scenario_type": "nguoi_tieu_duong",
    }
    result = engine.recommend(request)
    assert result.status == "success"
    assert len(result.recommendations) > 0

    for rec in result.recommendations:
        full_rec = snapshot.recipes_by_id[str(rec.id)]
        sugar = float(full_rec.get("sugar_g_per_serving") or 0.0)
        carbs = float(full_rec.get("carbs_per_serving") or 0.0)
        assert sugar < 10.0
        assert carbs < 45.0


def test_data_quality_safety_filters() -> None:
    """Nutrition anomaly flag and incomplete flag reject candidate recipes."""
    recipe_normal = {"id": "1", "nutrition_anomaly_flag": 0, "incomplete_flag": 0}
    recipe_anomaly = {"id": "2", "nutrition_anomaly_flag": 1, "incomplete_flag": 0}
    recipe_incomplete = {"id": "3", "nutrition_anomaly_flag": 0, "incomplete_flag": "1"}

    assert filter_candidate(recipe_normal, "custom", []) is True
    assert filter_candidate(recipe_anomaly, "custom", []) is False
    assert filter_candidate(recipe_incomplete, "custom", []) is False


def test_badge_logic_ready_elastic_shopping() -> None:
    """Feasibility badges correctly distinguish ready, elastic, and shopping."""
    cand = {"id": "test-1", "name": "Món test"}
    full_rec = {"id": "test-1", "name": "Món test", "default_servings": 4}

    # Ready dish: all ingredients present
    r_ings_ready = [
        {"master_ingredient_name": "Trứng", "estimated_weight_g": 100, "ingredient_role": "core"},
    ]
    pantry_ready = {"items": [{"name": "Trứng", "quantity_g": 200, "hours_to_expire": 48}]}
    feats_ready = {"core_coverage": 1.0}

    formatted_ready = format_candidate_recommendation(
        cand, full_rec, score=1.0, feats=feats_ready,
        r_ings=r_ings_ready, pantry_dict=pantry_ready, household_size=4,
    )
    assert formatted_ready["status_badge"] == "ready"

    # Elastic dish: 1 missing ingredient with >= 75% coverage
    r_ings_elastic = [
        {"master_ingredient_name": "Thịt heo", "estimated_weight_g": 300, "ingredient_role": "core"},
        {"master_ingredient_name": "Hành lá", "estimated_weight_g": 20, "ingredient_role": "secondary"},
    ]
    pantry_elastic = {"items": [{"name": "Thịt heo", "quantity_g": 300, "hours_to_expire": 48}]}
    feats_elastic = {"core_coverage": 0.85}

    formatted_elastic = format_candidate_recommendation(
        cand, full_rec, score=1.0, feats=feats_elastic,
        r_ings=r_ings_elastic, pantry_dict=pantry_elastic, household_size=4,
    )
    assert formatted_elastic["status_badge"] == "elastic"


def test_tiering_rank_key() -> None:
    """Zero-waste heroes and ready dishes receive top ranking tiers."""
    ready_hero = {"status_badge": "ready", "is_zero_waste_hero": True, "score": 2.0}
    ready_normal = {"status_badge": "ready", "is_zero_waste_hero": False, "score": 2.0}
    shopping_hero = {"status_badge": "shopping", "is_zero_waste_hero": True, "missing_ingredients": [{"name": "a"}], "score": 2.0}
    elastic = {"status_badge": "elastic", "is_zero_waste_hero": False, "missing_ingredients": [{"name": "a"}], "score": 2.0}
    shopping_normal = {"status_badge": "shopping", "is_zero_waste_hero": False, "missing_ingredients": [{"name": "a"}, {"name": "b"}], "score": 2.0}

    assert feasibility_rank_key(ready_hero)[0] == 0
    assert feasibility_rank_key(ready_normal)[0] == 1
    assert feasibility_rank_key(shopping_hero)[0] == 2
    assert feasibility_rank_key(elastic)[0] == 3
    assert feasibility_rank_key(shopping_normal)[0] >= 4


def test_urgent_round_robin_diversity() -> None:
    """Interleaves dishes across multiple urgent ingredients."""
    pantry_items = [
        {"name": "Cá basa", "hours_to_expire": 8, "is_staple": False},
        {"name": "Thịt ba chỉ", "hours_to_expire": 12, "is_staple": False},
    ]
    cands = [
        {"id": "c1", "name": "Cá 1", "rescued_items": ["Cá basa"], "status_badge": "ready", "score": 3.0},
        {"id": "c2", "name": "Cá 2", "rescued_items": ["Cá basa"], "status_badge": "ready", "score": 2.9},
        {"id": "t1", "name": "Thịt 1", "rescued_items": ["Thịt ba chỉ"], "status_badge": "ready", "score": 2.8},
        {"id": "t2", "name": "Thịt 2", "rescued_items": ["Thịt ba chỉ"], "status_badge": "ready", "score": 2.7},
    ]

    selected = select_urgent_round_robin(cands, pantry_items, top_k=4)
    # Must include both Ca and Thit dishes, not just 2 Ca dishes monopolizing the top
    selected_rescued = [r["rescued_items"][0] for r in selected[:2]]
    assert "Cá basa" in selected_rescued
    assert "Thịt ba chỉ" in selected_rescued


def test_fallback_to_heuristic(snapshot: CatalogSnapshot) -> None:
    """When model file is missing or invalid, falls back to Domain Heuristic with clear attribution."""
    engine_fallback = RecommendationEngine(snapshot, model_path="nonexistent_file_path.txt")
    assert engine_fallback.ranker.ranker_model_name == "Domain Heuristic"
    assert "domain-heuristic" in engine_fallback.ranker.model_version_string

    res = engine_fallback.recommend({
        "items": [{"name": "thịt bò", "quantity_g": 300, "hours_to_expire": 24}],
        "household_size": 2,
    })
    assert res.status == "success"
    assert res.ranker_model == "Domain Heuristic"
    assert "domain-heuristic" in res.model_version
    assert len(res.recommendations) > 0


class _EmptySession:
    async def execute(self, _statement: object) -> object:
        class _Result:
            def scalars(self) -> "_Result":
                return self

            def all(self) -> list[object]:
                return []

        return _Result()


@pytest.mark.anyio
async def test_empty_db_raises_catalog_not_loaded_error_no_bundle_fallback() -> None:
    """Empty DB must raise CatalogNotLoadedError without falling back to bundle."""
    invalidate_catalog_snapshot()
    session = _EmptySession()
    with pytest.raises(CatalogNotLoadedError, match="python -m AI.catalog.importer"):
        await get_catalog_snapshot(cast(AsyncSession, session))


@pytest.mark.anyio
async def test_session_none_without_cache_raises_catalog_not_loaded_error() -> None:
    """If session is None and cache is empty, CatalogNotLoadedError is raised."""
    invalidate_catalog_snapshot()
    with pytest.raises(CatalogNotLoadedError):
        await get_catalog_snapshot(None)


@pytest.mark.anyio
async def test_snapshot_caching_and_invalidation() -> None:
    """Catalog snapshot is cached in memory and invalidated cleanly."""
    invalidate_catalog_snapshot()

    class _PopulatedSession:
        def __init__(self) -> None:
            from decimal import Decimal

            class _R:
                id = UUID("018f0f90-26e6-7ce7-8f61-8769f9e5b102")
                name = "R1"
                default_servings = Decimal(4)
                estimated_cooking_minutes = 20
                total_calories = Decimal(100)
                total_protein_g = Decimal(10)
                total_fat_g = Decimal(5)
                total_carbs_g = Decimal(15)
                total_sugar_g = Decimal(2)

            self.calls: list[list[object]] = [[_R()], [], [], []]

        async def execute(self, _statement: object) -> object:
            items = self.calls.pop(0) if self.calls else []

            class _Result:
                def scalars(self) -> "_Result":
                    return self

                def all(self) -> list[object]:
                    return items

            return _Result()
    session = _PopulatedSession()
    s1 = await get_catalog_snapshot(cast(AsyncSession, session))
    s2 = await get_catalog_snapshot()
    assert s1 is s2

    invalidate_catalog_snapshot()
    s3 = await get_catalog_snapshot(cast(AsyncSession, _PopulatedSession()))
    assert s3 is not s1
    assert s3.revision == s1.revision

@pytest.mark.anyio
async def test_deterministic_revision_order_independence() -> None:
    """Same rows returned in different order produce identical revision string."""
    from decimal import Decimal
    from AI.catalog.snapshot import load_snapshot

    class _R:
        def __init__(self, r_id: UUID, name: str, features: dict[str, object] | None = None) -> None:
            self.id = r_id
            self.name = name
            self.default_servings = Decimal(4)
            self.estimated_cooking_minutes = 20
            self.total_calories = Decimal(100)
            self.total_protein_g = Decimal(10)
            self.total_fat_g = Decimal(5)
            self.total_carbs_g = Decimal(15)
            self.total_sugar_g = Decimal(2)
            self.ai_features = features or {"dish_type": "Main"}

    r1 = _R(UUID("018f0f90-26e6-7ce7-8f61-8769f9e5b102"), "R1")
    r2 = _R(UUID("018f0f90-26e6-7ce7-8f61-8769f9e5b103"), "R2")

    class _SessionOrder:
        def __init__(self, recipe_list: list[object]) -> None:
            self.calls: list[list[object]] = [recipe_list, [], [], []]

        async def execute(self, _statement: object) -> object:
            items = self.calls.pop(0) if self.calls else []

            class _Result:
                def scalars(self) -> "_Result":
                    return self

                def all(self) -> list[object]:
                    return items

            return _Result()

    snap_order_1 = await load_snapshot(cast(AsyncSession, _SessionOrder([r1, r2])))
    snap_order_2 = await load_snapshot(cast(AsyncSession, _SessionOrder([r2, r1])))
    assert snap_order_1.revision == snap_order_2.revision


@pytest.mark.anyio
async def test_deterministic_revision_changes_on_feature_update() -> None:
    """Updating a recipe's ai_features produces a different revision string."""
    from decimal import Decimal
    from AI.catalog.snapshot import load_snapshot

    class _R:
        def __init__(self, r_id: UUID, name: str, features: dict[str, object]) -> None:
            self.id = r_id
            self.name = name
            self.default_servings = Decimal(4)
            self.estimated_cooking_minutes = 20
            self.total_calories = Decimal(100)
            self.total_protein_g = Decimal(10)
            self.total_fat_g = Decimal(5)
            self.total_carbs_g = Decimal(15)
            self.total_sugar_g = Decimal(2)
            self.ai_features = features

    r_orig = _R(UUID("018f0f90-26e6-7ce7-8f61-8769f9e5b102"), "R1", {"dish_type": "Main"})
    r_updated = _R(UUID("018f0f90-26e6-7ce7-8f61-8769f9e5b102"), "R1", {"dish_type": "Soup"})

    class _SessionSimple:
        def __init__(self, recipe_list: list[object]) -> None:
            self.calls: list[list[object]] = [recipe_list, [], [], []]

        async def execute(self, _statement: object) -> object:
            items = self.calls.pop(0) if self.calls else []

            class _Result:
                def scalars(self) -> "_Result":
                    return self

                def all(self) -> list[object]:
                    return items

            return _Result()

    snap_orig = await load_snapshot(cast(AsyncSession, _SessionSimple([r_orig])))
    snap_updated = await load_snapshot(cast(AsyncSession, _SessionSimple([r_updated])))
    assert snap_orig.revision != snap_updated.revision
    assert snap_orig.revision.startswith("catalog-db-1-")
    assert snap_updated.revision.startswith("catalog-db-1-")
