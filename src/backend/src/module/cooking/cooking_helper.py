"""Pure cooking transformations and transactional inventory write helpers."""

from dataclasses import dataclass
from datetime import UTC, datetime
from decimal import Decimal
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.model.cooking_consumption_model import CookingConsumptionModel
from src.model.cooking_session_model import CookingSessionModel
from src.model.enum_model import (
    CookingConsumptionMode,
    CookingSessionStatus,
    InventoryBatchStatus,
    InventoryLedgerEventType,
)
from src.model.inventory_batch_model import InventoryBatchModel
from src.model.inventory_ledger_entry_model import InventoryLedgerEntryModel
from src.model.master_ingredient_model import MasterIngredientModel
from src.model.recipe_ingredient_model import RecipeIngredientModel
from src.model.recipe_model import RecipeModel
from src.module.cooking.cooking_dto import (
    CompleteCookingSessionRequestDTO,
    CookingCompletionResponseDTO,
    CookingConsumptionDTO,
    CookingConsumptionInputDTO,
    CookingPreviewResponseDTO,
    CookingPreviewWarningCode,
    CookingPreviewWarningDTO,
    CookingSessionDTO,
    MissingIngredientDTO,
    NutritionEstimateDTO,
    ProposedBatchDeductionDTO,
    ScaledRecipeIngredientDTO,
    UpdatedInventoryBatchDTO,
)
from src.service.fefo_service import (
    FEFOAllocation,
    FEFOAllocationResult,
    FEFOCandidate,
    FEFOService,
    are_units_compatible,
)

_QUANTITY_EPSILON = 1e-9


class CookingDomainError(HTTPException):
    """Base class for safe cooking-domain API errors."""

    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Cooking request could not be completed"

    def __init__(self, detail: str | None = None) -> None:
        """Build a stable client-safe cooking domain error."""
        super().__init__(
            status_code=self.status_code,
            detail=detail or self.default_detail,
        )


class RecipeNotFoundError(CookingDomainError):
    """Raised when the selected seeded recipe does not exist."""

    status_code = status.HTTP_404_NOT_FOUND
    default_detail = "Recipe was not found"


class CookingSessionNotFoundError(CookingDomainError):
    """Raised when one user attempts to access another or unknown session."""

    status_code = status.HTTP_404_NOT_FOUND
    default_detail = "Cooking session was not found"


class MealPlanItemNotFoundError(CookingDomainError):
    """Raised when a meal-plan item is unknown or not owned by the caller."""

    status_code = status.HTTP_404_NOT_FOUND
    default_detail = "Meal plan item was not found"


class CookingCompletionConflictError(CookingDomainError):
    """Raised when a completed session or idempotency key cannot be reused."""

    status_code = status.HTTP_409_CONFLICT
    default_detail = "Cooking session cannot be completed"


class InsufficientInventoryError(CookingCompletionConflictError):
    """Raised before writes when current inventory cannot satisfy cooking."""

    default_detail = "The requested cooking quantities are no longer available"


class InvalidCookingConsumptionError(CookingDomainError):
    """Raised for a custom selection that does not match locked inventory."""

    default_detail = "The submitted cooking consumption is invalid"


@dataclass(frozen=True, slots=True)
class ResolvedConsumption:
    """One validated deduction expressed in the selected batch's unit."""

    recipe_ingredient_id: UUID
    inventory_batch_id: UUID
    quantity: float


