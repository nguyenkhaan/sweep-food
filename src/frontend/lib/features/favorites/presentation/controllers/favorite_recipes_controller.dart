import 'package:riverpod_annotation/riverpod_annotation.dart';
import 'package:sweepfood/features/favorites/data/repositories/favorite_repository_impl.dart';
import 'package:sweepfood/features/favorites/domain/entities/favorite_recipe.dart';

part 'favorite_recipes_controller.g.dart';

@riverpod
class FavoriteRecipesController extends _$FavoriteRecipesController {
  @override
  Future<List<FavoriteRecipe>> build() async {
    final repo = ref.watch(favoriteRepositoryProvider);
    final res = await repo.fetchFavoriteRecipes();
    return res.fold(
      (f) => throw f,
      (recipes) => recipes,
    );
  }

  Future<void> addFavorite(String recipeId) async {
    final repo = ref.read(favoriteRepositoryProvider);
    final res = await repo.addFavoriteRecipe(recipeId);
    res.fold(
      (f) => throw f,
      (_) => ref.invalidateSelf(),
    );
  }

  Future<void> removeFavorite(String recipeId) async {
    final repo = ref.read(favoriteRepositoryProvider);
    final res = await repo.removeFavoriteRecipe(recipeId);
    res.fold(
      (f) => throw f,
      (_) => ref.invalidateSelf(),
    );
  }

  Future<bool> toggleFavorite(String recipeId) async {
    final currentList = state.asData?.value ?? [];
    final isFav = currentList.any((r) => r.recipeId == recipeId);
    if (isFav) {
      await removeFavorite(recipeId);
      return false;
    } else {
      await addFavorite(recipeId);
      return true;
    }
  }

  Future<void> refresh() => ref.refresh(favoriteRecipesControllerProvider.future);
}

@riverpod
bool isRecipeFavorite(Ref ref, String recipeId) {
  final recipes = ref.watch(favoriteRecipesControllerProvider).asData?.value;
  if (recipes == null) return false;
  return recipes.any((r) => r.recipeId == recipeId);
}
