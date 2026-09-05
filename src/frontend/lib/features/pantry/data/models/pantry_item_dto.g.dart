// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'pantry_item_dto.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

_PantryItemDto _$PantryItemDtoFromJson(Map<String, dynamic> json) =>
    _PantryItemDto(
      id: json['id'] as String,
      masterIngredientId: json['master_ingredient_id'] as String?,
      customName: json['custom_name'] as String?,
      ingredientName: json['ingredient_name'] as String,
      currentQuantity: (json['current_quantity'] as num).toDouble(),
      unit: json['unit'] as String,
      storageMode: json['storage_mode'] as String,
      status: json['status'] as String? ?? 'ACTIVE',
      source: json['source'] as String? ?? 'MANUAL',
      purchasedAt: json['purchased_at'] == null
          ? null
          : DateTime.parse(json['purchased_at'] as String),
      packagedAt: json['packaged_at'] == null
          ? null
          : DateTime.parse(json['packaged_at'] as String),
      expiresAt: json['expires_at'] == null
          ? null
          : DateTime.parse(json['expires_at'] as String),
      unitCost: json['unit_cost'] as num?,
      createdAt: DateTime.parse(json['created_at'] as String),
    );

Map<String, dynamic> _$PantryItemDtoToJson(_PantryItemDto instance) =>
    <String, dynamic>{
      'id': instance.id,
      'master_ingredient_id': instance.masterIngredientId,
      'custom_name': instance.customName,
      'ingredient_name': instance.ingredientName,
      'current_quantity': instance.currentQuantity,
      'unit': instance.unit,
      'storage_mode': instance.storageMode,
      'status': instance.status,
      'source': instance.source,
      'purchased_at': instance.purchasedAt?.toIso8601String(),
      'packaged_at': instance.packagedAt?.toIso8601String(),
      'expires_at': instance.expiresAt?.toIso8601String(),
      'unit_cost': instance.unitCost,
      'created_at': instance.createdAt.toIso8601String(),
    };
