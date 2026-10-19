@Tags(['live'])
library;

/// Exercises the recommendations data layer (POST /recommendations + DTO parsing +
/// embedded recipe-summary mapping) against a running backend and SweepFood AI.
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
    test(
      'live recommendations (skipped: set --dart-define=LIVE_BASE_URL)',
      () {},
      skip: true,
    );
    return;
  }

  late DioApiClient api;
  late SuggestionRemoteDataSource remote;
  late SuggestionRepositoryImpl repo;

  setUpAll(() async {
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

  test(
    'POST /recommendations returns RecommendationListResponseDTO shape',
    () async {
      const request = SuggestionRequest(
        pantryItems: [
          RecommendationPantryItemDraft(
            name: 'thịt bò',
            quantityG: 300,
            hoursToExpire: 12,
          ),
          RecommendationPantryItemDraft(
            name: 'cà chua',
            quantityG: 200,
            hoursToExpire: 36,
          ),
        ],
        householdSize: 2,
      );

      final response = await remote.fetch(request);

      expect(response.request['household_size'], 2.0);
      expect(response.contractVersion, '2');
      expect(response.modelVersion, isNotEmpty);
      expect(response.rankerModel, contains('LightGBM'));
      expect(response.timings.totalMs, greaterThanOrEqualTo(0));
      expect(response.analysis.isMock, isFalse);
      expect(response.analysis.intent, isNotEmpty);
      expect(response.analysis.summary, isNotEmpty);
      expect(response.items, isNotEmpty);
      expect(response.items.length, inInclusiveRange(1, 7));

      final first = response.items.first;
      expect(first.recipeId, isNotEmpty);
      expect(first.recipeName, isNotEmpty);
      expect(first.rank, 1);
      expect(first.rankScore.isFinite, isTrue);
      expect(first.rankingFeatures.coreCoverage, inInclusiveRange(0.0, 1.0));
      expect(
        first.rankingFeatures.secondaryCoverage,
        inInclusiveRange(0.0, 1.0),
      );
      expect(
        first.rankingFeatures.nutritionConfidence,
        inInclusiveRange(0.0, 1.0),
      );
      expect(first.statusBadge, isNotEmpty);
      expect(first.dish, isNotNull);
      expect(first.explanation, isNotEmpty);
      expect(first.provider, isNotEmpty);
    },
    timeout: const Timeout(Duration(minutes: 2)),
  );

  test(
    'SuggestionRepositoryImpl.fetch maps recommendations into DishSuggestion with recipes',
    () async {
      const request = SuggestionRequest(
        pantryItems: [
          RecommendationPantryItemDraft(name: 'thịt bò', quantityG: 300),
          RecommendationPantryItemDraft(name: 'cà chua', quantityG: 200),
        ],
        mealType: MealType.dinner,
        maxCookTimeMin: 30,
      );

      final result = await repo.fetch(request);
      final suggestions = result.fold(
        (f) => fail('fetch recommendations failed: $f'),
        (s) => s,
      );

      expect(suggestions, isNotEmpty);
      expect(suggestions.length, inInclusiveRange(1, 7));

      final first = suggestions.first;
      expect(first.id, isNotEmpty);
      expect(first.dish.name, isNotEmpty);
      expect(first.rank, 1);
      expect(first.rankScore.isFinite, isTrue);
      expect(first.score, inInclusiveRange(0, 100));
      expect(first.breakdown.e, inInclusiveRange(0.0, 1.0));
      expect(first.breakdown.a, inInclusiveRange(0.0, 1.0));
      expect(first.breakdown.p, inInclusiveRange(0.0, 1.0));
      expect(first.breakdown.u, inInclusiveRange(0.0, 1.0));
      expect(first.modelVersion, isNotEmpty);
      expect(first.rankerModel, contains('LightGBM'));
      expect(first.isMock, isFalse);
    },
    timeout: const Timeout(Duration(minutes: 2)),
  );
}
