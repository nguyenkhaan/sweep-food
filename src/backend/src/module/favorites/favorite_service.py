"""Ownership-safe persistence for favourite recipes and named menus."""

from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import delete, select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.functions import count

from src.model.favorite_menu_item_model import FavoriteMenuItemModel
from src.model.favorite_menu_model import FavoriteMenuModel
from src.model.favorite_recipe_model import FavoriteRecipeModel
from src.model.recipe_model import RecipeModel
from src.module.favorites.favorite_dto import (
    CreateFavoriteMenuItemRequestDTO,
    CreateFavoriteMenuRequestDTO,
    FavoriteMenuDetailDTO,
    FavoriteMenuDTO,
    FavoriteMenuItemDTO,
    FavoriteMenuListDTO,
    FavoriteRecipeDTO,
    FavoriteRecipeListDTO,
    FavoriteRecipeListItemDTO,
    UpdateFavoriteMenuItemRequestDTO,
    UpdateFavoriteMenuRequestDTO,
)


class FavoriteRecipeNotFoundError(HTTPException):
    """Reject a recipe that cannot be saved as a favourite."""

    def __init__(self) -> None:
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recipe was not found",
        )


class FavoriteMenuNotFoundError(HTTPException):
    """Hide whether a menu belongs to a different user."""

    def __init__(self) -> None:
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Favorite menu was not found",
        )


class FavoriteMenuItemNotFoundError(HTTPException):
    """Hide whether a menu entry belongs to another user's menu."""

    def __init__(self) -> None:
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Favorite menu item was not found",
        )


class FavoriteMenuConflictError(HTTPException):
    """Report duplicate recipes within a favourite menu."""

    def __init__(self) -> None:
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail="Recipe is already in this favorite menu",
        )


