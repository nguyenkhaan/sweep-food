// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'meal_plan_dto.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

_MealPlanEntryDto _$MealPlanEntryDtoFromJson(Map<String, dynamic> json) =>
    _MealPlanEntryDto(
      date: DateTime.parse(json['date'] as String),
      slot: json['slot'] as String,
      dishId: json['dish_id'] as String,
      dishName: json['dish_name'] as String?,
      dishImageUrl: json['dish_image_url'] as String?,
    );

Map<String, dynamic> _$MealPlanEntryDtoToJson(_MealPlanEntryDto instance) =>
    <String, dynamic>{
      'date': instance.date.toIso8601String(),
      'slot': instance.slot,
      'dish_id': instance.dishId,
      'dish_name': instance.dishName,
      'dish_image_url': instance.dishImageUrl,
    };

_MealPlanDto _$MealPlanDtoFromJson(Map<String, dynamic> json) => _MealPlanDto(
      weekStart: DateTime.parse(json['week_start'] as String),
      entries: (json['entries'] as List<dynamic>?)
              ?.map((e) => MealPlanEntryDto.fromJson(e as Map<String, dynamic>))
              .toList() ??
          const <MealPlanEntryDto>[],
    );

Map<String, dynamic> _$MealPlanDtoToJson(_MealPlanDto instance) =>
    <String, dynamic>{
      'week_start': instance.weekStart.toIso8601String(),
      'entries': instance.entries,
    };
