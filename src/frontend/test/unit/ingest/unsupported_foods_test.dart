import 'package:flutter_test/flutter_test.dart';
import 'package:mocktail/mocktail.dart';
import 'package:sweepfood/core/error/failure.dart';
import 'package:sweepfood/core/network/api_paths.dart';
import 'package:sweepfood/core/network/network_providers.dart';
import 'package:sweepfood/core/utils/result.dart';
import 'package:sweepfood/features/ingest/domain/entities/parsed_item_draft.dart';
import 'package:sweepfood/features/ingest/domain/entities/scan_job.dart';
import 'package:sweepfood/features/ingest/domain/entities/scan_type.dart';
import 'package:sweepfood/features/ingest/presentation/controllers/label_review_controller.dart';
import 'package:sweepfood/features/ingest/presentation/controllers/receipt_review_controller.dart';
import 'package:sweepfood/features/ingest/presentation/controllers/voice_capture_controller.dart';
import 'package:sweepfood/features/pantry/data/repositories/pantry_repository_impl.dart';
import 'package:sweepfood/features/pantry/domain/entities/pantry_item.dart';
import 'package:sweepfood/features/pantry/domain/entities/pantry_item_draft.dart';
import 'package:sweepfood/shared/domain/measurement_unit.dart';
import 'package:sweepfood/shared/domain/storage_tier.dart';

import '../../helpers/ingest_fixtures.dart';
import '../../helpers/mocks.dart';
import '../../helpers/test_providers.dart';

const _unknown = ParsedItemDraft(name: 'Món lạ', quantity: 100);

/// A repository that accepts every add and counts them.
MockPantryRepository _acceptingRepo() {
  final repo = MockPantryRepository();
  when(() => repo.add(any())).thenAnswer((inv) async {
    final d = inv.positionalArguments.first as PantryItemDraft;
    return Right(
      PantryItem(
        id: 'id-${d.name}',
        name: d.name,
        category: d.category,
        quantity: d.quantity,
        unit: d.unit,
        storageTier: d.storageTier,
        source: d.source,
        status: PantryItemStatus.active,
        addedAt: DateTime.now(),
      ),
    );
  });
  return repo;
}

