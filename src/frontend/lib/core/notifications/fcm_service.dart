/// Firebase Cloud Messaging — **deferred to M6** (needs a Firebase project +
/// `flutterfire configure`). Kept as a no-op so call sites and DI wiring can be
/// written now; `LocalNotifications` covers reminders in the meantime.
class FcmService {
  const FcmService();

  /// Would register FCM handlers and return the device token. No-op today.
  Future<String?> initAndGetToken() async => null;

  /// Would unregister the device token on logout. No-op today.
  Future<void> deleteToken() async {}
}
