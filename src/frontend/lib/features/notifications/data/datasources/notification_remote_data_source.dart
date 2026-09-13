import 'package:sweepfood/core/network/api_client.dart';
import 'package:sweepfood/core/network/api_paths.dart';
import 'package:sweepfood/features/notifications/data/models/app_notification_dto.dart';

/// Talks to `/notifications`. Throws on failure — the repository maps.
class NotificationRemoteDataSource {
  NotificationRemoteDataSource(this._api);

  final ApiClient _api;

  /// `GET /notifications` → `{ items, next_before }` (newest first, capped at
  /// the backend's default page size — the notification centre shows one page).
  Future<List<AppNotificationDto>> list() async {
    final json = await _api.get(ApiPaths.notifications);
    final items = (json is Map ? json['items'] : json) as List<dynamic>;
    return items
        .map((e) => AppNotificationDto.fromJson(e as Map<String, dynamic>))
        .toList();
  }

  /// `PATCH /notifications/{id}` — the only user-writable transition besides
  /// `DISMISSED`, which the app has no UI for yet.
  Future<void> markRead(String id) =>
      _api.patch(ApiPaths.notification(id), body: {'status': 'READ'});
}
