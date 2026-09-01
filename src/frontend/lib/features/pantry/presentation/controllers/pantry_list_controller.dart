import 'package:riverpod_annotation/riverpod_annotation.dart';
import 'package:sweepfood/features/pantry/data/repositories/pantry_repository_impl.dart';
import 'package:sweepfood/features/pantry/domain/entities/pantry_item.dart';
import 'package:sweepfood/features/pantry/domain/entities/pantry_item_draft.dart';
import 'package:sweepfood/features/pantry/domain/entities/pantry_summary.dart';
import 'package:sweepfood/features/pantry/domain/repositories/pantry_repository.dart';
import 'package:sweepfood/shared/domain/storage_tier.dart';

part 'pantry_list_controller.g.dart';

/// UI filter state for the Kho list (K-01).
class PantryFilter {
  const PantryFilter({
    this.tier,
    this.sort = PantrySort.priority,
    this.query = '',
  });

  /// `null` = "Tất cả".
  final StorageTier? tier;
  final PantrySort sort;
  final String query;

  PantryFilter withTier(StorageTier? t) =>
      PantryFilter(tier: t, sort: sort, query: query);
  PantryFilter withSort(PantrySort s) =>
      PantryFilter(tier: tier, sort: s, query: query);
  PantryFilter withQuery(String q) =>
      PantryFilter(tier: tier, sort: sort, query: q);
}

@riverpod
class PantryFilterController extends _$PantryFilterController {
  @override
  PantryFilter build() => const PantryFilter();

  void setTier(StorageTier? tier) => state = state.withTier(tier);
  void setSort(PantrySort sort) => state = state.withSort(sort);
  void setQuery(String query) => state = state.withQuery(query);
}

/// Loads the full active pantry list (mock returns everything) and owns the
/// mutations. Filtering/sorting is applied client-side by [pantryListView].
@riverpod
class PantryListController extends _$PantryListController {
  @override
  Future<List<PantryItem>> build() async {
    final res = await ref.watch(pantryRepositoryProvider).list();
    return res.fold((f) => throw f, (page) => page.items);
  }

  PantryRepository get _repo => ref.read(pantryRepositoryProvider);
  List<PantryItem> get _current => state.asData?.value ?? const [];

  Future<PantryItem> add(PantryItemDraft draft) async {
    final res = await _repo.add(draft);
    return res.fold(
      (f) => throw f,
      (item) {
        state = AsyncData([..._current, item]);
        ref.invalidate(pantrySummaryProvider);
        return item;
      },
    );
  }

  Future<PantryItem> updateItem(String id, PantryItemDraft draft) async {
    final res = await _repo.update(id, draft);
    return res.fold(
      (f) => throw f,
      (updated) {
        state = AsyncData([
          for (final i in _current) i.id == id ? updated : i,
        ]);
        ref.invalidate(pantrySummaryProvider);
        return updated;
      },
    );
  }

  Future<void> delete(String id) async {
    final prev = _current;
    state = AsyncData(prev.where((i) => i.id != id).toList()); // optimistic
    final res = await _repo.delete(id);
    res.fold(
      (f) {
        state = AsyncData(prev); // rollback
        throw f;
      },
      (_) => ref.invalidate(pantrySummaryProvider),
    );
  }

  Future<PantryItem> consume(String id, {required double quantityUsed}) async {
    final res = await _repo.consume(id, quantityUsed: quantityUsed);
    return res.fold(
      (f) => throw f,
      (updated) {
        state = AsyncData([
          if (updated.status == PantryItemStatus.active)
            for (final i in _current) i.id == id ? updated : i
          else
            for (final i in _current)
              if (i.id != id) i,
        ]);
        ref.invalidate(pantrySummaryProvider);
        return updated;
      },
    );
  }

  Future<void> refresh() => ref.refresh(pantryListControllerProvider.future);

  /// Insert an already-built item (leftover saved after cooking, D-06).
  void addExisting(PantryItem item) {
    state = AsyncData([..._current, item]);
    ref.invalidate(pantrySummaryProvider);
  }

  /// Splice post-cook quantities into the loaded list and drop depleted batches
  /// (M3 core loop — `CookResult.updatedPantryItems`).
  void applyCookChanges({
    required List<PantryItem> updated,
    List<String> depletedIds = const [],
  }) {
    final byId = {for (final u in updated) u.id: u};
    state = AsyncData([
      for (final i in _current)
        if (!depletedIds.contains(i.id)) byId[i.id] ?? i,
    ]);
    ref.invalidate(pantrySummaryProvider);
  }
}

/// The filtered + sorted list the K-01 screen renders.
@riverpod
List<PantryItem> pantryListView(Ref ref) {
  final items = ref.watch(pantryListControllerProvider).asData?.value ?? const [];
  final f = ref.watch(pantryFilterControllerProvider);

  var out = items.where((i) {
    if (f.tier != null && i.storageTier != f.tier) return false;
    if (f.query.trim().isNotEmpty &&
        !i.name.toLowerCase().contains(f.query.trim().toLowerCase())) {
      return false;
    }
    return true;
  }).toList();

  out.sort(
    switch (f.sort) {
      PantrySort.priority => (a, b) =>
          a.priorityScore.compareTo(b.priorityScore),
      PantrySort.name => (a, b) =>
          a.name.toLowerCase().compareTo(b.name.toLowerCase()),
      PantrySort.recent => (a, b) => b.addedAt.compareTo(a.addedAt),
    },
  );
  return out;
}

/// Per-tier counts for the segmented control chips.
@riverpod
Map<StorageTier?, int> pantryTierCounts(Ref ref) {
  final items = ref.watch(pantryListControllerProvider).asData?.value ?? const [];
  final counts = <StorageTier?, int>{null: items.length};
  for (final tier in StorageTier.values) {
    counts[tier] = items.where((i) => i.storageTier == tier).length;
  }
  return counts;
}

/// `GET /pantry/summary` (Home dashboard; also invalidated after mutations).
@riverpod
Future<PantrySummary> pantrySummary(Ref ref) async {
  final res = await ref.watch(pantryRepositoryProvider).summary();
  return res.fold((f) => throw f, (s) => s);
}
