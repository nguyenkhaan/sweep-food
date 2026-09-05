import 'package:freezed_annotation/freezed_annotation.dart';
import 'package:sweepfood/features/dishes/data/models/dish_dto.dart';
import 'package:sweepfood/features/suggestions/domain/entities/score_breakdown.dart';

part 'recommendation_dto.freezed.dart';
part 'recommendation_dto.g.dart';

double? _asDouble(dynamic v) {
  if (v == null) return null;
  if (v is num) return v.toDouble();
  return double.tryParse(v.toString());
}

double _asDoubleDefault(dynamic v) {
  if (v == null) return 0.0;
  if (v is num) return v.toDouble();
  return double.tryParse(v.toString()) ?? 0.0;
}

@freezed
abstract class MockRecommendationAnalysisDto with _$MockRecommendationAnalysisDto {
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
abstract class RecommendationScoreComponentsDto with _$RecommendationScoreComponentsDto {
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
    final e = _asDoubleDefault(json['expiration_utilization'] ?? json['e']);
    final a = _asDoubleDefault(json['availability'] ?? json['a']);
    final p = _asDoubleDefault(json['preference_fit'] ?? json['p']);
    final u = _asDoubleDefault(json['purchase_minimization'] ?? json['u']);
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

@freezed
abstract class RecommendationMissingIngredientDto with _$RecommendationMissingIngredientDto {
  const RecommendationMissingIngredientDto._();

  const factory RecommendationMissingIngredientDto({
    @JsonKey(name: 'master_ingredient_id') String? masterIngredientId,
    required String name,
    @JsonKey(fromJson: _asDoubleDefault) @Default(0.0) double quantity,
    @Default('') String unit,
  }) = _RecommendationMissingIngredientDto;

  factory RecommendationMissingIngredientDto.fromJson(Map<String, dynamic> json) =>
      _$RecommendationMissingIngredientDtoFromJson(json);
}

@freezed
abstract class RecommendationItemDto with _$RecommendationItemDto {
  const RecommendationItemDto._();

  const factory RecommendationItemDto({
    @JsonKey(name: 'recipe_id') required String recipeId,
    @JsonKey(name: 'recipe_name') required String recipeName,
    @Default(1) int rank,
    @JsonKey(fromJson: _asDoubleDefault) @Default(0.0) double score,
    @JsonKey(name: 'score_components')
    @Default(RecommendationScoreComponentsDto())
    RecommendationScoreComponentsDto scoreComponents,
    @JsonKey(name: 'missing_ingredients')
    @Default(<RecommendationMissingIngredientDto>[])
    List<RecommendationMissingIngredientDto> missingIngredients,
    @JsonKey(name: 'near_expiry_ingredients')
    @Default(<String>[])
    List<String> nearExpiryIngredients,
    @Default('') String explanation,
    @Default('') String provider,
    @JsonKey(name: 'model_version') @Default('') String modelVersion,
    // Optional embedded dish for backward compatibility with legacy fixtures/mocks
    DishDto? dish,
  }) = _RecommendationItemDto;

  factory RecommendationItemDto.fromJson(Map<String, dynamic> json) {
    final dishObj = json['dish'] is Map<String, dynamic>
        ? DishDto.fromJson(json['dish'] as Map<String, dynamic>)
        : null;

    final recipeId = (json['recipe_id'] ?? json['id'] ?? dishObj?.id ?? '').toString();
    final recipeName = (json['recipe_name'] ?? json['name'] ?? dishObj?.name ?? '').toString();
    final rank = (json['rank'] as num?)?.toInt() ?? 1;

    final rawScore = _asDouble(json['score']);
    final score = rawScore != null
        ? (rawScore > 1.0 ? rawScore / 100.0 : rawScore)
        : 0.0;

    final scoreComponentsJson =
        (json['score_components'] ?? json['breakdown']) as Map<String, dynamic>?;
    final scoreComponents = scoreComponentsJson != null
        ? RecommendationScoreComponentsDto.fromJson(scoreComponentsJson)
        : const RecommendationScoreComponentsDto();

    final missingList = (json['missing_ingredients'] as List<dynamic>?)
            ?.map((e) => RecommendationMissingIngredientDto.fromJson(
                e as Map<String, dynamic>))
            .toList() ??
        const <RecommendationMissingIngredientDto>[];

    final nearExpiry = (json['near_expiry_ingredients'] as List<dynamic>?)
            ?.map((e) => e.toString())
            .toList() ??
        const <String>[];

    final explanation = (json['explanation'] ?? '').toString();
    final provider = (json['provider'] ?? '').toString();
    final modelVersion = (json['model_version'] ?? '').toString();

    return RecommendationItemDto(
      recipeId: recipeId,
      recipeName: recipeName,
      rank: rank,
      score: score,
      scoreComponents: scoreComponents,
      missingIngredients: missingList,
      nearExpiryIngredients: nearExpiry,
      explanation: explanation,
      provider: provider,
      modelVersion: modelVersion,
      dish: dishObj,
    );
  }
}

@freezed
abstract class RecommendationListResponseDto with _$RecommendationListResponseDto {
  const RecommendationListResponseDto._();

  const factory RecommendationListResponseDto({
    @Default('') String request,
    @Default(MockRecommendationAnalysisDto())
    MockRecommendationAnalysisDto analysis,
    @Default(<RecommendationItemDto>[]) List<RecommendationItemDto> items,
  }) = _RecommendationListResponseDto;

  factory RecommendationListResponseDto.fromJson(Map<String, dynamic> json) {
    final analysisJson = json['analysis'] as Map<String, dynamic>?;
    final itemsList = (json['items'] as List<dynamic>?) ?? const [];

    return RecommendationListResponseDto(
      request: (json['request'] ?? '').toString(),
      analysis: analysisJson != null
          ? MockRecommendationAnalysisDto.fromJson(analysisJson)
          : const MockRecommendationAnalysisDto(),
      items: itemsList
          .map((e) => RecommendationItemDto.fromJson(e as Map<String, dynamic>))
          .toList(),
    );
  }
}
