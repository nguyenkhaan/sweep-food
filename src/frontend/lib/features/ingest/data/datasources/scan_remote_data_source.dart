import 'package:sweepfood/core/network/api_client.dart';
import 'package:sweepfood/features/ingest/data/models/scan_job_dto.dart';
import 'package:sweepfood/features/ingest/domain/entities/scan_type.dart';

/// Uploads captured media to `/scan/{label,receipt,voice}` and returns the
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
        if (transcript != null && transcript.isNotEmpty) 'transcript': transcript,
      },
      files: [
        if (mediaPath != null && mediaPath.isNotEmpty)
          (field: 'file', path: mediaPath, filename: null),
      ],
    );
    return ScanJobDto.fromJson(json as Map<String, dynamic>);
  }
}
