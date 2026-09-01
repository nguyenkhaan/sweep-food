"""Authenticated manual inventory batch CRUD routes."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Header, Query, Response, status

from src.middleware.auth_middleware import AuthenticatedUser, require_authentication
from src.module.inventory.inventory_dependency import get_inventory_service
from src.module.inventory.inventory_dto import (
    CreateInventoryBatchRequestDTO,
    InventoryBatchDTO,
    InventoryBatchListQueryDTO,
    InventoryBatchListResponseDTO,
    InventoryQuantityCommandRequestDTO,
    InventoryQuantityCommandResponseDTO,
    InventorySummaryResponseDTO,
    UpdateInventoryBatchRequestDTO,
)
from src.module.inventory.inventory_service import InventoryService

inventory_router = APIRouter(prefix="/inventory", tags=["inventory"])


@inventory_router.post(
    "/batches",
    response_model=InventoryBatchDTO,
    status_code=status.HTTP_201_CREATED,
    summary="Manually create an inventory batch",
    description=(
        "Create one distinct raw-ingredient batch for the authenticated user and "
        "record its initial stock in the immutable ledger."
    ),
)
async def post_inventory_batch(
    body: CreateInventoryBatchRequestDTO,
    user: Annotated[AuthenticatedUser, Depends(require_authentication)],
    service: Annotated[InventoryService, Depends(get_inventory_service)],
) -> InventoryBatchDTO:
    """Persist a manual batch with calculated expiration metadata."""
    return await service.create_batch(user.user_id, body)


@inventory_router.get(
    "/batches",
    response_model=InventoryBatchListResponseDTO,
    summary="List my inventory batches",
    description=(
        "List non-archived user batches using stable created-time and ID ordering. "
        "Use status=ARCHIVED to inspect archived records."
    ),
)
async def get_inventory_batches(
    user: Annotated[AuthenticatedUser, Depends(require_authentication)],
    service: Annotated[InventoryService, Depends(get_inventory_service)],
    filters: Annotated[InventoryBatchListQueryDTO, Query()],
) -> InventoryBatchListResponseDTO:
    """Return one stable, ownership-filtered page of inventory batches."""
    return await service.list_batches(user.user_id, filters)


@inventory_router.get(
    "/batches/{batch_id}",
    response_model=InventoryBatchDTO,
    summary="Read one inventory batch",
)
async def get_inventory_batch(
    batch_id: UUID,
    user: Annotated[AuthenticatedUser, Depends(require_authentication)],
    service: Annotated[InventoryService, Depends(get_inventory_service)],
) -> InventoryBatchDTO:
    """Return one owned batch without disclosing other users' records."""
    return await service.get_batch(user.user_id, batch_id)


@inventory_router.patch(
    "/batches/{batch_id}",
    response_model=InventoryBatchDTO,
    summary="Update owned batch metadata",
    description=(
        "Edit manual batch metadata only. Quantity and lifecycle commands are "
        "deliberately outside this endpoint."
    ),
)
async def patch_inventory_batch(
    batch_id: UUID,
    body: UpdateInventoryBatchRequestDTO,
    user: Annotated[AuthenticatedUser, Depends(require_authentication)],
    service: Annotated[InventoryService, Depends(get_inventory_service)],
) -> InventoryBatchDTO:
    """Update an owned batch and recalculate only non-authoritative expiration."""
    return await service.update_batch(user.user_id, batch_id, body)


@inventory_router.delete(
    "/batches/{batch_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Archive an owned inventory batch",
    description="Soft-archive one batch without changing its quantity or ledger history.",
)
async def delete_inventory_batch(
    batch_id: UUID,
    user: Annotated[AuthenticatedUser, Depends(require_authentication)],
    service: Annotated[InventoryService, Depends(get_inventory_service)],
) -> Response:
    """Mark an owned batch archived, leaving it retrievable via status=ARCHIVED."""
    await service.archive_batch(user.user_id, batch_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@inventory_router.get(
    "/summary",
    response_model=InventorySummaryResponseDTO,
    summary="Summarize my active inventory",
    description=(
        "Aggregate compatible active quantities without merging or hiding the "
        "underlying batch records."
    ),
)
async def get_inventory_summary(
    user: Annotated[AuthenticatedUser, Depends(require_authentication)],
    service: Annotated[InventoryService, Depends(get_inventory_service)],
) -> InventorySummaryResponseDTO:
    """Return owner-scoped compatible totals together with their batch details."""
    return await service.get_summary(user.user_id)


@inventory_router.post(
    "/batches/{batch_id}/adjustments",
    response_model=InventoryQuantityCommandResponseDTO,
    summary="Adjust, consume, or discard one owned inventory batch",
    description=(
        "Execute one explicit quantity command atomically and append its immutable "
        "ledger entry. An Idempotency-Key is required for safe retries."
    ),
)
async def post_inventory_quantity_command(
    batch_id: UUID,
    body: InventoryQuantityCommandRequestDTO,
    user: Annotated[AuthenticatedUser, Depends(require_authentication)],
    service: Annotated[InventoryService, Depends(get_inventory_service)],
    idempotency_key: Annotated[str, Header(alias="Idempotency-Key", min_length=1)],
) -> InventoryQuantityCommandResponseDTO:
    """Apply exactly one explicit, retry-safe quantity mutation to an owned batch."""
    return await service.apply_quantity_command(
        user.user_id,
        batch_id,
        idempotency_key,
        body,
    )
