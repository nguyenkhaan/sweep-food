import 'package:riverpod_annotation/riverpod_annotation.dart';
import 'package:sweepfood/core/network/api_result.dart';
import 'package:sweepfood/core/network/network_providers.dart';
import 'package:sweepfood/core/utils/result.dart';
import 'package:sweepfood/features/dishes/data/datasources/dish_remote_data_source.dart';
import 'package:sweepfood/features/dishes/domain/entities/dish.dart';
import 'package:sweepfood/features/suggestions/data/datasources/suggestion_remote_data_source.dart';
import 'package:sweepfood/features/suggestions/domain/entities/dish_suggestion.dart';
import 'package:sweepfood/features/suggestions/domain/entities/suggestion_request.dart';
import 'package:sweepfood/features/suggestions/domain/repositories/suggestion_repository.dart';
import 'package:sweepfood/shared/domain/nutrition_info.dart';

part 'suggestion_repository_impl.g.dart';

@Riverpod(keepAlive: true)
SuggestionRepository suggestionRepository(Ref ref) {
  final api = ref.watch(apiClientProvider);
  return SuggestionRepositoryImpl(
    SuggestionRemoteDataSource(api),
    dishRemote: DishRemoteDataSource(api),
  );
}

class SuggestionRepositoryImpl implements SuggestionRepository {
  SuggestionRepositoryImpl(this._remote, {DishRemoteDataSource? dishRemote})
    : _dishRemote = dishRemote;

  final SuggestionRemoteDataSource _remote;
  final DishRemoteDataSource? _dishRemote;

  @override
  Future<Result<List<DishSuggestion>>> fetch(SuggestionRequest request) =>
      runGuarded(() async {
        final response = await _remote.fetch(request);
        final isMock = response.analysis.isMock;

        final futures = response.items.map((item) async {
          Dish dish;
          if (item.dish != null) {
            dish = item.dish!.toEntity();
          } else if (_dishRemote != null && item.recipeId.isNotEmpty) {
            try {
              final recipeDto = await _dishRemote.getById(item.recipeId);
              dish = recipeDto.toEntity();
            } catch (_) {
              dish = Dish(
                id: item.recipeId,
                name: item.recipeName,
                servings: 1,
                prepTimeMin: 0,
                cookTimeMin: 0,
                nutritionPerServing: const NutritionInfo.zero(),
                cuisine: '',
                difficulty: '',
                ingredients: const [],
                steps: const [],
              );
            }
          } else {
            dish = Dish(
              id: item.recipeId,
              name: item.recipeName,
              servings: 1,
              prepTimeMin: 0,
              cookTimeMin: 0,
              nutritionPerServing: const NutritionInfo.zero(),
              cuisine: '',
              difficulty: '',
              ingredients: const [],
              steps: const [],
            );
          }

          final breakdown = item.scoreComponents.toEntity();
          final int scoreOut = (item.score * 100).round();
          final features = RecommendationRankingFeatures(
            coreCoverage: item.rankingFeatures.coreCoverage,
            coreMissingCount: item.rankingFeatures.coreMissingCount,
            secondaryCoverage: item.rankingFeatures.secondaryCoverage,
            shoppingGapItems: item.rankingFeatures.shoppingGapItems,
            rescueWeightG: item.rankingFeatures.rescueWeightG,
            nutritionConfidence: item.rankingFeatures.nutritionConfidence,
            kcalPerServing: item.rankingFeatures.kcalPerServing,
            proteinPerServing: item.rankingFeatures.proteinPerServing,
            prepComplexity: item.rankingFeatures.prepComplexity,
          );
          return DishSuggestion(
            dish: dish,
            breakdown: breakdown,
            rank: item.rank,
            rankScore: item.rankScore,
            rankingFeatures: features,
            matchedIngredients: item.matchedIngredients
                .map(
                  (value) => RecommendationIngredient(
                    name: value.name,
                    code: value.masterIngredientId,
                    requiredG: value.quantity,
                  ),
                )
                .toList(),
            missingIngredients: item.missingIngredients
                .map(
                  (value) => RecommendationIngredient(
                    name: value.name,
                    code: value.masterIngredientId,
                    requiredG: value.quantity,
                  ),
                )
                .toList(),
            optionalIngredients: item.optionalIngredients
                .map(
                  (value) => RecommendationIngredient(
                    name: value.name,
                    code: value.masterIngredientId,
                    requiredG: value.quantity,
                  ),
                )
                .toList(),
            statusBadge: item.statusBadge,
            provider: item.provider,
            modelVersion: response.modelVersion.isNotEmpty
                ? response.modelVersion
                : item.modelVersion,
            rankerModel: response.rankerModel,
            totalLatencyMs: response.timings.totalMs,
            nearExpiryIngredients: item.nearExpiryIngredients,
            availabilityRatio: response.contractVersion == '2'
                ? item.rankingFeatures.coreCoverage
                : item.scoreComponents.availability,
            toBuyCount: item.missingIngredients.length,
            scoreOverride: scoreOut > 0 ? scoreOut : breakdown.scoreOutOf100,
            explanation: item.explanation.isNotEmpty ? item.explanation : null,
            isMock: isMock,
          );
        });

        return Future.wait(futures);
      });
}
