"""Manual inventory batch application service."""

from collections.abc import Iterable
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from decimal import Decimal
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import Select, or_, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
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
from src.model.user_notification_preference_model import UserNotificationPreferenceModel
from src.module.inventory.inventory_dto import (
    AppliedShelfLifeRuleDTO,
    CreateInventoryBatchRequestDTO,
    IngredientIdentityDTO,
    InventoryBatchDTO,
    InventoryBatchListQueryDTO,
    InventoryBatchListResponseDTO,
    InventoryLedgerEntryDTO,
    InventoryQuantityCommand,
    InventoryQuantityCommandRequestDTO,
    InventoryQuantityCommandResponseDTO,
    InventorySummaryItemDTO,
    InventorySummaryResponseDTO,
    UpdateInventoryBatchRequestDTO,
)
from src.service.shelf_life_service import (
    ExistingExpiration,
    ExpirationResolution,
    FreshnessState,
    ShelfLifeEstimationContext,
    ShelfLifeRule,
    calculate_freshness,
    resolve_expiration,
)
from src.service.unit_conversion_service import (
    UnitGroup,
    are_units_compatible,
    convert_quantity,
    unit_group,
)

_DEFAULT_WARNING_DAYS = 3


@dataclass(frozen=True, slots=True)
class _ExpirationInputs:
    """The full authoritative and fallback context for an expiration decision."""

    ingredient: MasterIngredientModel | None
    storage_mode: StorageMode
    purchased_at: datetime | None
    stored_at: datetime | None
    manufacturer_expires_at: datetime | None
    override_expires_at: datetime | None


@dataclass(frozen=True, slots=True)
class _ResolvedBatchUpdate:
    """A validated metadata patch ready to apply to one loaded batch."""

    ingredient: MasterIngredientModel | None
    custom_name: str | None
    unit: MeasurementUnit
    storage_mode: StorageMode
    purchased_at: datetime | None
    stored_at: datetime | None
    expiration_inputs: _ExpirationInputs


class InventoryBatchNotFoundError(HTTPException):
    """Non-disclosing not-found response for unknown or unowned batches."""

    def __init__(self) -> None:
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Inventory batch was not found",
        )


class InventoryIngredientNotFoundError(HTTPException):
    """Reject unknown master identities supplied to a manual batch."""

    def __init__(self) -> None:
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="Master ingredient was not found",
        )


class InventoryUnitMismatchError(HTTPException):
    """Reject incompatible units before an inventory batch is persisted."""

    def __init__(self) -> None:
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="Unit is incompatible with the master ingredient",
        )


class InventoryQuantityConflictError(HTTPException):
    """Reject a command that cannot be applied to the current batch balance."""

    def __init__(self, detail: str) -> None:
        super().__init__(status_code=status.HTTP_409_CONFLICT, detail=detail)


