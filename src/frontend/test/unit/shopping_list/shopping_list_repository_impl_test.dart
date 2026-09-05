import 'package:flutter_test/flutter_test.dart';
import 'package:mocktail/mocktail.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:sweepfood/core/network/api_client.dart';
import 'package:sweepfood/core/network/api_paths.dart';
import 'package:sweepfood/features/shopping_list/data/datasources/shopping_list_remote_data_source.dart';
import 'package:sweepfood/features/shopping_list/data/repositories/shopping_list_repository_impl.dart';
import 'package:sweepfood/features/shopping_list/domain/entities/shopping_list_item.dart';
import 'package:sweepfood/features/shopping_list/domain/entities/shopping_purchase_draft.dart';
import 'package:sweepfood/shared/domain/measurement_unit.dart';
import 'package:sweepfood/shared/domain/storage_tier.dart';

class _MockApiClient extends Mock implements ApiClient {}

Map<String, dynamic> _item({
  String id = 'a',
  String name = 'Xà lách',
  double requiredQuantity = 150,
  double availableQuantity = 0,
  double missingQuantity = 150,
  String unit = 'GRAM',
  bool isChecked = false,
  bool isGenerated = true,
  num? estimatedCost = 12000,
}) => {
  'id': id,
  'name': name,
  'required_quantity': requiredQuantity,
  'available_quantity': availableQuantity,
  'missing_quantity': missingQuantity,
  'unit': unit,
  'is_checked': isChecked,
  'is_generated': isGenerated,
  'estimated_cost': estimatedCost,
};

void main() {
  late _MockApiClient api;
  late SharedPreferences prefs;
  late ShoppingListRepositoryImpl repo;

  setUp(() async {
    api = _MockApiClient();
    SharedPreferences.setMockInitialValues({});
    prefs = await SharedPreferences.getInstance();
    repo = ShoppingListRepositoryImpl(ShoppingListRemoteDataSource(api), prefs);
  });

  group('current()', () {
    test('returns null when no list has been generated yet', () async {
      final res = await repo.current();
      final list = res.fold((f) => fail('expected Right, got $f'), (r) => r);
      expect(list, isNull);
    });

    test('reads the locally-remembered list id and maps the payload', () async {
      await prefs.setString('pref.active_shopping_list_id', 'sl1');
      when(() => api.get(ApiPaths.shoppingList('sl1'))).thenAnswer(
        (_) async => {
          'id': 'sl1',
          'meal_plan_id': 'plan-1',
          'status': 'ACTIVE',
          'items': [
            _item(id: 'a', name: 'Xà lách'),
            _item(
              id: 'b',
              name: 'Trứng',
              unit: 'PIECE',
              requiredQuantity: 6,
              availableQuantity: 6,
              missingQuantity: 0,
              estimatedCost: 18000,
            ),
          ],
        },
      );

      final res = await repo.current();
      final list = res.fold((f) => fail('expected Right, got $f'), (r) => r);

      expect(list!.id, 'sl1');
      expect(list.items, hasLength(2));
      expect(list.toBuyCount, 1); // fully-available item excluded
      expect(list.items.first.unit, MeasurementUnit.gram);
      expect(list.estTotalVnd, 12000); // only unchecked, not-in-pantry
    });
  });

  group('generate()', () {
    test('posts meal_plan_id and remembers the returned list id', () async {
      when(
        () => api.post(
          ApiPaths.shoppingListsGenerate,
          body: any(named: 'body'),
          headers: any(named: 'headers'),
        ),
      ).thenAnswer(
        (_) async => {'id': 'sl-new', 'status': 'ACTIVE', 'items': <dynamic>[]},
      );

      final res = await repo.generate(mealPlanId: 'plan-1');

      final list = res.fold((f) => fail('expected Right, got $f'), (r) => r);
      expect(list.id, 'sl-new');
      expect(prefs.getString('pref.active_shopping_list_id'), 'sl-new');
      final body = verify(
        () => api.post(
          ApiPaths.shoppingListsGenerate,
          body: captureAny(named: 'body'),
          headers: any(named: 'headers'),
        ),
      ).captured.single as Map<String, dynamic>;
      expect(body['meal_plan_id'], 'plan-1');
    });
  });

  group('addItem()', () {
    test('sends custom_name/quantity/unit (no category/from_dish_ids)', () async {
      when(
        () => api.post(
          ApiPaths.shoppingListItems('sl1'),
          body: any(named: 'body'),
          headers: any(named: 'headers'),
        ),
      ).thenAnswer((_) async => _item(id: 'new-1', name: 'Chanh', isGenerated: false));

      final res = await repo.addItem(
        listId: 'sl1',
        draft: const ShoppingListItemDraft(
          name: 'Chanh',
          quantity: 3,
          unit: MeasurementUnit.fruit,
        ),
      );

      final item = res.fold((f) => fail('expected Right, got $f'), (r) => r);
      expect(item.id, 'new-1');
      expect(item.isManual, isTrue);

      final body = verify(
        () => api.post(
          ApiPaths.shoppingListItems('sl1'),
          body: captureAny(named: 'body'),
          headers: any(named: 'headers'),
        ),
      ).captured.single as Map<String, dynamic>;
      expect(body['custom_name'], 'Chanh');
      // The backend has no "quả" unit — collapses to OTHER.
      expect(body['unit'], 'OTHER');
      expect(body.containsKey('category'), isFalse);
      expect(body.containsKey('from_dish_ids'), isFalse);
    });
  });

  group('setChecked()', () {
    test('includes purchase only when checking to true', () async {
      when(
        () => api.patch(
          ApiPaths.shoppingListItem('sl1', 'a'),
          body: any(named: 'body'),
          headers: any(named: 'headers'),
        ),
      ).thenAnswer((_) async => null);

      await repo.setChecked(
        listId: 'sl1',
        itemId: 'a',
        checked: true,
        purchase: const ShoppingPurchaseDraft(storageTier: StorageTier.fridge),
      );
      final checkedBody = verify(
        () => api.patch(
          ApiPaths.shoppingListItem('sl1', 'a'),
          body: captureAny(named: 'body'),
          headers: any(named: 'headers'),
        ),
      ).captured.single as Map<String, dynamic>;
      expect(checkedBody['checked'], isTrue);
      expect(checkedBody['purchase'], isNotNull);

      await repo.setChecked(listId: 'sl1', itemId: 'a', checked: false);
      final uncheckedBody = verify(
        () => api.patch(
          ApiPaths.shoppingListItem('sl1', 'a'),
          body: captureAny(named: 'body'),
          headers: any(named: 'headers'),
        ),
      ).captured.single as Map<String, dynamic>;
      expect(uncheckedBody['checked'], isFalse);
      expect(uncheckedBody.containsKey('purchase'), isFalse);
    });
  });
}
