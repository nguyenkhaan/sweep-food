import 'package:freezed_annotation/freezed_annotation.dart';
import 'package:sweepfood/features/dishes/data/models/dish_dto.dart';
import 'package:sweepfood/features/suggestions/domain/entities/score_breakdown.dart';

part 'recommendation_dto.freezed.dart';
part 'recommendation_dto.g.dart';

double _asDoubleDefault(dynamic v) {
  if (v == null) return 0.0;
  if (v is num) return v.toDouble();
  return double.tryParse(v.toString()) ?? 0.0;
}

Map<String, dynamic> _asStringMap(dynamic value) {
  if (value is Map<String, dynamic>) return value;
  if (value is Map) return Map<String, dynamic>.from(value);
  if (value is String && value.isNotEmpty) return {'query': value};
  return const <String, dynamic>{};
}

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

@freezed
abstract class RecommendationScoreComponentsDto
    with _$RecommendationScoreComponentsDto {
  const RecommendationScoreComponentsDto._();

  const factory RecommendationScoreComponentsDto({
    @JsonKey(name: 'expiration_utilization', fromJson: _asDoubleDefault)
    @Default(0.0)
    double expirationUtilization,
    @JsonKey(fromJson: _asDoubleDefault) @Default(0.0) double availability,
    @JsonKey(name: 'preference_fit', fromJson: _asDoubleDefault)
    @Default(0.0)
    double preferenceFit,
    @JsonKey(name: 'purchase_minimization', fromJson: _asDoubleDefault)
    @Default(0.0)
    double purchaseMinimization,
  }) = _RecommendationScoreComponentsDto;

  factory RecommendationScoreComponentsDto.fromJson(Map<String, dynamic> json) {
    // Supports both legacy E/A/P/U and Backend v2 ranking_features
    final e = _asDoubleDefault(
      json['expiration_utilization'] ??
          json['e'] ??
          (json['rescue_weight_g'] != null
              ? ((json['rescue_weight_g'] as num) > 0 ? 1.0 : 0.0)
              : null),
    );
    final a = _asDoubleDefault(
      json['availability'] ?? json['a'] ?? json['core_coverage'],
    );
    final p = _asDoubleDefault(
      json['preference_fit'] ?? json['p'] ?? json['nutrition_confidence'],
    );
    final u = _asDoubleDefault(
      json['purchase_minimization'] ?? json['u'] ?? json['secondary_coverage'],
    );
    return RecommendationScoreComponentsDto(
      expirationUtilization: e,
      availability: a,
      preferenceFit: p,
      purchaseMinimization: u,
    );
  }

  ScoreBreakdown toEntity() => ScoreBreakdown(
    e: expirationUtilization,
    a: availability,
    p: preferenceFit,
    u: purchaseMinimization,
  );
}

/// The nine features produced by the active SweepFood LightGBM ranker.
///
/// These values deliberately remain separate from the legacy E/A/P/U score:
/// `rank_score` is an unbounded model score, not a percentage.
@freezed
abstract class RecommendationRankingFeaturesDto
    with _$RecommendationRankingFeaturesDto {
  const RecommendationRankingFeaturesDto._();

  const factory RecommendationRankingFeaturesDto({
    @JsonKey(name: 'core_coverage', fromJson: _asDoubleDefault)
    @Default(0.0)
    double coreCoverage,
    @JsonKey(name: 'core_missing_count', fromJson: _asDoubleDefault)
    @Default(0.0)
    double coreMissingCount,
    @JsonKey(name: 'secondary_coverage', fromJson: _asDoubleDefault)
    @Default(0.0)
    double secondaryCoverage,
    @JsonKey(name: 'shopping_gap_items', fromJson: _asDoubleDefault)
    @Default(0.0)
    double shoppingGapItems,
    @JsonKey(name: 'rescue_weight_g', fromJson: _asDoubleDefault)
    @Default(0.0)
    double rescueWeightG,
    @JsonKey(name: 'nutrition_confidence', fromJson: _asDoubleDefault)
    @Default(0.0)
    double nutritionConfidence,
    @JsonKey(name: 'kcal_per_serving', fromJson: _asDoubleDefault)
    @Default(0.0)
    double kcalPerServing,
    @JsonKey(name: 'protein_per_serving', fromJson: _asDoubleDefault)
    @Default(0.0)
    double proteinPerServing,
    @JsonKey(name: 'prep_complexity', fromJson: _asDoubleDefault)
    @Default(0.0)
    double prepComplexity,
  }) = _RecommendationRankingFeaturesDto;

  factory RecommendationRankingFeaturesDto.fromJson(
    Map<String, dynamic> json,
  ) => _$RecommendationRankingFeaturesDtoFromJson(json);

  /// Compatibility projection for screens that still consume E/A/P/U.
  RecommendationScoreComponentsDto toLegacyScore() =>
      RecommendationScoreComponentsDto(
        expirationUtilization: rescueWeightG > 0 ? 1 : 0,
        availability: coreCoverage,
        preferenceFit: nutritionConfidence,
        purchaseMinimization: secondaryCoverage,
      );
}

