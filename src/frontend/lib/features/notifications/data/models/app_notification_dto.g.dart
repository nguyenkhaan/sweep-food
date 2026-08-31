// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'app_notification_dto.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

_AppNotificationDto _$AppNotificationDtoFromJson(Map<String, dynamic> json) =>
    _AppNotificationDto(
      id: json['id'] as String,
      type: json['type'] as String,
      title: json['title'] as String,
      body: json['body'] as String,
      createdAt: DateTime.parse(json['created_at'] as String),
      read: json['read'] as bool? ?? false,
      pantryItemId: json['pantry_item_id'] as String?,
      dishIds: (json['dish_ids'] as List<dynamic>?)
              ?.map((e) => e as String)
              .toList() ??
          const <String>[],
    );

Map<String, dynamic> _$AppNotificationDtoToJson(_AppNotificationDto instance) =>
    <String, dynamic>{
      'id': instance.id,
      'type': instance.type,
      'title': instance.title,
      'body': instance.body,
      'created_at': instance.createdAt.toIso8601String(),
      'read': instance.read,
      'pantry_item_id': instance.pantryItemId,
      'dish_ids': instance.dishIds,
    };
