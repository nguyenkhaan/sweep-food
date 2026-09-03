"""Ownership-safe persistence for meal plans and selected recipe slots."""

from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from src.model.enum_model import MealPlanItemStatus
from src.model.meal_plan_item_model import MealPlanItemModel
from src.model.meal_plan_model import MealPlanModel
from src.model.recipe_model import RecipeModel
from src.model.recommendation_run_model import RecommendationRunModel
from src.module.meal_plans.meal_plan_dto import (
    CreateMealPlanItemRequestDTO,
    CreateMealPlanRequestDTO,
    MealPlanDTO,
    MealPlanItemDTO,
    UpdateMealPlanItemRequestDTO,
)


class MealPlanNotFoundError(HTTPException):
    """Hide whether an unknown plan belongs to another user."""

    def __init__(self) -> None:
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Meal plan was not found",
        )


class MealPlanItemNotFoundError(HTTPException):
    """Hide whether an unknown slot belongs to an owned plan."""

    def __init__(self) -> None:
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Meal plan item was not found",
        )


class MealPlanRecipeNotFoundError(HTTPException):
    """Reject a recipe that cannot be selected into a plan."""

    def __init__(self) -> None:
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recipe was not found",
        )


class MealPlanRecommendationRunNotFoundError(HTTPException):
    """Reject a recommendation run outside the authenticated user's history."""

    def __init__(self) -> None:
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recommendation run was not found",
        )


class MealPlanConflictError(HTTPException):
    """Report a date-range or duplicate-slot write conflict."""

    def __init__(self, detail: str = "Meal plan item conflicts with an existing slot") -> None:
        super().__init__(status_code=status.HTTP_409_CONFLICT, detail=detail)


