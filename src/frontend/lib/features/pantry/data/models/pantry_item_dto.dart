import 'package:freezed_annotation/freezed_annotation.dart';
import 'package:sweepfood/features/pantry/domain/entities/pantry_item.dart';
import 'package:sweepfood/shared/domain/measurement_unit.dart';
import 'package:sweepfood/shared/domain/storage_tier.dart';

part 'pantry_item_dto.freezed.dart';
part 'pantry_item_dto.g.dart';

/// Maps the backend's `InventoryBatchStatus` (`ACTIVE|DEPLETED|DISCARDED|
/// ARCHIVED`) onto the frontend's simpler `active|used` bucket — the FE has
/// no dedicated UI for discarded/archived vs. depleted.
String _statusFromBackend(String? beStatus) =>
    beStatus == 'ACTIVE' ? 'active' : 'used';

/// One `/inventory/batches` row, mapped onto the frontend's [PantryItem]
/// shape. See `docs/api-contract.md` §10.
///
/// Known lossy mappings (backend has no equivalent — see IMPLEMENTATION_PLAN):
/// - `category` is always blank (batches carry no category, only an ingredient
///   name).
/// - `source` collapses to manual/cooked (backend only tracks MANUAL/LEFTOVER,
///   losing label/receipt/voice provenance).
/// - `referenceShelfLifeDays` is always null (not a per-batch backend concept).
/// - `priceVnd` is read from `unit_cost` (the backend has no separate
///   "total price paid" field).
@freezed
abstract class PantryItemDto with _$PantryItemDto {
  const PantryItemDto._();

  const factory PantryItemDto({
    required String id,
    @JsonKey(name: 'master_ingredient_id') String? masterIngredientId,
    @JsonKey(name: 'custom_name') String? customName,
    @JsonKey(name: 'ingredient_name') required String ingredientName,
    @JsonKey(name: 'current_quantity') required double currentQuantity,
    required String unit,
    @JsonKey(name: 'storage_mode') required String storageMode,
    @Default('ACTIVE') String status,
    @JsonKey(name: 'source') @Default('MANUAL') String source,
    @JsonKey(name: 'purchased_at') DateTime? purchasedAt,
    @JsonKey(name: 'packaged_at') DateTime? packagedAt,
    @JsonKey(name: 'expires_at') DateTime? expiresAt,
    @JsonKey(name: 'unit_cost') num? unitCost,
    @JsonKey(name: 'created_at') required DateTime createdAt,
  }) = _PantryItemDto;

  factory PantryItemDto.fromJson(Map<String, dynamic> json) =>
      _$PantryItemDtoFromJson(json);

  PantryItem toEntity() => PantryItem(
        id: id,
        name: customName ?? ingredientName,
        category: '',
        quantity: currentQuantity,
        unit: MeasurementUnit.fromWire(unit),
        storageTier: StorageTier.fromBackendWire(storageMode),
        addedAt: createdAt,
        source: source == 'LEFTOVER' ? PantrySource.cooked : PantrySource.manual,
        status: PantryItemStatus.fromWire(_statusFromBackend(status)),
        ingredientId: masterIngredientId,
        packedDate: packagedAt,
        expiryDate: expiresAt,
        referenceShelfLifeDays: null,
        priceVnd: unitCost?.round(),
      );
}
