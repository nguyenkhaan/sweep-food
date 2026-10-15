import 'package:freezed_annotation/freezed_annotation.dart';
import 'package:sweepfood/features/dishes/data/models/dish_dto.dart';
import 'package:sweepfood/features/dishes/data/models/recipe_dto.dart';
import 'package:sweepfood/features/suggestions/domain/entities/score_breakdown.dart';

part 'recommendation_dto.freezed.dart';
part 'recommendation_dto.g.dart';

double? _asDouble(dynamic value) {
  if (value == null) return null;
  if (value is num) return value.toDouble();
  return double.tryParse(value.toString());
}

double _asDoubleDefault(dynamic value) => _asDouble(value) ?? 0;

@freezed
abstract class MockRecommendationAnalysisDto
    with _$MockRecommendationAnalysisDto {
  const MockRecommendationAnalysisDto._();

  const factory MockRecommendationAnalysisDto({
    @Default('') String intent,
    @Default('') String summary,
    @JsonKey(name: 'is_mock') @Default(false) bool isMock,
  }) = _MockRecommendationAnalysisDto;

  factory MockRecommendationAnalysisDto.fromJson(Map<String, dynamic> json) =>
      _$MockRecommendationAnalysisDtoFromJson(json);
}

/// Contextual features returned by recommendation contract v2.
@freezed
abstract class RecommendationRankingFeaturesDto
    with _$RecommendationRankingFeaturesDto {
  const RecommendationRankingFeaturesDto._();

  const factory RecommendationRankingFeaturesDto({
    @JsonKey(name: 'core_coverage', fromJson: _asDoubleDefault)
    @Default(0)
    double coreCoverage,
    @JsonKey(name: 'core_missing_count', fromJson: _asDoubleDefault)
    @Default(0)
    double coreMissingCount,
    @JsonKey(name: 'secondary_coverage', fromJson: _asDoubleDefault)
    @Default(0)
    double secondaryCoverage,
    @JsonKey(name: 'shopping_gap_items', fromJson: _asDoubleDefault)
    @Default(0)
    double shoppingGapItems,
    @JsonKey(name: 'rescue_weight_g', fromJson: _asDoubleDefault)
    @Default(0)
    double rescueWeightG,
    @JsonKey(name: 'nutrition_confidence', fromJson: _asDoubleDefault)
    @Default(0)
    double nutritionConfidence,
    @JsonKey(name: 'kcal_per_serving', fromJson: _asDoubleDefault)
    @Default(0)
    double kcalPerServing,
    @JsonKey(name: 'protein_per_serving', fromJson: _asDoubleDefault)
    @Default(0)
    double proteinPerServing,
    @JsonKey(name: 'prep_complexity', fromJson: _asDoubleDefault)
    @Default(0)
    double prepComplexity,
  }) = _RecommendationRankingFeaturesDto;

  factory RecommendationRankingFeaturesDto.fromJson(
    Map<String, dynamic> json,
  ) => _$RecommendationRankingFeaturesDtoFromJson(json);

  RankingFeatures toEntity() => RankingFeatures(
    coreCoverage: coreCoverage,
    coreMissingCount: coreMissingCount,
    secondaryCoverage: secondaryCoverage,
    shoppingGapItems: shoppingGapItems,
    rescueWeightG: rescueWeightG,
    nutritionConfidence: nutritionConfidence,
    kcalPerServing: kcalPerServing,
    proteinPerServing: proteinPerServing,
    prepComplexity: prepComplexity,
  );
}

@freezed
abstract class RecommendationIngredientDto with _$RecommendationIngredientDto {
  const RecommendationIngredientDto._();

  const factory RecommendationIngredientDto({
    @Default('') String name,
    String? code,
    @JsonKey(name: 'required_g', fromJson: _asDoubleDefault)
    @Default(0)
    double requiredG,
    // Legacy fields kept only so old fixtures remain readable.
    @JsonKey(name: 'master_ingredient_id') String? masterIngredientId,
    @JsonKey(fromJson: _asDouble) double? quantity,
    String? unit,
  }) = _RecommendationIngredientDto;

