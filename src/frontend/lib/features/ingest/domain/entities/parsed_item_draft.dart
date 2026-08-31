import 'package:freezed_annotation/freezed_annotation.dart';
import 'package:sweepfood/features/pantry/domain/entities/pantry_item.dart';
import 'package:sweepfood/features/pantry/domain/entities/pantry_item_draft.dart';
import 'package:sweepfood/shared/domain/measurement_unit.dart';
import 'package:sweepfood/shared/domain/storage_tier.dart';

part 'parsed_item_draft.freezed.dart';

/// One item parsed from OCR label / receipt / voice ingestion, shown on the
/// review screens (I-03 / I-05 / I-07) before the user confirms it into the
/// pantry. Defaults are neutral — real values come from the [ScanJob].
@freezed
abstract class ParsedItemDraft with _$ParsedItemDraft {
  const ParsedItemDraft._();

  const factory ParsedItemDraft({
    @Default('') String name,
    @Default('') String category,
    @Default(0) double quantity,
    @Default(MeasurementUnit.gram) MeasurementUnit unit,
    @Default(StorageTier.fridge) StorageTier storageTier,
    DateTime? packedDate,
    DateTime? expiryDate,
    int? priceVnd,

    /// The OCR / ASR filled this field with low confidence — flag it for review.
    @Default(false) bool isExpiryWarn,
    String? imagePath,
  }) = _ParsedItemDraft;

  bool get isValid => name.trim().isNotEmpty && quantity > 0;

  PantryItemDraft toPantryItemDraft({
    PantrySource source = PantrySource.labelScan,
  }) {
    return PantryItemDraft(
      name: name,
      category: category,
      quantity: quantity,
      unit: unit,
      storageTier: storageTier,
      source: source,
      packedDate: packedDate,
      expiryDate: expiryDate,
      priceVnd: priceVnd,
    );
  }
}
