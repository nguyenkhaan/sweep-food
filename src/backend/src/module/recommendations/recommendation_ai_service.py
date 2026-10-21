"""AI-backed recommendation orchestration for authenticated users."""

from collections.abc import Callable
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.concurrency import run_in_threadpool

from AI.catalog.master_index import merge_pantry_items, normalize
from AI.recommendation.contextual_features import URGENT_HOURS
from AI.recommendation.engine import (
    EngineRecommendation,
    EngineRescuedItem,
    RecommendationEngine,
)
from src.model.enum_model import InventoryBatchStatus, MeasurementUnit
from src.model.inventory_batch_model import InventoryBatchModel
from src.model.master_ingredient_model import MasterIngredientModel
from src.model.recipe_model import RecipeModel
from src.module.recommendations.recommendation_dto import (
    MockRecommendationAnalysisDTO,
    RecommendationIngredientDTO,
    RecommendationItemDTO,
    RecommendationListResponseDTO,
    RecommendationPantryItemDTO,
    RecommendationRankingFeaturesDTO,
    RecommendationRequestDTO,
    RecommendationRescuedItemDTO,
    RecommendationTimingsDTO,
)
from src.module.recommendations.recommendation_mapper import to_recipe_summary
from src.service.fefo_service import (
    FEFOCandidate,
    FEFOService,
    are_units_compatible,
    convert_quantity,
)

# Batches expiring inside the AI urgency window count as rescued when cooked.
_RESCUE_WINDOW = timedelta(hours=URGENT_HOURS)


@dataclass(frozen=True, slots=True)
class _StockBatch:
    """One active batch reduced to what pantry enrichment and rescue need."""

    batch_id: UUID
    source_code: str | None
    grams: float | None
    expires_at: datetime | None
    created_at: datetime


_StockByName = dict[str, list[_StockBatch]]


