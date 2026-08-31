import 'package:frontend/features/ingest/domain/entities/parsed_item_draft.dart';
import 'package:frontend/features/pantry/domain/entities/pantry_item.dart';
import 'package:frontend/features/pantry/presentation/controllers/pantry_list_controller.dart';
import 'package:frontend/shared/domain/measurement_unit.dart';
import 'package:frontend/shared/domain/storage_tier.dart';
import 'package:riverpod_annotation/riverpod_annotation.dart';

part 'voice_capture_controller.g.dart';

class VoiceCaptureState {
  const VoiceCaptureState({
    this.isRecording = false,
    this.elapsedSeconds = 0,
    this.transcript = '2 lạng thịt bò, 1 bó cải bó xôi, 3 quả trứng',
    this.partialTranscript = '…1 bó cải bó xôi',
    this.items = const [],
  });

  final bool isRecording;
  final int elapsedSeconds;
  final String transcript;
  final String partialTranscript;
  final List<ParsedItemDraft> items;

  VoiceCaptureState copyWith({
    bool? isRecording,
    int? elapsedSeconds,
    String? transcript,
    String? partialTranscript,
    List<ParsedItemDraft>? items,
  }) {
    return VoiceCaptureState(
      isRecording: isRecording ?? this.isRecording,
      elapsedSeconds: elapsedSeconds ?? this.elapsedSeconds,
      transcript: transcript ?? this.transcript,
      partialTranscript: partialTranscript ?? this.partialTranscript,
      items: items ?? this.items,
    );
  }
}

@riverpod
class VoiceCaptureController extends _$VoiceCaptureController {
  @override
  VoiceCaptureState build() {
    return const VoiceCaptureState(
      items: [
        ParsedItemDraft(
          name: 'Thịt bò',
          category: 'Thịt & Hải sản',
          quantity: 200,
          unit: MeasurementUnit.gram,
          storageTier: StorageTier.fridge,
        ),
        ParsedItemDraft(
          name: 'Cải bó xôi',
          category: 'Rau củ',
          quantity: 1,
          unit: MeasurementUnit.bunch,
          storageTier: StorageTier.fridge,
        ),
        ParsedItemDraft(
          name: 'Trứng gà',
          category: 'Trứng & Sữa',
          quantity: 3,
          unit: MeasurementUnit.piece,
          storageTier: StorageTier.fridge,
        ),
      ],
    );
  }

  void startRecording() {
    state = state.copyWith(isRecording: true, elapsedSeconds: 0);
  }

  void stopRecording() {
    state = state.copyWith(isRecording: false);
  }

  void incrementTimer() {
    state = state.copyWith(elapsedSeconds: state.elapsedSeconds + 1);
  }

  void updateItem(int index, ParsedItemDraft item) {
    final list = List<ParsedItemDraft>.from(state.items);
    list[index] = item;
    state = state.copyWith(items: list);
  }

  void addItem(ParsedItemDraft item) {
    state = state.copyWith(items: [...state.items, item]);
  }

  void removeItem(int index) {
    final list = List<ParsedItemDraft>.from(state.items)..removeAt(index);
    state = state.copyWith(items: list);
  }

  Future<List<PantryItem>> saveAllToPantry() async {
    final pantryNotifier = ref.read(pantryListControllerProvider.notifier);
    final saved = <PantryItem>[];

    for (final item in state.items) {
      final draft = item.toPantryItemDraft(source: PantrySource.voice);
      final res = await pantryNotifier.add(draft);
      saved.add(res);
    }

    return saved;
  }
}
