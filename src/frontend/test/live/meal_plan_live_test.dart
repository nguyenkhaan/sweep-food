@Tags(['live'])
library;

/// Exercises the meal-plan data layer (DTO parsing + Dio + AuthInterceptor)
/// against a running backend with the seed dataset loaded. Skipped unless
/// `LIVE_BASE_URL` is set:
///
///   flutter test test/live/meal_plan_live_test.dart --run-skipped \
///     --dart-define=LIVE_BASE_URL=http://127.0.0.1:4000/api
import 'package:dio/dio.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:sweepfood/core/network/dio_api_client.dart';
import 'package:sweepfood/core/network/interceptors/auth_interceptor.dart';
import 'package:sweepfood/core/storage/secure_storage.dart';
import 'package:sweepfood/features/auth/data/datasources/auth_remote_data_source.dart';
import 'package:sweepfood/features/auth/data/repositories/auth_repository_impl.dart';
import 'package:sweepfood/features/meal_plan/data/datasources/meal_plan_remote_data_source.dart';
import 'package:sweepfood/features/meal_plan/data/repositories/meal_plan_repository_impl.dart';
import 'package:sweepfood/features/meal_plan/domain/entities/meal_plan.dart';
import 'package:sweepfood/features/meal_plan/domain/entities/meal_plan_entry.dart';

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
    test('live meal plan (skipped: set --dart-define=LIVE_BASE_URL)', () {},
        skip: true);
    return;
  }

  late DioApiClient api;
  late MealPlanRepositoryImpl mealPlans;

  setUp(() async {
    final store = _MemStore();
    final dio = Dio(BaseOptions(baseUrl: _baseUrl))
      ..interceptors.add(AuthInterceptor(store, baseUrl: _baseUrl));
    api = DioApiClient(dio);
    final auth = AuthRepositoryImpl(AuthRemoteDataSource(api), store);

    final tail = DateTime.now().microsecondsSinceEpoch.toString();
    final phone = '+8493${tail.substring(tail.length - 8)}';
    const password = 'secret12345';
    await auth.register(phone: phone, password: password, name: 'MealPlan Live');
    final session = await auth.verifyRegisterAndLogin(
      phone: phone,
      otp: '123456',
      password: password,
    );
    session.fold((f) => fail('sign-in failed: $f'), (_) {});

    mealPlans = MealPlanRepositoryImpl(MealPlanRemoteDataSource(api));
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

  test('forWeek() creates a plan for a never-seen week, then reuses it', () async {
    // A far-future week is very unlikely to collide with another test run.
    final weekStart = MealPlan.weekStartOf(
      DateTime.now().add(const Duration(days: 365)),
    );

    final first = await mealPlans.forWeek(weekStart);
    final plan1 = first.fold((f) => fail('forWeek failed: $f'), (p) => p);
    expect(plan1.id, isNotNull);
    expect(plan1.weekStart, weekStart);
    expect(plan1.entries, isEmpty);

    final second = await mealPlans.forWeek(weekStart);
    final plan2 = second.fold((f) => fail('forWeek failed: $f'), (p) => p);
    // Same week -> same backend plan, not a duplicate.
    expect(plan2.id, plan1.id);
  });

  test('addEntry() then updateEntry() keeps the same item id', () async {
    final weekStart = MealPlan.weekStartOf(
      DateTime.now().add(const Duration(days: 372)),
    );
    final recipeId = await chickenRecipeId();
    final day = weekStart.add(const Duration(days: 2));

    final added = await mealPlans.addEntry(
      weekStart: weekStart,
      date: day,
      slot: MealSlot.dinner,
      dishId: recipeId,
      servings: 2,
    );
    final entry = added.fold((f) => fail('addEntry failed: $f'), (e) => e);
    expect(entry.id, isNotEmpty);
    expect(entry.dishId, recipeId);
    expect(entry.servings, 2);
    expect(entry.slot, MealSlot.dinner);

    final updated = await mealPlans.updateEntry(
      weekStart: weekStart,
      itemId: entry.id,
      dishId: recipeId,
      servings: 4,
    );
    final entry2 = updated.fold((f) => fail('updateEntry failed: $f'), (e) => e);
    expect(entry2.id, entry.id); // same item, not delete+recreate
    expect(entry2.servings, 4);

    final plan = (await mealPlans.forWeek(weekStart))
        .fold((f) => fail('forWeek failed: $f'), (p) => p);
    expect(plan.entryAt(day, MealSlot.dinner)?.servings, 4);
  });

  test('removeEntry() deletes the item', () async {
    final weekStart = MealPlan.weekStartOf(
      DateTime.now().add(const Duration(days: 379)),
    );
    final recipeId = await chickenRecipeId();
    final day = weekStart.add(const Duration(days: 1));

    final added = await mealPlans.addEntry(
      weekStart: weekStart,
      date: day,
      slot: MealSlot.lunch,
      dishId: recipeId,
      servings: 1,
    );
    final entry = added.fold((f) => fail('addEntry failed: $f'), (e) => e);

    final removed = await mealPlans.removeEntry(
      weekStart: weekStart,
      itemId: entry.id,
    );
    expect(removed.isRight(), isTrue);

    final plan = (await mealPlans.forWeek(weekStart))
        .fold((f) => fail('forWeek failed: $f'), (p) => p);
    expect(plan.entryAt(day, MealSlot.lunch), isNull);
  });
}
