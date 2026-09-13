import 'package:riverpod_annotation/riverpod_annotation.dart';
import 'package:sweepfood/core/network/api_result.dart';
import 'package:sweepfood/core/network/network_providers.dart';
import 'package:sweepfood/core/utils/result.dart';
import 'package:sweepfood/features/favorites/data/datasources/favorite_remote_data_source.dart';
import 'package:sweepfood/features/favorites/domain/entities/favorite_menu.dart';
import 'package:sweepfood/features/favorites/domain/entities/favorite_recipe.dart';
import 'package:sweepfood/features/favorites/domain/repositories/favorite_repository.dart';

part 'favorite_repository_impl.g.dart';

@Riverpod(keepAlive: true)
FavoriteRepository favoriteRepository(Ref ref) => FavoriteRepositoryImpl(
      FavoriteRemoteDataSource(ref.watch(apiClientProvider)),
    );

class FavoriteRepositoryImpl implements FavoriteRepository {
  FavoriteRepositoryImpl(this._remote);

  final FavoriteRemoteDataSource _remote;

  @override
  Future<Result<bool>> addFavoriteRecipe(String recipeId) =>
      runGuarded(() async {
        final dto = await _remote.addFavoriteRecipe(recipeId);
        return dto.isFavorite;
      });

  @override
  Future<Result<void>> removeFavoriteRecipe(String recipeId) =>
      guardVoid(() => _remote.removeFavoriteRecipe(recipeId));

  @override
  Future<Result<List<FavoriteRecipe>>> fetchFavoriteRecipes({
    int limit = 50,
    int offset = 0,
  }) =>
      runGuarded(() async {
        final dto = await _remote.getFavoriteRecipes(limit: limit, offset: offset);
        return dto.items.map((e) => e.toEntity()).toList();
      });

  @override
  Future<Result<List<FavoriteMenu>>> fetchFavoriteMenus({
    int limit = 50,
    int offset = 0,
  }) =>
      runGuarded(() async {
        final dto = await _remote.getFavoriteMenus(limit: limit, offset: offset);
        return dto.items.map((e) => e.toEntity()).toList();
      });

  @override
  Future<Result<FavoriteMenuDetail>> fetchFavoriteMenuDetail(String menuId) =>
      runGuarded(() async {
        final dto = await _remote.getFavoriteMenu(menuId);
        return dto.toEntity();
      });

  @override
  Future<Result<FavoriteMenu>> createFavoriteMenu({
    required String name,
    String? description,
  }) =>
      runGuarded(() async {
        final dto = await _remote.createFavoriteMenu(
          name: name,
          description: description,
        );
        return dto.toEntity();
      });

  @override
  Future<Result<FavoriteMenu>> updateFavoriteMenu(
    String menuId, {
    String? name,
    String? description,
  }) =>
      runGuarded(() async {
        final dto = await _remote.updateFavoriteMenu(
          menuId,
          name: name,
          description: description,
        );
        return dto.toEntity();
      });

  @override
  Future<Result<void>> deleteFavoriteMenu(String menuId) =>
      guardVoid(() => _remote.deleteFavoriteMenu(menuId));

  @override
  Future<Result<FavoriteMenuItem>> addMenuItem(
    String menuId,
    String recipeId,
  ) =>
      runGuarded(() async {
        final dto = await _remote.addMenuItem(menuId, recipeId);
        return dto.toEntity();
      });

  @override
  Future<Result<void>> removeMenuItem(String menuId, String itemId) =>
      guardVoid(() => _remote.removeMenuItem(menuId, itemId));
}
