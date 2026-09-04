import 'package:firebase_core/firebase_core.dart';
import 'package:firebase_messaging/firebase_messaging.dart';
import 'package:flutter/foundation.dart';
import 'package:sweepfood/core/utils/logger.dart';

/// Thin wrapper over Firebase Cloud Messaging.
///
/// Android-only: the project ships `android/app/google-services.json` (no
/// `flutterfire configure`), so `Firebase.initializeApp()` is called with no
/// options and reads the native config. Every method is guarded — on web, or
/// when Firebase / Play Services are unavailable, calls become no-ops and
/// [getToken] returns `null` so the caller never has to special-case it.
///
/// This class knows nothing about the backend; [PushRegistrar] owns the
/// register/unregister lifecycle against `/users/me/devices`.
class FcmService {
  FcmService({required this.enabled});

  /// Mirrors `AppConfig.fcmEnabled`. When false the whole class is inert.
  final bool enabled;

  bool _initialised = false;

  bool get _usable => enabled && !kIsWeb;

  /// Initialise Firebase (once) and ask the OS for notification permission.
  /// Safe to call repeatedly.
  Future<void> initialize() async {
    if (!_usable || _initialised) return;
    try {
      if (Firebase.apps.isEmpty) {
        await Firebase.initializeApp();
      }
      await FirebaseMessaging.instance.requestPermission(
        alert: true,
        badge: true,
        sound: true,
      );
      await FirebaseMessaging.instance
          .setForegroundNotificationPresentationOptions(
        alert: true,
        badge: true,
        sound: true,
      );
      _initialised = true;
    } catch (e, st) {
      log.w('FcmService.initialize skipped', error: e, stackTrace: st);
    }
  }

  /// The current registration token, or `null` when unavailable.
  Future<String?> getToken() async {
    if (!_usable) return null;
    try {
      await initialize();
      return await FirebaseMessaging.instance.getToken();
    } catch (e) {
      log.w('FcmService.getToken failed: $e');
      return null;
    }
  }

  /// Emits a fresh token whenever FCM rotates it.
  Stream<String> get onTokenRefresh {
    if (!_usable) return const Stream<String>.empty();
    try {
      return FirebaseMessaging.instance.onTokenRefresh;
    } catch (_) {
      return const Stream<String>.empty();
    }
  }

  /// Messages received while the app is in the foreground.
  Stream<RemoteMessage> get onMessage {
    if (!_usable) return const Stream<RemoteMessage>.empty();
    return FirebaseMessaging.onMessage;
  }

  /// The user tapped a notification and the app was already running.
  Stream<RemoteMessage> get onMessageOpenedApp {
    if (!_usable) return const Stream<RemoteMessage>.empty();
    return FirebaseMessaging.onMessageOpenedApp;
  }

  /// The notification that cold-started the app, if any.
  Future<RemoteMessage?> getInitialMessage() async {
    if (!_usable) return null;
    try {
      await initialize();
      return await FirebaseMessaging.instance.getInitialMessage();
    } catch (e) {
      log.w('FcmService.getInitialMessage failed: $e');
      return null;
    }
  }

  /// Drop the token so the device stops receiving push (call on logout).
  Future<void> deleteToken() async {
    if (!_usable) return;
    try {
      await FirebaseMessaging.instance.deleteToken();
    } catch (e) {
      log.w('FcmService.deleteToken failed: $e');
    }
  }
}

/// Background / terminated message handler. Must be a top-level function and
/// carry the `vm:entry-point` pragma so the FCM isolate can find it.
@pragma('vm:entry-point')
Future<void> firebaseMessagingBackgroundHandler(RemoteMessage message) async {
  try {
    if (Firebase.apps.isEmpty) {
      await Firebase.initializeApp();
    }
  } catch (e) {
    log.w('background handler init failed: $e');
  }
  // Android renders `message.notification` on the default channel by itself;
  // nothing else to do here for the MVP.
}
