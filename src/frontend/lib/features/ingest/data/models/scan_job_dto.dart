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

/// Wire shape of a completed extraction job returned by `/extractions/*`
/// or legacy `/scan/{label,receipt,voice}`.
@Freezed(fromJson: false, toJson: false)
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

  /// Custom factory to parse both backend ExtractionResponse/InvoiceExtractionResponse/BarcodeExtractionResponse
  /// and legacy ScanJobDto formats.
  factory ScanJobDto.fromJson(
    Map<String, dynamic> json, {
    ScanType? fallbackType,
  }) {
    // Check if this is a backend ExtractionResponse envelope:
    // It has `request_id`, `status`, `provider`, `fields`.
    if (json.containsKey('request_id') && json.containsKey('fields')) {
      final reqId = json['request_id']?.toString() ?? 'job_unknown';
      final statusStr = json['status']?.toString() ?? 'SUCCEEDED';
      final rawText = json['raw_text']?.toString();
      final fields = json['fields'] as Map<String, dynamic>? ?? {};
      final confidence = json['confidence'] as Map<String, dynamic>? ?? {};

      // 1. Invoice Extraction
      if (fields.containsKey('line_items')) {
        final lineItemsRaw = fields['line_items'] as List<dynamic>? ?? [];
        final parsedItems = <ParsedItemDraftDto>[];
        for (final li in lineItemsRaw) {
          if (li is Map<String, dynamic>) {
            final name = li['name']?.toString() ?? '';
            final qty = (li['quantity'] as num?)?.toDouble() ?? 1.0;
            final unitStr = li['unit']?.toString() ?? 'g';
            final unitPrice = (li['unit_price'] as num?)?.round();
            final totalPrice = (li['total_price'] as num?)?.round();
            parsedItems.add(
              ParsedItemDraftDto(
                name: name,
                quantity: qty,
                unit: unitStr,
                priceVnd: unitPrice ?? totalPrice,
              ),
            );
          }
        }
        final storeName = fields['vendor_name']?.toString();
        final purchaseDate =
            DateTime.tryParse(fields['invoice_date']?.toString() ?? '');

        return ScanJobDto(
          jobId: reqId,
          type: ScanType.receipt.wire,
          status: statusStr,
          rawText: rawText,
          storeName: storeName,
          purchaseDate: purchaseDate,
          fieldCount: parsedItems.length,
          items: parsedItems,
        );
      }

      // 2. Barcode Extraction
      if (fields.containsKey('product_name') || fields.containsKey('brand')) {
        final name = fields['ingredient_name']?.toString() ??
            fields['product_name']?.toString() ??
            '';
        final category = fields['category']?.toString() ?? '';
        final qty = (fields['quantity'] as num?)?.toDouble() ?? 1.0;
        final unitStr = fields['unit']?.toString() ?? 'g';
        final expiresAt =
            DateTime.tryParse(fields['expires_at']?.toString() ?? '');
        final price = (fields['price'] as num?)?.round();

        final item = ParsedItemDraftDto(
          name: name,
          category: category,
          quantity: qty,
          unit: unitStr,
          expiryDate: expiresAt,
          priceVnd: price,
        );

        return ScanJobDto(
          jobId: reqId,
          type: (fallbackType ?? ScanType.label).wire,
          status: statusStr,
          rawText: rawText,
          fieldCount: 5,
          item: item,
          items: const [],
        );
      }

      // 3. Label OCR or ASR Extraction
      final name = fields['ingredient_name']?.toString() ?? '';
      final qty = (fields['quantity'] as num?)?.toDouble() ?? 1.0;
      final unitStr = fields['unit']?.toString() ?? 'g';
      final packedAt =
          DateTime.tryParse(fields['packaged_at']?.toString() ?? '');
      final expiresAt =
          DateTime.tryParse(fields['expires_at']?.toString() ?? '');
      final price = (fields['price'] as num?)?.round();

      // Confidence warning: e.g. expires_at confidence < 0.8
      final expiryConf = (confidence['expires_at'] as num?)?.toDouble();
      final isExpiryWarn = expiryConf != null && expiryConf < 0.8;

      final item = ParsedItemDraftDto(
        name: name,
        quantity: qty,
        unit: unitStr,
        packedDate: packedAt,
        expiryDate: expiresAt,
        priceVnd: price,
        isExpiryWarn: isExpiryWarn,
      );

      final determinedType = fallbackType?.wire ??
          (json['provider']?.toString().toUpperCase().contains('ASR') == true
              ? ScanType.voice.wire
              : ScanType.label.wire);

      return ScanJobDto(
        jobId: reqId,
        type: determinedType,
        status: statusStr,
        rawText: rawText,
        rawTranscript: rawText,
        fieldCount: 5,
        item: item,
        items: const [],
      );
    }

    // Otherwise parse legacy ScanJobDto format
    final itemsList = <ParsedItemDraftDto>[];
    if (json['items'] is List) {
      for (final itemJson in json['items'] as List) {
        if (itemJson is Map<String, dynamic>) {
          itemsList.add(ParsedItemDraftDto.fromJson(itemJson));
        }
      }
    }

    ParsedItemDraftDto? singleItem;
    if (json['item'] is Map<String, dynamic>) {
      singleItem = ParsedItemDraftDto.fromJson(json['item'] as Map<String, dynamic>);
    }

    return ScanJobDto(
      jobId: json['job_id']?.toString() ?? '',
      type: json['type']?.toString() ?? (fallbackType?.wire ?? ScanType.label.wire),
      status: json['status']?.toString() ?? 'completed',
      rawText: json['raw_text']?.toString(),
      rawTranscript: json['raw_transcript']?.toString(),
      storeName: json['store_name']?.toString(),
      purchaseDate: json['purchase_date'] == null
          ? null
          : DateTime.tryParse(json['purchase_date'].toString()),
      fieldCount: (json['field_count'] as num?)?.toInt(),
      item: singleItem,
      items: itemsList,
    );
  }

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
