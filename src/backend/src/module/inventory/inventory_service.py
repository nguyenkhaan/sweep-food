"""Inventory calculations and database orchestration."""

from collections.abc import Sequence
from dataclasses import dataclass
from datetime import datetime, timedelta
from math import isfinite
from typing import Protocol
from uuid import UUID
from zoneinfo import ZoneInfo

from fastapi import HTTPException, status
from sqlalchemy import or_, select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.elements import ColumnElement
from sqlalchemy.sql.functions import count

from src.model.enum_model import (
    ExpirationSource,
    InventoryBatchStatus,
    InventoryBatchType,
    InventoryLedgerEventType,
    InventorySource,
    MeasurementUnit,
    StorageMode,
)
from src.model.inventory_batch_model import InventoryBatchModel
from src.model.inventory_ledger_entry_model import InventoryLedgerEntryModel
from src.model.master_ingredient_model import MasterIngredientModel
from src.model.shelf_life_rule_model import ShelfLifeRuleModel
from src.module.inventory.inventory_dto import (
    ConsumeInventoryBatchRequestDTO,
    CreateInventoryBatchRequestDTO,
    FreshnessState,
    InventoryAdjustmentRequestDTO,
    InventoryBatchDTO,
    InventoryBatchListResponseDTO,
    InventoryBatchQueryDTO,
    InventoryBatchSummaryDTO,
    InventoryLedgerEntryDTO,
    InventoryLedgerListResponseDTO,
    InventoryLedgerQueryDTO,
    InventorySummaryResponseDTO,
    MoveInventoryBatchRequestDTO,
    UpdateInventoryBatchRequestDTO,
)
from src.service.fefo_service import are_units_compatible, convert_quantity

_QUANTITY_EPSILON = 1e-9
_PRODUCT_TIMEZONE = ZoneInfo("Asia/Ho_Chi_Minh")


class RecordAdder(Protocol):
    """Smallest persistence surface needed by quantity mutation logic."""

    def add(self, instance: object) -> None:
        """Stage one ORM instance for persistence."""


class InventoryConflictError(HTTPException):
    """Reject an inventory mutation that conflicts with current stock."""

    def __init__(self, detail: str = "Inventory quantity conflict") -> None:
        super().__init__(status_code=status.HTTP_409_CONFLICT, detail=detail)


class InventoryBatchNotFoundError(HTTPException):
    """Hide whether an unknown batch belongs to another user."""

    def __init__(self) -> None:
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Inventory batch was not found",
        )


class InventoryIngredientNotFoundError(HTTPException):
    """Reject a catalog identity that does not exist."""

    def __init__(self) -> None:
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ingredient was not found",
        )


@dataclass(frozen=True, slots=True)
class InventoryQuantityChange:
    """One validated quantity mutation shared by inventory and cooking."""

    user_id: UUID
    quantity_delta: float
    event_type: InventoryLedgerEventType
    idempotency_key: str | None
    reason: str | None
    cooking_session_id: UUID | None = None


def apply_quantity_change(
    db_session: RecordAdder,
    batch: InventoryBatchModel,
    change: InventoryQuantityChange,
) -> InventoryLedgerEntryModel:
    """Mutate one locked balance and stage its arithmetically matching ledger."""
    if batch.user_id != change.user_id:
        raise InventoryConflictError()
    if batch.status in {
        InventoryBatchStatus.ARCHIVED,
        InventoryBatchStatus.DISCARDED,
    }:
        raise InventoryConflictError("Inactive inventory batch cannot be adjusted")
    if (
        not isfinite(change.quantity_delta)
        or abs(change.quantity_delta) <= _QUANTITY_EPSILON
    ):
        raise InventoryConflictError("Quantity change must be finite and non-zero")

    quantity_before = batch.current_quantity
    quantity_after = quantity_before + change.quantity_delta
    if quantity_after < -_QUANTITY_EPSILON:
        raise InventoryConflictError("Inventory quantity cannot become negative")

    batch.current_quantity = max(0.0, quantity_after)
    if change.event_type is InventoryLedgerEventType.DISCARDED:
        if batch.current_quantity > _QUANTITY_EPSILON:
            raise InventoryConflictError("Discard must consume the full batch")
        batch.status = InventoryBatchStatus.DISCARDED
    elif batch.current_quantity <= _QUANTITY_EPSILON:
        batch.status = InventoryBatchStatus.DEPLETED
    else:
        batch.status = InventoryBatchStatus.ACTIVE

    ledger = InventoryLedgerEntryModel(
        user_id=change.user_id,
        inventory_batch_id=batch.id,
        event_type=change.event_type,
        quantity_before=quantity_before,
        quantity_delta=change.quantity_delta,
        quantity_after=batch.current_quantity,
        unit=batch.unit,
        cooking_session_id=change.cooking_session_id,
        idempotency_key=change.idempotency_key,
        reason=change.reason,
    )
    db_session.add(ledger)
    return ledger


