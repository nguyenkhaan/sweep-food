"""Authenticated inventory batch, summary, and ledger routes."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Header, Query, Response, status

from src.middleware.auth_middleware import AuthenticatedUser, require_authentication
from src.module.inventory.inventory_dependency import get_inventory_service
from src.module.inventory.inventory_dto import (
    ConsumeInventoryBatchRequestDTO,
    CreateInventoryBatchRequestDTO,
    InventoryAdjustmentRequestDTO,
    InventoryBatchDTO,
    InventoryBatchListResponseDTO,
    InventoryBatchQueryDTO,
    InventoryLedgerListResponseDTO,
    InventoryLedgerQueryDTO,
    InventorySummaryResponseDTO,
    MoveInventoryBatchRequestDTO,
    UpdateInventoryBatchRequestDTO,
)
from src.module.inventory.inventory_service import InventoryService

inventory_router = APIRouter(prefix="/inventory", tags=["inventory"])


@inventory_router.post(
    "/batches",
    response_model=InventoryBatchDTO,
    status_code=status.HTTP_201_CREATED,
)
async def post_inventory_batch(
    body: CreateInventoryBatchRequestDTO,
    user: Annotated[AuthenticatedUser, Depends(require_authentication)],
    service: Annotated[InventoryService, Depends(get_inventory_service)],
    idempotency_key: Annotated[str, Header(alias="Idempotency-Key", min_length=1)],
) -> InventoryBatchDTO:
    """Create one manual batch and its initial-stock ledger entry."""
    return await service.create_batch(user.user_id, body, idempotency_key)


@inventory_router.get("/batches", response_model=InventoryBatchListResponseDTO)
async def get_inventory_batches(
    user: Annotated[AuthenticatedUser, Depends(require_authentication)],
    service: Annotated[InventoryService, Depends(get_inventory_service)],
    query: Annotated[InventoryBatchQueryDTO, Query()],
) -> InventoryBatchListResponseDTO:
    """List the current user's batches with stable pagination."""
    return await service.list_batches(user.user_id, query)


@inventory_router.get("/batches/{batch_id}", response_model=InventoryBatchDTO)
async def get_inventory_batch(
    batch_id: UUID,
    user: Annotated[AuthenticatedUser, Depends(require_authentication)],
    service: Annotated[InventoryService, Depends(get_inventory_service)],
) -> InventoryBatchDTO:
    """Read one owned batch without disclosing cross-user existence."""
    return await service.get_batch(user.user_id, batch_id)


@inventory_router.patch("/batches/{batch_id}", response_model=InventoryBatchDTO)
async def patch_inventory_batch(
    batch_id: UUID,
    body: UpdateInventoryBatchRequestDTO,
    user: Annotated[AuthenticatedUser, Depends(require_authentication)],
    service: Annotated[InventoryService, Depends(get_inventory_service)],
    idempotency_key: Annotated[str, Header(alias="Idempotency-Key", min_length=1)],
) -> InventoryBatchDTO:
    """Update batch metadata and audit expiration overrides."""
    return await service.update_batch(
        user.user_id,
        batch_id,
        body,
        idempotency_key,
    )


@inventory_router.delete(
    "/batches/{batch_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_inventory_batch(
    batch_id: UUID,
    user: Annotated[AuthenticatedUser, Depends(require_authentication)],
    service: Annotated[InventoryService, Depends(get_inventory_service)],
    idempotency_key: Annotated[str, Header(alias="Idempotency-Key", min_length=1)],
    reason: Annotated[str, Header(alias="X-Reason", min_length=1, max_length=500)],
) -> Response:
    """Archive one batch and append an idempotent zero-delta audit."""
    await service.archive_batch(user.user_id, batch_id, idempotency_key, reason)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@inventory_router.post(
    "/batches/{batch_id}/adjustments",
    response_model=InventoryBatchDTO,
)
async def post_inventory_adjustment(
    batch_id: UUID,
    body: InventoryAdjustmentRequestDTO,
    user: Annotated[AuthenticatedUser, Depends(require_authentication)],
    service: Annotated[InventoryService, Depends(get_inventory_service)],
    idempotency_key: Annotated[str, Header(alias="Idempotency-Key", min_length=1)],
) -> InventoryBatchDTO:
    """Atomically adjust a locked batch and append one ledger record."""
    return await service.adjust_batch(
        user.user_id,
        batch_id,
        body,
        idempotency_key,
    )


@inventory_router.post(
    "/batches/{batch_id}/consume",
    response_model=InventoryBatchDTO,
)
async def post_inventory_consumption(
    batch_id: UUID,
    body: ConsumeInventoryBatchRequestDTO,
    user: Annotated[AuthenticatedUser, Depends(require_authentication)],
    service: Annotated[InventoryService, Depends(get_inventory_service)],
    idempotency_key: Annotated[str, Header(alias="Idempotency-Key", min_length=1)],
) -> InventoryBatchDTO:
    """Consume stock in the batch unit and append one manual-consumption ledger."""
    return await service.consume_batch(
        user.user_id,
        batch_id,
        body,
        idempotency_key,
    )


@inventory_router.post(
    "/batches/{batch_id}/move",
    response_model=InventoryBatchDTO,
)
async def post_inventory_move(
    batch_id: UUID,
    body: MoveInventoryBatchRequestDTO,
    user: Annotated[AuthenticatedUser, Depends(require_authentication)],
    service: Annotated[InventoryService, Depends(get_inventory_service)],
    idempotency_key: Annotated[str, Header(alias="Idempotency-Key", min_length=1)],
) -> InventoryBatchDTO:
    """Move one batch, refresh estimates, and append an idempotent audit."""
    return await service.move_batch(user.user_id, batch_id, body, idempotency_key)


@inventory_router.get("/summary", response_model=InventorySummaryResponseDTO)
async def get_inventory_summary(
    user: Annotated[AuthenticatedUser, Depends(require_authentication)],
    service: Annotated[InventoryService, Depends(get_inventory_service)],
) -> InventorySummaryResponseDTO:
    """Return compatible active quantities grouped for display."""
    return await service.get_summary(user.user_id)


@inventory_router.get("/ledger", response_model=InventoryLedgerListResponseDTO)
async def get_inventory_ledger(
    user: Annotated[AuthenticatedUser, Depends(require_authentication)],
    service: Annotated[InventoryService, Depends(get_inventory_service)],
    query: Annotated[InventoryLedgerQueryDTO, Query()],
) -> InventoryLedgerListResponseDTO:
    """Read the authenticated user's immutable quantity history."""
    return await service.list_ledger(user.user_id, query)
