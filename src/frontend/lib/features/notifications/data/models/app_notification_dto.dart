import 'package:freezed_annotation/freezed_annotation.dart';
import 'package:sweepfood/features/notifications/domain/entities/app_notification.dart';

part 'app_notification_dto.freezed.dart';
part 'app_notification_dto.g.dart';

/// Mirrors the backend `NotificationResponseDTO` (`GET /api/notifications`,
/// `PATCH /api/notifications/{id}` — see `src/backend/src/module/notification`).
///
/// The backend keys the id as `notification_id`, tracks a tri-state `status`
/// (`UNREAD` / `READ` / `DISMISSED`) instead of a `read` bool, and links the
/// affected batch as `inventory_batch_id`.
@freezed
abstract class AppNotificationDto with _$AppNotificationDto {
  const AppNotificationDto._();

  const factory AppNotificationDto({
    @JsonKey(name: 'notification_id') required String id,
    required String type,
    required String title,
    required String body,
    @JsonKey(name: 'created_at') required DateTime createdAt,
    @Default('UNREAD') String status,
    @JsonKey(name: 'inventory_batch_id') String? inventoryBatchId,
  }) = _AppNotificationDto;

  factory AppNotificationDto.fromJson(Map<String, dynamic> json) =>
      _$AppNotificationDtoFromJson(json);

  AppNotification toEntity() => AppNotification(
        id: id,
        type: AppNotificationType.fromWire(type),
        title: title,
        body: body,
        createdAt: createdAt.toLocal(),
        read: status.toUpperCase() != 'UNREAD',
        pantryItemId: inventoryBatchId,
        dishIds: const [],
      );
}
