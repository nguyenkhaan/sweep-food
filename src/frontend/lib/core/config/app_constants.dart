/// Non-secret, non-configurable constants.
abstract final class AppConstants {
  static const appName = 'SweepFood';

  static const connectTimeout = Duration(seconds: 20);
  static const receiveTimeout = Duration(seconds: 20);
  // OCR/ASR calls include cloud-model inference and legitimately take longer
  // than ordinary CRUD requests. Keep this above the backend's 60s ceiling.
  static const aiUploadReceiveTimeout = Duration(seconds: 75);

  /// Artificial latency added by [MockApiClient] so loading states are visible.
  static const mockLatency = Duration(milliseconds: 320);

  /// Default page size for paginated list endpoints.
  static const pageSize = 20;

  /// SweepFood AI currently returns up to seven feasibility-ranked dishes.
  static const maxSuggestions = 7;

  /// SharedPreferences keys.
  static const kThemeMode = 'pref.theme_mode';
  static const kLocale = 'pref.locale';
  static const kDietaryPreference = 'pref.dietary_preference';
  static const kDefaultUnit = 'pref.default_unit';
  static const kOnboardingDone = 'pref.onboarding_done';
  static const kNotificationPrefs = 'pref.notification_prefs';
  static const kMealPlanWeekStart = 'pref.meal_plan_week_start';

  /// The id from the last successful `generate` is remembered locally so the
  /// same list remains selected across app restarts.
  static const kActiveShoppingListId = 'pref.active_shopping_list_id';

  /// SecureStorage keys.
  static const kAccessToken = 'auth.access_token';
  static const kRefreshToken = 'auth.refresh_token';
}
