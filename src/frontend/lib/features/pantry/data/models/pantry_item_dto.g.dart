// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'pantry_item_dto.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

_PantryItemDto _$PantryItemDtoFromJson(Map<String, dynamic> json) =>
    _PantryItemDto(
      id: json['id'] as String,
      name: json['name'] as String,
      category: json['category'] as String,
      quantity: (json['quantity'] as num).toDouble(),
      unit: json['unit'] as String,
      storageTier: json['storage_tier'] as String,
      addedAt: DateTime.parse(json['added_at'] as String),
      source: json['source'] as String,
      status: json['status'] as String? ?? 'active',
      ingredientId: json['ingredient_id'] as String?,
      packedDate: json['packed_date'] == null
          ? null
          : DateTime.parse(json['packed_date'] as String),
      expiryDate: json['expiry_date'] == null
          ? null
          : DateTime.parse(json['expiry_date'] as String),
      referenceShelfLifeDays:
          (json['reference_shelf_life_days'] as num?)?.toInt(),
      priceVnd: (json['price_vnd'] as num?)?.toInt(),
    );

Map<String, dynamic> _$PantryItemDtoToJson(_PantryItemDto instance) =>
    <String, dynamic>{
      'id': instance.id,
      'name': instance.name,
      'category': instance.category,
      'quantity': instance.quantity,
      'unit': instance.unit,
      'storage_tier': instance.storageTier,
      'added_at': instance.addedAt.toIso8601String(),
      'source': instance.source,
      'status': instance.status,
      'ingredient_id': instance.ingredientId,
      'packed_date': instance.packedDate?.toIso8601String(),
      'expiry_date': instance.expiryDate?.toIso8601String(),
      'reference_shelf_life_days': instance.referenceShelfLifeDays,
      'price_vnd': instance.priceVnd,
    };

_PantrySummaryDto _$PantrySummaryDtoFromJson(Map<String, dynamic> json) =>
    _PantrySummaryDto(
      totalCount: (json['total_count'] as num).toInt(),
      countByTier: (json['count_by_tier'] as Map<String, dynamic>?)?.map(
            (k, e) => MapEntry(k, (e as num).toInt()),
          ) ??
          const {},
      nearExpiry: (json['near_expiry'] as List<dynamic>?)
              ?.map((e) => PantryItemDto.fromJson(e as Map<String, dynamic>))
              .toList() ??
          const [],
      wasteReductionCount:
          (json['waste_reduction_count'] as num?)?.toInt() ?? 0,
      wasteAvoidedKg: (json['waste_avoided_kg'] as num?)?.toDouble(),
    );

Map<String, dynamic> _$PantrySummaryDtoToJson(_PantrySummaryDto instance) =>
    <String, dynamic>{
      'total_count': instance.totalCount,
      'count_by_tier': instance.countByTier,
      'near_expiry': instance.nearExpiry,
      'waste_reduction_count': instance.wasteReductionCount,
      'waste_avoided_kg': instance.wasteAvoidedKg,
    };
