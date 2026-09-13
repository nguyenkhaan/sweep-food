import 'package:freezed_annotation/freezed_annotation.dart';
import 'package:sweepfood/features/shopping_list/domain/entities/shopping_list.dart';
import 'package:sweepfood/features/shopping_list/domain/entities/shopping_list_item.dart';
import 'package:sweepfood/shared/domain/measurement_unit.dart';

part 'shopping_list_dto.freezed.dart';
part 'shopping_list_dto.g.dart';

/// One `shopping-lists/{id}/items/{item_id}` row. See `docs/api-contract.md` §8.
///
/// The backend has no category taxonomy — [toEntity] buckets by [isGenerated]
/// instead (reusing the label already shown for D-01 "missing ingredient"
/// additions), and no per-line "already in pantry" flag — derived here as
/// `missingQuantity <= 0`.
@freezed
abstract class ShoppingListItemDto with _$ShoppingListItemDto {
  const ShoppingListItemDto._();

  const factory ShoppingListItemDto({
    required String id,
    @JsonKey(name: 'master_ingredient_id') String? masterIngredientId,
    @JsonKey(name: 'custom_name') String? customName,
    required String name,
    @JsonKey(name: 'required_quantity') @Default(0) double requiredQuantity,
    @JsonKey(name: 'available_quantity') @Default(0) double availableQuantity,
    @JsonKey(name: 'missing_quantity') @Default(0) double missingQuantity,
    required String unit,
    @JsonKey(name: 'estimated_cost') num? estimatedCost,
    @JsonKey(name: 'is_checked') @Default(false) bool isChecked,
    @JsonKey(name: 'is_generated') @Default(true) bool isGenerated,
    @JsonKey(name: 'source_recipe_ids')
    @Default(<String>[])
    List<String> sourceRecipeIds,
    @JsonKey(name: 'inventory_batch_id') String? inventoryBatchId,
  }) = _ShoppingListItemDto;

  factory ShoppingListItemDto.fromJson(Map<String, dynamic> json) =>
      _$ShoppingListItemDtoFromJson(json);

  ShoppingListItem toEntity() => ShoppingListItem(
        id: id,
        name: customName ?? name,
        quantity: missingQuantity,
        unit: MeasurementUnit.fromWire(unit),
        category: isGenerated ? 'Từ công thức' : 'Khác',
        checked: isChecked,
        alreadyInPantry: missingQuantity <= 0,
        fromDishIds: sourceRecipeIds,
        isGenerated: isGenerated,
        estPriceVnd: estimatedCost?.round(),
      );
}

/// `POST /shopping-lists/generate` / `GET /shopping-lists/{list_id}` response.
@freezed
abstract class ShoppingListDto with _$ShoppingListDto {
  const ShoppingListDto._();

  const factory ShoppingListDto({
    required String id,
    @JsonKey(name: 'meal_plan_id') String? mealPlanId,
    @Default('ACTIVE') String status,
    @JsonKey(name: 'generated_at') DateTime? generatedAt,
    @Default(<ShoppingListItemDto>[]) List<ShoppingListItemDto> items,
  }) = _ShoppingListDto;

  factory ShoppingListDto.fromJson(Map<String, dynamic> json) =>
      _$ShoppingListDtoFromJson(json);

  /// The backend has no descriptive label — the B-01 screen already renders
  /// nothing when this is null.
  ShoppingList toEntity() => ShoppingList(
        id: id,
        sourceLabel: null,
        items: [for (final i in items) i.toEntity()],
      );
}
