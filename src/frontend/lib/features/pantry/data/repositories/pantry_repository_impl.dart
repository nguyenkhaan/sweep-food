import 'package:riverpod_annotation/riverpod_annotation.dart';
import 'package:sweepfood/core/network/api_result.dart';
import 'package:sweepfood/core/network/network_providers.dart';
import 'package:sweepfood/core/utils/result.dart';
import 'package:sweepfood/features/pantry/data/datasources/pantry_remote_data_source.dart';
import 'package:sweepfood/features/pantry/domain/entities/pantry_item.dart';
import 'package:sweepfood/features/pantry/domain/entities/pantry_item_draft.dart';
import 'package:sweepfood/features/pantry/domain/entities/pantry_summary.dart';
import 'package:sweepfood/features/pantry/domain/repositories/pantry_repository.dart';
import 'package:sweepfood/shared/domain/paginated.dart';
import 'package:sweepfood/shared/domain/storage_tier.dart';

part 'pantry_repository_impl.g.dart';

@Riverpod(keepAlive: true)
PantryRepository pantryRepository(Ref ref) => PantryRepositoryImpl(
      PantryRemoteDataSource(ref.watch(apiClientProvider)),
    );

/// The backend has no `/inventory/summary`-for-dashboard endpoint (its
/// `GET /inventory/summary` only rolls up by ingredient, not storage tier or
/// waste stats) — [summary] is computed client-side from the active batch
/// list instead. `wasteReductionCount`/`wasteAvoidedKg` have no backend
/// equivalent and are left at zero/null rather than fabricated.
class PantryRepositoryImpl implements PantryRepository {
  PantryRepositoryImpl(this._remote);

  final PantryRemoteDataSource _remote;

  @override
  Future<Result<Paginated<PantryItem>>> list({
    StorageTier? tier,
    PantryItemStatus status = PantryItemStatus.active,
    PantrySort sort = PantrySort.priority,
    int page = 1,
  }) =>
      runGuarded(() async {
        final dtos = await _remote.list(
          tier: tier,
          status: status,
          sort: sort,
          page: page,
        );
        return Paginated.single([for (final d in dtos) d.toEntity()]);
      });

  @override
  Future<Result<PantrySummary>> summary() => runGuarded(() async {
        final dtos = await _remote.list(
          status: PantryItemStatus.active,
          sort: PantrySort.priority,
          page: 1,
        );
        final items = [for (final d in dtos) d.toEntity()];
        final countByTier = <StorageTier, int>{};
        for (final item in items) {
          countByTier[item.storageTier] = (countByTier[item.storageTier] ?? 0) + 1;
        }
        final nearExpiry = items.where((i) => i.isNearExpiry()).toList()
          ..sort((a, b) => (a.daysUntilExpiry ?? 0).compareTo(b.daysUntilExpiry ?? 0));
        return PantrySummary(
          totalCount: items.length,
          countByTier: countByTier,
          nearExpiry: nearExpiry,
          wasteReductionCount: 0,
          wasteAvoidedKg: null,
        );
      });

  @override
  Future<Result<PantryItem>> add(PantryItemDraft draft) =>
      runGuarded(() async => (await _remote.add(draft)).toEntity());

  @override
  Future<Result<List<PantryItem>>> addBatch(List<PantryItemDraft> drafts) =>
      runGuarded(() async {
        final dtos = await _remote.addBatch(drafts);
        return [for (final d in dtos) d.toEntity()];
      });

  @override
  Future<Result<PantryItem>> update(String id, PantryItemDraft draft) =>
      runGuarded(() async => (await _remote.update(id, draft)).toEntity());

  @override
  Future<Result<void>> delete(String id) => guardVoid(() => _remote.delete(id));

  @override
  Future<Result<PantryItem>> consume(String id, {required double quantityUsed}) =>
      runGuarded(() async => (await _remote.consume(id, quantityUsed)).toEntity());
}