  factory RecommendationIngredientDto.fromJson(Map<String, dynamic> json) =>
      _$RecommendationIngredientDtoFromJson(json);
}

@freezed
abstract class RecommendationTimingsDto with _$RecommendationTimingsDto {
  const factory RecommendationTimingsDto({
    @JsonKey(name: 'total_ms', fromJson: _asDoubleDefault)
    @Default(0)
    double totalMs,
    @JsonKey(name: 'candidate_ms', fromJson: _asDoubleDefault)
    @Default(0)
    double candidateMs,
    @JsonKey(name: 'ranker_ms', fromJson: _asDoubleDefault)
    @Default(0)
    double rankerMs,
  }) = _RecommendationTimingsDto;

  factory RecommendationTimingsDto.fromJson(Map<String, dynamic> json) =>
      _$RecommendationTimingsDtoFromJson(json);
}

@Freezed(toJson: false)
abstract class RecommendationItemDto with _$RecommendationItemDto {
  const RecommendationItemDto._();

  const factory RecommendationItemDto({
    @JsonKey(name: 'recipe_id') required String recipeId,
    @JsonKey(name: 'recipe_name') required String recipeName,
    @Default(1) int rank,
    @JsonKey(name: 'rank_score', fromJson: _asDouble) double? rankScore,
    @JsonKey(name: 'ranking_features')
    RecommendationRankingFeaturesDto? rankingFeatures,
    @JsonKey(name: 'matched_ingredients')
    @Default(<RecommendationIngredientDto>[])
    List<RecommendationIngredientDto> matchedIngredients,
    @JsonKey(name: 'missing_ingredients')
    @Default(<RecommendationIngredientDto>[])
    List<RecommendationIngredientDto> missingIngredients,
    @JsonKey(name: 'optional_ingredients')
    @Default(<RecommendationIngredientDto>[])
    List<RecommendationIngredientDto> optionalIngredients,
    @JsonKey(name: 'rescued_items')
    @Default(<String>[])
    List<String> rescuedItems,
    @JsonKey(name: 'status_badge') @Default('') String statusBadge,
    @Default('') String explanation,
    @Default('') String provider,
    @JsonKey(name: 'recipe_summary') RecipeDto? recipeSummary,
    // Legacy response fields.
    @JsonKey(fromJson: _asDouble) double? score,
    @JsonKey(name: 'score_components')
    @Default(RecommendationScoreComponentsDto())
    RecommendationScoreComponentsDto scoreComponents,
    @JsonKey(name: 'near_expiry_ingredients')
    @Default(<String>[])
    List<String> nearExpiryIngredients,
    DishDto? dish,
  }) = _RecommendationItemDto;

  factory RecommendationItemDto.fromJson(Map<String, dynamic> json) {
    final dishJson = json['dish'];
    final dish = dishJson is Map
        ? DishDto.fromJson(Map<String, dynamic>.from(dishJson))
        : null;
    final summaryJson = json['recipe_summary'];
    final summary = summaryJson is Map
        ? RecipeDto.fromJson(Map<String, dynamic>.from(summaryJson))
        : null;
    final rawLegacyScore = _asDouble(json['score']);
    final normalizedLegacyScore = rawLegacyScore != null && rawLegacyScore > 1
        ? rawLegacyScore / 100
        : rawLegacyScore;

    return RecommendationItemDto(
      recipeId: (json['recipe_id'] ?? json['id'] ?? dish?.id ?? '').toString(),
      recipeName: (json['recipe_name'] ?? json['name'] ?? dish?.name ?? '')
          .toString(),
      rank: (json['rank'] as num?)?.toInt() ?? 1,
      rankScore: _asDouble(json['rank_score']),
      rankingFeatures: _parseObject(
        json['ranking_features'],
        RecommendationRankingFeaturesDto.fromJson,
      ),
      matchedIngredients: _parseList(
        json['matched_ingredients'],
        RecommendationIngredientDto.fromJson,
      ),
      missingIngredients: _parseList(
        json['missing_ingredients'],
        RecommendationIngredientDto.fromJson,
      ),
      optionalIngredients: _parseList(
        json['optional_ingredients'],
        RecommendationIngredientDto.fromJson,
      ),
      rescuedItems: _stringList(json['rescued_items']),
      statusBadge: (json['status_badge'] ?? '').toString(),
      explanation: (json['explanation'] ?? '').toString(),
      provider: (json['provider'] ?? '').toString(),
      recipeSummary: summary,
      score: normalizedLegacyScore,
      scoreComponents:
          _parseObject(
            json['score_components'] ?? json['breakdown'],
            RecommendationScoreComponentsDto.fromJson,
          ) ??
          const RecommendationScoreComponentsDto(),
      nearExpiryIngredients: _stringList(json['near_expiry_ingredients']),
      dish: dish,
    );
  }
}

