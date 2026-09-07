"""Database-backed shopping lists with atomic inventory synchronisation."""

import json
from dataclasses import dataclass, field
from datetime import UTC, datetime
from decimal import Decimal
from hashlib import sha256
from typing import Generic, TypeVar, cast
from uuid import UUID

from fastapi import HTTPException, status
from pydantic import BaseModel
from sqlalchemy import func, or_, select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from src.model.enum_model import (
    InventoryBatchStatus,
    MealPlanItemStatus,
    MeasurementUnit,
    ShoppingListStatus,
)
from src.model.inventory_batch_model import InventoryBatchModel
from src.model.master_ingredient_model import MasterIngredientModel
from src.model.meal_plan_item_model import MealPlanItemModel
from src.model.meal_plan_model import MealPlanModel
from src.model.recipe_ingredient_model import RecipeIngredientModel
from src.model.recipe_model import RecipeModel
from src.model.shopping_list_item_model import ShoppingListItemModel
from src.model.shopping_list_model import ShoppingListModel
from src.model.shopping_mutation_receipt_model import ShoppingMutationReceiptModel
from src.module.inventory.inventory_dto import CreateInventoryBatchRequestDTO
from src.module.inventory.inventory_service import InventoryService
from src.module.shopping_lists.shopping_dto import (
    CreateShoppingItemRequestDTO,
    GenerateShoppingListRequestDTO,
    ShoppingListCollectionResponseDTO,
    ShoppingListDTO,
    ShoppingListItemDTO,
    ShoppingListQueryDTO,
    ShoppingListSummaryDTO,
    ShoppingPurchaseDTO,
    UpdateShoppingListItemRequestDTO,
)
from src.service.fefo_service import are_units_compatible, convert_quantity


class ShoppingListNotFoundError(HTTPException):
    """Hide whether an unknown list belongs to another user."""

    def __init__(self) -> None:
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Shopping list was not found",
        )


class ShoppingListItemNotFoundError(HTTPException):
    """Hide whether an unknown item belongs to an owned shopping list."""

    def __init__(self) -> None:
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Shopping list item was not found",
        )


class ShoppingMealPlanNotFoundError(HTTPException):
    """Reject a list generation request outside the current user's plans."""

    def __init__(self) -> None:
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Meal plan was not found",
        )


class ShoppingIngredientNotFoundError(HTTPException):
    """Reject a manual item that names an unknown catalog ingredient."""

    def __init__(self) -> None:
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ingredient was not found",
        )


class ShoppingListConflictError(HTTPException):
    """Reject unsafe edits and lifecycle transitions."""

    def __init__(self, detail: str) -> None:
        super().__init__(status_code=status.HTTP_409_CONFLICT, detail=detail)


ReceiptDTO = TypeVar("ReceiptDTO", bound=BaseModel)


@dataclass(frozen=True, slots=True)
class ShoppingMutationResult(Generic[ReceiptDTO]):
    """A public mutation snapshot and the status code that created it."""

    status_code: int
    body: ReceiptDTO


@dataclass(frozen=True, slots=True)
class _MutationReceiptRequest:
    """Canonical receipt lookup scope derived before a shopping mutation."""

    user_id: UUID
    method: str
    request_path: str
    idempotency_key: str
    key_hash: str
    request_fingerprint: str


@dataclass(slots=True)
class _Requirement:
    """One mergeable recipe requirement before inventory subtraction."""

    master_ingredient_id: UUID
    name: str
    quantity: float
    unit: MeasurementUnit
    recipe_ids: list[str] = field(default_factory=list)


