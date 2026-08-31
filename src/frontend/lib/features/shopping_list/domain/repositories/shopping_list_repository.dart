import 'package:frontend/core/utils/result.dart';
import 'package:frontend/features/shopping_list/domain/entities/shopping_list.dart';
import 'package:frontend/features/shopping_list/domain/entities/shopping_list_item.dart';

abstract interface class ShoppingListRepository {
  /// The user's current list (`GET /shopping-lists`).
  Future<Result<ShoppingList>> current();

  /// `POST /shopping-lists/generate` from the given week / meal plan.
  Future<Result<ShoppingList>> generate({String? weekStart, String? mealPlanId});

  /// `PATCH /shopping-lists/{listId}/items/{itemId} {checked}`.
  Future<Result<void>> setChecked({
    required String listId,
    required String itemId,
    required bool checked,
  });

  /// Add a manual line (B-02) or the missing ingredients from a dish (D-01).
  Future<Result<ShoppingListItem>> addItem({
    required String listId,
    required ShoppingListItemDraft draft,
  });

  Future<Result<void>> removeItem({
    required String listId,
    required String itemId,
  });
}
