import 'package:flutter_test/flutter_test.dart';
import 'package:mocktail/mocktail.dart';
import 'package:sweepfood/core/network/api_client.dart';
import 'package:sweepfood/core/network/api_paths.dart';
import 'package:sweepfood/features/pantry/data/datasources/pantry_remote_data_source.dart';
import 'package:sweepfood/features/pantry/data/repositories/pantry_repository_impl.dart';
import 'package:sweepfood/features/pantry/domain/entities/inventory_ledger.dart';
import 'package:sweepfood/shared/domain/measurement_unit.dart';

class _MockApiClient extends Mock implements ApiClient {}

Map<String, dynamic> _row({
  required String id,
  String batchId = 'b1',
  String eventType = 'MANUAL_CONSUMPTION',
  Object before = 300,
  Object delta = -100,
  Object after = 200,
  String unit = 'GRAM',
  String? reason,
}) => {
      'id': id,
      'inventory_batch_id': batchId,
      'event_type': eventType,
      'quantity_before': before,
      'quantity_delta': delta,
      'quantity_after': after,
      'unit': unit,
      'reason': reason,
      'created_at': '2026-09-01T18:30:00.000Z',
    };

void main() {
  late _MockApiClient api;
  late PantryRepositoryImpl repo;

  setUp(() {
    api = _MockApiClient();
    repo = PantryRepositoryImpl(PantryRemoteDataSource(api));
  });

  group('ledger()', () {
    test('maps GET /inventory/ledger rows to entities', () async {
      when(() => api.get(ApiPaths.inventoryLedger, query: any(named: 'query')))
          .thenAnswer(
        (_) async => {
          'items': [
            _row(
              id: 'l1',
              eventType: 'INITIAL_STOCK',
              before: 0,
              delta: 300,
              after: 300,
              reason: 'Nhập kho ban đầu',
            ),
            // Decimals serialized as JSON strings (pydantic Decimal).
            _row(
              id: 'l2',
              eventType: 'COOKING_CONSUMPTION',
              before: '300.0',
              delta: '-200.0',
              after: '100.0',
            ),
          ],
          'total': 2,
          'page': 1,
          'per_page': 30,
        },
      );

      final res = await repo.ledger();
      final page = res.fold((f) => fail('expected Right, got $f'), (r) => r);

      expect(page.items, hasLength(2));
      expect(page.items.first.id, 'l1');
      expect(page.items.first.eventType, LedgerEventType.initialStock);
      expect(page.items.first.quantityDelta, 300);
      expect(page.items.first.isIncrease, isTrue);
      expect(page.items.first.unit, MeasurementUnit.gram);
      expect(page.items.first.reason, 'Nhập kho ban đầu');
      // String decimals parsed.
      expect(page.items[1].eventType, LedgerEventType.cookingConsumption);
      expect(page.items[1].quantityBefore, 300.0);
      expect(page.items[1].quantityDelta, -200.0);
      expect(page.items[1].quantityAfter, 100.0);
      expect(page.items[1].isIncrease, isFalse);
      // Everything on one page → no more.
      expect(page.hasMore, isFalse);
      expect(page.nextPage, isNull);
    });

    test('reports another page when total exceeds what is loaded', () async {
      when(() => api.get(ApiPaths.inventoryLedger, query: any(named: 'query')))
          .thenAnswer(
        (_) async => {
          'items': [for (var i = 0; i < 30; i++) _row(id: 'l$i')],
          'total': 74,
          'page': 1,
          'per_page': 30,
        },
      );

      final res = await repo.ledger();
      final page = res.fold((f) => fail('expected Right, got $f'), (r) => r);

      expect(page.items, hasLength(30));
      expect(page.hasMore, isTrue);
      expect(page.nextPage, 2);
    });

    test('forwards the batch_id filter to the query', () async {
      when(() => api.get(ApiPaths.inventoryLedger, query: any(named: 'query')))
          .thenAnswer(
        (_) async => {'items': <dynamic>[], 'total': 0, 'page': 1, 'per_page': 30},
      );

      await repo.ledger(batchId: 'batch-42', eventType: LedgerEventType.moved);

      final captured = verify(
        () => api.get(ApiPaths.inventoryLedger, query: captureAny(named: 'query')),
      ).captured.single as Map<String, dynamic>;
      expect(captured['batch_id'], 'batch-42');
      expect(captured['event_type'], 'MOVED');
      expect(captured['page'], 1);
    });

    test('returns a Failure when the client throws', () async {
      when(() => api.get(ApiPaths.inventoryLedger, query: any(named: 'query')))
          .thenThrow(Exception('offline'));
      final res = await repo.ledger();
      expect(res.isLeft(), isTrue);
    });
  });
}
