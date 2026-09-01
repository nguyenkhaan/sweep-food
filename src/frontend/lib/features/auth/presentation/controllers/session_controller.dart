import 'package:riverpod_annotation/riverpod_annotation.dart';
import 'package:sweepfood/core/network/session_expired.dart';
import 'package:sweepfood/core/storage/storage_providers.dart';
import 'package:sweepfood/core/utils/logger.dart';
import 'package:sweepfood/features/auth/data/repositories/auth_repository_impl.dart';
import 'package:sweepfood/features/auth/domain/entities/session.dart';
import 'package:sweepfood/features/auth/domain/entities/user.dart';

part 'session_controller.g.dart';

/// App-wide auth state. `AsyncData(null)` = signed out, `AsyncData(session)` =
/// signed in, `AsyncLoading` = still reviving a persisted session (Splash).
///
/// The router watches this (via `route_guards.dart`) to gate every route. The
/// form controllers call in here and rethrow failures for the form to display —
/// this notifier only ever moves to a resolved state.
@Riverpod(keepAlive: true)
class SessionController extends _$SessionController {
  @override
  Future<Session?> build() async {
    // A refresh failure deep in the network stack → tear the session down.
    ref.listen(sessionExpiredProvider, (_, __) => _onExpired());

    final repo = ref.watch(authRepositoryProvider);
    if (!await repo.hasStoredSession()) return null;

    final res = await repo.me();
    return res.fold(
      (failure) {
        log.w('Session restore failed: ${failure.message}');
        return null;
      },
      (user) async {
        final store = ref.read(secureStoreProvider);
        return Session(
          user: user,
          accessToken: await store.readAccessToken() ?? '',
          refreshToken: await store.readRefreshToken() ?? '',
        );
      },
    );
  }

  Session? get currentSession => state.asData?.value;

  bool get isAuthenticated => currentSession != null;

  /// A-02. Sign in with phone + password. Rethrows the `Failure` for the form.
  Future<void> logIn({required String phone, required String password}) async {
    final res = await ref
        .read(authRepositoryProvider)
        .login(phone: phone, password: password);
    res.fold(
      (failure) => throw failure,
      (session) => state = AsyncData(session),
    );
  }

  /// A-03 step 2. Confirm the registration OTP and sign in with the credentials
  /// just entered. Rethrows the `Failure` for the OTP form.
  Future<void> verifyRegister({
    required String phone,
    required String otp,
    required String password,
  }) async {
    final res = await ref.read(authRepositoryProvider).verifyRegisterAndLogin(
          phone: phone,
          otp: otp,
          password: password,
        );
    res.fold(
      (failure) => throw failure,
      (session) => state = AsyncData(session),
    );
  }

  Future<void> logOut() async {
    await ref.read(authRepositoryProvider).logout();
    state = const AsyncData(null);
  }

  /// Swap the cached [User] on the live session after a profile / email / phone
  /// change. No-op when signed out.
  void applyUpdatedUser(User user) {
    final session = currentSession;
    if (session != null) {
      state = AsyncData(session.copyWith(user: user));
    }
  }

  /// Re-fetch `GET /users/profile` and refresh the cached user. Used after a
  /// verified email or phone change, where the server is the source of truth.
  Future<void> refreshProfile() async {
    final res = await ref.read(authRepositoryProvider).me();
    res.fold(
      (failure) => log.w('Profile refresh failed: ${failure.message}'),
      applyUpdatedUser,
    );
  }

  Future<void> _onExpired() async {
    await ref.read(secureStoreProvider).clear();
    state = const AsyncData(null);
  }
}
