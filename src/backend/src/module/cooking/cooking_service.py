"""Business logic for read-only cooking previews."""

from datetime import UTC, datetime
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from src.model.enum_model import InventoryBatchStatus
from src.model.inventory_batch_model import InventoryBatchModel
from src.model.master_ingredient_model import MasterIngredientModel
from src.model.recipe_ingredient_model import RecipeIngredientModel
from src.model.recipe_model import RecipeModel
from src.module.cooking.cooking_dto import (
    CookingPreviewRequestDTO,
    CookingPreviewResponseDTO,
    CookingPreviewWarningCode,
    CookingPreviewWarningDTO,
    MissingIngredientDTO,
    NutritionEstimateDTO,
    ProposedBatchDeductionDTO,
    ScaledRecipeIngredientDTO,
)
from src.service.fefo_service import (
    FEFOAllocation,
    FEFOAllocationResult,
    FEFOCandidate,
    FEFOService,
)


class CookingDomainError(HTTPException):
    """Base class for safe cooking-domain API errors."""

    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Cooking preview could not be completed"

    def __init__(self, detail: str | None = None) -> None:
        """Build a stable client-safe cooking domain error."""
        super().__init__(
            status_code=self.status_code, detail=detail or self.default_detail
        )


class RecipeNotFoundError(CookingDomainError):
    """Raised when the selected seeded recipe does not exist."""

    status_code = status.HTTP_404_NOT_FOUND
    default_detail = "Recipe was not found"


