// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'dish_suggestion_dto.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

_DishSuggestionDto _$DishSuggestionDtoFromJson(Map<String, dynamic> json) =>
    _DishSuggestionDto(
      dish: DishDto.fromJson(json['dish'] as Map<String, dynamic>),
      breakdown: json['breakdown'] == null
          ? null
          : ScoreBreakdownDto.fromJson(
              json['breakdown'] as Map<String, dynamic>,
            ),
      nearExpiryIngredients:
          (json['near_expiry_ingredients'] as List<dynamic>?)
              ?.map((e) => e as String)
              .toList() ??
          const <String>[],
      availabilityRatio: (json['availability_ratio'] as num?)?.toDouble() ?? 0,
      toBuyCount: (json['to_buy_count'] as num?)?.toInt() ?? 0,
      score: (json['score'] as num?)?.toInt(),
    );

Map<String, dynamic> _$DishSuggestionDtoToJson(_DishSuggestionDto instance) =>
    <String, dynamic>{
      'dish': instance.dish,
      'breakdown': instance.breakdown,
      'near_expiry_ingredients': instance.nearExpiryIngredients,
      'availability_ratio': instance.availabilityRatio,
      'to_buy_count': instance.toBuyCount,
      'score': instance.score,
    };

_ScoreBreakdownDto _$ScoreBreakdownDtoFromJson(Map<String, dynamic> json) =>
    _ScoreBreakdownDto(
      e: (json['e'] as num?)?.toDouble() ?? 0,
      a: (json['a'] as num?)?.toDouble() ?? 0,
      p: (json['p'] as num?)?.toDouble() ?? 0,
      u: (json['u'] as num?)?.toDouble() ?? 0,
    );

Map<String, dynamic> _$ScoreBreakdownDtoToJson(_ScoreBreakdownDto instance) =>
    <String, dynamic>{
      'e': instance.e,
      'a': instance.a,
      'p': instance.p,
      'u': instance.u,
    };
