import 'package:freezed_annotation/freezed_annotation.dart';
import 'package:frontend/features/notifications/domain/entities/app_notification.dart';

part 'app_notification_dto.freezed.dart';
part 'app_notification_dto.g.dart';

@freezed
abstract class AppNotificationDto with _$AppNotificationDto {
  const AppNotificationDto._();

  const factory AppNotificationDto({
    required String id,
    required String type,
    required String title,
    required String body,
    @JsonKey(name: 'created_at') required DateTime createdAt,
    @Default(false) bool read,
    @JsonKey(name: 'pantry_item_id') String? pantryItemId,
    @JsonKey(name: 'dish_ids') @Default(<String>[]) List<String> dishIds,
  }) = _AppNotificationDto;

  factory AppNotificationDto.fromJson(Map<String, dynamic> json) =>
      _$AppNotificationDtoFromJson(json);

  AppNotification toEntity() => AppNotification(
        id: id,
        type: AppNotificationType.fromWire(type),
        title: title,
        body: body,
        createdAt: createdAt,
        read: read,
        pantryItemId: pantryItemId,
        dishIds: dishIds,
      );
}