@freezed
abstract class RecommendationTimingsDto with _$RecommendationTimingsDto {
  const factory RecommendationTimingsDto({
    @JsonKey(name: 'total_ms', fromJson: _asDoubleDefault)
    @Default(0.0)
    double totalMs,
    @JsonKey(name: 'candidate_ms', fromJson: _asDoubleDefault)
    @Default(0.0)
    double candidateMs,
    @JsonKey(name: 'ranker_ms', fromJson: _asDoubleDefault)
    @Default(0.0)
    double rankerMs,
  }) = _RecommendationTimingsDto;

  factory RecommendationTimingsDto.fromJson(Map<String, dynamic> json) =>
      _$RecommendationTimingsDtoFromJson(json);
}

@freezed
abstract class RecommendationMissingIngredientDto
    with _$RecommendationMissingIngredientDto {
  const RecommendationMissingIngredientDto._();

  const factory RecommendationMissingIngredientDto({
    @JsonKey(name: 'master_ingredient_id') String? masterIngredientId,
    required String name,
    @JsonKey(fromJson: _asDoubleDefault) @Default(0.0) double quantity,
    @Default('') String unit,
  }) = _RecommendationMissingIngredientDto;

  factory RecommendationMissingIngredientDto.fromJson(
    Map<String, dynamic> json,
  ) => RecommendationMissingIngredientDto(
    masterIngredientId:
        (json['master_ingredient_id'] ?? json['code']) as String?,
    name: (json['name'] ?? '').toString(),
    quantity: _asDoubleDefault(json['quantity'] ?? json['required_g']),
    unit: (json['unit'] ?? (json['required_g'] != null ? 'g' : '')).toString(),
  );
}

/// One `rescued_details` entry: grams of a near-expiry ingredient a recipe
/// uses up, split FEFO over the user's batches.
class RecommendationRescuedItemDto {
  const RecommendationRescuedItemDto({
    required this.name,
    this.requiredG = 0,
    this.rescuedG = 0,
    this.expiringG = 0,
    this.expiresAt,
  });

  factory RecommendationRescuedItemDto.fromJson(Map<String, dynamic> json) =>
      RecommendationRescuedItemDto(
        name: (json['name'] ?? '').toString(),
        requiredG: _asDoubleDefault(json['required_g']),
        rescuedG: _asDoubleDefault(json['rescued_g']),
        expiringG: _asDoubleDefault(json['expiring_g']),
        expiresAt: DateTime.tryParse((json['expires_at'] ?? '').toString()),
      );

  final String name;
  final double requiredG;
  final double rescuedG;
  final double expiringG;
  final DateTime? expiresAt;
}

@freezed
abstract class RecommendationItemDto with _$RecommendationItemDto {
  const RecommendationItemDto._();

