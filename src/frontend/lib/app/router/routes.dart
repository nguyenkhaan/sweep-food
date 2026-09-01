/// Route paths + names. Keep every `context.go(...)` / `GoRoute(path:)` pointed
/// at a constant here — no string literals scattered around the app.
abstract final class Routes {
  // Auth / onboarding (wired in M5; dev-bypassed until then)
  static const splash = '/splash';
  static const welcome = '/welcome';
  static const login = '/login';
  static const register = '/register';
  static const verifyOtp = '/verify-otp';
  static const forgotPassword = '/forgot-password';
  static const resetPassword = '/reset-password';
  static const onboardingDiet = '/onboarding/diet';
  static const onboardingPantry = '/onboarding/pantry';

  // Bottom-nav tab roots
  static const home = '/home';
  static const pantry = '/pantry';
  static const suggestions = '/suggestions';
  static const shopping = '/shopping';
  static const profile = '/profile';

  // Pantry sub-routes
  static const pantryItem = 'item/:id'; // relative to /pantry
  static const addIngredient = 'add'; // relative to /pantry
  static const scanCamera = 'scan/camera'; // relative to /pantry
  static const scanLabelReview = 'scan/label-review';
  static const scanReceiptReview = 'scan/receipt-review';
  static const scanVoiceCapture = 'scan/voice-capture';
  static const scanVoiceReview = 'scan/voice-review';
  static const scanFailed = 'scan/failed';

  // Suggestions / dishes
  static const dish = 'dish/:id'; // relative to /suggestions

  // Misc pushed screens
  static const cookResult = '/cook-result';
  static const notifications = '/notifications';
  static const paywall = '/paywall';
  static const reports = '/reports';
  static const mealPlan = '/meal-plan';
  static const settingsPreferences = '/settings/preferences';
  static const settingsNotifications = '/settings/notifications';
  static const settingsPantrySharing = '/settings/pantry-sharing';
  static const settingsAbout = '/settings/about';
  static const settingsSubscription = '/settings/subscription';
  static const settingsProfile = '/settings/profile';
  static const settingsEditProfile = '/settings/profile/edit';
  static const settingsChangePassword = '/settings/profile/password';
  static const settingsChangeEmail = '/settings/profile/email';
  static const settingsChangePhone = '/settings/profile/phone';

  /// Where the router boots. [appRedirect] immediately routes on from here
  /// based on session + onboarding state.
  static const initialLocation = splash;
}