class FavoriteService:
    """Store user-scoped favourite recipes, menus, and menu entries."""

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

    async def remove_recipe(self, user_id: UUID, recipe_id: UUID) -> dict:
        """Remove a favourite idempotently without exposing other users' state."""
        try:
            await self.db_session.execute(
                delete(FavoriteRecipeModel).where(
                    FavoriteRecipeModel.user_id == user_id,
                    FavoriteRecipeModel.recipe_id == recipe_id,
                )
            )
            await self.db_session.commit()
            return {
                "message": "Remove recipe from favorite list successfully"
            }
        except SQLAlchemyError:
            await self.db_session.rollback()
            raise

    async def list_recipes(
        self, user_id: UUID, limit: int, offset: int
    ) -> FavoriteRecipeListDTO:
        """Read the current user's saved recipes in reverse creation order."""
        try:
            total = await self._favorite_recipe_count(user_id)
            result = await self.db_session.execute(
                select(FavoriteRecipeModel, RecipeModel)
                .join(RecipeModel, RecipeModel.id == FavoriteRecipeModel.recipe_id)
                .where(FavoriteRecipeModel.user_id == user_id)
                .order_by(FavoriteRecipeModel.created_at.desc(), FavoriteRecipeModel.id)
                .offset(offset)
                .limit(limit),
            )
            return FavoriteRecipeListDTO(
                items=[
                    self._to_favorite_recipe_dto(favorite, recipe)
                    for favorite, recipe in result.tuples().all()
                ],
                total=total,
                limit=limit,
                offset=offset,
            )
        except SQLAlchemyError:
            await self.db_session.rollback()
            raise

    async def create_menu(
        self, user_id: UUID, body: CreateFavoriteMenuRequestDTO
    ) -> FavoriteMenuDTO:
        """Create an empty named menu for the authenticated user."""
        menu = FavoriteMenuModel(
            user_id=user_id,
            name=body.name,
            description=body.description,
        )
        try:
            self.db_session.add(menu)
            await self.db_session.commit()
        except SQLAlchemyError:
            await self.db_session.rollback()
            raise
        return self._to_menu_dto(menu)

    async def list_menus(
        self, user_id: UUID, limit: int, offset: int
    ) -> FavoriteMenuListDTO:
        """List owned menus without loading their recipe entries."""
        try:
            total = await self._favorite_menu_count(user_id)
            menus = list(
                (
                    await self.db_session.execute(
                        select(FavoriteMenuModel)
                        .where(FavoriteMenuModel.user_id == user_id)
                        .order_by(
                            FavoriteMenuModel.created_at.desc(), FavoriteMenuModel.id
                        )
                        .offset(offset)
                        .limit(limit),
                    )
                )
                .scalars()
                .all()
            )
            return FavoriteMenuListDTO(
                items=[self._to_menu_dto(menu) for menu in menus],
                total=total,
                limit=limit,
                offset=offset,
            )
        except SQLAlchemyError:
            await self.db_session.rollback()
            raise

    async def get_menu(self, user_id: UUID, menu_id: UUID) -> FavoriteMenuDetailDTO:
        """Read an owned menu and its recipes in creation order."""
        try:
            menu = await self._find_menu(user_id, menu_id, lock=False)
            return FavoriteMenuDetailDTO(
                **self._to_menu_dto(menu).model_dump(),
                items=await self._find_menu_items(menu.id),
            )
        except SQLAlchemyError:
            await self.db_session.rollback()
            raise

    async def update_menu(
        self,
        user_id: UUID,
        menu_id: UUID,
        body: UpdateFavoriteMenuRequestDTO,
    ) -> FavoriteMenuDTO:
        """Update fields explicitly provided by an owned menu request."""
        try:
            print('Hello world') 
            menu = await self._find_menu(user_id, menu_id, lock=True)
            if "name" in body.model_fields_set and body.name is not None:
                menu.name = body.name
            if "description" in body.model_fields_set:
                menu.description = body.description
            await self.db_session.commit()
            return self._to_menu_dto(menu)
        except (HTTPException, SQLAlchemyError):
            await self.db_session.rollback()
            raise

    async def remove_menu(self, user_id: UUID, menu_id: UUID):
        """Delete an owned menu together with all of its recipe entries."""
        try:
            menu = await self._find_menu(user_id, menu_id, lock=True)
            await self.db_session.execute(
                delete(FavoriteMenuItemModel).where(
                    FavoriteMenuItemModel.favorite_menu_id == menu.id,
                )
            )
            await self.db_session.delete(menu)
            await self.db_session.commit()
            return {
                "message": "Drop favorite menu successfully"
            }
        except (HTTPException, SQLAlchemyError):
            await self.db_session.rollback()
            raise

    async def add_menu_item(
        self,
        user_id: UUID,
        menu_id: UUID,
        body: CreateFavoriteMenuItemRequestDTO,
    ) -> FavoriteMenuItemDTO:
        """Add a recipe to an owned menu exactly once."""
        try:
            menu = await self._find_menu(user_id, menu_id, lock=True)
            recipe = await self._find_recipe(body.recipe_id)
            item = FavoriteMenuItemModel(
                favorite_menu_id=menu.id,
                recipe_id=recipe.id,
            )
            self.db_session.add(item)
            await self.db_session.commit()
            return self._to_menu_item_dto(item, recipe)
        except IntegrityError as error:
            await self.db_session.rollback()
            raise FavoriteMenuConflictError() from error
        except (HTTPException, SQLAlchemyError):
            await self.db_session.rollback()
            raise

    async def update_menu_item(
        self,
        user_id: UUID,
        menu_id: UUID,
        item_id: UUID,
        body: UpdateFavoriteMenuItemRequestDTO,
    ) -> FavoriteMenuItemDTO:
        """Replace a recipe entry while retaining its menu-item identity."""
        try:
            menu = await self._find_menu(user_id, menu_id, lock=True)
            item = await self._find_menu_item(menu.id, item_id, lock=True)
            recipe = await self._find_recipe(body.recipe_id)
            item.recipe_id = recipe.id
            await self.db_session.commit()
            return self._to_menu_item_dto(item, recipe)
        except IntegrityError as error:
            await self.db_session.rollback()
            raise FavoriteMenuConflictError() from error
        except (HTTPException, SQLAlchemyError):
            await self.db_session.rollback()
            raise

    async def remove_menu_item(
        self, user_id: UUID, menu_id: UUID, item_id: UUID
    ) -> None:
        """Remove one recipe entry from an owned menu."""
        try:
            menu = await self._find_menu(user_id, menu_id, lock=True)
            item = await self._find_menu_item(menu.id, item_id, lock=True)
            await self.db_session.delete(item)
            await self.db_session.commit()
        except (HTTPException, SQLAlchemyError):
            await self.db_session.rollback()
            raise

    async def _find_recipe(self, recipe_id: UUID) -> RecipeModel:
        recipe = (
            await self.db_session.execute(
                select(RecipeModel).where(RecipeModel.id == recipe_id),
            )
        ).scalar_one_or_none()
        if recipe is None:
            raise FavoriteRecipeNotFoundError()
        return recipe

    async def _ensure_recipe(self, recipe_id: UUID) -> None:
        await self._find_recipe(recipe_id)

    async def _find(self, user_id: UUID, recipe_id: UUID) -> FavoriteRecipeModel | None:
        return (
            await self.db_session.execute(
                select(FavoriteRecipeModel).where(
                    FavoriteRecipeModel.user_id == user_id,
                    FavoriteRecipeModel.recipe_id == recipe_id,
                )
            )
        ).scalar_one_or_none()

    async def _find_menu(
        self, user_id: UUID, menu_id: UUID, *, lock: bool
    ) -> FavoriteMenuModel:
        statement = select(FavoriteMenuModel).where(
            FavoriteMenuModel.id == menu_id,
            FavoriteMenuModel.user_id == user_id,
        )
        if lock:
            statement = statement.with_for_update()
        menu = (await self.db_session.execute(statement)).scalar_one_or_none()
        if menu is None:
            raise FavoriteMenuNotFoundError()
        return menu

    async def _find_menu_item(
        self, menu_id: UUID, item_id: UUID, *, lock: bool
    ) -> FavoriteMenuItemModel:
        statement = select(FavoriteMenuItemModel).where(
            FavoriteMenuItemModel.id == item_id,
            FavoriteMenuItemModel.favorite_menu_id == menu_id,
        )
        if lock:
            statement = statement.with_for_update()
        item = (await self.db_session.execute(statement)).scalar_one_or_none()
        if item is None:
            raise FavoriteMenuItemNotFoundError()
        return item

    async def _favorite_recipe_count(self, user_id: UUID) -> int:
        """Count the current user's saved recipes before applying a page."""
        return int(
            (
                await self.db_session.execute(
                    select(count())
                    .select_from(FavoriteRecipeModel)
                    .where(FavoriteRecipeModel.user_id == user_id),
                )
            ).scalar_one()
        )

    async def _favorite_menu_count(self, user_id: UUID) -> int:
        """Count the current user's menus before applying a page."""
        return int(
            (
                await self.db_session.execute(
                    select(count())
                    .select_from(FavoriteMenuModel)
                    .where(FavoriteMenuModel.user_id == user_id),
                )
            ).scalar_one()
        )

    async def _find_menu_items(self, menu_id: UUID) -> list[FavoriteMenuItemDTO]:
        """Read every recipe in one menu in creation order."""
        result = await self.db_session.execute(
            select(FavoriteMenuItemModel, RecipeModel)
            .join(RecipeModel, RecipeModel.id == FavoriteMenuItemModel.recipe_id)
            .where(FavoriteMenuItemModel.favorite_menu_id == menu_id)
            .order_by(FavoriteMenuItemModel.created_at, FavoriteMenuItemModel.id),
        )
        return [
            self._to_menu_item_dto(item, recipe)
            for item, recipe in result.tuples().all()
        ]

    @staticmethod
    def _to_favorite_recipe_dto(
        favorite: FavoriteRecipeModel, recipe: RecipeModel
    ) -> FavoriteRecipeListItemDTO:
        return FavoriteRecipeListItemDTO(
            recipe_id=recipe.id,
            recipe_name=recipe.name,
            recipe_description=recipe.description,
            media_url=recipe.media_url,
            created_at=favorite.created_at,
        )

    @staticmethod
    def _to_menu_dto(menu: FavoriteMenuModel) -> FavoriteMenuDTO:
        return FavoriteMenuDTO(
            id=menu.id,
            name=menu.name,
            description=menu.description,
            created_at=menu.created_at,
            updated_at=menu.updated_at,
        )

    @staticmethod
    def _to_menu_item_dto(
        item: FavoriteMenuItemModel, recipe: RecipeModel
    ) -> FavoriteMenuItemDTO:
        return FavoriteMenuItemDTO(
            id=item.id,
            recipe_id=recipe.id,
            recipe_name=recipe.name,
            recipe_description=recipe.description,
            media_url=recipe.media_url,
            created_at=item.created_at,
        )