class RecommendationAIService:
    """Forward structured requests and map AI rankings to backend recipes."""

    def __init__(
        self,
        db_session: AsyncSession,
        engine: RecommendationEngine,
        clock: Callable[[], datetime] | None = None,
    ) -> None:
        self._db_session = db_session
        self._engine = engine
        self._clock = clock or (lambda: datetime.now(UTC))
        self._fefo = FEFOService()

    async def recommend(
        self,
        _user_id: UUID,
        body: RecommendationRequestDTO,
    ) -> RecommendationListResponseDTO:
        """Return calibrated AI rankings backed by the backend recipe catalog."""
        now = self._clock()
        stock = await self._load_stock(_user_id) if body.items else {}
        effective_request = _with_saved_stock(body, stock, now)
        ai_response = await run_in_threadpool(
            self._engine.recommend,
            effective_request,
        )

        warnings: list[str] = []
        recipes = await self._load_recipes(
            [recommendation.id for recommendation in ai_response.recommendations]
        )
        recipe_by_id = {recipe.id: recipe for recipe in recipes}
        pantry_by_name = {normalize(item.name): item for item in effective_request.items}
        items: list[RecommendationItemDTO] = []
        for recommendation in ai_response.recommendations:
            recipe = recipe_by_id.get(recommendation.id)
            if recipe is None:
                warnings.append(f"UNKNOWN_RECIPE_ID:{recommendation.id}")
                continue
            rescued_details = [
                detail
                for requirement in recommendation.rescued_requirements
                if (
                    detail := self._rescue_detail(
                        requirement,
                        pantry_by_name,
                        stock,
                        now,
                    )
                )
                is not None
            ]
            items.append(
                self._map_recommendation(
                    recommendation,
                    recipe,
                    rescued_details,
                    rank=len(items) + 1,
                )
            )

        return RecommendationListResponseDTO(
            request=effective_request,
            contract_version=ai_response.contract_version,
            model_version=ai_response.model_version,
            catalog_revision=ai_response.catalog_revision,
            ranker_model=ai_response.ranker_model,
            timings=RecommendationTimingsDTO(**ai_response.timings.model_dump()),
            analysis=MockRecommendationAnalysisDTO(
                intent="meal_recommendation",
                summary=(
                    "Recommendations were ranked from the supplied pantry and "
                    "preferences."
                ),
                is_mock=False,
            ),
            items=items,
            warnings=warnings,
        )

    async def _load_stock(self, user_id: UUID) -> _StockByName:
        """Group the user's active batches by normalized pantry name."""
        result = await self._db_session.execute(
            select(
                InventoryBatchModel.id,
                InventoryBatchModel.custom_name,
                MasterIngredientModel.name,
                MasterIngredientModel.source_code,
                InventoryBatchModel.current_quantity,
                InventoryBatchModel.unit,
                InventoryBatchModel.expires_at,
                InventoryBatchModel.created_at,
            )
            .outerjoin(
                MasterIngredientModel,
                MasterIngredientModel.id == InventoryBatchModel.master_ingredient_id,
            )
            .where(
                InventoryBatchModel.user_id == user_id,
                InventoryBatchModel.status == InventoryBatchStatus.ACTIVE,
                InventoryBatchModel.current_quantity > 0,
            )
        )
        stock: _StockByName = {}
        for (
            batch_id,
            custom_name,
            ingredient_name,
            source_code,
            quantity,
            unit,
            expires_at,
            created_at,
        ) in result.all():
            pantry_name = custom_name or ingredient_name
            if pantry_name is None:
                continue
            stock.setdefault(normalize(pantry_name), []).append(
                _StockBatch(
                    batch_id=batch_id,
                    source_code=source_code,
                    grams=_grams(quantity, unit),
                    expires_at=expires_at,
                    created_at=created_at,
                )
            )
        return stock

    async def _load_recipes(self, recipe_ids: list[UUID]) -> list[RecipeModel]:
        if not recipe_ids:
            return []
        result = await self._db_session.execute(
            select(RecipeModel).where(RecipeModel.id.in_(recipe_ids))
        )
        return list(result.scalars().all())

    def _rescue_detail(
        self,
        requirement: EngineRescuedItem,
        pantry_by_name: dict[str, RecommendationPantryItemDTO],
        stock: _StockByName,
        now: datetime,
    ) -> RecommendationRescuedItemDTO | None:
        """Split the recipe's need over batches FEFO-first and keep the urgent part."""
        key = normalize(requirement.name)
        pantry_item = pantry_by_name.get(key)
        name = pantry_item.name if pantry_item is not None else requirement.name
        code = pantry_item.code if pantry_item is not None else None
        deadline = now + _RESCUE_WINDOW
        candidates = [
            FEFOCandidate(
                batch_id=batch.batch_id,
                current_quantity=batch.grams,
                unit=MeasurementUnit.GRAM,
                expires_at=batch.expires_at,
                created_at=batch.created_at,
            )
            for batch in stock.get(key, [])
            if batch.grams is not None
        ]
        if candidates:
            allocation = self._fefo.allocate(
                requirement.required_g,
                MeasurementUnit.GRAM,
                candidates,
                now,
            )
            urgent_allocations = [
                item
                for item in allocation.allocations
                if item.expires_at is not None and item.expires_at <= deadline
            ]
            rescued_g = sum(item.recipe_quantity for item in urgent_allocations)
            expiring_g = sum(
                candidate.current_quantity
                for candidate in candidates
                if candidate.expires_at is not None
                and now < candidate.expires_at <= deadline
            )
            expires_at = min(
                (item.expires_at for item in urgent_allocations if item.expires_at),
                default=None,
            )
        elif pantry_item is not None and pantry_item.hours_to_expire is not None:
            # Items without saved stock keep the client-supplied urgency.
            rescued_g = min(requirement.required_g, pantry_item.quantity_g)
            expiring_g = pantry_item.quantity_g
            expires_at = now + timedelta(hours=pantry_item.hours_to_expire)
        else:
            return None
        if rescued_g <= 0:
            return None
        return RecommendationRescuedItemDTO(
            name=name,
            code=code,
            required_g=round(requirement.required_g, 1),
            rescued_g=round(rescued_g, 1),
            expiring_g=round(expiring_g, 1),
            expires_at=expires_at,
        )

    @staticmethod
    def _map_recommendation(
        recommendation: EngineRecommendation,
        recipe: RecipeModel,
        rescued_details: list[RecommendationRescuedItemDTO],
        *,
        rank: int,
    ) -> RecommendationItemDTO:
        return RecommendationItemDTO(
            recipe_id=recipe.id,
            recipe_name=recipe.name,
            rank=rank,
            rank_score=recommendation.rank_score,
            ranking_features=RecommendationRankingFeaturesDTO(
                **recommendation.ranking_features.model_dump()
            ),
            matched_ingredients=[
                RecommendationIngredientDTO(**item.model_dump())
                for item in recommendation.matched_ingredients
            ],
            missing_ingredients=[
                RecommendationIngredientDTO(**item.model_dump())
                for item in recommendation.missing_ingredients
            ],
            optional_ingredients=[
                RecommendationIngredientDTO(**item.model_dump())
                for item in recommendation.optional_ingredients
            ],
            rescued_items=_unique_names(recommendation.rescued_items),
            rescued_details=rescued_details,
            status_badge=recommendation.status_badge,
            explanation="AI-ranked from pantry availability, expiry, and shopping gaps.",
            provider="SWEEP_FOOD_AI",
            recipe_summary=to_recipe_summary(recipe),
        )