class InventoryService:
    """Orchestrate ownership-safe inventory queries and atomic mutations."""

    def __init__(self, db_session: AsyncSession, warning_days: int = 3) -> None:
        self.db_session = db_session
        self.warning_days = warning_days

    async def create_batch(
        self,
        user_id: UUID,
        body: CreateInventoryBatchRequestDTO,
        idempotency_key: str,
    ) -> InventoryBatchDTO:
        """Create one manual batch with an INITIAL_STOCK ledger entry."""
        try:
            batch = await self.stage_batch(
                user_id,
                body,
                idempotency_key,
                reason="Manual batch creation",
            )
            await self.db_session.commit()
            return await self._to_batch_dto(batch)
        except IntegrityError as error:
            await self.db_session.rollback()
            existing = await self._find_idempotent_batch(
                user_id,
                idempotency_key,
                InventoryLedgerEventType.INITIAL_STOCK,
            )
            if existing is not None:
                return await self._to_batch_dto(existing)
            raise InventoryConflictError(
                "Inventory batch creation conflicted"
            ) from error
        except (HTTPException, SQLAlchemyError):
            await self.db_session.rollback()
            raise

    async def stage_batch(
        self,
        user_id: UUID,
        body: CreateInventoryBatchRequestDTO,
        idempotency_key: str,
        *,
        reason: str,
    ) -> InventoryBatchModel:
        """Stage initial stock without committing a caller-owned transaction."""
        existing = await self._find_idempotent_batch(
            user_id,
            idempotency_key,
            InventoryLedgerEventType.INITIAL_STOCK,
        )
        if existing is not None:
            return existing

        ingredient = await self._find_ingredient(body.master_ingredient_id)
        rules = await self._find_shelf_life_rules(ingredient, body.storage_mode)
        rule = (
            choose_shelf_life_rule(rules, master_ingredient_id=ingredient.id)
            if ingredient is not None
            else None
        )
        now = datetime.now(_PRODUCT_TIMEZONE)
        expires_at, expiration_source = resolve_expiration(
            manufacturer_expires_at=body.expires_at,
            stored_at=body.stored_at,
            purchased_at=body.purchased_at,
            shelf_life_days=rule.default_days if rule is not None else None,
            now=now,
        )
        batch = InventoryBatchModel(
            user_id=user_id,
            master_ingredient_id=body.master_ingredient_id,
            custom_name=body.custom_name,
            batch_type=InventoryBatchType.RAW_INGREDIENT,
            initial_quantity=body.quantity,
            current_quantity=body.quantity,
            unit=body.unit,
            storage_mode=body.storage_mode,
            status=InventoryBatchStatus.ACTIVE,
            purchased_at=body.purchased_at,
            packaged_at=body.packaged_at,
            stored_at=body.stored_at,
            expires_at=expires_at,
            expiration_source=expiration_source,
            unit_cost=body.unit_cost,
            note=body.note,
            media_url=body.media_url,
            source=InventorySource.MANUAL,
        )
        self.db_session.add(batch)
        await self.db_session.flush()
        self.db_session.add(
            InventoryLedgerEntryModel(
                user_id=user_id,
                inventory_batch_id=batch.id,
                event_type=InventoryLedgerEventType.INITIAL_STOCK,
                quantity_before=0.0,
                quantity_delta=body.quantity,
                quantity_after=body.quantity,
                unit=body.unit,
                idempotency_key=idempotency_key,
                reason=reason,
            )
        )
        return batch

    async def list_batches(
        self,
        user_id: UUID,
        query: InventoryBatchQueryDTO,
    ) -> InventoryBatchListResponseDTO:
        """List owned batches with filters and deterministic ordering."""
        filters = self._batch_filters(
            user_id,
            query.batch_status,
            query.storage_mode,
            query.master_ingredient_id,
        )
        try:
            total = int(
                (
                    await self.db_session.execute(
                        select(count()).select_from(InventoryBatchModel).where(*filters)
                    )
                ).scalar_one()
            )
            result = await self.db_session.execute(
                select(InventoryBatchModel)
                .where(*filters)
                .order_by(
                    InventoryBatchModel.created_at.desc(),
                    InventoryBatchModel.id.desc(),
                )
                .offset((query.page - 1) * query.per_page)
                .limit(query.per_page)
            )
            batches = list(result.scalars().all())
            names = await self._ingredient_names(batches)
            return InventoryBatchListResponseDTO(
                items=[
                    self._map_batch(
                        batch,
                        names.get(batch.master_ingredient_id)
                        if batch.master_ingredient_id is not None
                        else None,
                    )
                    for batch in batches
                ],
                total=total,
                page=query.page,
                per_page=query.per_page,
            )
        except SQLAlchemyError:
            await self.db_session.rollback()
            raise

    async def get_batch(self, user_id: UUID, batch_id: UUID) -> InventoryBatchDTO:
        """Read one batch through an ownership-constrained query."""
        try:
            batch = await self._find_batch(user_id, batch_id, lock=False)
            return await self._to_batch_dto(batch)
        except (HTTPException, SQLAlchemyError):
            await self.db_session.rollback()
            raise

    async def update_batch(
        self,
        user_id: UUID,
        batch_id: UUID,
        body: UpdateInventoryBatchRequestDTO,
        idempotency_key: str,
    ) -> InventoryBatchDTO:
        """Update metadata once and append one zero-delta audit."""
        try:
            existing = await self._find_idempotent_batch(
                user_id,
                idempotency_key,
                InventoryLedgerEventType.METADATA_UPDATED,
                batch_id=batch_id,
            )
            if existing is not None:
                return await self._to_batch_dto(existing)
            batch = await self._find_batch(user_id, batch_id, lock=True)
            expiration_was_submitted = "expires_at" in body.model_fields_set
            if (
                expiration_was_submitted
                and body.expires_at is None
                and batch.expiration_source is ExpirationSource.MANUFACTURER
            ):
                raise InventoryConflictError(
                    "Manufacturer expiration cannot be cleared"
                )
            values = body.model_dump(
                exclude_unset=True,
                exclude={"expires_at", "reason"},
            )
            for field_name, value in values.items():
                setattr(batch, field_name, value)

            date_anchor_changed = bool(
                {"stored_at", "purchased_at"} & body.model_fields_set
            )
            if expiration_was_submitted and body.expires_at is not None:
                batch.expires_at = body.expires_at
                batch.expiration_source = ExpirationSource.USER_OVERRIDE
            elif expiration_was_submitted or (
                date_anchor_changed
                and batch.expiration_source is ExpirationSource.ESTIMATED
            ):
                await self._recalculate_estimated_expiration(batch)
            self._add_zero_delta_audit(
                batch,
                user_id,
                InventoryLedgerEventType.METADATA_UPDATED,
                idempotency_key,
                body.reason,
            )
            await self.db_session.commit()
            return await self._to_batch_dto(batch)
        except IntegrityError as error:
            await self.db_session.rollback()
            existing = await self._find_idempotent_batch(
                user_id,
                idempotency_key,
                InventoryLedgerEventType.METADATA_UPDATED,
                batch_id=batch_id,
            )
            if existing is not None:
                return await self._to_batch_dto(existing)
            raise InventoryConflictError("Inventory update conflicted") from error
        except (HTTPException, SQLAlchemyError):
            await self.db_session.rollback()
            raise

    async def archive_batch(
        self,
        user_id: UUID,
        batch_id: UUID,
        idempotency_key: str,
        reason: str,
    ) -> None:
        """Archive one owned batch once and retain an explicit audit."""
        try:
            existing = await self._find_idempotent_batch(
                user_id,
                idempotency_key,
                InventoryLedgerEventType.ARCHIVED,
                batch_id=batch_id,
            )
            if existing is not None:
                return
            batch = await self._find_batch(user_id, batch_id, lock=True)
            if batch.status is not InventoryBatchStatus.ARCHIVED:
                batch.status = InventoryBatchStatus.ARCHIVED
                batch.archived_at = datetime.now(_PRODUCT_TIMEZONE)
                self._add_zero_delta_audit(
                    batch,
                    user_id,
                    InventoryLedgerEventType.ARCHIVED,
                    idempotency_key,
                    reason,
                )
                await self.db_session.commit()
        except IntegrityError as error:
            await self.db_session.rollback()
            existing = await self._find_idempotent_batch(
                user_id,
                idempotency_key,
                InventoryLedgerEventType.ARCHIVED,
                batch_id=batch_id,
            )
            if existing is not None:
                return
            raise InventoryConflictError("Inventory archive conflicted") from error
        except (HTTPException, SQLAlchemyError):
            await self.db_session.rollback()
            raise

    async def adjust_batch(
        self,
        user_id: UUID,
        batch_id: UUID,
        body: InventoryAdjustmentRequestDTO,
        idempotency_key: str,
    ) -> InventoryBatchDTO:
        """Lock and mutate one batch exactly once for an idempotency key."""
        quantity_delta = body.quantity_delta
        if body.event_type is InventoryLedgerEventType.DISCARDED:
            quantity_delta = None
        return await self._change_quantity(
            user_id,
            batch_id,
            body.event_type,
            quantity_delta,
            body.reason,
            idempotency_key,
        )

    async def consume_batch(
        self,
        user_id: UUID,
        batch_id: UUID,
        body: ConsumeInventoryBatchRequestDTO,
        idempotency_key: str,
    ) -> InventoryBatchDTO:
        """Consume a positive batch-unit quantity exactly once."""
        return await self._change_quantity(
            user_id,
            batch_id,
            InventoryLedgerEventType.MANUAL_CONSUMPTION,
            -body.quantity,
            body.reason,
            idempotency_key,
        )

    # Each argument is retained in the immutable ledger record for this mutation.
    # pylint: disable-next=too-many-arguments,too-many-positional-arguments
    async def _change_quantity(
        self,
        user_id: UUID,
        batch_id: UUID,
        event_type: InventoryLedgerEventType,
        quantity_delta: float | None,
        reason: str,
        idempotency_key: str,
    ) -> InventoryBatchDTO:
        """Apply one locked, idempotent quantity mutation."""
        try:
            existing = await self._find_idempotent_batch(
                user_id,
                idempotency_key,
                event_type,
                batch_id=batch_id,
            )
            if existing is not None:
                return await self._to_batch_dto(existing)
            batch = await self._find_batch(user_id, batch_id, lock=True)
            if event_type is InventoryLedgerEventType.DISCARDED:
                quantity_delta = -batch.current_quantity
            if quantity_delta is None:
                raise InventoryConflictError("Quantity change is required")
            apply_quantity_change(
                self.db_session,
                batch,
                InventoryQuantityChange(
                    user_id=user_id,
                    quantity_delta=quantity_delta,
                    event_type=event_type,
                    idempotency_key=idempotency_key,
                    reason=reason,
                ),
            )
            await self.db_session.commit()
            await self.db_session.refresh(batch)
            return await self._to_batch_dto(batch)
        except IntegrityError as error:
            await self.db_session.rollback()
            existing = await self._find_idempotent_batch(
                user_id,
                idempotency_key,
                event_type,
                batch_id=batch_id,
            )
            if existing is not None:
                return await self._to_batch_dto(existing)
            raise InventoryConflictError("Inventory adjustment conflicted") from error
        except (HTTPException, SQLAlchemyError):
            await self.db_session.rollback()
            raise

    async def move_batch(
        self,
        user_id: UUID,
        batch_id: UUID,
        body: MoveInventoryBatchRequestDTO,
        idempotency_key: str,
    ) -> InventoryBatchDTO:
        """Move a batch once and refresh only non-authoritative estimates."""
        try:
            existing = await self._find_idempotent_batch(
                user_id,
                idempotency_key,
                InventoryLedgerEventType.MOVED,
                batch_id=batch_id,
            )
            if existing is not None:
                return await self._to_batch_dto(existing)
            batch = await self._find_batch(user_id, batch_id, lock=True)
            previous_storage_mode = batch.storage_mode
            if previous_storage_mode is body.storage_mode:
                return await self._to_batch_dto(batch)
            batch.storage_mode = body.storage_mode
            if batch.expiration_source in {
                ExpirationSource.ESTIMATED,
                ExpirationSource.UNKNOWN,
            }:
                await self._recalculate_estimated_expiration(batch)
            self._add_zero_delta_audit(
                batch,
                user_id,
                InventoryLedgerEventType.MOVED,
                idempotency_key,
                f"{body.reason}; {previous_storage_mode.value} -> {body.storage_mode.value}",
            )
            await self.db_session.commit()
            return await self._to_batch_dto(batch)
        except IntegrityError as error:
            await self.db_session.rollback()
            existing = await self._find_idempotent_batch(
                user_id,
                idempotency_key,
                InventoryLedgerEventType.MOVED,
                batch_id=batch_id,
            )
            if existing is not None:
                return await self._to_batch_dto(existing)
            raise InventoryConflictError("Inventory move conflicted") from error
        except (HTTPException, SQLAlchemyError):
            await self.db_session.rollback()
            raise

    async def get_summary(self, user_id: UUID) -> InventorySummaryResponseDTO:
        """Aggregate compatible active quantities while preserving status counts."""
        try:
            result = await self.db_session.execute(
                select(InventoryBatchModel).where(
                    InventoryBatchModel.user_id == user_id,
                    InventoryBatchModel.status == InventoryBatchStatus.ACTIVE,
                    InventoryBatchModel.current_quantity > 0,
                )
            )
            batches = list(result.scalars().all())
            ingredients = await self._ingredients_by_id(batches)
            return InventorySummaryResponseDTO(
                items=self._summarize_batches(
                    batches,
                    ingredients,
                    warning_days=self.warning_days,
                )
            )
        except SQLAlchemyError:
            await self.db_session.rollback()
            raise

    async def list_ledger(
        self,
        user_id: UUID,
        query: InventoryLedgerQueryDTO,
    ) -> InventoryLedgerListResponseDTO:
        """Return immutable history for the authenticated owner only."""
        filters: list[ColumnElement[bool]] = [
            InventoryLedgerEntryModel.user_id == user_id
        ]
        if query.batch_id is not None:
            filters.append(
                InventoryLedgerEntryModel.inventory_batch_id == query.batch_id
            )
        if query.event_type is not None:
            filters.append(InventoryLedgerEntryModel.event_type == query.event_type)
        if query.created_from is not None:
            filters.append(InventoryLedgerEntryModel.created_at >= query.created_from)
        if query.created_to is not None:
            filters.append(InventoryLedgerEntryModel.created_at <= query.created_to)
        try:
            total = int(
                (
                    await self.db_session.execute(
                        select(count())
                        .select_from(InventoryLedgerEntryModel)
                        .where(*filters)
                    )
                ).scalar_one()
            )
            result = await self.db_session.execute(
                select(InventoryLedgerEntryModel)
                .where(*filters)
                .order_by(
                    InventoryLedgerEntryModel.created_at.desc(),
                    InventoryLedgerEntryModel.id.desc(),
                )
                .offset((query.page - 1) * query.per_page)
                .limit(query.per_page)
            )
            entries = list(result.scalars().all())
            return InventoryLedgerListResponseDTO(
                items=[self._map_ledger(entry) for entry in entries],
                total=total,
                page=query.page,
                per_page=query.per_page,
            )
        except SQLAlchemyError:
            await self.db_session.rollback()
            raise

    async def _find_ingredient(
        self,
        ingredient_id: UUID | None,
    ) -> MasterIngredientModel | None:
        if ingredient_id is None:
            return None
        result = await self.db_session.execute(
            select(MasterIngredientModel).where(
                MasterIngredientModel.id == ingredient_id
            )
        )
        ingredient = result.scalar_one_or_none()
        if ingredient is None:
            raise InventoryIngredientNotFoundError()
        return ingredient

    async def _find_shelf_life_rules(
        self,
        ingredient: MasterIngredientModel | None,
        storage_mode: StorageMode,
    ) -> list[ShelfLifeRuleModel]:
        if ingredient is None:
            return []
        result = await self.db_session.execute(
            select(ShelfLifeRuleModel).where(
                ShelfLifeRuleModel.storage_mode == storage_mode,
                or_(
                    ShelfLifeRuleModel.master_ingredient_id == ingredient.id,
                    ShelfLifeRuleModel.category_id == ingredient.category_id,
                ),
            )
        )
        return list(result.scalars().all())

    async def _find_batch(
        self,
        user_id: UUID,
        batch_id: UUID,
        *,
        lock: bool,
    ) -> InventoryBatchModel:
        statement = select(InventoryBatchModel).where(
            InventoryBatchModel.id == batch_id,
            InventoryBatchModel.user_id == user_id,
        )
        if lock:
            statement = statement.with_for_update()
        result = await self.db_session.execute(statement)
        batch = result.scalar_one_or_none()
        if batch is None:
            raise InventoryBatchNotFoundError()
        return batch

    async def _find_idempotent_batch(
        self,
        user_id: UUID,
        idempotency_key: str,
        event_type: InventoryLedgerEventType,
        *,
        batch_id: UUID | None = None,
    ) -> InventoryBatchModel | None:
        statement = (
            select(InventoryBatchModel)
            .join(
                InventoryLedgerEntryModel,
                InventoryLedgerEntryModel.inventory_batch_id == InventoryBatchModel.id,
            )
            .where(
                InventoryLedgerEntryModel.user_id == user_id,
                InventoryLedgerEntryModel.idempotency_key == idempotency_key,
                InventoryLedgerEntryModel.event_type == event_type,
            )
        )
        if batch_id is not None:
            statement = statement.where(InventoryBatchModel.id == batch_id)
        result = await self.db_session.execute(statement)
        return result.scalar_one_or_none()

    async def _recalculate_estimated_expiration(
        self,
        batch: InventoryBatchModel,
    ) -> None:
        ingredient = await self._find_ingredient(batch.master_ingredient_id)
        rules = await self._find_shelf_life_rules(ingredient, batch.storage_mode)
        rule = (
            choose_shelf_life_rule(rules, master_ingredient_id=ingredient.id)
            if ingredient is not None
            else None
        )
        batch.expires_at, batch.expiration_source = resolve_expiration(
            manufacturer_expires_at=None,
            stored_at=batch.stored_at,
            purchased_at=batch.purchased_at,
            shelf_life_days=rule.default_days if rule is not None else None,
            now=datetime.now(_PRODUCT_TIMEZONE),
        )

    def _add_zero_delta_audit(
        self,
        batch: InventoryBatchModel,
        user_id: UUID,
        event_type: InventoryLedgerEventType,
        idempotency_key: str,
        reason: str,
    ) -> None:
        self.db_session.add(
            InventoryLedgerEntryModel(
                user_id=user_id,
                inventory_batch_id=batch.id,
                event_type=event_type,
                quantity_before=batch.current_quantity,
                quantity_delta=0.0,
                quantity_after=batch.current_quantity,
                unit=batch.unit,
                idempotency_key=idempotency_key,
                reason=reason,
            )
        )

    async def _to_batch_dto(self, batch: InventoryBatchModel) -> InventoryBatchDTO:
        ingredient_name: str | None = None
        if batch.master_ingredient_id is not None:
            ingredient = await self._find_ingredient(batch.master_ingredient_id)
            if ingredient is not None:
                ingredient_name = ingredient.name
        return self._map_batch(batch, ingredient_name)

    def _map_batch(
        self,
        batch: InventoryBatchModel,
        ingredient_name: str | None,
    ) -> InventoryBatchDTO:
        return InventoryBatchDTO(
            id=batch.id,
            master_ingredient_id=batch.master_ingredient_id,
            custom_name=batch.custom_name,
            ingredient_name=ingredient_name
            or batch.custom_name
            or "Unknown ingredient",
            batch_type=batch.batch_type,
            initial_quantity=batch.initial_quantity,
            current_quantity=batch.current_quantity,
            unit=batch.unit,
            storage_mode=batch.storage_mode,
            status=batch.status,
            purchased_at=batch.purchased_at,
            packaged_at=batch.packaged_at,
            stored_at=batch.stored_at,
            expires_at=batch.expires_at,
            expiration_source=batch.expiration_source,
            freshness=calculate_freshness(
                batch.expires_at,
                datetime.now(_PRODUCT_TIMEZONE),
                warning_days=self.warning_days,
            ),
            unit_cost=batch.unit_cost,
            note=batch.note,
            media_url=batch.media_url,
            source=batch.source,
            source_cooking_session_id=batch.source_cooking_session_id,
            created_at=batch.created_at,
            updated_at=batch.updated_at,
            archived_at=batch.archived_at,
        )

    async def _ingredient_names(
        self,
        batches: Sequence[InventoryBatchModel],
    ) -> dict[UUID, str]:
        ingredients = await self._ingredients_by_id(batches)
        return {ingredient_id: item.name for ingredient_id, item in ingredients.items()}

    async def _ingredients_by_id(
        self,
        batches: Sequence[InventoryBatchModel],
    ) -> dict[UUID, MasterIngredientModel]:
        ingredient_ids = {
            batch.master_ingredient_id
            for batch in batches
            if batch.master_ingredient_id is not None
        }
        if not ingredient_ids:
            return {}
        result = await self.db_session.execute(
            select(MasterIngredientModel).where(
                MasterIngredientModel.id.in_(ingredient_ids)
            )
        )
        return {ingredient.id: ingredient for ingredient in result.scalars().all()}

    @staticmethod
    def _batch_filters(
        user_id: UUID,
        batch_status: InventoryBatchStatus | None,
        storage_mode: StorageMode | None,
        master_ingredient_id: UUID | None,
    ) -> list[ColumnElement[bool]]:
        filters: list[ColumnElement[bool]] = [InventoryBatchModel.user_id == user_id]
        if batch_status is not None:
            filters.append(InventoryBatchModel.status == batch_status)
        if storage_mode is not None:
            filters.append(InventoryBatchModel.storage_mode == storage_mode)
        if master_ingredient_id is not None:
            filters.append(
                InventoryBatchModel.master_ingredient_id == master_ingredient_id
            )
        return filters

    @staticmethod
    def _summarize_batches(
        batches: Sequence[InventoryBatchModel],
        ingredients: dict[UUID, MasterIngredientModel],
        *,
        warning_days: int,
    ) -> list[InventoryBatchSummaryDTO]:
        grouped: dict[tuple[str, MeasurementUnit], InventoryBatchSummaryDTO] = {}
        now = datetime.now(_PRODUCT_TIMEZONE)
        for batch in batches:
            ingredient = (
                ingredients.get(batch.master_ingredient_id)
                if batch.master_ingredient_id is not None
                else None
            )
            target_unit = InventoryService._summary_unit(batch, ingredient)
            identity = (
                str(batch.master_ingredient_id)
                if batch.master_ingredient_id is not None
                else (batch.custom_name or "").casefold()
            )
            key = (identity, target_unit)
            freshness = calculate_freshness(
                batch.expires_at,
                now,
                warning_days=warning_days,
            )
            quantity = convert_quantity(
                batch.current_quantity,
                batch.unit,
                target_unit,
            )
            current = grouped.get(key)
            if current is None:
                grouped[key] = InventoryBatchSummaryDTO(
                    master_ingredient_id=batch.master_ingredient_id,
                    custom_name=batch.custom_name,
                    ingredient_name=(
                        ingredient.name
                        if ingredient is not None
                        else batch.custom_name or "Unknown ingredient"
                    ),
                    quantity=quantity,
                    unit=target_unit,
                    batch_count=1,
                    expiring_soon_count=int(freshness is FreshnessState.EXPIRING_SOON),
                    expired_count=int(freshness is FreshnessState.EXPIRED),
                )
            else:
                current.quantity += quantity
                current.batch_count += 1
                current.expiring_soon_count += int(
                    freshness is FreshnessState.EXPIRING_SOON
                )
                current.expired_count += int(freshness is FreshnessState.EXPIRED)
        return sorted(
            grouped.values(),
            key=lambda item: (item.ingredient_name.casefold(), item.unit.value),
        )

    @staticmethod
    def _summary_unit(
        batch: InventoryBatchModel,
        ingredient: MasterIngredientModel | None,
    ) -> MeasurementUnit:
        if ingredient is not None and are_units_compatible(
            batch.unit, ingredient.canonical_unit
        ):
            return ingredient.canonical_unit
        if are_units_compatible(batch.unit, MeasurementUnit.GRAM):
            return MeasurementUnit.GRAM
        if are_units_compatible(batch.unit, MeasurementUnit.ML):
            return MeasurementUnit.ML
        return batch.unit

    @staticmethod
    def _map_ledger(entry: InventoryLedgerEntryModel) -> InventoryLedgerEntryDTO:
        return InventoryLedgerEntryDTO(
            id=entry.id,
            inventory_batch_id=entry.inventory_batch_id,
            event_type=entry.event_type,
            quantity_before=entry.quantity_before,
            quantity_delta=entry.quantity_delta,
            quantity_after=entry.quantity_after,
            unit=entry.unit,
            cooking_session_id=entry.cooking_session_id,
            idempotency_key=entry.idempotency_key,
            reason=entry.reason,
            created_at=entry.created_at,
        )


