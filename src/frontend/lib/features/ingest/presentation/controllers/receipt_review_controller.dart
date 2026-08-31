import 'package:frontend/features/ingest/domain/entities/parsed_item_draft.dart';
import 'package:frontend/features/ingest/domain/entities/scan_job.dart';
import 'package:frontend/features/pantry/domain/entities/pantry_item.dart';
import 'package:frontend/features/pantry/presentation/controllers/pantry_list_controller.dart';
import 'package:riverpod_annotation/riverpod_annotation.dart';

part 'receipt_review_controller.g.dart';

/// Selection + edit state for the Receipt Review screen (I-05).
class ReceiptReviewState {
  const ReceiptReviewState({
    required this.storeName,
    required this.purchaseDate,
    required this.items,
    required this.selectedIndices,
  });

  final String storeName;
  final DateTime? purchaseDate;
  final List<ParsedItemDraft> items;
  final Set<int> selectedIndices;

  int get selectedCount => selectedIndices.length;
  bool isSelected(int index) => selectedIndices.contains(index);

  ReceiptReviewState copyWith({
    String? storeName,
    DateTime? purchaseDate,
    List<ParsedItemDraft>? items,
    Set<int>? selectedIndices,
  }) {
    return ReceiptReviewState(
      storeName: storeName ?? this.storeName,
      purchaseDate: purchaseDate ?? this.purchaseDate,
      items: items ?? this.items,
      selectedIndices: selectedIndices ?? this.selectedIndices,
    );
  }
}

/// Seeds from the receipt OCR [ScanJob]; every line is selected by default.
@riverpod
class ReceiptReviewController extends _$ReceiptReviewController {
  @override
  ReceiptReviewState build(ScanJob job) {
    return ReceiptReviewState(
      storeName: job.storeName ?? 'Hóa đơn',
      purchaseDate: job.purchaseDate,
      items: job.items,
      selectedIndices: {for (var i = 0; i < job.items.length; i++) i},
    );
  }

  void toggleItem(int index) {
    final next = Set<int>.from(state.selectedIndices);
    next.contains(index) ? next.remove(index) : next.add(index);
    state = state.copyWith(selectedIndices: next);
  }

  void selectAll() => state = state.copyWith(
        selectedIndices: {for (var i = 0; i < state.items.length; i++) i},
      );

  void deselectAll() => state = state.copyWith(selectedIndices: {});

  void updateItem(int index, ParsedItemDraft updated) {
    final newItems = List<ParsedItemDraft>.from(state.items);
    newItems[index] = updated;
    state = state.copyWith(items: newItems);
  }

  void removeItem(int index) {
    final newItems = List<ParsedItemDraft>.from(state.items)..removeAt(index);
    final newSelected = <int>{};
    for (final s in state.selectedIndices) {
      if (s < index) {
        newSelected.add(s);
      } else if (s > index) {
        newSelected.add(s - 1);
      }
    }
    state = state.copyWith(items: newItems, selectedIndices: newSelected);
  }

  /// Confirms every selected line into the pantry.
  Future<List<PantryItem>> saveSelectedToPantry() async {
    final pantryNotifier = ref.read(pantryListControllerProvider.notifier);
    final saved = <PantryItem>[];
    for (final idx in state.selectedIndices.toList()..sort()) {
      if (idx >= 0 && idx < state.items.length) {
        final draft = state.items[idx]
            .toPantryItemDraft(source: PantrySource.receiptScan);
        saved.add(await pantryNotifier.add(draft));
      }
    }
    return saved;
  }
}
