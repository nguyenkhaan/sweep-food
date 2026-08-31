// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'dish_dto.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

_DishDto _$DishDtoFromJson(Map<String, dynamic> json) => _DishDto(
  id: json['id'] as String,
  name: json['name'] as String,
  servings: (json['servings'] as num?)?.toInt() ?? 1,
  prepTimeMin: (json['prep_time_min'] as num?)?.toInt() ?? 0,
  cookTimeMin: (json['cook_time_min'] as num?)?.toInt() ?? 0,
  cuisine: json['cuisine'] as String? ?? '',
  difficulty: json['difficulty'] as String? ?? '',
  imageUrl: json['image_url'] as String?,
  nutritionPerServing: json['nutrition_per_serving'] == null
      ? null
      : MacrosDto.fromJson(
          json['nutrition_per_serving'] as Map<String, dynamic>,
        ),
  ingredients:
      (json['ingredients'] as List<dynamic>?)
          ?.map((e) => DishIngredientDto.fromJson(e as Map<String, dynamic>))
          .toList() ??
      const <DishIngredientDto>[],
  steps:
      (json['steps'] as List<dynamic>?)
          ?.map((e) => CookingStepDto.fromJson(e as Map<String, dynamic>))
          .toList() ??
      const <CookingStepDto>[],
);

Map<String, dynamic> _$DishDtoToJson(_DishDto instance) => <String, dynamic>{
  'id': instance.id,
  'name': instance.name,
  'servings': instance.servings,
  'prep_time_min': instance.prepTimeMin,
  'cook_time_min': instance.cookTimeMin,
  'cuisine': instance.cuisine,
  'difficulty': instance.difficulty,
  'image_url': instance.imageUrl,
  'nutrition_per_serving': instance.nutritionPerServing,
  'ingredients': instance.ingredients,
  'steps': instance.steps,
};

_DishIngredientDto _$DishIngredientDtoFromJson(Map<String, dynamic> json) =>
    _DishIngredientDto(
      name: json['name'] as String,
      quantity: (json['quantity'] as num?)?.toDouble() ?? 0,
      unit: json['unit'] as String? ?? 'g',
      isSeasoning: json['is_seasoning'] as bool? ?? false,
      availableInPantry: json['available_in_pantry'] as bool? ?? false,
      missingQty: (json['missing_qty'] as num?)?.toDouble() ?? 0,
      nearExpiry: json['near_expiry'] as bool? ?? false,
      pantryItemId: json['pantry_item_id'] as String?,
    );

Map<String, dynamic> _$DishIngredientDtoToJson(_DishIngredientDto instance) =>
    <String, dynamic>{
      'name': instance.name,
      'quantity': instance.quantity,
      'unit': instance.unit,
      'is_seasoning': instance.isSeasoning,
      'available_in_pantry': instance.availableInPantry,
      'missing_qty': instance.missingQty,
      'near_expiry': instance.nearExpiry,
      'pantry_item_id': instance.pantryItemId,
    };

_CookingStepDto _$CookingStepDtoFromJson(Map<String, dynamic> json) =>
    _CookingStepDto(
      order: (json['order'] as num).toInt(),
      text: json['text'] as String,
      durationMin: (json['duration_min'] as num?)?.toInt(),
    );

Map<String, dynamic> _$CookingStepDtoToJson(_CookingStepDto instance) =>
    <String, dynamic>{
      'order': instance.order,
      'text': instance.text,
      'duration_min': instance.durationMin,
    };

_MacrosDto _$MacrosDtoFromJson(Map<String, dynamic> json) => _MacrosDto(
  energyKcal: (json['energy_kcal'] as num?)?.toDouble() ?? 0,
  proteinG: (json['protein_g'] as num?)?.toDouble() ?? 0,
  carbG: (json['carb_g'] as num?)?.toDouble() ?? 0,
  lipidG: (json['lipid_g'] as num?)?.toDouble() ?? 0,
);

Map<String, dynamic> _$MacrosDtoToJson(_MacrosDto instance) =>
    <String, dynamic>{
      'energy_kcal': instance.energyKcal,
      'protein_g': instance.proteinG,
      'carb_g': instance.carbG,
      'lipid_g': instance.lipidG,
    };
