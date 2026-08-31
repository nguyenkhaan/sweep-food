import 'package:flutter_local_notifications/flutter_local_notifications.dart';
import 'package:riverpod_annotation/riverpod_annotation.dart';
import 'package:sweepfood/core/config/app_config_provider.dart';
import 'package:sweepfood/core/notifications/fcm_service.dart';
import 'package:sweepfood/core/notifications/local_notifications.dart';

part 'notification_providers.g.dart';

@Riverpod(keepAlive: true)
FlutterLocalNotificationsPlugin flutterLocalNotificationsPlugin(Ref ref) =>
    FlutterLocalNotificationsPlugin();

/// Local (on-device) notifications — the MVP reminder channel.
@Riverpod(keepAlive: true)
LocalNotifications localNotifications(Ref ref) =>
    LocalNotifications(ref.watch(flutterLocalNotificationsPluginProvider));

/// FCM service — active when config.fcmEnabled is true.
@Riverpod(keepAlive: true)
FcmService fcmService(Ref ref) {
  final config = ref.watch(appConfigProvider);
  return FcmService(enabled: config.fcmEnabled);
}

