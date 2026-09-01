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
    test('maps the API payload to PantryItem entities', () async {
      when(
        () => api.get(ApiPaths.pantryItems, query: any(named: 'query')),
      ).thenAnswer(
        (_) async => {
          'items': [
            {
              'id': 'p1',
              'name': 'Cà chua bi',
              'category': 'Rau củ',
              'quantity': 250.0,
              'unit': 'g',
              'storage_tier': 'fridge',
              'added_at': '2026-08-30T00:00:00.000',
              'source': 'manual',
              'status': 'active',
              'expiry_date': '2026-09-02T00:00:00.000',
            },
          ],
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
        () => api.get(ApiPaths.pantryItems, query: any(named: 'query')),
      ).thenThrow(Exception('network down'));

      final res = await repo.list();

      expect(res.isLeft(), isTrue);
    });
  });

  group('add()', () {
    test('sends a snake_case body and maps the echoed item back', () async {
      when(
        () => api.post(ApiPaths.pantryItems, body: any(named: 'body')),
      ).thenAnswer((invocation) async {
        final body = invocation.namedArguments[#body]! as Map<String, dynamic>;
        return {...body, 'id': 'new-1', 'added_at': '2026-08-30T00:00:00.000'};
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
      expect(item.unit, MeasurementUnit.fruit);

      final body =
          verify(
                () => api.post(
                  ApiPaths.pantryItems,
                  body: captureAny(named: 'body'),
                ),
              ).captured.single
              as Map<String, dynamic>;
      expect(body['storage_tier'], 'fridge');
      expect(body['unit'], 'qua');
    });
  });
}
