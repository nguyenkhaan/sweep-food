// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'app_notification_dto.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

_AppNotificationDto _$AppNotificationDtoFromJson(Map<String, dynamic> json) =>
    _AppNotificationDto(
      id: json['notification_id'] as String,
      type: json['type'] as String,
      title: json['title'] as String,
      body: json['body'] as String,
      createdAt: DateTime.parse(json['created_at'] as String),
      status: json['status'] as String? ?? 'UNREAD',
      inventoryBatchId: json['inventory_batch_id'] as String?,
    );

Map<String, dynamic> _$AppNotificationDtoToJson(_AppNotificationDto instance) =>
    <String, dynamic>{
      'notification_id': instance.id,
      'type': instance.type,
      'title': instance.title,
      'body': instance.body,
      'created_at': instance.createdAt.toIso8601String(),
      'status': instance.status,
      'inventory_batch_id': instance.inventoryBatchId,
    };
