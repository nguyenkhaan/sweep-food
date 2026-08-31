import 'package:flutter_test/flutter_test.dart';
import 'package:frontend/core/utils/result.dart';
import 'package:frontend/features/ingest/domain/entities/parsed_item_draft.dart';
import 'package:frontend/features/ingest/presentation/controllers/receipt_review_controller.dart';
import 'package:frontend/features/pantry/data/repositories/pantry_repository_impl.dart';
import 'package:frontend/features/pantry/domain/entities/pantry_item.dart';
import 'package:frontend/features/pantry/domain/entities/pantry_item_draft.dart';
import 'package:frontend/shared/domain/measurement_unit.dart';
import 'package:frontend/shared/domain/storage_tier.dart';
import 'package:mocktail/mocktail.dart';

import '../../helpers/mocks.dart';
import '../../helpers/test_providers.dart';

void main() {
  setUpAll(() {
    registerFallbackValue(
      const PantryItemDraft(
        name: 'test',
        category: 'test',
        quantity: 1,
        unit: MeasurementUnit.piece,
        storageTier: StorageTier.fridge,
        source: PantrySource.receiptScan,
      ),
    );
  });

  group('ReceiptReviewController', () {
    test('initializes with 6 items all selected by default', () {
      final container = createContainer();
      final state = container.read(
        receiptReviewControllerProvider(imagePath: null),
      );

      expect(state.storeName, 'Bách Hóa Xanh');
      expect(state.items, hasLength(6));
      expect(state.selectedCount, 6);
      expect(state.isSelected(0), isTrue);
      expect(state.isSelected(5), isTrue);
    });

    test('toggleItem, selectAll, deselectAll operate properly', () {
      final container = createContainer();
      final notifier = container.read(
        receiptReviewControllerProvider(imagePath: null).notifier,
      );

      // Deselect item at index 0
      notifier.toggleItem(0);
      var state = container.read(
        receiptReviewControllerProvider(imagePath: null),
      );
      expect(state.selectedCount, 5);
      expect(state.isSelected(0), isFalse);

      // Re-select item at index 0
      notifier.toggleItem(0);
      state = container.read(receiptReviewControllerProvider(imagePath: null));
      expect(state.selectedCount, 6);
      expect(state.isSelected(0), isTrue);

      // Deselect all
      notifier.deselectAll();
      state = container.read(receiptReviewControllerProvider(imagePath: null));
      expect(state.selectedCount, 0);

      // Select all
      notifier.selectAll();
      state = container.read(receiptReviewControllerProvider(imagePath: null));
      expect(state.selectedCount, 6);
    });

    test('updateItem and removeItem modify the items list correctly', () {
      final container = createContainer();
      final notifier = container.read(
        receiptReviewControllerProvider(imagePath: null).notifier,
      );

      // Update item 0
      const updated = ParsedItemDraft(
        name: 'Cà chua organic',
        category: 'Rau củ',
        quantity: 600,
        unit: MeasurementUnit.gram,
        storageTier: StorageTier.fridge,
      );
      notifier.updateItem(0, updated);

      var state = container.read(
        receiptReviewControllerProvider(imagePath: null),
      );
      expect(state.items[0].name, 'Cà chua organic');
      expect(state.items[0].quantity, 600);

      // Remove item 0
      notifier.removeItem(0);
      state = container.read(receiptReviewControllerProvider(imagePath: null));
      expect(state.items, hasLength(5));
      expect(state.items[0].name, 'Trứng gà');
    });

    test('saveSelectedToPantry adds all selected items to pantry repository', () async {
      final repo = MockPantryRepository();
      when(() => repo.add(any())).thenAnswer(
        (inv) async {
          final draft = inv.positionalArguments.first as PantryItemDraft;
          return Right(
            PantryItem(
              id: 'id-${draft.name}',
              name: draft.name,
              category: draft.category,
              quantity: draft.quantity,
              unit: draft.unit,
              storageTier: draft.storageTier,
              source: draft.source,
              status: PantryItemStatus.active,
              addedAt: DateTime.now(),
            ),
          );
        },
      );

      final container = createContainer(
        overrides: [pantryRepositoryProvider.overrideWithValue(repo)],
      );

      final notifier = container.read(
        receiptReviewControllerProvider(imagePath: null).notifier,
      );

      // Deselect everything except 2 items
      notifier.deselectAll();
      notifier.toggleItem(0); // Cà chua bi
      notifier.toggleItem(1); // Trứng gà

      final saved = await notifier.saveSelectedToPantry();

      expect(saved, hasLength(2));
      expect(saved[0].name, 'Cà chua bi');
      expect(saved[1].name, 'Trứng gà');
      verify(() => repo.add(any())).called(2);
    });
  });
}
