import 'package:sweepfood/core/network/api_client.dart';
import 'package:sweepfood/core/network/api_paths.dart';
import 'package:sweepfood/features/suggestions/data/models/recommendation_dto.dart';
import 'package:sweepfood/features/suggestions/domain/entities/suggestion_request.dart';

/// Talks to `POST /recommendations`. Throws on failure — the repo catches and maps.
class SuggestionRemoteDataSource {
  SuggestionRemoteDataSource(this._api);

  final ApiClient _api;

  Future<RecommendationListResponseDto> fetch(SuggestionRequest request) async {
    final json = await _api.post(ApiPaths.recommendations, body: request.toBody());
    final map = json is List
        ? <String, dynamic>{'items': json}
        : Map<String, dynamic>.from(json as Map);
    return RecommendationListResponseDto.fromJson(map);
  }
}
