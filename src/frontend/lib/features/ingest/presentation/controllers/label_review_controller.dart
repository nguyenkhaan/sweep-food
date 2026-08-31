import 'package:frontend/features/ingest/domain/entities/parsed_item_draft.dart';
import 'package:frontend/features/pantry/domain/entities/pantry_item.dart';
import 'package:frontend/features/pantry/presentation/controllers/pantry_list_controller.dart';
import 'package:frontend/shared/domain/measurement_unit.dart';
import 'package:frontend/shared/domain/storage_tier.dart';
import 'package:riverpod_annotation/riverpod_annotation.dart';

part 'label_review_controller.g.dart';

/// Controller managing the state of the Label Review screen (I-03).
@riverpod
class LabelReviewController extends _$LabelReviewController {
  @override
  ParsedItemDraft build({String? imagePath}) {
    // Default initial mock data matching design I-03
    return ParsedItemDraft(
      name: 'Cà chua bi',
      category: 'Rau củ',
      quantity: 500,
      unit: MeasurementUnit.gram,
      storageTier: StorageTier.fridge,
      packedDate: DateTime(2026, 9, 5),
      expiryDate: DateTime(2026, 9, 12),
      priceVnd: 18000,
      isExpiryWarn: true,
      imagePath: imagePath,
    );
  }

  void setName(String name) {
    state = state.copyWith(name: name);
  }

  void setQuantity(double quantity) {
    state = state.copyWith(quantity: quantity);
  }

  void setUnit(MeasurementUnit unit) {
    state = state.copyWith(unit: unit);
  }

  void setPrice(int? price) {
    state = state.copyWith(priceVnd: price);
  }

  void setPackedDate(DateTime? date) {
    state = state.copyWith(packedDate: date);
  }

  void setExpiryDate(DateTime? date) {
    state = state.copyWith(expiryDate: date, isExpiryWarn: false);
  }

  void setStorageTier(StorageTier tier) {
    state = state.copyWith(storageTier: tier);
  }

  void setCategory(String category) {
    state = state.copyWith(category: category);
  }

  /// Saves the parsed item draft to the real/mock Pantry.
  Future<PantryItem> saveToPantry() async {
    final draft = state.toPantryItemDraft(source: PantrySource.labelScan);
    return ref.read(pantryListControllerProvider.notifier).add(draft);
  }
}
