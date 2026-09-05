// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'cooking_preview_dto.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

_ProposedDeductionDto _$ProposedDeductionDtoFromJson(
  Map<String, dynamic> json,
) => _ProposedDeductionDto(
  recipeIngredientId: json['recipe_ingredient_id'] as String,
  batchId: json['batch_id'] as String,
  quantity: (json['quantity'] as num).toDouble(),
  unit: json['unit'] as String,
  masterIngredientId: json['master_ingredient_id'] as String?,
);

Map<String, dynamic> _$ProposedDeductionDtoToJson(
  _ProposedDeductionDto instance,
) => <String, dynamic>{
  'recipe_ingredient_id': instance.recipeIngredientId,
  'batch_id': instance.batchId,
  'quantity': instance.quantity,
  'unit': instance.unit,
  'master_ingredient_id': instance.masterIngredientId,
};

_MissingIngredientPreviewDto _$MissingIngredientPreviewDtoFromJson(
  Map<String, dynamic> json,
) => _MissingIngredientPreviewDto(
  recipeIngredientId: json['recipe_ingredient_id'] as String,
  ingredientName: json['ingredient_name'] as String,
  missingQuantity: (json['missing_quantity'] as num).toDouble(),
  unit: json['unit'] as String,
);

Map<String, dynamic> _$MissingIngredientPreviewDtoToJson(
  _MissingIngredientPreviewDto instance,
) => <String, dynamic>{
  'recipe_ingredient_id': instance.recipeIngredientId,
  'ingredient_name': instance.ingredientName,
  'missing_quantity': instance.missingQuantity,
  'unit': instance.unit,
};

_CookingPreviewResponseDto _$CookingPreviewResponseDtoFromJson(
  Map<String, dynamic> json,
) => _CookingPreviewResponseDto(
  recipeId: json['recipe_id'] as String,
  recipeName: json['recipe_name'] as String,
  servings: (json['servings'] as num).toDouble(),
  proposedDeductions:
      (json['proposed_deductions'] as List<dynamic>?)
          ?.map((e) => ProposedDeductionDto.fromJson(e as Map<String, dynamic>))
          .toList() ??
      const <ProposedDeductionDto>[],
  missingIngredients:
      (json['missing_ingredients'] as List<dynamic>?)
          ?.map(
            (e) =>
                MissingIngredientPreviewDto.fromJson(e as Map<String, dynamic>),
          )
          .toList() ??
      const <MissingIngredientPreviewDto>[],
);

Map<String, dynamic> _$CookingPreviewResponseDtoToJson(
  _CookingPreviewResponseDto instance,
) => <String, dynamic>{
  'recipe_id': instance.recipeId,
  'recipe_name': instance.recipeName,
  'servings': instance.servings,
  'proposed_deductions': instance.proposedDeductions,
  'missing_ingredients': instance.missingIngredients,
};
