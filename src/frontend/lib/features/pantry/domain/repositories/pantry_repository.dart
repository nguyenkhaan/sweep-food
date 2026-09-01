import 'package:sweepfood/core/utils/result.dart';
import 'package:sweepfood/features/pantry/domain/entities/pantry_item.dart';
import 'package:sweepfood/features/pantry/domain/entities/pantry_item_draft.dart';
import 'package:sweepfood/features/pantry/domain/entities/pantry_summary.dart';
import 'package:sweepfood/l10n/app_localizations.dart';
import 'package:sweepfood/shared/domain/paginated.dart';
import 'package:sweepfood/shared/domain/storage_tier.dart';

/// How the pantry list is sorted (K-01).
enum PantrySort {
  priority,
  name,
  recent;

  String label(AppL10n l10n) => switch (this) {
    PantrySort.priority => l10n.pantrySortPriority,
    PantrySort.name => l10n.pantrySortName,
    PantrySort.recent => l10n.pantrySortRecent,
  };
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
