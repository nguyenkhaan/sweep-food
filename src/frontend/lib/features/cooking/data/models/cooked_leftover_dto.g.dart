// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'cooked_leftover_dto.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

_CookedLeftoverDto _$CookedLeftoverDtoFromJson(Map<String, dynamic> json) =>
    _CookedLeftoverDto(
      batchId: json['batch_id'] as String,
      cookingSessionId: json['cooking_session_id'] as String,
      quantity: (json['quantity'] as num).toDouble(),
      unit: json['unit'] as String,
      storageMode: json['storage_mode'] as String,
      expiresAt: json['expires_at'] == null
          ? null
          : DateTime.parse(json['expires_at'] as String),
      createdAt: DateTime.parse(json['created_at'] as String),
    );

Map<String, dynamic> _$CookedLeftoverDtoToJson(_CookedLeftoverDto instance) =>
    <String, dynamic>{
      'batch_id': instance.batchId,
      'cooking_session_id': instance.cookingSessionId,
      'quantity': instance.quantity,
      'unit': instance.unit,
      'storage_mode': instance.storageMode,
      'expires_at': instance.expiresAt?.toIso8601String(),
      'created_at': instance.createdAt.toIso8601String(),
    };
