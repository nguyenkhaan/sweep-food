import 'package:flutter_test/flutter_test.dart';
import 'package:mocktail/mocktail.dart';
import 'package:sweepfood/core/network/api_client.dart';
import 'package:sweepfood/core/network/api_paths.dart';
import 'package:sweepfood/features/cooking/data/datasources/cooking_remote_data_source.dart';
import 'package:sweepfood/features/cooking/data/repositories/cooking_repository_impl.dart';
import 'package:sweepfood/features/cooking/domain/entities/cook_confirmation.dart';
import 'package:sweepfood/features/cooking/domain/entities/cooking_history.dart';
import 'package:sweepfood/shared/domain/measurement_unit.dart';

class _MockApiClient extends Mock implements ApiClient {}

void main() {
  late _MockApiClient api;
  late CookingRepositoryImpl repo;

  setUp(() {
    api = _MockApiClient();
    repo = CookingRepositoryImpl(CookingRemoteDataSource(api));
  });

  group('history()', () {
    test('maps GET /cooking/history rows to entries', () async {
      when(() => api.get(ApiPaths.cookingHistory)).thenAnswer(
        (_) async => {
          'items': [
            {
              'session_id': 's1',
              'recipe_id': 'r1',
              'recipe_name': 'Salad bơ ức gà',
              'servings': 2.0,
              'status': 'COMPLETED',
              'completed_at': '2026-09-01T18:30:00.000Z',
            },
            {
              'session_id': 's2',
              'recipe_id': 'r2',
              'recipe_name': 'Canh chua',
              // Decimal serialized as a JSON string.
              'servings': '3.0',
              'status': 'CANCELLED',
              'completed_at': null,
            },
          ],
        },
      );

      final res = await repo.history();
      final list = res.fold((f) => fail('expected Right, got $f'), (r) => r);

      expect(list, hasLength(2));
      expect(list.first.sessionId, 's1');
      expect(list.first.recipeName, 'Salad bơ ức gà');
      expect(list.first.servings, 2.0);
      expect(list.first.status, CookingSessionStatus.completed);
      expect(list[1].servings, 3.0);
      expect(list[1].status, CookingSessionStatus.cancelled);
      expect(list[1].completedAt, isNull);
    });

    test('returns a Failure when the client throws', () async {
      when(() => api.get(ApiPaths.cookingHistory))
          .thenThrow(Exception('offline'));
      final res = await repo.history();
      expect(res.isLeft(), isTrue);
    });
  });

  group('historyDetail()', () {
    test('flattens the nested session + consumptions shape', () async {
      when(() => api.get(ApiPaths.cookingHistoryDetail('s1'))).thenAnswer(
        (_) async => {
          'session': {
            'id': 's1',
            'recipe_id': 'r1',
            'meal_plan_item_id': 'mpi1',
            'servings': 2.0,
            'status': 'COMPLETED',
            'consumption_mode': 'HALF',
            'nutrition_snapshot': <String, dynamic>{},
            'completed_at': '2026-09-01T18:30:00.000Z',
          },
          'recipe_id': 'r1',
          'recipe_name': 'Salad bơ ức gà',
          'consumptions': [
            {
              'recipe_ingredient_id': 'ri1',
              'inventory_batch_id': 'b3',
              'quantity': 100.0,
              'unit': 'GRAM',
            },
          ],
          'leftover_batch_id': 'b99',
          'completed_at': '2026-09-01T18:30:00.000Z',
        },
      );

      final res = await repo.historyDetail('s1');
      final d = res.fold((f) => fail('expected Right, got $f'), (r) => r);

      expect(d.sessionId, 's1');
      expect(d.recipeName, 'Salad bơ ức gà');
      expect(d.servings, 2.0);
      expect(d.consumptionMode, CookMode.half);
      expect(d.leftoverBatchId, 'b99');
      expect(d.consumptions, hasLength(1));
      expect(d.consumptions.first.inventoryBatchId, 'b3');
      expect(d.consumptions.first.quantity, 100.0);
      expect(d.consumptions.first.unit, MeasurementUnit.gram);
    });
  });
}
