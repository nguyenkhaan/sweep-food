import 'package:sweepfood/core/error/error_mapper.dart';
import 'package:sweepfood/core/network/api_client.dart';
import 'package:sweepfood/core/network/api_paths.dart';
import 'package:sweepfood/core/utils/idempotency.dart';
import 'package:sweepfood/features/pantry/data/models/freshness_dto.dart';

/// The backend rejected free-text ("Khác") answers as off-topic or too vague
/// (`422 FRESHCHECK_OTHER_ANSWER_NEEDS_CLARIFICATION`). [axisErrors] maps each
/// rubric axis to the message to show under that axis' input box.
class FreshnessClarificationException implements Exception {
  const FreshnessClarificationException(this.axisErrors);

  final Map<String, String> axisErrors;

  static const code = 'FRESHCHECK_OTHER_ANSWER_NEEDS_CLARIFICATION';

  /// Reads the error envelope; `null` when [body] is any other kind of error.
  static FreshnessClarificationException? tryParse(Object? body) {
    if (body is! Map || body['code'] != code) return null;
    final axes = body['axes'];
    if (axes is! List) return null;
    final errors = <String, String>{
      for (final a in axes)
        if (a is Map && a['axis'] is String)
          a['axis'] as String:
              (a['message_vi'] ?? body['detail'] ?? '').toString(),
    };
    return errors.isEmpty ? null : FreshnessClarificationException(errors);
  }

  @override
  String toString() => 'FreshnessClarificationException($axisErrors)';
}

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
    Map<String, String> otherAnswers = const {},
    String? storageMode,
    DateTime? purchasedAt,
  }) async {
    final json = await _guardClarification(
      () => _api.post(
        ApiPaths.freshnessAssessment(batchId),
        body: {
          'answers': answers,
          if (otherAnswers.isNotEmpty) 'other_answers': otherAnswers,
          if (storageMode != null) 'storage_mode': storageMode,
          if (purchasedAt != null)
            'purchased_at': purchasedAt.toUtc().toIso8601String(),
        },
        headers: {'Idempotency-Key': Idempotency.newKey()},
      ),
    );
    return FreshnessAssessmentResponseDto.fromJson(
      json as Map<String, dynamic>,
    );
  }

  /// Estimates an expiry for an item that is not saved yet; writes nothing.
  Future<FreshnessPreviewDto> preview({
    required String masterIngredientId,
    required String storageMode,
    required Map<String, String> answers,
    Map<String, String> otherAnswers = const {},
  }) async {
    final json = await _guardClarification(
      () => _api.post(
        ApiPaths.freshnessPreview,
        body: {
          'master_ingredient_id': masterIngredientId,
          'storage_mode': storageMode,
          'answers': answers,
          if (otherAnswers.isNotEmpty) 'other_answers': otherAnswers,
        },
      ),
    );
    return FreshnessPreviewDto.fromJson(json as Map<String, dynamic>);
  }

  /// Turns the backend's "answer something relevant" 422 into a typed error;
  /// every other failure passes through untouched.
  Future<dynamic> _guardClarification(Future<dynamic> Function() call) async {
    try {
      return await call();
    } on Object catch (e) {
      final clarification = FreshnessClarificationException.tryParse(
        responseBodyOf(e),
      );
      if (clarification == null) rethrow;
      throw clarification;
    }
  }
}
