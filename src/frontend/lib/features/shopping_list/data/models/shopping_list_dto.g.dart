// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'shopping_list_dto.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

_ShoppingListItemDto _$ShoppingListItemDtoFromJson(Map<String, dynamic> json) =>
    _ShoppingListItemDto(
      id: json['id'] as String,
      masterIngredientId: json['master_ingredient_id'] as String?,
      customName: json['custom_name'] as String?,
      name: json['name'] as String,
      requiredQuantity: (json['required_quantity'] as num?)?.toDouble() ?? 0,
      availableQuantity: (json['available_quantity'] as num?)?.toDouble() ?? 0,
      missingQuantity: (json['missing_quantity'] as num?)?.toDouble() ?? 0,
      unit: json['unit'] as String,
      estimatedCost: json['estimated_cost'] as num?,
      isChecked: json['is_checked'] as bool? ?? false,
      isGenerated: json['is_generated'] as bool? ?? true,
      sourceRecipeIds:
          (json['source_recipe_ids'] as List<dynamic>?)
              ?.map((e) => e as String)
              .toList() ??
          const <String>[],
      inventoryBatchId: json['inventory_batch_id'] as String?,
    );

Map<String, dynamic> _$ShoppingListItemDtoToJson(
  _ShoppingListItemDto instance,
) => <String, dynamic>{
  'id': instance.id,
  'master_ingredient_id': instance.masterIngredientId,
  'custom_name': instance.customName,
  'name': instance.name,
  'required_quantity': instance.requiredQuantity,
  'available_quantity': instance.availableQuantity,
  'missing_quantity': instance.missingQuantity,
  'unit': instance.unit,
  'estimated_cost': instance.estimatedCost,
  'is_checked': instance.isChecked,
  'is_generated': instance.isGenerated,
  'source_recipe_ids': instance.sourceRecipeIds,
  'inventory_batch_id': instance.inventoryBatchId,
};

_ShoppingListDto _$ShoppingListDtoFromJson(Map<String, dynamic> json) =>
    _ShoppingListDto(
      id: json['id'] as String,
      mealPlanId: json['meal_plan_id'] as String?,
      status: json['status'] as String? ?? 'ACTIVE',
      generatedAt: json['generated_at'] == null
          ? null
          : DateTime.parse(json['generated_at'] as String),
      items:
          (json['items'] as List<dynamic>?)
              ?.map(
                (e) => ShoppingListItemDto.fromJson(e as Map<String, dynamic>),
              )
              .toList() ??
          const <ShoppingListItemDto>[],
    );

Map<String, dynamic> _$ShoppingListDtoToJson(_ShoppingListDto instance) =>
    <String, dynamic>{
      'id': instance.id,
      'meal_plan_id': instance.mealPlanId,
      'status': instance.status,
      'generated_at': instance.generatedAt?.toIso8601String(),
      'items': instance.items,
    };
