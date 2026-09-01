import 'package:freezed_annotation/freezed_annotation.dart';
import 'package:sweepfood/features/pantry/domain/entities/pantry_item.dart';
import 'package:sweepfood/shared/domain/measurement_unit.dart';
import 'package:sweepfood/shared/domain/storage_tier.dart';

part 'pantry_item_draft.freezed.dart';

/// The write payload for adding / editing a pantry item (K-03 form,
/// ingest confirm). No id / computed fields.
@freezed
abstract class PantryItemDraft with _$PantryItemDraft {
  const PantryItemDraft._();

  const factory PantryItemDraft({
    @Default('') String name,
    @Default('') String category,
    @Default(0) double quantity,
    @Default(MeasurementUnit.gram) MeasurementUnit unit,
    @Default(StorageTier.fridge) StorageTier storageTier,
    @Default(PantrySource.manual) PantrySource source,
    String? ingredientId,
    DateTime? packedDate,
    DateTime? expiryDate,
    int? referenceShelfLifeDays,
    int? priceVnd,
  }) = _PantryItemDraft;

  factory PantryItemDraft.fromItem(PantryItem i) => PantryItemDraft(
        name: i.name,
        category: i.category,
        quantity: i.quantity,
        unit: i.unit,
        storageTier: i.storageTier,
        source: i.source,
        ingredientId: i.ingredientId,
        packedDate: i.packedDate,
        expiryDate: i.expiryDate,
        referenceShelfLifeDays: i.referenceShelfLifeDays,
        priceVnd: i.priceVnd,
      );

  bool get isValid => name.trim().isNotEmpty && quantity > 0;
}
