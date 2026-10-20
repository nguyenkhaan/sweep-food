import 'dart:async';
import 'dart:convert';

import 'package:riverpod_annotation/riverpod_annotation.dart';
import 'package:sweepfood/core/network/session_expired.dart';
import 'package:sweepfood/core/notifications/push_registrar.dart';
import 'package:sweepfood/core/storage/prefs.dart';
import 'package:sweepfood/core/storage/storage_providers.dart';
import 'package:sweepfood/core/utils/logger.dart';
import 'package:sweepfood/features/auth/data/repositories/auth_repository_impl.dart';
import 'package:sweepfood/features/auth/domain/entities/session.dart';
import 'package:sweepfood/features/auth/domain/entities/user.dart';
import 'package:sweepfood/shared/domain/dietary_preference.dart';

part 'session_controller.g.dart';

/// App-wide auth state. `AsyncData(null)` = signed out, `AsyncData(session)` =
/// signed in, `AsyncLoading` = still reviving a persisted session (Splash).
///
/// The router watches this (via `route_guards.dart`) to gate every route. The
/// form controllers call in here and rethrow failures for the form to display —
/// this notifier only ever moves to a resolved state.
@Riverpod(keepAlive: true)
class SessionController extends _$SessionController {
  static const _cachedUserKey = 'auth.cached_user.v1';

  @override
  Future<Session?> build() async {
    // A refresh failure deep in the network stack → tear the session down.
    ref.listen(sessionExpiredProvider, (_, __) => _onExpired());

    final repo = ref.watch(authRepositoryProvider);
    if (!await repo.hasStoredSession()) return null;

    final store = ref.read(secureStoreProvider);
    final cachedUser = _readCachedUser();
    if (cachedUser != null) {
      final session = Session(
        user: cachedUser,
        accessToken: await store.readAccessToken() ?? '',
        refreshToken: await store.readRefreshToken() ?? '',
      );
      _syncPush();
      // Do not hold the first screen behind `/users/profile`. The cache makes
      // the session immediately usable; the server refreshes it afterwards.
      unawaited(Future<void>.delayed(Duration.zero, _refreshRestoredProfile));
      return session;
    }

    final res = await repo.me();
    return res.fold(
      (failure) {
        log.w('Session restore failed: ${failure.message}');
        return null;
      },
      (user) async {
        await _cacheUser(user);
        _syncPush();
        return Session(
          user: user,
          accessToken: await store.readAccessToken() ?? '',
          refreshToken: await store.readRefreshToken() ?? '',
        );
      },
    );
  }

  /// Fire-and-forget: register this device's FCM token with the backend. Never
  /// blocks or fails the auth flow.
  void _syncPush() {
    ref.read(pushRegistrarProvider).syncForSession();
  }

  Session? get currentSession => state.asData?.value;

  bool get isAuthenticated => currentSession != null;

  /// A-02. Sign in with phone + password. Rethrows the `Failure` for the form.
  Future<void> logIn({required String phone, required String password}) async {
    final res = await ref
        .read(authRepositoryProvider)
        .login(phone: phone, password: password);
    res.fold((failure) => throw failure, (session) {
      state = AsyncData(session);
      unawaited(_cacheUser(session.user));
      _syncPush();
    });
  }

  /// A-03 step 2. Confirm the registration OTP and sign in with the credentials
  /// just entered. Rethrows the `Failure` for the OTP form.
  Future<void> verifyRegister({
    required String phone,
    required String otp,
    required String password,
  }) async {
    final res = await ref
        .read(authRepositoryProvider)
        .verifyRegisterAndLogin(phone: phone, otp: otp, password: password);
    res.fold((failure) => throw failure, (session) {
      state = AsyncData(session);
      unawaited(_cacheUser(session.user));
      _syncPush();
    });
  }

  Future<void> logOut() async {
    // Unregister the device while the access token is still valid.
    await ref.read(pushRegistrarProvider).clear();
    await ref.read(authRepositoryProvider).logout();
    await ref.read(sharedPreferencesProvider).remove(_cachedUserKey);
    state = const AsyncData(null);
  }

  /// Swap the cached [User] on the live session after a profile / email / phone
  /// change. No-op when signed out.
  void applyUpdatedUser(User user) {
    final session = currentSession;
    if (session != null) {
      state = AsyncData(session.copyWith(user: user));
      unawaited(_cacheUser(user));
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
    await ref.read(pushRegistrarProvider).clear();
    await ref.read(secureStoreProvider).clear();
    await ref.read(sharedPreferencesProvider).remove(_cachedUserKey);
    state = const AsyncData(null);
  }

  Future<void> _refreshRestoredProfile() async {
    final res = await ref.read(authRepositoryProvider).me();
    res.fold(
      (failure) =>
          log.w('Background profile refresh failed: ${failure.message}'),
      (user) {
        applyUpdatedUser(user);
        unawaited(_cacheUser(user));
      },
    );
  }

  User? _readCachedUser() {
    final raw = ref.read(sharedPreferencesProvider).getString(_cachedUserKey);
    if (raw == null || raw.isEmpty) return null;
    try {
      final json = jsonDecode(raw) as Map<String, dynamic>;
      return User(
        id: json['id']?.toString() ?? '',
        phone: json['phone']?.toString() ?? '',
        name: json['name']?.toString(),
        email: json['email']?.toString(),
        dietaryPreference: json['dietary_preference'] == null
            ? null
            : DietaryPreference.fromWire(
                json['dietary_preference']?.toString(),
              ),
        avatarUrl: json['avatar_url']?.toString(),
      );
    } on Object {
      return null;
    }
  }

  Future<void> _cacheUser(User user) => ref
      .read(sharedPreferencesProvider)
      .setString(
        _cachedUserKey,
        jsonEncode({
          'id': user.id,
          'phone': user.phone,
          'name': user.name,
          'email': user.email,
          'dietary_preference': user.dietaryPreference?.wire,
          'avatar_url': user.avatarUrl,
        }),
      );
}
