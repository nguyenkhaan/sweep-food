import 'package:freezed_annotation/freezed_annotation.dart';
import 'package:frontend/features/shopping_list/domain/entities/shopping_list_item.dart';

part 'shopping_list.freezed.dart';

/// B-01. Generated from the weekly meal plan, deduped against the pantry.
@freezed
abstract class ShoppingList with _$ShoppingList {
  const ShoppingList._();

  const factory ShoppingList({
    required String id,

    /// "Từ thực đơn tuần 09/09 – 15/09 · 8 món · đối chiếu với tủ bếp"
    String? sourceLabel,
    @Default(<ShoppingListItem>[]) List<ShoppingListItem> items,
  }) = _ShoppingList;

  /// Items still to buy (not already in the pantry).
  List<ShoppingListItem> get toBuy =>
      [for (final i in items) if (!i.alreadyInPantry) i];

  int get toBuyCount => toBuy.length;

  int get checkedCount => toBuy.where((i) => i.checked).length;

  int get estTotalVnd => toBuy
      .where((i) => !i.checked)
      .fold<int>(0, (sum, i) => sum + (i.estPriceVnd ?? 0));

  bool get hasPriceData => items.any((i) => i.estPriceVnd != null);

  /// Category → items, honouring [showInStock]. Insertion order follows first
  /// appearance so the UI stays stable.
  Map<String, List<ShoppingListItem>> grouped({required bool showInStock}) {
    final out = <String, List<ShoppingListItem>>{};
    for (final i in items) {
      if (!showInStock && i.alreadyInPantry) continue;
      out.putIfAbsent(i.category, () => []).add(i);
    }
    return out;
  }
}
