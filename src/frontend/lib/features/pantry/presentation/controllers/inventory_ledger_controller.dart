import 'package:riverpod_annotation/riverpod_annotation.dart';
import 'package:sweepfood/features/pantry/data/repositories/pantry_repository_impl.dart';
import 'package:sweepfood/features/pantry/domain/entities/inventory_ledger.dart';
import 'package:sweepfood/shared/domain/paginated.dart';

part 'inventory_ledger_controller.g.dart';

/// K-04 — the inventory ledger (`GET /inventory/ledger`). Pass `batchId` to
/// scope it to one batch, or `null` for the whole pantry. Supports
/// incremental paging via [loadMore].
@riverpod
class InventoryLedgerController extends _$InventoryLedgerController {
  @override
  Future<Paginated<InventoryLedgerEntry>> build(String? batchId) async {
    final res =
        await ref.watch(pantryRepositoryProvider).ledger(batchId: batchId);
    return res.fold((f) => throw f, (p) => p);
  }

  Future<void> refresh() =>
      ref.refresh(inventoryLedgerControllerProvider(batchId).future);

  Future<void> loadMore() async {
    final current = state.asData?.value;
    if (current == null || !current.hasMore) return;
    final res = await ref
        .read(pantryRepositoryProvider)
        .ledger(batchId: batchId, page: current.nextPage!);
    res.fold(
      (_) {}, // keep what we have on a paging error
      (next) => state = AsyncData(current.append(next)),
    );
  }
}
