"""Read-only catalog query service."""

from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy.sql.elements import ColumnElement
from sqlalchemy.sql.functions import count

from src.model.ingredient_alias_model import IngredientAliasModel
from src.model.ingredient_category_model import IngredientCategoryModel
from src.model.master_ingredient_model import MasterIngredientModel
from src.module.catalog.catalog_dto import (
    IngredientCategoryDTO,
    IngredientDetailDTO,
    IngredientListItemDTO,
    IngredientListResponseDTO,
    IngredientNutritionDTO,
    ShelfLifeRuleDTO,
)


class CatalogIngredientNotFoundError(HTTPException):
    """Return a safe not-found response for an unknown catalog ingredient."""

    def __init__(self) -> None:
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ingredient was not found",
        )


class CatalogService:
    """Load public catalog data without exposing any mutation operation."""

    def __init__(self, db_session: AsyncSession) -> None:
        self.db_session = db_session

    async def list_ingredients(
        self,
        *,
        query: str | None,
        category: str | None,
        page: int,
        per_page: int,
    ) -> IngredientListResponseDTO:
        """Search canonical names and aliases with deterministic page ordering."""
        filters = self._filters(query=query, category=category)
        count_statement = select(count()).select_from(MasterIngredientModel)
        statement = (
            select(MasterIngredientModel)
            .options(
                selectinload(MasterIngredientModel.category),
                selectinload(MasterIngredientModel.aliases),
            )
            .order_by(func.lower(MasterIngredientModel.name), MasterIngredientModel.id)
            .offset((page - 1) * per_page)
            .limit(per_page)
        )
        if filters:
            count_statement = count_statement.where(*filters)
            statement = statement.where(*filters)
        total = int((await self.db_session.execute(count_statement)).scalar_one())
        ingredients = list((await self.db_session.execute(statement)).scalars().all())
        return IngredientListResponseDTO(
            items=[self._to_list_item(item) for item in ingredients],
            total=total,
            page=page,
            per_page=per_page,
        )

    async def get_ingredient(self, ingredient_id: UUID) -> IngredientDetailDTO:
        """Return one canonical catalog ingredient with aliases and shelf-life rules."""
        statement = (
            select(MasterIngredientModel)
            .where(MasterIngredientModel.id == ingredient_id)
            .options(
                selectinload(MasterIngredientModel.category),
                selectinload(MasterIngredientModel.aliases),
                selectinload(MasterIngredientModel.shelf_life_rules),
            )
        )
        ingredient = (await self.db_session.execute(statement)).scalar_one_or_none()
        if ingredient is None:
            raise CatalogIngredientNotFoundError()
        return IngredientDetailDTO(
            **self._to_list_item(ingredient).model_dump(),
            description=ingredient.description,
            default_media_url=ingredient.default_media_url,
            nutrition=IngredientNutritionDTO(
                calories=ingredient.calories,
                protein_g=ingredient.protein_g,
                fat_g=ingredient.fat_g,
                carbs_g=ingredient.carbs_g,
                sugar_g=ingredient.sugar_g,
                sodium_mg=ingredient.sodium_mg,
                other_nutrients=ingredient.other_nutrients,
            ),
            shelf_life_rules=[
                ShelfLifeRuleDTO(
                    scope=rule.scope,
                    storage_mode=rule.storage_mode,
                    min_days=rule.min_days,
                    max_days=rule.max_days,
                    default_days=rule.default_days,
                )
                for rule in sorted(
                    ingredient.shelf_life_rules,
                    key=lambda rule: (rule.storage_mode.value, rule.id),
                )
            ],
        )

    @staticmethod
    def _filters(
        *,
        query: str | None,
        category: str | None,
    ) -> list[ColumnElement[bool]]:
        """Build case-insensitive canonical-name, alias, and category filters."""
        filters: list[ColumnElement[bool]] = []
        if query is not None and (normalized_query := query.strip().casefold()):
            alias_match = (
                select(IngredientAliasModel.id)
                .where(
                    IngredientAliasModel.master_ingredient_id
                    == MasterIngredientModel.id,
                    func.lower(IngredientAliasModel.normalized_alias).like(
                        f"%{normalized_query}%"
                    ),
                )
                .exists()
            )
            filters.append(
                or_(
                    func.lower(MasterIngredientModel.name).like(
                        f"%{normalized_query}%"
                    ),
                    alias_match,
                )
            )
        if category is not None and (
            normalized_category := category.strip().casefold()
        ):
            filters.append(
                MasterIngredientModel.category.has(
                    func.lower(IngredientCategoryModel.name) == normalized_category,
                )
            )
        return filters

    @staticmethod
    def _to_list_item(ingredient: MasterIngredientModel) -> IngredientListItemDTO:
        """Map a loaded ORM ingredient to the compact public representation."""
        return IngredientListItemDTO(
            id=ingredient.id,
            name=ingredient.name,
            category=IngredientCategoryDTO(
                id=ingredient.category.id,
                name=ingredient.category.name,
            ),
            default_unit=ingredient.canonical_unit,
            default_storage_mode=ingredient.default_storage_mode,
            aliases=sorted(
                (alias.alias for alias in ingredient.aliases),
                key=str.casefold,
            ),
        )
