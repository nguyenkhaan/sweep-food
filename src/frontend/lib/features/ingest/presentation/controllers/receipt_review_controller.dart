import 'package:frontend/features/ingest/domain/entities/parsed_item_draft.dart';
import 'package:frontend/features/pantry/domain/entities/pantry_item.dart';
import 'package:frontend/features/pantry/presentation/controllers/pantry_list_controller.dart';
import 'package:frontend/shared/domain/measurement_unit.dart';
import 'package:frontend/shared/domain/storage_tier.dart';
import 'package:riverpod_annotation/riverpod_annotation.dart';

part 'receipt_review_controller.g.dart';

class ReceiptReviewState {
  const ReceiptReviewState({
    required this.storeName,
    required this.purchaseDate,
    required this.items,
    required this.selectedIndices,
  });

  final String storeName;
  final DateTime purchaseDate;
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

@riverpod
class ReceiptReviewController extends _$ReceiptReviewController {
  @override
  ReceiptReviewState build({String? imagePath}) {
    // Default initial mock items matching design I-05
    final initialItems = [
      const ParsedItemDraft(
        name: 'Cà chua bi',
        category: 'Rau củ',
        quantity: 500,
        unit: MeasurementUnit.gram,
        storageTier: StorageTier.fridge,
        priceVnd: 18000,
        isExpiryWarn: false,
      ),
      const ParsedItemDraft(
        name: 'Trứng gà',
        category: 'Trứng & Sữa',
        quantity: 10,
        unit: MeasurementUnit.piece,
        storageTier: StorageTier.fridge,
        priceVnd: 32000,
        isExpiryWarn: false,
      ),
      const ParsedItemDraft(
        name: 'Thịt ba chỉ',
        category: 'Thịt & Hải sản',
        quantity: 300,
        unit: MeasurementUnit.gram,
        storageTier: StorageTier.fridge,
        priceVnd: 45000,
        isExpiryWarn: true,
      ),
      const ParsedItemDraft(
        name: 'Sữa tươi',
        category: 'Trứng & Sữa',
        quantity: 1,
        unit: MeasurementUnit.liter,
        storageTier: StorageTier.fridge,
        priceVnd: 36000,
        isExpiryWarn: false,
      ),
      const ParsedItemDraft(
        name: 'Hành lá',
        category: 'Rau củ',
        quantity: 1,
        unit: MeasurementUnit.bunch,
        storageTier: StorageTier.fridge,
        priceVnd: 5000,
        isExpiryWarn: true,
      ),
      const ParsedItemDraft(
        name: 'Dầu ăn',
        category: 'Gia vị',
        quantity: 1,
        unit: MeasurementUnit.bottle,
        storageTier: StorageTier.pantryShelf,
        priceVnd: 42000,
        isExpiryWarn: false,
      ),
    ];

    return ReceiptReviewState(
      storeName: 'Bách Hóa Xanh',
      purchaseDate: DateTime(2026, 9, 5),
      items: initialItems,
      selectedIndices: Set.from(List.generate(initialItems.length, (i) => i)),
    );
  }

  void toggleItem(int index) {
    final next = Set<int>.from(state.selectedIndices);
    if (next.contains(index)) {
      next.remove(index);
    } else {
      next.add(index);
    }
    state = state.copyWith(selectedIndices: next);
  }

  void selectAll() {
    state = state.copyWith(
      selectedIndices: Set.from(List.generate(state.items.length, (i) => i)),
    );
  }

  void deselectAll() {
    state = state.copyWith(selectedIndices: {});
  }

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

  /// Saves all selected items to pantry.
  Future<List<PantryItem>> saveSelectedToPantry() async {
    final pantryNotifier = ref.read(pantryListControllerProvider.notifier);
    final saved = <PantryItem>[];

    for (final idx in state.selectedIndices) {
      if (idx >= 0 && idx < state.items.length) {
        final itemDraft = state.items[idx].toPantryItemDraft(source: PantrySource.receiptScan);
        final item = await pantryNotifier.add(itemDraft);
        saved.add(item);
      }
    }

    return saved;
  }
}
