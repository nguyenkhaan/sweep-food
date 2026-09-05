import 'package:freezed_annotation/freezed_annotation.dart';
import 'package:sweepfood/features/pantry/domain/entities/pantry_item.dart';
import 'package:sweepfood/shared/domain/measurement_unit.dart';
import 'package:sweepfood/shared/domain/storage_tier.dart';

part 'cooked_leftover_dto.freezed.dart';
part 'cooked_leftover_dto.g.dart';

/// `POST /cooking/sessions/{id}/leftovers` response — a narrower, distinct
/// shape from the general inventory batch (`PantryItemDto`): no id/name
/// fields, just `batch_id` + the storage/quantity info. See
/// `docs/api-contract.md` §6.
@freezed
abstract class CookedLeftoverDto with _$CookedLeftoverDto {
  const CookedLeftoverDto._();

  const factory CookedLeftoverDto({
    @JsonKey(name: 'batch_id') required String batchId,
    @JsonKey(name: 'cooking_session_id') required String cookingSessionId,
    required double quantity,
    required String unit,
    @JsonKey(name: 'storage_mode') required String storageMode,
    @JsonKey(name: 'expires_at') DateTime? expiresAt,
    @JsonKey(name: 'created_at') required DateTime createdAt,
  }) = _CookedLeftoverDto;

  factory CookedLeftoverDto.fromJson(Map<String, dynamic> json) =>
      _$CookedLeftoverDtoFromJson(json);

  /// The backend has no name/category for a leftover batch — [dishName]
  /// (known client-side from the cooking session) fills the display name.
  PantryItem toEntity(String dishName) => PantryItem(
        id: batchId,
        name: dishName,
        category: '',
        quantity: quantity,
        unit: MeasurementUnit.fromWire(unit),
        storageTier: StorageTier.fromBackendWire(storageMode),
        addedAt: createdAt,
        source: PantrySource.cooked,
        status: PantryItemStatus.active,
        expiryDate: expiresAt,
      );
}
