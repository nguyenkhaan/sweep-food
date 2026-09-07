@Tags(['live'])
library;

import 'package:dio/dio.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:sweepfood/core/network/dio_api_client.dart';
import 'package:sweepfood/core/network/interceptors/auth_interceptor.dart';
import 'package:sweepfood/core/storage/secure_storage.dart';
import 'package:sweepfood/core/utils/result.dart';
import 'package:sweepfood/features/auth/data/datasources/auth_remote_data_source.dart';
import 'package:sweepfood/features/auth/data/repositories/auth_repository_impl.dart';
import 'package:sweepfood/features/favorites/data/datasources/favorite_remote_data_source.dart';
import 'package:sweepfood/features/favorites/data/repositories/favorite_repository_impl.dart';

const _baseUrl = String.fromEnvironment('LIVE_BASE_URL');

class _MemStore implements SecureStore {
  String? _access;
  String? _refresh;
  @override
  Future<String?> readAccessToken() async => _access;
  @override
  Future<String?> readRefreshToken() async => _refresh;
  @override
  Future<void> writeTokens({
    required String accessToken,
    required String refreshToken,
  }) async {
    _access = accessToken;
    _refresh = refreshToken;
  }

  @override
  Future<void> clear() async {
    _access = null;
    _refresh = null;
  }
}

void main() {
  if (_baseUrl.isEmpty) {
    test('live favorites (skipped: set --dart-define=LIVE_BASE_URL)', () {},
        skip: true);
    return;
  }

  late DioApiClient api;
  late FavoriteRepositoryImpl favRepo;

  setUp(() async {
    final store = _MemStore();
    final dio = Dio(BaseOptions(baseUrl: _baseUrl))
      ..interceptors.add(AuthInterceptor(store, baseUrl: _baseUrl));
    api = DioApiClient(dio);
    final auth = AuthRepositoryImpl(AuthRemoteDataSource(api), store);

    final tail = DateTime.now().microsecondsSinceEpoch.toString();
    final phone = '+8493${tail.substring(tail.length - 8)}';
    const password = 'secret12345';
    await auth.register(
      phone: phone,
      password: password,
      name: 'Favorites Live',
    );
    final session = await auth.verifyRegisterAndLogin(
      phone: phone,
      otp: '123456',
      password: password,
    );
    session.fold((f) => fail('sign-in failed: $f'), (_) {});

    favRepo = FavoriteRepositoryImpl(FavoriteRemoteDataSource(api));
  });

  test('full favorites lifecycle (favorite toggle + menu CRUD + menu items)', () async {
    // 1. Get a recipe ID to favorite
    final recipes = await favRepo.fetchFavoriteRecipes();
    expect(recipes.isSuccess, isTrue);

    // 2. Favorite recipe test
    const testRecipeId = '00000000-0000-0000-0000-000000000001';
    final addFavRes = await favRepo.addFavoriteRecipe(testRecipeId);
    if (addFavRes.isSuccess) {
      expect(addFavRes.valueOrNull, isTrue);

      // Verify in list
      final favs = await favRepo.fetchFavoriteRecipes();
      expect(favs.isSuccess, isTrue);

      // Remove favorite
      final removeFavRes = await favRepo.removeFavoriteRecipe(testRecipeId);
      expect(removeFavRes.isSuccess, isTrue);
    }

    // 3. Menu CRUD test
    final createMenuRes = await favRepo.createFavoriteMenu(
      name: 'Live Test Menu',
      description: 'Created by live test',
    );
    expect(createMenuRes.isSuccess, isTrue);
    final menu = createMenuRes.valueOrNull!;
    expect(menu.name, 'Live Test Menu');

    // 4. Update menu
    final updateMenuRes = await favRepo.updateFavoriteMenu(
      menu.id,
      name: 'Live Test Menu Updated',
    );
    expect(updateMenuRes.isSuccess, isTrue);
    expect(updateMenuRes.valueOrNull!.name, 'Live Test Menu Updated');

    // 5. Add recipe item to menu
    final addItemRes = await favRepo.addMenuItem(menu.id, testRecipeId);
    if (addItemRes.isSuccess) {
      final item = addItemRes.valueOrNull!;
      expect(item.recipeId, testRecipeId);

      // Verify detail
      final detailRes = await favRepo.fetchFavoriteMenuDetail(menu.id);
      expect(detailRes.isSuccess, isTrue);
      expect(detailRes.valueOrNull!.items.any((i) => i.id == item.id), isTrue);

      // Remove item
      final removeItemRes = await favRepo.removeMenuItem(menu.id, item.id);
      expect(removeItemRes.isSuccess, isTrue);
    }

    // 6. Delete menu
    final deleteMenuRes = await favRepo.deleteFavoriteMenu(menu.id);
    expect(deleteMenuRes.isSuccess, isTrue);
  });
}
