import 'package:freezed_annotation/freezed_annotation.dart';
import 'package:sweepfood/l10n/app_localizations.dart';
import 'package:sweepfood/shared/domain/expiry_status.dart';
import 'package:sweepfood/shared/domain/measurement_unit.dart';
import 'package:sweepfood/shared/domain/storage_tier.dart';

part 'pantry_item.freezed.dart';

/// How an item got into the pantry.
enum PantrySource {
  labelScan('label_scan'),
  receiptScan('receipt_scan'),
  voice('voice'),
  manual('manual'),
  cooked('cooked'); // leftover saved after cooking

  const PantrySource(this.wire);
  final String wire;

  static PantrySource fromWire(String? v) => PantrySource.values.firstWhere(
    (s) => s.wire == v,
    orElse: () => PantrySource.manual,
  );

  String label(AppL10n l10n) => switch (this) {
    PantrySource.labelScan => l10n.pantrySourceLabelScan,
    PantrySource.receiptScan => l10n.pantrySourceReceiptScan,
    PantrySource.voice => l10n.pantrySourceVoice,
    PantrySource.manual => l10n.pantrySourceManual,
    PantrySource.cooked => l10n.pantrySourceCooked,
  };
}

enum PantryItemStatus {
  active('active'),
  used('used'),
  expired('expired');

  const PantryItemStatus(this.wire);
  final String wire;

  static PantryItemStatus fromWire(String? v) => PantryItemStatus.values
      .firstWhere((s) => s.wire == v, orElse: () => PantryItemStatus.active);
}

/// One tracked pantry item (spec 6.3.2). Immutable; UI-facing.
@freezed
abstract class PantryItem with _$PantryItem {
  const PantryItem._();

  const factory PantryItem({
    required String id,
    required String name,
    required String category,
    required double quantity,
    required MeasurementUnit unit,
    required StorageTier storageTier,
    required DateTime addedAt,
    required PantrySource source,
    required PantryItemStatus status,
    String? ingredientId,
    DateTime? packedDate,
    DateTime? expiryDate,
    int? referenceShelfLifeDays,
    int? priceVnd,
  }) = _PantryItem;

  /// Whole days until [expiryDate] (date-only). Negative = past. `null` = no HSD.
  int? get daysUntilExpiry => Expiry.daysUntil(expiryDate);

  ExpiryLevel get expiryLevel => Expiry.levelFromDays(daysUntilExpiry);

  bool isNearExpiry({int threshold = 3}) =>
      Expiry.isNearExpiry(daysUntilExpiry, threshold: threshold);

  /// Lower = more urgent. Items in the "eat soon" tier get bumped up; items
  /// with no expiry sink to the bottom.
  double get priorityScore {
    final base = (daysUntilExpiry ?? 99999).toDouble();
    final tierBonus = storageTier == StorageTier.eatSoon ? -2.0 : 0.0;
    return base + tierBonus;
  }

  /// "500 g" / "1 bó" / "3 quả".
  String get quantityLabel {
    final n = quantity == quantity.roundToDouble()
        ? quantity.round().toString()
        : quantity.toStringAsFixed(1).replaceAll('.', ',');
    return '$n ${unit.label}';
  }

  /// "500 g · Rau củ" — the pantry-card subtitle.
  String get subtitle => '$quantityLabel · $category';
}
