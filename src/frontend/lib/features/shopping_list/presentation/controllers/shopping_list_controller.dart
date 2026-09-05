import 'package:riverpod_annotation/riverpod_annotation.dart';
import 'package:sweepfood/core/analytics/analytics_events.dart';
import 'package:sweepfood/core/analytics/analytics_provider.dart';
import 'package:sweepfood/core/utils/result.dart';
import 'package:sweepfood/features/dishes/domain/entities/dish.dart';
import 'package:sweepfood/features/shopping_list/data/repositories/shopping_list_repository_impl.dart';
import 'package:sweepfood/features/shopping_list/domain/entities/shopping_list.dart';
import 'package:sweepfood/features/shopping_list/domain/entities/shopping_list_item.dart';
import 'package:sweepfood/features/shopping_list/domain/entities/shopping_purchase_draft.dart';
import 'package:sweepfood/l10n/app_localizations.dart';

part 'shopping_list_controller.g.dart';

/// B-01 toggle: show the "đã có trong kho" lines or hide them (default hidden).
@riverpod
class ShoppingListShowInStock extends _$ShoppingListShowInStock {
  @override
  bool build() => false;
  void toggle() => state = !state;
}

/// B-01. The backend has no "current list" endpoint — [build] reads whichever
/// list id was locally remembered from the last successful [generateFromWeek]
/// call, and `null` when the user hasn't generated one yet (the screen shows
/// the same empty-state either way). Check-off / add / remove update
/// optimistically and roll back on failure.
@riverpod
class ShoppingListController extends _$ShoppingListController {
  @override
  Future<ShoppingList?> build() async {
    final res = await ref.watch(shoppingListRepositoryProvider).current();
    return res.fold((f) => throw f, (list) => list);
  }

  ShoppingList? get _list => state.asData?.value;

  Future<void> refresh() => ref.refresh(shoppingListControllerProvider.future);

  /// M-01's "Tạo danh sách mua sắm" button.
  Future<Result<ShoppingList>> generateFromWeek(String mealPlanId) async {
    final res = await ref
        .read(shoppingListRepositoryProvider)
        .generate(mealPlanId: mealPlanId);
    res.fold((_) {}, (list) => state = AsyncData(list));
    return res;
  }

  /// Checking an item requires [purchase] (the backend uses it to create the
  /// resulting inventory batch); un-checking must omit it. The caller decides
  /// which applies by checking `item.checked` before calling this.
  Future<void> toggleChecked(String itemId, {ShoppingPurchaseDraft? purchase}) async {
    final list = _list;
    if (list == null) return;
    final item = list.items.firstWhere((i) => i.id == itemId);
    final next = !item.checked;
    state = AsyncData(
      list.copyWith(
        items: [
          for (final i in list.items)
            i.id == itemId ? i.copyWith(checked: next) : i,
        ],
      ),
    );
    final res = await ref
        .read(shoppingListRepositoryProvider)
        .setChecked(
          listId: list.id,
          itemId: itemId,
          checked: next,
          purchase: next ? purchase : null,
        );
    res.fold((_) => ref.invalidateSelf(), (_) {});
  }

  Future<void> addManualItem(ShoppingListItemDraft draft) async {
    final list = _list;
    if (list == null) return;
    final res = await ref
        .read(shoppingListRepositoryProvider)
        .addItem(listId: list.id, draft: draft);
    res.fold(
      (_) => ref.invalidateSelf(),
      (item) => state = AsyncData(list.copyWith(items: [...list.items, item])),
    );
  }

  Future<void> removeItem(String itemId) async {
    final list = _list;
    if (list == null) return;
    state = AsyncData(
      list.copyWith(
        items: [
          for (final i in list.items)
            if (i.id != itemId) i,
        ],
      ),
    );
    final res = await ref
        .read(shoppingListRepositoryProvider)
        .removeItem(listId: list.id, itemId: itemId);
    res.fold((_) => ref.invalidateSelf(), (_) {});
  }

  /// D-01 "Thêm phần thiếu vào danh sách mua". Returns how many lines were
  /// added. Added lines lose their recipe association — the backend's manual
  /// add-item endpoint has no field for it (only `generate` produces
  /// `source_recipe_ids`).
  Future<int> addMissingFromDish(Dish dish, AppL10n l10n) async {
    final list = _list;
    if (list == null) return 0;
    final missing = dish.mainIngredients.where((i) => !i.availableInPantry);
    var added = 0;
    for (final ing in missing) {
      final qty = ing.missingQty > 0 ? ing.missingQty : ing.quantity;
      final res = await ref
          .read(shoppingListRepositoryProvider)
          .addItem(
            listId: list.id,
            draft: ShoppingListItemDraft(name: ing.name, quantity: qty, unit: ing.unit),
          );
      res.fold((_) {}, (item) {
        final cur = _list ?? list;
        state = AsyncData(cur.copyWith(items: [...cur.items, item]));
        added++;
      });
    }
    if (added > 0) {
      ref.read(analyticsProvider).log(AnalyticsEvents.shoppingListGenerated, {
        AnalyticsParams.dishId: dish.id,
        AnalyticsParams.count: added,
      });
    }
    return added;
  }
}
