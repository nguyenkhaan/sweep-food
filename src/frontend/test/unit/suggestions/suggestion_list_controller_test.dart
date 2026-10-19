import 'package:flutter_test/flutter_test.dart';
import 'package:mocktail/mocktail.dart';
import 'package:sweepfood/core/network/api_paths.dart';
import 'package:sweepfood/core/utils/result.dart';
import 'package:sweepfood/features/dishes/data/datasources/dish_remote_data_source.dart';
import 'package:sweepfood/features/dishes/data/models/recipe_dto.dart';
import 'package:sweepfood/features/suggestions/data/datasources/suggestion_remote_data_source.dart';
import 'package:sweepfood/features/suggestions/data/repositories/suggestion_repository_impl.dart';
import 'package:sweepfood/features/suggestions/domain/entities/dish_suggestion.dart';
import 'package:sweepfood/features/suggestions/domain/entities/suggestion_request.dart';
import 'package:sweepfood/features/suggestions/presentation/controllers/suggestion_list_controller.dart';
import 'package:sweepfood/shared/domain/dietary_preference.dart';

import '../../helpers/mocks.dart';
import '../../helpers/test_providers.dart';

class MockDishRemoteDataSource extends Mock implements DishRemoteDataSource {}

void main() {
  setUpAll(() => registerFallbackValue(const SuggestionRequest()));

  group('SuggestionRequest.toBody()', () {
    test(
      'defaults to empty items and standard defaults when fields are empty',
      () {
        const req = SuggestionRequest();
        expect(req.toBody(), {
          'items': [],
          'household_size': 4.0,
          'scenario_type': 'custom',
          'dietary_restrictions': [],
          'allergies': [],
          'disliked_ingredients': [],
          'preferred_cuisines': [],
        });
      },
    );

    test(
      'combines meal, preference, and pantry items into request body',
      () {
        const req = SuggestionRequest(
          prompt: 'Món cay',
          mealType: MealType.dinner,
          dietaryPreference: DietaryPreference.moreVeg,
          pantryItems: [
            RecommendationPantryItemDraft(
              name: 'Rau chân vịt',
              code: 'ing-1',
              quantityG: 300,
              hoursToExpire: 12,
            ),
          ],
        );
        expect(req.toBody(), {
          'items': [
            {
              'name': 'Rau chân vịt',
              'code': 'ing-1',
              'quantity_g': 300.0,
              'hours_to_expire': 12.0,
              'is_staple': false,
            },
          ],
          'household_size': 4.0,
          'scenario_type': 'dinner',
          'dietary_restrictions': ['vegetarian'],
          'allergies': [],
          'disliked_ingredients': [],
          'preferred_cuisines': [],
        });
      },
    );

    test('never includes max_cooking_time_min in the request body', () {
      const req = SuggestionRequest();
      expect(req.toBody().containsKey('max_cooking_time_min'), isFalse);
    });
  });

  group('SuggestionRepositoryImpl.fetch()', () {
    late MockApiClient api;
    late MockDishRemoteDataSource dishRemote;
    late SuggestionRepositoryImpl repo;

    setUp(() {
      api = MockApiClient();
      dishRemote = MockDishRemoteDataSource();
      repo = SuggestionRepositoryImpl(
        SuggestionRemoteDataSource(api),
        dishRemote: dishRemote,
      );
    });

    test(
      'maps RecommendationListResponseDTO to DishSuggestion with parallel recipe fetch',
      () async {
        when(
          () => api.post(ApiPaths.recommendations, body: any(named: 'body')),
        ).thenAnswer(
          (_) async => {
            'request': 'Gợi ý món ăn hôm nay',
            'analysis': {
              'intent': 'meal_recommendation',
              'summary': 'Mock recommendation active',
              'is_mock': true,
            },
            'items': [
              {
                'recipe_id': 'd1',
                'recipe_name': 'Salad bơ ức gà',
                'rank': 1,
                'score': 0.95,
                'score_components': {
                  'expiration_utilization': 0.92,
                  'availability': 0.8,
                  'preference_fit': 0.74,
                  'purchase_minimization': 0.78,
                },
                'missing_ingredients': [
                  {
                    'master_ingredient_id': 'i-lettuce',
                    'name': 'Xà lách',
                    'quantity': 150.0,
                    'unit': 'GRAM',
                  },
                  {
                    'master_ingredient_id': 'i-olive-oil',
                    'name': 'Dầu ô liu',
                    'quantity': 15.0,
                    'unit': 'ML',
                  },
                ],
                'near_expiry_ingredients': ['Bơ', 'Ức gà'],
                'explanation': 'Tận dụng bơ và ức gà sắp hết hạn.',
                'provider': 'MOCK',
                'model_version': 'mock-v1',
              },
            ],
          },
        );

        when(() => dishRemote.getById('d1')).thenAnswer(
          (_) async => const RecipeDto(
            id: 'd1',
            name: 'Salad bơ ức gà',
            description: 'Salad trộn nhiều đạm',
            estimatedCookingMinutes: 15,
          ),
        );

        final res = await repo.fetch(const SuggestionRequest());
        final list = res.fold((f) => fail('expected Right, got $f'), (r) => r);

        expect(list, hasLength(1));
        final s = list.single;
        expect(s.id, 'd1');
        expect(s.dish.name, 'Salad bơ ức gà');
        expect(s.dish.cookTimeMin, 15);
        expect(s.score, 95);
        expect(s.nearExpiryCount, 2);
        expect(s.availabilityPercent, 80);
        expect(s.toBuyCount, 2);
        expect(s.breakdown.e, 0.92);
        expect(s.breakdown.a, 0.8);
        expect(s.breakdown.p, 0.74);
        expect(s.breakdown.u, 0.78);
        expect(s.explanation, 'Tận dụng bơ và ức gà sắp hết hạn.');
        expect(s.isMock, isTrue);

        verify(() => dishRemote.getById('d1')).called(1);
      },
    );

    test(
      'maps the exact AI v2 contract without treating rank score as percent',
      () async {
        when(
          () => api.post(ApiPaths.recommendations, body: any(named: 'body')),
        ).thenAnswer(
          (_) async => {
            'request': {
              'items': [
                {'name': 'Thịt bò', 'quantity_g': 300.0},
              ],
              'household_size': 2.0,
            },
            'contract_version': '2',
            'model_version': 'lgbm-contextual-v1',
            'catalog_revision': 'sha256:test',
            'ranker_model': 'LightGBM LambdaMART',
            'timings': {
              'total_ms': 20.1,
              'candidate_ms': 2.3,
              'ranker_ms': 4.8,
            },
            'analysis': {
              'intent': 'meal_recommendation',
              'summary': 'AI ranking',
              'is_mock': false,
            },
            'items': [
              {
                'recipe_id': 'r-ai-1',
                'recipe_name': 'Bò xào cà chua',
                'rank': 1,
                'rank_score': 4.1098,
                'ranking_features': {
                  'core_coverage': 0.9,
                  'core_missing_count': 0.0,
                  'secondary_coverage': 0.75,
                  'shopping_gap_items': 1.0,
                  'rescue_weight_g': 300.0,
                  'nutrition_confidence': 0.8,
                  'kcal_per_serving': 420.0,
                  'protein_per_serving': 32.0,
                  'prep_complexity': 2.5,
                },
                'matched_ingredients': [
                  {'name': 'Thịt bò', 'code': '7003', 'required_g': 250.0},
                ],
                'missing_ingredients': [
                  {'name': 'Hành tây', 'code': '4039', 'required_g': 50.0},
                ],
                'optional_ingredients': [],
                'rescued_items': ['Thịt bò'],
                'status_badge': 'elastic',
                'explanation': 'AI-ranked from pantry availability.',
                'provider': 'SWEEP_FOOD_AI',
                'recipe_summary': {
                  'id': 'r-ai-1',
                  'name': 'Bò xào cà chua',
                  'media_url': 'https://example.test/bo.jpg',
                  'estimated_cooking_minutes': 30,
                  'default_servings': '2.00',
                  'nutrition': {
                    'calories': '840.0',
                    'protein_g': '64.0',
                    'fat_g': '30.0',
                    'carbs_g': '40.0',
                  },
                },
              },
            ],
            'warnings': <String>[],
          },
        );

        final res = await repo.fetch(const SuggestionRequest());
        final suggestion = res.fold(
          (f) => fail('expected Right, got $f'),
          (items) => items.single,
        );

        expect(suggestion.rank, 1);
        expect(suggestion.rankScore, closeTo(4.1098, 0.0001));
        expect(suggestion.score, 90);
        expect(suggestion.rankingFeatures.coreCoverage, 0.9);
        expect(suggestion.rankingFeatures.rescueWeightG, 300);
        expect(suggestion.matchedIngredients.single.name, 'Thịt bò');
        expect(suggestion.missingIngredients.single.name, 'Hành tây');
        expect(suggestion.statusLabel, 'Thiếu nhẹ, có thể linh hoạt');
        expect(suggestion.modelVersion, 'lgbm-contextual-v1');
        expect(suggestion.rankerModel, 'LightGBM LambdaMART');
        expect(suggestion.dish.imageUrl, 'https://example.test/bo.jpg');
        expect(suggestion.dish.nutritionPerServing.energyKcal, 420);
        expect(suggestion.isMock, isFalse);
        verifyNever(() => dishRemote.getById(any()));
      },
    );

    test('falls back gracefully when recipe fetch fails', () async {
      when(
        () => api.post(ApiPaths.recommendations, body: any(named: 'body')),
      ).thenAnswer(
        (_) async => {
          'items': [
            {
              'recipe_id': 'd99',
              'recipe_name': 'Món chưa đồng bộ',
              'score': 0.88,
              'score_components': {
                'expiration_utilization': 0.8,
                'availability': 0.9,
                'preference_fit': 0.85,
                'purchase_minimization': 0.95,
              },
            },
          ],
        },
      );

      when(
        () => dishRemote.getById('d99'),
      ).thenThrow(Exception('404 Not Found'));

      final res = await repo.fetch(const SuggestionRequest());
      final list = res.fold((f) => fail('expected Right, got $f'), (r) => r);

      expect(list, hasLength(1));
      expect(list.single.id, 'd99');
      expect(list.single.dish.name, 'Món chưa đồng bộ');
      expect(list.single.score, 88);
    });

    test(
      'supports embedded dish payload (legacy or mocked test fixture)',
      () async {
        when(
          () => api.post(ApiPaths.recommendations, body: any(named: 'body')),
        ).thenAnswer(
          (_) async => {
            'items': [
              {
                'score': 90,
                'breakdown': {'e': 0.9, 'a': 0.8, 'p': 0.7, 'u': 0.6},
                'dish': {
                  'id': 'd2',
                  'name': 'Canh chua cá lóc',
                  'servings': 3,
                  'prep_time_min': 15,
                  'cook_time_min': 20,
                },
              },
            ],
          },
        );

        final res = await repo.fetch(const SuggestionRequest());
        final list = res.fold((f) => fail('expected Right, got $f'), (r) => r);

        expect(list, hasLength(1));
        expect(list.single.dish.name, 'Canh chua cá lóc');
        expect(list.single.score, 90);
        verifyNever(() => dishRemote.getById(any()));
      },
    );

    test('returns a Failure (Left) when the client throws', () async {
      when(
        () => api.post(ApiPaths.recommendations, body: any(named: 'body')),
      ).thenThrow(Exception('offline'));

      final res = await repo.fetch(const SuggestionRequest());
      expect(res.isLeft(), isTrue);
    });
  });

  group('SuggestionListController', () {
    test('loads from the repository with the current filter', () async {
      final repo = MockSuggestionRepository();
      SuggestionRequest? captured;
      when(() => repo.fetch(any())).thenAnswer((invocation) async {
        captured = invocation.positionalArguments.single as SuggestionRequest;
        return const Right(<DishSuggestion>[]);
      });

      final container = createContainer(
        overrides: [suggestionRepositoryProvider.overrideWithValue(repo)],
      );

      await container.read(suggestionListControllerProvider.future);
      expect(captured, isNotNull);
      expect(captured!.mealType, isNull);

      container
          .read(suggestionFilterControllerProvider.notifier)
          .toggleMeal(MealType.dinner);
      await container.read(suggestionListControllerProvider.future);

      expect(captured!.mealType, MealType.dinner);
      verify(() => repo.fetch(any())).called(2);
    });
  });

  group('AiServiceHealthDto', () {
    test('parses ready backend payload correctly', () {
      final dto = AiServiceHealthDto.fromJson({
        'status': 'ready',
        'catalog_revision': 'catalog-test-r1',
        'recipe_count': 100,
        'ranker_model': 'LightGBM LambdaMART',
        'model_version': 'lgbm-contextual-v3.1.0',
        'ocr_configured': true,
        'asr_configured': false,
        'latency_ms': 12.5,
      });

      expect(dto.isReady, isTrue);
      expect(dto.status, 'ready');
      expect(dto.catalogRevision, 'catalog-test-r1');
      expect(dto.recipeCount, 100);
      expect(dto.rankerModel, 'LightGBM LambdaMART');
      expect(dto.modelVersion, 'lgbm-contextual-v3.1.0');
      expect(dto.ocrConfigured, isTrue);
      expect(dto.asrConfigured, isFalse);
      expect(dto.latencyMs, 12.5);
    });

    test('handles fallback defaults defensively on unexpected/503 payload', () {
      final dto = AiServiceHealthDto.fromJson({
        'status_code': 503,
        'detail': 'AI catalog is not loaded.',
        'path': '/api/health/ai',
      });

      expect(dto.isReady, isFalse);
      expect(dto.status, '');
      expect(dto.catalogRevision, '');
      expect(dto.recipeCount, 0);
      expect(dto.rankerModel, '');
      expect(dto.modelVersion, '');
      expect(dto.ocrConfigured, isFalse);
      expect(dto.asrConfigured, isFalse);
      expect(dto.latencyMs, 0.0);
    });
  });
}
