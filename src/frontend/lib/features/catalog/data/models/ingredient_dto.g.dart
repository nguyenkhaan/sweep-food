// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'ingredient_dto.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

_IngredientDto _$IngredientDtoFromJson(Map<String, dynamic> json) =>
    _IngredientDto(
      id: json['id'] as String,
      name: json['name'] as String,
      category: json['category'] as String,
      defaultUnit: json['default_unit'] as String? ?? 'g',
      nutritionPer100g: json['nutrition_per_100g'] == null
          ? null
          : NutritionPer100gDto.fromJson(
              json['nutrition_per_100g'] as Map<String, dynamic>,
            ),
      referenceShelfLifeDays: (json['reference_shelf_life_days'] as num?)
          ?.toInt(),
    );

Map<String, dynamic> _$IngredientDtoToJson(_IngredientDto instance) =>
    <String, dynamic>{
      'id': instance.id,
      'name': instance.name,
      'category': instance.category,
      'default_unit': instance.defaultUnit,
      'nutrition_per_100g': instance.nutritionPer100g,
      'reference_shelf_life_days': instance.referenceShelfLifeDays,
    };

_NutritionPer100gDto _$NutritionPer100gDtoFromJson(Map<String, dynamic> json) =>
    _NutritionPer100gDto(
      energyKcal: (json['energy_kcal'] as num?)?.toDouble() ?? 0,
      proteinG: (json['protein_g'] as num?)?.toDouble() ?? 0,
      carbG: (json['carb_g'] as num?)?.toDouble() ?? 0,
      lipidG: (json['lipid_g'] as num?)?.toDouble() ?? 0,
    );

Map<String, dynamic> _$NutritionPer100gDtoToJson(
  _NutritionPer100gDto instance,
) => <String, dynamic>{
  'energy_kcal': instance.energyKcal,
  'protein_g': instance.proteinG,
  'carb_g': instance.carbG,
  'lipid_g': instance.lipidG,
};
