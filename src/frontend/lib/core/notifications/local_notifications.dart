import 'package:flutter/foundation.dart';
import 'package:flutter_local_notifications/flutter_local_notifications.dart';
import 'package:frontend/core/utils/logger.dart';
import 'package:frontend/features/settings/domain/entities/notification_preferences.dart';

/// Thin wrapper over `flutter_local_notifications`. In the MVP this is how the
/// near-expiry reminders reach the user — there's no server push (FCM is
/// deferred to M6, see [fcmServiceProvider]).
///
/// Every call is guarded: no-op on web, swallow-and-log on platforms where the
/// plugin isn't available so callers never have to care.
class LocalNotifications {
  LocalNotifications(this._plugin);

  final FlutterLocalNotificationsPlugin _plugin;
  bool _ready = false;

  static const _channelId = 'sweepfood_expiry';
  static const _channelName = 'Nhắc hạn sử dụng';
  static const _nearExpiryDigestId = 1001;

  NotificationDetails get _details => const NotificationDetails(
        android: AndroidNotificationDetails(
          _channelId,
          _channelName,
          channelDescription: 'Nhắc nguyên liệu sắp hết hạn',
          importance: Importance.defaultImportance,
          priority: Priority.defaultPriority,
        ),
        iOS: DarwinNotificationDetails(),
      );

  Future<void> init() async {
    if (kIsWeb || _ready) return;
    try {
      const settings = InitializationSettings(
        android: AndroidInitializationSettings('@mipmap/ic_launcher'),
        iOS: DarwinInitializationSettings(),
      );
      await _plugin.initialize(settings);
      _ready = true;
    } catch (e, st) {
      log.w('LocalNotifications.init skipped', error: e, stackTrace: st);
    }
  }

  /// Ask the OS for permission (primed by G-04 before this is called).
  Future<bool> requestPermission() async {
    if (kIsWeb) return false;
    try {
      final ios = await _plugin
          .resolvePlatformSpecificImplementation<
              IOSFlutterLocalNotificationsPlugin>()
          ?.requestPermissions(alert: true, badge: true, sound: true);
      final android = await _plugin
          .resolvePlatformSpecificImplementation<
              AndroidFlutterLocalNotificationsPlugin>()
          ?.requestNotificationsPermission();
      return ios ?? android ?? false;
    } catch (e) {
      log.w('requestPermission failed: $e');
      return false;
    }
  }

  /// Fire an immediate near-expiry alert (used when the app spots an item that
  /// needs using today). Tapping it deep-links via [payload].
  Future<void> showExpiryAlert({
    required String pantryItemId,
    required String title,
    required String body,
  }) async {
    if (kIsWeb) return;
    try {
      await _plugin.show(
        pantryItemId.hashCode,
        title,
        body,
        _details,
        payload: 'pantry_item:$pantryItemId',
      );
    } catch (e) {
      log.w('showExpiryAlert failed: $e');
    }
  }

  /// Re-arm the recurring near-expiry digest from [prefs].
  ///
  /// MVP: cancels the existing schedule and logs the intent. Exact-time daily
  /// delivery (at `prefs.nearExpiryHour`, respecting the DND window) needs
  /// `timezone` bootstrapping and is finished in M6 with on-device testing.
  Future<void> syncFromPreferences(NotificationPreferences prefs) async {
    if (kIsWeb) return;
    try {
      await _plugin.cancel(_nearExpiryDigestId);
      log.d(
        prefs.nearExpiry
            ? 'Near-expiry digest armed for ${prefs.nearExpiryTimeLabel} '
                '(DND ${prefs.dndWindowLabel})'
            : 'Near-expiry digest disabled',
      );
    } catch (e) {
      log.w('syncFromPreferences failed: $e');
    }
  }
}
