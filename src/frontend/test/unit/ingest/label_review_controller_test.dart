import 'package:flutter_test/flutter_test.dart';
import 'package:mocktail/mocktail.dart';
import 'package:sweepfood/core/utils/result.dart';
import 'package:sweepfood/features/ingest/presentation/controllers/label_review_controller.dart';
import 'package:sweepfood/features/pantry/data/repositories/pantry_repository_impl.dart';
import 'package:sweepfood/features/pantry/domain/entities/freshness_estimate.dart';
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
        source: PantrySource.manual,
      ),
    );
  });

  final job = labelScanJob();

  group('LabelReviewController', () {
    test('seeds the draft from the scan job (incl. image path + warn flag)', () {
      final container = createContainer();
      final draft = container.read(labelReviewControllerProvider(job));

      expect(draft.name, 'Cà chua bi');
      expect(draft.quantity, 500);
      expect(draft.unit, MeasurementUnit.gram);
      expect(draft.storageTier, StorageTier.fridge);
      expect(draft.imagePath, 'path/to/label.jpg');
      expect(draft.isExpiryWarn, isTrue);
    });

    test('updates field values correctly', () {
      final container = createContainer();
      final notifier =
          container.read(labelReviewControllerProvider(job).notifier);

      notifier.setName('Dưa leo');
      notifier.setQuantity(300);
      notifier.setUnit(MeasurementUnit.gram);
      notifier.setPrice(15000);
      notifier.setCategory('Rau củ quả');
      notifier.setStorageTier(StorageTier.fridge);

      final newExpiry = DateTime(2026, 9, 8);
      notifier.setExpiry(newExpiry, null);

      final state = container.read(labelReviewControllerProvider(job));
      expect(state.name, 'Dưa leo');
      expect(state.quantity, 300);
      expect(state.priceVnd, 15000);
      expect(state.category, 'Rau củ quả');
      expect(state.expiryDate, newExpiry);
      expect(state.isExpiryWarn, isFalse); // setExpiry clears the flag
    });

    test('a FreshCheck estimate replaces the date and is dropped on rename or tier change', () {
      final container = createContainer();
      final notifier =
          container.read(labelReviewControllerProvider(job).notifier);
      final estimate = FreshnessEstimate(
        answers: const {'appearance': 'fresh'},
        expiresAt: DateTime(2026, 9, 3),
      );

      notifier.setExpiry(null, estimate);
      var state = container.read(labelReviewControllerProvider(job));
      expect(state.expiryDate, isNull);
      expect(state.freshness, estimate);

      notifier.setStorageTier(StorageTier.freezer);
      state = container.read(labelReviewControllerProvider(job));
      expect(state.freshness, isNull);

      notifier.setExpiry(null, estimate);
      notifier.setName('Cà rốt');
      state = container.read(labelReviewControllerProvider(job));
      expect(state.freshness, isNull);
      expect(state.ingredientId, isNull);
    });

    test('saveToPantry delegates to the pantry repository', () async {
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
      final saved = await container
          .read(labelReviewControllerProvider(job).notifier)
          .saveToPantry();

      expect(saved.source, PantrySource.labelScan);
      verify(() => repo.add(any())).called(1);
    });
  });
}
