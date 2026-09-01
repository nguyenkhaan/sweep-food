import 'package:riverpod_annotation/riverpod_annotation.dart';
import 'package:sweepfood/features/catalog/domain/entities/ingredient.dart';
import 'package:sweepfood/features/pantry/domain/entities/pantry_item.dart';
import 'package:sweepfood/features/pantry/domain/entities/pantry_item_draft.dart';
import 'package:sweepfood/features/pantry/presentation/controllers/pantry_item_controller.dart';
import 'package:sweepfood/features/pantry/presentation/controllers/pantry_list_controller.dart';
import 'package:sweepfood/shared/domain/measurement_unit.dart';
import 'package:sweepfood/shared/domain/storage_tier.dart';

part 'add_ingredient_controller.g.dart';

/// Form state for K-03 (add) and K-03 in edit mode (`editItemId != null`).
@riverpod
class AddIngredientController extends _$AddIngredientController {
  @override
  PantryItemDraft build(String? editItemId) {
    if (editItemId != null) {
      final item = ref.read(pantryItemByIdProvider(editItemId));
      if (item != null) return PantryItemDraft.fromItem(item);
    }
    return const PantryItemDraft();
  }

  bool get isEditing => editItemId != null;

  void setName(String v) => state = state.copyWith(name: v);
  void setCategory(String v) => state = state.copyWith(category: v);
  void setQuantity(double v) => state = state.copyWith(quantity: v);
  void setUnit(MeasurementUnit v) => state = state.copyWith(unit: v);
  void setTier(StorageTier v) => state = state.copyWith(storageTier: v);
  void setPackedDate(DateTime? v) => state = state.copyWith(packedDate: v);
  void setExpiryDate(DateTime? v) => state = state.copyWith(expiryDate: v);
  void setPrice(int? v) => state = state.copyWith(priceVnd: v);

  /// Fill name / category / unit from a picked catalog [ingredient].
  void applyIngredient(Ingredient ingredient) => state = state.copyWith(
        name: ingredient.name,
        category: ingredient.category,
        unit: ingredient.defaultUnit,
        ingredientId: ingredient.id,
        referenceShelfLifeDays: ingredient.referenceShelfLifeDays,
      );

  /// Persists via [PantryListController]. Throws a `Failure` on error.
  Future<PantryItem> submit() {
    final list = ref.read(pantryListControllerProvider.notifier);
    final id = editItemId;
    return id != null ? list.updateItem(id, state) : list.add(state);
  }
}
