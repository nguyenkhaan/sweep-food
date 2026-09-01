// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'ingredient_dto.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

_IngredientDto _$IngredientDtoFromJson(Map<String, dynamic> json) =>
    _IngredientDto(
      id: json['id'] as String,
      name: json['name'] as String,
      category: IngredientCategoryDto.fromJson(
        json['category'] as Map<String, dynamic>,
      ),
      defaultUnit: json['default_unit'] as String? ?? 'GRAM',
      defaultStorageMode: json['default_storage_mode'] as String?,
      aliases:
          (json['aliases'] as List<dynamic>?)
              ?.map((e) => e as String)
              .toList() ??
          const <String>[],
      description: json['description'] as String?,
      nutrition: json['nutrition'] == null
          ? null
          : IngredientNutritionDto.fromJson(
              json['nutrition'] as Map<String, dynamic>,
            ),
      shelfLifeRules:
          (json['shelf_life_rules'] as List<dynamic>?)
              ?.map((e) => ShelfLifeRuleDto.fromJson(e as Map<String, dynamic>))
              .toList() ??
          const <ShelfLifeRuleDto>[],
    );

Map<String, dynamic> _$IngredientDtoToJson(_IngredientDto instance) =>
    <String, dynamic>{
      'id': instance.id,
      'name': instance.name,
      'category': instance.category,
      'default_unit': instance.defaultUnit,
      'default_storage_mode': instance.defaultStorageMode,
      'aliases': instance.aliases,
      'description': instance.description,
      'nutrition': instance.nutrition,
      'shelf_life_rules': instance.shelfLifeRules,
    };

_IngredientCategoryDto _$IngredientCategoryDtoFromJson(
  Map<String, dynamic> json,
) => _IngredientCategoryDto(
  id: json['id'] as String,
  name: json['name'] as String,
);

Map<String, dynamic> _$IngredientCategoryDtoToJson(
  _IngredientCategoryDto instance,
) => <String, dynamic>{'id': instance.id, 'name': instance.name};

_IngredientNutritionDto _$IngredientNutritionDtoFromJson(
  Map<String, dynamic> json,
) => _IngredientNutritionDto(
  calories: _asDouble(json['calories']),
  proteinG: _asDouble(json['protein_g']),
  fatG: _asDouble(json['fat_g']),
  carbsG: _asDouble(json['carbs_g']),
  sugarG: _asDouble(json['sugar_g']),
  sodiumMg: _asDouble(json['sodium_mg']),
);

Map<String, dynamic> _$IngredientNutritionDtoToJson(
  _IngredientNutritionDto instance,
) => <String, dynamic>{
  'calories': instance.calories,
  'protein_g': instance.proteinG,
  'fat_g': instance.fatG,
  'carbs_g': instance.carbsG,
  'sugar_g': instance.sugarG,
  'sodium_mg': instance.sodiumMg,
};

_ShelfLifeRuleDto _$ShelfLifeRuleDtoFromJson(Map<String, dynamic> json) =>
    _ShelfLifeRuleDto(
      scope: json['scope'] as String?,
      storageMode: json['storage_mode'] as String?,
      minDays: (json['min_days'] as num?)?.toInt(),
      maxDays: (json['max_days'] as num?)?.toInt(),
      defaultDays: (json['default_days'] as num?)?.toInt() ?? 0,
    );

Map<String, dynamic> _$ShelfLifeRuleDtoToJson(_ShelfLifeRuleDto instance) =>
    <String, dynamic>{
      'scope': instance.scope,
      'storage_mode': instance.storageMode,
      'min_days': instance.minDays,
      'max_days': instance.maxDays,
      'default_days': instance.defaultDays,
    };
