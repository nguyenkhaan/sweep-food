import 'package:freezed_annotation/freezed_annotation.dart';
import 'package:sweepfood/core/utils/formatters/quantity_format.dart';
import 'package:sweepfood/shared/domain/measurement_unit.dart';

part 'shopping_list_item.freezed.dart';

/// One line on the shopping list (B-01). `alreadyInPantry` items are hidden by
/// default (the kitchen already has enough).
@freezed
abstract class ShoppingListItem with _$ShoppingListItem {
  const ShoppingListItem._();

  const factory ShoppingListItem({
    required String id,
    required String name,
    required double quantity,
    required MeasurementUnit unit,
    required String category,
    @Default(false) bool checked,
    @Default(false) bool alreadyInPantry,
    @Default(<String>[]) List<String> fromDishIds,
    @Default(true) bool isGenerated,
    int? estPriceVnd,
  }) = _ShoppingListItem;

  String get quantityLabel => formatQuantity(quantity, unit);

  /// Added through the manual "thêm món" flow rather than `generate` — the
  /// backend has no per-item recipe link for these (only generated items keep
  /// `source_recipe_ids`).
  bool get isManual => !isGenerated;
}

/// Write payload for "thêm món thủ công" (B-02). The backend's create-item
/// endpoint only accepts `custom_name`/`quantity`/`unit`/`estimated_cost` —
/// no category or recipe association (see IMPLEMENTATION_PLAN.md).
class ShoppingListItemDraft {
  const ShoppingListItemDraft({
    required this.name,
    required this.quantity,
    required this.unit,
    this.estPriceVnd,
  });

  final String name;
  final double quantity;
  final MeasurementUnit unit;
  final int? estPriceVnd;

  Map<String, dynamic> toBody() => {
        'custom_name': name.trim(),
        'quantity': quantity,
        'unit': unit.backendWire,
        if (estPriceVnd != null) 'estimated_cost': estPriceVnd,
      };
}
