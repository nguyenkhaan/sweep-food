import 'package:riverpod_annotation/riverpod_annotation.dart';
import 'package:sweepfood/core/error/failure.dart';
import 'package:sweepfood/features/ingest/domain/entities/parsed_item_draft.dart';
import 'package:sweepfood/features/ingest/domain/entities/scan_job.dart';
import 'package:sweepfood/features/ingest/presentation/controllers/ingredient_recognition.dart';
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

  int get spokenClauseCount => transcript
      .split(
        RegExp(
          r'\s*(?:,|;|\bvà\b|\bvới\b|\brồi\b|\bkèm\b|\bthêm\b)\s*',
          caseSensitive: false,
        ),
      )
      .where((part) => part.trim().isNotEmpty)
      .length;

  int get suspectedMissingCount {
    final missing = spokenClauseCount - items.length;
    return missing > 0 ? missing : 0;
  }

  bool get hasSuspiciousQuantity {
    final mentionsLargeUnit = RegExp(
      r'\b(?:kg|kí|ký|kilo|kilô|cân)\b',
      caseSensitive: false,
    ).hasMatch(transcript);
    return !mentionsLargeUnit &&
        items.any(
          (item) => item.unit == MeasurementUnit.gram && item.quantity >= 1000,
        );
  }

  bool get needsReview => suspectedMissingCount > 0 || hasSuspiciousQuantity;

  /// A food the smart parser could not recognize: adding must be blocked until
  /// the user removes it (or renames it to something recognized).
  bool get hasUnsupported => items.any((item) => !item.isSupported);

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
  VoiceReviewState build(ScanJob job) =>
      VoiceReviewState(transcript: job.rawText ?? '', items: job.items);

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
      item.copyWith(
        name: name,
        ingredientId: null,
        freshness: null,
        category: '',
      ),
    );
  }

  /// After a rename the smart parser looks at the new text; a catalog match
  /// makes the food supported again and fills its food group.
  Future<void> rematchItem(int index) async {
    if (index < 0 || index >= state.items.length) return;
    final typed = state.items[index].name.trim();
    if (state.items[index].isSupported) return;
    final match = await recognizeIngredient(ref, typed);
    if (match == null ||
        index >= state.items.length ||
        state.items[index].name.trim() != typed) {
      return;
    }
    updateItem(
      index,
      state.items[index].copyWith(
        ingredientId: match.masterIngredientId,
        category: match.category ?? '',
      ),
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
    // Never add a partial list: every food must be supported.
    if (state.hasUnsupported) throw const UnsupportedIngredientFailure();
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
  category: '',
  quantity: 1,
  unit: MeasurementUnit.piece,
  storageTier: StorageTier.fridge,
);
