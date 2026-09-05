@Tags(['live'])
library;

/// Exercises the shopping-list data layer (DTO parsing + Dio + AuthInterceptor)
/// against a running backend with the seed dataset loaded. Skipped unless
/// `LIVE_BASE_URL` is set:
///
///   flutter test test/live/shopping_list_live_test.dart --run-skipped \
///     --dart-define=LIVE_BASE_URL=http://127.0.0.1:4000/api
import 'package:dio/dio.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:sweepfood/core/network/dio_api_client.dart';
import 'package:sweepfood/core/network/interceptors/auth_interceptor.dart';
import 'package:sweepfood/core/storage/secure_storage.dart';
import 'package:sweepfood/features/auth/data/datasources/auth_remote_data_source.dart';
import 'package:sweepfood/features/auth/data/repositories/auth_repository_impl.dart';
import 'package:sweepfood/features/meal_plan/data/datasources/meal_plan_remote_data_source.dart';
import 'package:sweepfood/features/meal_plan/data/repositories/meal_plan_repository_impl.dart';
import 'package:sweepfood/features/meal_plan/domain/entities/meal_plan.dart';
import 'package:sweepfood/features/meal_plan/domain/entities/meal_plan_entry.dart';
import 'package:sweepfood/features/shopping_list/data/datasources/shopping_list_remote_data_source.dart';
import 'package:sweepfood/features/shopping_list/data/repositories/shopping_list_repository_impl.dart';
import 'package:sweepfood/features/shopping_list/domain/entities/shopping_list_item.dart';
import 'package:sweepfood/features/shopping_list/domain/entities/shopping_purchase_draft.dart';
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
    test('live shopping list (skipped: set --dart-define=LIVE_BASE_URL)', () {},
        skip: true);
    return;
  }

  late DioApiClient api;
  late MealPlanRepositoryImpl mealPlans;
  late ShoppingListRepositoryImpl shoppingLists;

  setUp(() async {
    final store = _MemStore();
    final dio = Dio(BaseOptions(baseUrl: _baseUrl))
      ..interceptors.add(AuthInterceptor(store, baseUrl: _baseUrl));
    api = DioApiClient(dio);
    final auth = AuthRepositoryImpl(AuthRemoteDataSource(api), store);

    final tail = DateTime.now().microsecondsSinceEpoch.toString();
    final phone = '+8493${tail.substring(tail.length - 8)}';
    const password = 'secret12345';
    await auth.register(phone: phone, password: password, name: 'Shopping Live');
    final session = await auth.verifyRegisterAndLogin(
      phone: phone,
      otp: '123456',
      password: password,
    );
    session.fold((f) => fail('sign-in failed: $f'), (_) {});

    mealPlans = MealPlanRepositoryImpl(MealPlanRemoteDataSource(api));
    SharedPreferences.setMockInitialValues({});
    final prefs = await SharedPreferences.getInstance();
    shoppingLists = ShoppingListRepositoryImpl(ShoppingListRemoteDataSource(api), prefs);
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

  /// A meal plan with one item, for `generate {meal_plan_id}`.
  Future<String> planWithOneItem() async {
    final weekStart = MealPlan.weekStartOf(
      DateTime.now().add(const Duration(days: 386)),
    );
    final plan = (await mealPlans.forWeek(weekStart))
        .fold((f) => fail('forWeek failed: $f'), (p) => p);
    final recipeId = await chickenRecipeId();
    await mealPlans.addEntry(
      weekStart: weekStart,
      date: weekStart,
      slot: MealSlot.dinner,
      dishId: recipeId,
      servings: 2,
    );
    return plan.id!;
  }

  test('current() is null until generate() has been called', () async {
    final res = await shoppingLists.current();
    final list = res.fold((f) => fail('current failed: $f'), (l) => l);
    expect(list, isNull);
  });

  test('generate() creates a list and current() then finds it', () async {
    final planId = await planWithOneItem();

    final generated = await shoppingLists.generate(mealPlanId: planId);
    final list = generated.fold((f) => fail('generate failed: $f'), (l) => l);
    expect(list.id, isNotEmpty);

    final res = await shoppingLists.current();
    final current = res.fold((f) => fail('current failed: $f'), (l) => l);
    expect(current, isNotNull);
    expect(current!.id, list.id);
  });

  test('addItem() adds a manual line', () async {
    final planId = await planWithOneItem();
    final list = (await shoppingLists.generate(mealPlanId: planId))
        .fold((f) => fail('generate failed: $f'), (l) => l);

    final res = await shoppingLists.addItem(
      listId: list.id,
      draft: const ShoppingListItemDraft(
        name: 'Khăn giấy live',
        quantity: 2,
        unit: MeasurementUnit.piece,
      ),
    );
    final item = res.fold((f) => fail('addItem failed: $f'), (i) => i);
    expect(item.name, 'Khăn giấy live');
    expect(item.isManual, isTrue);
  });

  test(
      'setChecked(true) requires purchase and setChecked(false) omits it',
      () async {
    final planId = await planWithOneItem();
    final list = (await shoppingLists.generate(mealPlanId: planId))
        .fold((f) => fail('generate failed: $f'), (l) => l);

    final added = await shoppingLists.addItem(
      listId: list.id,
      draft: const ShoppingListItemDraft(
        name: 'Muối live',
        quantity: 1,
        unit: MeasurementUnit.piece,
      ),
    );
    final item = added.fold((f) => fail('addItem failed: $f'), (i) => i);

    final checked = await shoppingLists.setChecked(
      listId: list.id,
      itemId: item.id,
      checked: true,
      purchase: const ShoppingPurchaseDraft(storageTier: StorageTier.pantryShelf),
    );
    expect(checked.isRight(), isTrue);

    final unchecked = await shoppingLists.setChecked(
      listId: list.id,
      itemId: item.id,
      checked: false,
    );
    expect(unchecked.isRight(), isTrue);
  });

  test('removeItem() deletes a manual line', () async {
    final planId = await planWithOneItem();
    final list = (await shoppingLists.generate(mealPlanId: planId))
        .fold((f) => fail('generate failed: $f'), (l) => l);

    final added = await shoppingLists.addItem(
      listId: list.id,
      draft: const ShoppingListItemDraft(
        name: 'Đường live',
        quantity: 1,
        unit: MeasurementUnit.piece,
      ),
    );
    final item = added.fold((f) => fail('addItem failed: $f'), (i) => i);

    final removed = await shoppingLists.removeItem(
      listId: list.id,
      itemId: item.id,
    );
    expect(removed.isRight(), isTrue);
  });
}
