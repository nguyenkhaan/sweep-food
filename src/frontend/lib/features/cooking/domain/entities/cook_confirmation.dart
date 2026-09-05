import 'package:sweepfood/l10n/app_localizations.dart';

/// How much stock to deduct when a dish is marked cooked (D-03). Matches the
/// backend's `CookingConsumptionMode`.
enum CookMode {
  exact('EXACT'),
  half('HALF'),
  all('USE_ALL_MATCHED'),
  custom('CUSTOM');

  const CookMode(this.wire);
  final String wire;

  String label(AppL10n l10n) => switch (this) {
    CookMode.exact => l10n.cookModeExact,
    CookMode.half => l10n.cookModeHalf,
    CookMode.all => l10n.cookModeAll,
    CookMode.custom => l10n.cookModeCustom,
  };

  String description(AppL10n l10n) => switch (this) {
    CookMode.exact => l10n.cookModeExactDesc,
    CookMode.half => l10n.cookModeHalfDesc,
    CookMode.all => l10n.cookModeAllDesc,
    CookMode.custom => l10n.cookModeCustomDesc,
  };
}

/// One line of `POST /cooking/sessions/{id}/complete`'s `consumptions` array —
/// only sent for [CookMode.custom] (quantity required there) and
/// [CookMode.all] doesn't need it at all; `EXACT`/`HALF` let the backend
/// compute from its own proposed deductions.
class ConsumptionLine {
  const ConsumptionLine({
    required this.recipeIngredientId,
    required this.batchId,
    this.quantity,
  });

  final String recipeIngredientId;
  final String batchId;
  final double? quantity;

  Map<String, dynamic> toBody() => {
        'recipe_ingredient_id': recipeIngredientId,
        'inventory_batch_id': batchId,
        if (quantity != null) 'quantity': quantity,
      };
}
