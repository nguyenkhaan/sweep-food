import 'package:flutter_test/flutter_test.dart';
import 'package:mocktail/mocktail.dart';
import 'package:sweepfood/core/network/api_paths.dart';
import 'package:sweepfood/core/utils/result.dart';
import 'package:sweepfood/features/dishes/data/datasources/dish_remote_data_source.dart';
import 'package:sweepfood/features/pantry/data/repositories/pantry_repository_impl.dart';
import 'package:sweepfood/features/pantry/domain/entities/pantry_item.dart';
import 'package:sweepfood/features/pantry/domain/repositories/pantry_repository.dart';
import 'package:sweepfood/features/suggestions/data/datasources/suggestion_remote_data_source.dart';
import 'package:sweepfood/features/suggestions/data/repositories/suggestion_repository_impl.dart';
import 'package:sweepfood/features/suggestions/domain/entities/dish_suggestion.dart';
import 'package:sweepfood/features/suggestions/domain/entities/suggestion_request.dart';
import 'package:sweepfood/features/suggestions/presentation/controllers/suggestion_list_controller.dart';
import 'package:sweepfood/shared/domain/measurement_unit.dart';
import 'package:sweepfood/shared/domain/paginated.dart';
import 'package:sweepfood/shared/domain/storage_tier.dart';

import '../../helpers/mocks.dart';
import '../../helpers/test_providers.dart';

class MockDishRemoteDataSource extends Mock implements DishRemoteDataSource {}

