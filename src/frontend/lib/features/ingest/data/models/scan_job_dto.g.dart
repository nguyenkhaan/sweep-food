// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'scan_job_dto.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

_ParsedItemDraftDto _$ParsedItemDraftDtoFromJson(Map<String, dynamic> json) =>
    _ParsedItemDraftDto(
      name: json['name'] as String? ?? '',
      category: json['category'] as String? ?? '',
      quantity: (json['quantity'] as num?)?.toDouble() ?? 0,
      unit: json['unit'] as String? ?? 'g',
      storageTier: json['storage_tier'] as String? ?? 'fridge',
      packedDate: json['packed_date'] == null
          ? null
          : DateTime.parse(json['packed_date'] as String),
      expiryDate: json['expiry_date'] == null
          ? null
          : DateTime.parse(json['expiry_date'] as String),
      priceVnd: (json['price_vnd'] as num?)?.toInt(),
      isExpiryWarn: json['is_expiry_warn'] as bool? ?? false,
    );

Map<String, dynamic> _$ParsedItemDraftDtoToJson(_ParsedItemDraftDto instance) =>
    <String, dynamic>{
      'name': instance.name,
      'category': instance.category,
      'quantity': instance.quantity,
      'unit': instance.unit,
      'storage_tier': instance.storageTier,
      'packed_date': instance.packedDate?.toIso8601String(),
      'expiry_date': instance.expiryDate?.toIso8601String(),
      'price_vnd': instance.priceVnd,
      'is_expiry_warn': instance.isExpiryWarn,
    };
