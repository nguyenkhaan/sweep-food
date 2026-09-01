import 'package:sweepfood/core/utils/result.dart';
import 'package:sweepfood/features/auth/domain/entities/session.dart';
import 'package:sweepfood/features/auth/domain/entities/user.dart';

/// Auth surface used by [SessionController] and the auth-form controllers.
///
/// Backend flow (`docs/api-contract.md` §1): phone + password + OTP. Sign-up is
/// two steps — [register] issues an OTP, [verifyRegisterAndLogin] confirms it
/// and signs the user in. Every method returns a [Result]; token persistence
/// (`SecureStore`) is handled inside the implementation.
abstract interface class AuthRepository {
  /// `POST /auth/register` — creates an `UNVERIFIED` account and sends an OTP.
  /// Returns the OTP lifetime in seconds. No session is created yet.
  Future<Result<int>> register({
    required String phone,
    required String password,
    String? name,
    String? email,
  });

  /// `POST /auth/register/resend-otp` — new OTP for an unverified account.
  /// Returns the OTP lifetime in seconds.
  Future<Result<int>> resendRegisterOtp(String phone);

  /// `POST /auth/verify/register` then `POST /auth/login` — activates the
  /// account with [otp] and immediately signs in with [phone] + [password].
  Future<Result<Session>> verifyRegisterAndLogin({
    required String phone,
    required String otp,
    required String password,
  });

  /// `POST /auth/login`.
  Future<Result<Session>> login({
    required String phone,
    required String password,
  });

  /// `GET /users/profile` — used on cold start to revive a persisted session.
  Future<Result<User>> me();

  /// `POST /auth/password/reset` — sends a reset OTP. Always resolves (the
  /// backend never reveals whether the number exists). Returns OTP lifetime (s).
  Future<Result<int>> requestPasswordReset(String phone);

  /// `POST /auth/verify/change-password` with `purpose: RESET_PASSWORD` —
  /// consumes [otp] and sets [newPassword].
  Future<Result<void>> confirmPasswordReset({
    required String phone,
    required String otp,
    required String newPassword,
  });

  /// `POST /auth/logout` (best-effort) then clears local tokens.
  Future<Result<void>> logout();

  /// Whether a persisted access token exists (no network call).
  Future<bool> hasStoredSession();

  // --- Account management (authenticated) ----------------------------------

  /// `PATCH /users/profile` — update the display name and/or preferences.
  /// Returns the refreshed [User].
  Future<Result<User>> updateProfile({
    String? name,
    Map<String, dynamic>? preferences,
  });

  /// `POST /auth/password/change` — sends a `CHANGE_PASSWORD` OTP to the
  /// signed-in user's phone. Returns the OTP lifetime in seconds.
  Future<Result<int>> requestPasswordChange();

  /// `POST /auth/verify/change-password` with `purpose: CHANGE_PASSWORD` —
  /// consumes [otp], sets [newPassword], and revokes every session server-side
  /// (the caller must sign in again afterwards).
  Future<Result<void>> confirmPasswordChange({
    required String phone,
    required String otp,
    required String newPassword,
  });

  /// `POST /users/me/email/request-verification` — sends an OTP to [email].
  /// Returns the OTP lifetime in seconds.
  Future<Result<int>> requestEmailChange(String email);

  /// `POST /users/me/email/verify` — verifies [otp] for the pending email.
  Future<Result<void>> confirmEmailChange(String otp);

  /// `POST /users/me/phone/request-change` — sends an OTP to [phone] (E.164).
  /// Returns the OTP lifetime in seconds.
  Future<Result<int>> requestPhoneChange(String phone);

  /// `POST /users/me/phone/confirm-change` — verifies [otp] for the pending
  /// phone number.
  Future<Result<void>> confirmPhoneChange(String otp);
}
