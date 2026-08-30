import 'package:frontend/core/utils/result.dart';
import 'package:frontend/features/suggestions/domain/entities/dish_suggestion.dart';
import 'package:frontend/features/suggestions/domain/entities/suggestion_request.dart';

abstract interface class SuggestionRepository {
  /// The 3–5 top-ranked dishes for the current pantry (`POST /suggestions/dishes`).
  Future<Result<List<DishSuggestion>>> fetch(SuggestionRequest request);
}
