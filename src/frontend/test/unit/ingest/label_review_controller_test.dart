import 'package:flutter_test/flutter_test.dart';
import 'package:frontend/core/utils/result.dart';
import 'package:frontend/features/ingest/presentation/controllers/label_review_controller.dart';
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
        source: PantrySource.manual,
      ),
    );
  });

  group('LabelReviewController', () {
    test('initializes with mock label data and imagePath', () {
      final container = createContainer();
      final draft = container.read(
        labelReviewControllerProvider(imagePath: 'path/to/img.jpg'),
      );

      expect(draft.name, 'Cà chua bi');
      expect(draft.quantity, 500);
      expect(draft.unit, MeasurementUnit.gram);
      expect(draft.storageTier, StorageTier.fridge);
      expect(draft.imagePath, 'path/to/img.jpg');
      expect(draft.isExpiryWarn, isTrue);
    });

    test('updates field values correctly', () {
      final container = createContainer();
      final notifier = container.read(
        labelReviewControllerProvider(imagePath: null).notifier,
      );

      notifier.setName('Dưa leo');
      notifier.setQuantity(300);
      notifier.setUnit(MeasurementUnit.gram);
      notifier.setPrice(15000);
      notifier.setCategory('Rau củ quả');
      notifier.setStorageTier(StorageTier.fridge);

      final newPacked = DateTime(2026, 9, 2);
      final newExpiry = DateTime(2026, 9, 8);
      notifier.setPackedDate(newPacked);
      notifier.setExpiryDate(newExpiry);

      final state = container.read(
        labelReviewControllerProvider(imagePath: null),
      );

      expect(state.name, 'Dưa leo');
      expect(state.quantity, 300);
      expect(state.unit, MeasurementUnit.gram);
      expect(state.priceVnd, 15000);
      expect(state.category, 'Rau củ quả');
      expect(state.storageTier, StorageTier.fridge);
      expect(state.packedDate, newPacked);
      expect(state.expiryDate, newExpiry);
      expect(state.isExpiryWarn, isFalse); // setExpiryDate clears the warning flag
    });

    test('saveToPantry delegates to pantry repository', () async {
      final repo = MockPantryRepository();
      when(() => repo.add(any())).thenAnswer(
        (_) async => Right(
          PantryItem(
            id: 'item-1',
            name: 'Cà chua bi',
            category: 'Rau củ',
            quantity: 500,
            unit: MeasurementUnit.gram,
            storageTier: StorageTier.fridge,
            source: PantrySource.labelScan,
            status: PantryItemStatus.active,
            addedAt: DateTime.now(),
          ),
        ),
      );

      final container = createContainer(
        overrides: [pantryRepositoryProvider.overrideWithValue(repo)],
      );

      final notifier = container.read(
        labelReviewControllerProvider(imagePath: null).notifier,
      );
      final savedItem = await notifier.saveToPantry();

      expect(savedItem.name, 'Cà chua bi');
      expect(savedItem.source, PantrySource.labelScan);
      verify(() => repo.add(any())).called(1);
    });
  });
}
