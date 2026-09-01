import 'package:riverpod_annotation/riverpod_annotation.dart';
import 'package:sweepfood/features/ingest/domain/entities/parsed_item_draft.dart';
import 'package:sweepfood/features/ingest/domain/entities/scan_job.dart';
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

  void setName(String name) => state = state.copyWith(name: name);

  void setQuantity(double quantity) =>
      state = state.copyWith(quantity: quantity);

  void setUnit(MeasurementUnit unit) => state = state.copyWith(unit: unit);

  void setPrice(int? price) => state = state.copyWith(priceVnd: price);

  void setPackedDate(DateTime? date) =>
      state = state.copyWith(packedDate: date);

  void setExpiryDate(DateTime? date) =>
      state = state.copyWith(expiryDate: date, isExpiryWarn: false);

  void setStorageTier(StorageTier tier) =>
      state = state.copyWith(storageTier: tier);

  void setCategory(String category) =>
      state = state.copyWith(category: category);

  /// Confirms the reviewed draft into the pantry.
  Future<PantryItem> saveToPantry() {
    final draft = state.toPantryItemDraft(source: PantrySource.labelScan);
    return ref.read(pantryListControllerProvider.notifier).add(draft);
  }
}
