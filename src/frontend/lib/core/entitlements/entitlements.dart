/// What the current user is allowed to do. In the MVP every field is unlimited
/// / enabled (see [Entitlements.allUnlocked]); the shape is kept so real gating
/// can be switched on later without touching call sites.
class Entitlements {
  const Entitlements({
    required this.maxActiveIngredients,
    required this.scansPerMonth,
    required this.weeklyPlanner,
    required this.nutritionGoals,
    required this.reports,
    required this.pantrySharing,
    required this.dishHistory,
    required this.customReminders,
  });

  /// `null` = unlimited.
  final int? maxActiveIngredients;
  final int? scansPerMonth;

  final bool weeklyPlanner;
  final bool nutritionGoals;
  final bool reports;
  final bool pantrySharing;
  final bool dishHistory;
  final bool customReminders;

  static const allUnlocked = Entitlements(
    maxActiveIngredients: null,
    scansPerMonth: null,
    weeklyPlanner: true,
    nutritionGoals: true,
    reports: true,
    pantrySharing: true,
    dishHistory: true,
    customReminders: true,
  );

  /// The v2 free tier (spec 12.1) — kept for reference; not used while
  /// `kPremiumEnabled == false`.
  static const freeTier = Entitlements(
    maxActiveIngredients: 40,
    scansPerMonth: 10,
    weeklyPlanner: false,
    nutritionGoals: false,
    reports: false,
    pantrySharing: false,
    dishHistory: false,
    customReminders: false,
  );

  bool get hasUnlimitedIngredients => maxActiveIngredients == null;
  bool get hasUnlimitedScans => scansPerMonth == null;
}

/// A gateable capability.
enum Feature {
  ingredientQuota,
  scanQuota,
  weeklyPlanner,
  nutritionGoals,
  reports,
  pantrySharing,
  dishHistory,
  customReminders,
}