class CookingService:
    """Create previews using recipe data and the caller's own inventory only."""

    def __init__(self, db_session: AsyncSession, fefo_service: FEFOService) -> None:
        """Store the request-scoped database session and reusable FEFO service."""
        self.db_session = db_session
        self.fefo_service = fefo_service

    async def preview(
        self,
        user_id: UUID,
        request: CookingPreviewRequestDTO,
    ) -> CookingPreviewResponseDTO:
        """Return one recipe's serving-scaled, ownership-safe cooking proposal."""
        try:
            recipe = await self._find_recipe(request.recipe_id)
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
        return self._build_preview(
            recipe, recipe_ingredients, batches, request.servings
        )

    async def _find_recipe(self, recipe_id: UUID) -> RecipeModel:
        result = await self.db_session.execute(
            select(RecipeModel).where(RecipeModel.id == recipe_id),
        )
        recipe = result.scalar_one_or_none()
        if recipe is None:
            raise RecipeNotFoundError()
        return recipe

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

    def _build_preview(
        self,
        recipe: RecipeModel,
        recipe_ingredients: list[tuple[RecipeIngredientModel, MasterIngredientModel]],
        batches: list[InventoryBatchModel],
        servings: float,
    ) -> CookingPreviewResponseDTO:
        scale = servings / recipe.default_servings
        now = datetime.now(UTC)
        scaled_ingredients: list[ScaledRecipeIngredientDTO] = []
        deductions: list[ProposedBatchDeductionDTO] = []
        missing_ingredients: list[MissingIngredientDTO] = []
        warnings: list[CookingPreviewWarningDTO] = []
        for recipe_ingredient, ingredient in recipe_ingredients:
            required_quantity = recipe_ingredient.required_quantity * scale
            scaled_ingredients.append(
                ScaledRecipeIngredientDTO(
                    recipe_ingredient_id=recipe_ingredient.id,
                    master_ingredient_id=ingredient.id,
                    ingredient_name=ingredient.name,
                    required_quantity=required_quantity,
                    unit=recipe_ingredient.unit,
                )
            )
            allocation_result = self.fefo_service.allocate(
                required_quantity,
                recipe_ingredient.unit,
                self._to_fefo_candidates(batches, ingredient.id),
                now,
            )
            deductions.extend(
                self._to_deduction_dtos(
                    recipe_ingredient,
                    ingredient.id,
                    allocation_result.allocations,
                )
            )
            if allocation_result.missing_quantity > 0:
                missing_ingredients.append(
                    MissingIngredientDTO(
                        recipe_ingredient_id=recipe_ingredient.id,
                        master_ingredient_id=ingredient.id,
                        ingredient_name=ingredient.name,
                        missing_quantity=allocation_result.missing_quantity,
                        unit=recipe_ingredient.unit,
                    )
                )
            warnings.extend(
                self._to_warning_dtos(ingredient.id, ingredient.name, allocation_result)
            )
        return CookingPreviewResponseDTO(
            recipe_id=recipe.id,
            recipe_name=recipe.name,
            servings=servings,
            scaled_ingredients=scaled_ingredients,
            proposed_deductions=deductions,
            missing_ingredients=missing_ingredients,
            nutrition_estimate=self._scale_nutrition(recipe, scale),
            warnings=warnings,
        )

    @staticmethod
    def _to_fefo_candidates(
        batches: list[InventoryBatchModel],
        ingredient_id: UUID,
    ) -> list[FEFOCandidate]:
        return [
            FEFOCandidate(
                batch_id=batch.id,
                current_quantity=batch.current_quantity,
                unit=batch.unit,
                expires_at=batch.expires_at,
                created_at=batch.created_at,
            )
            for batch in batches
            if batch.master_ingredient_id == ingredient_id
        ]

    @staticmethod
    def _to_deduction_dtos(
        recipe_ingredient: RecipeIngredientModel,
        ingredient_id: UUID,
        allocations: list[FEFOAllocation],
    ) -> list[ProposedBatchDeductionDTO]:
        return [
            ProposedBatchDeductionDTO(
                recipe_ingredient_id=recipe_ingredient.id,
                master_ingredient_id=ingredient_id,
                batch_id=allocation.batch_id,
                quantity=allocation.batch_quantity,
                unit=allocation.batch_unit,
                recipe_quantity=allocation.recipe_quantity,
                recipe_unit=allocation.recipe_unit,
                expires_at=allocation.expires_at,
            )
            for allocation in allocations
        ]

    @staticmethod
    def _to_warning_dtos(
        ingredient_id: UUID,
        ingredient_name: str,
        allocation_result: FEFOAllocationResult,
    ) -> list[CookingPreviewWarningDTO]:
        warnings: list[CookingPreviewWarningDTO] = []
        warnings.extend(
            CookingPreviewWarningDTO(
                code=CookingPreviewWarningCode.EXPIRED_BATCH_EXCLUDED,
                message=f"{ingredient_name} batch is expired and was excluded.",
                batch_id=candidate.batch_id,
                master_ingredient_id=ingredient_id,
            )
            for candidate in allocation_result.expired_candidates
        )
        warnings.extend(
            CookingPreviewWarningDTO(
                code=CookingPreviewWarningCode.UNKNOWN_EXPIRATION_BATCH,
                message=(
                    f"{ingredient_name} batch has no expiration date and is considered "
                    "after dated batches."
                ),
                batch_id=candidate.batch_id,
                master_ingredient_id=ingredient_id,
            )
            for candidate in allocation_result.unknown_expiration_candidates
        )
        warnings.extend(
            CookingPreviewWarningDTO(
                code=CookingPreviewWarningCode.INCOMPATIBLE_UNIT_BATCH,
                message=f"{ingredient_name} batch has an incompatible unit.",
                batch_id=candidate.batch_id,
                master_ingredient_id=ingredient_id,
            )
            for candidate in allocation_result.incompatible_candidates
        )
        return warnings

    @staticmethod
    def _scale_nutrition(recipe: RecipeModel, scale: float) -> NutritionEstimateDTO:
        return NutritionEstimateDTO(
            calories=_scale_optional_value(recipe.total_calories, scale),
            protein_g=_scale_optional_value(recipe.total_protein_g, scale),
            fat_g=_scale_optional_value(recipe.total_fat_g, scale),
            carbs_g=_scale_optional_value(recipe.total_carbs_g, scale),
            sugar_g=_scale_optional_value(recipe.total_sugar_g, scale),
            other_nutrients={
                nutrient: _scale_json_nutrient(value, scale)
                for nutrient, value in recipe.other_nutrients.items()
            },
        )


def _scale_optional_value(value: float | None, scale: float) -> float | None:
    """Scale a nullable denormalized nutrition field."""
    return value * scale if value is not None else None


def _scale_json_nutrient(value: object, scale: float) -> object:
    """Scale numeric supplemental nutrients while retaining other metadata."""
    return value * scale if isinstance(value, (int, float)) else value
