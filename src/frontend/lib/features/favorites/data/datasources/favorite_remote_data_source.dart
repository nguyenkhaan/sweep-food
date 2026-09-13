import 'package:sweepfood/core/network/api_client.dart';
import 'package:sweepfood/core/network/api_paths.dart';
import 'package:sweepfood/features/favorites/data/models/favorite_dto.dart';

class FavoriteRemoteDataSource {
  FavoriteRemoteDataSource(this._api);

  final ApiClient _api;

  Future<FavoriteRecipeDto> addFavoriteRecipe(String recipeId) async {
    final json = await _api.put(ApiPaths.recipeFavorite(recipeId));
    return FavoriteRecipeDto.fromJson(json as Map<String, dynamic>);
  }

  Future<void> removeFavoriteRecipe(String recipeId) async {
    await _api.delete(ApiPaths.recipeFavorite(recipeId));
  }

  Future<FavoriteRecipeListDto> getFavoriteRecipes({
    int limit = 50,
    int offset = 0,
  }) async {
    final json = await _api.get(
      ApiPaths.favoriteRecipes,
      query: {'limit': limit, 'offset': offset},
    );
    return FavoriteRecipeListDto.fromJson(json as Map<String, dynamic>);
  }

  Future<FavoriteMenuListDto> getFavoriteMenus({
    int limit = 50,
    int offset = 0,
  }) async {
    final json = await _api.get(
      ApiPaths.favoriteMenus,
      query: {'limit': limit, 'offset': offset},
    );
    return FavoriteMenuListDto.fromJson(json as Map<String, dynamic>);
  }

  Future<FavoriteMenuDetailDto> getFavoriteMenu(String menuId) async {
    final json = await _api.get(ApiPaths.favoriteMenu(menuId));
    return FavoriteMenuDetailDto.fromJson(json as Map<String, dynamic>);
  }

  Future<FavoriteMenuDto> createFavoriteMenu({
    required String name,
    String? description,
  }) async {
    final json = await _api.post(
      ApiPaths.favoriteMenus,
      body: {
        'name': name,
        if (description != null) 'description': description,
      },
    );
    return FavoriteMenuDto.fromJson(json as Map<String, dynamic>);
  }

  Future<FavoriteMenuDto> updateFavoriteMenu(
    String menuId, {
    String? name,
    String? description,
  }) async {
    final json = await _api.patch(
      ApiPaths.favoriteMenu(menuId),
      body: {
        if (name != null) 'name': name,
        if (description != null) 'description': description,
      },
    );
    return FavoriteMenuDto.fromJson(json as Map<String, dynamic>);
  }

  Future<void> deleteFavoriteMenu(String menuId) async {
    await _api.delete(ApiPaths.favoriteMenu(menuId));
  }

  Future<FavoriteMenuItemDto> addMenuItem(String menuId, String recipeId) async {
    final json = await _api.post(
      ApiPaths.favoriteMenuItems(menuId),
      body: {'recipe_id': recipeId},
    );
    return FavoriteMenuItemDto.fromJson(json as Map<String, dynamic>);
  }

  Future<void> removeMenuItem(String menuId, String itemId) async {
    await _api.delete(ApiPaths.favoriteMenuItem(menuId, itemId));
  }
}
