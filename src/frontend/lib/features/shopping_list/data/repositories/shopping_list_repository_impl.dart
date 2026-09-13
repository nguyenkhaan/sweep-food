import 'package:riverpod_annotation/riverpod_annotation.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:sweepfood/core/config/app_constants.dart';
import 'package:sweepfood/core/network/api_result.dart';
import 'package:sweepfood/core/network/network_providers.dart';
import 'package:sweepfood/core/storage/prefs.dart';
import 'package:sweepfood/core/utils/result.dart';
import 'package:sweepfood/features/shopping_list/data/datasources/shopping_list_remote_data_source.dart';
import 'package:sweepfood/features/shopping_list/domain/entities/shopping_list.dart';
import 'package:sweepfood/features/shopping_list/domain/entities/shopping_list_item.dart';
import 'package:sweepfood/features/shopping_list/domain/entities/shopping_purchase_draft.dart';
import 'package:sweepfood/features/shopping_list/domain/repositories/shopping_list_repository.dart';

part 'shopping_list_repository_impl.g.dart';

@Riverpod(keepAlive: true)
ShoppingListRepository shoppingListRepository(Ref ref) =>
    ShoppingListRepositoryImpl(
      ShoppingListRemoteDataSource(ref.watch(apiClientProvider)),
      ref.watch(sharedPreferencesProvider),
    );

class ShoppingListRepositoryImpl implements ShoppingListRepository {
  ShoppingListRepositoryImpl(this._remote, this._prefs);

  final ShoppingListRemoteDataSource _remote;
  final SharedPreferences _prefs;

  String? get _savedListId =>
      _prefs.getString(AppConstants.kActiveShoppingListId);

  @override
  Future<Result<ShoppingList?>> current() => runGuarded(() async {
        final id = _savedListId;
        if (id == null) return null;
        return (await _remote.getById(id)).toEntity();
      });

  @override
  Future<Result<ShoppingList>> generate({required String mealPlanId}) =>
      runGuarded(() async {
        final dto = await _remote.generate(mealPlanId: mealPlanId);
        await _prefs.setString(AppConstants.kActiveShoppingListId, dto.id);
        return dto.toEntity();
      });

  @override
  Future<Result<void>> setChecked({
    required String listId,
    required String itemId,
    required bool checked,
    ShoppingPurchaseDraft? purchase,
  }) =>
      guardVoid(() => _remote.setChecked(listId, itemId, checked, purchase));

  @override
  Future<Result<ShoppingListItem>> addItem({
    required String listId,
    required ShoppingListItemDraft draft,
  }) =>
      runGuarded(() async => (await _remote.addItem(listId, draft)).toEntity());

  @override
  Future<Result<void>> removeItem({
    required String listId,
    required String itemId,
  }) =>
      guardVoid(() => _remote.removeItem(listId, itemId));
}
