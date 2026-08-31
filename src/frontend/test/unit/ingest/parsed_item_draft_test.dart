import 'package:flutter_test/flutter_test.dart';
import 'package:frontend/features/ingest/domain/entities/parsed_item_draft.dart';
import 'package:frontend/features/pantry/domain/entities/pantry_item.dart';
import 'package:frontend/shared/domain/measurement_unit.dart';
import 'package:frontend/shared/domain/storage_tier.dart';

void main() {
  group('ParsedItemDraft', () {
    test('creates with default values', () {
      const draft = ParsedItemDraft();
      expect(draft.name, 'Cà chua bi');
      expect(draft.category, 'Rau củ');
      expect(draft.quantity, 500);
      expect(draft.unit, MeasurementUnit.gram);
      expect(draft.storageTier, StorageTier.fridge);
      expect(draft.isExpiryWarn, isFalse);
    });

    test('toPantryItemDraft converts correctly with given source', () {
      final packed = DateTime(2026, 9, 1);
      final expiry = DateTime(2026, 9, 10);
      final draft = ParsedItemDraft(
        name: 'Thịt bò phi lê',
        category: 'Thịt & Hải sản',
        quantity: 300,
        unit: MeasurementUnit.gram,
        storageTier: StorageTier.freezer,
        packedDate: packed,
        expiryDate: expiry,
        priceVnd: 75000,
        isExpiryWarn: true,
      );

      final pantryDraft = draft.toPantryItemDraft(source: PantrySource.labelScan);

      expect(pantryDraft.name, 'Thịt bò phi lê');
      expect(pantryDraft.category, 'Thịt & Hải sản');
      expect(pantryDraft.quantity, 300);
      expect(pantryDraft.unit, MeasurementUnit.gram);
      expect(pantryDraft.storageTier, StorageTier.freezer);
      expect(pantryDraft.source, PantrySource.labelScan);
      expect(pantryDraft.packedDate, packed);
      expect(pantryDraft.expiryDate, expiry);
      expect(pantryDraft.priceVnd, 75000);
    });

    test('copyWith modifies attributes properly', () {
      const draft = ParsedItemDraft(name: 'Sữa tươi', quantity: 1);
      final updated = draft.copyWith(
        quantity: 2,
        unit: MeasurementUnit.liter,
        isExpiryWarn: true,
      );

      expect(updated.name, 'Sữa tươi');
      expect(updated.quantity, 2);
      expect(updated.unit, MeasurementUnit.liter);
      expect(updated.isExpiryWarn, isTrue);
    });
  });
}
