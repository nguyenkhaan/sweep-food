import 'package:freezed_annotation/freezed_annotation.dart';
import 'package:sweepfood/features/ingest/domain/entities/parsed_item_draft.dart';
import 'package:sweepfood/features/ingest/domain/entities/scan_type.dart';

part 'scan_job.freezed.dart';

/// The normalized result of one OCR label / receipt / voice extraction (M4).
///
/// The extraction endpoints never write inventory — a job only carries the
/// parsed drafts the review screens (I-03 / I-05 / I-07) let the user confirm.
@freezed
abstract class ScanJob with _$ScanJob {
  const ScanJob._();

  const factory ScanJob({
    required String id,
    required ScanType type,
    @Default(ScanStatus.completed) ScanStatus status,

    /// Extracted drafts. Label jobs carry exactly one; receipt / voice carry many.
    @Default(<ParsedItemDraft>[]) List<ParsedItemDraft> items,

    /// OCR raw text (label / receipt) or ASR transcript (voice), for display.
    String? rawText,

    /// Receipt only.
    String? storeName,
    DateTime? purchaseDate,

    /// How many label fields the OCR filled (I-03 banner).
    int? fieldCount,

    /// Local path of the captured photo / audio, kept for the review thumbnail.
    /// Filled client-side by the repository, never by the server.
    String? sourcePath,
  }) = _ScanJob;

  bool get isFailed => status == ScanStatus.failed;

  bool get hasItems => items.isNotEmpty;

  /// The single draft for a label job (or a sane empty default).
  ParsedItemDraft get single =>
      items.isNotEmpty ? items.first : const ParsedItemDraft();
}
