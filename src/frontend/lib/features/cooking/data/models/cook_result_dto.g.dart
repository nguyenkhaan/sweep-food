// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'cook_result_dto.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

_CookResultDto _$CookResultDtoFromJson(Map<String, dynamic> json) =>
    _CookResultDto(
      dishId: json['dish_id'] as String? ?? '',
      dishName: json['dish_name'] as String? ?? '',
      changes:
          (json['changes'] as List<dynamic>?)
              ?.map((e) => PantryChangeDto.fromJson(e as Map<String, dynamic>))
              .toList() ??
          const <PantryChangeDto>[],
      updatedPantryItems:
          (json['updated_pantry_items'] as List<dynamic>?)
              ?.map((e) => PantryItemDto.fromJson(e as Map<String, dynamic>))
              .toList() ??
          const <PantryItemDto>[],
      depletedItemIds:
          (json['depleted_item_ids'] as List<dynamic>?)
              ?.map((e) => e as String)
              .toList() ??
          const <String>[],
      nearExpiryUsedCount:
          (json['near_expiry_used_count'] as num?)?.toInt() ?? 0,
      wasteAvoidedGrams: (json['waste_avoided_grams'] as num?)?.toDouble() ?? 0,
      leftoverServings: (json['leftover_servings'] as num?)?.toInt() ?? 0,
    );

Map<String, dynamic> _$CookResultDtoToJson(_CookResultDto instance) =>
    <String, dynamic>{
      'dish_id': instance.dishId,
      'dish_name': instance.dishName,
      'changes': instance.changes,
      'updated_pantry_items': instance.updatedPantryItems,
      'depleted_item_ids': instance.depletedItemIds,
      'near_expiry_used_count': instance.nearExpiryUsedCount,
      'waste_avoided_grams': instance.wasteAvoidedGrams,
      'leftover_servings': instance.leftoverServings,
    };

_PantryChangeDto _$PantryChangeDtoFromJson(Map<String, dynamic> json) =>
    _PantryChangeDto(
      name: json['name'] as String,
      unit: json['unit'] as String? ?? 'g',
      before: (json['before'] as num?)?.toDouble() ?? 0,
      after: (json['after'] as num?)?.toDouble() ?? 0,
      nearExpiryUsed: json['near_expiry_used'] as bool? ?? false,
      pantryItemId: json['pantry_item_id'] as String?,
    );

Map<String, dynamic> _$PantryChangeDtoToJson(_PantryChangeDto instance) =>
    <String, dynamic>{
      'name': instance.name,
      'unit': instance.unit,
      'before': instance.before,
      'after': instance.after,
      'near_expiry_used': instance.nearExpiryUsed,
      'pantry_item_id': instance.pantryItemId,
    };
