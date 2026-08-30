import 'package:frontend/core/utils/result.dart';
import 'package:frontend/features/pantry/domain/entities/pantry_item.dart';
import 'package:frontend/features/pantry/domain/entities/pantry_item_draft.dart';
import 'package:frontend/features/pantry/domain/entities/pantry_summary.dart';
import 'package:frontend/shared/domain/paginated.dart';
import 'package:frontend/shared/domain/storage_tier.dart';

/// How the pantry list is sorted (K-01).
enum PantrySort {
  priority('Cận hạn'),
  name('Tên A–Z'),
  recent('Mới thêm');

  const PantrySort(this.label);
  final String label;
}

abstract interface class PantryRepository {
  Future<Result<Paginated<PantryItem>>> list({
    StorageTier? tier,
    PantryItemStatus status,
    PantrySort sort,
    int page,
  });

  Future<Result<PantrySummary>> summary();

  Future<Result<PantryItem>> add(PantryItemDraft draft);

  Future<Result<List<PantryItem>>> addBatch(List<PantryItemDraft> drafts);

  Future<Result<PantryItem>> update(String id, PantryItemDraft draft);

  Future<Result<void>> delete(String id);

  /// Reduce the quantity by [quantityUsed]; reaching 0 marks it `used`.
  Future<Result<PantryItem>> consume(String id, {required double quantityUsed});
}
