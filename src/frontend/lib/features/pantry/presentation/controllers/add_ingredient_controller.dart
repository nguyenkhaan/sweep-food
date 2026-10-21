import 'package:flutter_riverpod/flutter_riverpod.dart' show Provider;
import 'package:riverpod_annotation/riverpod_annotation.dart';
import 'package:sweepfood/core/error/failure.dart';
import 'package:sweepfood/core/network/network_providers.dart';
import 'package:sweepfood/features/catalog/data/repositories/ingredient_repository_impl.dart';
import 'package:sweepfood/features/catalog/domain/entities/ingredient.dart';
import 'package:sweepfood/features/pantry/data/datasources/ingredient_match_remote_data_source.dart';
import 'package:sweepfood/features/pantry/domain/entities/freshness_estimate.dart';
import 'package:sweepfood/features/pantry/domain/entities/pantry_item.dart';
import 'package:sweepfood/features/pantry/domain/entities/pantry_item_draft.dart';
import 'package:sweepfood/features/pantry/presentation/controllers/pantry_item_controller.dart';
import 'package:sweepfood/features/pantry/presentation/controllers/pantry_list_controller.dart';
import 'package:sweepfood/shared/domain/measurement_unit.dart';
import 'package:sweepfood/shared/domain/storage_tier.dart';

part 'add_ingredient_controller.g.dart';

final ingredientMatchRemoteDataSourceProvider =
    Provider<IngredientMatchRemoteDataSource>(
      (ref) => IngredientMatchRemoteDataSource(ref.watch(apiClientProvider)),
    );

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

  /// Editing the name detaches the item from the catalog match (and from any
  /// FreshCheck estimate and food group derived from it) until the smart
  /// parser runs again. When editing a saved item the stored group is kept.
  void setName(String v) => state = v == state.name
      ? state
      : state.copyWith(
          name: v,
          ingredientId: null,
          freshness: null,
          category: isEditing ? state.category : '',
        );
  void setQuantity(double v) => state = state.copyWith(quantity: v);
  void setUnit(MeasurementUnit v) => state = state.copyWith(unit: v);
  /// FreshCheck depends on where the item is stored, so changing the tier
  /// discards an estimate computed for the previous one.
  void setTier(StorageTier v) => state = state.copyWith(
    storageTier: v,
    freshness: v == state.storageTier ? state.freshness : null,
  );
  void setPackedDate(DateTime? v) => state = state.copyWith(packedDate: v);
  /// A manual date and a FreshCheck estimate are mutually exclusive.
  void setExpiry(DateTime? expiry, FreshnessEstimate? freshness) =>
      state = state.copyWith(expiryDate: expiry, freshness: freshness);
  void setPrice(int? v) => state = state.copyWith(priceVnd: v);

  /// Fill name / category / unit from a picked catalog [ingredient].
  void applyIngredient(Ingredient ingredient) => state = state.copyWith(
        name: ingredient.name,
        category: ingredient.category,
        unit: ingredient.defaultUnit,
        ingredientId: ingredient.id,
        referenceShelfLifeDays: ingredient.referenceShelfLifeDays,
      );

  /// Runs the typed name through the smart parser. A catalog match links the
  /// item to its master ingredient (enabling FreshCheck) and fills the
  /// normalized name; a stated quantity only fills an empty quantity. Returns
  /// `true` when the draft changed.
  Future<bool> matchTypedName() async {
    final typed = state.name.trim();
    if (typed.isEmpty || state.ingredientId != null || isEditing) return false;
    final IngredientMatch? match;
    try {
      match = await ref.read(ingredientMatchRemoteDataSourceProvider).match(typed);
    } on Object {
      return false;
    }
    if (match == null ||
        match.masterIngredientId == null ||
        state.name.trim() != typed) {
      return false;
    }
    final fillQuantity = state.quantity <= 0 && match.quantity != null;
    state = state.copyWith(
      name: match.name,
      ingredientId: match.masterIngredientId,
      category: match.category ?? '',
      quantity: fillQuantity ? match.quantity! : state.quantity,
      unit: fillQuantity && match.unit != null ? match.unit! : state.unit,
    );
    return true;
  }

  /// Persists via [PantryListController]. Throws a `Failure` on error.
  Future<PantryItem> submit() async {
    if (state.ingredientId == null &&
        state.name.trim().isNotEmpty &&
        editItemId == null) {
      await matchTypedName();
      if (state.ingredientId == null) {
        try {
          final searchRes = await ref
              .read(ingredientRepositoryProvider)
              .search(state.name.trim());
          final items = searchRes.fold((_) => <Ingredient>[], (list) => list);
          if (items.isNotEmpty) {
            final exact = items.firstWhere(
              (i) =>
                  i.name.toLowerCase().trim() ==
                  state.name.toLowerCase().trim(),
              orElse: () => items.first,
            );
            state = state.copyWith(
              ingredientId: exact.id,
              category: exact.category,
            );
          }
        } catch (_) {}
      }
      // Still unrecognized after the parser and the catalog lookup: unsupported.
      if (state.ingredientId == null) throw const UnsupportedIngredientFailure();
    }
    final list = ref.read(pantryListControllerProvider.notifier);
    final id = editItemId;
    return id != null ? list.updateItem(id, state) : list.add(state);
  }
}