/// Legacy E/A/P/U shape retained for old local fixtures only.
@freezed
abstract class RecommendationScoreComponentsDto
    with _$RecommendationScoreComponentsDto {
  const RecommendationScoreComponentsDto._();

  const factory RecommendationScoreComponentsDto({
    @Default(0) double expirationUtilization,
    @Default(0) double availability,
    @Default(0) double preferenceFit,
    @Default(0) double purchaseMinimization,
  }) = _RecommendationScoreComponentsDto;

  factory RecommendationScoreComponentsDto.fromJson(
    Map<String, dynamic> json,
  ) => RecommendationScoreComponentsDto(
    expirationUtilization: _asDoubleDefault(
      json['expiration_utilization'] ?? json['e'],
    ),
    availability: _asDoubleDefault(json['availability'] ?? json['a']),
    preferenceFit: _asDoubleDefault(json['preference_fit'] ?? json['p']),
    purchaseMinimization: _asDoubleDefault(
      json['purchase_minimization'] ?? json['u'],
    ),
  );

  ScoreBreakdown toEntity() => ScoreBreakdown(
    e: expirationUtilization,
    a: availability,
    p: preferenceFit,
    u: purchaseMinimization,
  );
}

@Freezed(toJson: false)
abstract class RecommendationListResponseDto
    with _$RecommendationListResponseDto {
  const RecommendationListResponseDto._();

  const factory RecommendationListResponseDto({
    Object? request,
    @Default('') String contractVersion,
    @Default('') String modelVersion,
    @Default('') String catalogRevision,
    @Default('') String rankerModel,
    @Default(RecommendationTimingsDto()) RecommendationTimingsDto timings,
    @Default(MockRecommendationAnalysisDto())
    MockRecommendationAnalysisDto analysis,
    @Default(<RecommendationItemDto>[]) List<RecommendationItemDto> items,
    @Default(<String>[]) List<String> warnings,
  }) = _RecommendationListResponseDto;

  factory RecommendationListResponseDto.fromJson(Map<String, dynamic> json) =>
      RecommendationListResponseDto(
        request: json['request'],
        contractVersion: (json['contract_version'] ?? '').toString(),
        modelVersion: (json['model_version'] ?? '').toString(),
        catalogRevision: (json['catalog_revision'] ?? '').toString(),
        rankerModel: (json['ranker_model'] ?? '').toString(),
        timings:
            _parseObject(json['timings'], RecommendationTimingsDto.fromJson) ??
            const RecommendationTimingsDto(),
        analysis:
            _parseObject(
              json['analysis'],
              MockRecommendationAnalysisDto.fromJson,
            ) ??
            const MockRecommendationAnalysisDto(),
        items: _parseList(json['items'], RecommendationItemDto.fromJson),
        warnings: _stringList(json['warnings']),
      );
}

T? _parseObject<T>(dynamic value, T Function(Map<String, dynamic>) parser) {
  if (value is! Map) return null;
  return parser(Map<String, dynamic>.from(value));
}

List<T> _parseList<T>(dynamic value, T Function(Map<String, dynamic>) parser) {
  if (value is! List) return <T>[];
  return [
    for (final item in value)
      if (item is Map) parser(Map<String, dynamic>.from(item)),
  ];
}

List<String> _stringList(dynamic value) =>
    value is List ? value.map((item) => item.toString()).toList() : <String>[];
