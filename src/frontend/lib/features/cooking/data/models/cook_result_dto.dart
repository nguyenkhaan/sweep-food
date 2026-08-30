import 'package:freezed_annotation/freezed_annotation.dart';
import 'package:frontend/features/cooking/domain/entities/cook_result.dart';
import 'package:frontend/features/pantry/data/models/pantry_item_dto.dart';
import 'package:frontend/shared/domain/measurement_unit.dart';

part 'cook_result_dto.freezed.dart';
part 'cook_result_dto.g.dart';

@freezed
abstract class CookResultDto with _$CookResultDto {
  const CookResultDto._();

  const factory CookResultDto({
    @JsonKey(name: 'dish_id') @Default('') String dishId,
    @JsonKey(name: 'dish_name') @Default('') String dishName,
    @Default(<PantryChangeDto>[]) List<PantryChangeDto> changes,
    @JsonKey(name: 'updated_pantry_items')
    @Default(<PantryItemDto>[])
    List<PantryItemDto> updatedPantryItems,
    @JsonKey(name: 'depleted_item_ids')
    @Default(<String>[])
    List<String> depletedItemIds,
    @JsonKey(name: 'near_expiry_used_count') @Default(0) int nearExpiryUsedCount,
    @JsonKey(name: 'waste_avoided_grams') @Default(0) double wasteAvoidedGrams,
    @JsonKey(name: 'leftover_servings') @Default(0) int leftoverServings,
  }) = _CookResultDto;

  factory CookResultDto.fromJson(Map<String, dynamic> json) =>
      _$CookResultDtoFromJson(json);

  CookResult toEntity() => CookResult(
        dishId: dishId,
        dishName: dishName,
        changes: [for (final c in changes) c.toEntity()],
        updatedPantryItems: [for (final i in updatedPantryItems) i.toEntity()],
        depletedItemIds: depletedItemIds,
        nearExpiryUsedCount: nearExpiryUsedCount,
        wasteAvoidedGrams: wasteAvoidedGrams,
        leftoverServings: leftoverServings,
      );
}

@freezed
abstract class PantryChangeDto with _$PantryChangeDto {
  const PantryChangeDto._();

  const factory PantryChangeDto({
    required String name,
    @Default('g') String unit,
    @Default(0) double before,
    @Default(0) double after,
    @JsonKey(name: 'near_expiry_used') @Default(false) bool nearExpiryUsed,
    @JsonKey(name: 'pantry_item_id') String? pantryItemId,
  }) = _PantryChangeDto;

  factory PantryChangeDto.fromJson(Map<String, dynamic> json) =>
      _$PantryChangeDtoFromJson(json);

  PantryChange toEntity() => PantryChange(
        name: name,
        unit: MeasurementUnit.fromWire(unit),
        before: before,
        after: after,
        nearExpiryUsed: nearExpiryUsed,
        pantryItemId: pantryItemId,
      );
}
