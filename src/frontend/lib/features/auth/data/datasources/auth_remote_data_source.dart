import 'package:sweepfood/core/network/api_client.dart';
import 'package:sweepfood/core/network/api_paths.dart';
import 'package:sweepfood/features/auth/data/models/auth_dto.dart';

/// Talks to `/auth/*` and `/users/*`. Throws on failure — the repository
/// catches and maps via `error_mapper.dart`.
///
/// `AuthInterceptor` never runs its 401→refresh retry for `/auth/*` paths
/// (it treats them as the auth flow), so these calls can't recurse even though
/// a stale access token may be attached. `profile()` and `logout()` are the
/// authenticated calls.
class AuthRemoteDataSource {
  AuthRemoteDataSource(this._api);

  final ApiClient _api;

  /// `POST /auth/register` → `{ otp, expires_in_seconds }`.
  Future<OtpIssueDto> register({
    required String phone,
    required String password,
    String? name,
    String? email,
  }) async {
    final json = await _api.post(
      ApiPaths.register,
      body: {
        'phone': phone,
        'password': password,
        if (name != null && name.trim().isNotEmpty) 'name': name.trim(),
        if (email != null && email.trim().isNotEmpty) 'email': email.trim(),
      },
    );
    return OtpIssueDto.fromJson(json as Map<String, dynamic>);
  }

  /// `POST /auth/register/resend-otp`.
  Future<OtpIssueDto> resendRegisterOtp(String phone) async {
    final json = await _api.post(
      ApiPaths.registerResendOtp,
      body: {'phone': phone},
    );
    return OtpIssueDto.fromJson(json as Map<String, dynamic>);
  }

  /// `POST /auth/verify/register` — returns plain text, nothing to decode.
  Future<void> verifyRegister({
    required String phone,
    required String otp,
  }) =>
      _api.post(ApiPaths.verifyRegister, body: {'phone': phone, 'otp': otp});

  /// `POST /auth/login` → token pair (no user block).
  Future<TokenPairDto> login({
    required String phone,
    required String password,
  }) async {
    final json = await _api.post(
      ApiPaths.login,
      body: {'phone': phone, 'password': password},
    );
    return TokenPairDto.fromJson(json as Map<String, dynamic>);
  }

  /// `GET /users/profile`.
  Future<UserProfileDto> profile() async {
    final json = await _api.get(ApiPaths.profile);
    return UserProfileDto.fromJson(json as Map<String, dynamic>);
  }

  /// `POST /auth/password/reset` → `{ otp, expires_in_seconds }`.
  Future<OtpIssueDto> requestPasswordReset(String phone) async {
    final json = await _api.post(
      ApiPaths.passwordReset,
      body: {'phone': phone},
    );
    return OtpIssueDto.fromJson(json as Map<String, dynamic>);
  }

  /// `POST /auth/verify/change-password` with `purpose: RESET_PASSWORD`.
  Future<void> confirmPasswordReset({
    required String phone,
    required String otp,
    required String newPassword,
  }) =>
      _api.post(
        ApiPaths.verifyChangePassword,
        body: {
          'phone': phone,
          'otp': otp,
          'purpose': 'RESET_PASSWORD',
          'new_password': newPassword,
        },
      );

  /// `POST /auth/logout` — authenticated; revokes the given refresh session.
  Future<void> logout(String? refreshToken) => _api.post(
        ApiPaths.logout,
        body: {if (refreshToken != null) 'refresh_token': refreshToken},
      );
}
