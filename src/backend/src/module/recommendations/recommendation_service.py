"""Read-only loading and orchestration for recommendation providers."""

from datetime import UTC, datetime
from decimal import Decimal
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.model.enum_model import InventoryBatchStatus, InventoryBatchType
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
    UserRecommendationContext,
)


class RecommendationUserNotFoundError(LookupError):
    """Raised when no user can own the requested recommendation evaluation."""


class RecommendationService:
    """Load live ORM data once, then call an interchangeable provider contract."""

    def __init__(
        self, db_session: AsyncSession, provider: RecommendationProvider
    ) -> None:
        self.db_session = db_session
        self.provider = provider

    async def recommend(
        self,
        user_id: UUID,
        criteria: RecommendationCriteria,
        limit: int,
        now: datetime | None = None,
    ) -> list[RankedRecommendation]:
        """Rank real seeded recipes against current inventory without any writes."""
        evaluation_time = now or datetime.now(UTC)
        user = await self._find_user(user_id)
        candidates = await self._load_candidates()
        inventory_snapshot = await self._load_inventory_snapshot(user_id)
        return self.provider.recommend(
            RecommendationRequest(
                user_context=UserRecommendationContext(
                    user_id=user.id,
                    preferences=user.preferences,
                ),
                inventory_snapshot=inventory_snapshot,
                candidate_recipes=candidates,
                criteria=criteria,
                limit=limit,
                now=evaluation_time,
            ),
        )

    async def _find_user(self, user_id: UUID) -> UserModel:
        result = await self.db_session.execute(
            select(UserModel).where(UserModel.id == user_id),
        )
        user = result.scalar_one_or_none()
        if user is None:
            raise RecommendationUserNotFoundError()
        return user

    async def _load_candidates(self) -> list[RecommendationCandidate]:
        result = await self.db_session.execute(
            select(RecipeModel, RecipeIngredientModel, MasterIngredientModel)
            .join(
                RecipeIngredientModel,
                RecipeIngredientModel.recipe_id == RecipeModel.id,
            )
            .join(
                MasterIngredientModel,
                MasterIngredientModel.id == RecipeIngredientModel.master_ingredient_id,
            )
            .order_by(
                RecipeModel.id,
                RecipeIngredientModel.created_at,
                RecipeIngredientModel.id,
            ),
        )
        grouped: dict[UUID, tuple[RecipeModel, list[RecipeIngredientCandidate]]] = {}
        for recipe, recipe_ingredient, ingredient in result.tuples().all():
            current = grouped.get(recipe.id)
            if current is None:
                current = (recipe, [])
                grouped[recipe.id] = current
            current[1].append(
                RecipeIngredientCandidate(
                    master_ingredient_id=ingredient.id,
                    name=ingredient.name,
                    required_quantity=recipe_ingredient.required_quantity,
                    unit=recipe_ingredient.unit,
                    is_optional=recipe_ingredient.is_optional,
                )
            )
        return [
            RecommendationCandidate(
                recipe_id=recipe.id,
                name=recipe.name,
                default_servings=recipe.default_servings,
                estimated_cooking_minutes=recipe.estimated_cooking_minutes,
                ingredients=tuple(ingredients),
            )
            for recipe, ingredients in grouped.values()
        ]

    async def _load_inventory_snapshot(self, user_id: UUID) -> InventorySnapshot:
        result = await self.db_session.execute(
            select(InventoryBatchModel).where(
                InventoryBatchModel.user_id == user_id,
                InventoryBatchModel.batch_type == InventoryBatchType.RAW_INGREDIENT,
                InventoryBatchModel.status == InventoryBatchStatus.ACTIVE,
                InventoryBatchModel.current_quantity > 0,
                InventoryBatchModel.master_ingredient_id.is_not(None),
            ),
        )
        return InventorySnapshot(
            batches=tuple(
                InventorySnapshotBatch(
                    batch_id=batch.id,
                    master_ingredient_id=batch.master_ingredient_id,
                    current_quantity=Decimal(str(batch.current_quantity)),
                    unit=batch.unit,
                    expires_at=batch.expires_at,
                    created_at=batch.created_at,
                )
                for batch in result.scalars().all()
                if batch.master_ingredient_id is not None
            ),
        )
