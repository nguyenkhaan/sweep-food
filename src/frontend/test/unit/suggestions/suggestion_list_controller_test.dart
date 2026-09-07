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
    test('defaults to "Gợi ý món ăn hôm nay" when fields are empty', () {
      const req = SuggestionRequest();
      expect(req.toBody(), {'request': 'Gợi ý món ăn hôm nay'});
    });

    test('combines meal, time, preference, and prompt into request string', () {
      const req = SuggestionRequest(
        prompt: 'Món cay',
        mealType: MealType.dinner,
        maxCookTimeMin: 30,
        dietaryPreference: DietaryPreference.moreVeg,
      );
      expect(req.toBody(), {
        'request': 'Món cay, Bữa tối, Nấu nhanh ≤ 30 phút, Nhiều rau',
      });
    });

    test('uses explicit request if provided', () {
      const req = SuggestionRequest(
        request: 'Canh rau ngót nấu tôm',
      );
      expect(req.toBody(), {'request': 'Canh rau ngót nấu tôm'});
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

    test('maps RecommendationListResponseDTO to DishSuggestion with parallel recipe fetch', () async {
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
    });

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

      when(() => dishRemote.getById('d99')).thenThrow(Exception('404 Not Found'));

      final res = await repo.fetch(const SuggestionRequest());
      final list = res.fold((f) => fail('expected Right, got $f'), (r) => r);

      expect(list, hasLength(1));
      expect(list.single.id, 'd99');
      expect(list.single.dish.name, 'Món chưa đồng bộ');
      expect(list.single.score, 88);
    });

    test('supports embedded dish payload (legacy or mocked test fixture)', () async {
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
    });

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
}
