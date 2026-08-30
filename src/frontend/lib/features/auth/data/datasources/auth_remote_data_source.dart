import 'package:frontend/core/network/api_client.dart';
import 'package:frontend/core/network/api_paths.dart';
import 'package:frontend/features/auth/data/models/auth_dto.dart';

/// Talks to `/auth/*`. Throws on failure — the repository catches and maps.
///
/// All calls here set `skipAuth` so a stale/expired access token is never
/// attached to a login or refresh request.
class AuthRemoteDataSource {
  AuthRemoteDataSource(this._api);

  final ApiClient _api;

  Future<SessionDto> register({
    required String name,
    required String email,
    required String password,
  }) async {
    final json = await _api.post(
      ApiPaths.register,
      body: {'name': name.trim(), 'email': email.trim(), 'password': password},
    );
    return SessionDto.fromJson(json as Map<String, dynamic>);
  }

  Future<SessionDto> login({
    required String email,
    required String password,
  }) async {
    final json = await _api.post(
      ApiPaths.login,
      body: {'email': email.trim(), 'password': password},
    );
    return SessionDto.fromJson(json as Map<String, dynamic>);
  }

  Future<UserDto> me() async {
    final json = await _api.get(ApiPaths.me);
    return UserDto.fromJson(json as Map<String, dynamic>);
  }

  Future<void> requestPasswordReset(String email) =>
      _api.post(ApiPaths.forgotPassword, body: {'email': email.trim()});

  Future<void> logout(String? refreshToken) => _api.post(
        ApiPaths.logout,
        body: {if (refreshToken != null) 'refresh_token': refreshToken},
      );
}
