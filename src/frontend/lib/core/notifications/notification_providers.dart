import 'package:flutter_local_notifications/flutter_local_notifications.dart';
import 'package:frontend/core/notifications/fcm_service.dart';
import 'package:frontend/core/notifications/local_notifications.dart';
import 'package:riverpod_annotation/riverpod_annotation.dart';

part 'notification_providers.g.dart';

@Riverpod(keepAlive: true)
FlutterLocalNotificationsPlugin flutterLocalNotificationsPlugin(Ref ref) =>
    FlutterLocalNotificationsPlugin();

/// Local (on-device) notifications — the MVP reminder channel.
@Riverpod(keepAlive: true)
LocalNotifications localNotifications(Ref ref) =>
    LocalNotifications(ref.watch(flutterLocalNotificationsPluginProvider));

/// FCM — no-op until M6 (see [FcmService]).
@Riverpod(keepAlive: true)
FcmService fcmService(Ref ref) => const FcmService();
