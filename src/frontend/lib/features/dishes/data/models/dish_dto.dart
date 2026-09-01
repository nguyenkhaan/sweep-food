import 'package:freezed_annotation/freezed_annotation.dart';
import 'package:sweepfood/features/dishes/domain/entities/cooking_step.dart';
import 'package:sweepfood/features/dishes/domain/entities/dish.dart';
import 'package:sweepfood/features/dishes/domain/entities/dish_ingredient.dart';
import 'package:sweepfood/shared/domain/measurement_unit.dart';
import 'package:sweepfood/shared/domain/nutrition_info.dart';

part 'dish_dto.freezed.dart';
part 'dish_dto.g.dart';

@freezed
abstract class DishDto with _$DishDto {
  const DishDto._();

  const factory DishDto({
    required String id,
    required String name,
    @Default(1) int servings,
    @JsonKey(name: 'prep_time_min') @Default(0) int prepTimeMin,
    @JsonKey(name: 'cook_time_min') @Default(0) int cookTimeMin,
    @Default('') String cuisine,
    @Default('') String difficulty,
    @JsonKey(name: 'image_url') String? imageUrl,
    @JsonKey(name: 'nutrition_per_serving') MacrosDto? nutritionPerServing,
    @Default(<DishIngredientDto>[]) List<DishIngredientDto> ingredients,
    @Default(<CookingStepDto>[]) List<CookingStepDto> steps,
  }) = _DishDto;

  factory DishDto.fromJson(Map<String, dynamic> json) => _$DishDtoFromJson(json);

  Dish toEntity() => Dish(
        id: id,
        name: name,
        servings: servings <= 0 ? 1 : servings,
        prepTimeMin: prepTimeMin,
        cookTimeMin: cookTimeMin,
        cuisine: cuisine,
        difficulty: difficulty,
        imageUrl: imageUrl,
        nutritionPerServing:
            nutritionPerServing?.toEntity() ?? const NutritionInfo.zero(),
        ingredients: [for (final i in ingredients) i.toEntity()],
        steps: [for (final s in steps) s.toEntity()],
      );
}

@freezed
abstract class DishIngredientDto with _$DishIngredientDto {
  const DishIngredientDto._();

  const factory DishIngredientDto({
    required String name,
    @Default(0) double quantity,
    @Default('g') String unit,
    @JsonKey(name: 'is_seasoning') @Default(false) bool isSeasoning,
    @JsonKey(name: 'available_in_pantry') @Default(false) bool availableInPantry,
    @JsonKey(name: 'missing_qty') @Default(0) double missingQty,
    @JsonKey(name: 'near_expiry') @Default(false) bool nearExpiry,
    @JsonKey(name: 'pantry_item_id') String? pantryItemId,
  }) = _DishIngredientDto;

  factory DishIngredientDto.fromJson(Map<String, dynamic> json) =>
      _$DishIngredientDtoFromJson(json);

  DishIngredient toEntity() => DishIngredient(
        name: name,
        quantity: quantity,
        unit: MeasurementUnit.fromWire(unit),
        isSeasoning: isSeasoning,
        availableInPantry: availableInPantry,
        missingQty: missingQty,
        nearExpiry: nearExpiry,
        pantryItemId: pantryItemId,
      );
}

@freezed
abstract class CookingStepDto with _$CookingStepDto {
  const CookingStepDto._();

  const factory CookingStepDto({
    required int order,
    required String text,
    @JsonKey(name: 'duration_min') int? durationMin,
  }) = _CookingStepDto;

  factory CookingStepDto.fromJson(Map<String, dynamic> json) =>
      _$CookingStepDtoFromJson(json);

  CookingStep toEntity() =>
      CookingStep(order: order, text: text, durationMin: durationMin);
}

/// Shared macro shape for dish / serving nutrition (`energy_kcal`, `protein_g`,
/// `carb_g`, `lipid_g`) — mirrors the catalog's per-100g DTO.
@freezed
abstract class MacrosDto with _$MacrosDto {
  const MacrosDto._();

  const factory MacrosDto({
    @JsonKey(name: 'energy_kcal') @Default(0) double energyKcal,
    @JsonKey(name: 'protein_g') @Default(0) double proteinG,
    @JsonKey(name: 'carb_g') @Default(0) double carbG,
    @JsonKey(name: 'lipid_g') @Default(0) double lipidG,
  }) = _MacrosDto;

  factory MacrosDto.fromJson(Map<String, dynamic> json) =>
      _$MacrosDtoFromJson(json);

  NutritionInfo toEntity() => NutritionInfo(
        energyKcal: energyKcal,
        proteinG: proteinG,
        carbG: carbG,
        lipidG: lipidG,
      );
}
