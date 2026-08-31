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

_ScanJobDto _$ScanJobDtoFromJson(Map<String, dynamic> json) => _ScanJobDto(
  jobId: json['job_id'] as String,
  type: json['type'] as String,
  status: json['status'] as String? ?? 'completed',
  rawText: json['raw_text'] as String?,
  rawTranscript: json['raw_transcript'] as String?,
  storeName: json['store_name'] as String?,
  purchaseDate: json['purchase_date'] == null
      ? null
      : DateTime.parse(json['purchase_date'] as String),
  fieldCount: (json['field_count'] as num?)?.toInt(),
  item: json['item'] == null
      ? null
      : ParsedItemDraftDto.fromJson(json['item'] as Map<String, dynamic>),
  items:
      (json['items'] as List<dynamic>?)
          ?.map((e) => ParsedItemDraftDto.fromJson(e as Map<String, dynamic>))
          .toList() ??
      const <ParsedItemDraftDto>[],
);

Map<String, dynamic> _$ScanJobDtoToJson(_ScanJobDto instance) =>
    <String, dynamic>{
      'job_id': instance.jobId,
      'type': instance.type,
      'status': instance.status,
      'raw_text': instance.rawText,
      'raw_transcript': instance.rawTranscript,
      'store_name': instance.storeName,
      'purchase_date': instance.purchaseDate?.toIso8601String(),
      'field_count': instance.fieldCount,
      'item': instance.item,
      'items': instance.items,
    };