  const factory RecommendationItemDto({
    @JsonKey(name: 'recipe_id') required String recipeId,
    @JsonKey(name: 'recipe_name') required String recipeName,
    @Default(1) int rank,
    @JsonKey(fromJson: _asDoubleDefault) @Default(0.0) double score,
    @JsonKey(name: 'rank_score', fromJson: _asDoubleDefault)
    @Default(0.0)
    double rankScore,
    @JsonKey(name: 'ranking_features')
    @Default(RecommendationRankingFeaturesDto())
    RecommendationRankingFeaturesDto rankingFeatures,
    @JsonKey(name: 'score_components')
    @Default(RecommendationScoreComponentsDto())
    RecommendationScoreComponentsDto scoreComponents,
    @JsonKey(name: 'missing_ingredients')
    @Default(<RecommendationMissingIngredientDto>[])
    List<RecommendationMissingIngredientDto> missingIngredients,
    @JsonKey(name: 'matched_ingredients')
    @Default(<RecommendationMissingIngredientDto>[])
    List<RecommendationMissingIngredientDto> matchedIngredients,
    @JsonKey(name: 'optional_ingredients')
    @Default(<RecommendationMissingIngredientDto>[])
    List<RecommendationMissingIngredientDto> optionalIngredients,
    @JsonKey(name: 'near_expiry_ingredients')
    @Default(<String>[])
    List<String> nearExpiryIngredients,
    @JsonKey(name: 'rescued_details')
    @Default(<RecommendationRescuedItemDto>[])
    List<RecommendationRescuedItemDto> rescuedDetails,
    @Default('') String explanation,
    @Default('') String provider,
    @JsonKey(name: 'status_badge') @Default('') String statusBadge,
    @JsonKey(name: 'model_version') @Default('') String modelVersion,
    // Optional embedded dish for backward compatibility with legacy fixtures/mocks
    DishDto? dish,
  }) = _RecommendationItemDto;

  factory RecommendationItemDto.fromJson(Map<String, dynamic> json) {
    final dishObj = _dishFromRecommendation(json);

    final recipeId = (json['recipe_id'] ?? json['id'] ?? dishObj?.id ?? '')
        .toString();
    final recipeName =
        (json['recipe_name'] ?? json['name'] ?? dishObj?.name ?? '').toString();
    final rank = (json['rank'] as num?)?.toInt() ?? 1;

    final rankScore = _asDoubleDefault(json['rank_score']);

    final scoreComponentsJson =
        (json['ranking_features'] ??
                json['score_components'] ??
                json['breakdown'])
            as Map<String, dynamic>?;
    final scoreComponents = scoreComponentsJson != null
        ? RecommendationScoreComponentsDto.fromJson(scoreComponentsJson)
        : const RecommendationScoreComponentsDto();

    final rankingFeaturesJson =
        json['ranking_features'] as Map<String, dynamic>?;
    final rankingFeatures = rankingFeaturesJson != null
        ? RecommendationRankingFeaturesDto.fromJson(rankingFeaturesJson)
        : const RecommendationRankingFeaturesDto();
    final effectiveScoreComponents = json['ranking_features'] != null
        ? rankingFeatures.toLegacyScore()
        : scoreComponents;

    final legacyScore = _asDoubleDefault(json['score']);
    final score = json['rank_score'] != null
        ? rankingFeatures.coreCoverage
        : (legacyScore > 1 ? legacyScore / 100 : legacyScore);

    final missingList =
        (json['missing_ingredients'] as List<dynamic>?)
            ?.map(
              (e) => RecommendationMissingIngredientDto.fromJson(
                e as Map<String, dynamic>,
              ),
            )
            .toList() ??
        const <RecommendationMissingIngredientDto>[];

    List<RecommendationMissingIngredientDto> ingredients(String key) =>
        (json[key] as List<dynamic>?)
            ?.whereType<Map>()
            .map(
              (e) => RecommendationMissingIngredientDto.fromJson(
                Map<String, dynamic>.from(e),
              ),
            )
            .toList() ??
        const <RecommendationMissingIngredientDto>[];

    final nearExpiry =
        ((json['rescued_items'] ?? json['near_expiry_ingredients'])
                as List<dynamic>?)
            ?.map((e) => e.toString())
            .toList() ??
        const <String>[];

    final rescuedDetails =
        (json['rescued_details'] as List<dynamic>?)
            ?.whereType<Map>()
            .map(
              (e) => RecommendationRescuedItemDto.fromJson(
                Map<String, dynamic>.from(e),
              ),
            )
            .toList() ??
        const <RecommendationRescuedItemDto>[];

    final explanation = (json['explanation'] ?? '').toString();
    final provider = (json['provider'] ?? '').toString();
    final modelVersion = (json['model_version'] ?? '').toString();

    return RecommendationItemDto(
      recipeId: recipeId,
      recipeName: recipeName,
      rank: rank,
      score: score,
      rankScore: rankScore,
      rankingFeatures: rankingFeatures,
      scoreComponents: effectiveScoreComponents,
      missingIngredients: missingList,
      matchedIngredients: ingredients('matched_ingredients'),
      optionalIngredients: ingredients('optional_ingredients'),
      nearExpiryIngredients: nearExpiry,
      rescuedDetails: rescuedDetails,
      explanation: explanation,
      provider: provider,
      statusBadge: (json['status_badge'] ?? '').toString(),
      modelVersion: modelVersion,
      dish: dishObj,
    );
  }
}

