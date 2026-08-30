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

  String get label => switch (this) {
        StorageTier.eatSoon => 'Ăn liền / Nấu trong ngày',
        StorageTier.fridge => 'Ngăn mát',
        StorageTier.freezer => 'Ngăn đông',
        StorageTier.pantryShelf => 'Kệ đồ khô',
      };

  String get shortLabel => switch (this) {
        StorageTier.eatSoon => 'Ăn liền',
        StorageTier.fridge => 'Ngăn mát',
        StorageTier.freezer => 'Ngăn đông',
        StorageTier.pantryShelf => 'Kệ đồ khô',
      };

  /// Wire name (matches the API contract / mock fixtures).
  String get wire => name;

  static StorageTier fromWire(String value) => StorageTier.values.firstWhere(
        (t) => t.name == value,
        orElse: () => StorageTier.fridge,
      );
}
