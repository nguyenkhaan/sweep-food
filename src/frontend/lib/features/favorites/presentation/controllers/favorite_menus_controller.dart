import 'package:riverpod_annotation/riverpod_annotation.dart';
import 'package:sweepfood/features/favorites/data/repositories/favorite_repository_impl.dart';
import 'package:sweepfood/features/favorites/domain/entities/favorite_menu.dart';

part 'favorite_menus_controller.g.dart';

@riverpod
class FavoriteMenusController extends _$FavoriteMenusController {
  @override
  Future<List<FavoriteMenu>> build() async {
    final repo = ref.watch(favoriteRepositoryProvider);
    final res = await repo.fetchFavoriteMenus();
    return res.fold(
      (f) => throw f,
      (menus) => menus,
    );
  }

  Future<FavoriteMenu> createMenu({required String name, String? description}) async {
    final repo = ref.read(favoriteRepositoryProvider);
    final res = await repo.createFavoriteMenu(name: name, description: description);
    return res.fold(
      (f) => throw f,
      (menu) {
        ref.invalidateSelf();
        return menu;
      },
    );
  }

  Future<void> updateMenu(String menuId, {String? name, String? description}) async {
    final repo = ref.read(favoriteRepositoryProvider);
    final res = await repo.updateFavoriteMenu(menuId, name: name, description: description);
    res.fold(
      (f) => throw f,
      (_) {
        ref.invalidateSelf();
        ref.invalidate(favoriteMenuDetailControllerProvider(menuId));
      },
    );
  }

  Future<void> deleteMenu(String menuId) async {
    final repo = ref.read(favoriteRepositoryProvider);
    final res = await repo.deleteFavoriteMenu(menuId);
    res.fold(
      (f) => throw f,
      (_) => ref.invalidateSelf(),
    );
  }

  Future<void> refresh() => ref.refresh(favoriteMenusControllerProvider.future);
}

@riverpod
class FavoriteMenuDetailController extends _$FavoriteMenuDetailController {
  @override
  Future<FavoriteMenuDetail> build(String menuId) async {
    final repo = ref.watch(favoriteRepositoryProvider);
    final res = await repo.fetchFavoriteMenuDetail(menuId);
    return res.fold(
      (f) => throw f,
      (detail) => detail,
    );
  }

  Future<void> addRecipe(String recipeId) async {
    final repo = ref.read(favoriteRepositoryProvider);
    final res = await repo.addMenuItem(menuId, recipeId);
    res.fold(
      (f) => throw f,
      (_) {
        ref.invalidateSelf();
        ref.invalidate(favoriteMenusControllerProvider);
      },
    );
  }

  Future<void> removeRecipe(String itemId) async {
    final repo = ref.read(favoriteRepositoryProvider);
    final res = await repo.removeMenuItem(menuId, itemId);
    res.fold(
      (f) => throw f,
      (_) {
        ref.invalidateSelf();
        ref.invalidate(favoriteMenusControllerProvider);
      },
    );
  }

  Future<void> refresh() =>
      ref.refresh(favoriteMenuDetailControllerProvider(menuId).future);
}