@freezed
abstract class RecommendationListResponseDto
    with _$RecommendationListResponseDto {
  const RecommendationListResponseDto._();

  const factory RecommendationListResponseDto({
    @JsonKey(fromJson: _asStringMap)
    @Default(<String, dynamic>{})
    Map<String, dynamic> request,
    @JsonKey(name: 'contract_version') @Default('') String contractVersion,
    @JsonKey(name: 'model_version') @Default('') String modelVersion,
    @JsonKey(name: 'catalog_revision') @Default('') String catalogRevision,
    @JsonKey(name: 'ranker_model') @Default('') String rankerModel,
    @Default(RecommendationTimingsDto()) RecommendationTimingsDto timings,
    @Default(MockRecommendationAnalysisDto())
    MockRecommendationAnalysisDto analysis,
    @Default(<RecommendationItemDto>[]) List<RecommendationItemDto> items,
    @Default(<String>[]) List<String> warnings,
  }) = _RecommendationListResponseDto;

  factory RecommendationListResponseDto.fromJson(Map<String, dynamic> json) {
    final analysisJson = json['analysis'] as Map<String, dynamic>?;
    final itemsList = (json['items'] as List<dynamic>?) ?? const [];

    return RecommendationListResponseDto(
      request: _asStringMap(json['request']),
      contractVersion: (json['contract_version'] ?? '').toString(),
      modelVersion: (json['model_version'] ?? '').toString(),
      catalogRevision: (json['catalog_revision'] ?? '').toString(),
      rankerModel: (json['ranker_model'] ?? '').toString(),
      timings: json['timings'] is Map
          ? RecommendationTimingsDto.fromJson(
              Map<String, dynamic>.from(json['timings'] as Map),
            )
          : const RecommendationTimingsDto(),
      analysis: analysisJson != null
          ? MockRecommendationAnalysisDto.fromJson(analysisJson)
          : const MockRecommendationAnalysisDto(),
      items: itemsList
          .map((e) => RecommendationItemDto.fromJson(e as Map<String, dynamic>))
          .toList(),
      warnings:
          (json['warnings'] as List<dynamic>?)
              ?.map((e) => e.toString())
              .toList() ??
          const <String>[],
    );
  }
}

DishDto? _dishFromRecommendation(Map<String, dynamic> json) {
  if (json['dish'] is Map) {
    return DishDto.fromJson(Map<String, dynamic>.from(json['dish'] as Map));
  }
  final summary = json['recipe_summary'];
  if (summary is! Map) return null;
  final map = Map<String, dynamic>.from(summary);
  final servings = _asDoubleDefault(map['default_servings']);
  final divisor = servings > 0 ? servings : 1.0;
  final nutrition = map['nutrition'] is Map
      ? Map<String, dynamic>.from(map['nutrition'] as Map)
      : const <String, dynamic>{};
  return DishDto(
    id: (map['id'] ?? json['recipe_id'] ?? '').toString(),
    name: (map['name'] ?? json['recipe_name'] ?? '').toString(),
    servings: divisor.round().clamp(1, 1000),
    cookTimeMin: (map['estimated_cooking_minutes'] as num?)?.toInt() ?? 0,
    imageUrl: map['media_url']?.toString(),
    nutritionPerServing: MacrosDto(
      energyKcal: _asDoubleDefault(nutrition['calories']) / divisor,
      proteinG: _asDoubleDefault(nutrition['protein_g']) / divisor,
      carbG: _asDoubleDefault(nutrition['carbs_g']) / divisor,
      lipidG: _asDoubleDefault(nutrition['fat_g']) / divisor,
    ),
  );
}
