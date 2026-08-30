import 'package:frontend/core/utils/result.dart';
import 'package:frontend/features/auth/domain/entities/session.dart';
import 'package:frontend/features/auth/domain/entities/user.dart';

/// Auth surface used by [SessionController] and the auth-form controllers.
///
/// Every method returns a [Result]; token persistence (`SecureStore`) is handled
/// inside the implementation so callers never touch storage directly.
abstract interface class AuthRepository {
  /// `POST /auth/register` → creates the account and signs it in.
  Future<Result<Session>> register({
    required String name,
    required String email,
    required String password,
  });

  /// `POST /auth/login`.
  Future<Result<Session>> login({
    required String email,
    required String password,
  });

  /// `GET /auth/me` — used on cold start to revive a persisted session.
  Future<Result<User>> me();

  /// `POST /auth/forgot-password` — always resolves for an existing email; the
  /// UI shows the same "đã gửi" state regardless (A-04).
  Future<Result<void>> requestPasswordReset(String email);

  /// `POST /auth/logout` (best-effort) then clears local tokens.
  Future<Result<void>> logout();

  /// Whether a persisted access token exists (no network call).
  Future<bool> hasStoredSession();
}