void main() {
  setUpAll(() => registerFallbackValue(const SuggestionRequest()));

  group('SuggestionRequest.toBody()', () {
    test('emits the complete recommendation v2 body', () {
      const req = SuggestionRequest();
      expect(req.toBody(), {
        'items': <dynamic>[],
        'household_size': 4.0,
        'max_cooking_time_min': 45.0,
        'scenario_type': 'custom',
        'dietary_restrictions': <String>[],
        'allergies': <String>[],
        'disliked_ingredients': <String>[],
        'preferred_cuisines': <String>[],
      });
    });

    test('serializes pantry quantities and typed preferences', () {
      const req = SuggestionRequest(
        items: [
          RecommendationPantryItem(
            name: 'Cà chua',
            code: '4001',
            quantityG: 300,
            hoursToExpire: 12,
          ),
        ],
        householdSize: 2,
        maxCookTimeMin: 30,
        scenarioType: 'quick_meal',
        dietaryRestrictions: ['vegetarian'],
        allergies: ['peanut'],
      );
      expect(req.toBody(), {
        'items': [
          {
            'name': 'Cà chua',
            'code': '4001',
            'quantity_g': 300.0,
            'hours_to_expire': 12.0,
            'is_staple': false,
          },
        ],
        'household_size': 2.0,
        'max_cooking_time_min': 30.0,
        'scenario_type': 'quick_meal',
        'dietary_restrictions': ['vegetarian'],
        'allergies': ['peanut'],
        'disliked_ingredients': <String>[],
        'preferred_cuisines': <String>[],
      });
    });

    test('converts kg to grams and does not invent count-unit weights', () {
      final now = DateTime.utc(2026, 10, 13, 12);
      final kg = _pantryItem(
        name: 'Thịt bò',
        quantity: 0.5,
        unit: MeasurementUnit.kilogram,
        expiryDate: now.add(const Duration(hours: 18)),
      );
      final piece = _pantryItem(
        name: 'Trứng',
        quantity: 4,
        unit: MeasurementUnit.piece,
      );

      final kgItem = RecommendationPantryItem.fromPantryItem(kg, now: now);
      final pieceItem = RecommendationPantryItem.fromPantryItem(
        piece,
        now: now,
      );

      expect(kgItem?.quantityG, 500);
      expect(kgItem?.hoursToExpire, 18);
      expect(pieceItem, isNull);
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
      'maps recommendation v2 ranking and embedded recipe summary',
      () async {
        when(
          () => api.post(ApiPaths.recommendations, body: any(named: 'body')),
        ).thenAnswer(
          (_) async => {
            'request': {'items': <dynamic>[]},
            'contract_version': '2',
            'model_version': 'lgbm-contextual-v1',
            'catalog_revision': 'catalog-test',
            'ranker_model': 'LightGBM LambdaMART',
            'timings': {
              'total_ms': 20.1,
              'candidate_ms': 2.3,
              'ranker_ms': 4.8,
            },
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
                'rank_score': 1.86,
                'ranking_features': {
                  'core_coverage': 0.9,
                  'core_missing_count': 0,
                  'secondary_coverage': 0.8,
                  'shopping_gap_items': 2,
                  'rescue_weight_g': 300,
                  'nutrition_confidence': 0.9,
                  'kcal_per_serving': 350,
                  'protein_per_serving': 20,
                  'prep_complexity': 2.5,
                },
                'matched_ingredients': <dynamic>[],
                'missing_ingredients': [
                  {'name': 'Xà lách', 'code': '4002', 'required_g': 150.0},
                  {'name': 'Dầu ô liu', 'code': '4003', 'required_g': 15.0},
                ],
                'optional_ingredients': <dynamic>[],
                'rescued_items': ['Bơ', 'Ức gà'],
                'status_badge': 'ready',
                'explanation': 'Tận dụng bơ và ức gà sắp hết hạn.',
                'provider': 'SWEEP_FOOD_AI',
                'recipe_summary': {
                  'id': 'd1',
                  'name': 'Salad bơ ức gà',
                  'media_url': null,
                  'estimated_cooking_minutes': 15,
                  'default_servings': 2,
                  'nutrition': {
                    'calories': 600,
                    'protein_g': 40,
                    'fat_g': 20,
                    'carbs_g': 30,
                    'sugar_g': 5,
                  },
                },
              },
            ],
            'warnings': <String>[],
          },
        );

        final res = await repo.fetch(const SuggestionRequest());
        final list = res.fold((f) => fail('expected Right, got $f'), (r) => r);

        expect(list, hasLength(1));
        final s = list.single;
        expect(s.id, 'd1');
        expect(s.dish.name, 'Salad bơ ức gà');
        expect(s.dish.cookTimeMin, 15);
        expect(s.rank, 1);
        expect(s.rankScore, 1.86);
        expect(s.usesRankingV2, isTrue);
        expect(s.nearExpiryCount, 2);
        expect(s.availabilityPercent, 90);
        expect(s.toBuyCount, 2);
        expect(s.rankingFeatures?.rescueWeightG, 300);
        expect(s.explanation, 'Tận dụng bơ và ức gà sắp hết hạn.');
        expect(s.isMock, isTrue);

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
      final pantryRepo = MockPantryRepository();
      SuggestionRequest? captured;
      when(() => repo.fetch(any())).thenAnswer((invocation) async {
        captured = invocation.positionalArguments.single as SuggestionRequest;
        return const Right(<DishSuggestion>[]);
      });
      when(
        () => pantryRepo.list(
          status: PantryItemStatus.active,
          sort: PantrySort.priority,
          page: 1,
          tier: null,
        ),
      ).thenAnswer(
        (_) async => Right(Paginated.single([_pantryItem(name: 'Cà chua')])),
      );

      final container = createContainer(
        overrides: [
          suggestionRepositoryProvider.overrideWithValue(repo),
          pantryRepositoryProvider.overrideWithValue(pantryRepo),
        ],
      );

      await container.read(suggestionListControllerProvider.future);
      expect(captured, isNotNull);
      expect(captured!.mealType, isNull);
      expect(captured!.items.single.name, 'Cà chua');

      container
          .read(suggestionFilterControllerProvider.notifier)
          .toggleMeal(MealType.dinner);
      await container.read(suggestionListControllerProvider.future);

      expect(captured!.mealType, MealType.dinner);
      verify(() => repo.fetch(any())).called(2);
    });
  });
}

PantryItem _pantryItem({
  String name = 'Cà chua',
  double quantity = 300,
  MeasurementUnit unit = MeasurementUnit.gram,
  DateTime? expiryDate,
}) => PantryItem(
  id: 'batch-1',
  name: name,
  category: 'Rau củ',
  quantity: quantity,
  unit: unit,
  storageTier: StorageTier.fridge,
  addedAt: DateTime.utc(2026, 10, 13),
  source: PantrySource.manual,
  status: PantryItemStatus.active,
  ingredientId: '4001',
  expiryDate: expiryDate,
);
