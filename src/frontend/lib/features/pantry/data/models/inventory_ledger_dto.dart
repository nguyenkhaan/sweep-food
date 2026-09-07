import 'package:freezed_annotation/freezed_annotation.dart';
import 'package:sweepfood/features/pantry/domain/entities/inventory_ledger.dart';
import 'package:sweepfood/shared/domain/measurement_unit.dart';

part 'inventory_ledger_dto.freezed.dart';
part 'inventory_ledger_dto.g.dart';

/// Tolerates decimals that arrive as JSON strings (pydantic `Decimal`).
double _asDouble(Object? v) {
  if (v == null) return 0;
  if (v is num) return v.toDouble();
  return double.tryParse(v.toString()) ?? 0;
}

/// One `GET /inventory/ledger` row. See `docs/api-contract.md` §10.
@freezed
abstract class InventoryLedgerEntryDto with _$InventoryLedgerEntryDto {
  const InventoryLedgerEntryDto._();

  const factory InventoryLedgerEntryDto({
    required String id,
    @JsonKey(name: 'inventory_batch_id') required String inventoryBatchId,
    @JsonKey(name: 'event_type') @Default('CORRECTION') String eventType,
    @JsonKey(name: 'quantity_before', fromJson: _asDouble)
    @Default(0)
    double quantityBefore,
    @JsonKey(name: 'quantity_delta', fromJson: _asDouble)
    @Default(0)
    double quantityDelta,
    @JsonKey(name: 'quantity_after', fromJson: _asDouble)
    @Default(0)
    double quantityAfter,
    @Default('GRAM') String unit,
    @JsonKey(name: 'cooking_session_id') String? cookingSessionId,
    @JsonKey(name: 'idempotency_key') String? idempotencyKey,
    String? reason,
    @JsonKey(name: 'created_at') required DateTime createdAt,
  }) = _InventoryLedgerEntryDto;

  factory InventoryLedgerEntryDto.fromJson(Map<String, dynamic> json) =>
      _$InventoryLedgerEntryDtoFromJson(json);

  InventoryLedgerEntry toEntity() => InventoryLedgerEntry(
        id: id,
        inventoryBatchId: inventoryBatchId,
        eventType: LedgerEventType.fromWire(eventType),
        quantityBefore: quantityBefore,
        quantityDelta: quantityDelta,
        quantityAfter: quantityAfter,
        unit: MeasurementUnit.fromWire(unit),
        cookingSessionId: cookingSessionId,
        reason: reason,
        createdAt: createdAt,
      );
}

@freezed
abstract class InventoryLedgerListDto with _$InventoryLedgerListDto {
  const factory InventoryLedgerListDto({
    @Default(<InventoryLedgerEntryDto>[]) List<InventoryLedgerEntryDto> items,
    @Default(0) int total,
    @Default(1) int page,
    @JsonKey(name: 'per_page') @Default(20) int perPage,
  }) = _InventoryLedgerListDto;

  factory InventoryLedgerListDto.fromJson(Map<String, dynamic> json) =>
      _$InventoryLedgerListDtoFromJson(json);
}
