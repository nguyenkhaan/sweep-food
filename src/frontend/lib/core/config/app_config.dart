import 'package:frontend/core/config/flavor.dart';

/// Immutable runtime configuration, read once from compile-time
/// `--dart-define` values (supplied via `--dart-define-from-file=config/<f>.json`).
///
/// Run the app with:
/// ```
/// flutter run --dart-define-from-file=config/dev.json
/// ```
class AppConfig {
  const AppConfig({
    required this.flavor,
    required this.backend,
    required this.apiBaseUrl,
    required this.premiumEnabled,
    required this.nearExpiryDays,
  });

  /// Reads the values baked in at build time. Falls back to dev/mock defaults
  /// so the app still boots if run without the dart-define file.
  factory AppConfig.fromEnvironment() {
    return AppConfig(
      flavor: Flavor.fromName(
        const String.fromEnvironment('FLAVOR', defaultValue: 'dev'),
      ),
      backend: Backend.fromName(
        const String.fromEnvironment('BACKEND', defaultValue: 'mock'),
      ),
      apiBaseUrl: const String.fromEnvironment(
        'API_BASE_URL',
        defaultValue: 'http://10.0.2.2:8000/api/v1',
      ),
      premiumEnabled: const bool.fromEnvironment('PREMIUM_ENABLED'),
      nearExpiryDays: const int.fromEnvironment(
        'NEAR_EXPIRY_DAYS',
        defaultValue: 3,
      ),
    );
  }

  final Flavor flavor;
  final Backend backend;
  final String apiBaseUrl;

  /// MVP: `false` — every feature is unlocked, no gating, no quotas.
  final bool premiumEnabled;

  /// An ingredient is "near expiry" when it expires within this many days.
  /// Used by suggestion scoring and the waste-reduction count.
  final int nearExpiryDays;

  @override
  String toString() =>
      'AppConfig(flavor: ${flavor.name}, backend: ${backend.name}, '
      'apiBaseUrl: $apiBaseUrl, premiumEnabled: $premiumEnabled, '
      'nearExpiryDays: $nearExpiryDays)';
}
