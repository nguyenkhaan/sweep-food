/// Analytics event names + param keys (spec §10). Keep every `analytics.log(...)`
/// call pointed at a constant here so the event taxonomy stays in one place.
abstract final class AnalyticsEvents {
  // Onboarding / activation
  static const onboardingCompleted = 'onboarding_completed';
  static const firstPantrySetupDone = 'first_pantry_setup_done';

  // Ingredient entry — `param.method` in {manual, label_scan, receipt_scan, voice}
  static const ingredientAdded = 'ingredient_added';
  static const ocrFieldEdited = 'ocr_field_edited';
  static const scanFailed = 'scan_failed';

  // Cooking loop
  static const dishOpened = 'dish_opened';
  static const dishCooked = 'dish_cooked';
  static const nearExpiryIngredientUsed = 'near_expiry_ingredient_used';

  // Shopping / planning
  static const shoppingListGenerated = 'shopping_list_generated';
  static const mealPlanEntryAdded = 'meal_plan_entry_added';

  // Notifications
  static const notificationOpened = 'notification_opened';
  static const notificationPermissionChanged = 'notification_permission_changed';

  // Monetisation
  static const paywallViewed = 'paywall_viewed';
  static const premiumInterestSubmitted = 'premium_interest_submitted';
}

/// Common param keys.
abstract final class AnalyticsParams {
  static const method = 'method';
  static const source = 'source';
  static const count = 'count';
  static const dishId = 'dish_id';
  static const field = 'field';
  static const plan = 'plan';
}

/// Sticky user-dimension keys.
abstract final class AnalyticsUserProps {
  static const dietaryPreference = 'dietary_preference';
  static const planTier = 'plan_tier';
}
