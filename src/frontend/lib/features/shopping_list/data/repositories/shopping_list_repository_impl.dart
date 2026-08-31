import 'package:frontend/core/network/api_result.dart';
import 'package:frontend/core/network/network_providers.dart';
import 'package:frontend/core/utils/result.dart';
import 'package:frontend/features/shopping_list/data/datasources/shopping_list_remote_data_source.dart';
import 'package:frontend/features/shopping_list/domain/entities/shopping_list.dart';
import 'package:frontend/features/shopping_list/domain/entities/shopping_list_item.dart';
import 'package:frontend/features/shopping_list/domain/repositories/shopping_list_repository.dart';
import 'package:riverpod_annotation/riverpod_annotation.dart';

part 'shopping_list_repository_impl.g.dart';

@Riverpod(keepAlive: true)
ShoppingListRepository shoppingListRepository(Ref ref) =>
    ShoppingListRepositoryImpl(
      ShoppingListRemoteDataSource(ref.watch(apiClientProvider)),
    );

class ShoppingListRepositoryImpl implements ShoppingListRepository {
  ShoppingListRepositoryImpl(this._remote);

  final ShoppingListRemoteDataSource _remote;

  @override
  Future<Result<ShoppingList>> current() =>
      runGuarded(() async => (await _remote.current()).toEntity());

  @override
  Future<Result<ShoppingList>> generate({
    String? weekStart,
    String? mealPlanId,
  }) =>
      runGuarded(() async {
        final dto = await _remote.generate(
          weekStart: weekStart,
          mealPlanId: mealPlanId,
        );
        return dto.toEntity();
      });

  @override
  Future<Result<void>> setChecked({
    required String listId,
    required String itemId,
    required bool checked,
  }) =>
      guardVoid(() => _remote.setChecked(listId, itemId, checked));

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
