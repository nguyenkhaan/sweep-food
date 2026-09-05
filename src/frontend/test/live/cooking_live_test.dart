@Tags(['live'])
library;

/// Exercises the cooking data layer (DTO parsing + Dio + AuthInterceptor)
/// against a running backend with the seed dataset loaded. Skipped unless
/// `LIVE_BASE_URL` is set:
///
///   flutter test test/live/cooking_live_test.dart --run-skipped \
///     --dart-define=LIVE_BASE_URL=http://127.0.0.1:4000/api
///
/// Stocks one of the seeded chicken recipe's ingredients (matched by
/// `master_ingredient_id`, the same key the backend's preview step uses) so
/// `proposed_deductions` isn't empty and the 3-step flow can actually run.
import 'package:dio/dio.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:sweepfood/core/network/dio_api_client.dart';
import 'package:sweepfood/core/network/interceptors/auth_interceptor.dart';
import 'package:sweepfood/core/storage/secure_storage.dart';
import 'package:sweepfood/features/auth/data/datasources/auth_remote_data_source.dart';
import 'package:sweepfood/features/auth/data/repositories/auth_repository_impl.dart';
import 'package:sweepfood/features/cooking/data/datasources/cooking_remote_data_source.dart';
import 'package:sweepfood/features/cooking/data/repositories/cooking_repository_impl.dart';
import 'package:sweepfood/features/cooking/domain/entities/cook_confirmation.dart';
import 'package:sweepfood/features/cooking/domain/entities/cooked_food.dart';
import 'package:sweepfood/features/meal_plan/data/datasources/meal_plan_remote_data_source.dart';
import 'package:sweepfood/features/meal_plan/data/repositories/meal_plan_repository_impl.dart';
import 'package:sweepfood/features/meal_plan/domain/entities/meal_plan.dart';
import 'package:sweepfood/features/meal_plan/domain/entities/meal_plan_entry.dart';
import 'package:sweepfood/features/pantry/data/datasources/pantry_remote_data_source.dart';
import 'package:sweepfood/features/pantry/data/repositories/pantry_repository_impl.dart';
import 'package:sweepfood/features/pantry/domain/entities/pantry_item.dart';
import 'package:sweepfood/features/pantry/domain/entities/pantry_item_draft.dart';
import 'package:sweepfood/shared/domain/measurement_unit.dart';
import 'package:sweepfood/shared/domain/storage_tier.dart';

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
    test('live cooking (skipped: set --dart-define=LIVE_BASE_URL)', () {},
        skip: true);
    return;
  }

  late DioApiClient api;
  late MealPlanRepositoryImpl mealPlans;
  late PantryRepositoryImpl pantry;
  late CookingRepositoryImpl cooking;

  setUp(() async {
    final store = _MemStore();
    final dio = Dio(BaseOptions(baseUrl: _baseUrl))
      ..interceptors.add(AuthInterceptor(store, baseUrl: _baseUrl));
    api = DioApiClient(dio);
    final auth = AuthRepositoryImpl(AuthRemoteDataSource(api), store);

    final tail = DateTime.now().microsecondsSinceEpoch.toString();
    final phone = '+8493${tail.substring(tail.length - 8)}';
    const password = 'secret12345';
    await auth.register(phone: phone, password: password, name: 'Cooking Live');
    final session = await auth.verifyRegisterAndLogin(
      phone: phone,
      otp: '123456',
      password: password,
    );
    session.fold((f) => fail('sign-in failed: $f'), (_) {});

    mealPlans = MealPlanRepositoryImpl(MealPlanRemoteDataSource(api));
    pantry = PantryRepositoryImpl(PantryRemoteDataSource(api));
    cooking = CookingRepositoryImpl(CookingRemoteDataSource(api));
  });

  /// Finds the seeded chicken recipe and its detail (ingredients included).
  Future<Map<String, dynamic>> chickenRecipeDetail() async {
    final list = await api.get('/recipes') as Map<String, dynamic>;
    final items = (list['items'] as List).cast<Map<String, dynamic>>();
    expect(items, isNotEmpty, reason: 'is the seed dataset loaded?');
    final id = items
        .firstWhere(
          (r) => (r['name'] as String).toLowerCase().contains('chicken'),
          orElse: () => fail('no "chicken" recipe in $items'),
        )['id'] as String;
    return await api.get('/recipes/$id') as Map<String, dynamic>;
  }

  /// Stocks one non-optional ingredient (matched by `master_ingredient_id`,
  /// same as the backend's own preview matching) and creates a meal-plan item
  /// for the recipe. Returns the created item's id.
  Future<({String mealPlanItemId, String masterIngredientId, PantryItem batch})>
      setUpCookableItem() async {
    final recipe = await chickenRecipeDetail();
    final ingredients = (recipe['ingredients'] as List).cast<Map<String, dynamic>>();
    final ing = ingredients.firstWhere(
      (i) => i['is_optional'] != true && i['master_ingredient_id'] != null,
      orElse: () => fail('no matchable non-optional ingredient in $ingredients'),
    );
    final masterIngredientId = ing['master_ingredient_id'] as String;
    // Pydantic Decimal fields serialize as JSON strings on this backend.
    final requiredQty = double.parse(ing['required_quantity'].toString());
    final unit = MeasurementUnit.fromWire(ing['unit'] as String);

    final batchRes = await pantry.add(
      PantryItemDraft(
        name: ing['name'] as String,
        ingredientId: masterIngredientId,
        quantity: requiredQty * 3,
        unit: unit,
        storageTier: StorageTier.fridge,
        expiryDate: DateTime.now().toUtc().add(const Duration(days: 5)),
      ),
    );
    final batch = batchRes.fold((f) => fail('stocking failed: $f'), (i) => i);

    final weekStart = MealPlan.weekStartOf(
      DateTime.now().add(const Duration(days: 393)),
    );
    await mealPlans.forWeek(weekStart);
    final servings = recipe['default_servings'] == null
        ? 1.0
        : double.parse(recipe['default_servings'].toString());
    final entryRes = await mealPlans.addEntry(
      weekStart: weekStart,
      date: weekStart,
      slot: MealSlot.dinner,
      dishId: recipe['id'] as String,
      servings: servings,
    );
    final entry = entryRes.fold((f) => fail('addEntry failed: $f'), (e) => e);

    return (mealPlanItemId: entry.id, masterIngredientId: masterIngredientId, batch: batch);
  }

  test('preview() proposes a deduction from the stocked batch', () async {
    final setup = await setUpCookableItem();

    final res = await cooking.preview(setup.mealPlanItemId);
    final preview = res.fold((f) => fail('preview failed: $f'), (p) => p);

    expect(preview.recipeId, isNotEmpty);
    expect(preview.proposedDeductions, isNotEmpty);
    expect(
      preview.proposedDeductions.any((d) => d.batchId == setup.batch.id),
      isTrue,
      reason: 'expected the stocked batch to be proposed for deduction',
    );
  });

  test('createSession() then complete(EXACT) deducts the stocked batch',
      () async {
    final setup = await setUpCookableItem();
    final preview = (await cooking.preview(setup.mealPlanItemId))
        .fold((f) => fail('preview failed: $f'), (p) => p);
    final deduction = preview.proposedDeductions
        .firstWhere((d) => d.batchId == setup.batch.id);

    final sessionRes = await cooking.createSession(setup.mealPlanItemId);
    final sessionId = sessionRes.fold((f) => fail('createSession failed: $f'), (id) => id);
    expect(sessionId, isNotEmpty);

    final completeRes = await cooking.complete(sessionId, CookMode.exact);
    expect(completeRes.isRight(), isTrue);

    final after = (await pantry.list())
        .fold((f) => fail('list failed: $f'), (p) => p)
        .items
        .firstWhere(
          (i) => i.id == setup.batch.id,
          orElse: () => fail('batch ${setup.batch.id} missing after cooking'),
        );
    expect(after.quantity, closeTo(setup.batch.quantity - deduction.quantity, 0.001));
  });

  test('saveLeftover() creates a new batch tied to the session', () async {
    final setup = await setUpCookableItem();
    final sessionRes = await cooking.createSession(setup.mealPlanItemId);
    final sessionId = sessionRes.fold((f) => fail('createSession failed: $f'), (id) => id);
    await cooking.complete(sessionId, CookMode.exact);

    final res = await cooking.saveLeftover(
      CookedFood(sessionId: sessionId, dishName: 'Gà rán live', servings: 2),
    );
    final leftover = res.fold((f) => fail('saveLeftover failed: $f'), (i) => i);
    expect(leftover.id, isNotEmpty);
    expect(leftover.quantity, 2);
  });
}
