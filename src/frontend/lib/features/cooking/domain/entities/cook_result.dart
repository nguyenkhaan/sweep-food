import 'package:freezed_annotation/freezed_annotation.dart';
import 'package:frontend/core/utils/formatters/quantity_format.dart';
import 'package:frontend/features/pantry/domain/entities/pantry_item.dart';
import 'package:frontend/shared/domain/measurement_unit.dart';

part 'cook_result.freezed.dart';

/// One "trước → sau" line on the cook-result screen (D-05).
@freezed
abstract class PantryChange with _$PantryChange {
  const PantryChange._();

  const factory PantryChange({
    required String name,
    required MeasurementUnit unit,
    required double before,
    required double after,
    @Default(false) bool nearExpiryUsed,
    String? pantryItemId,
  }) = _PantryChange;

  bool get depleted => after <= 0;

  /// After cooking there's a small amount left of a near-expiry ingredient.
  bool get lowAndUrgent => !depleted && nearExpiryUsed && after < before / 2;

  String get beforeLabel => formatQuantity(before, unit);
  String get afterLabel => formatQuantity(after, unit);
}

/// Result of `POST /dishes/{id}/cook` — what changed in the pantry plus the
/// waste-avoided feedback (D-05 / D-07). No money figure (spec: no price data).
@freezed
abstract class CookResult with _$CookResult {
  const CookResult._();

  const factory CookResult({
    @Default('') String dishId,
    @Default('') String dishName,
    @Default(<PantryChange>[]) List<PantryChange> changes,

    /// Post-cook state of the touched pantry items, for the list to splice in.
    @Default(<PantryItem>[]) List<PantryItem> updatedPantryItems,

    /// Ids of pantry items that dropped to zero and were marked used.
    @Default(<String>[]) List<String> depletedItemIds,

    @Default(0) int nearExpiryUsedCount,
    @Default(0) double wasteAvoidedGrams,

    /// Servings cooked but not eaten — offered as a leftover to save (D-06).
    @Default(0) int leftoverServings,
  }) = _CookResult;

  double get wasteAvoidedKg => wasteAvoidedGrams / 1000;

  List<String> get depletedNames =>
      [for (final c in changes) if (c.depleted) c.name];

  List<String> get lowStockNames =>
      [for (final c in changes) if (c.lowAndUrgent) c.name];
}
