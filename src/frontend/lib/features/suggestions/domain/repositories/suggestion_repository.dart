import 'package:sweepfood/core/utils/result.dart';
import 'package:sweepfood/features/suggestions/domain/entities/dish_suggestion.dart';
import 'package:sweepfood/features/suggestions/domain/entities/suggestion_request.dart';

abstract interface class SuggestionRepository {
  /// AI-ranked dishes for the current pantry (`POST /recommendations`).
  Future<Result<List<DishSuggestion>>> fetch(SuggestionRequest request);
}