class InventoryService:
    """Create, read, edit, and archive only user-owned manual raw batches."""

    def __init__(self, db_session: AsyncSession) -> None:
        self.db_session = db_session

    async def create_batch(
        self,
        user_id: UUID,
        request: CreateInventoryBatchRequestDTO,
    ) -> InventoryBatchDTO:
        """Create a batch and its immutable initial-stock ledger entry together."""
        ingredient = await self._get_master_ingredient(request.master_ingredient_id)
        self._validate_unit(ingredient, request.unit)
        expiration, rules = await self._resolve_expiration(
            _ExpirationInputs(
                ingredient=ingredient,
                storage_mode=request.storage_mode,
                purchased_at=request.purchased_at,
                stored_at=request.stored_at,
                manufacturer_expires_at=request.manufacturer_expires_at,
                override_expires_at=request.expiration_override_at,
            ),
        )
        batch = InventoryBatchModel(
            user_id=user_id,
            master_ingredient_id=ingredient.id if ingredient is not None else None,
            custom_name=request.custom_name,
            batch_type=InventoryBatchType.RAW_INGREDIENT,
            initial_quantity=request.quantity,
            current_quantity=request.quantity,
            unit=request.unit,
            storage_mode=request.storage_mode,
            status=InventoryBatchStatus.ACTIVE,
            purchased_at=request.purchased_at,
            packaged_at=request.packaged_at,
            stored_at=request.stored_at,
            expires_at=expiration.expires_at,
            expiration_source=expiration.source,
            unit_cost=request.unit_cost,
            note=request.note,
            media_url=request.media_url,
            source=InventorySource.MANUAL,
        )
        batch.master_ingredient = ingredient
        try:
            self.db_session.add(batch)
            await self.db_session.flush()
            self.db_session.add(
                InventoryLedgerEntryModel(
                    user_id=user_id,
                    inventory_batch_id=batch.id,
                    event_type=InventoryLedgerEventType.INITIAL_STOCK,
                    quantity_before=0.0,
                    quantity_delta=request.quantity,
                    quantity_after=request.quantity,
                    unit=request.unit,
                )
            )
            await self.db_session.commit()
        except SQLAlchemyError:
            await self.db_session.rollback()
            raise
        return await self._to_dto(batch, rules=rules)

    async def list_batches(
        self,
        user_id: UUID,
        filters: InventoryBatchListQueryDTO,
    ) -> InventoryBatchListResponseDTO:
        """List filtered batches with deterministic pagination and computed freshness."""
        warning_days = await self._warning_days(user_id)
        clauses = self._list_filters(user_id, filters, warning_days)
        statement = self._batch_statement().where(*clauses)
        count_statement = (
            select(count()).select_from(InventoryBatchModel).where(*clauses)
        )
        total = int((await self.db_session.execute(count_statement)).scalar_one())
        batches = list(
            (
                await self.db_session.execute(
                    statement.order_by(
                        InventoryBatchModel.created_at.desc(),
                        InventoryBatchModel.id.desc(),
                    )
                    .offset((filters.page - 1) * filters.per_page)
                    .limit(filters.per_page),
                )
            )
            .scalars()
            .all()
        )
        rules = await self._get_rules_for_batches(batches)
        items = [
            await self._to_dto(
                batch,
                rules=rules,
                warning_days=warning_days,
            )
            for batch in batches
        ]
        return InventoryBatchListResponseDTO(
            items=items,
            total=total,
            page=filters.page,
            per_page=filters.per_page,
        )

    async def get_batch(self, user_id: UUID, batch_id: UUID) -> InventoryBatchDTO:
        """Return one owned batch with fresh calculated expiration metadata."""
        batch = await self._get_owned_batch(user_id, batch_id)
        return await self._to_dto(batch)

    async def update_batch(
        self,
        user_id: UUID,
        batch_id: UUID,
        request: UpdateInventoryBatchRequestDTO,
    ) -> InventoryBatchDTO:
        """Apply a metadata-only patch while respecting expiration authority."""
        batch = await self._get_owned_batch(user_id, batch_id)
        if batch.source is not InventorySource.MANUAL:
            raise InventoryBatchNotFoundError()
        update = await self._prepare_update(batch, request)
        expiration, rules = await self._resolve_expiration(update.expiration_inputs)
        self._apply_update(batch, request, update, expiration)
        try:
            await self.db_session.commit()
        except SQLAlchemyError:
            await self.db_session.rollback()
            raise
        await self.db_session.refresh(batch, attribute_names=["updated_at"])
        return await self._to_dto(batch, rules=rules)

    async def archive_batch(self, user_id: UUID, batch_id: UUID) -> None:
        """Soft-archive an owned batch without changing its inventory balance."""
        batch = await self._get_owned_batch(user_id, batch_id)
        if batch.source is not InventorySource.MANUAL:
            raise InventoryBatchNotFoundError()
        if batch.status is not InventoryBatchStatus.ARCHIVED:
            batch.status = InventoryBatchStatus.ARCHIVED
            batch.archived_at = datetime.now(UTC)
            try:
                await self.db_session.commit()
            except SQLAlchemyError:
                await self.db_session.rollback()
                raise

    async def get_summary(self, user_id: UUID) -> InventorySummaryResponseDTO:
        """Aggregate only active owned batches while preserving each batch response."""
        warning_days = await self._warning_days(user_id)
        batches = list(
            (
                await self.db_session.execute(
                    self._batch_statement()
                    .where(
                        InventoryBatchModel.user_id == user_id,
                        InventoryBatchModel.status == InventoryBatchStatus.ACTIVE,
                    )
                    .order_by(
                        InventoryBatchModel.created_at.desc(),
                        InventoryBatchModel.id.desc(),
                    ),
                )
            )
            .scalars()
            .all()
        )
        rules = await self._get_rules_for_batches(batches)
        groups: dict[tuple[str, str], list[InventoryBatchModel]] = {}
        for batch in batches:
            groups.setdefault(self._summary_key(batch), []).append(batch)
        items = [
            await self._summary_item(batches_for_group, rules, warning_days)
            for batches_for_group in groups.values()
        ]
        return InventorySummaryResponseDTO(items=items, total_batches=len(batches))

    async def apply_quantity_command(
        self,
        user_id: UUID,
        batch_id: UUID,
        idempotency_key: str,
        request: InventoryQuantityCommandRequestDTO,
    ) -> InventoryQuantityCommandResponseDTO:
        """Atomically append one valid quantity change, or return its prior retry."""
        event_type = self._command_event_type(request)
        batch = await self._get_owned_batch(user_id, batch_id)
        existing = await self._get_idempotent_ledger_entry(
            user_id,
            batch_id,
            idempotency_key,
            event_type,
        )
        if existing is not None:
            return await self._command_response(batch, existing)
        if batch.status in {
            InventoryBatchStatus.ARCHIVED,
            InventoryBatchStatus.DISCARDED,
        }:
            raise InventoryQuantityConflictError(
                "Quantity commands cannot modify an archived or discarded batch",
            )
        delta = self._command_delta(batch, request)
        quantity_after = batch.current_quantity + delta
        if quantity_after < 0:
            raise InventoryQuantityConflictError(
                "Inventory quantity cannot become negative",
            )
        batch.current_quantity = quantity_after
        batch.status = self._status_after_command(request, quantity_after)
        ledger_entry = InventoryLedgerEntryModel(
            user_id=user_id,
            inventory_batch_id=batch.id,
            event_type=event_type,
            quantity_before=quantity_after - delta,
            quantity_delta=delta,
            quantity_after=quantity_after,
            unit=batch.unit,
            idempotency_key=idempotency_key,
        )
        try:
            self.db_session.add(ledger_entry)
            await self.db_session.commit()
        except SQLAlchemyError:
            await self.db_session.rollback()
            raise
        await self.db_session.refresh(batch, attribute_names=["updated_at"])
        await self.db_session.refresh(ledger_entry)
        return await self._command_response(batch, ledger_entry)

    @staticmethod
    def _summary_key(batch: InventoryBatchModel) -> tuple[str, str]:
        """Keep distinct ingredient identities and incompatible unit families apart."""
        identity = (
            f"ingredient:{batch.master_ingredient_id}"
            if batch.master_ingredient_id is not None
            else f"custom:{batch.custom_name}"
        )
        group = unit_group(batch.unit)
        return identity, group.value if group is not None else batch.unit.value

    async def _summary_item(
        self,
        batches: list[InventoryBatchModel],
        rules: list[ShelfLifeRule],
        warning_days: int,
    ) -> InventorySummaryItemDTO:
        """Convert a compatible group to its documented base unit with batch detail."""
        first_batch = batches[0]
        group = unit_group(first_batch.unit)
        summary_unit = self._summary_unit(first_batch.unit, group)
        quantity = sum(
            (
                convert_quantity(
                    Decimal(str(batch.current_quantity)),
                    batch.unit,
                    summary_unit,
                )
                for batch in batches
            ),
            start=Decimal(0),
        )
        batch_dtos = [
            await self._to_dto(batch, rules=rules, warning_days=warning_days)
            for batch in batches
        ]
        first_dto = batch_dtos[0]
        return InventorySummaryItemDTO(
            master_ingredient=first_dto.master_ingredient,
            custom_name=first_dto.custom_name,
            quantity=float(quantity),
            unit=summary_unit,
            batches=batch_dtos,
        )

    @staticmethod
    def _summary_unit(
        unit: MeasurementUnit,
        group: UnitGroup | None,
    ) -> MeasurementUnit:
        """Return a stable base unit for an automatically compatible group."""
        if group is UnitGroup.MASS:
            return MeasurementUnit.GRAM
        if group is UnitGroup.VOLUME:
            return MeasurementUnit.ML
        return unit

    @staticmethod
    def _command_event_type(
        request: InventoryQuantityCommandRequestDTO,
    ) -> InventoryLedgerEventType:
        """Map explicit commands to the existing immutable ledger vocabulary."""
        if request.command is InventoryQuantityCommand.ADJUST:
            if request.event_type is None:
                raise ValueError("ADJUST requires an event type")
            return request.event_type
        if request.command is InventoryQuantityCommand.DISCARD:
            return InventoryLedgerEventType.DISCARDED
        return InventoryLedgerEventType.MANUAL_ADJUSTMENT

    @staticmethod
    def _command_delta(
        batch: InventoryBatchModel,
        request: InventoryQuantityCommandRequestDTO,
    ) -> float:
        """Derive each command's one allowed balance delta before mutating state."""
        if request.command is InventoryQuantityCommand.ADJUST:
            if request.quantity_delta is None:
                raise ValueError("ADJUST requires a quantity delta")
            return request.quantity_delta
        if request.command is InventoryQuantityCommand.CONSUME:
            if request.quantity is None:
                raise ValueError("CONSUME requires a quantity")
            return -request.quantity
        return -batch.current_quantity

    @staticmethod
    def _status_after_command(
        request: InventoryQuantityCommandRequestDTO,
        quantity_after: float,
    ) -> InventoryBatchStatus:
        """Apply the documented depleted and discarded lifecycle semantics."""
        if request.command is InventoryQuantityCommand.DISCARD:
            return InventoryBatchStatus.DISCARDED
        if quantity_after == 0:
            return InventoryBatchStatus.DEPLETED
        return InventoryBatchStatus.ACTIVE

    async def _get_idempotent_ledger_entry(
        self,
        user_id: UUID,
        batch_id: UUID,
        idempotency_key: str,
        event_type: InventoryLedgerEventType,
    ) -> InventoryLedgerEntryModel | None:
        """Find the exact existing ledger operation defined by the DB uniqueness scope."""
        entry = await self.db_session.scalar(
            select(InventoryLedgerEntryModel).where(
                InventoryLedgerEntryModel.user_id == user_id,
                InventoryLedgerEntryModel.inventory_batch_id == batch_id,
                InventoryLedgerEntryModel.idempotency_key == idempotency_key,
                InventoryLedgerEntryModel.event_type == event_type,
            ),
        )
        return entry

    async def _command_response(
        self,
        batch: InventoryBatchModel,
        ledger_entry: InventoryLedgerEntryModel,
    ) -> InventoryQuantityCommandResponseDTO:
        """Map a command outcome and its immutable audit row to the public response."""
        return InventoryQuantityCommandResponseDTO(
            batch=await self._to_dto(batch),
            ledger_entry=InventoryLedgerEntryDTO(
                id=ledger_entry.id,
                event_type=ledger_entry.event_type,
                quantity_before=ledger_entry.quantity_before,
                quantity_delta=ledger_entry.quantity_delta,
                quantity_after=ledger_entry.quantity_after,
                unit=ledger_entry.unit,
                idempotency_key=ledger_entry.idempotency_key,
                created_at=ledger_entry.created_at,
            ),
        )

    def _list_filters(
        self,
        user_id: UUID,
        request: InventoryBatchListQueryDTO,
        warning_days: int,
    ) -> list[ColumnElement[bool]]:
        """Build SQL ownership and database-native list filters."""
        filters: list[ColumnElement[bool]] = [InventoryBatchModel.user_id == user_id]
        if request.master_ingredient_id is not None:
            filters.append(
                InventoryBatchModel.master_ingredient_id == request.master_ingredient_id
            )
        if request.category_id is not None:
            filters.append(
                InventoryBatchModel.master_ingredient.has(
                    MasterIngredientModel.category_id == request.category_id,
                )
            )
        if request.storage_mode is not None:
            filters.append(InventoryBatchModel.storage_mode == request.storage_mode)
        if request.status is not None:
            filters.append(InventoryBatchModel.status == request.status)
        else:
            filters.append(InventoryBatchModel.status != InventoryBatchStatus.ARCHIVED)
        if request.freshness_state is not None:
            now = datetime.now(UTC)
            warning_boundary = now + self._warning_delta(warning_days)
            if request.freshness_state is FreshnessState.UNKNOWN:
                filters.append(InventoryBatchModel.expires_at.is_(None))
            elif request.freshness_state is FreshnessState.EXPIRED:
                filters.append(InventoryBatchModel.expires_at < now)
            elif request.freshness_state is FreshnessState.EXPIRING_SOON:
                filters.extend(
                    [
                        InventoryBatchModel.expires_at >= now,
                        InventoryBatchModel.expires_at <= warning_boundary,
                    ],
                )
            else:
                filters.append(InventoryBatchModel.expires_at > warning_boundary)
        if request.expires_from is not None:
            filters.append(InventoryBatchModel.expires_at >= request.expires_from)
        if request.expires_to is not None:
            filters.append(InventoryBatchModel.expires_at <= request.expires_to)
        return filters

    async def _get_owned_batch(
        self,
        user_id: UUID,
        batch_id: UUID,
    ) -> InventoryBatchModel:
        """Load a batch only through its owner predicate to avoid data disclosure."""
        batch = (
            await self.db_session.execute(
                self._batch_statement().where(
                    InventoryBatchModel.id == batch_id,
                    InventoryBatchModel.user_id == user_id,
                ),
            )
        ).scalar_one_or_none()
        if batch is None:
            raise InventoryBatchNotFoundError()
        return batch

    @staticmethod
    def _batch_statement() -> Select[tuple[InventoryBatchModel]]:
        """Return the common load shape required by public batch DTO mapping."""
        return select(InventoryBatchModel).options(
            selectinload(InventoryBatchModel.master_ingredient).selectinload(
                MasterIngredientModel.category,
            ),
        )

    async def _get_master_ingredient(
        self,
        ingredient_id: UUID | None,
    ) -> MasterIngredientModel | None:
        """Load an existing catalog identity, or permit a custom identity."""
        if ingredient_id is None:
            return None
        ingredient = (
            await self.db_session.execute(
                select(MasterIngredientModel)
                .where(MasterIngredientModel.id == ingredient_id)
                .options(selectinload(MasterIngredientModel.category)),
            )
        ).scalar_one_or_none()
        if ingredient is None:
            raise InventoryIngredientNotFoundError()
        return ingredient

    @staticmethod
    def _validate_unit(
        ingredient: MasterIngredientModel | None,
        unit: "MeasurementUnit",
    ) -> None:
        """Reuse the Task 4.2 compatibility service for catalog-backed batches."""
        if ingredient is not None and not are_units_compatible(
            unit, ingredient.canonical_unit
        ):
            raise InventoryUnitMismatchError()

    async def _resolve_updated_identity(
        self,
        batch: InventoryBatchModel,
        request: UpdateInventoryBatchRequestDTO,
    ) -> MasterIngredientModel | None:
        """Resolve a complete patched identity before applying it to the ORM model."""
        fields_set = request.model_fields_set
        master_ingredient_id = (
            request.master_ingredient_id
            if "master_ingredient_id" in fields_set
            else batch.master_ingredient_id
        )
        custom_name = self._updated_custom_name(batch, request)
        if (master_ingredient_id is None) == (custom_name is None):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                detail="Exactly one of master_ingredient_id and custom_name is required",
            )
        return await self._get_master_ingredient(master_ingredient_id)

    async def _prepare_update(
        self,
        batch: InventoryBatchModel,
        request: UpdateInventoryBatchRequestDTO,
    ) -> _ResolvedBatchUpdate:
        """Resolve all fields that must be valid together before mutation."""
        fields_set = request.model_fields_set
        ingredient = await self._resolve_updated_identity(batch, request)
        if "unit" in fields_set and request.unit is None:
            raise self._required_patch_field_error("unit")
        if "storage_mode" in fields_set and request.storage_mode is None:
            raise self._required_patch_field_error("storage_mode")
        unit = request.unit if request.unit is not None else batch.unit
        self._validate_unit(ingredient, unit)
        storage_mode = (
            request.storage_mode
            if request.storage_mode is not None
            else batch.storage_mode
        )
        purchased_at = (
            request.purchased_at if "purchased_at" in fields_set else batch.purchased_at
        )
        stored_at = request.stored_at if "stored_at" in fields_set else batch.stored_at
        manufacturer_expires_at = self._expiration_patch_value(
            batch,
            request,
            use_manufacturer=True,
            authoritative_source=ExpirationSource.MANUFACTURER,
        )
        override_expires_at = self._expiration_patch_value(
            batch,
            request,
            use_manufacturer=False,
            authoritative_source=ExpirationSource.USER_OVERRIDE,
        )
        if manufacturer_expires_at is not None and override_expires_at is not None:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                detail=(
                    "manufacturer_expires_at and expiration_override_at cannot both "
                    "be set"
                ),
            )
        return _ResolvedBatchUpdate(
            ingredient=ingredient,
            custom_name=self._updated_custom_name(batch, request),
            unit=unit,
            storage_mode=storage_mode,
            purchased_at=purchased_at,
            stored_at=stored_at,
            expiration_inputs=_ExpirationInputs(
                ingredient=ingredient,
                storage_mode=storage_mode,
                purchased_at=purchased_at,
                stored_at=stored_at,
                manufacturer_expires_at=manufacturer_expires_at,
                override_expires_at=override_expires_at,
            ),
        )

    @staticmethod
    def _apply_update(
        batch: InventoryBatchModel,
        request: UpdateInventoryBatchRequestDTO,
        update: _ResolvedBatchUpdate,
        expiration: ExpirationResolution,
    ) -> None:
        """Apply a fully validated metadata patch without touching quantity state."""
        batch.master_ingredient_id = (
            update.ingredient.id if update.ingredient is not None else None
        )
        batch.master_ingredient = update.ingredient
        batch.custom_name = update.custom_name
        batch.unit = update.unit
        batch.storage_mode = update.storage_mode
        batch.purchased_at = update.purchased_at
        batch.stored_at = update.stored_at
        for field_name in ("packaged_at", "unit_cost", "note", "media_url"):
            if field_name in request.model_fields_set:
                setattr(batch, field_name, getattr(request, field_name))
        batch.expires_at = expiration.expires_at
        batch.expiration_source = expiration.source

    @staticmethod
    def _updated_custom_name(
        batch: InventoryBatchModel,
        request: UpdateInventoryBatchRequestDTO,
    ) -> str | None:
        """Keep or replace custom identity according to explicit patch fields."""
        return (
            request.custom_name
            if "custom_name" in request.model_fields_set
            else batch.custom_name
        )

    @staticmethod
    def _expiration_patch_value(
        batch: InventoryBatchModel,
        request: UpdateInventoryBatchRequestDTO,
        *,
        use_manufacturer: bool,
        authoritative_source: ExpirationSource,
    ) -> datetime | None:
        """Apply an explicit clear/set or preserve the matching authoritative value."""
        field_name = (
            "manufacturer_expires_at" if use_manufacturer else "expiration_override_at"
        )
        if field_name in request.model_fields_set:
            return (
                request.manufacturer_expires_at
                if use_manufacturer
                else request.expiration_override_at
            )
        if batch.expiration_source is authoritative_source:
            return batch.expires_at
        return None

    @staticmethod
    def _required_patch_field_error(field_name: str) -> HTTPException:
        """Return a stable validation response for non-nullable patch fields."""
        return HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=f"{field_name} must not be null",
        )

    async def _resolve_expiration(
        self,
        inputs: _ExpirationInputs,
    ) -> tuple[ExpirationResolution, list[ShelfLifeRule]]:
        """Resolve precedence and shelf-life fallback through the pure Task 4.2 service."""
        if inputs.manufacturer_expires_at is not None:
            existing = ExistingExpiration(
                expires_at=inputs.manufacturer_expires_at,
                source=ExpirationSource.MANUFACTURER,
            )
        elif inputs.override_expires_at is not None:
            existing = ExistingExpiration(
                expires_at=inputs.override_expires_at,
                source=ExpirationSource.USER_OVERRIDE,
            )
        else:
            existing = ExistingExpiration(
                expires_at=None,
                source=ExpirationSource.UNKNOWN,
            )
        rules = await self._get_applicable_rules(inputs.ingredient, inputs.storage_mode)
        resolution = resolve_expiration(
            existing,
            ShelfLifeEstimationContext(
                stored_at=inputs.stored_at,
                purchased_at=inputs.purchased_at,
                master_ingredient_id=(
                    inputs.ingredient.id if inputs.ingredient is not None else None
                ),
                category_id=(
                    inputs.ingredient.category_id
                    if inputs.ingredient is not None
                    else None
                ),
                storage_mode=inputs.storage_mode,
            ),
            rules,
        )
        return resolution, rules

    async def _get_applicable_rules(
        self,
        ingredient: MasterIngredientModel | None,
        storage_mode: StorageMode,
    ) -> list[ShelfLifeRule]:
        """Load only the ingredient/category rules relevant to one batch context."""
        if ingredient is None:
            return []
        rows = list(
            (
                await self.db_session.execute(
                    select(ShelfLifeRuleModel).where(
                        ShelfLifeRuleModel.storage_mode == storage_mode,
                        or_(
                            ShelfLifeRuleModel.master_ingredient_id == ingredient.id,
                            ShelfLifeRuleModel.category_id == ingredient.category_id,
                        ),
                    ),
                )
            )
            .scalars()
            .all()
        )
        return [self._as_domain_rule(rule) for rule in rows]

    async def _get_rules_for_batches(
        self,
        batches: Iterable[InventoryBatchModel],
    ) -> list[ShelfLifeRule]:
        """Fetch all potentially applicable list-page rules in one query."""
        ingredients = [
            batch.master_ingredient
            for batch in batches
            if batch.master_ingredient is not None
        ]
        ingredient_ids = [ingredient.id for ingredient in ingredients]
        category_ids = [ingredient.category_id for ingredient in ingredients]
        if not ingredient_ids:
            return []
        rows = list(
            (
                await self.db_session.execute(
                    select(ShelfLifeRuleModel).where(
                        or_(
                            ShelfLifeRuleModel.master_ingredient_id.in_(ingredient_ids),
                            ShelfLifeRuleModel.category_id.in_(category_ids),
                        ),
                    ),
                )
            )
            .scalars()
            .all()
        )
        return [self._as_domain_rule(rule) for rule in rows]

    @staticmethod
    def _as_domain_rule(rule: ShelfLifeRuleModel) -> ShelfLifeRule:
        """Map persisted shelf-life rows to the pure service's value object."""
        return ShelfLifeRule(
            scope=rule.scope,
            storage_mode=rule.storage_mode,
            default_days=rule.default_days,
            master_ingredient_id=rule.master_ingredient_id,
            category_id=rule.category_id,
        )

    async def _warning_days(self, user_id: UUID) -> int:
        """Use an optional user notification override or the MVP default window."""
        preference = await self.db_session.scalar(
            select(UserNotificationPreferenceModel.warning_days).where(
                UserNotificationPreferenceModel.user_id == user_id,
            ),
        )
        return preference if preference is not None else _DEFAULT_WARNING_DAYS

    async def _to_dto(
        self,
        batch: InventoryBatchModel,
        *,
        rules: list[ShelfLifeRule] | None = None,
        warning_days: int | None = None,
    ) -> InventoryBatchDTO:
        """Map a loaded batch to its response including computed freshness metadata."""
        batch_rules = rules
        if batch_rules is None:
            batch_rules = await self._get_applicable_rules(
                batch.master_ingredient,
                batch.storage_mode,
            )
        resolution = resolve_expiration(
            ExistingExpiration(batch.expires_at, batch.expiration_source),
            ShelfLifeEstimationContext(
                stored_at=batch.stored_at,
                purchased_at=batch.purchased_at,
                master_ingredient_id=(
                    batch.master_ingredient.id
                    if batch.master_ingredient is not None
                    else None
                ),
                category_id=(
                    batch.master_ingredient.category_id
                    if batch.master_ingredient is not None
                    else None
                ),
                storage_mode=batch.storage_mode,
            ),
            batch_rules,
        )
        effective_warning_days = (
            warning_days
            if warning_days is not None
            else await self._warning_days(batch.user_id)
        )
        ingredient = batch.master_ingredient
        return InventoryBatchDTO(
            id=batch.id,
            master_ingredient=(
                IngredientIdentityDTO(
                    id=ingredient.id,
                    name=ingredient.name,
                    category_id=ingredient.category_id,
                    category_name=ingredient.category.name,
                )
                if ingredient is not None
                else None
            ),
            custom_name=batch.custom_name,
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
            freshness_state=calculate_freshness(
                batch.expires_at,
                now=datetime.now(UTC),
                warning_days=effective_warning_days,
            ),
            applied_shelf_life_rule=(
                AppliedShelfLifeRuleDTO(
                    scope=resolution.shelf_life_rule.scope,
                    storage_mode=resolution.shelf_life_rule.storage_mode,
                    default_days=resolution.shelf_life_rule.default_days,
                )
                if resolution.shelf_life_rule is not None
                else None
            ),
            unit_cost=batch.unit_cost,
            note=batch.note,
            media_url=batch.media_url,
            created_at=batch.created_at,
            updated_at=batch.updated_at,
            archived_at=batch.archived_at,
        )

    @staticmethod
    def _warning_delta(warning_days: int) -> timedelta:
        """Build the configured warning horizon without duplicating freshness logic."""
        return timedelta(days=warning_days)
