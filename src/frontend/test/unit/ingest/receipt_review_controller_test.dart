import 'package:flutter_test/flutter_test.dart';
import 'package:mocktail/mocktail.dart';
import 'package:sweepfood/core/utils/result.dart';
import 'package:sweepfood/features/ingest/domain/entities/parsed_item_draft.dart';
import 'package:sweepfood/features/ingest/presentation/controllers/receipt_review_controller.dart';
import 'package:sweepfood/features/pantry/data/repositories/pantry_repository_impl.dart';
import 'package:sweepfood/features/pantry/domain/entities/pantry_item.dart';
import 'package:sweepfood/features/pantry/domain/entities/pantry_item_draft.dart';
import 'package:sweepfood/shared/domain/measurement_unit.dart';
import 'package:sweepfood/shared/domain/storage_tier.dart';

import '../../helpers/ingest_fixtures.dart';
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

  final job = receiptScanJob();

  group('ReceiptReviewController', () {
    test('seeds store + every line selected by default', () {
      final container = createContainer();
      final state = container.read(receiptReviewControllerProvider(job));

      expect(state.storeName, 'Bách Hóa Xanh');
      expect(state.items, hasLength(6));
      expect(state.selectedCount, 6);
      expect(state.isSelected(0), isTrue);
      expect(state.isSelected(5), isTrue);
    });

    test('toggleItem, selectAll, deselectAll operate properly', () {
      final container = createContainer();
      final notifier =
          container.read(receiptReviewControllerProvider(job).notifier);

      notifier.toggleItem(0);
      expect(
        container.read(receiptReviewControllerProvider(job)).selectedCount,
        5,
      );

      notifier.toggleItem(0);
      expect(
        container.read(receiptReviewControllerProvider(job)).isSelected(0),
        isTrue,
      );

      notifier.deselectAll();
      expect(
        container.read(receiptReviewControllerProvider(job)).selectedCount,
        0,
      );

      notifier.selectAll();
      expect(
        container.read(receiptReviewControllerProvider(job)).selectedCount,
        6,
      );
    });

    test('updateItem and removeItem modify the list + keep selection aligned',
        () {
      final container = createContainer();
      final notifier =
          container.read(receiptReviewControllerProvider(job).notifier);

      notifier.updateItem(
        0,
        const ParsedItemDraft(
          name: 'Cà chua organic',
          category: 'Rau củ',
          quantity: 600,
        ),
      );
      var state = container.read(receiptReviewControllerProvider(job));
      expect(state.items[0].name, 'Cà chua organic');
      expect(state.items[0].quantity, 600);

      notifier.removeItem(0);
      state = container.read(receiptReviewControllerProvider(job));
      expect(state.items, hasLength(5));
      expect(state.items[0].name, 'Trứng gà');
    });

    test('saveSelectedToPantry adds only the selected lines', () async {
      final repo = MockPantryRepository();
      when(() => repo.add(any())).thenAnswer((inv) async {
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
      });

      final container = createContainer(
        overrides: [pantryRepositoryProvider.overrideWithValue(repo)],
      );
      final notifier =
          container.read(receiptReviewControllerProvider(job).notifier)
            ..deselectAll()
            ..toggleItem(0)
            ..toggleItem(1);

      final saved = await notifier.saveSelectedToPantry();

      expect(saved, hasLength(2));
      expect(saved[0].name, 'Cà chua bi');
      expect(saved[1].name, 'Trứng gà');
      verify(() => repo.add(any())).called(2);
    });
  });
}
