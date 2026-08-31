import 'package:flutter_test/flutter_test.dart';
import 'package:frontend/core/utils/result.dart';
import 'package:frontend/features/ingest/presentation/controllers/voice_capture_controller.dart';
import 'package:frontend/features/pantry/data/repositories/pantry_repository_impl.dart';
import 'package:frontend/features/pantry/domain/entities/pantry_item.dart';
import 'package:frontend/features/pantry/domain/entities/pantry_item_draft.dart';
import 'package:frontend/shared/domain/measurement_unit.dart';
import 'package:frontend/shared/domain/storage_tier.dart';
import 'package:mocktail/mocktail.dart';

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
        source: PantrySource.voice,
      ),
    );
  });

  final job = voiceScanJob();

  group('VoiceCaptureController', () {
    test('seeds transcript + items from the scan job', () {
      final container = createContainer();
      final state = container.read(voiceCaptureControllerProvider(job));

      expect(state.transcript, contains('thịt bò'));
      expect(state.items, hasLength(3));
      expect(state.items[0].name, 'Thịt bò');
      expect(state.items[1].name, 'Cải bó xôi');
      expect(state.items[2].name, 'Trứng gà');
    });

    test('addItem, updateItem, removeItem update the item list', () {
      final container = createContainer();
      final notifier =
          container.read(voiceCaptureControllerProvider(job).notifier);

      notifier.addItem(kBlankVoiceDraft);
      var state = container.read(voiceCaptureControllerProvider(job));
      expect(state.items, hasLength(4));
      expect(state.items.last.name, 'Nguyên liệu mới');

      notifier.updateItem(0, state.items[0].copyWith(quantity: 350));
      state = container.read(voiceCaptureControllerProvider(job));
      expect(state.items[0].quantity, 350);

      notifier.removeItem(0);
      state = container.read(voiceCaptureControllerProvider(job));
      expect(state.items, hasLength(3));
      expect(state.items[0].name, 'Cải bó xôi');
    });

    test('saveAllToPantry saves every item with the voice source', () async {
      final repo = MockPantryRepository();
      when(() => repo.add(any())).thenAnswer((inv) async {
        final draft = inv.positionalArguments.first as PantryItemDraft;
        return Right(
          PantryItem(
            id: 'voice-${draft.name}',
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
      final saved = await container
          .read(voiceCaptureControllerProvider(job).notifier)
          .saveAllToPantry();

      expect(saved, hasLength(3));
      expect(saved[0].name, 'Thịt bò');
      expect(saved[0].source, PantrySource.voice);
      verify(() => repo.add(any())).called(3);
    });
  });
}
