import 'package:flutter_test/flutter_test.dart';
import 'package:frontend/core/network/api_client.dart';
import 'package:frontend/core/network/api_paths.dart';
import 'package:frontend/features/shopping_list/data/datasources/shopping_list_remote_data_source.dart';
import 'package:frontend/features/shopping_list/data/repositories/shopping_list_repository_impl.dart';
import 'package:frontend/features/shopping_list/domain/entities/shopping_list_item.dart';
import 'package:frontend/shared/domain/measurement_unit.dart';
import 'package:mocktail/mocktail.dart';

class _MockApiClient extends Mock implements ApiClient {}

void main() {
  late _MockApiClient api;
  late ShoppingListRepositoryImpl repo;

  setUp(() {
    api = _MockApiClient();
    repo = ShoppingListRepositoryImpl(ShoppingListRemoteDataSource(api));
  });

  test('current() maps the payload and computes to-buy / totals', () async {
    when(() => api.get(ApiPaths.shoppingLists)).thenAnswer(
      (_) async => {
        'id': 'sl1',
        'source_label': 'Từ thực đơn tuần',
        'items': [
          {
            'id': 'a',
            'name': 'Xà lách',
            'quantity': 150.0,
            'unit': 'g',
            'category': 'Rau củ',
            'checked': false,
            'est_price_vnd': 12000,
          },
          {
            'id': 'b',
            'name': 'Trứng',
            'quantity': 6.0,
            'unit': 'qua',
            'category': 'Đạm',
            'already_in_pantry': true,
            'est_price_vnd': 18000,
          },
        ],
      },
    );

    final res = await repo.current();
    final list = res.fold((f) => fail('expected Right, got $f'), (r) => r);

    expect(list.id, 'sl1');
    expect(list.items, hasLength(2));
    expect(list.toBuyCount, 1); // the in-pantry item is excluded
    expect(list.items.first.unit, MeasurementUnit.gram);
    expect(list.estTotalVnd, 12000); // only unchecked, not-in-pantry
  });

  test('current() returns a Failure (Left) when the client throws', () async {
    when(() => api.get(ApiPaths.shoppingLists))
        .thenThrow(Exception('offline'));
    final res = await repo.current();
    expect(res.isLeft(), isTrue);
  });

  test('addItem() posts a snake_case body and maps the echo back', () async {
    when(() => api.post('/shopping-lists/sl1/items', body: any(named: 'body')))
        .thenAnswer((invocation) async {
      final body = invocation.namedArguments[#body]! as Map<String, dynamic>;
      return {...body, 'id': 'new-1'};
    });

    final res = await repo.addItem(
      listId: 'sl1',
      draft: const ShoppingListItemDraft(
        name: 'Chanh',
        quantity: 3,
        unit: MeasurementUnit.fruit,
        category: 'Rau củ',
      ),
    );

    final item = res.fold((f) => fail('expected Right, got $f'), (r) => r);
    expect(item.id, 'new-1');
    expect(item.name, 'Chanh');

    final body = verify(
      () => api.post('/shopping-lists/sl1/items', body: captureAny(named: 'body')),
    ).captured.single as Map<String, dynamic>;
    expect(body['unit'], 'qua');
    expect(body['category'], 'Rau củ');
  });
}
