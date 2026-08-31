import 'package:frontend/l10n/app_localizations.dart';

/// The four pantry storage tiers (spec 6.3.2). Order = suggestion priority
/// (eatSoon first).
enum StorageTier {
  /// Ăn liền / Nấu trong ngày — highest priority in the dish scorer.
  eatSoon,

  /// Ngăn mát — reference shelf-life per food group.
  fridge,

  /// Ngăn đông.
  freezer,

  /// Kệ đồ khô — gia vị, đồ hộp, mì, ngũ cốc.
  pantryShelf;

  String label(AppL10n l10n) => switch (this) {
    StorageTier.eatSoon => l10n.tierEatSoon,
    StorageTier.fridge => l10n.tierFridge,
    StorageTier.freezer => l10n.tierFreezer,
    StorageTier.pantryShelf => l10n.tierPantryShelf,
  };

  String shortLabel(AppL10n l10n) => switch (this) {
    StorageTier.eatSoon => l10n.tierEatSoonShort,
    StorageTier.fridge => l10n.tierFridge,
    StorageTier.freezer => l10n.tierFreezer,
    StorageTier.pantryShelf => l10n.tierPantryShelf,
  };

  /// Wire name (matches the API contract / mock fixtures).
  String get wire => name;

  static StorageTier fromWire(String value) => StorageTier.values.firstWhere(
    (t) => t.name == value,
    orElse: () => StorageTier.fridge,
  );
}
