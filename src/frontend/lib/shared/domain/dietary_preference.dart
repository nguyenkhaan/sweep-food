import 'package:sweepfood/l10n/app_localizations.dart';

/// The user's dietary mode stored in `users.preferences.diet`.
///
/// `vegetarian` acts as a hard filter (`an_chay`); the other four options act
/// as ranking preferences in SweepFood AI.
enum DietaryPreference {
  balanced('balanced'),
  highProtein('high_protein'),
  lowCalorie('low_calorie'),
  moreVeg('more_veg'),
  vegetarian('vegetarian');

  const DietaryPreference(this.wire);
  final String wire;

  bool get isHardFilter => this == DietaryPreference.vegetarian;

  String label(AppL10n l10n) => switch (this) {
    DietaryPreference.balanced => l10n.dietBalanced,
    DietaryPreference.highProtein => l10n.dietHighProtein,
    DietaryPreference.lowCalorie => l10n.dietLowCalorie,
    DietaryPreference.moreVeg => l10n.dietMoreVeg,
    DietaryPreference.vegetarian => l10n.dietVegetarian,
  };

  String description(AppL10n l10n) => switch (this) {
    DietaryPreference.balanced => l10n.dietBalancedDesc,
    DietaryPreference.highProtein => l10n.dietHighProteinDesc,
    DietaryPreference.lowCalorie => l10n.dietLowCalorieDesc,
    DietaryPreference.moreVeg => l10n.dietMoreVegDesc,
    DietaryPreference.vegetarian => l10n.dietVegetarianDesc,
  };

  static DietaryPreference fromWire(String? value) {
    final normalized = value?.trim().toLowerCase();
    return DietaryPreference.values.firstWhere(
      (p) => p.wire == normalized,
      orElse: () => DietaryPreference.balanced,
    );
  }
}
