"""Database orchestration for cooking previews and session completion."""

from datetime import UTC, datetime, timedelta
from decimal import Decimal
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from src.model.cooking_consumption_model import CookingConsumptionModel
from src.model.cooking_session_model import CookingSessionModel
from src.model.enum_model import (
    CookingSessionStatus,
    ExpirationSource,
    InventoryBatchStatus,
    InventoryBatchType,
    InventoryLedgerEventType,
    InventorySource,
)
from src.model.inventory_batch_model import InventoryBatchModel
from src.model.inventory_ledger_entry_model import InventoryLedgerEntryModel
from src.model.master_ingredient_model import MasterIngredientModel
from src.model.meal_plan_item_model import MealPlanItemModel
from src.model.meal_plan_model import MealPlanModel
from src.model.recipe_ingredient_model import RecipeIngredientModel
from src.model.recipe_model import RecipeModel
from src.module.cooking.cooking_dto import (
    CompleteCookingSessionRequestDTO,
    CookedLeftoverResponseDTO,
    CookingConsumptionDTO,
    CookingCompletionResponseDTO,
    CookingHistoryDetailResponseDTO,
    CookingHistoryListResponseDTO,
    CookingHistorySummaryDTO,
    CookingPreviewRequestDTO,
    CookingPreviewResponseDTO,
    CookingSessionDTO,
    CreateCookedLeftoverRequestDTO,
    CreateCookingSessionRequestDTO,
)
from src.module.cooking.cooking_helper import (
    CookingCompletionConflictError,
    CookingDomainError,
    CookingHelper,
    CookingSessionNotFoundError,
    InsufficientInventoryError,
    MealPlanItemNotFoundError,
    RecipeNotFoundError,
)
from src.service.fefo_service import FEFOService


