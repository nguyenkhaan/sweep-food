import 'package:riverpod_annotation/riverpod_annotation.dart';
import 'package:sweepfood/features/ingest/domain/entities/parsed_item_draft.dart';
import 'package:sweepfood/features/ingest/domain/entities/scan_job.dart';
import 'package:sweepfood/features/pantry/domain/entities/freshness_estimate.dart';
import 'package:sweepfood/features/pantry/domain/entities/pantry_item.dart';
import 'package:sweepfood/features/pantry/presentation/controllers/pantry_list_controller.dart';
import 'package:sweepfood/shared/domain/measurement_unit.dart';
import 'package:sweepfood/shared/domain/storage_tier.dart';

part 'label_review_controller.g.dart';

/// Holds the single editable draft on the Label Review screen (I-03), seeded
/// from the OCR [ScanJob].
@riverpod
class LabelReviewController extends _$LabelReviewController {
  @override
  ParsedItemDraft build(ScanJob job) =>
      job.single.copyWith(imagePath: job.sourcePath);

  /// Renaming detaches the item from its catalog match, its FreshCheck estimate
  /// and the food group the smart parser derived from that match.
  void setName(String name) => state = name == state.name
      ? state
      : state.copyWith(
          name: name,
          ingredientId: null,
          freshness: null,
          category: '',
        );

  void setQuantity(double quantity) =>
      state = state.copyWith(quantity: quantity);

  void setUnit(MeasurementUnit unit) => state = state.copyWith(unit: unit);

  void setPrice(int? price) => state = state.copyWith(priceVnd: price);

  void setPackedDate(DateTime? date) =>
      state = state.copyWith(packedDate: date);

  /// A manual date and a FreshCheck estimate are mutually exclusive.
  void setExpiry(DateTime? date, FreshnessEstimate? freshness) => state =
      state.copyWith(expiryDate: date, freshness: freshness, isExpiryWarn: false);

  /// FreshCheck depends on where the item is stored.
  void setStorageTier(StorageTier tier) => state = state.copyWith(
    storageTier: tier,
    freshness: tier == state.storageTier ? state.freshness : null,
  );

  /// Confirms the reviewed draft into the pantry.
  Future<PantryItem> saveToPantry() {
    final draft = state.toPantryItemDraft(source: PantrySource.labelScan);
    return ref.read(pantryListControllerProvider.notifier).add(draft);
  }
}
