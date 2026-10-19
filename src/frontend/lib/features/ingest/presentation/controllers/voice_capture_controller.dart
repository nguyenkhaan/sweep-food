import 'package:riverpod_annotation/riverpod_annotation.dart';
import 'package:sweepfood/features/ingest/domain/entities/parsed_item_draft.dart';
import 'package:sweepfood/features/ingest/domain/entities/scan_job.dart';
import 'package:sweepfood/features/pantry/domain/entities/freshness_estimate.dart';
import 'package:sweepfood/features/pantry/domain/entities/pantry_item.dart';
import 'package:sweepfood/features/pantry/presentation/controllers/pantry_list_controller.dart';
import 'package:sweepfood/shared/domain/measurement_unit.dart';
import 'package:sweepfood/shared/domain/storage_tier.dart';

part 'voice_capture_controller.g.dart';

/// Editable transcript + item list for the Voice Review screen (I-07), seeded
/// from the ASR [ScanJob]. Live recording lives in `AudioRecorderService`.
class VoiceReviewState {
  const VoiceReviewState({required this.transcript, required this.items});

  final String transcript;
  final List<ParsedItemDraft> items;

  VoiceReviewState copyWith({
    String? transcript,
    List<ParsedItemDraft>? items,
  }) {
    return VoiceReviewState(
      transcript: transcript ?? this.transcript,
      items: items ?? this.items,
    );
  }
}

@riverpod
class VoiceCaptureController extends _$VoiceCaptureController {
  @override
  VoiceReviewState build(ScanJob job) => VoiceReviewState(
        transcript: job.rawText ?? '',
        items: job.items,
      );

  void updateItem(int index, ParsedItemDraft item) {
    final list = List<ParsedItemDraft>.from(state.items);
    list[index] = item;
    state = state.copyWith(items: list);
  }

  /// Renaming detaches the row from its catalog match and FreshCheck estimate.
  void renameItem(int index, String name) {
    final item = state.items[index];
    if (name == item.name) return;
    updateItem(
      index,
      item.copyWith(name: name, ingredientId: null, freshness: null),
    );
  }

  /// A manual date and a FreshCheck estimate are mutually exclusive.
  void setItemExpiry(
    int index,
    DateTime? expiry,
    FreshnessEstimate? freshness,
  ) => updateItem(
    index,
    state.items[index].copyWith(expiryDate: expiry, freshness: freshness),
  );

  void addItem(ParsedItemDraft item) =>
      state = state.copyWith(items: [...state.items, item]);

  void removeItem(int index) {
    final list = List<ParsedItemDraft>.from(state.items)..removeAt(index);
    state = state.copyWith(items: list);
  }

  Future<List<PantryItem>> saveAllToPantry() async {
    final pantryNotifier = ref.read(pantryListControllerProvider.notifier);
    final saved = <PantryItem>[];
    for (final item in state.items) {
      final draft = item.toPantryItemDraft(source: PantrySource.voice);
      saved.add(await pantryNotifier.add(draft));
    }
    return saved;
  }
}

/// A blank draft row for the "Thêm dòng" action on I-07.
const ParsedItemDraft kBlankVoiceDraft = ParsedItemDraft(
  name: 'Nguyên liệu mới',
  category: 'Khác',
  quantity: 1,
  unit: MeasurementUnit.piece,
  storageTier: StorageTier.fridge,
);
