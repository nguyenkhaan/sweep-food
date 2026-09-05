import 'package:sweepfood/core/utils/result.dart';
import 'package:sweepfood/features/favorites/domain/entities/favorite_menu.dart';
import 'package:sweepfood/features/favorites/domain/entities/favorite_recipe.dart';

abstract interface class FavoriteRepository {
  /// Save a recipe as favorite (PUT /recipes/{recipe_id}/favorite).
  Future<Result<bool>> addFavoriteRecipe(String recipeId);

  /// Remove a recipe from favorites (DELETE /recipes/{recipe_id}/favorite).
  Future<Result<void>> removeFavoriteRecipe(String recipeId);

  /// List saved favorite recipes (GET /favorite-recipes).
  Future<Result<List<FavoriteRecipe>>> fetchFavoriteRecipes({
    int limit = 50,
    int offset = 0,
  });

  /// List owned favorite menus (GET /favorite-menus).
  Future<Result<List<FavoriteMenu>>> fetchFavoriteMenus({
    int limit = 50,
    int offset = 0,
  });

  /// Read one favorite menu with its items (GET /favorite-menus/{id}).
  Future<Result<FavoriteMenuDetail>> fetchFavoriteMenuDetail(String menuId);

  /// Create an empty favorite menu (POST /favorite-menus).
  Future<Result<FavoriteMenu>> createFavoriteMenu({
    required String name,
    String? description,
  });

  /// Update favorite menu name/description (PATCH /favorite-menus/{id}).
  Future<Result<FavoriteMenu>> updateFavoriteMenu(
    String menuId, {
    String? name,
    String? description,
  });

  /// Delete a favorite menu (DELETE /favorite-menus/{id}).
  Future<Result<void>> deleteFavoriteMenu(String menuId);

  /// Add a recipe to a favorite menu (POST /favorite-menus/{id}/items).
  Future<Result<FavoriteMenuItem>> addMenuItem(String menuId, String recipeId);

  /// Remove a recipe from a favorite menu (DELETE /favorite-menus/{id}/items/{item_id}).
  Future<Result<void>> removeMenuItem(String menuId, String itemId);
}
