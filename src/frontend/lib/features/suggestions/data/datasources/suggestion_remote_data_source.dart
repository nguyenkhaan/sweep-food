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
    required this.service,
    required this.status,
    required this.provider,
    required this.latencyMs,
  });

  final String service;
  final String status;
  final String provider;
  final double latencyMs;

  bool get isReady => status == 'ready';

  factory AiServiceHealthDto.fromJson(Map<String, dynamic> json) =>
      AiServiceHealthDto(
        service: (json['service'] ?? '').toString(),
        status: (json['status'] ?? '').toString(),
        provider: (json['provider'] ?? '').toString(),
        latencyMs: _readDouble(json['latency_ms']),
      );

  static double _readDouble(Object? value) =>
      value is num ? value.toDouble() : double.tryParse('$value') ?? 0;
}
