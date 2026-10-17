import 'package:sweepfood/core/network/api_client.dart';
import 'package:sweepfood/core/network/api_paths.dart';

class RatingRemoteDataSource {
  RatingRemoteDataSource(this._api);

  final ApiClient _api;

  Future<void> submitRating({
    required double rating,
    String? feedback,
  }) async {
    await _api.post(
      '${ApiPaths.rating}?rating=$rating',
      body: (feedback != null && feedback.trim().isNotEmpty)
          ? {'feedback': feedback.trim()}
          : null,
    );
  }
}
