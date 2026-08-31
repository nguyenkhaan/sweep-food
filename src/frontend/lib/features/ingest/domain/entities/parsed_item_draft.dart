import 'package:freezed_annotation/freezed_annotation.dart';
import 'package:frontend/features/pantry/domain/entities/pantry_item.dart';
import 'package:frontend/features/pantry/domain/entities/pantry_item_draft.dart';
import 'package:frontend/shared/domain/measurement_unit.dart';
import 'package:frontend/shared/domain/storage_tier.dart';

part 'parsed_item_draft.freezed.dart';

/// One parsed item draft from OCR label / receipt / voice ingestion before saving.
@freezed
abstract class ParsedItemDraft with _$ParsedItemDraft {
  const ParsedItemDraft._();

  const factory ParsedItemDraft({
    @Default('Cà chua bi') String name,
    @Default('Rau củ') String category,
    @Default(500) double quantity,
    @Default(MeasurementUnit.gram) MeasurementUnit unit,
    @Default(StorageTier.fridge) StorageTier storageTier,
    DateTime? packedDate,
    DateTime? expiryDate,
    int? priceVnd,
    @Default(false) bool isExpiryWarn,
    String? imagePath,
  }) = _ParsedItemDraft;

  PantryItemDraft toPantryItemDraft({PantrySource source = PantrySource.labelScan}) {
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
