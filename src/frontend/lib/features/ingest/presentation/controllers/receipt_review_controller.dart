import 'package:riverpod_annotation/riverpod_annotation.dart';
import 'package:sweepfood/core/error/failure.dart';
import 'package:sweepfood/features/ingest/domain/entities/parsed_item_draft.dart';
import 'package:sweepfood/features/ingest/domain/entities/scan_job.dart';
import 'package:sweepfood/features/ingest/presentation/controllers/ingredient_recognition.dart';
import 'package:sweepfood/features/pantry/domain/entities/freshness_estimate.dart';
import 'package:sweepfood/features/pantry/domain/entities/pantry_item.dart';
import 'package:sweepfood/features/pantry/presentation/controllers/pantry_list_controller.dart';

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

  /// A ticked food the smart parser could not recognize: adding must be blocked
  /// until the user unticks or removes it.
  bool get hasSelectedUnsupported => selectedIndices.any(
    (i) => i >= 0 && i < items.length && !items[i].isSupported,
  );

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

/// Seeds from the receipt OCR [ScanJob]. Every supported line is ticked by
/// default; a food the smart parser cannot recognize starts (and is kept)
/// unticked, though the user may still tick it — which blocks adding.
@riverpod
class ReceiptReviewController extends _$ReceiptReviewController {
  @override
  ReceiptReviewState build(ScanJob job) {
    return ReceiptReviewState(
      storeName: job.storeName ?? 'Hóa đơn',
      purchaseDate: job.purchaseDate,
      items: job.items,
      selectedIndices: {
        for (var i = 0; i < job.items.length; i++)
          if (job.items[i].isSupported) i,
      },
    );
  }

  void toggleItem(int index) {
    final next = Set<int>.from(state.selectedIndices);
    next.contains(index) ? next.remove(index) : next.add(index);
    state = state.copyWith(selectedIndices: next);
  }

  void selectAll() => state = state.copyWith(
        selectedIndices: {
          for (var i = 0; i < state.items.length; i++)
            if (state.items[i].isSupported) i,
        },
      );

  void deselectAll() => state = state.copyWith(selectedIndices: {});

  void updateItem(int index, ParsedItemDraft updated) {
    final becameUnsupported = state.items[index].isSupported && !updated.isSupported;
    final newItems = List<ParsedItemDraft>.from(state.items);
    newItems[index] = updated;
    state = state.copyWith(
      items: newItems,
      // A renamed food the parser no longer recognizes is unticked automatically.
      selectedIndices: becameUnsupported
          ? (Set<int>.from(state.selectedIndices)..remove(index))
          : null,
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
    // Recognized after all: tick it again.
    state = state.copyWith(
      selectedIndices: {...state.selectedIndices, index},
    );
  }

  /// A manual date and a FreshCheck estimate are mutually exclusive.
  void setItemExpiry(
    int index,
    DateTime? expiry,
    FreshnessEstimate? freshness,
  ) => updateItem(
    index,
    state.items[index].copyWith(
      expiryDate: expiry,
      freshness: freshness,
      isExpiryWarn: false,
    ),
  );

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
    // Never add a partial list: every ticked food must be supported.
    if (state.hasSelectedUnsupported) throw const UnsupportedIngredientFailure();
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
