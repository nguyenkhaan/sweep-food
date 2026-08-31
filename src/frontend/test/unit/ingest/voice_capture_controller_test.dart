import 'package:flutter_test/flutter_test.dart';
import 'package:frontend/core/utils/result.dart';
import 'package:frontend/features/ingest/domain/entities/parsed_item_draft.dart';
import 'package:frontend/features/ingest/presentation/controllers/voice_capture_controller.dart';
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
        source: PantrySource.voice,
      ),
    );
  });

  group('VoiceCaptureController', () {
    test('initializes with default voice items and recording false', () {
      final container = createContainer();
      final state = container.read(voiceCaptureControllerProvider);

      expect(state.isRecording, isFalse);
      expect(state.items, hasLength(3));
      expect(state.items[0].name, 'Thịt bò');
      expect(state.items[1].name, 'Cải bó xôi');
      expect(state.items[2].name, 'Trứng gà');
    });

    test('startRecording, incrementTimer and stopRecording modify state', () {
      final container = createContainer();
      final notifier = container.read(voiceCaptureControllerProvider.notifier);

      notifier.startRecording();
      var state = container.read(voiceCaptureControllerProvider);
      expect(state.isRecording, isTrue);
      expect(state.elapsedSeconds, 0);

      notifier.incrementTimer();
      notifier.incrementTimer();
      state = container.read(voiceCaptureControllerProvider);
      expect(state.elapsedSeconds, 2);

      notifier.stopRecording();
      state = container.read(voiceCaptureControllerProvider);
      expect(state.isRecording, isFalse);
    });

    test('addItem, updateItem, removeItem update items list', () {
      final container = createContainer();
      final notifier = container.read(voiceCaptureControllerProvider.notifier);

      // Add item
      const newItem = ParsedItemDraft(
        name: 'Hành tây',
        quantity: 2,
        unit: MeasurementUnit.piece,
        storageTier: StorageTier.pantryShelf,
      );
      notifier.addItem(newItem);
      var state = container.read(voiceCaptureControllerProvider);
      expect(state.items, hasLength(4));
      expect(state.items.last.name, 'Hành tây');

      // Update item
      final updated = state.items[0].copyWith(quantity: 350);
      notifier.updateItem(0, updated);
      state = container.read(voiceCaptureControllerProvider);
      expect(state.items[0].quantity, 350);

      // Remove item
      notifier.removeItem(0);
      state = container.read(voiceCaptureControllerProvider);
      expect(state.items, hasLength(3));
      expect(state.items[0].name, 'Cải bó xôi');
    });

    test('saveAllToPantry saves all items to pantry repository', () async {
      final repo = MockPantryRepository();
      when(() => repo.add(any())).thenAnswer(
        (inv) async {
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
        },
      );

      final container = createContainer(
        overrides: [pantryRepositoryProvider.overrideWithValue(repo)],
      );

      final notifier = container.read(voiceCaptureControllerProvider.notifier);
      final saved = await notifier.saveAllToPantry();

      expect(saved, hasLength(3));
      expect(saved[0].name, 'Thịt bò');
      expect(saved[0].source, PantrySource.voice);
      verify(() => repo.add(any())).called(3);
    });
  });
}
