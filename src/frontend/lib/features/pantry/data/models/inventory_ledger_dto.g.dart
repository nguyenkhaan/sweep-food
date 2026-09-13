// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'inventory_ledger_dto.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

_InventoryLedgerEntryDto _$InventoryLedgerEntryDtoFromJson(
  Map<String, dynamic> json,
) => _InventoryLedgerEntryDto(
  id: json['id'] as String,
  inventoryBatchId: json['inventory_batch_id'] as String,
  eventType: json['event_type'] as String? ?? 'CORRECTION',
  quantityBefore: json['quantity_before'] == null
      ? 0
      : _asDouble(json['quantity_before']),
  quantityDelta: json['quantity_delta'] == null
      ? 0
      : _asDouble(json['quantity_delta']),
  quantityAfter: json['quantity_after'] == null
      ? 0
      : _asDouble(json['quantity_after']),
  unit: json['unit'] as String? ?? 'GRAM',
  cookingSessionId: json['cooking_session_id'] as String?,
  idempotencyKey: json['idempotency_key'] as String?,
  reason: json['reason'] as String?,
  createdAt: DateTime.parse(json['created_at'] as String),
);

Map<String, dynamic> _$InventoryLedgerEntryDtoToJson(
  _InventoryLedgerEntryDto instance,
) => <String, dynamic>{
  'id': instance.id,
  'inventory_batch_id': instance.inventoryBatchId,
  'event_type': instance.eventType,
  'quantity_before': instance.quantityBefore,
  'quantity_delta': instance.quantityDelta,
  'quantity_after': instance.quantityAfter,
  'unit': instance.unit,
  'cooking_session_id': instance.cookingSessionId,
  'idempotency_key': instance.idempotencyKey,
  'reason': instance.reason,
  'created_at': instance.createdAt.toIso8601String(),
};

_InventoryLedgerListDto _$InventoryLedgerListDtoFromJson(
  Map<String, dynamic> json,
) => _InventoryLedgerListDto(
  items:
      (json['items'] as List<dynamic>?)
          ?.map(
            (e) => InventoryLedgerEntryDto.fromJson(e as Map<String, dynamic>),
          )
          .toList() ??
      const <InventoryLedgerEntryDto>[],
  total: (json['total'] as num?)?.toInt() ?? 0,
  page: (json['page'] as num?)?.toInt() ?? 1,
  perPage: (json['per_page'] as num?)?.toInt() ?? 20,
);

Map<String, dynamic> _$InventoryLedgerListDtoToJson(
  _InventoryLedgerListDto instance,
) => <String, dynamic>{
  'items': instance.items,
  'total': instance.total,
  'page': instance.page,
  'per_page': instance.perPage,
};