/// The text-extraction endpoint: recognizes only "thịt bò", like a real parser.
MockApiClient _parserApi() {
  final api = MockApiClient();
  when(
    () => api.post(ApiPaths.extractionText, body: any(named: 'body')),
  ).thenAnswer((inv) async {
    final text = (inv.namedArguments[#body] as Map)['text'] as String;
    final known = text.toLowerCase().contains('thịt bò');
    return {
      'request_id': 'r',
      'status': 'SUCCEEDED',
      'provider': 'SWEEP_FOOD_AI',
      'fields': {
        'ingredient_name': known ? 'Thịt bò' : text,
        'master_ingredient_id': known ? 'ing-thit-bo' : null,
        'category': known ? 'Thịt & Hải sản' : null,
      },
    };
  });
  return api;
}

void main() {
  setUpAll(() {
    registerFallbackValue(
      const PantryItemDraft(
        name: 'x',
        category: 'x',
        quantity: 1,
        unit: MeasurementUnit.piece,
        storageTier: StorageTier.fridge,
        source: PantrySource.manual,
      ),
    );
  });

  group('receipt', () {
    final job = ScanJob(
      id: 'r',
      type: ScanType.receipt,
      items: [...receiptScanJob().items, _unknown],
    );

    test('an unrecognized food starts unticked and select-all skips it', () {
      final container = createContainer();
      final notifier = container.read(
        receiptReviewControllerProvider(job).notifier,
      );
      var state = container.read(receiptReviewControllerProvider(job));

      expect(state.items, hasLength(7));
      expect(state.isSelected(6), isFalse);
      expect(state.selectedCount, 6);
      expect(state.hasSelectedUnsupported, isFalse);

      notifier
        ..deselectAll()
        ..selectAll();
      state = container.read(receiptReviewControllerProvider(job));
      expect(state.isSelected(6), isFalse);
      expect(state.selectedCount, 6);
    });

    test('a ticked unsupported food blocks the whole add; nothing is saved', () async {
      final repo = _acceptingRepo();
      final container = createContainer(
        overrides: [pantryRepositoryProvider.overrideWithValue(repo)],
      );
      final notifier = container.read(
        receiptReviewControllerProvider(job).notifier,
      )..toggleItem(6);
      expect(
        container.read(receiptReviewControllerProvider(job)).hasSelectedUnsupported,
        isTrue,
      );

      await expectLater(
        notifier.saveSelectedToPantry(),
        throwsA(isA<UnsupportedIngredientFailure>()),
      );
      verifyNever(() => repo.add(any()));

      // Unticking it unblocks the rest, and the unsupported food is never added.
      notifier.toggleItem(6);
      final saved = await notifier.saveSelectedToPantry();
      expect(saved, hasLength(6));
      expect(saved.map((e) => e.name), isNot(contains('Món lạ')));
    });

    test('renaming a food to something unrecognized unticks it', () {
      final container = createContainer();
      final notifier = container.read(
        receiptReviewControllerProvider(job).notifier,
      );
      expect(
        container.read(receiptReviewControllerProvider(job)).isSelected(0),
        isTrue,
      );

      final item = container.read(receiptReviewControllerProvider(job)).items[0];
      notifier.updateItem(
        0,
        item.copyWith(name: 'Tên khác', ingredientId: null, category: ''),
      );

      final state = container.read(receiptReviewControllerProvider(job));
      expect(state.items[0].isSupported, isFalse);
      expect(state.isSelected(0), isFalse);
    });

    test('re-recognizing a renamed food makes it supported and ticks it again', () async {
      final container = createContainer(
        overrides: [apiClientProvider.overrideWithValue(_parserApi())],
      );
      final notifier = container.read(
        receiptReviewControllerProvider(job).notifier,
      );

      notifier.updateItem(6, _unknown.copyWith(name: 'thịt bò xào'));
      await notifier.rematchItem(6);

      final state = container.read(receiptReviewControllerProvider(job));
      expect(state.items[6].isSupported, isTrue);
      expect(state.items[6].ingredientId, 'ing-thit-bo');
      expect(state.items[6].category, 'Thịt & Hải sản');
      expect(state.isSelected(6), isTrue);
    });

    test('a name the parser still does not know stays unsupported and unticked', () async {
      final container = createContainer(
        overrides: [apiClientProvider.overrideWithValue(_parserApi())],
      );
      final notifier = container.read(
        receiptReviewControllerProvider(job).notifier,
      );

      await notifier.rematchItem(6);

      final state = container.read(receiptReviewControllerProvider(job));
      expect(state.items[6].isSupported, isFalse);
      expect(state.isSelected(6), isFalse);
    });
  });

  group('voice', () {
    final job = ScanJob(
      id: 'v',
      type: ScanType.voice,
      items: [...voiceScanJob().items, _unknown],
    );

    test('one unsupported food blocks saving everything until it is removed', () async {
      final repo = _acceptingRepo();
      final container = createContainer(
        overrides: [pantryRepositoryProvider.overrideWithValue(repo)],
      );
      final notifier = container.read(voiceCaptureControllerProvider(job).notifier);
      expect(container.read(voiceCaptureControllerProvider(job)).hasUnsupported, isTrue);

      await expectLater(
        notifier.saveAllToPantry(),
        throwsA(isA<UnsupportedIngredientFailure>()),
      );
      verifyNever(() => repo.add(any()));

      notifier.removeItem(3);
      expect(container.read(voiceCaptureControllerProvider(job)).hasUnsupported, isFalse);
      expect(await notifier.saveAllToPantry(), hasLength(3));
      verify(() => repo.add(any())).called(3);
    });

    test('renaming to a food the parser knows clears the block', () async {
      final container = createContainer(
        overrides: [apiClientProvider.overrideWithValue(_parserApi())],
      );
      final notifier = container.read(voiceCaptureControllerProvider(job).notifier)
        ..renameItem(3, 'thịt bò hầm');
      expect(container.read(voiceCaptureControllerProvider(job)).hasUnsupported, isTrue);

      await notifier.rematchItem(3);

      final state = container.read(voiceCaptureControllerProvider(job));
      expect(state.hasUnsupported, isFalse);
      expect(state.items[3].category, 'Thịt & Hải sản');
    });
  });

  group('label', () {
    const job = ScanJob(
      id: 'l',
      type: ScanType.label,
      items: [_unknown],
    );

    test('an unsupported food cannot be saved', () async {
      final repo = _acceptingRepo();
      final container = createContainer(
        overrides: [pantryRepositoryProvider.overrideWithValue(repo)],
      );
      final notifier = container.read(labelReviewControllerProvider(job).notifier);

      expect(container.read(labelReviewControllerProvider(job)).isSupported, isFalse);
      expect(notifier.saveToPantry, throwsA(isA<UnsupportedIngredientFailure>()));
      verifyNever(() => repo.add(any()));
    });

    test('renaming to a recognized food makes it savable', () async {
      final repo = _acceptingRepo();
      final container = createContainer(
        overrides: [
          pantryRepositoryProvider.overrideWithValue(repo),
          apiClientProvider.overrideWithValue(_parserApi()),
        ],
      );
      final notifier = container.read(labelReviewControllerProvider(job).notifier)
        ..setName('thịt bò');
      await notifier.rematchName();

      final draft = container.read(labelReviewControllerProvider(job));
      expect(draft.isSupported, isTrue);
      expect(draft.category, 'Thịt & Hải sản');
      await notifier.saveToPantry();
      verify(() => repo.add(any())).called(1);
    });
  });
}
