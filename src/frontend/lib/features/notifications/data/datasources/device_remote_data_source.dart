import 'package:sweepfood/core/network/api_client.dart';
import 'package:sweepfood/core/network/api_paths.dart';

/// Registers / unregisters this device's FCM token against the backend
/// (`/users/me/devices` — see `src/backend/src/module/notification`).
class DeviceRemoteDataSource {
  DeviceRemoteDataSource(this._api);

  final ApiClient _api;

  /// `POST /users/me/devices` → `{ device_id, platform, is_enabled, last_seen_at }`.
  /// Returns the `device_id`, which is what [unregister] needs.
  Future<String> register(String fcmToken, {required String platform}) async {
    final json = await _api.post(
      ApiPaths.devices,
      body: {'fcm_token': fcmToken, 'platform': platform},
    );
    return (json as Map<String, dynamic>)['device_id'].toString();
  }

  /// `DELETE /users/me/devices/{device_id}` — disable one owned registration.
  Future<void> unregister(String deviceId) =>
      _api.delete(ApiPaths.device(deviceId));
}
