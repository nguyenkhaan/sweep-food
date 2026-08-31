import 'package:freezed_annotation/freezed_annotation.dart';
import 'package:sweepfood/features/ingest/domain/entities/parsed_item_draft.dart';
import 'package:sweepfood/features/ingest/domain/entities/scan_job.dart';
import 'package:sweepfood/features/ingest/domain/entities/scan_type.dart';
import 'package:sweepfood/shared/domain/measurement_unit.dart';
import 'package:sweepfood/shared/domain/storage_tier.dart';

part 'scan_job_dto.freezed.dart';
part 'scan_job_dto.g.dart';

/// Wire shape of one extracted item (label field set / receipt line / spoken
/// phrase). Tolerant of missing fields — OCR / ASR output is unreliable.
@freezed
abstract class ParsedItemDraftDto with _$ParsedItemDraftDto {
  const ParsedItemDraftDto._();

  const factory ParsedItemDraftDto({
    @Default('') String name,
    @Default('') String category,
    @Default(0) double quantity,
    @Default('g') String unit,
    @JsonKey(name: 'storage_tier') @Default('fridge') String storageTier,
    @JsonKey(name: 'packed_date') DateTime? packedDate,
    @JsonKey(name: 'expiry_date') DateTime? expiryDate,
    @JsonKey(name: 'price_vnd') int? priceVnd,
    @JsonKey(name: 'is_expiry_warn') @Default(false) bool isExpiryWarn,
  }) = _ParsedItemDraftDto;

  factory ParsedItemDraftDto.fromJson(Map<String, dynamic> json) =>
      _$ParsedItemDraftDtoFromJson(json);

  ParsedItemDraft toDraft() => ParsedItemDraft(
        name: name,
        category: category,
        quantity: quantity,
        unit: MeasurementUnit.fromWire(unit),
        storageTier: StorageTier.fromWire(storageTier),
        packedDate: packedDate,
        expiryDate: expiryDate,
        priceVnd: priceVnd,
        isExpiryWarn: isExpiryWarn,
      );
}

/// Wire shape of a completed extraction job returned by `/scan/{label,receipt,voice}`.
@freezed
abstract class ScanJobDto with _$ScanJobDto {
  const ScanJobDto._();

  const factory ScanJobDto({
    @JsonKey(name: 'job_id') required String jobId,
    required String type,
    @Default('completed') String status,
    @JsonKey(name: 'raw_text') String? rawText,
    @JsonKey(name: 'raw_transcript') String? rawTranscript,
    @JsonKey(name: 'store_name') String? storeName,
    @JsonKey(name: 'purchase_date') DateTime? purchaseDate,
    @JsonKey(name: 'field_count') int? fieldCount,

    /// Label jobs return a single [item]; receipt / voice return [items].
    ParsedItemDraftDto? item,
    @Default(<ParsedItemDraftDto>[]) List<ParsedItemDraftDto> items,
  }) = _ScanJobDto;

  factory ScanJobDto.fromJson(Map<String, dynamic> json) =>
      _$ScanJobDtoFromJson(json);

  ScanJob toEntity() {
    final drafts = <ParsedItemDraftDto>[
      if (item != null) item!,
      ...items,
    ].map((d) => d.toDraft()).toList();
    return ScanJob(
      id: jobId,
      type: ScanType.fromWire(type),
      status: ScanStatus.fromWire(status),
      items: drafts,
      rawText: rawText ?? rawTranscript,
      storeName: storeName,
      purchaseDate: purchaseDate,
      fieldCount: fieldCount,
    );
  }
}
