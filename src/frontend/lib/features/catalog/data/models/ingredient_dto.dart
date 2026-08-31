import 'package:freezed_annotation/freezed_annotation.dart';
import 'package:sweepfood/features/catalog/domain/entities/ingredient.dart';
import 'package:sweepfood/shared/domain/measurement_unit.dart';
import 'package:sweepfood/shared/domain/nutrition_info.dart';

part 'ingredient_dto.freezed.dart';
part 'ingredient_dto.g.dart';

@freezed
abstract class IngredientDto with _$IngredientDto {
  const IngredientDto._();

  const factory IngredientDto({
    required String id,
    required String name,
    required String category,
    @JsonKey(name: 'default_unit') @Default('g') String defaultUnit,
    @JsonKey(name: 'nutrition_per_100g') NutritionPer100gDto? nutritionPer100g,
    @JsonKey(name: 'reference_shelf_life_days') int? referenceShelfLifeDays,
  }) = _IngredientDto;

  factory IngredientDto.fromJson(Map<String, dynamic> json) =>
      _$IngredientDtoFromJson(json);

  Ingredient toEntity() => Ingredient(
        id: id,
        name: name,
        category: category,
        defaultUnit: MeasurementUnit.fromWire(defaultUnit),
        nutritionPer100g: nutritionPer100g?.toEntity(),
        referenceShelfLifeDays: referenceShelfLifeDays,
      );
}

@freezed
abstract class NutritionPer100gDto with _$NutritionPer100gDto {
  const NutritionPer100gDto._();

  const factory NutritionPer100gDto({
    @JsonKey(name: 'energy_kcal') @Default(0) double energyKcal,
    @JsonKey(name: 'protein_g') @Default(0) double proteinG,
    @JsonKey(name: 'carb_g') @Default(0) double carbG,
    @JsonKey(name: 'lipid_g') @Default(0) double lipidG,
  }) = _NutritionPer100gDto;

  factory NutritionPer100gDto.fromJson(Map<String, dynamic> json) =>
      _$NutritionPer100gDtoFromJson(json);

  NutritionInfo toEntity() => NutritionInfo(
        energyKcal: energyKcal,
        proteinG: proteinG,
        carbG: carbG,
        lipidG: lipidG,
      );
}
