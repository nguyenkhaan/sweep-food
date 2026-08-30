import 'package:freezed_annotation/freezed_annotation.dart';
import 'package:frontend/core/utils/formatters/quantity_format.dart';
import 'package:frontend/shared/domain/measurement_unit.dart';

part 'dish_ingredient.freezed.dart';

/// One line in a recipe's ingredient list (D-01). Quantities are for the dish's
/// current serving count — [Dish.scaledTo] rebuilds these when servings change.
@freezed
abstract class DishIngredient with _$DishIngredient {
  const DishIngredient._();

  const factory DishIngredient({
    required String name,
    required double quantity,
    required MeasurementUnit unit,

    /// Salt / pepper / fish sauce — shown as chips, never "cần mua".
    @Default(false) bool isSeasoning,

    /// The kitchen already has enough of this.
    @Default(false) bool availableInPantry,

    /// How much still needs buying (0 when [availableInPantry]).
    @Default(0) double missingQty,

    /// The matching pantry batch is near its expiry date — drives the "cận hạn"
    /// tag and the `E` term of the suggestion score.
    @Default(false) bool nearExpiry,

    /// The pantry item this maps to, when matched.
    String? pantryItemId,
  }) = _DishIngredient;

  /// "200 g", "1 quả", "1 thìa".
  String get quantityLabel => formatQuantity(quantity, unit);

  /// "cần mua 150 g" for the checklist row.
  String get missingLabel => formatQuantity(missingQty, unit);
}
