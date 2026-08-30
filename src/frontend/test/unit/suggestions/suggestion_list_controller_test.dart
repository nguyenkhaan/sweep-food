import 'package:flutter_test/flutter_test.dart';
import 'package:frontend/core/network/api_paths.dart';
import 'package:frontend/core/utils/result.dart';
import 'package:frontend/features/suggestions/data/datasources/suggestion_remote_data_source.dart';
import 'package:frontend/features/suggestions/data/repositories/suggestion_repository_impl.dart';
import 'package:frontend/features/suggestions/domain/entities/dish_suggestion.dart';
import 'package:frontend/features/suggestions/domain/entities/suggestion_request.dart';
import 'package:frontend/features/suggestions/presentation/controllers/suggestion_list_controller.dart';
import 'package:mocktail/mocktail.dart';

import '../../helpers/mocks.dart';
import '../../helpers/test_providers.dart';

void main() {
  setUpAll(() => registerFallbackValue(const SuggestionRequest()));

  group('SuggestionRepositoryImpl.fetch()', () {
    late MockApiClient api;
    late SuggestionRepositoryImpl repo;

    setUp(() {
      api = MockApiClient();
      repo = SuggestionRepositoryImpl(SuggestionRemoteDataSource(api));
    });

    test('maps the payload to DishSuggestion entities', () async {
      when(
        () => api.post(ApiPaths.suggestions, body: any(named: 'body')),
      ).thenAnswer(
        (_) async => {
          'items': [
            {
              'score': 95,
              'availability_ratio': 0.8,
              'to_buy_count': 2,
              'near_expiry_ingredients': ['Bơ', 'Ức gà'],
              'breakdown': {'e': 0.9, 'a': 0.8, 'p': 0.7, 'u': 0.6},
              'dish': {
                'id': 'd1',
                'name': 'Salad bơ ức gà',
                'servings': 2,
                'prep_time_min': 15,
                'cook_time_min': 10,
                'nutrition_per_serving': {'energy_kcal': 320, 'protein_g': 28},
              },
            },
          ],
        },
      );

      final res = await repo.fetch(const SuggestionRequest());
      final list = res.fold((f) => fail('expected Right, got $f'), (r) => r);

      expect(list, hasLength(1));
      final s = list.single;
      expect(s.id, 'd1');
      expect(s.dish.name, 'Salad bơ ức gà');
      expect(s.score, 95); // server override wins over the computed value
      expect(s.nearExpiryCount, 2);
      expect(s.availabilityPercent, 80);
      expect(s.toBuyCount, 2);
      expect(s.breakdown.e, 0.9);
    });

    test('falls back to the computed score when the server omits it', () async {
      when(
        () => api.post(ApiPaths.suggestions, body: any(named: 'body')),
      ).thenAnswer(
        (_) async => {
          'items': [
            {
              'breakdown': {'e': 1.0, 'a': 1.0, 'p': 1.0, 'u': 1.0},
              'dish': {
                'id': 'd9',
                'name': 'Món đủ điểm',
                'servings': 1,
                'prep_time_min': 1,
                'cook_time_min': 1,
              },
            },
          ],
        },
      );

      final res = await repo.fetch(const SuggestionRequest());
      final list = res.fold((f) => fail('expected Right, got $f'), (r) => r);
      expect(list.single.score, 100); // 0.4+0.3+0.2+0.1 = 1.0 -> 100
    });

    test('returns a Failure (Left) when the client throws', () async {
      when(
        () => api.post(ApiPaths.suggestions, body: any(named: 'body')),
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
