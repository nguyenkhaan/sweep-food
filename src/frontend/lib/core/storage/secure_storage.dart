import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:frontend/core/config/app_constants.dart';

/// Thin wrapper over [FlutterSecureStorage] for the auth tokens. Nothing else
/// belongs here — use SharedPreferences (`prefs.dart`) for non-secret prefs.
class SecureStore {
  SecureStore(this._raw);

  final FlutterSecureStorage _raw;

  static const _opts = AndroidOptions(encryptedSharedPreferences: true);

  Future<String?> readAccessToken() =>
      _raw.read(key: AppConstants.kAccessToken, aOptions: _opts);

  Future<String?> readRefreshToken() =>
      _raw.read(key: AppConstants.kRefreshToken, aOptions: _opts);

  Future<void> writeTokens({
    required String accessToken,
    required String refreshToken,
  }) async {
    await _raw.write(
      key: AppConstants.kAccessToken,
      value: accessToken,
      aOptions: _opts,
    );
    await _raw.write(
      key: AppConstants.kRefreshToken,
      value: refreshToken,
      aOptions: _opts,
    );
  }

  Future<void> clear() async {
    await _raw.delete(key: AppConstants.kAccessToken, aOptions: _opts);
    await _raw.delete(key: AppConstants.kRefreshToken, aOptions: _opts);
  }
}