class CookingService:
    """Orchestrate ownership-safe cooking queries and one transaction per completion."""

    def __init__(self, db_session: AsyncSession, fefo_service: FEFOService) -> None:
        """Store the request-scoped database session and cooking helpers."""
        self.db_session = db_session
        self.helper = CookingHelper(db_session, fefo_service)

    async def preview(
        self,
        user_id: UUID,
        request: CookingPreviewRequestDTO,
    ) -> CookingPreviewResponseDTO:
        """Return an ownership-safe, serving-scaled preview for one planned meal."""
        try:
            meal_plan_item = await self._find_meal_plan_item(
                user_id,
                request.meal_plan_item_id,
            )
            recipe = await self._find_recipe(meal_plan_item.recipe_id)
            recipe_ingredients = await self._find_recipe_ingredients(recipe.id)
            batches = await self._find_active_batches(
                user_id,
                [
                    ingredient.master_ingredient_id
                    for ingredient, _ in recipe_ingredients
                ],
            )
        except SQLAlchemyError:
            await self.db_session.rollback()
            raise
        return self.helper.build_preview(
            recipe,
            recipe_ingredients,
            batches,
            meal_plan_item.servings,
        )

    async def create_session(
        self,
        user_id: UUID,
        request: CreateCookingSessionRequestDTO,
    ) -> CookingSessionDTO:
        """Create a planned session from an owned meal-plan item without deduction."""
        try:
            meal_plan_item = await self._find_meal_plan_item(
                user_id,
                request.meal_plan_item_id,
            )
            recipe = await self._find_recipe(meal_plan_item.recipe_id)
            recipe_ingredients = await self._find_recipe_ingredients(recipe.id)
            batches = await self._find_active_batches(
                user_id,
                [
                    ingredient.master_ingredient_id
                    for ingredient, _ in recipe_ingredients
                ],
            )
            preview = self.helper.build_preview(
                recipe,
                recipe_ingredients,
                batches,
                meal_plan_item.servings,
            )
            if preview.missing_ingredients:
                raise InsufficientInventoryError(
                    self.helper.insufficient_inventory_detail(
                        preview.missing_ingredients,
                    )
                )
            nutrition_snapshot = self.helper.scale_nutrition(
                recipe,
                Decimal(str(meal_plan_item.servings))
                / Decimal(str(recipe.default_servings)),
            ).model_dump()
            cooking_session = CookingSessionModel(
                user_id=user_id,
                recipe_id=recipe.id,
                meal_plan_item_id=meal_plan_item.id,
                servings=meal_plan_item.servings,
                status=CookingSessionStatus.PLANNED,
                nutrition_snapshot=nutrition_snapshot,
            )
            self.db_session.add(cooking_session)
            await self.db_session.commit()
            return self.helper.to_session_dto(cooking_session)
        except (CookingDomainError, SQLAlchemyError):
            await self.db_session.rollback()
            raise

    async def complete_session(
        self,
        user_id: UUID,
        session_id: UUID,
        idempotency_key: str,
        request: CompleteCookingSessionRequestDTO,
    ) -> CookingCompletionResponseDTO:
        """Atomically deduct locked batches and create auditable cooking records."""
        try:
            previous_session = await self._find_session_by_idempotency_key(
                user_id,
                idempotency_key,
            )
            if previous_session is not None:
                return await self._existing_completion_response(previous_session)

            cooking_session = await self._find_locked_session(user_id, session_id)
            previous_session = await self._find_session_by_idempotency_key(
                user_id,
                idempotency_key,
            )
            if previous_session is not None:
                return await self._existing_completion_response(previous_session)
            self._ensure_session_is_completable(cooking_session)

            recipe = await self._find_recipe(cooking_session.recipe_id)
            recipe_ingredients = await self._find_recipe_ingredients(recipe.id)
            locked_batches = await self._find_locked_batches(
                user_id,
                [
                    ingredient.master_ingredient_id
                    for ingredient, _ in recipe_ingredients
                ],
            )
            resolved_consumptions = self.helper.resolve_consumptions(
                cooking_session,
                recipe,
                recipe_ingredients,
                locked_batches,
                request,
            )
            cooking_session.idempotency_key = idempotency_key
            response = self.helper.apply_completion(
                cooking_session,
                recipe,
                locked_batches,
                resolved_consumptions,
                request.consumption_mode,
            )
            await self.db_session.commit()
            return response
        except IntegrityError as error:
            await self.db_session.rollback()
            raise CookingCompletionConflictError(
                "Cooking completion was already submitted",
            ) from error
        except (CookingDomainError, SQLAlchemyError):
            await self.db_session.rollback()
            raise

    async def create_leftover(
        self,
        user_id: UUID,
        session_id: UUID,
        request: CreateCookedLeftoverRequestDTO,
    ) -> CookedLeftoverResponseDTO:
        """Create a COOKED_FOOD batch linked to a completed cooking session."""
        try:
            cooking_session = await self._find_session_by_id(user_id, session_id)
            if cooking_session.status is not CookingSessionStatus.COMPLETED:
                raise CookingCompletionConflictError(
                    "Leftovers can only be created for completed cooking sessions",
                )
            recipe = await self._find_recipe(cooking_session.recipe_id)

            now = datetime.now(UTC)
            expires_at = request.expires_at
            expiration_source = (
                ExpirationSource.USER_OVERRIDE
                if expires_at is not None
                else ExpirationSource.ESTIMATED
            )
            if expires_at is None:
                expires_at = now + timedelta(days=3)

            leftover_batch = InventoryBatchModel(
                user_id=user_id,
                master_ingredient_id=None,
                custom_name=recipe.name,
                batch_type=InventoryBatchType.COOKED_FOOD,
                initial_quantity=request.quantity,
                current_quantity=request.quantity,
                unit=request.unit,
                storage_mode=request.storage_mode,
                status=InventoryBatchStatus.ACTIVE,
                expires_at=expires_at,
                expiration_source=expiration_source,
                note=request.note,
                source=InventorySource.LEFTOVER,
                source_cooking_session_id=cooking_session.id,
            )
            self.db_session.add(leftover_batch)
            await self.db_session.flush()

            ledger_entry = InventoryLedgerEntryModel(
                user_id=user_id,
                inventory_batch_id=leftover_batch.id,
                event_type=InventoryLedgerEventType.LEFTOVER_CREATED,
                quantity_before=0.0,
                quantity_delta=request.quantity,
                quantity_after=request.quantity,
                unit=request.unit,
                cooking_session_id=cooking_session.id,
            )
            self.db_session.add(ledger_entry)
            await self.db_session.commit()

            return CookedLeftoverResponseDTO(
                batch_id=leftover_batch.id,
                cooking_session_id=cooking_session.id,
                batch_type=leftover_batch.batch_type,
                quantity=leftover_batch.current_quantity,
                unit=leftover_batch.unit,
                storage_mode=leftover_batch.storage_mode,
                expires_at=leftover_batch.expires_at,
                created_at=leftover_batch.created_at,
            )
        except (CookingDomainError, SQLAlchemyError):
            await self.db_session.rollback()
            raise

    async def get_cooking_history(
        self,
        user_id: UUID,
    ) -> CookingHistoryListResponseDTO:
        """List all completed cooking sessions for the authenticated user."""
        try:
            result = await self.db_session.execute(
                select(CookingSessionModel)
                .where(
                    CookingSessionModel.user_id == user_id,
                    CookingSessionModel.status == CookingSessionStatus.COMPLETED,
                )
                .order_by(CookingSessionModel.completed_at.desc()),
            )
            sessions = list(result.scalars().all())
            recipe_ids = [s.recipe_id for s in sessions]
            recipes_by_id = {}
            if recipe_ids:
                recipes_result = await self.db_session.execute(
                    select(RecipeModel).where(RecipeModel.id.in_(recipe_ids)),
                )
                for recipe in recipes_result.scalars().all():
                    recipes_by_id[recipe.id] = recipe

            items = [
                CookingHistorySummaryDTO(
                    session_id=s.id,
                    recipe_id=s.recipe_id,
                    recipe_name=recipes_by_id[s.recipe_id].name
                    if s.recipe_id in recipes_by_id
                    else "Unknown Recipe",
                    servings=s.servings,
                    status=s.status,
                    completed_at=s.completed_at,
                )
                for s in sessions
            ]
            return CookingHistoryListResponseDTO(items=items)
        except SQLAlchemyError:
            await self.db_session.rollback()
            raise

    async def get_cooking_history_detail(
        self,
        user_id: UUID,
        session_id: UUID,
    ) -> CookingHistoryDetailResponseDTO:
        """Get detail of one completed cooking session, consumptions, and leftover."""
        try:
            cooking_session = await self._find_session_by_id(user_id, session_id)
            recipe = await self._find_recipe(cooking_session.recipe_id)

            consumptions_result = await self.db_session.execute(
                select(CookingConsumptionModel)
                .where(CookingConsumptionModel.cooking_session_id == cooking_session.id)
                .order_by(CookingConsumptionModel.created_at),
            )
            consumptions = [
                CookingConsumptionDTO(
                    recipe_ingredient_id=c.recipe_ingredient_id,
                    inventory_batch_id=c.inventory_batch_id,
                    quantity=c.quantity,
                    unit=c.unit,
                )
                for c in consumptions_result.scalars().all()
            ]

            leftover_result = await self.db_session.execute(
                select(InventoryBatchModel).where(
                    InventoryBatchModel.source_cooking_session_id == cooking_session.id,
                    InventoryBatchModel.source == InventorySource.LEFTOVER,
                ),
            )
            leftover_batch = leftover_result.scalar_one_or_none()

            return CookingHistoryDetailResponseDTO(
                session=self.helper.to_session_dto(cooking_session),
                recipe_id=recipe.id,
                recipe_name=recipe.name,
                consumptions=consumptions,
                leftover_batch_id=leftover_batch.id if leftover_batch else None,
                completed_at=cooking_session.completed_at,
            )
        except (CookingDomainError, SQLAlchemyError):
            await self.db_session.rollback()
            raise

    async def _find_session_by_id(
        self,
        user_id: UUID,
        session_id: UUID,
    ) -> CookingSessionModel:
        result = await self.db_session.execute(
            select(CookingSessionModel).where(
                CookingSessionModel.id == session_id,
                CookingSessionModel.user_id == user_id,
            ),
        )
        cooking_session = result.scalar_one_or_none()
        if cooking_session is None:
            raise CookingSessionNotFoundError()
        return cooking_session


    async def _find_recipe(self, recipe_id: UUID) -> RecipeModel:
        result = await self.db_session.execute(
            select(RecipeModel).where(RecipeModel.id == recipe_id),
        )
        recipe = result.scalar_one_or_none()
        if recipe is None:
            raise RecipeNotFoundError()
        return recipe

    async def _find_meal_plan_item(
        self,
        user_id: UUID,
        meal_plan_item_id: UUID,
    ) -> MealPlanItemModel:
        result = await self.db_session.execute(
            select(MealPlanItemModel)
            .join(MealPlanModel, MealPlanModel.id == MealPlanItemModel.meal_plan_id)
            .where(
                MealPlanItemModel.id == meal_plan_item_id,
                MealPlanModel.user_id == user_id,
            ),
        )
        meal_plan_item = result.scalar_one_or_none()
        if meal_plan_item is None:
            raise MealPlanItemNotFoundError()
        return meal_plan_item

    async def _find_session_by_idempotency_key(
        self,
        user_id: UUID,
        idempotency_key: str,
    ) -> CookingSessionModel | None:
        result = await self.db_session.execute(
            select(CookingSessionModel).where(
                CookingSessionModel.user_id == user_id,
                CookingSessionModel.idempotency_key == idempotency_key,
            ),
        )
        return result.scalar_one_or_none()

    async def _find_locked_session(
        self,
        user_id: UUID,
        session_id: UUID,
    ) -> CookingSessionModel:
        result = await self.db_session.execute(
            select(CookingSessionModel)
            .where(
                CookingSessionModel.id == session_id,
                CookingSessionModel.user_id == user_id,
            )
            .with_for_update(),
        )
        cooking_session = result.scalar_one_or_none()
        if cooking_session is None:
            raise CookingSessionNotFoundError()
        return cooking_session

    async def _find_recipe_ingredients(
        self,
        recipe_id: UUID,
    ) -> list[tuple[RecipeIngredientModel, MasterIngredientModel]]:
        result = await self.db_session.execute(
            select(RecipeIngredientModel, MasterIngredientModel)
            .join(
                MasterIngredientModel,
                MasterIngredientModel.id == RecipeIngredientModel.master_ingredient_id,
            )
            .where(RecipeIngredientModel.recipe_id == recipe_id)
            .order_by(RecipeIngredientModel.created_at),
        )
        return list(result.tuples().all())

    async def _find_active_batches(
        self,
        user_id: UUID,
        ingredient_ids: list[UUID],
    ) -> list[InventoryBatchModel]:
        if not ingredient_ids:
            return []
        result = await self.db_session.execute(
            select(InventoryBatchModel)
            .where(
                InventoryBatchModel.user_id == user_id,
                InventoryBatchModel.status == InventoryBatchStatus.ACTIVE,
                InventoryBatchModel.current_quantity > 0,
                InventoryBatchModel.master_ingredient_id.in_(ingredient_ids),
            )
            .order_by(InventoryBatchModel.created_at),
        )
        return list(result.scalars().all())

    async def _find_locked_batches(
        self,
        user_id: UUID,
        ingredient_ids: list[UUID],
    ) -> list[InventoryBatchModel]:
        if not ingredient_ids:
            return []
        result = await self.db_session.execute(
            select(InventoryBatchModel)
            .where(
                InventoryBatchModel.user_id == user_id,
                InventoryBatchModel.status == InventoryBatchStatus.ACTIVE,
                InventoryBatchModel.current_quantity > 0,
                InventoryBatchModel.master_ingredient_id.in_(ingredient_ids),
            )
            .with_for_update(),
        )
        return list(result.scalars().all())

    async def _existing_completion_response(
        self,
        cooking_session: CookingSessionModel,
    ) -> CookingCompletionResponseDTO:
        if cooking_session.status is not CookingSessionStatus.COMPLETED:
            raise CookingCompletionConflictError(
                "Idempotency key belongs to an incomplete cooking session",
            )
        consumption_result = await self.db_session.execute(
            select(CookingConsumptionModel)
            .where(CookingConsumptionModel.cooking_session_id == cooking_session.id)
            .order_by(CookingConsumptionModel.created_at),
        )
        consumptions = list(consumption_result.scalars().all())
        batches = await self._find_current_batches_for_consumptions(consumptions)
        return self.helper.build_saved_completion_response(
            cooking_session,
            consumptions,
            batches,
        )

    async def _find_current_batches_for_consumptions(
        self,
        consumptions: list[CookingConsumptionModel],
    ) -> list[InventoryBatchModel]:
        batch_ids = [consumption.inventory_batch_id for consumption in consumptions]
        if not batch_ids:
            return []
        result = await self.db_session.execute(
            select(InventoryBatchModel).where(InventoryBatchModel.id.in_(batch_ids)),
        )
        return list(result.scalars().all())

    @staticmethod
    def _ensure_session_is_completable(cooking_session: CookingSessionModel) -> None:
        if cooking_session.status is CookingSessionStatus.COMPLETED:
            raise CookingCompletionConflictError("Cooking session is already completed")
        if cooking_session.status is CookingSessionStatus.CANCELLED:
            raise CookingCompletionConflictError(
                "Cancelled cooking session cannot complete"
            )
