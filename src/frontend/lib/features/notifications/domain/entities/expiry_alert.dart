import 'package:sweepfood/l10n/app_localizations.dart';

/// Storage advice shown in the near-expiry detail sheet (T-02). Category-keyed
/// copy — sourced from FoodKeeper-style guidance (see P-06).
abstract final class ExpiryTips {
  /// Keyword (matched against the lower-cased category) → l10n tip resolver.
  static const _keywords = ['rau', 'trái', 'thịt', 'cá', 'sữa', 'trứng'];

  static String _tipFor(String keyword, AppL10n l10n) => switch (keyword) {
    'rau' => l10n.expiryTipVeg,
    'trái' => l10n.expiryTipFruit,
    'thịt' => l10n.expiryTipMeat,
    'cá' => l10n.expiryTipFish,
    'sữa' => l10n.expiryTipDairy,
    'trứng' => l10n.expiryTipEgg,
    _ => l10n.expiryTipDefault,
  };

  /// A tip for [category]; falls back to a generic reminder.
  static String forCategory(String category, AppL10n l10n) {
    final c = category.toLowerCase();
    for (final k in _keywords) {
      if (c.contains(k)) return _tipFor(k, l10n);
    }
    return l10n.expiryTipDefault;
  }
}
