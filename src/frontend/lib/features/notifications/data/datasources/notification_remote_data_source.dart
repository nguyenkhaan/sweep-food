import 'package:frontend/core/network/api_client.dart';
import 'package:frontend/core/network/api_paths.dart';
import 'package:frontend/features/notifications/data/models/app_notification_dto.dart';

/// Talks to `/notifications`. Throws on failure — the repository maps.
class NotificationRemoteDataSource {
  NotificationRemoteDataSource(this._api);

  final ApiClient _api;

  Future<List<AppNotificationDto>> list() async {
    final json = await _api.get(ApiPaths.notifications);
    final items = (json is Map ? json['items'] : json) as List<dynamic>;
    return items
        .map((e) => AppNotificationDto.fromJson(e as Map<String, dynamic>))
        .toList();
  }

  Future<void> markRead(String id) =>
      _api.post(ApiPaths.notificationRead(id));
}
