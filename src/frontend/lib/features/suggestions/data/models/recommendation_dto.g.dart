// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'recommendation_dto.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

_MockRecommendationAnalysisDto _$MockRecommendationAnalysisDtoFromJson(
  Map<String, dynamic> json,
) => _MockRecommendationAnalysisDto(
  intent: json['intent'] as String? ?? '',
  summary: json['summary'] as String? ?? '',
  isMock: json['is_mock'] as bool? ?? false,
);

Map<String, dynamic> _$MockRecommendationAnalysisDtoToJson(
  _MockRecommendationAnalysisDto instance,
) => <String, dynamic>{
  'intent': instance.intent,
  'summary': instance.summary,
  'is_mock': instance.isMock,
};

_RecommendationMissingIngredientDto
_$RecommendationMissingIngredientDtoFromJson(Map<String, dynamic> json) =>
    _RecommendationMissingIngredientDto(
      masterIngredientId: json['master_ingredient_id'] as String?,
      name: json['name'] as String,
      quantity: json['quantity'] == null
          ? 0.0
          : _asDoubleDefault(json['quantity']),
      unit: json['unit'] as String? ?? '',
    );

Map<String, dynamic> _$RecommendationMissingIngredientDtoToJson(
  _RecommendationMissingIngredientDto instance,
) => <String, dynamic>{
  'master_ingredient_id': instance.masterIngredientId,
  'name': instance.name,
  'quantity': instance.quantity,
  'unit': instance.unit,
};
