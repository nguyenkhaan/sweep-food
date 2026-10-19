"""AI-backed recommendation orchestration for authenticated users."""

from collections.abc import Callable
from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.concurrency import run_in_threadpool

from AI.recommendation.engine import EngineRecommendation, RecommendationEngine
from src.model.enum_model import InventoryBatchStatus
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
    RecommendationTimingsDTO,
)
from src.module.recommendations.recommendation_mapper import to_recipe_summary


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

    async def recommend(
        self,
        _user_id: UUID,
        body: RecommendationRequestDTO,
    ) -> RecommendationListResponseDTO:
        """Return calibrated AI rankings backed by the backend recipe catalog."""
        effective_request = await self._with_saved_expiries(_user_id, body)
        ai_response = await run_in_threadpool(
            self._engine.recommend,
            effective_request,
        )

        warnings: list[str] = []
        recipes = await self._load_recipes(
            [recommendation.id for recommendation in ai_response.recommendations]
        )
        recipe_by_id = {recipe.id: recipe for recipe in recipes}
        items: list[RecommendationItemDTO] = []
        for recommendation in ai_response.recommendations:
            recipe = recipe_by_id.get(recommendation.id)
            if recipe is None:
                warnings.append(f"UNKNOWN_RECIPE_ID:{recommendation.id}")
                continue
            items.append(
                self._map_recommendation(
                    recommendation,
                    recipe,
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

    async def _with_saved_expiries(
        self,
        user_id: UUID,
        request: RecommendationRequestDTO,
    ) -> RecommendationRequestDTO:
        """Replace client urgency with the earliest expiry in owned active stock."""
        if not request.items:
            return request
        result = await self._db_session.execute(
            select(
                InventoryBatchModel.custom_name,
                MasterIngredientModel.name,
                InventoryBatchModel.expires_at,
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
        saved_expiries = _earliest_expiries(
            [(row[0], row[1], row[2]) for row in result.all()]
        )
        now = self._clock()
        items = [
            _with_saved_expiry(item, saved_expiries, now) for item in request.items
        ]
        return request.model_copy(update={"items": items})

    async def _load_recipes(self, recipe_ids: list[UUID]) -> list[RecipeModel]:
        if not recipe_ids:
            return []
        result = await self._db_session.execute(
            select(RecipeModel).where(RecipeModel.id.in_(recipe_ids))
        )
        return list(result.scalars().all())

    @staticmethod
    def _map_recommendation(
        recommendation: EngineRecommendation,
        recipe: RecipeModel,
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
            rescued_items=recommendation.rescued_items,
            status_badge=recommendation.status_badge,
            explanation="AI-ranked from pantry availability, expiry, and shopping gaps.",
            provider="SWEEP_FOOD_AI",
            recipe_summary=to_recipe_summary(recipe),
        )


def _earliest_expiries(
    rows: list[tuple[str | None, str | None, datetime | None]],
) -> dict[str, datetime | None]:
    """Select the earliest known batch expiry for each normalized pantry name."""
    expiries: dict[str, datetime | None] = {}
    for custom_name, ingredient_name, expires_at in rows:
        pantry_name = custom_name or ingredient_name
        if pantry_name is None:
            continue
        normalized_name = _normalize_name(pantry_name)
        current_expiry = expiries.get(normalized_name)
        if normalized_name not in expiries or (
            expires_at is not None
            and (current_expiry is None or expires_at < current_expiry)
        ):
            expiries[normalized_name] = expires_at
    return expiries


def _with_saved_expiry(
    item: RecommendationPantryItemDTO,
    saved_expiries: dict[str, datetime | None],
    now: datetime,
) -> RecommendationPantryItemDTO:
    """Return one pantry item with server-authoritative expiry urgency when found."""
    normalized_name = _normalize_name(item.name)
    if normalized_name not in saved_expiries:
        return item
    expires_at = saved_expiries[normalized_name]
    hours_to_expire = (
        None
        if expires_at is None
        else round(max(0.0, (expires_at - now).total_seconds() / 3600), 1)
    )
    return item.model_copy(update={"hours_to_expire": hours_to_expire})


def _normalize_name(value: str) -> str:
    """Normalize an inventory name for case-insensitive request matching."""
    return " ".join(value.casefold().split())
