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

    /// Stable position returned by the AI service after feasibility re-ranking.
    @Default(1) int rank,

    /// Raw LightGBM score. This is intentionally not presented as a percent.
    @Default(0) double rankScore,

    @Default(RecommendationRankingFeatures())
    RecommendationRankingFeatures rankingFeatures,

    @Default(<RecommendationIngredient>[])
    List<RecommendationIngredient> matchedIngredients,

    @Default(<RecommendationIngredient>[])
    List<RecommendationIngredient> missingIngredients,

    @Default(<RecommendationIngredient>[])
    List<RecommendationIngredient> optionalIngredients,

    @Default('') String statusBadge,
    @Default('') String provider,
    @Default('') String modelVersion,
    @Default('') String rankerModel,
    @Default(0) double totalLatencyMs,

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

  bool get isTopChoice => rank == 1;

  String get statusLabel => switch (statusBadge) {
    'ready' => 'Sẵn sàng nấu',
    'elastic' => 'Thiếu nhẹ, có thể linh hoạt',
    'shopping' => 'Cần mua thêm',
    _ => toBuyCount == 0 ? 'Sẵn sàng nấu' : 'Cần mua thêm',
  };
}

/// Exact contextual feature vector exposed by SweepFood AI contract v2.
class RecommendationRankingFeatures {
  const RecommendationRankingFeatures({
    this.coreCoverage = 0,
    this.coreMissingCount = 0,
    this.secondaryCoverage = 0,
    this.shoppingGapItems = 0,
    this.rescueWeightG = 0,
    this.nutritionConfidence = 0,
    this.kcalPerServing = 0,
    this.proteinPerServing = 0,
    this.prepComplexity = 0,
  });

  final double coreCoverage;
  final double coreMissingCount;
  final double secondaryCoverage;
  final double shoppingGapItems;
  final double rescueWeightG;
  final double nutritionConfidence;
  final double kcalPerServing;
  final double proteinPerServing;
  final double prepComplexity;
}

class RecommendationIngredient {
  const RecommendationIngredient({
    required this.name,
    this.code,
    this.requiredG = 0,
  });

  final String name;
  final String? code;
  final double requiredG;
}