def resolve_expiration(
    *,
    manufacturer_expires_at: datetime | None,
    stored_at: datetime | None,
    purchased_at: datetime | None,
    shelf_life_days: int | None,
    now: datetime,
) -> tuple[datetime | None, ExpirationSource]:
    """Apply manufacturer precedence and seeded-rule estimation."""
    if manufacturer_expires_at is not None:
        return manufacturer_expires_at, ExpirationSource.MANUFACTURER
    if shelf_life_days is None:
        return None, ExpirationSource.UNKNOWN
    base_at = stored_at or purchased_at or now
    return base_at + timedelta(days=shelf_life_days), ExpirationSource.ESTIMATED


def calculate_freshness(
    expires_at: datetime | None,
    now: datetime,
    *,
    warning_days: int,
) -> FreshnessState:
    """Classify one expiration instant using an inclusive warning window."""
    if expires_at is None:
        return FreshnessState.UNKNOWN
    if expires_at < now:
        return FreshnessState.EXPIRED
    if expires_at <= now + timedelta(days=warning_days):
        return FreshnessState.EXPIRING_SOON
    return FreshnessState.SAFE


def choose_shelf_life_rule(
    rules: Sequence[ShelfLifeRuleModel],
    *,
    master_ingredient_id: UUID,
) -> ShelfLifeRuleModel | None:
    """Prefer an ingredient-specific rule over its category fallback."""
    ingredient_rule = next(
        (rule for rule in rules if rule.master_ingredient_id == master_ingredient_id),
        None,
    )
    return ingredient_rule or next(iter(rules), None)
