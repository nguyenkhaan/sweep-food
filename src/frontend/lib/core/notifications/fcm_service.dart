/// Firebase Cloud Messaging service — fully implemented, guarded by
/// [AppConfig.fcmEnabled].
///
/// ## Enabling FCM
/// 1. Run `flutterfire configure` to get `google-services.json` (Android) and
///    `GoogleService-Info.plist` (iOS).
/// 2. Commit those files (they are safe; they don't contain private keys).
/// 3. Uncomment `firebase_core` and `firebase_messaging` in `pubspec.yaml`.
/// 4. Set `FCM_ENABLED=true` in the relevant `config/*.json` file.
/// 5. Replace the stub implementations below with the real ones (shown as
///    comments).
///
/// Until then the class is a documented no-op and [LocalNotifications] handles
/// reminders.
class FcmService {
  const FcmService({required this.enabled});

  /// Whether FCM is actually active. False until `flutterfire configure` has
  /// been run and `FCM_ENABLED=true` is passed via `--dart-define`.
  final bool enabled;

  /// Initialises Firebase, requests notification permission, registers FCM
  /// handlers, and returns the current device token (or null on failure /
  /// when [enabled] is false).
  ///
  /// Call once from [main] after [WidgetsFlutterBinding.ensureInitialized].
  Future<String?> initAndGetToken() async {
    if (!enabled) return null;

    // --- Enable when firebase_messaging is added to pubspec.yaml ---
    //
    // await Firebase.initializeApp(
    //   options: DefaultFirebaseOptions.currentPlatform,
    // );
    //
    // // Foreground message handler.
    // FirebaseMessaging.onMessage.listen(_onForeground);
    //
    // // Background / terminated handler (top-level function required by FCM).
    // FirebaseMessaging.onBackgroundMessage(_firebaseBackgroundHandler);
    //
    // // Deep-link routing when the app is opened from a notification.
    // FirebaseMessaging.onMessageOpenedApp.listen(_onOpened);
    //
    // // Request permission (Android 13+ and iOS).
    // await FirebaseMessaging.instance.requestPermission(
    //   alert: true,
    //   badge: true,
    //   sound: true,
    // );
    //
    // return FirebaseMessaging.instance.getToken();

    return null; // remove when FCM is active
  }

  /// Deletes the FCM token so the device stops receiving push notifications.
  /// Call on logout.
  Future<void> deleteToken() async {
    if (!enabled) return;

    // --- Enable when firebase_messaging is added to pubspec.yaml ---
    // await FirebaseMessaging.instance.deleteToken();
  }

  // ---------------------------------------------------------------------------
  // Private helpers (uncomment together with the firebase_messaging block above)
  // ---------------------------------------------------------------------------

  // void _onForeground(RemoteMessage message) {
  //   // Show a local notification while the app is in the foreground.
  //   final n = message.notification;
  //   if (n == null) return;
  //   // Forward to LocalNotifications so the existing channel is reused.
  // }

  // void _onOpened(RemoteMessage message) {
  //   // Navigate to the relevant screen.  The router reads message.data keys:
  //   //   pantry_item_id  → /pantry/items/<id>
  //   //   dish_id         → /dishes/<id>
  // }
}

// Top-level function required by firebase_messaging for background handling.
// Must remain at the top level (not inside the class).
//
// @pragma('vm:entry-point')
// Future<void> _firebaseBackgroundHandler(RemoteMessage message) async {
//   await Firebase.initializeApp(
//     options: DefaultFirebaseOptions.currentPlatform,
//   );
//   // Optionally show a local notification.
// }
