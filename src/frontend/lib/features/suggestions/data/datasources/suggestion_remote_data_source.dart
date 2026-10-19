import 'package:sweepfood/core/network/api_client.dart';
import 'package:sweepfood/core/network/api_paths.dart';
import 'package:sweepfood/features/suggestions/data/models/recommendation_dto.dart';
import 'package:sweepfood/features/suggestions/domain/entities/suggestion_request.dart';

/// Talks to `POST /recommendations`. Throws on failure — the repo catches and maps.
class SuggestionRemoteDataSource {
  SuggestionRemoteDataSource(this._api);

  final ApiClient _api;

  Future<RecommendationListResponseDto> fetch(SuggestionRequest request) async {
    final json = await _api.post(
      ApiPaths.recommendations,
      body: request.toBody(),
    );
    final map = json is List
        ? <String, dynamic>{'items': json}
        : Map<String, dynamic>.from(json as Map);
    return RecommendationListResponseDto.fromJson(map);
  }

  Future<AiServiceHealthDto> health() async {
    final json = await _api.get(ApiPaths.aiHealth);
    return AiServiceHealthDto.fromJson(Map<String, dynamic>.from(json as Map));
  }
}

class AiServiceHealthDto {
  const AiServiceHealthDto({
    required this.status,
    required this.catalogRevision,
    required this.recipeCount,
    required this.rankerModel,
    required this.modelVersion,
    required this.ocrConfigured,
    required this.asrConfigured,
    required this.latencyMs,
  });

  final String status;
  final String catalogRevision;
  final int recipeCount;
  final String rankerModel;
  final String modelVersion;
  final bool ocrConfigured;
  final bool asrConfigured;
  final double latencyMs;

  bool get isReady => status == 'ready';

  factory AiServiceHealthDto.fromJson(Map<String, dynamic> json) =>
      AiServiceHealthDto(
        status: (json['status'] ?? '').toString(),
        catalogRevision: (json['catalog_revision'] ?? '').toString(),
        recipeCount: _readInt(json['recipe_count']),
        rankerModel: (json['ranker_model'] ?? '').toString(),
        modelVersion: (json['model_version'] ?? '').toString(),
        ocrConfigured: _readBool(json['ocr_configured']),
        asrConfigured: _readBool(json['asr_configured']),
        latencyMs: _readDouble(json['latency_ms']),
      );

  static int _readInt(Object? value) =>
      value is num ? value.toInt() : int.tryParse('$value') ?? 0;

  static bool _readBool(Object? value) =>
      value is bool ? value : value == 'true' || value == 1;

  static double _readDouble(Object? value) =>
      value is num ? value.toDouble() : double.tryParse('$value') ?? 0;
}