class MealPlanService:
    """Create and mutate plans using user-scoped database queries."""

    def __init__(self, db_session: AsyncSession) -> None:
        self.db_session = db_session

    async def create(self, user_id: UUID, body: CreateMealPlanRequestDTO) -> MealPlanDTO:
        """Persist an empty plan with a valid inclusive date range."""
        plan = MealPlanModel(
            user_id=user_id,
            name=body.name,
            starts_on=body.starts_on,
            ends_on=body.ends_on,
        )
        try:
            self.db_session.add(plan)
            await self.db_session.commit()
        except SQLAlchemyError:
            await self.db_session.rollback()
            raise
        return self._to_plan_dto(plan, [])

    async def get(self, user_id: UUID, plan_id: UUID) -> MealPlanDTO:
        """Read one owned plan together with its recipes in deterministic order."""
        try:
            plan = await self._find_plan(user_id, plan_id, lock=False)
            return self._to_plan_dto(plan, await self._find_items(plan.id))
        except SQLAlchemyError:
            await self.db_session.rollback()
            raise

    async def add_item(
        self,
        user_id: UUID,
        plan_id: UUID,
        body: CreateMealPlanItemRequestDTO,
    ) -> MealPlanItemDTO:
        """Persist one recipe in an owned plan slot."""
        try:
            plan = await self._find_plan(user_id, plan_id, lock=True)
            self._ensure_date_in_plan(plan, body.planned_for)
            recipe = await self._find_recipe(body.recipe_id)
            await self._verify_recommendation_run(user_id, body.recommendation_run_id)
            item = MealPlanItemModel(
                meal_plan_id=plan.id,
                recipe_id=recipe.id,
                recommendation_run_id=body.recommendation_run_id,
                planned_for=body.planned_for,
                meal_slot=body.meal_slot,
                servings=body.servings,
                status=MealPlanItemStatus.PLANNED,
            )
            self.db_session.add(item)
            await self.db_session.commit()
            return self._to_item_dto(item, recipe.name)
        except IntegrityError as error:
            await self.db_session.rollback()
            raise MealPlanConflictError() from error
        except (HTTPException, SQLAlchemyError):
            await self.db_session.rollback()
            raise

    async def update_item(
        self,
        user_id: UUID,
        plan_id: UUID,
        item_id: UUID,
        body: UpdateMealPlanItemRequestDTO,
    ) -> MealPlanItemDTO:
        """Replace or reschedule an owned slot while preserving its plan boundary."""
        try:
            plan = await self._find_plan(user_id, plan_id, lock=True)
            item = await self._find_item(plan.id, item_id, lock=True)
            recipe_name = (await self._find_recipe(item.recipe_id)).name
            if body.recipe_id is not None:
                recipe = await self._find_recipe(body.recipe_id)
                item.recipe_id = recipe.id
                recipe_name = recipe.name
            if body.planned_for is not None:
                self._ensure_date_in_plan(plan, body.planned_for)
                item.planned_for = body.planned_for
            if body.meal_slot is not None:
                item.meal_slot = body.meal_slot
            if body.servings is not None:
                item.servings = body.servings
            await self.db_session.commit()
            return self._to_item_dto(item, recipe_name)
        except IntegrityError as error:
            await self.db_session.rollback()
            raise MealPlanConflictError() from error
        except (HTTPException, SQLAlchemyError):
            await self.db_session.rollback()
            raise

    async def remove_item(self, user_id: UUID, plan_id: UUID, item_id: UUID) -> None:
        """Delete one owned selection without disclosing cross-user records."""
        try:
            plan = await self._find_plan(user_id, plan_id, lock=True)
            item = await self._find_item(plan.id, item_id, lock=True)
            await self.db_session.delete(item)
            await self.db_session.commit()
        except (HTTPException, SQLAlchemyError):
            await self.db_session.rollback()
            raise

    async def _find_plan(
        self, user_id: UUID, plan_id: UUID, *, lock: bool
    ) -> MealPlanModel:
        statement = select(MealPlanModel).where(
            MealPlanModel.id == plan_id,
            MealPlanModel.user_id == user_id,
        )
        if lock:
            statement = statement.with_for_update()
        plan = (await self.db_session.execute(statement)).scalar_one_or_none()
        if plan is None:
            raise MealPlanNotFoundError()
        return plan

    async def _find_item(
        self, plan_id: UUID, item_id: UUID, *, lock: bool
    ) -> MealPlanItemModel:
        statement = select(MealPlanItemModel).where(
            MealPlanItemModel.id == item_id,
            MealPlanItemModel.meal_plan_id == plan_id,
        )
        if lock:
            statement = statement.with_for_update()
        item = (await self.db_session.execute(statement)).scalar_one_or_none()
        if item is None:
            raise MealPlanItemNotFoundError()
        return item

    async def _find_recipe(self, recipe_id: UUID) -> RecipeModel:
        recipe = (
            await self.db_session.execute(
                select(RecipeModel).where(RecipeModel.id == recipe_id),
            )
        ).scalar_one_or_none()
        if recipe is None:
            raise MealPlanRecipeNotFoundError()
        return recipe

    async def _verify_recommendation_run(
        self, user_id: UUID, recommendation_run_id: UUID | None
    ) -> None:
        if recommendation_run_id is None:
            return
        run = (
            await self.db_session.execute(
                select(RecommendationRunModel).where(
                    RecommendationRunModel.id == recommendation_run_id,
                    RecommendationRunModel.user_id == user_id,
                )
            )
        ).scalar_one_or_none()
        if run is None:
            raise MealPlanRecommendationRunNotFoundError()

    async def _find_items(
        self, plan_id: UUID
    ) -> list[tuple[MealPlanItemModel, RecipeModel]]:
        result = await self.db_session.execute(
            select(MealPlanItemModel, RecipeModel)
            .join(RecipeModel, RecipeModel.id == MealPlanItemModel.recipe_id)
            .where(MealPlanItemModel.meal_plan_id == plan_id)
            .order_by(
                MealPlanItemModel.planned_for,
                MealPlanItemModel.meal_slot,
                MealPlanItemModel.id,
            )
        )
        return list(result.tuples().all())

    @staticmethod
    def _ensure_date_in_plan(plan: MealPlanModel, planned_for: object) -> None:
        if not isinstance(planned_for, type(plan.starts_on)) or not (
            plan.starts_on <= planned_for <= plan.ends_on
        ):
            raise MealPlanConflictError("Planned date must be within the meal plan range")

    @staticmethod
    def _to_item_dto(item: MealPlanItemModel, recipe_name: str) -> MealPlanItemDTO:
        return MealPlanItemDTO(
            id=item.id,
            recipe_id=item.recipe_id,
            recipe_name=recipe_name,
            recommendation_run_id=item.recommendation_run_id,
            planned_for=item.planned_for,
            meal_slot=item.meal_slot,
            servings=item.servings,
            status=item.status,
        )

    @classmethod
    def _to_plan_dto(
        cls,
        plan: MealPlanModel,
        items: list[tuple[MealPlanItemModel, RecipeModel]],
    ) -> MealPlanDTO:
        return MealPlanDTO(
            id=plan.id,
            name=plan.name,
            starts_on=plan.starts_on,
            ends_on=plan.ends_on,
            items=[cls._to_item_dto(item, recipe.name) for item, recipe in items],
        )
