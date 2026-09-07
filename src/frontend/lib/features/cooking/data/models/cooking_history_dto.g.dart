// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'cooking_history_dto.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

_CookingHistorySummaryDto _$CookingHistorySummaryDtoFromJson(
  Map<String, dynamic> json,
) => _CookingHistorySummaryDto(
  sessionId: json['session_id'] as String,
  recipeId: json['recipe_id'] as String,
  recipeName: json['recipe_name'] as String? ?? '',
  servings: json['servings'] == null ? 0 : _asDouble(json['servings']),
  status: json['status'] as String? ?? 'COMPLETED',
  completedAt: json['completed_at'] == null
      ? null
      : DateTime.parse(json['completed_at'] as String),
);

Map<String, dynamic> _$CookingHistorySummaryDtoToJson(
  _CookingHistorySummaryDto instance,
) => <String, dynamic>{
  'session_id': instance.sessionId,
  'recipe_id': instance.recipeId,
  'recipe_name': instance.recipeName,
  'servings': instance.servings,
  'status': instance.status,
  'completed_at': instance.completedAt?.toIso8601String(),
};

_CookingHistoryListDto _$CookingHistoryListDtoFromJson(
  Map<String, dynamic> json,
) => _CookingHistoryListDto(
  items:
      (json['items'] as List<dynamic>?)
          ?.map(
            (e) => CookingHistorySummaryDto.fromJson(e as Map<String, dynamic>),
          )
          .toList() ??
      const <CookingHistorySummaryDto>[],
);

Map<String, dynamic> _$CookingHistoryListDtoToJson(
  _CookingHistoryListDto instance,
) => <String, dynamic>{'items': instance.items};

_CookingConsumptionDto _$CookingConsumptionDtoFromJson(
  Map<String, dynamic> json,
) => _CookingConsumptionDto(
  recipeIngredientId: json['recipe_ingredient_id'] as String?,
  inventoryBatchId: json['inventory_batch_id'] as String,
  quantity: json['quantity'] == null ? 0 : _asDouble(json['quantity']),
  unit: json['unit'] as String? ?? 'GRAM',
);

Map<String, dynamic> _$CookingConsumptionDtoToJson(
  _CookingConsumptionDto instance,
) => <String, dynamic>{
  'recipe_ingredient_id': instance.recipeIngredientId,
  'inventory_batch_id': instance.inventoryBatchId,
  'quantity': instance.quantity,
  'unit': instance.unit,
};

_CookingSessionDto _$CookingSessionDtoFromJson(Map<String, dynamic> json) =>
    _CookingSessionDto(
      id: json['id'] as String,
      recipeId: json['recipe_id'] as String,
      mealPlanItemId: json['meal_plan_item_id'] as String?,
      servings: json['servings'] == null ? 0 : _asDouble(json['servings']),
      status: json['status'] as String? ?? 'COMPLETED',
      consumptionMode: json['consumption_mode'] as String?,
      completedAt: json['completed_at'] == null
          ? null
          : DateTime.parse(json['completed_at'] as String),
    );

Map<String, dynamic> _$CookingSessionDtoToJson(_CookingSessionDto instance) =>
    <String, dynamic>{
      'id': instance.id,
      'recipe_id': instance.recipeId,
      'meal_plan_item_id': instance.mealPlanItemId,
      'servings': instance.servings,
      'status': instance.status,
      'consumption_mode': instance.consumptionMode,
      'completed_at': instance.completedAt?.toIso8601String(),
    };

_CookingHistoryDetailDto _$CookingHistoryDetailDtoFromJson(
  Map<String, dynamic> json,
) => _CookingHistoryDetailDto(
  session: CookingSessionDto.fromJson(json['session'] as Map<String, dynamic>),
  recipeId: json['recipe_id'] as String,
  recipeName: json['recipe_name'] as String? ?? '',
  consumptions:
      (json['consumptions'] as List<dynamic>?)
          ?.map(
            (e) => CookingConsumptionDto.fromJson(e as Map<String, dynamic>),
          )
          .toList() ??
      const <CookingConsumptionDto>[],
  leftoverBatchId: json['leftover_batch_id'] as String?,
  completedAt: json['completed_at'] == null
      ? null
      : DateTime.parse(json['completed_at'] as String),
);

Map<String, dynamic> _$CookingHistoryDetailDtoToJson(
  _CookingHistoryDetailDto instance,
) => <String, dynamic>{
  'session': instance.session,
  'recipe_id': instance.recipeId,
  'recipe_name': instance.recipeName,
  'consumptions': instance.consumptions,
  'leftover_batch_id': instance.leftoverBatchId,
  'completed_at': instance.completedAt?.toIso8601String(),
};
