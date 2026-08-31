import 'package:frontend/core/network/api_client.dart';
import 'package:frontend/core/network/api_paths.dart';

/// Registers / unregisters this device's push token (`/devices`).
///
/// FCM is deferred to M6, so nothing calls this yet — it's here so the wiring
/// exists the moment a real token is available.
class DeviceRemoteDataSource {
  DeviceRemoteDataSource(this._api);

  final ApiClient _api;

  Future<void> register(String fcmToken, {required String platform}) =>
      _api.post(
        ApiPaths.devices,
        body: {'fcm_token': fcmToken, 'platform': platform},
      );

  Future<void> unregister(String fcmToken) =>
      _api.delete(ApiPaths.device(fcmToken));
}
