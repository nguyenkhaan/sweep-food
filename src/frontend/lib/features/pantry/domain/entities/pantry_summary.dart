import 'package:freezed_annotation/freezed_annotation.dart';
import 'package:sweepfood/features/pantry/domain/entities/pantry_item.dart';
import 'package:sweepfood/shared/domain/storage_tier.dart';

part 'pantry_summary.freezed.dart';

/// `GET /pantry/summary` — drives the Home dashboard (H-01).
@freezed
abstract class PantrySummary with _$PantrySummary {
  const PantrySummary._();

  const factory PantrySummary({
    required int totalCount,
    required Map<StorageTier, int> countByTier,

    /// Items to surface in "Cần dùng sớm" (already sorted by urgency).
    required List<PantryItem> nearExpiry,

    /// Ingredients used before their expiry date this period — the number shown
    /// in the Home waste pill. (No money figure: scanning doesn't capture prices.)
    required int wasteReductionCount,
    double? wasteAvoidedKg,
  }) = _PantrySummary;

  int countFor(StorageTier tier) => countByTier[tier] ?? 0;

  bool get isEmpty => totalCount == 0;
}
