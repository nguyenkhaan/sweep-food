import 'package:flutter_test/flutter_test.dart';
import 'package:mocktail/mocktail.dart';
import 'package:sweepfood/core/network/api_client.dart';
import 'package:sweepfood/core/network/api_paths.dart';
import 'package:sweepfood/features/pantry/data/datasources/freshness_remote_data_source.dart';
import 'package:sweepfood/features/pantry/data/datasources/pantry_remote_data_source.dart';
import 'package:sweepfood/features/pantry/data/repositories/pantry_repository_impl.dart';
import 'package:sweepfood/features/pantry/domain/entities/freshness_estimate.dart';
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
    repo = PantryRepositoryImpl(
      PantryRemoteDataSource(api),
      FreshnessRemoteDataSource(api),
    );
  });

  group('list()', () {
    test(
      'maps the /inventory/batches payload to PantryItem entities',
      () async {
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
      },
    );

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
        // The backend has no "quả" unit — it collapses to OTHER on write and
        // is presented as the explicit frontend "phần" unit on read.
        expect(item.unit, MeasurementUnit.other);

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

  group('add() with a FreshCheck estimate', () {
    final estimate = FreshnessEstimate(
      answers: const {'appearance': 'fresh'},
      expiresAt: DateTime.utc(2026, 9, 3),
      remainingDaysMin: 3,
      remainingDaysMax: 3,
    );
    const draft = PantryItemDraft(
      name: 'Rau muống',
      quantity: 300,
      ingredientId: 'ing-1',
    );

    void stubBatchCreate() {
      when(
        () => api.post(
          ApiPaths.inventoryBatches,
          body: any(named: 'body'),
          headers: any(named: 'headers'),
        ),
      ).thenAnswer(
        (_) async => {
          'id': 'new-2',
          'master_ingredient_id': 'ing-1',
          'ingredient_name': 'Rau muống',
          'current_quantity': 300,
          'unit': 'GRAM',
          'storage_mode': 'REFRIGERATED',
          'status': 'ACTIVE',
          'source': 'MANUAL',
          'created_at': '2026-08-30T00:00:00.000Z',
        },
      );
    }

    test(
      'creates the batch without the estimated date, then records the estimate via assessment',
      () async {
        stubBatchCreate();
        when(
          () => api.post(
            ApiPaths.freshnessAssessment('new-2'),
            body: any(named: 'body'),
            headers: any(named: 'headers'),
          ),
        ).thenAnswer(
          (_) async => {
            'assessment_id': 'asm-1',
            'batch_id': 'new-2',
            'blocked': false,
            'expires_at': '2026-09-03T00:00:00Z',
          },
        );

        final res = await repo.add(draft.copyWith(freshness: estimate));

        final item = res.fold((f) => fail('expected Right, got $f'), (r) => r);
        expect(item.expiryDate?.toUtc(), DateTime.utc(2026, 9, 3));
        final created =
            verify(
                  () => api.post(
                    ApiPaths.inventoryBatches,
                    body: captureAny(named: 'body'),
                    headers: any(named: 'headers'),
                  ),
                ).captured.single
                as Map<String, dynamic>;
        expect(created['master_ingredient_id'], 'ing-1');
        expect(created.containsKey('expires_at'), isFalse);
        final assessed =
            verify(
                  () => api.post(
                    ApiPaths.freshnessAssessment('new-2'),
                    body: captureAny(named: 'body'),
                    headers: any(named: 'headers'),
                  ),
                ).captured.single
                as Map<String, dynamic>;
        expect(assessed['answers'], {'appearance': 'fresh'});
        expect(assessed['purchased_at'], isNotNull);
      },
    );

    test('keeps the saved item when the assessment fails', () async {
      stubBatchCreate();
      when(
        () => api.post(
          ApiPaths.freshnessAssessment('new-2'),
          body: any(named: 'body'),
          headers: any(named: 'headers'),
        ),
      ).thenThrow(Exception('assessment unavailable'));

      final res = await repo.add(draft.copyWith(freshness: estimate));

      final item = res.fold((f) => fail('expected Right, got $f'), (r) => r);
      expect(item.id, 'new-2');
      expect(item.expiryDate, isNull);
    });

    test('never assesses an item whose date was entered or read', () async {
      stubBatchCreate();

      await repo.add(
        draft.copyWith(
          expiryDate: DateTime.utc(2026, 9, 10),
          freshness: estimate,
        ),
      );

      verifyNever(
        () => api.post(
          ApiPaths.freshnessAssessment('new-2'),
          body: any(named: 'body'),
          headers: any(named: 'headers'),
        ),
      );
    });
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
