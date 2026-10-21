import 'package:riverpod_annotation/riverpod_annotation.dart';
import 'package:sweepfood/core/network/api_result.dart';
import 'package:sweepfood/core/network/network_providers.dart';
import 'package:sweepfood/core/utils/result.dart';
import 'package:sweepfood/features/pantry/data/datasources/freshness_remote_data_source.dart';
import 'package:sweepfood/features/pantry/data/datasources/pantry_remote_data_source.dart';
import 'package:sweepfood/features/pantry/data/models/pantry_item_dto.dart';
import 'package:sweepfood/features/pantry/domain/entities/inventory_ledger.dart';
import 'package:sweepfood/features/pantry/domain/entities/pantry_item.dart';
import 'package:sweepfood/features/pantry/domain/entities/pantry_item_draft.dart';
import 'package:sweepfood/features/pantry/domain/entities/pantry_summary.dart';
import 'package:sweepfood/features/pantry/domain/repositories/pantry_repository.dart';
import 'package:sweepfood/shared/domain/paginated.dart';
import 'package:sweepfood/shared/domain/storage_tier.dart';

part 'pantry_repository_impl.g.dart';

@Riverpod(keepAlive: true)
PantryRepository pantryRepository(Ref ref) {
  final api = ref.watch(apiClientProvider);
  return PantryRepositoryImpl(
    PantryRemoteDataSource(api),
    FreshnessRemoteDataSource(api),
  );
}

/// The backend has no `/inventory/summary`-for-dashboard endpoint (its
/// `GET /inventory/summary` only rolls up by ingredient, not storage tier or
/// waste stats) — [summary] is computed client-side from the active batch
/// list instead. `wasteReductionCount`/`wasteAvoidedKg` have no backend
/// equivalent and are left at zero/null rather than fabricated.
class PantryRepositoryImpl implements PantryRepository {
  PantryRepositoryImpl(this._remote, this._freshness);

  final PantryRemoteDataSource _remote;
  final FreshnessRemoteDataSource _freshness;

  /// Creates the batch, then — when the user accepted a FreshCheck estimate in
  /// place of a printed date — records it through the batch assessment. The
  /// item is already saved at that point, so an assessment failure keeps the
  /// saved batch (without an expiry) instead of failing the whole add.
  Future<PantryItemDto> _addWithFreshness(PantryItemDraft draft) async {
    final saved = await _remote.add(draft);
    final estimate = draft.freshness;
    if (estimate == null || draft.expiryDate != null) return saved;
    try {
      final assessed = await _freshness.assessBatch(
        saved.id,
        answers: estimate.answers,
        otherAnswers: estimate.otherAnswers,
        purchasedAt: DateTime.now(),
      );
      final expiresAt = assessed.expiresAt;
      return expiresAt == null ? saved : saved.copyWith(expiresAt: expiresAt);
    } on Object {
      return saved;
    }
  }

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
      runGuarded(() async => (await _addWithFreshness(draft)).toEntity());

  @override
  Future<Result<List<PantryItem>>> addBatch(List<PantryItemDraft> drafts) =>
      runGuarded(() async {
        final saved = <PantryItemDto>[];
        for (final draft in drafts) {
          saved.add(await _addWithFreshness(draft));
        }
        return [for (final d in saved) d.toEntity()];
      });

  @override
  Future<Result<PantryItem>> update(String id, PantryItemDraft draft) =>
      runGuarded(() async => (await _remote.update(id, draft)).toEntity());

  @override
  Future<Result<void>> delete(String id) => guardVoid(() => _remote.delete(id));

  @override
  Future<Result<PantryItem>> consume(String id, {required double quantityUsed}) =>
      runGuarded(() async => (await _remote.consume(id, quantityUsed)).toEntity());

  @override
  Future<Result<Paginated<InventoryLedgerEntry>>> ledger({
    String? batchId,
    LedgerEventType? eventType,
    int page = 1,
  }) =>
      runGuarded(() async {
        final dto = await _remote.ledger(
          batchId: batchId,
          eventType: eventType,
          page: page,
        );
        final loaded = page * dto.perPage;
        return Paginated(
          items: [for (final e in dto.items) e.toEntity()],
          page: dto.page,
          total: dto.total,
          nextPage: loaded < dto.total ? dto.page + 1 : null,
        );
      });
}
