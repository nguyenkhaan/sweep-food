import 'package:sweepfood/core/utils/result.dart';

/// Registers this device's push token with the backend so the expiry worker can
/// reach it. Ownership is enforced server-side from the access token.
abstract interface class DeviceRepository {
  /// `POST /users/me/devices` — returns the server `device_id`.
  Future<Result<String>> register(String fcmToken, {required String platform});

  /// `DELETE /users/me/devices/{device_id}`.
  Future<Result<void>> unregister(String deviceId);
}
