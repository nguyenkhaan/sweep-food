import 'package:freezed_annotation/freezed_annotation.dart';
import 'package:frontend/features/dishes/data/models/dish_dto.dart';
import 'package:frontend/features/suggestions/domain/entities/dish_suggestion.dart';
import 'package:frontend/features/suggestions/domain/entities/score_breakdown.dart';

part 'dish_suggestion_dto.freezed.dart';
part 'dish_suggestion_dto.g.dart';

@freezed
abstract class DishSuggestionDto with _$DishSuggestionDto {
  const DishSuggestionDto._();

  const factory DishSuggestionDto({
    required DishDto dish,
    ScoreBreakdownDto? breakdown,
    @JsonKey(name: 'near_expiry_ingredients')
    @Default(<String>[])
    List<String> nearExpiryIngredients,
    @JsonKey(name: 'availability_ratio') @Default(0) double availabilityRatio,
    @JsonKey(name: 'to_buy_count') @Default(0) int toBuyCount,
    int? score,
  }) = _DishSuggestionDto;

  factory DishSuggestionDto.fromJson(Map<String, dynamic> json) =>
      _$DishSuggestionDtoFromJson(json);

  DishSuggestion toEntity() => DishSuggestion(
        dish: dish.toEntity(),
        breakdown: (breakdown ?? const ScoreBreakdownDto()).toEntity(),
        nearExpiryIngredients: nearExpiryIngredients,
        availabilityRatio: availabilityRatio,
        toBuyCount: toBuyCount,
        scoreOverride: score,
      );
}

@freezed
abstract class ScoreBreakdownDto with _$ScoreBreakdownDto {
  const ScoreBreakdownDto._();

  const factory ScoreBreakdownDto({
    @Default(0) double e,
    @Default(0) double a,
    @Default(0) double p,
    @Default(0) double u,
  }) = _ScoreBreakdownDto;

  factory ScoreBreakdownDto.fromJson(Map<String, dynamic> json) =>
      _$ScoreBreakdownDtoFromJson(json);

  ScoreBreakdown toEntity() => ScoreBreakdown(e: e, a: a, p: p, u: u);
}
