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

  // --- Account management (authenticated) ------------------------------------

  /// `PATCH /users/profile` — update the display name and/or preferences map.
  Future<UserProfileDto> updateProfile({
    String? name,
    Map<String, dynamic>? preferences,
  }) async {
    final json = await _api.patch(
      ApiPaths.profile,
      body: {
        if (name != null) 'name': name,
        if (preferences != null) 'preferences': preferences,
      },
    );
    return UserProfileDto.fromJson(json as Map<String, dynamic>);
  }

  /// `POST /auth/password/change` — authenticated; issues a `CHANGE_PASSWORD`
  /// OTP to the caller's phone. Returns `{ otp, expires_in_seconds }`.
  Future<OtpIssueDto> requestPasswordChange() async {
    final json = await _api.post(ApiPaths.passwordChange);
    return OtpIssueDto.fromJson(json as Map<String, dynamic>);
  }

  /// `POST /auth/verify/change-password` with `purpose: CHANGE_PASSWORD` —
  /// consumes [otp], sets [newPassword], and revokes sessions server-side.
  /// Plain-text / `{ message }` response — nothing to decode.
  Future<void> confirmPasswordChange({
    required String phone,
    required String otp,
    required String newPassword,
  }) =>
      _api.post(
        ApiPaths.verifyChangePassword,
        body: {
          'phone': phone,
          'otp': otp,
          'purpose': 'CHANGE_PASSWORD',
          'new_password': newPassword,
        },
      );

  /// `POST /users/me/email/request-verification` — sends an OTP to [email].
  Future<OtpIssueDto> requestEmailChange(String email) async {
    final json = await _api.post(
      ApiPaths.meEmailRequest,
      body: {'email': email},
    );
    return OtpIssueDto.fromJson(json as Map<String, dynamic>);
  }

  /// `POST /users/me/email/verify` — verifies [otp] for the pending email.
  /// Plain-text response — nothing to decode.
  Future<void> confirmEmailChange(String otp) =>
      _api.post(ApiPaths.meEmailVerify, body: {'otp': otp});

  /// `POST /users/me/phone/request-change` — sends an OTP to [phone] (E.164).
  Future<OtpIssueDto> requestPhoneChange(String phone) async {
    final json = await _api.post(
      ApiPaths.mePhoneRequest,
      body: {'phone': phone},
    );
    return OtpIssueDto.fromJson(json as Map<String, dynamic>);
  }

  /// `POST /users/me/phone/confirm-change` — verifies [otp] for the pending
  /// phone. Plain-text response — nothing to decode.
  Future<void> confirmPhoneChange(String otp) =>
      _api.post(ApiPaths.mePhoneConfirm, body: {'otp': otp});
}
