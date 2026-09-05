import 'package:flutter_test/flutter_test.dart';
import 'package:mocktail/mocktail.dart';
import 'package:sweepfood/core/network/api_client.dart';
import 'package:sweepfood/core/network/api_paths.dart';
import 'package:sweepfood/features/meal_plan/data/datasources/meal_plan_remote_data_source.dart';
import 'package:sweepfood/features/meal_plan/data/repositories/meal_plan_repository_impl.dart';
import 'package:sweepfood/features/meal_plan/domain/entities/meal_plan_entry.dart';

class _MockApiClient extends Mock implements ApiClient {}

void main() {
  late _MockApiClient api;
  late MealPlanRepositoryImpl repo;
  final monday = DateTime(2026, 8, 31);

  setUp(() {
    api = _MockApiClient();
    repo = MealPlanRepositoryImpl(MealPlanRemoteDataSource(api));
  });

  group('forWeek()', () {
    test('creates a new plan when no existing plan matches the week', () async {
      when(
        () => api.get(ApiPaths.mealPlansList, query: any(named: 'query')),
      ).thenAnswer((_) async => {'items': <dynamic>[], 'total': 0});
      when(
        () => api.post(ApiPaths.mealPlans, body: any(named: 'body')),
      ).thenAnswer(
        (_) async => {
          'id': 'plan-1',
          'starts_on': '2026-08-31',
          'ends_on': '2026-09-06',
          'items': <dynamic>[],
        },
      );
      when(
        () => api.get(ApiPaths.mealPlan('plan-1')),
      ).thenAnswer(
        (_) async => {
          'id': 'plan-1',
          'starts_on': '2026-08-31',
          'ends_on': '2026-09-06',
          'items': <dynamic>[],
        },
      );

      final res = await repo.forWeek(monday);

      final plan = res.fold((f) => fail('expected Right, got $f'), (r) => r);
      expect(plan.weekStart, monday);
      expect(plan.entries, isEmpty);
      verify(
        () => api.post(
          ApiPaths.mealPlans,
          body: {'starts_on': '2026-08-31', 'ends_on': '2026-09-06'},
        ),
      ).called(1);
    });

    test('reuses an existing plan matching starts_on instead of creating one', () async {
      when(
        () => api.get(ApiPaths.mealPlansList, query: any(named: 'query')),
      ).thenAnswer(
        (_) async => {
          'items': [
            {'id': 'plan-existing', 'starts_on': '2026-08-31', 'ends_on': '2026-09-06'},
          ],
          'total': 1,
        },
      );
      when(
        () => api.get(ApiPaths.mealPlan('plan-existing')),
      ).thenAnswer(
        (_) async => {
          'id': 'plan-existing',
          'starts_on': '2026-08-31',
          'ends_on': '2026-09-06',
          'items': [
            {
              'id': 'item-1',
              'recipe_id': 'd1',
              'recipe_name': 'Salad bơ ức gà',
              'planned_for': '2026-09-02',
              'meal_slot': 'LUNCH',
              'servings': 2.0,
              'status': 'PLANNED',
            },
          ],
        },
      );

      final res = await repo.forWeek(monday);

      final plan = res.fold((f) => fail('expected Right, got $f'), (r) => r);
      expect(plan.entries, hasLength(1));
      expect(plan.entries.single.dishName, 'Salad bơ ức gà');
      expect(plan.entries.single.slot, MealSlot.lunch);
      verifyNever(() => api.post(ApiPaths.mealPlans, body: any(named: 'body')));
    });
  });

  group('addEntry()', () {
    test('resolves the plan then posts the item', () async {
      when(
        () => api.get(ApiPaths.mealPlansList, query: any(named: 'query')),
      ).thenAnswer(
        (_) async => {
          'items': [
            {'id': 'plan-1', 'starts_on': '2026-08-31', 'ends_on': '2026-09-06'},
          ],
        },
      );
      when(
        () => api.post(ApiPaths.mealPlanItems('plan-1'), body: any(named: 'body')),
      ).thenAnswer(
        (_) async => {
          'id': 'item-9',
          'recipe_id': 'd2',
          'recipe_name': null,
          'planned_for': '2026-09-01',
          'meal_slot': 'DINNER',
          'servings': 3.0,
          'status': 'PLANNED',
        },
      );

      final res = await repo.addEntry(
        weekStart: monday,
        date: DateTime(2026, 9, 1),
        slot: MealSlot.dinner,
        dishId: 'd2',
        servings: 3,
        dishName: 'Canh chua cá lóc',
      );

      final entry = res.fold((f) => fail('expected Right, got $f'), (r) => r);
      expect(entry.id, 'item-9');
      // recipe_name is null in the response -> falls back to the caller's dishName.
      expect(entry.dishName, 'Canh chua cá lóc');

      final body = verify(
        () => api.post(
          ApiPaths.mealPlanItems('plan-1'),
          body: captureAny(named: 'body'),
        ),
      ).captured.single as Map<String, dynamic>;
      expect(body['meal_slot'], 'DINNER');
      expect(body['planned_for'], '2026-09-01');
    });
  });
}
