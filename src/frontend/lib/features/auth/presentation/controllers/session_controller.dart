import 'package:riverpod_annotation/riverpod_annotation.dart';
import 'package:sweepfood/core/network/session_expired.dart';
import 'package:sweepfood/core/storage/storage_providers.dart';
import 'package:sweepfood/core/utils/logger.dart';
import 'package:sweepfood/features/auth/data/repositories/auth_repository_impl.dart';
import 'package:sweepfood/features/auth/domain/entities/session.dart';

part 'session_controller.g.dart';

/// App-wide auth state. `AsyncData(null)` = signed out, `AsyncData(session)` =
/// signed in, `AsyncLoading` = still reviving a persisted session (Splash).
///
/// The router watches this (via `route_guards.dart`) to gate every route. The
/// form controllers (`login`/`register`) call in here and rethrow failures for
/// the form to display — this notifier only ever moves to a resolved state.
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

  Future<void> logIn({required String email, required String password}) async {
    final res = await ref
        .read(authRepositoryProvider)
        .login(email: email, password: password);
    res.fold(
      (failure) => throw failure,
      (session) => state = AsyncData(session),
    );
  }

  Future<void> register({
    required String name,
    required String email,
    required String password,
  }) async {
    final res = await ref.read(authRepositoryProvider).register(
          name: name,
          email: email,
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

  Future<void> _onExpired() async {
    await ref.read(secureStoreProvider).clear();
    state = const AsyncData(null);
  }
}
