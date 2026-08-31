import 'package:frontend/l10n/app_localizations.dart';

/// The user's meal-ranking preference (spec 6.3.4, N-01). Feeds the `P` term
/// of the suggestion score. Chosen at onboarding, editable in Cài đặt → Tùy chọn.
enum DietaryPreference {
  balanced('balanced'),
  highProtein('high_protein'),
  lowCalorie('low_calorie'),
  moreVeg('more_veg');

  const DietaryPreference(this.wire);
  final String wire;

  String label(AppL10n l10n) => switch (this) {
    DietaryPreference.balanced => l10n.dietBalanced,
    DietaryPreference.highProtein => l10n.dietHighProtein,
    DietaryPreference.lowCalorie => l10n.dietLowCalorie,
    DietaryPreference.moreVeg => l10n.dietMoreVeg,
  };

  String description(AppL10n l10n) => switch (this) {
    DietaryPreference.balanced => l10n.dietBalancedDesc,
    DietaryPreference.highProtein => l10n.dietHighProteinDesc,
    DietaryPreference.lowCalorie => l10n.dietLowCalorieDesc,
    DietaryPreference.moreVeg => l10n.dietMoreVegDesc,
  };

  static DietaryPreference fromWire(String? value) =>
      DietaryPreference.values.firstWhere(
        (p) => p.wire == value,
        orElse: () => DietaryPreference.balanced,
      );
}
