import 'dart:async';

import 'package:firebase_core/firebase_core.dart';
import 'package:firebase_messaging/firebase_messaging.dart';
import 'package:flutter/foundation.dart' show kIsWeb;
import 'package:flutter/widgets.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:sweepfood/app/app.dart';
import 'package:sweepfood/core/config/app_config.dart';
import 'package:sweepfood/core/config/app_config_provider.dart';
import 'package:sweepfood/core/notifications/fcm_service.dart';
import 'package:sweepfood/core/storage/prefs.dart';
import 'package:sweepfood/core/utils/logger.dart';

/// Single async entry: load what must exist before the first frame, then run
/// the app inside a guarded zone so uncaught errors are logged (not swallowed).
Future<void> bootstrap() async {
  await runZonedGuarded(
    () async {
      WidgetsFlutterBinding.ensureInitialized();

      final config = AppConfig.fromEnvironment();
      final prefs = await SharedPreferences.getInstance();

      log.i('Booting SweepFood — $config');

      await _initFirebase(config);

      FlutterError.onError = (details) {
        FlutterError.presentError(details);
        log.e('FlutterError', error: details.exception, stackTrace: details.stack);
      };

      runApp(
        ProviderScope(
          overrides: [
            appConfigProvider.overrideWithValue(config),
            sharedPreferencesProvider.overrideWithValue(prefs),
          ],
          child: const SweepFoodApp(),
        ),
      );
    },
    (error, stack) => log.e('Uncaught zone error', error: error, stackTrace: stack),
  );
}

/// Bring up Firebase and register the FCM background handler before the first
/// frame. Android reads `android/app/google-services.json`; web and disabled
/// builds skip it. Best-effort — a missing/invalid config must not block boot.
Future<void> _initFirebase(AppConfig config) async {
  if (kIsWeb || !config.fcmEnabled) return;
  try {
    if (Firebase.apps.isEmpty) {
      await Firebase.initializeApp();
    }
    FirebaseMessaging.onBackgroundMessage(firebaseMessagingBackgroundHandler);
  } catch (e, st) {
    log.w('Firebase init skipped', error: e, stackTrace: st);
  }
}