def _with_saved_stock(
    request: RecommendationRequestDTO,
    stock: _StockByName,
    now: datetime,
) -> RecommendationRequestDTO:
    """Merge per-batch pantry entries and apply server-authoritative stock."""
    if not request.items:
        return request
    merged_items = merge_pantry_items(item.model_dump() for item in request.items)
    items = [
        _with_saved_batches(
            RecommendationPantryItemDTO(**item),
            stock.get(normalize(item["name"]), []),
            now,
        )
        for item in merged_items
    ]
    return request.model_copy(update={"items": items})


def _with_saved_batches(
    item: RecommendationPantryItemDTO,
    batches: list[_StockBatch],
    now: datetime,
) -> RecommendationPantryItemDTO:
    """Return one pantry item with saved total grams, earliest expiry, and code."""
    if not batches:
        return item
    usable = [
        batch
        for batch in batches
        if batch.expires_at is None or batch.expires_at > now
    ]
    if not usable:
        return item.model_copy(update={"hours_to_expire": 0.0})
    update: dict[str, object] = {
        "hours_to_expire": _hours_until(_earliest_expiry(usable), now),
    }
    grams = sum(batch.grams for batch in usable if batch.grams is not None)
    if grams > 0:
        update["quantity_g"] = round(grams, 1)
    source_code = next((batch.source_code for batch in usable if batch.source_code), None)
    if source_code is not None:
        update["code"] = source_code
    return item.model_copy(update=update)


def _earliest_expiry(batches: list[_StockBatch]) -> datetime | None:
    """Select the earliest known batch expiry."""
    return min(
        (batch.expires_at for batch in batches if batch.expires_at is not None),
        default=None,
    )


def _hours_until(expires_at: datetime | None, now: datetime) -> float | None:
    if expires_at is None:
        return None
    return round(max(0.0, (expires_at - now).total_seconds() / 3600), 1)


def _grams(quantity: float, unit: MeasurementUnit) -> float | None:
    """Convert mass to grams and volume at water density; count units stay unknown."""
    for reference_unit in (MeasurementUnit.GRAM, MeasurementUnit.ML):
        if are_units_compatible(unit, reference_unit):
            return convert_quantity(quantity, unit, reference_unit)
    return None


def _unique_names(names: list[str]) -> list[str]:
    """Drop repeated names, comparing them normalized, and keep first-seen order."""
    seen: set[str] = set()
    unique: list[str] = []
    for name in names:
        key = normalize(name)
        if key not in seen:
            seen.add(key)
            unique.append(name)
    return unique
