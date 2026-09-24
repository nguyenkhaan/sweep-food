"""Ingredient-category persistence and deletion safeguards."""

from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from src.model.ingredient_category_model import IngredientCategoryModel
from src.model.master_ingredient_model import MasterIngredientModel
from src.model.shelf_life_rule_model import ShelfLifeRuleModel
from src.module.category.category_dto import (
    CategoryDTO,
    CreateCategoryRequestDTO,
    UpdateCategoryRequestDTO,
)


class CategoryNotFoundError(HTTPException):
    """Report an unknown ingredient category."""

    def __init__(self) -> None:
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category was not found",
        )


class CategoryConflictError(HTTPException):
    """Report a duplicate category name."""

    def __init__(self) -> None:
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail="Category already exists",
        )


class CategoryInUseError(HTTPException):
    """Prevent hard deletion of a referenced category."""

    def __init__(self) -> None:
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail="Category is already in use and cannot be deleted",
        )


class CategoryService:
    """Create, list, update, and safely hard-delete ingredient categories."""

    def __init__(self, db_session: AsyncSession) -> None:
        self.db_session = db_session

    async def create_category(self, body: CreateCategoryRequestDTO) -> CategoryDTO:
        """Create a category with a case-insensitively unique name."""
        category = IngredientCategoryModel(
            name=body.name,
            description=body.description,
        )
        try:
            self.db_session.add(category)
            await self.db_session.commit()
        except IntegrityError as error:
            await self.db_session.rollback()
            raise CategoryConflictError() from error
        except SQLAlchemyError:
            await self.db_session.rollback()
            raise
        return self._to_dto(category)

    async def list_categories(self) -> list[CategoryDTO]:
        """List every category in deterministic name order."""
        try:
            categories = (
                (
                    await self.db_session.execute(
                        select(IngredientCategoryModel).order_by(
                            func.lower(IngredientCategoryModel.name),
                            IngredientCategoryModel.id,
                        )
                    )
                )
                .scalars()
                .all()
            )
            return [self._to_dto(category) for category in categories]
        except SQLAlchemyError:
            await self.db_session.rollback()
            raise

    async def update_category(
        self,
        category_id: UUID,
        body: UpdateCategoryRequestDTO,
    ) -> CategoryDTO:
        """Update only explicitly supplied category fields."""
        try:
            category = await self._find_category(category_id, lock=True)
            for field_name, value in body.model_dump(exclude_unset=True).items():
                setattr(category, field_name, value)
            await self.db_session.commit()
            return self._to_dto(category)
        except IntegrityError as error:
            await self.db_session.rollback()
            raise CategoryConflictError() from error
        except (HTTPException, SQLAlchemyError):
            await self.db_session.rollback()
            raise

    async def delete_category(self, category_id: UUID) -> None:
        """Hard-delete an unreferenced category."""
        try:
            category = await self._find_category(category_id, lock=True)
            references = (
                MasterIngredientModel.category_id == category_id,
                ShelfLifeRuleModel.category_id == category_id,
            )
            for reference in references:
                used = await self.db_session.execute(
                    select(1).where(reference).limit(1)
                )
                if used.scalar_one_or_none() is not None:
                    raise CategoryInUseError()
            await self.db_session.delete(category)
            await self.db_session.commit()
        except IntegrityError as error:
            await self.db_session.rollback()
            raise CategoryInUseError() from error
        except (HTTPException, SQLAlchemyError):
            await self.db_session.rollback()
            raise

    async def _find_category(
        self,
        category_id: UUID,
        *,
        lock: bool,
    ) -> IngredientCategoryModel:
        statement = select(IngredientCategoryModel).where(
            IngredientCategoryModel.id == category_id
        )
        if lock:
            statement = statement.with_for_update()
        category = (await self.db_session.execute(statement)).scalar_one_or_none()
        if category is None:
            raise CategoryNotFoundError()
        return category

    @staticmethod
    def _to_dto(category: IngredientCategoryModel) -> CategoryDTO:
        return CategoryDTO(
            id=category.id,
            name=category.name,
            description=category.description,
        )
