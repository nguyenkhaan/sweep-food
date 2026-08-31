import 'package:freezed_annotation/freezed_annotation.dart';
import 'package:frontend/core/utils/formatters/quantity_format.dart';
import 'package:frontend/shared/domain/measurement_unit.dart';

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
    int? estPriceVnd,
  }) = _ShoppingListItem;

  String get quantityLabel => formatQuantity(quantity, unit);

  bool get isManual => fromDishIds.isEmpty;
}

/// Write payload for "thêm món thủ công" (B-02) / "thêm phần thiếu" from D-01.
class ShoppingListItemDraft {
  const ShoppingListItemDraft({
    required this.name,
    required this.quantity,
    required this.unit,
    this.category = 'Khác',
    this.fromDishIds = const [],
  });

  final String name;
  final double quantity;
  final MeasurementUnit unit;
  final String category;
  final List<String> fromDishIds;

  Map<String, dynamic> toBody() => {
        'name': name.trim(),
        'quantity': quantity,
        'unit': unit.wire,
        'category': category,
        if (fromDishIds.isNotEmpty) 'from_dish_ids': fromDishIds,
      };
}
