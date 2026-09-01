import 'package:sweepfood/core/network/api_client.dart';
import 'package:sweepfood/core/network/api_paths.dart';
import 'package:sweepfood/features/shopping_list/data/models/shopping_list_dto.dart';
import 'package:sweepfood/features/shopping_list/domain/entities/shopping_list_item.dart';

/// Talks to `/shopping-lists`. Throws on failure — the repository maps.
class ShoppingListRemoteDataSource {
  ShoppingListRemoteDataSource(this._api);

  final ApiClient _api;

  Future<ShoppingListDto> current() async {
    final json = await _api.get(ApiPaths.shoppingLists);
    final map = json is List ? json.first : json;
    return ShoppingListDto.fromJson(map as Map<String, dynamic>);
  }

  Future<ShoppingListDto> generate({String? weekStart, String? mealPlanId}) async {
    final json = await _api.post(
      ApiPaths.shoppingListsGenerate,
      body: {
        if (weekStart != null) 'week_start': weekStart,
        if (mealPlanId != null) 'meal_plan_id': mealPlanId,
      },
    );
    return ShoppingListDto.fromJson(json as Map<String, dynamic>);
  }

  Future<void> setChecked(String listId, String itemId, bool checked) =>
      _api.patch(
        ApiPaths.shoppingListItem(listId, itemId),
        body: {'checked': checked},
      );

  Future<ShoppingListItemDto> addItem(
    String listId,
    ShoppingListItemDraft draft,
  ) async {
    final json = await _api.post(
      '${ApiPaths.shoppingList(listId)}/items',
      body: draft.toBody(),
    );
    return ShoppingListItemDto.fromJson(json as Map<String, dynamic>);
  }

  Future<void> removeItem(String listId, String itemId) =>
      _api.delete(ApiPaths.shoppingListItem(listId, itemId));
}
