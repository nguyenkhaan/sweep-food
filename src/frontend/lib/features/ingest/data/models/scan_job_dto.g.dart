// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'scan_job_dto.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

_ParsedItemDraftDto _$ParsedItemDraftDtoFromJson(Map<String, dynamic> json) =>
    _ParsedItemDraftDto(
      name: json['name'] as String? ?? '',
      rawName: json['raw_name'] as String?,
      masterIngredientCode: json['master_ingredient_code'] as String?,
      category: json['category'] as String? ?? '',
      quantity: (json['quantity'] as num?)?.toDouble() ?? 0,
      quantitySource: json['quantity_source'] as String?,
      unit: json['unit'] as String? ?? 'g',
      storageTier: json['storage_tier'] as String? ?? 'fridge',
      packedDate: json['packed_date'] == null
          ? null
          : DateTime.parse(json['packed_date'] as String),
      expiryDate: json['expiry_date'] == null
          ? null
          : DateTime.parse(json['expiry_date'] as String),
      priceVnd: (json['price_vnd'] as num?)?.toInt(),
      nutrition: json['nutrition'] as Map<String, dynamic>?,
      freshnessGuide: json['freshness_guide'] as Map<String, dynamic>?,
      isStaple: json['is_staple'] as bool?,
      isExpiryWarn: json['is_expiry_warn'] as bool? ?? false,
    );

Map<String, dynamic> _$ParsedItemDraftDtoToJson(_ParsedItemDraftDto instance) =>
    <String, dynamic>{
      'name': instance.name,
      'raw_name': instance.rawName,
      'master_ingredient_code': instance.masterIngredientCode,
      'category': instance.category,
      'quantity': instance.quantity,
      'quantity_source': instance.quantitySource,
      'unit': instance.unit,
      'storage_tier': instance.storageTier,
      'packed_date': instance.packedDate?.toIso8601String(),
      'expiry_date': instance.expiryDate?.toIso8601String(),
      'price_vnd': instance.priceVnd,
      'nutrition': instance.nutrition,
      'freshness_guide': instance.freshnessGuide,
      'is_staple': instance.isStaple,
      'is_expiry_warn': instance.isExpiryWarn,
    };
