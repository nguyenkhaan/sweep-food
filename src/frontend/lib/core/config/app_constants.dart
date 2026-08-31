/// Non-secret, non-configurable constants.
abstract final class AppConstants {
  static const appName = 'SweepFood';

  static const connectTimeout = Duration(seconds: 20);
  static const receiveTimeout = Duration(seconds: 20);

  /// Artificial latency added by [MockApiClient] so loading states are visible.
  static const mockLatency = Duration(milliseconds: 320);

  /// Default page size for paginated list endpoints.
  static const pageSize = 20;

  /// Max suggestions requested / shown at once (spec: 3–5 dishes).
  static const maxSuggestions = 5;

  /// SharedPreferences keys.
  static const kThemeMode = 'pref.theme_mode';
  static const kDietaryPreference = 'pref.dietary_preference';
  static const kDefaultUnit = 'pref.default_unit';
  static const kOnboardingDone = 'pref.onboarding_done';
  static const kNotificationPrefs = 'pref.notification_prefs';
  static const kMealPlanWeekStart = 'pref.meal_plan_week_start';

  /// SecureStorage keys.
  static const kAccessToken = 'auth.access_token';
  static const kRefreshToken = 'auth.refresh_token';
}
