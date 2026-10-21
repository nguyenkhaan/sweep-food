import 'package:sweepfood/core/config/app_constants.dart';
import 'package:sweepfood/core/network/api_client.dart';
import 'package:sweepfood/core/network/api_paths.dart';
import 'package:sweepfood/features/ingest/data/models/scan_job_dto.dart';
import 'package:sweepfood/features/ingest/domain/entities/scan_type.dart';

/// Uploads captured media to `/extractions/*` and returns the
/// normalized job. Throws on failure — the repository catches and maps.
class ScanRemoteDataSource {
  ScanRemoteDataSource(this._api);

  final ApiClient _api;

  Future<ScanJobDto> submit(
    ScanType type, {
    String? mediaPath,
    String? transcript,
  }) async {
    final json = await _api.postMultipart(
      type.endpoint,
      fields: {
        if (transcript != null && transcript.isNotEmpty)
          'transcript': transcript,
      },
      files: [
        if (mediaPath != null && mediaPath.isNotEmpty)
          (
            field: 'file',
            path: mediaPath,
            filename: null,
            contentType: type == ScanType.voice ? 'audio/wav' : null,
          ),
      ],
      receiveTimeout: AppConstants.aiUploadReceiveTimeout,
    );
    final payload = json as Map<String, dynamic>;
    if (type == ScanType.voice) {
      final recovered = await _recoverOmittedVoiceItems(payload);
      if (recovered != null) return recovered;
    }
    return ScanJobDto.fromJson(payload, fallbackType: type);
  }

  /// The current ASR envelope is backward-compatible and exposes only the
  /// first parsed item, with `ADDITIONAL_ITEMS_OMITTED` in warnings. Recover
  /// the omitted clauses through the existing text extraction endpoint so the
  /// review screen can still present every spoken ingredient.
  Future<ScanJobDto?> _recoverOmittedVoiceItems(
    Map<String, dynamic> payload,
  ) async {
    final warnings = (payload['warnings'] as List<dynamic>? ?? const [])
        .map((e) => e.toString())
        .toSet();
    final transcript = payload['raw_text']?.toString().trim() ?? '';
    if (!warnings.contains('ADDITIONAL_ITEMS_OMITTED') || transcript.isEmpty) {
      return null;
    }

    final clauses = transcript
        .split(
          RegExp(
            r'\s*(?:,|;|\bvà\b|\bvới\b|\brồi\b|\bkèm\b|\bthêm\b)\s*',
            caseSensitive: false,
          ),
        )
        .map((e) => e.trim())
        .where((e) => e.isNotEmpty)
        .toList();
    if (clauses.length < 2) return null;

    final recovered = <ParsedItemDraftDto>[];
    for (final clause in clauses) {
      try {
        final response = await _api.post(
          ApiPaths.extractionText,
          body: {'text': clause},
        );
        final parsed = ScanJobDto.fromJson(
          response as Map<String, dynamic>,
          fallbackType: ScanType.voice,
        );
        if (parsed.item != null && parsed.item!.name.trim().isNotEmpty) {
          recovered.add(parsed.item!);
        } else {
          recovered.addAll(
            parsed.items.where((item) => item.name.trim().isNotEmpty),
          );
        }
      } on Object {
        // Keep the successful clauses. If none succeed, the caller falls back
        // to the original ASR response instead of failing the whole scan.
      }
    }
    if (recovered.isEmpty) return null;

    return ScanJobDto(
      jobId: payload['request_id']?.toString() ?? 'voice_recovered',
      type: ScanType.voice.wire,
      status: payload['status']?.toString() ?? 'PARTIAL',
      rawText: transcript,
      rawTranscript: transcript,
      fieldCount: recovered.length,
      items: recovered,
    );
  }

  Future<ScanJobDto> lookupBarcode(String barcode) async {
    final json = await _api.post(ApiPaths.extractionBarcode(barcode));
    return ScanJobDto.fromJson(
      json as Map<String, dynamic>,
      fallbackType: ScanType.label,
    );
  }
}