class CookingHelper:
    """Keep cooking calculations and record mapping outside request orchestration."""

    def __init__(self, db_session: AsyncSession, fefo_service: FEFOService) -> None:
        """Store dependencies used for allocation and transactional record creation."""
        self.db_session = db_session
        self.fefo_service = fefo_service

    def resolve_consumptions(
        self,
        cooking_session: CookingSessionModel,
        recipe: RecipeModel,
        recipe_ingredients: list[tuple[RecipeIngredientModel, MasterIngredientModel]],
        locked_batches: list[InventoryBatchModel],
        request: CompleteCookingSessionRequestDTO,
    ) -> list[ResolvedConsumption]:
        """Resolve and revalidate the actual batch deductions for one completion."""
        if request.consumption_mode in {
            CookingConsumptionMode.EXACT,
            CookingConsumptionMode.HALF,
        }:
            return self._resolve_automatic_consumptions(
                cooking_session,
                recipe,
                recipe_ingredients,
                locked_batches,
                request.consumption_mode,
            )
        return self._resolve_explicit_consumptions(
            recipe_ingredients,
            locked_batches,
            request.consumptions,
            request.consumption_mode,
        )

    def apply_completion(
        self,
        cooking_session: CookingSessionModel,
        recipe: RecipeModel,
        locked_batches: list[InventoryBatchModel],
        resolved_consumptions: list[ResolvedConsumption],
        consumption_mode: CookingConsumptionMode,
    ) -> CookingCompletionResponseDTO:
        """Mutate locked batches and add auditable records to the current transaction."""
        batch_by_id = {batch.id: batch for batch in locked_batches}
        consumption_dtos: list[CookingConsumptionDTO] = []
        updated_batches: list[UpdatedInventoryBatchDTO] = []
        for resolved_consumption in resolved_consumptions:
            batch = batch_by_id[resolved_consumption.inventory_batch_id]
            quantity_before = batch.current_quantity
            quantity_after = quantity_before - resolved_consumption.quantity
            if quantity_after < -_QUANTITY_EPSILON:
                raise InsufficientInventoryError()
            batch.current_quantity = max(0.0, quantity_after)
            if batch.current_quantity <= _QUANTITY_EPSILON:
                batch.status = InventoryBatchStatus.DEPLETED
            self.db_session.add(
                CookingConsumptionModel(
                    cooking_session_id=cooking_session.id,
                    recipe_ingredient_id=resolved_consumption.recipe_ingredient_id,
                    inventory_batch_id=batch.id,
                    quantity=resolved_consumption.quantity,
                    unit=batch.unit,
                )
            )
            self.db_session.add(
                InventoryLedgerEntryModel(
                    user_id=cooking_session.user_id,
                    inventory_batch_id=batch.id,
                    event_type=InventoryLedgerEventType.COOKING_CONSUMPTION,
                    quantity_before=quantity_before,
                    quantity_delta=-resolved_consumption.quantity,
                    quantity_after=batch.current_quantity,
                    unit=batch.unit,
                    cooking_session_id=cooking_session.id,
                    idempotency_key=cooking_session.idempotency_key,
                )
            )
            consumption_dtos.append(
                CookingConsumptionDTO(
                    recipe_ingredient_id=resolved_consumption.recipe_ingredient_id,
                    inventory_batch_id=batch.id,
                    quantity=resolved_consumption.quantity,
                    unit=batch.unit,
                )
            )
            updated_batches.append(self.to_updated_batch_dto(batch))
        cooking_session.status = CookingSessionStatus.COMPLETED
        cooking_session.consumption_mode = consumption_mode
        cooking_session.completed_at = datetime.now(UTC)
        cooking_session.nutrition_snapshot = self.completion_nutrition_snapshot(
            cooking_session,
            recipe,
            consumption_mode,
        )
        return CookingCompletionResponseDTO(
            session=self.to_session_dto(cooking_session),
            consumptions=consumption_dtos,
            updated_batches=updated_batches,
        )

    def build_preview(
        self,
        recipe: RecipeModel,
        recipe_ingredients: list[tuple[RecipeIngredientModel, MasterIngredientModel]],
        batches: list[InventoryBatchModel],
        servings: float,
    ) -> CookingPreviewResponseDTO:
        """Build a read-only, serving-scaled FEFO preview response."""
        scale = _serving_scale(servings, recipe.default_servings)
        now = datetime.now(UTC)
        scaled_ingredients: list[ScaledRecipeIngredientDTO] = []
        deductions: list[ProposedBatchDeductionDTO] = []
        missing_ingredients: list[MissingIngredientDTO] = []
        warnings: list[CookingPreviewWarningDTO] = []
        for recipe_ingredient, ingredient in recipe_ingredients:
            required_quantity = float(
                _as_decimal(recipe_ingredient.required_quantity) * scale,
            )
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
            nutrition_estimate=self.scale_nutrition(recipe, scale),
            warnings=warnings,
        )

    def build_saved_completion_response(
        self,
        cooking_session: CookingSessionModel,
        consumptions: list[CookingConsumptionModel],
        batches: list[InventoryBatchModel],
    ) -> CookingCompletionResponseDTO:
        """Map previously persisted completion records to an idempotent response."""
        return CookingCompletionResponseDTO(
            session=self.to_session_dto(cooking_session),
            consumptions=[
                CookingConsumptionDTO(
                    recipe_ingredient_id=consumption.recipe_ingredient_id,
                    inventory_batch_id=consumption.inventory_batch_id,
                    quantity=consumption.quantity,
                    unit=consumption.unit,
                )
                for consumption in consumptions
            ],
            updated_batches=[self.to_updated_batch_dto(batch) for batch in batches],
        )

    @staticmethod
    def insufficient_inventory_detail(
        missing_ingredients: list[MissingIngredientDTO],
    ) -> str:
        """Describe the currently missing recipe quantities without exposing batches."""
        missing_details = ", ".join(
            (
                f"{missing.ingredient_name}: "
                f"missing {missing.missing_quantity:g} {missing.unit.value}"
            )
            for missing in missing_ingredients
        )
        return f"Insufficient inventory to create cooking session: {missing_details}"

    def completion_nutrition_snapshot(
        self,
        cooking_session: CookingSessionModel,
        recipe: RecipeModel,
        consumption_mode: CookingConsumptionMode,
    ) -> dict[str, object]:
        """Preserve normal nutrition or halve it for a HALF completion."""
        if consumption_mode is not CookingConsumptionMode.HALF:
            return cooking_session.nutrition_snapshot
        nutrition = self.scale_nutrition(
            recipe,
            _serving_scale(cooking_session.servings, recipe.default_servings)
            * Decimal("0.5"),
        )
        return nutrition.model_dump()

    @staticmethod
    def to_session_dto(cooking_session: CookingSessionModel) -> CookingSessionDTO:
        """Map a persistent cooking session to the public response shape."""
        return CookingSessionDTO(
            id=cooking_session.id,
            recipe_id=cooking_session.recipe_id,
            meal_plan_item_id=cooking_session.meal_plan_item_id,
            servings=cooking_session.servings,
            status=cooking_session.status,
            consumption_mode=cooking_session.consumption_mode,
            nutrition_snapshot=cooking_session.nutrition_snapshot,
            completed_at=cooking_session.completed_at,
        )

    @staticmethod
    def to_updated_batch_dto(batch: InventoryBatchModel) -> UpdatedInventoryBatchDTO:
        """Map a changed inventory batch to its public post-completion state."""
        return UpdatedInventoryBatchDTO(
            inventory_batch_id=batch.id,
            current_quantity=batch.current_quantity,
            unit=batch.unit,
            status=batch.status.value,
        )

    @staticmethod
    def scale_nutrition(recipe: RecipeModel, scale: Decimal) -> NutritionEstimateDTO:
        """Scale denormalized recipe nutrition for the requested servings."""
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

    def _resolve_automatic_consumptions(
        self,
        cooking_session: CookingSessionModel,
        recipe: RecipeModel,
        recipe_ingredients: list[tuple[RecipeIngredientModel, MasterIngredientModel]],
        locked_batches: list[InventoryBatchModel],
        consumption_mode: CookingConsumptionMode,
    ) -> list[ResolvedConsumption]:
        scale = _serving_scale(cooking_session.servings, recipe.default_servings) * (
            Decimal("0.5")
            if consumption_mode is CookingConsumptionMode.HALF
            else Decimal(1)
        )
        now = datetime.now(UTC)
        resolved: list[ResolvedConsumption] = []
        for recipe_ingredient, ingredient in recipe_ingredients:
            allocation_result = self.fefo_service.allocate(
                float(_as_decimal(recipe_ingredient.required_quantity) * scale),
                recipe_ingredient.unit,
                self._to_fefo_candidates(locked_batches, ingredient.id),
                now,
            )
            if allocation_result.missing_quantity > _QUANTITY_EPSILON:
                raise InsufficientInventoryError()
            resolved.extend(
                ResolvedConsumption(
                    recipe_ingredient_id=recipe_ingredient.id,
                    inventory_batch_id=allocation.batch_id,
                    quantity=allocation.batch_quantity,
                )
                for allocation in allocation_result.allocations
            )
        return resolved

    def _resolve_explicit_consumptions(
        self,
        recipe_ingredients: list[tuple[RecipeIngredientModel, MasterIngredientModel]],
        locked_batches: list[InventoryBatchModel],
        requested_consumptions: list[CookingConsumptionInputDTO],
        consumption_mode: CookingConsumptionMode,
    ) -> list[ResolvedConsumption]:
        ingredient_by_recipe_ingredient_id = {
            recipe_ingredient.id: recipe_ingredient
            for recipe_ingredient, _ in recipe_ingredients
        }
        batch_by_id = {batch.id: batch for batch in locked_batches}
        now = datetime.now(UTC)
        resolved: list[ResolvedConsumption] = []
        for requested_consumption in requested_consumptions:
            recipe_ingredient = ingredient_by_recipe_ingredient_id.get(
                requested_consumption.recipe_ingredient_id,
            )
            batch = batch_by_id.get(requested_consumption.inventory_batch_id)
            if recipe_ingredient is None or batch is None:
                raise InvalidCookingConsumptionError()
            quantity = self._resolve_explicit_quantity(
                requested_consumption,
                batch,
                consumption_mode,
            )
            self._validate_explicit_consumption(
                recipe_ingredient,
                batch,
                quantity,
                now,
            )
            resolved.append(
                ResolvedConsumption(
                    recipe_ingredient_id=recipe_ingredient.id,
                    inventory_batch_id=batch.id,
                    quantity=quantity,
                )
            )
        return resolved

    @staticmethod
    def _resolve_explicit_quantity(
        requested_consumption: CookingConsumptionInputDTO,
        batch: InventoryBatchModel,
        consumption_mode: CookingConsumptionMode,
    ) -> float:
        if consumption_mode is CookingConsumptionMode.USE_ALL_MATCHED:
            return batch.current_quantity
        quantity = requested_consumption.quantity
        if quantity is None:
            raise InvalidCookingConsumptionError()
        return quantity

    @staticmethod
    def _validate_explicit_consumption(
        recipe_ingredient: RecipeIngredientModel,
        batch: InventoryBatchModel,
        quantity: float,
        now: datetime,
    ) -> None:
        if batch.master_ingredient_id != recipe_ingredient.master_ingredient_id:
            raise InvalidCookingConsumptionError(
                "Batch does not match recipe ingredient"
            )
        if batch.expires_at is not None and batch.expires_at < now:
            raise InvalidCookingConsumptionError(
                "Expired inventory batch cannot be consumed"
            )
        if not are_units_compatible(batch.unit, recipe_ingredient.unit):
            raise InvalidCookingConsumptionError("Batch unit is incompatible")
        if quantity > batch.current_quantity + _QUANTITY_EPSILON:
            raise InsufficientInventoryError()

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


def _as_decimal(value: Decimal | float) -> Decimal:
    """Normalize legacy floats and database Numeric values for calculation."""
    return Decimal(str(value))


def _serving_scale(
    servings: float,
    default_servings: Decimal | float,
) -> Decimal:
    """Return the precise multiplier for a current public float serving value."""
    return Decimal(str(servings)) / _as_decimal(default_servings)


def _scale_optional_value(
    value: Decimal | float | None,
    scale: Decimal,
) -> float | None:
    """Scale a nullable denormalized nutrition field."""
    if value is None:
        return None
    return float(_as_decimal(value) * scale)


def _scale_json_nutrient(value: object, scale: Decimal) -> object:
    """Scale numeric supplemental nutrients while retaining other metadata."""
    if isinstance(value, (int, float, Decimal)):
        return float(_as_decimal(value) * scale)
    return value