class ShoppingService:
    """Generate and mutate owned lists while keeping inventory and ledger atomic."""

    def __init__(
        self,
        db_session: AsyncSession,
        inventory_service: InventoryService,
    ) -> None:
        self.db_session = db_session
        self.inventory_service = inventory_service

    async def generate(
        self,
        user_id: UUID,
        body: GenerateShoppingListRequestDTO,
        idempotency_key: str,
    ) -> ShoppingMutationResult[ShoppingListDTO]:
        """Generate one active list once for an owned plan using usable inventory."""
        receipt_request = self._receipt_request(
            user_id,
            "POST",
            "/api/shopping-lists/generate",
            idempotency_key,
            body,
        )
        try:
            plan = await self._find_plan(user_id, body.meal_plan_id, lock=True)
            receipt = await self._find_receipt(receipt_request)
            if receipt is not None:
                return self._replay_receipt(receipt, ShoppingListDTO)
            existing = await self._find_active_list(user_id, plan.id)
            if existing is not None:
                result = await self._to_list_dto(existing)
            else:
                requirements = await self._requirements_for_plan(plan.id)
                available = await self._available_quantities(user_id, requirements)
                shopping_list = ShoppingListModel(
                    user_id=user_id,
                    meal_plan_id=plan.id,
                    status=ShoppingListStatus.ACTIVE,
                    generated_at=datetime.now(UTC),
                )
                self.db_session.add(shopping_list)
                await self.db_session.flush()
                for requirement in requirements:
                    available_quantity = min(
                        requirement.quantity,
                        available.get(
                            (requirement.master_ingredient_id, requirement.unit), 0.0
                        ),
                    )
                    missing_quantity = requirement.quantity - available_quantity
                    if missing_quantity > 0:
                        self.db_session.add(
                            ShoppingListItemModel(
                                shopping_list_id=shopping_list.id,
                                master_ingredient_id=requirement.master_ingredient_id,
                                custom_name=None,
                                required_quantity=requirement.quantity,
                                available_quantity=available_quantity,
                                missing_quantity=missing_quantity,
                                unit=requirement.unit,
                                estimated_cost=None,
                                is_checked=False,
                                source_metadata={
                                    "generated": True,
                                    "recipe_ids": requirement.recipe_ids,
                                },
                            )
                        )
                result = await self._to_list_dto(shopping_list)
            self._record_receipt(receipt_request, status.HTTP_201_CREATED, result)
            await self.db_session.commit()
            return ShoppingMutationResult(status.HTTP_201_CREATED, result)
        except IntegrityError as error:
            receipt = await self._receipt_after_integrity_error(receipt_request)
            if receipt is not None:
                return self._replay_receipt(receipt, ShoppingListDTO)
            raise ShoppingListConflictError("Shopping list generation conflicted") from error
        except (HTTPException, SQLAlchemyError):
            await self.db_session.rollback()
            raise

    async def get(self, user_id: UUID, list_id: UUID) -> ShoppingListDTO:
        """Read one owned list and all of its traceable line items."""
        try:
            shopping_list = await self._find_list(user_id, list_id, lock=False)
            return await self._to_list_dto(shopping_list)
        except SQLAlchemyError:
            await self.db_session.rollback()
            raise

    async def list_lists(
        self,
        user_id: UUID,
        query: ShoppingListQueryDTO,
    ) -> ShoppingListCollectionResponseDTO:
        """List one user's shopping-list metadata in deterministic newest-first order."""
        filters = [ShoppingListModel.user_id == user_id]
        if query.list_status is not None:
            filters.append(ShoppingListModel.status == query.list_status)
        if query.meal_plan_id is not None:
            filters.append(ShoppingListModel.meal_plan_id == query.meal_plan_id)
        try:
            total = int(
                (
                    await self.db_session.execute(
                        select(func.count())
                        .select_from(ShoppingListModel)
                        .where(*filters)
                    )
                ).scalar_one()
            )
            result = await self.db_session.execute(
                select(ShoppingListModel)
                .where(*filters)
                .order_by(
                    ShoppingListModel.created_at.desc(),
                    ShoppingListModel.id.desc(),
                )
                .offset(query.offset)
                .limit(query.limit)
            )
            return ShoppingListCollectionResponseDTO(
                items=[
                    self._to_summary_dto(shopping_list)
                    for shopping_list in result.scalars().all()
                ],
                total=total,
                limit=query.limit,
                offset=query.offset,
            )
        except SQLAlchemyError:
            await self.db_session.rollback()
            raise

    async def add_item(
        self,
        user_id: UUID,
        list_id: UUID,
        body: CreateShoppingItemRequestDTO,
        idempotency_key: str,
    ) -> ShoppingMutationResult[ShoppingListItemDTO]:
        """Persist an unchecked manual reminder without changing inventory."""
        receipt_request = self._receipt_request(
            user_id,
            "POST",
            f"/api/shopping-lists/{list_id}/items",
            idempotency_key,
            body,
        )
        try:
            shopping_list = await self._find_list(user_id, list_id, lock=True)
            receipt = await self._find_receipt(receipt_request)
            if receipt is not None:
                return self._replay_receipt(receipt, ShoppingListItemDTO)
            self._ensure_active(shopping_list)
            ingredient = await self._find_ingredient(body.master_ingredient_id)
            item = ShoppingListItemModel(
                shopping_list_id=shopping_list.id,
                master_ingredient_id=body.master_ingredient_id,
                custom_name=body.custom_name,
                required_quantity=body.quantity,
                available_quantity=0.0,
                missing_quantity=body.quantity,
                unit=body.unit,
                estimated_cost=body.estimated_cost,
                is_checked=False,
                source_metadata={"generated": False, "recipe_ids": []},
            )
            self.db_session.add(item)
            await self.db_session.flush()
            result = self._to_item_dto(item, ingredient.name if ingredient else None)
            self._record_receipt(receipt_request, status.HTTP_201_CREATED, result)
            await self.db_session.commit()
            return ShoppingMutationResult(status.HTTP_201_CREATED, result)
        except IntegrityError as error:
            receipt = await self._receipt_after_integrity_error(receipt_request)
            if receipt is not None:
                return self._replay_receipt(receipt, ShoppingListItemDTO)
            raise ShoppingListConflictError("Shopping item creation conflicted") from error
        except (HTTPException, SQLAlchemyError):
            await self.db_session.rollback()
            raise

    async def update_item(
        self,
        user_id: UUID,
        list_id: UUID,
        item_id: UUID,
        body: UpdateShoppingListItemRequestDTO,
        idempotency_key: str,
    ) -> ShoppingMutationResult[ShoppingListItemDTO]:
        """Edit an unchecked manual item or atomically sync a checked purchase."""
        receipt_request = self._receipt_request(
            user_id,
            "PATCH",
            f"/api/shopping-lists/{list_id}/items/{item_id}",
            idempotency_key,
            body,
        )
        try:
            shopping_list = await self._find_list(user_id, list_id, lock=True)
            receipt = await self._find_receipt(receipt_request)
            if receipt is not None:
                return self._replay_receipt(receipt, ShoppingListItemDTO)
            self._ensure_active(shopping_list)
            item = await self._find_item(shopping_list.id, item_id, lock=True)
            ingredient = await self._find_ingredient(item.master_ingredient_id)
            if body.quantity is not None:
                self._update_manual_quantity(item, body.quantity)
            if body.estimated_cost is not None:
                self._update_manual_cost(item, body.estimated_cost)
            if body.checked is True:
                await self._check_item(
                    user_id,
                    item,
                    ingredient,
                    body.purchase,
                    idempotency_key,
                )
            elif body.checked is False:
                item.is_checked = False
            result = self._to_item_dto(item, ingredient.name if ingredient else None)
            self._record_receipt(receipt_request, status.HTTP_200_OK, result)
            await self.db_session.commit()
            return ShoppingMutationResult(status.HTTP_200_OK, result)
        except IntegrityError as error:
            receipt = await self._receipt_after_integrity_error(receipt_request)
            if receipt is not None:
                return self._replay_receipt(receipt, ShoppingListItemDTO)
            raise ShoppingListConflictError("Shopping item update conflicted") from error
        except (HTTPException, SQLAlchemyError):
            await self.db_session.rollback()
            raise

    async def remove_item(
        self,
        user_id: UUID,
        list_id: UUID,
        item_id: UUID,
        idempotency_key: str,
    ) -> int:
        """Remove only an unchecked manual reminder from an owned active list."""
        receipt_request = self._receipt_request(
            user_id,
            "DELETE",
            f"/api/shopping-lists/{list_id}/items/{item_id}",
            idempotency_key,
            None,
        )
        try:
            shopping_list = await self._find_list(user_id, list_id, lock=True)
            receipt = await self._find_receipt(receipt_request)
            if receipt is not None:
                return self._replay_delete_receipt(receipt)
            self._ensure_active(shopping_list)
            item = await self._find_item(shopping_list.id, item_id, lock=True)
            if self._is_generated(item):
                raise ShoppingListConflictError("Generated shopping items cannot be deleted")
            if item.is_checked:
                raise ShoppingListConflictError("Checked shopping items cannot be deleted")
            await self.db_session.delete(item)
            self._record_receipt(receipt_request, status.HTTP_204_NO_CONTENT, None)
            await self.db_session.commit()
            return status.HTTP_204_NO_CONTENT
        except IntegrityError as error:
            receipt = await self._receipt_after_integrity_error(receipt_request)
            if receipt is not None:
                return self._replay_delete_receipt(receipt)
            raise ShoppingListConflictError("Shopping item deletion conflicted") from error
        except (HTTPException, SQLAlchemyError):
            await self.db_session.rollback()
            raise

    @staticmethod
    def _receipt_request(
        user_id: UUID,
        method: str,
        request_path: str,
        idempotency_key: str,
        body: BaseModel | None,
    ) -> _MutationReceiptRequest:
        canonical_path = request_path.partition("?")[0]
        payload = body.model_dump(mode="json", exclude_unset=True) if body else {}
        serialized_payload = json.dumps(
            payload,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
        )
        return _MutationReceiptRequest(
            user_id=user_id,
            method=method,
            request_path=canonical_path,
            idempotency_key=idempotency_key,
            key_hash=sha256(idempotency_key.encode()).hexdigest(),
            request_fingerprint=sha256(serialized_payload.encode()).hexdigest(),
        )

    async def _find_receipt(
        self,
        request: _MutationReceiptRequest,
    ) -> ShoppingMutationReceiptModel | None:
        receipt = (
            await self.db_session.execute(
                select(ShoppingMutationReceiptModel).where(
                    ShoppingMutationReceiptModel.user_id == request.user_id,
                    ShoppingMutationReceiptModel.method == request.method,
                    ShoppingMutationReceiptModel.request_path == request.request_path,
                    ShoppingMutationReceiptModel.key_hash == request.key_hash,
                )
            )
        ).scalar_one_or_none()
        if receipt is not None and (
            receipt.idempotency_key != request.idempotency_key
            or receipt.request_fingerprint != request.request_fingerprint
        ):
            raise ShoppingListConflictError(
                "Idempotency key was reused with a different request"
            )
        return receipt

    async def _receipt_after_integrity_error(
        self,
        request: _MutationReceiptRequest,
    ) -> ShoppingMutationReceiptModel | None:
        """Reset a failed transaction before reading a concurrent receipt winner."""
        await self.db_session.rollback()
        return await self._find_receipt(request)

    @staticmethod
    def _replay_receipt(
        receipt: ShoppingMutationReceiptModel,
        dto_type: type[ReceiptDTO],
    ) -> ShoppingMutationResult[ReceiptDTO]:
        if receipt.response_body is None:
            raise ShoppingListConflictError("Stored shopping receipt has no response body")
        return ShoppingMutationResult(
            receipt.response_status,
            dto_type.model_validate(receipt.response_body),
        )

    @staticmethod
    def _replay_delete_receipt(receipt: ShoppingMutationReceiptModel) -> int:
        if receipt.response_status != status.HTTP_204_NO_CONTENT:
            raise ShoppingListConflictError("Stored shopping receipt has an invalid status")
        return receipt.response_status

    def _record_receipt(
        self,
        request: _MutationReceiptRequest,
        response_status: int,
        response_body: BaseModel | None,
    ) -> None:
        self.db_session.add(
            ShoppingMutationReceiptModel(
                user_id=request.user_id,
                method=request.method,
                request_path=request.request_path,
                idempotency_key=request.idempotency_key,
                key_hash=request.key_hash,
                request_fingerprint=request.request_fingerprint,
                response_status=response_status,
                response_body=(
                    cast(dict[str, object], response_body.model_dump(mode="json"))
                    if response_body is not None
                    else None
                ),
            )
        )

    async def _check_item(
        self,
        user_id: UUID,
        item: ShoppingListItemModel,
        ingredient: MasterIngredientModel | None,
        purchase: ShoppingPurchaseDTO | None,
        idempotency_key: str,
    ) -> None:
        metadata = dict(item.source_metadata)
        if item.is_checked or metadata.get("inventory_batch_id") is not None:
            item.is_checked = True
            return
        if purchase is None:
            raise ValueError("purchase is required when checked is true")
        quantity = item.missing_quantity if self._is_generated(item) else item.required_quantity
        batch = await self.inventory_service.stage_batch(
            user_id,
            self._purchase_batch_request(item, ingredient, quantity, purchase),
            f"{idempotency_key}:{item.id}",
            reason="Shopping item purchase",
        )
        metadata["inventory_batch_id"] = str(batch.id)
        item.source_metadata = metadata
        item.is_checked = True

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
            raise ShoppingMealPlanNotFoundError()
        return plan

    async def _find_active_list(
        self, user_id: UUID, plan_id: UUID
    ) -> ShoppingListModel | None:
        statement = (
            select(ShoppingListModel)
            .where(
                ShoppingListModel.user_id == user_id,
                ShoppingListModel.meal_plan_id == plan_id,
                ShoppingListModel.status == ShoppingListStatus.ACTIVE,
            )
            .order_by(ShoppingListModel.created_at.desc())
            .limit(1)
        )
        return (await self.db_session.execute(statement)).scalar_one_or_none()

    async def _find_list(
        self, user_id: UUID, list_id: UUID, *, lock: bool
    ) -> ShoppingListModel:
        statement = select(ShoppingListModel).where(
            ShoppingListModel.id == list_id,
            ShoppingListModel.user_id == user_id,
        )
        if lock:
            statement = statement.with_for_update()
        shopping_list = (await self.db_session.execute(statement)).scalar_one_or_none()
        if shopping_list is None:
            raise ShoppingListNotFoundError()
        return shopping_list

    async def _find_item(
        self, list_id: UUID, item_id: UUID, *, lock: bool
    ) -> ShoppingListItemModel:
        statement = select(ShoppingListItemModel).where(
            ShoppingListItemModel.id == item_id,
            ShoppingListItemModel.shopping_list_id == list_id,
        )
        if lock:
            statement = statement.with_for_update()
        item = (await self.db_session.execute(statement)).scalar_one_or_none()
        if item is None:
            raise ShoppingListItemNotFoundError()
        return item

    async def _find_ingredient(
        self, ingredient_id: UUID | None
    ) -> MasterIngredientModel | None:
        if ingredient_id is None:
            return None
        ingredient = (
            await self.db_session.execute(
                select(MasterIngredientModel).where(
                    MasterIngredientModel.id == ingredient_id,
                )
            )
        ).scalar_one_or_none()
        if ingredient is None:
            raise ShoppingIngredientNotFoundError()
        return ingredient

    async def _requirements_for_plan(self, plan_id: UUID) -> list[_Requirement]:
        result = await self.db_session.execute(
            select(
                MealPlanItemModel,
                RecipeModel,
                RecipeIngredientModel,
                MasterIngredientModel,
            )
            .join(RecipeModel, RecipeModel.id == MealPlanItemModel.recipe_id)
            .join(
                RecipeIngredientModel,
                RecipeIngredientModel.recipe_id == RecipeModel.id,
            )
            .join(
                MasterIngredientModel,
                MasterIngredientModel.id == RecipeIngredientModel.master_ingredient_id,
            )
            .where(
                MealPlanItemModel.meal_plan_id == plan_id,
                MealPlanItemModel.status == MealPlanItemStatus.PLANNED,
            )
        )
        requirements: list[_Requirement] = []
        for item, recipe, ingredient, master in result.tuples().all():
            if ingredient.is_optional:
                continue
            quantity = float(
                ingredient.required_quantity
                * Decimal(str(item.servings))
                / recipe.default_servings
            )
            self._merge_requirement(
                requirements,
                _Requirement(
                    master_ingredient_id=master.id,
                    name=master.name,
                    quantity=quantity,
                    unit=ingredient.unit,
                    recipe_ids=[str(recipe.id)],
                ),
            )
        return requirements

    async def _available_quantities(
        self, user_id: UUID, requirements: list[_Requirement]
    ) -> dict[tuple[UUID, MeasurementUnit], float]:
        ingredient_ids = {item.master_ingredient_id for item in requirements}
        if not ingredient_ids:
            return {}
        now = datetime.now(UTC)
        result = await self.db_session.execute(
            select(InventoryBatchModel).where(
                InventoryBatchModel.user_id == user_id,
                InventoryBatchModel.status == InventoryBatchStatus.ACTIVE,
                InventoryBatchModel.current_quantity > 0,
                InventoryBatchModel.master_ingredient_id.in_(ingredient_ids),
                or_(
                    InventoryBatchModel.expires_at.is_(None),
                    InventoryBatchModel.expires_at >= now,
                ),
            )
        )
        batches = list(result.scalars().all())
        available: dict[tuple[UUID, MeasurementUnit], float] = {}
        for requirement in requirements:
            key = (requirement.master_ingredient_id, requirement.unit)
            available[key] = sum(
                convert_quantity(batch.current_quantity, batch.unit, requirement.unit)
                for batch in batches
                if batch.master_ingredient_id == requirement.master_ingredient_id
                and are_units_compatible(batch.unit, requirement.unit)
            )
        return available

    async def _to_list_dto(self, shopping_list: ShoppingListModel) -> ShoppingListDTO:
        result = await self.db_session.execute(
            select(ShoppingListItemModel, MasterIngredientModel)
            .outerjoin(
                MasterIngredientModel,
                MasterIngredientModel.id == ShoppingListItemModel.master_ingredient_id,
            )
            .where(ShoppingListItemModel.shopping_list_id == shopping_list.id)
            .order_by(ShoppingListItemModel.created_at, ShoppingListItemModel.id)
        )
        return ShoppingListDTO(
            id=shopping_list.id,
            meal_plan_id=shopping_list.meal_plan_id,
            status=shopping_list.status,
            generated_at=shopping_list.generated_at,
            items=[
                self._to_item_dto(item, ingredient.name if ingredient else None)
                for item, ingredient in result.tuples().all()
            ],
        )

    @staticmethod
    def _merge_requirement(
        requirements: list[_Requirement], candidate: _Requirement
    ) -> None:
        for requirement in requirements:
            if (
                requirement.master_ingredient_id == candidate.master_ingredient_id
                and are_units_compatible(candidate.unit, requirement.unit)
            ):
                requirement.quantity += convert_quantity(
                    candidate.quantity, candidate.unit, requirement.unit
                )
                requirement.recipe_ids.extend(candidate.recipe_ids)
                return
        requirements.append(candidate)

    @staticmethod
    def _ensure_active(shopping_list: ShoppingListModel) -> None:
        if shopping_list.status is not ShoppingListStatus.ACTIVE:
            raise ShoppingListConflictError("Shopping list is archived")

    @staticmethod
    def _is_generated(item: ShoppingListItemModel) -> bool:
        return item.source_metadata.get("generated") is True

    @staticmethod
    def _update_manual_quantity(item: ShoppingListItemModel, quantity: float) -> None:
        if item.is_checked or ShoppingService._is_generated(item):
            raise ShoppingListConflictError("Only unchecked manual items can be edited")
        item.required_quantity = quantity
        item.missing_quantity = quantity

    @staticmethod
    def _update_manual_cost(item: ShoppingListItemModel, cost: float) -> None:
        if item.is_checked or ShoppingService._is_generated(item):
            raise ShoppingListConflictError("Only unchecked manual items can be edited")
        item.estimated_cost = cost

    @staticmethod
    def _purchase_batch_request(
        item: ShoppingListItemModel,
        ingredient: MasterIngredientModel | None,
        quantity: float,
        purchase: ShoppingPurchaseDTO,
    ) -> CreateInventoryBatchRequestDTO:
        storage_mode = purchase.storage_mode
        if storage_mode is None and ingredient is not None:
            storage_mode = ingredient.default_storage_mode
        if storage_mode is None:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                detail="purchase.storage_mode is required when no catalog default exists",
            )
        return CreateInventoryBatchRequestDTO(
            master_ingredient_id=item.master_ingredient_id,
            custom_name=item.custom_name,
            quantity=quantity,
            unit=item.unit,
            storage_mode=storage_mode,
            **purchase.model_dump(exclude={"storage_mode"}),
        )

    @staticmethod
    def _to_summary_dto(
        shopping_list: ShoppingListModel,
    ) -> ShoppingListSummaryDTO:
        """Map only collection fields so list reads never load item rows."""
        return ShoppingListSummaryDTO(
            id=shopping_list.id,
            meal_plan_id=shopping_list.meal_plan_id,
            status=shopping_list.status,
            generated_at=shopping_list.generated_at,
            created_at=shopping_list.created_at,
            updated_at=shopping_list.updated_at,
        )

    @staticmethod
    def _to_item_dto(
        item: ShoppingListItemModel, ingredient_name: str | None
    ) -> ShoppingListItemDTO:
        metadata = item.source_metadata
        raw_recipe_ids = metadata.get("recipe_ids", [])
        source_recipe_ids = (
            [recipe_id for recipe_id in raw_recipe_ids if isinstance(recipe_id, str)]
            if isinstance(raw_recipe_ids, list)
            else []
        )
        raw_batch_id = metadata.get("inventory_batch_id")
        try:
            inventory_batch_id = (
                UUID(raw_batch_id) if isinstance(raw_batch_id, str) else None
            )
        except ValueError:
            inventory_batch_id = None
        return ShoppingListItemDTO(
            id=item.id,
            master_ingredient_id=item.master_ingredient_id,
            custom_name=item.custom_name,
            name=ingredient_name or item.custom_name or "Unknown ingredient",
            required_quantity=item.required_quantity,
            available_quantity=item.available_quantity,
            missing_quantity=item.missing_quantity,
            unit=item.unit,
            estimated_cost=item.estimated_cost,
            is_checked=item.is_checked,
            is_generated=ShoppingService._is_generated(item),
            source_recipe_ids=source_recipe_ids,
            inventory_batch_id=inventory_batch_id,
        )
