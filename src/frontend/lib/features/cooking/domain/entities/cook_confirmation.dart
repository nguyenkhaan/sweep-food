import 'package:sweepfood/l10n/app_localizations.dart';

/// How much stock to deduct when a dish is marked cooked (D-03).
enum CookMode {
  exact('exact'),
  half('half'),
  all('all'),
  custom('custom');

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

/// Body for `POST /dishes/{id}/cook`.
class CookConfirmation {
  const CookConfirmation({
    required this.dishId,
    required this.mode,
    required this.servingsCooked,
    this.customUsage = const {},
  });

  final String dishId;
  final CookMode mode;
  final int servingsCooked;

  /// Only for [CookMode.custom]: ingredient name → actual quantity used.
  final Map<String, double> customUsage;

  Map<String, dynamic> toBody() => {
    'mode': mode.wire,
    'servings_cooked': servingsCooked,
    if (mode == CookMode.custom) 'custom_usage': customUsage,
  };
}
