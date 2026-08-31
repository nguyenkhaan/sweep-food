"""Persistence contract tests for notification worker query indexes."""

from typing import cast

from sqlalchemy import Table

from src.model.device_registration_model import DeviceRegistrationModel
from src.model.inventory_batch_model import InventoryBatchModel
from src.model.notification_model import NotificationModel


def test_notification_models_define_worker_query_indexes() -> None:
    """Device, delivery, list, and expiration scans have supporting indexes."""
    device_table = cast(Table, DeviceRegistrationModel.__table__)
    notification_table = cast(Table, NotificationModel.__table__)
    inventory_table = cast(Table, InventoryBatchModel.__table__)
    device_indexes = {index.name for index in device_table.indexes}
    notification_indexes = {index.name for index in notification_table.indexes}
    inventory_indexes = {index.name for index in inventory_table.indexes}

    assert "ix_device_registrations_user_enabled" in device_indexes
    assert "ix_notifications_user_created_at" in notification_indexes
    assert "ix_notifications_delivery_scheduled" in notification_indexes
    assert "ix_inventory_batches_status_expires_at" in inventory_indexes
