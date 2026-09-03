"""Ownership-safe database persistence for recipe favourites."""

from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import delete, select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from src.model.favorite_recipe_model import FavoriteRecipeModel
from src.model.recipe_model import RecipeModel
from src.module.favorites.favorite_dto import FavoriteRecipeDTO


class FavoriteRecipeNotFoundError(HTTPException):
    """Reject a recipe that cannot be saved as a favourite."""

    def __init__(self) -> None:
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recipe was not found",
        )


class FavoriteService:
    """Store idempotent user-to-recipe favourite relationships."""

    def __init__(self, db_session: AsyncSession) -> None:
        self.db_session = db_session

    async def add_recipe(self, user_id: UUID, recipe_id: UUID) -> FavoriteRecipeDTO:
        """Save a recipe once for the authenticated user."""
        try:
            await self._ensure_recipe(recipe_id)
            existing = await self._find(user_id, recipe_id)
            if existing is None:
                self.db_session.add(
                    FavoriteRecipeModel(user_id=user_id, recipe_id=recipe_id)
                )
                await self.db_session.commit()
        except IntegrityError:
            await self.db_session.rollback()
            existing = await self._find(user_id, recipe_id)
            if existing is None:
                raise
        except SQLAlchemyError:
            await self.db_session.rollback()
            raise
        return FavoriteRecipeDTO(recipe_id=recipe_id, is_favorite=True)

    async def remove_recipe(self, user_id: UUID, recipe_id: UUID) -> None:
        """Remove a favourite idempotently without exposing other users' state."""
        try:
            await self.db_session.execute(
                delete(FavoriteRecipeModel).where(
                    FavoriteRecipeModel.user_id == user_id,
                    FavoriteRecipeModel.recipe_id == recipe_id,
                )
            )
            await self.db_session.commit()
        except SQLAlchemyError:
            await self.db_session.rollback()
            raise

    async def _ensure_recipe(self, recipe_id: UUID) -> None:
        recipe = (
            await self.db_session.execute(
                select(RecipeModel.id).where(RecipeModel.id == recipe_id),
            )
        ).scalar_one_or_none()
        if recipe is None:
            raise FavoriteRecipeNotFoundError()

    async def _find(
        self, user_id: UUID, recipe_id: UUID
    ) -> FavoriteRecipeModel | None:
        return (
            await self.db_session.execute(
                select(FavoriteRecipeModel).where(
                    FavoriteRecipeModel.user_id == user_id,
                    FavoriteRecipeModel.recipe_id == recipe_id,
                )
            )
        ).scalar_one_or_none()
