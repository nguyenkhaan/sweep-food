import 'package:sweepfood/core/network/api_client.dart';
import 'package:sweepfood/core/network/api_paths.dart';
import 'package:sweepfood/core/utils/idempotency.dart';
import 'package:sweepfood/features/shopping_list/data/models/shopping_list_dto.dart';
import 'package:sweepfood/features/shopping_list/domain/entities/shopping_list_item.dart';
import 'package:sweepfood/features/shopping_list/domain/entities/shopping_purchase_draft.dart';

/// Talks to `/shopping-lists`. Throws on failure — the repository maps.
/// See `docs/api-contract.md` §8.
class ShoppingListRemoteDataSource {
  ShoppingListRemoteDataSource(this._api);

  final ApiClient _api;

  Future<ShoppingListDto> getById(String listId) async {
    final json = await _api.get(ApiPaths.shoppingList(listId));
    return ShoppingListDto.fromJson(json as Map<String, dynamic>);
  }

  Future<ShoppingListDto> generate({required String mealPlanId}) async {
    final json = await _api.post(
      ApiPaths.shoppingListsGenerate,
      body: {'meal_plan_id': mealPlanId},
      headers: _idempotencyHeaders(),
    );
    return ShoppingListDto.fromJson(json as Map<String, dynamic>);
  }

  /// `purchase` is required by the backend when [checked] is true and
  /// forbidden when false — the caller only passes [purchase] on the
  /// check-to-true transition (see `ShoppingListController.toggleChecked`).
  Future<void> setChecked(
    String listId,
    String itemId,
    bool checked,
    ShoppingPurchaseDraft? purchase,
  ) =>
      _api.patch(
        ApiPaths.shoppingListItem(listId, itemId),
        body: {
          'checked': checked,
          if (checked && purchase != null) 'purchase': purchase.toBody(),
        },
        headers: _idempotencyHeaders(),
      );

  Future<ShoppingListItemDto> addItem(
    String listId,
    ShoppingListItemDraft draft,
  ) async {
    final json = await _api.post(
      ApiPaths.shoppingListItems(listId),
      body: draft.toBody(),
      headers: _idempotencyHeaders(),
    );
    return ShoppingListItemDto.fromJson(json as Map<String, dynamic>);
  }

  Future<void> removeItem(String listId, String itemId) => _api.delete(
        ApiPaths.shoppingListItem(listId, itemId),
        headers: _idempotencyHeaders(),
      );

  Map<String, String> _idempotencyHeaders() =>
      {'Idempotency-Key': Idempotency.newKey()};
}
