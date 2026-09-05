import 'package:sweepfood/core/utils/result.dart';
import 'package:sweepfood/features/shopping_list/domain/entities/shopping_list.dart';
import 'package:sweepfood/features/shopping_list/domain/entities/shopping_list_item.dart';
import 'package:sweepfood/features/shopping_list/domain/entities/shopping_purchase_draft.dart';

abstract interface class ShoppingListRepository {
  /// The backend has no "list all" / "active list" endpoint — this reads
  /// whichever list id was locally remembered from the last [generate] call,
  /// returning `null` when none exists yet.
  Future<Result<ShoppingList?>> current();

  /// `POST /shopping-lists/generate {meal_plan_id}` — remembers the returned
  /// list id locally for future [current] calls.
  Future<Result<ShoppingList>> generate({required String mealPlanId});

  /// `PATCH /shopping-lists/{listId}/items/{itemId} {checked, purchase?}`.
  /// [purchase] is required by the backend when checking an item (creates the
  /// resulting inventory batch) and must be omitted when un-checking.
  Future<Result<void>> setChecked({
    required String listId,
    required String itemId,
    required bool checked,
    ShoppingPurchaseDraft? purchase,
  });

  /// Add a manual line (B-02).
  Future<Result<ShoppingListItem>> addItem({
    required String listId,
    required ShoppingListItemDraft draft,
  });

  Future<Result<void>> removeItem({
    required String listId,
    required String itemId,
  });
}
