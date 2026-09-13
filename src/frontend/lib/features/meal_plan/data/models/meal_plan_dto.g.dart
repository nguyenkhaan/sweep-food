// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'meal_plan_dto.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

_MealPlanItemDto _$MealPlanItemDtoFromJson(Map<String, dynamic> json) =>
    _MealPlanItemDto(
      id: json['id'] as String,
      recipeId: json['recipe_id'] as String,
      recipeName: json['recipe_name'] as String?,
      plannedFor: DateTime.parse(json['planned_for'] as String),
      mealSlot: json['meal_slot'] as String,
      servings: (json['servings'] as num).toDouble(),
      status: json['status'] as String? ?? 'PLANNED',
    );

Map<String, dynamic> _$MealPlanItemDtoToJson(_MealPlanItemDto instance) =>
    <String, dynamic>{
      'id': instance.id,
      'recipe_id': instance.recipeId,
      'recipe_name': instance.recipeName,
      'planned_for': instance.plannedFor.toIso8601String(),
      'meal_slot': instance.mealSlot,
      'servings': instance.servings,
      'status': instance.status,
    };

_MealPlanDto _$MealPlanDtoFromJson(Map<String, dynamic> json) => _MealPlanDto(
  id: json['id'] as String,
  name: json['name'] as String?,
  startsOn: DateTime.parse(json['starts_on'] as String),
  endsOn: DateTime.parse(json['ends_on'] as String),
  items:
      (json['items'] as List<dynamic>?)
          ?.map((e) => MealPlanItemDto.fromJson(e as Map<String, dynamic>))
          .toList() ??
      const <MealPlanItemDto>[],
);

Map<String, dynamic> _$MealPlanDtoToJson(_MealPlanDto instance) =>
    <String, dynamic>{
      'id': instance.id,
      'name': instance.name,
      'starts_on': instance.startsOn.toIso8601String(),
      'ends_on': instance.endsOn.toIso8601String(),
      'items': instance.items,
    };
