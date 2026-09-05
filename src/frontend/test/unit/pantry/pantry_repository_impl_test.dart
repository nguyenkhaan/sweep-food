import 'package:flutter_test/flutter_test.dart';
import 'package:mocktail/mocktail.dart';
import 'package:sweepfood/core/network/api_client.dart';
import 'package:sweepfood/core/network/api_paths.dart';
import 'package:sweepfood/features/pantry/data/datasources/pantry_remote_data_source.dart';
import 'package:sweepfood/features/pantry/data/repositories/pantry_repository_impl.dart';
import 'package:sweepfood/features/pantry/domain/entities/pantry_item.dart';
import 'package:sweepfood/features/pantry/domain/entities/pantry_item_draft.dart';
import 'package:sweepfood/shared/domain/measurement_unit.dart';
import 'package:sweepfood/shared/domain/storage_tier.dart';

class _MockApiClient extends Mock implements ApiClient {}

void main() {
  late _MockApiClient api;
  late PantryRepositoryImpl repo;

  setUp(() {
    api = _MockApiClient();
    repo = PantryRepositoryImpl(PantryRemoteDataSource(api));
  });

  group('list()', () {
    test('maps the /inventory/batches payload to PantryItem entities', () async {
      when(
        () => api.get(ApiPaths.inventoryBatches, query: any(named: 'query')),
      ).thenAnswer(
        (_) async => {
          'items': [
            {
              'id': 'batch-1',
              'custom_name': 'Cà chua bi',
              'ingredient_name': 'Cà chua bi',
              'current_quantity': 250.0,
              'unit': 'GRAM',
              'storage_mode': 'REFRIGERATED',
              'status': 'ACTIVE',
              'source': 'MANUAL',
              'created_at': '2026-08-30T00:00:00.000Z',
              'expires_at': '2026-09-02T00:00:00.000Z',
            },
          ],
          'total': 1,
          'page': 1,
          'per_page': 100,
        },
      );

      final res = await repo.list();

      final page = res.fold((f) => fail('expected Right, got $f'), (r) => r);
      expect(page.items, hasLength(1));
      final item = page.items.single;
      expect(item.name, 'Cà chua bi');
      expect(item.quantity, 250.0);
      expect(item.unit, MeasurementUnit.gram);
      expect(item.storageTier, StorageTier.fridge);
      expect(item.source, PantrySource.manual);
      expect(item.status, PantryItemStatus.active);
    });

    test('returns a Failure (Left) when the client throws', () async {
      when(
        () => api.get(ApiPaths.inventoryBatches, query: any(named: 'query')),
      ).thenThrow(Exception('network down'));

      final res = await repo.list();

      expect(res.isLeft(), isTrue);
    });
  });

  group('add()', () {
    test(
      'sends a snake_case batch body with an Idempotency-Key and maps the response back',
      () async {
        when(
          () => api.post(
            ApiPaths.inventoryBatches,
            body: any(named: 'body'),
            headers: any(named: 'headers'),
          ),
        ).thenAnswer((invocation) async {
          final body =
              invocation.namedArguments[#body]! as Map<String, dynamic>;
          return {
            'id': 'new-1',
            'custom_name': body['custom_name'],
            'ingredient_name': body['custom_name'],
            'current_quantity': body['quantity'],
            'unit': body['unit'],
            'storage_mode': body['storage_mode'],
            'status': 'ACTIVE',
            'source': 'MANUAL',
            'created_at': '2026-08-30T00:00:00.000Z',
          };
        });

        final res = await repo.add(
          const PantryItemDraft(
            name: 'Trứng gà',
            category: 'Đạm',
            quantity: 10,
            unit: MeasurementUnit.fruit,
            storageTier: StorageTier.fridge,
          ),
        );

        final item = res.fold((f) => fail('expected Right, got $f'), (r) => r);
        expect(item.id, 'new-1');
        expect(item.name, 'Trứng gà');
        // The backend has no "quả" unit — collapses to OTHER on write, which
        // falls back to gram on read (documented limitation).
        expect(item.unit, MeasurementUnit.gram);

        final captured = verify(
          () => api.post(
            ApiPaths.inventoryBatches,
            body: captureAny(named: 'body'),
            headers: captureAny(named: 'headers'),
          ),
        ).captured;
        final body = captured[0] as Map<String, dynamic>;
        final headers = captured[1] as Map<String, String>;
        expect(body['storage_mode'], 'REFRIGERATED');
        expect(body['unit'], 'OTHER');
        expect(body['custom_name'], 'Trứng gà');
        expect(headers['Idempotency-Key'], isNotEmpty);
      },
    );
  });

  group('consume()', () {
    test('posts to /adjustments-consume and maps the updated batch', () async {
      when(
        () => api.post(
          ApiPaths.inventoryBatchConsume('batch-1'),
          body: any(named: 'body'),
          headers: any(named: 'headers'),
        ),
      ).thenAnswer(
        (_) async => {
          'id': 'batch-1',
          'custom_name': 'Cà chua bi',
          'ingredient_name': 'Cà chua bi',
          'current_quantity': 0.0,
          'unit': 'GRAM',
          'storage_mode': 'REFRIGERATED',
          'status': 'DEPLETED',
          'source': 'MANUAL',
          'created_at': '2026-08-30T00:00:00.000Z',
        },
      );

      final res = await repo.consume('batch-1', quantityUsed: 250);

      final item = res.fold((f) => fail('expected Right, got $f'), (r) => r);
      expect(item.status, PantryItemStatus.used);
      expect(item.quantity, 0.0);
    });
  });
}
