import 'package:sweepfood/core/utils/result.dart';
import 'package:sweepfood/features/ingest/domain/entities/scan_job.dart';

/// Contract for the multimodal ingestion channels (M4).
///
/// Implementations upload the captured media, wait for the extraction result,
/// and return a normalized [ScanJob]. They never persist inventory — saving the
/// reviewed drafts is the pantry repository's job.
abstract interface class ScanRepository {
  /// OCR a single product label (I-01 → I-03).
  Future<Result<ScanJob>> scanLabel(String imagePath);

  /// OCR a purchase receipt into a line-item list (I-04 → I-05).
  Future<Result<ScanJob>> scanReceipt(String imagePath);

  /// Transcribe a spoken ingredient list (I-06 → I-07). Either an [audioPath]
  /// or a already-recognized [transcript] may be supplied.
  Future<Result<ScanJob>> scanVoice({String? audioPath, String? transcript});
}
