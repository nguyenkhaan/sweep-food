@Tags(['live'])
library;

/// Exercises the recipe → Dish mapping (RecipeDto + Dio + AuthInterceptor)
/// against a running backend with the seed dataset loaded. Skipped unless
/// `LIVE_BASE_URL` is set:
///
///   flutter test test/live/recipe_live_test.dart --run-skipped \
///     --dart-define=LIVE_BASE_URL=http://127.0.0.1:4000/api
///
/// Needs the backend up with `ENV=dev` and the seed run (recipes: Spinach soup,
/// Grilled chicken breast, Fresh milk smoothie, Steamed rice).
import 'package:dio/dio.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:sweepfood/core/network/dio_api_client.dart';
import 'package:sweepfood/core/network/interceptors/auth_interceptor.dart';
import 'package:sweepfood/core/storage/secure_storage.dart';
import 'package:sweepfood/features/auth/data/datasources/auth_remote_data_source.dart';
import 'package:sweepfood/features/auth/data/repositories/auth_repository_impl.dart';
import 'package:sweepfood/features/dishes/data/datasources/dish_remote_data_source.dart';
import 'package:sweepfood/features/dishes/data/repositories/dish_repository_impl.dart';

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
    test('live recipe (skipped: set --dart-define=LIVE_BASE_URL)', () {},
        skip: true);
    return;
  }

  late DioApiClient api;
  late DishRepositoryImpl recipes;

  setUp(() async {
    final store = _MemStore();
    final dio = Dio(BaseOptions(baseUrl: _baseUrl))
      ..interceptors.add(AuthInterceptor(store, baseUrl: _baseUrl));
    api = DioApiClient(dio);
    final auth = AuthRepositoryImpl(AuthRemoteDataSource(api), store);

    final tail = DateTime.now().microsecondsSinceEpoch.toString();
    final phone = '+8493${tail.substring(tail.length - 8)}';
    const password = 'secret12345';
    await auth.register(phone: phone, password: password, name: 'Recipe Live');
    final session = await auth.verifyRegisterAndLogin(
      phone: phone,
      otp: '123456',
      password: password,
    );
    session.fold((f) => fail('sign-in failed: $f'), (_) {});

    recipes = DishRepositoryImpl(DishRemoteDataSource(api));
  });

  Future<String> chickenRecipeId() async {
    final body = await api.get('/recipes') as Map<String, dynamic>;
    final items = (body['items'] as List).cast<Map<String, dynamic>>();
    expect(items, isNotEmpty, reason: 'is the seed dataset loaded?');
    return items
        .firstWhere(
          (r) => (r['name'] as String).toLowerCase().contains('chicken'),
          orElse: () => fail('no "chicken" recipe in $items'),
        )['id'] as String;
  }

  test('GET /recipes/{id} maps into a Dish with steps and per-serving macros',
      () async {
    final id = await chickenRecipeId();

    final res = await recipes.getById(id);
    final dish = res.fold((f) => fail('getById failed: $f'), (d) => d);

    expect(dish.name.toLowerCase(), contains('chicken'));
    expect(dish.servings, greaterThanOrEqualTo(1));
    expect(dish.cookTimeMin, greaterThan(0));
    expect(dish.steps, isNotEmpty);
    expect(dish.steps.first.order, 1);
    expect(dish.ingredients, isNotEmpty);
    // Seeded macros are non-zero and already divided to per-serving.
    expect(dish.nutritionPerServing.energyKcal, greaterThan(0));
  });

  test('a scaled serving request keeps per-serving macros stable', () async {
    final id = await chickenRecipeId();

    final base = (await recipes.getById(id)).fold((f) => fail('$f'), (d) => d);
    // Dish.scaledTo re-derives quantities client-side; per-serving is unchanged.
    final scaled = base.scaledTo(base.servings * 2);
    expect(
      scaled.nutritionPerServing.energyKcal,
      closeTo(base.nutritionPerServing.energyKcal, 1e-6),
    );
    expect(
      scaled.ingredients.first.quantity,
      closeTo(base.ingredients.first.quantity * 2, 1e-6),
    );
  });
}
