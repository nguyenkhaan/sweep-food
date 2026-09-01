@Tags(['live'])
library;

/// Exercises the catalog data layer (DTO parsing + Dio + AuthInterceptor)
/// against a running backend with the seed dataset loaded. Skipped unless
/// `LIVE_BASE_URL` is set:
///
///   flutter test test/live/catalog_live_test.dart --run-skipped \
///     --dart-define=LIVE_BASE_URL=http://127.0.0.1:4000/api
///
/// Needs the backend up with `ENV=dev` and `python -m src.seed` already run
/// (seed ingredients: Spinach, Chicken breast, Fresh milk, Rice).
import 'package:dio/dio.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:sweepfood/core/network/dio_api_client.dart';
import 'package:sweepfood/core/network/interceptors/auth_interceptor.dart';
import 'package:sweepfood/core/storage/secure_storage.dart';
import 'package:sweepfood/features/auth/data/datasources/auth_remote_data_source.dart';
import 'package:sweepfood/features/auth/data/repositories/auth_repository_impl.dart';
import 'package:sweepfood/features/catalog/data/datasources/ingredient_remote_data_source.dart';
import 'package:sweepfood/features/catalog/data/repositories/ingredient_repository_impl.dart';
import 'package:sweepfood/shared/domain/measurement_unit.dart';

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
    test('live catalog (skipped: set --dart-define=LIVE_BASE_URL)', () {},
        skip: true);
    return;
  }

  late IngredientRepositoryImpl catalog;

  setUp(() async {
    final store = _MemStore();
    final dio = Dio(BaseOptions(baseUrl: _baseUrl))
      ..interceptors.add(AuthInterceptor(store, baseUrl: _baseUrl));
    final api = DioApiClient(dio);
    final auth = AuthRepositoryImpl(AuthRemoteDataSource(api), store);

    final tail = DateTime.now().microsecondsSinceEpoch.toString();
    final phone = '+8493${tail.substring(tail.length - 8)}';
    const password = 'secret12345';
    await auth.register(phone: phone, password: password, name: 'Catalog Live');
    final session = await auth.verifyRegisterAndLogin(
      phone: phone,
      otp: '123456',
      password: password,
    );
    session.fold((f) => fail('sign-in failed: $f'), (_) {});

    catalog = IngredientRepositoryImpl(IngredientRemoteDataSource(api));
  });

  test('search matches a seeded canonical name and maps units/category',
      () async {
    final res = await catalog.search('milk');
    final list = res.fold((f) => fail('search failed: $f'), (l) => l);
    expect(list, isNotEmpty, reason: 'is the seed dataset loaded?');

    final milk = list.firstWhere(
      (i) => i.name.toLowerCase().contains('milk'),
      orElse: () => fail('no "milk" ingredient in $list'),
    );
    expect(milk.category, 'Dairy');
    expect(milk.defaultUnit, MeasurementUnit.milliliter);
  });

  test('search matches a seeded alias', () async {
    // "Ức gà" is a seeded alias of "Chicken breast" (normalized "uc ga").
    final res = await catalog.search('uc ga');
    final list = res.fold((f) => fail('search failed: $f'), (l) => l);
    expect(
      list.any((i) => i.name.toLowerCase().contains('chicken')),
      isTrue,
      reason: 'alias search should surface Chicken breast',
    );
  });

  test('byId returns nutrition and a flattened shelf-life hint', () async {
    final found = (await catalog.search('milk')).fold(
      (f) => fail('search failed: $f'),
      (l) => l.firstWhere((i) => i.name.toLowerCase().contains('milk')),
    );

    final res = await catalog.byId(found.id);
    final milk = res.fold((f) => fail('byId failed: $f'), (i) => i);
    expect(milk.nutritionPer100g, isNotNull);
    expect(milk.nutritionPer100g!.energyKcal, greaterThan(0));
    expect(milk.referenceShelfLifeDays, isNotNull);
  });
}
