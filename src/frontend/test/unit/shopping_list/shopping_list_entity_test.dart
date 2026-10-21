import 'package:flutter_test/flutter_test.dart';
import 'package:sweepfood/features/shopping_list/domain/entities/shopping_list.dart';
import 'package:sweepfood/features/shopping_list/domain/entities/shopping_list_item.dart';
import 'package:sweepfood/shared/domain/measurement_unit.dart';

void main() {
  group('ShoppingList entity', () {
    const itemToBuy = ShoppingListItem(
      id: 'item-1',
      name: 'Thịt bò',
      quantity: 500,
      unit: MeasurementUnit.gram,
      category: 'Từ công thức',
      checked: false,
      alreadyInPantry: false,
      estPriceVnd: 150000,
    );

    const itemBought = ShoppingListItem(
      id: 'item-2',
      name: 'Cà rốt',
      quantity: 2,
      unit: MeasurementUnit.piece,
      category: 'Từ công thức',
      checked: true,
      alreadyInPantry: false,
      estPriceVnd: 10000,
    );

    const itemInPantry = ShoppingListItem(
      id: 'item-3',
      name: 'Hành tây',
      quantity: 0,
      unit: MeasurementUnit.piece,
      category: 'Từ công thức',
      checked: false,
      alreadyInPantry: true,
      estPriceVnd: 5000,
    );

    const list = ShoppingList(
      id: 'list-1',
      items: [itemToBuy, itemBought, itemInPantry],
    );

    test('grouped() filters out checked (bought) items regardless of showInStock', () {
      final hiddenStock = list.grouped(showInStock: false);
      expect(hiddenStock['Từ công thức'], hasLength(1));
      expect(hiddenStock['Từ công thức']!.first.id, 'item-1');

      final withStock = list.grouped(showInStock: true);
      expect(withStock['Từ công thức'], hasLength(2));
      final ids = withStock['Từ công thức']!.map((i) => i.id).toList();
      expect(ids, containsAll(['item-1', 'item-3']));
      expect(ids, isNot(contains('item-2')));
    });

    test('toBuy and toBuyCount only include unchecked and not-in-pantry items', () {
      expect(list.toBuyCount, 1);
      expect(list.toBuy.first.id, 'item-1');
    });

    test('estTotalVnd only sums remaining unbought items', () {
      expect(list.estTotalVnd, 150000);
    });

    test('checkedCount counts checked items', () {
      expect(list.checkedCount, 1);
    });
  });
}
