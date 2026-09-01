import 'package:sweepfood/core/network/api_client.dart';
import 'package:sweepfood/core/network/api_paths.dart';
import 'package:sweepfood/features/suggestions/data/models/dish_suggestion_dto.dart';
import 'package:sweepfood/features/suggestions/domain/entities/suggestion_request.dart';

/// Talks to `/suggestions/dishes`. Throws on failure — the repo catches and maps.
class SuggestionRemoteDataSource {
  SuggestionRemoteDataSource(this._api);

  final ApiClient _api;

  Future<List<DishSuggestionDto>> fetch(SuggestionRequest request) async {
    final json = await _api.post(ApiPaths.suggestions, body: request.toBody());
    final items = (json is Map ? json['items'] : json) as List<dynamic>;
    return items
        .map((e) => DishSuggestionDto.fromJson(e as Map<String, dynamic>))
        .toList();
  }
}
