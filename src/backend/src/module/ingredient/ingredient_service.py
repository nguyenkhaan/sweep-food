"""Master ingredient mutations and owned inventory storage changes."""

from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import delete, select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.model.ingredient_alias_model import IngredientAliasModel
from src.model.ingredient_category_model import IngredientCategoryModel
from src.model.inventory_batch_model import InventoryBatchModel
from src.model.master_ingredient_model import MasterIngredientModel
from src.model.recipe_ingredient_model import RecipeIngredientModel
from src.model.shelf_life_rule_model import ShelfLifeRuleModel
from src.model.shopping_list_item_model import ShoppingListItemModel
from src.model.waste_reduction_event_model import WasteReductionEventModel
from src.module.catalog.catalog_dto import IngredientDetailDTO
from src.module.catalog.catalog_service import CatalogService
from src.module.ingredient.ingredient_dto import (
    AssignIngredientCategoryDTO,
    UpdateIngredientDefaultStorageDTO,
    UpdateIngredientDTO,
)
from src.module.inventory.inventory_dto import (
    InventoryBatchDTO,
    MoveInventoryBatchRequestDTO,
)
from src.module.inventory.inventory_service import InventoryService


class IngredientService:
    """Write shared catalog data and reuse audited, owner-scoped batch moves."""

    def __init__(self, db_session: AsyncSession) -> None:
        self.db_session = db_session

    async def _get_master(self, ingredient_id: UUID) -> MasterIngredientModel:
        result = await self.db_session.execute(
            select(MasterIngredientModel)
            .where(MasterIngredientModel.id == ingredient_id)
            .with_for_update()
        )
        ingredient = result.scalar_one_or_none()
        if ingredient is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Ingredient was not found",
            )
        return ingredient

    async def _update_master_fields(
        self,
        ingredient_id: UUID,
        values: dict[str, object],
    ) -> IngredientDetailDTO:
        """Update only named columns and return the unchanged full record."""
        try:
            await self.db_session.execute(
                update(MasterIngredientModel)
                .where(MasterIngredientModel.id == ingredient_id)
                .values(**values)
            )
            await self.db_session.commit()
        except IntegrityError as error:
            await self.db_session.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Ingredient update conflicts with existing data",
            ) from error
        return await CatalogService(self.db_session).get_ingredient(ingredient_id)

    async def update_ingredient(
        self, ingredient_id: UUID, body: UpdateIngredientDTO
    ) -> IngredientDetailDTO:
        """Change only the explicitly requested mutable catalog fields."""
        await self._get_master(ingredient_id)
        return await self._update_master_fields(
            ingredient_id,
            body.model_dump(exclude_unset=True),
        )

    async def update_default_storage(
        self, ingredient_id: UUID, body: UpdateIngredientDefaultStorageDTO
    ) -> IngredientDetailDTO:
        """Change only the global default storage mode."""
        await self._get_master(ingredient_id)
        return await self._update_master_fields(
            ingredient_id,
            {"default_storage_mode": body.default_storage_mode},
        )

    async def update_category(
        self, ingredient_id: UUID, body: AssignIngredientCategoryDTO
    ) -> IngredientDetailDTO:
        """Attach an existing category to a master ingredient."""
        await self._get_master(ingredient_id)
        category = await self.db_session.execute(
            select(IngredientCategoryModel.id).where(
                IngredientCategoryModel.id == body.category_id
            )
        )
        if category.scalar_one_or_none() is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Category not found",
            )
        return await self._update_master_fields(
            ingredient_id,
            {"category_id": body.category_id},
        )

    async def delete_ingredient(self, ingredient_id: UUID) -> None:
        """Delete only an ingredient unused by business records."""
        ingredient = await self._get_master(ingredient_id)
        references = (
            RecipeIngredientModel.master_ingredient_id == ingredient_id,
            InventoryBatchModel.master_ingredient_id == ingredient_id,
            ShoppingListItemModel.master_ingredient_id == ingredient_id,
            WasteReductionEventModel.master_ingredient_id == ingredient_id,
        )
        for reference in references:
            used = await self.db_session.execute(select(1).where(reference).limit(1))
            if used.scalar_one_or_none() is not None:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Master ingredient is in use and cannot be deleted",
                )
        try:
            await self.db_session.execute(
                delete(IngredientAliasModel).where(
                    IngredientAliasModel.master_ingredient_id == ingredient_id
                )
            )
            await self.db_session.execute(
                delete(ShelfLifeRuleModel).where(
                    ShelfLifeRuleModel.master_ingredient_id == ingredient_id
                )
            )
            await self.db_session.delete(ingredient)
            await self.db_session.commit()
        except IntegrityError as error:
            await self.db_session.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Master ingredient is in use and cannot be deleted",
            ) from error

    async def move_inventory_batch(
        self,
        user_id: UUID,
        batch_id: UUID,
        body: MoveInventoryBatchRequestDTO,
        key: str,
    ) -> InventoryBatchDTO:
        """Use the existing owner-scoped move, expiry, and ledger transaction."""
        return await InventoryService(self.db_session).move_batch(
            user_id, batch_id, body, key
        )
