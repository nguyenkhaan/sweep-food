@Tags(['live'])
library;

/// Exercises the recommendations data layer (POST /recommendations + DTO parsing +
/// parallel recipe fetching) against a running backend with the seed dataset loaded.
/// Skipped unless `LIVE_BASE_URL` is set:
///
///   flutter test test/live/recommendations_live_test.dart --run-skipped \
///     --dart-define=LIVE_BASE_URL=http://127.0.0.1:4000/api
///
/// Needs the backend up with `ENV=dev` and `python -m src.seed` already run.
import 'package:dio/dio.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:sweepfood/core/network/dio_api_client.dart';
import 'package:sweepfood/core/network/interceptors/auth_interceptor.dart';
import 'package:sweepfood/core/storage/secure_storage.dart';
import 'package:sweepfood/features/auth/data/datasources/auth_remote_data_source.dart';
import 'package:sweepfood/features/auth/data/repositories/auth_repository_impl.dart';
import 'package:sweepfood/features/dishes/data/datasources/dish_remote_data_source.dart';
import 'package:sweepfood/features/suggestions/data/datasources/suggestion_remote_data_source.dart';
import 'package:sweepfood/features/suggestions/data/repositories/suggestion_repository_impl.dart';
import 'package:sweepfood/features/suggestions/domain/entities/suggestion_request.dart';

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
    test('live recommendations (skipped: set --dart-define=LIVE_BASE_URL)', () {},
        skip: true);
    return;
  }

  late DioApiClient api;
  late SuggestionRemoteDataSource remote;
  late SuggestionRepositoryImpl repo;

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
      name: 'Recommendations Live',
    );
    final session = await auth.verifyRegisterAndLogin(
      phone: phone,
      otp: '123456',
      password: password,
    );
    session.fold((f) => fail('sign-in failed: $f'), (_) {});

    remote = SuggestionRemoteDataSource(api);
    repo = SuggestionRepositoryImpl(
      remote,
      dishRemote: DishRemoteDataSource(api),
    );
  });

  test('POST /recommendations returns RecommendationListResponseDTO shape',
      () async {
    const request = SuggestionRequest(
      request: 'Gợi ý món ăn tối nay nhiều rau',
    );

    final response = await remote.fetch(request);

    expect(response.request, 'Gợi ý món ăn tối nay nhiều rau');
    expect(response.analysis.isMock, isTrue);
    expect(response.analysis.intent, isNotEmpty);
    expect(response.analysis.summary, isNotEmpty);
    expect(response.items, isNotEmpty);
    expect(response.items.length, inInclusiveRange(1, 5));

    final first = response.items.first;
    expect(first.recipeId, isNotEmpty);
    expect(first.recipeName, isNotEmpty);
    expect(first.rank, 1);
    expect(first.score, inInclusiveRange(0.0, 1.0));
    expect(first.scoreComponents.expirationUtilization, inInclusiveRange(0.0, 1.0));
    expect(first.scoreComponents.availability, inInclusiveRange(0.0, 1.0));
    expect(first.scoreComponents.preferenceFit, inInclusiveRange(0.0, 1.0));
    expect(first.scoreComponents.purchaseMinimization, inInclusiveRange(0.0, 1.0));
    expect(first.explanation, isNotEmpty);
    expect(first.provider, isNotEmpty);
  });

  test('SuggestionRepositoryImpl.fetch maps recommendations into DishSuggestion with recipes',
      () async {
    const request = SuggestionRequest(
      mealType: MealType.dinner,
      maxCookTimeMin: 30,
    );

    final result = await repo.fetch(request);
    final suggestions =
        result.fold((f) => fail('fetch recommendations failed: $f'), (s) => s);

    expect(suggestions, isNotEmpty);
    expect(suggestions.length, inInclusiveRange(1, 5));

    final first = suggestions.first;
    expect(first.id, isNotEmpty);
    expect(first.dish.name, isNotEmpty);
    expect(first.score, inInclusiveRange(0, 100));
    expect(first.breakdown.e, inInclusiveRange(0.0, 1.0));
    expect(first.breakdown.a, inInclusiveRange(0.0, 1.0));
    expect(first.breakdown.p, inInclusiveRange(0.0, 1.0));
    expect(first.breakdown.u, inInclusiveRange(0.0, 1.0));
    expect(first.isMock, isTrue);
  });
}
