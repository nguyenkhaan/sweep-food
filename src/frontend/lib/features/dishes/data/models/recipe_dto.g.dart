// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'recipe_dto.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

_RecipeDto _$RecipeDtoFromJson(Map<String, dynamic> json) => _RecipeDto(
  id: json['id'] as String,
  name: json['name'] as String,
  description: json['description'] as String? ?? '',
  mediaUrl: json['media_url'] as String?,
  defaultServings: _asDouble(json['default_servings']),
  estimatedCookingMinutes:
      (json['estimated_cooking_minutes'] as num?)?.toInt() ?? 0,
  estimatedCost: _asDouble(json['estimated_cost']),
  servings: _asDouble(json['servings']),
  instructions: json['instructions'] as Map<String, dynamic>?,
  nutrition: json['nutrition'] == null
      ? null
      : RecipeNutritionDto.fromJson(json['nutrition'] as Map<String, dynamic>),
  ingredients:
      (json['ingredients'] as List<dynamic>?)
          ?.map((e) => RecipeIngredientDto.fromJson(e as Map<String, dynamic>))
          .toList() ??
      const <RecipeIngredientDto>[],
);

Map<String, dynamic> _$RecipeDtoToJson(_RecipeDto instance) =>
    <String, dynamic>{
      'id': instance.id,
      'name': instance.name,
      'description': instance.description,
      'media_url': instance.mediaUrl,
      'default_servings': instance.defaultServings,
      'estimated_cooking_minutes': instance.estimatedCookingMinutes,
      'estimated_cost': instance.estimatedCost,
      'servings': instance.servings,
      'instructions': instance.instructions,
      'nutrition': instance.nutrition,
      'ingredients': instance.ingredients,
    };

_RecipeNutritionDto _$RecipeNutritionDtoFromJson(Map<String, dynamic> json) =>
    _RecipeNutritionDto(
      calories: _asDouble(json['calories']),
      proteinG: _asDouble(json['protein_g']),
      fatG: _asDouble(json['fat_g']),
      carbsG: _asDouble(json['carbs_g']),
      sugarG: _asDouble(json['sugar_g']),
    );

Map<String, dynamic> _$RecipeNutritionDtoToJson(_RecipeNutritionDto instance) =>
    <String, dynamic>{
      'calories': instance.calories,
      'protein_g': instance.proteinG,
      'fat_g': instance.fatG,
      'carbs_g': instance.carbsG,
      'sugar_g': instance.sugarG,
    };

_RecipeIngredientDto _$RecipeIngredientDtoFromJson(Map<String, dynamic> json) =>
    _RecipeIngredientDto(
      recipeIngredientId: json['recipe_ingredient_id'] as String?,
      masterIngredientId: json['master_ingredient_id'] as String?,
      name: json['name'] as String? ?? '',
      requiredQuantity: _asDouble(json['required_quantity']),
      unit: json['unit'] as String? ?? 'GRAM',
      isOptional: json['is_optional'] as bool? ?? false,
      preparationNote: json['preparation_note'] as String?,
    );

Map<String, dynamic> _$RecipeIngredientDtoToJson(
  _RecipeIngredientDto instance,
) => <String, dynamic>{
  'recipe_ingredient_id': instance.recipeIngredientId,
  'master_ingredient_id': instance.masterIngredientId,
  'name': instance.name,
  'required_quantity': instance.requiredQuantity,
  'unit': instance.unit,
  'is_optional': instance.isOptional,
  'preparation_note': instance.preparationNote,
};
