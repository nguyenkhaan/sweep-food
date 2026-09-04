import 'dart:async';

import 'package:firebase_messaging/firebase_messaging.dart';
import 'package:flutter/foundation.dart';
import 'package:riverpod_annotation/riverpod_annotation.dart';
import 'package:sweepfood/app/router/app_router.dart';
import 'package:sweepfood/app/router/routes.dart';
import 'package:sweepfood/core/notifications/notification_providers.dart';
import 'package:sweepfood/core/storage/prefs.dart';
import 'package:sweepfood/core/utils/logger.dart';
import 'package:sweepfood/features/notifications/data/repositories/device_repository_impl.dart';

part 'push_registrar.g.dart';

/// Owns the FCM-token ↔ backend `/users/me/devices` lifecycle: obtain a token
/// once the user is signed in, register it, keep it fresh, route notification
/// taps, and unregister on sign-out.
///
/// Entirely best-effort — when FCM is disabled or unavailable every method is a
/// quiet no-op, so callers (SessionController) never branch on it.
@Riverpod(keepAlive: true)
PushRegistrar pushRegistrar(Ref ref) => PushRegistrar(ref);

class PushRegistrar {
  PushRegistrar(this._ref);

  final Ref _ref;

  static const _kDeviceId = 'push.deviceId';
  static const _kToken = 'push.token';

  StreamSubscription<String>? _tokenRefreshSub;
  StreamSubscription<RemoteMessage>? _onMessageSub;
  StreamSubscription<RemoteMessage>? _onOpenedSub;
  bool _listenersWired = false;

  String get _platform => switch (defaultTargetPlatform) {
        TargetPlatform.iOS => 'IOS',
        _ => kIsWeb ? 'WEB' : 'ANDROID',
      };

  /// Call after a session becomes active. Gets the token, registers it, and
  /// wires the message/token-refresh listeners (idempotent).
  Future<void> syncForSession() async {
    try {
      final fcm = _ref.read(fcmServiceProvider);
      final token = await fcm.getToken();
      if (token == null) return;
      await _registerToken(token);
      _wireListeners();
    } catch (e, st) {
      log.w('PushRegistrar.syncForSession failed', error: e, stackTrace: st);
    }
  }

  /// Call before signing out (while the access token is still valid).
  /// Best-effort — never throws, so it can't break the sign-out flow.
  Future<void> clear() async {
    await _tokenRefreshSub?.cancel();
    await _onMessageSub?.cancel();
    await _onOpenedSub?.cancel();
    _tokenRefreshSub = _onMessageSub = _onOpenedSub = null;
    _listenersWired = false;

    try {
      final prefs = _ref.read(sharedPreferencesProvider);
      final deviceId = prefs.getString(_kDeviceId);
      if (deviceId != null) {
        await _ref.read(deviceRepositoryProvider).unregister(deviceId);
      }
      await _ref.read(fcmServiceProvider).deleteToken();
      await prefs.remove(_kDeviceId);
      await prefs.remove(_kToken);
    } catch (e, st) {
      log.w('PushRegistrar.clear failed', error: e, stackTrace: st);
    }
  }

  Future<void> _registerToken(String token) async {
    final prefs = _ref.read(sharedPreferencesProvider);
    if (prefs.getString(_kToken) == token &&
        prefs.getString(_kDeviceId) != null) {
      return; // already registered with this exact token
    }
    final res = await _ref
        .read(deviceRepositoryProvider)
        .register(token, platform: _platform);
    res.fold(
      (f) => log.w('device register failed: ${f.message}'),
      (deviceId) async {
        log.i('FCM device registered ($deviceId)');
        await prefs.setString(_kDeviceId, deviceId);
        await prefs.setString(_kToken, token);
      },
    );
  }

  void _wireListeners() {
    if (_listenersWired) return;
    _listenersWired = true;
    final fcm = _ref.read(fcmServiceProvider);
    _tokenRefreshSub = fcm.onTokenRefresh.listen(_registerToken);
    _onMessageSub = fcm.onMessage.listen(_onForeground);
    _onOpenedSub = fcm.onMessageOpenedApp.listen(_onOpened);
    unawaited(
      fcm.getInitialMessage().then((m) {
        if (m != null) _onOpened(m);
      }),
    );
  }

  void _onForeground(RemoteMessage message) {
    final n = message.notification;
    if (n == null) return;
    unawaited(
      _ref.read(localNotificationsProvider).showPush(
            title: n.title ?? '',
            body: n.body ?? '',
            data: message.data.map((k, v) => MapEntry(k, v.toString())),
          ),
    );
  }

  void _onOpened(RemoteMessage message) {
    final data = message.data;
    final router = _ref.read(appRouterProvider);
    if (data['inventory_batch_id'] != null || data['pantry_item_id'] != null) {
      router.go(Routes.pantry);
    } else {
      router.go(Routes.notifications);
    }
  }
}
