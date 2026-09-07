import 'package:freezed_annotation/freezed_annotation.dart';
import 'package:sweepfood/shared/domain/measurement_unit.dart';

part 'inventory_ledger.freezed.dart';

/// Backend `InventoryLedgerEventType` — one immutable quantity-change kind.
enum LedgerEventType {
  initialStock('INITIAL_STOCK'),
  manualAdjustment('MANUAL_ADJUSTMENT'),
  manualConsumption('MANUAL_CONSUMPTION'),
  cookingConsumption('COOKING_CONSUMPTION'),
  discarded('DISCARDED'),
  leftoverCreated('LEFTOVER_CREATED'),
  correction('CORRECTION'),
  metadataUpdated('METADATA_UPDATED'),
  moved('MOVED'),
  archived('ARCHIVED');

  const LedgerEventType(this.wire);
  final String wire;

  static LedgerEventType fromWire(String? v) => LedgerEventType.values.firstWhere(
        (e) => e.wire == v,
        orElse: () => LedgerEventType.correction,
      );

  String get label => switch (this) {
        LedgerEventType.initialStock => 'Nhập kho ban đầu',
        LedgerEventType.manualAdjustment => 'Điều chỉnh thủ công',
        LedgerEventType.manualConsumption => 'Đã dùng (thủ công)',
        LedgerEventType.cookingConsumption => 'Trừ kho khi nấu',
        LedgerEventType.discarded => 'Bỏ đi',
        LedgerEventType.leftoverCreated => 'Tạo món ăn thừa',
        LedgerEventType.correction => 'Chỉnh sửa',
        LedgerEventType.metadataUpdated => 'Cập nhật thông tin',
        LedgerEventType.moved => 'Chuyển ngăn bảo quản',
        LedgerEventType.archived => 'Lưu trữ',
      };

  /// Whether this event changed the quantity (vs. just metadata / a move).
  bool get affectsQuantity => switch (this) {
        LedgerEventType.metadataUpdated ||
        LedgerEventType.moved ||
        LedgerEventType.archived =>
          false,
        _ => true,
      };
}

/// One `GET /inventory/ledger` row.
@freezed
abstract class InventoryLedgerEntry with _$InventoryLedgerEntry {
  const InventoryLedgerEntry._();

  const factory InventoryLedgerEntry({
    required String id,
    required String inventoryBatchId,
    required LedgerEventType eventType,
    required double quantityBefore,
    required double quantityDelta,
    required double quantityAfter,
    required MeasurementUnit unit,
    String? cookingSessionId,
    String? reason,
    required DateTime createdAt,
  }) = _InventoryLedgerEntry;

  bool get isIncrease => quantityDelta > 0;
}
