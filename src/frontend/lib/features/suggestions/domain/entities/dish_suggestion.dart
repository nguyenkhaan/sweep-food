import 'package:freezed_annotation/freezed_annotation.dart';
import 'package:sweepfood/features/dishes/domain/entities/dish.dart';
import 'package:sweepfood/features/suggestions/domain/entities/score_breakdown.dart';

part 'dish_suggestion.freezed.dart';

/// A scored recipe recommendation (S-01 card, H-01 quick suggestions).
@freezed
abstract class DishSuggestion with _$DishSuggestion {
  const DishSuggestion._();

  const factory DishSuggestion({
    required Dish dish,
    required ScoreBreakdown breakdown,

    /// Names of near-expiry pantry ingredients this dish would use.
    @Default(<String>[]) List<String> nearExpiryIngredients,

    /// Share of the dish's ingredients already in the pantry (`0..1`).
    @Default(0) double availabilityRatio,

    /// How many ingredients still need buying.
    @Default(0) int toBuyCount,

    /// Server-provided score override; falls back to [breakdown.scoreOutOf100].
    int? scoreOverride,

    /// Human-readable explanation from recommendation engine / mock provider.
    String? explanation,

    /// True if the score and ranking are from a mock provider (`analysis.is_mock`).
    @Default(false) bool isMock,
  }) = _DishSuggestion;

  String get id => dish.id;

  int get score => scoreOverride ?? breakdown.scoreOutOf100;

  int get nearExpiryCount => nearExpiryIngredients.length;

  int get availabilityPercent => (availabilityRatio * 100).round();
}
