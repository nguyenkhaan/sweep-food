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

_RecommendationRankingFeaturesDto _$RecommendationRankingFeaturesDtoFromJson(
  Map<String, dynamic> json,
) => _RecommendationRankingFeaturesDto(
  coreCoverage: json['core_coverage'] == null
      ? 0.0
      : _asDoubleDefault(json['core_coverage']),
  coreMissingCount: json['core_missing_count'] == null
      ? 0.0
      : _asDoubleDefault(json['core_missing_count']),
  secondaryCoverage: json['secondary_coverage'] == null
      ? 0.0
      : _asDoubleDefault(json['secondary_coverage']),
  shoppingGapItems: json['shopping_gap_items'] == null
      ? 0.0
      : _asDoubleDefault(json['shopping_gap_items']),
  rescueWeightG: json['rescue_weight_g'] == null
      ? 0.0
      : _asDoubleDefault(json['rescue_weight_g']),
  nutritionConfidence: json['nutrition_confidence'] == null
      ? 0.0
      : _asDoubleDefault(json['nutrition_confidence']),
  kcalPerServing: json['kcal_per_serving'] == null
      ? 0.0
      : _asDoubleDefault(json['kcal_per_serving']),
  proteinPerServing: json['protein_per_serving'] == null
      ? 0.0
      : _asDoubleDefault(json['protein_per_serving']),
  prepComplexity: json['prep_complexity'] == null
      ? 0.0
      : _asDoubleDefault(json['prep_complexity']),
);

Map<String, dynamic> _$RecommendationRankingFeaturesDtoToJson(
  _RecommendationRankingFeaturesDto instance,
) => <String, dynamic>{
  'core_coverage': instance.coreCoverage,
  'core_missing_count': instance.coreMissingCount,
  'secondary_coverage': instance.secondaryCoverage,
  'shopping_gap_items': instance.shoppingGapItems,
  'rescue_weight_g': instance.rescueWeightG,
  'nutrition_confidence': instance.nutritionConfidence,
  'kcal_per_serving': instance.kcalPerServing,
  'protein_per_serving': instance.proteinPerServing,
  'prep_complexity': instance.prepComplexity,
};

_RecommendationTimingsDto _$RecommendationTimingsDtoFromJson(
  Map<String, dynamic> json,
) => _RecommendationTimingsDto(
  totalMs: json['total_ms'] == null ? 0.0 : _asDoubleDefault(json['total_ms']),
  candidateMs: json['candidate_ms'] == null
      ? 0.0
      : _asDoubleDefault(json['candidate_ms']),
  rankerMs: json['ranker_ms'] == null
      ? 0.0
      : _asDoubleDefault(json['ranker_ms']),
);

Map<String, dynamic> _$RecommendationTimingsDtoToJson(
  _RecommendationTimingsDto instance,
) => <String, dynamic>{
  'total_ms': instance.totalMs,
  'candidate_ms': instance.candidateMs,
  'ranker_ms': instance.rankerMs,
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
