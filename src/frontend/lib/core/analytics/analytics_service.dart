/// Fire-and-forget product analytics. One method; implementations decide where
/// events go ([NoopAnalyticsService] just logs, a Firebase impl lands in M6).
///
/// Call sites use the constants in `analytics_events.dart` — never a raw string.
abstract interface class AnalyticsService {
  /// Record [name] with optional [params]. Must never throw.
  void log(String name, [Map<String, Object?> params]);

  /// Set a sticky user dimension (e.g. dietary preference, plan tier).
  void setUserProperty(String name, String? value);
}
