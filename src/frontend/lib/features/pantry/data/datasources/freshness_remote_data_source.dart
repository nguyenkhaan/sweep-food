import 'package:sweepfood/core/network/api_client.dart';
import 'package:sweepfood/core/network/api_paths.dart';
import 'package:sweepfood/core/utils/idempotency.dart';
import 'package:sweepfood/features/pantry/data/models/freshness_dto.dart';

class FreshnessRemoteDataSource {
  FreshnessRemoteDataSource(this._api);

  final ApiClient _api;

  Future<FreshnessQuestionsResponseDto> getQuestions(
    String masterIngredientId,
  ) async {
    final json = await _api.get(
      ApiPaths.freshnessQuestions,
      query: {'master_ingredient_id': masterIngredientId},
    );
    return FreshnessQuestionsResponseDto.fromJson(
      json as Map<String, dynamic>,
    );
  }

  Future<FreshnessAssessmentResponseDto> assessBatch(
    String batchId, {
    required Map<String, String> answers,
    String? storageMode,
  }) async {
    final json = await _api.post(
      ApiPaths.freshnessAssessment(batchId),
      body: {
        'answers': answers,
        if (storageMode != null) 'storage_mode': storageMode,
      },
      headers: {'Idempotency-Key': Idempotency.newKey()},
    );
    return FreshnessAssessmentResponseDto.fromJson(
      json as Map<String, dynamic>,
    );
  }
}
