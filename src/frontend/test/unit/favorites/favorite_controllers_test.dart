import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:mocktail/mocktail.dart';
import 'package:sweepfood/core/utils/result.dart';
import 'package:sweepfood/features/favorites/data/repositories/favorite_repository_impl.dart';
import 'package:sweepfood/features/favorites/domain/entities/favorite_menu.dart';
import 'package:sweepfood/features/favorites/domain/entities/favorite_recipe.dart';
import 'package:sweepfood/features/favorites/domain/repositories/favorite_repository.dart';
import 'package:sweepfood/features/favorites/presentation/controllers/favorite_menus_controller.dart';
import 'package:sweepfood/features/favorites/presentation/controllers/favorite_recipes_controller.dart';

class _MockFavoriteRepository extends Mock implements FavoriteRepository {}

void main() {
  late _MockFavoriteRepository repo;
  late ProviderContainer container;

  setUp(() {
    repo = _MockFavoriteRepository();
    container = ProviderContainer(
      overrides: [
        favoriteRepositoryProvider.overrideWithValue(repo),
      ],
    );
  });

  tearDown(() => container.dispose());

  group('FavoriteRecipesController', () {
    test('loads favorite recipes and toggles favorite', () async {
      final item = FavoriteRecipe(
        recipeId: 'rec-1',
        recipeName: 'Món 1',
        recipeDescription: '',
        mediaUrl: null,
        createdAt: DateTime(2026, 3, 1),
      );

      when(() => repo.fetchFavoriteRecipes())
          .thenAnswer((_) async => Right([item]));
      when(() => repo.removeFavoriteRecipe('rec-1'))
          .thenAnswer((_) async => const Right(null));
      when(() => repo.addFavoriteRecipe('rec-2'))
          .thenAnswer((_) async => const Right(true));

      final controller = container.read(favoriteRecipesControllerProvider.notifier);
      final list = await container.read(favoriteRecipesControllerProvider.future);
      expect(list.length, 1);
      expect(list.first.recipeId, 'rec-1');

      // Test isRecipeFavorite provider
      expect(container.read(isRecipeFavoriteProvider('rec-1')), isTrue);
      expect(container.read(isRecipeFavoriteProvider('rec-2')), isFalse);

      // Toggle off rec-1
      final removed = await controller.toggleFavorite('rec-1');
      expect(removed, isFalse);
      verify(() => repo.removeFavoriteRecipe('rec-1')).called(1);

      // Toggle on rec-2
      final added = await controller.toggleFavorite('rec-2');
      expect(added, isTrue);
      verify(() => repo.addFavoriteRecipe('rec-2')).called(1);
    });
  });

  group('FavoriteMenusController', () {
    test('loads menus, creates, updates and deletes menu', () async {
      final menu = FavoriteMenu(
        id: 'menu-1',
        name: 'Thực đơn 1',
        description: 'Mô tả',
        itemCount: 1,
        createdAt: DateTime(2026, 3, 1),
        updatedAt: DateTime(2026, 3, 1),
      );

      when(() => repo.fetchFavoriteMenus())
          .thenAnswer((_) async => Right([menu]));
      when(() => repo.createFavoriteMenu(name: 'Thực đơn 2', description: null))
          .thenAnswer((_) async => Right(menu.copyWith(id: 'menu-2', name: 'Thực đơn 2')));
      when(() => repo.updateFavoriteMenu('menu-1', name: 'Thực đơn mới', description: null))
          .thenAnswer((_) async => Right(menu.copyWith(name: 'Thực đơn mới')));
      when(() => repo.deleteFavoriteMenu('menu-1'))
          .thenAnswer((_) async => const Right(null));

      final controller = container.read(favoriteMenusControllerProvider.notifier);
      final menus = await container.read(favoriteMenusControllerProvider.future);
      expect(menus.length, 1);
      expect(menus.first.name, 'Thực đơn 1');

      // Create
      final created = await controller.createMenu(name: 'Thực đơn 2');
      expect(created.id, 'menu-2');
      verify(() => repo.createFavoriteMenu(name: 'Thực đơn 2', description: null)).called(1);

      // Update
      await controller.updateMenu('menu-1', name: 'Thực đơn mới');
      verify(() => repo.updateFavoriteMenu('menu-1', name: 'Thực đơn mới', description: null)).called(1);

      // Delete
      await controller.deleteMenu('menu-1');
      verify(() => repo.deleteFavoriteMenu('menu-1')).called(1);
    });
  });

  group('FavoriteMenuDetailController', () {
    test('loads detail, adds recipe and removes item', () async {
      final detail = FavoriteMenuDetail(
        id: 'menu-1',
        name: 'Thực đơn 1',
        description: 'Mô tả',
        items: [
          FavoriteMenuItem(
            id: 'item-1',
            recipeId: 'rec-1',
            recipeName: 'Món 1',
            recipeDescription: '',
            mediaUrl: null,
            createdAt: DateTime(2026, 3, 1),
          ),
        ],
        createdAt: DateTime(2026, 3, 1),
        updatedAt: DateTime(2026, 3, 1),
      );

      when(() => repo.fetchFavoriteMenuDetail('menu-1'))
          .thenAnswer((_) async => Right(detail));
      when(() => repo.addMenuItem('menu-1', 'rec-2'))
          .thenAnswer((_) async => Right(
                FavoriteMenuItem(
                  id: 'item-2',
                  recipeId: 'rec-2',
                  recipeName: 'Món 2',
                  recipeDescription: '',
                  mediaUrl: null,
                  createdAt: DateTime(2026, 3, 1),
                ),
              ));
      when(() => repo.removeMenuItem('menu-1', 'item-1'))
          .thenAnswer((_) async => const Right(null));

      final controller = container.read(favoriteMenuDetailControllerProvider('menu-1').notifier);
      final loadedDetail = await container.read(favoriteMenuDetailControllerProvider('menu-1').future);
      expect(loadedDetail.items.length, 1);

      // Add item
      await controller.addRecipe('rec-2');
      verify(() => repo.addMenuItem('menu-1', 'rec-2')).called(1);

      // Remove item
      await controller.removeRecipe('item-1');
      verify(() => repo.removeMenuItem('menu-1', 'item-1')).called(1);
    });
  });
}
