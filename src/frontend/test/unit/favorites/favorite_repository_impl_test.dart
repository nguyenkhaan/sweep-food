import 'package:flutter_test/flutter_test.dart';
import 'package:mocktail/mocktail.dart';
import 'package:sweepfood/core/network/api_client.dart';
import 'package:sweepfood/core/network/api_paths.dart';
import 'package:sweepfood/core/utils/result.dart';
import 'package:sweepfood/features/favorites/data/datasources/favorite_remote_data_source.dart';
import 'package:sweepfood/features/favorites/data/repositories/favorite_repository_impl.dart';

class _MockApiClient extends Mock implements ApiClient {}

void main() {
  late _MockApiClient api;
  late FavoriteRepositoryImpl repo;

  setUp(() {
    api = _MockApiClient();
    repo = FavoriteRepositoryImpl(FavoriteRemoteDataSource(api));
  });

  group('FavoriteRepositoryImpl - Recipe Favorites', () {
    test('addFavoriteRecipe puts to recipeFavorite path and returns true', () async {
      when(() => api.put(ApiPaths.recipeFavorite('r-1')))
          .thenAnswer((_) async => {'recipe_id': 'r-1', 'is_favorite': true});

      final res = await repo.addFavoriteRecipe('r-1');

      final isFav = res.fold((f) => fail('expected Right: $f'), (v) => v);
      expect(isFav, isTrue);
      verify(() => api.put(ApiPaths.recipeFavorite('r-1'))).called(1);
    });

    test('removeFavoriteRecipe sends delete to recipeFavorite path', () async {
      when(() => api.delete(ApiPaths.recipeFavorite('r-1')))
          .thenAnswer((_) async => null);

      final res = await repo.removeFavoriteRecipe('r-1');

      expect(res.isSuccess, isTrue);
      verify(() => api.delete(ApiPaths.recipeFavorite('r-1'))).called(1);
    });

    test('fetchFavoriteRecipes returns parsed favorite recipes list', () async {
      when(() => api.get(ApiPaths.favoriteRecipes, query: {'limit': 20, 'offset': 0}))
          .thenAnswer((_) async => {
                'items': [
                  {
                    'recipe_id': 'r-1',
                    'recipe_name': 'Món A',
                    'recipe_image_url': 'https://example.com/a.jpg',
                    'favorited_at': '2026-03-01T08:00:00Z',
                  }
                ],
                'total': 1,
                'limit': 20,
                'offset': 0,
              });

      final res = await repo.fetchFavoriteRecipes(limit: 20, offset: 0);

      final items = res.fold((f) => fail('expected Right: $f'), (v) => v);
      expect(items.length, 1);
      expect(items.first.recipeId, 'r-1');
      expect(items.first.recipeName, 'Món A');
    });
  });

  group('FavoriteRepositoryImpl - Favorite Menus', () {
    test('fetchFavoriteMenus returns parsed menus list', () async {
      when(() => api.get(ApiPaths.favoriteMenus, query: {'limit': 50, 'offset': 0}))
          .thenAnswer((_) async => {
                'items': [
                  {
                    'id': 'menu-1',
                    'name': 'Thực đơn gia đình',
                    'description': 'Món ngon',
                    'created_at': '2026-03-01T08:00:00Z',
                    'updated_at': '2026-03-01T08:00:00Z',
                  }
                ],
              });

      final res = await repo.fetchFavoriteMenus();

      final items = res.fold((f) => fail('expected Right: $f'), (v) => v);
      expect(items.length, 1);
      expect(items.first.id, 'menu-1');
      expect(items.first.name, 'Thực đơn gia đình');
    });

    test('fetchFavoriteMenuDetail returns menu detail with items', () async {
      when(() => api.get(ApiPaths.favoriteMenu('menu-1')))
          .thenAnswer((_) async => {
                'id': 'menu-1',
                'name': 'Thực đơn gia đình',
                'description': 'Món ngon',
                'items': [
                  {
                    'id': 'item-1',
                    'recipe_id': 'r-1',
                    'recipe_name': 'Món A',
                    'recipe_image_url': null,
                    'created_at': '2026-03-01T08:00:00Z',
                  }
                ],
                'created_at': '2026-03-01T08:00:00Z',
                'updated_at': '2026-03-01T08:00:00Z',
              });

      final res = await repo.fetchFavoriteMenuDetail('menu-1');

      final detail = res.fold((f) => fail('expected Right: $f'), (v) => v);
      expect(detail.id, 'menu-1');
      expect(detail.items.length, 1);
      expect(detail.items.first.recipeId, 'r-1');
    });

    test('createFavoriteMenu posts payload and returns created menu', () async {
      when(() => api.post(ApiPaths.favoriteMenus, body: {
            'name': 'Menu mới',
            'description': 'Mô tả',
          })).thenAnswer((_) async => {
            'id': 'menu-2',
            'name': 'Menu mới',
            'description': 'Mô tả',
            'created_at': '2026-03-01T08:00:00Z',
            'updated_at': '2026-03-01T08:00:00Z',
          });

      final res = await repo.createFavoriteMenu(name: 'Menu mới', description: 'Mô tả');

      final menu = res.fold((f) => fail('expected Right: $f'), (v) => v);
      expect(menu.id, 'menu-2');
      expect(menu.name, 'Menu mới');
    });

    test('updateFavoriteMenu patches payload and returns updated menu', () async {
      when(() => api.patch(ApiPaths.favoriteMenu('menu-2'), body: {
            'name': 'Menu cập nhật',
          })).thenAnswer((_) async => {
            'id': 'menu-2',
            'name': 'Menu cập nhật',
            'description': 'Mô tả',
            'created_at': '2026-03-01T08:00:00Z',
            'updated_at': '2026-03-01T08:00:00Z',
          });

      final res = await repo.updateFavoriteMenu('menu-2', name: 'Menu cập nhật');

      final menu = res.fold((f) => fail('expected Right: $f'), (v) => v);
      expect(menu.name, 'Menu cập nhật');
    });

    test('deleteFavoriteMenu deletes menu path', () async {
      when(() => api.delete(ApiPaths.favoriteMenu('menu-2')))
          .thenAnswer((_) async => null);

      final res = await repo.deleteFavoriteMenu('menu-2');

      expect(res.isSuccess, isTrue);
      verify(() => api.delete(ApiPaths.favoriteMenu('menu-2'))).called(1);
    });

    test('addMenuItem posts recipe to menu items', () async {
      when(() => api.post(ApiPaths.favoriteMenuItems('menu-1'), body: {
            'recipe_id': 'r-2',
          })).thenAnswer((_) async => {
            'id': 'item-2',
            'recipe_id': 'r-2',
            'recipe_name': 'Món B',
            'recipe_image_url': null,
            'created_at': '2026-03-01T08:00:00Z',
          });

      final res = await repo.addMenuItem('menu-1', 'r-2');

      final item = res.fold((f) => fail('expected Right: $f'), (v) => v);
      expect(item.id, 'item-2');
      expect(item.recipeId, 'r-2');
    });

    test('removeMenuItem deletes item from menu items', () async {
      when(() => api.delete(ApiPaths.favoriteMenuItem('menu-1', 'item-2')))
          .thenAnswer((_) async => null);

      final res = await repo.removeMenuItem('menu-1', 'item-2');

      expect(res.isSuccess, isTrue);
      verify(() => api.delete(ApiPaths.favoriteMenuItem('menu-1', 'item-2'))).called(1);
    });
  });
}
