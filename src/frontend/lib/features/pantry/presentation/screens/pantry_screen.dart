import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:frontend/app/router/routes.dart';
import 'package:frontend/app/theme/app_spacing.dart';
import 'package:frontend/core/config/app_config_provider.dart';
import 'package:frontend/core/utils/extensions/build_context_x.dart';
import 'package:frontend/core/widgets/app_search_field.dart';
import 'package:frontend/core/widgets/async_value_widget.dart';
import 'package:frontend/core/widgets/empty_state.dart';
import 'package:frontend/core/widgets/section_header.dart';
import 'package:frontend/features/ingest/presentation/screens/add_entry_chooser_sheet.dart';
import 'package:frontend/features/pantry/domain/entities/pantry_item.dart';
import 'package:frontend/features/pantry/domain/repositories/pantry_repository.dart';
import 'package:frontend/features/pantry/presentation/controllers/pantry_list_controller.dart';
import 'package:frontend/features/pantry/presentation/widgets/pantry_item_tile.dart';
import 'package:frontend/features/pantry/presentation/widgets/tier_segmented_control.dart';
import 'package:go_router/go_router.dart';

/// K-01 — Kho thực phẩm.
class PantryScreen extends ConsumerWidget {
  const PantryScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final l10n = context.l10n;
    final listAsync = ref.watch(pantryListControllerProvider);
    final filter = ref.watch(pantryFilterControllerProvider);
    final counts = ref.watch(pantryTierCountsProvider);

    return Scaffold(
      appBar: AppBar(
        title: Text(l10n.pantryTitle),
        actions: [
          PopupMenuButton<PantrySort>(
            icon: const Icon(Icons.sort_rounded),
            initialValue: filter.sort,
            onSelected: (s) =>
                ref.read(pantryFilterControllerProvider.notifier).setSort(s),
            itemBuilder: (_) => [
              for (final s in PantrySort.values)
                PopupMenuItem(
                  value: s,
                  child: Text(l10n.pantrySortPrefix(s.label(l10n))),
                ),
            ],
          ),
        ],
      ),
      floatingActionButton: FloatingActionButton.extended(
        // Unique tag — all 5 shell branches stay mounted in the
        // StatefulShellRoute IndexedStack, so a default-tagged FAB here
        // collides with the one on the Shopping tab during route transitions.
        heroTag: 'pantry_fab',
        onPressed: () => showAddEntryChooser(context),
        icon: const Icon(Icons.add_rounded),
        label: Text(l10n.pantryAddIngredient),
      ),
      body: Column(
        children: [
          Padding(
            padding: const EdgeInsets.fromLTRB(Gap.lg, Gap.xs, Gap.lg, Gap.xs),
            child: AppSearchField(
              hintText: l10n.pantrySearchHint,
              onChanged: (q) =>
                  ref.read(pantryFilterControllerProvider.notifier).setQuery(q),
            ),
          ),
          TierSegmentedControl(
            selected: filter.tier,
            counts: counts,
            onSelected: (t) =>
                ref.read(pantryFilterControllerProvider.notifier).setTier(t),
          ),
          Gap.gapXs,
          Expanded(
            child: RefreshIndicator(
              onRefresh: () =>
                  ref.read(pantryListControllerProvider.notifier).refresh(),
              child: AsyncValueWidget<List<PantryItem>>(
                value: listAsync,
                onRetry: () => ref.invalidate(pantryListControllerProvider),
                data: (_) => const _PantryList(),
              ),
            ),
          ),
        ],
      ),
    );
  }
}

class _PantryList extends ConsumerWidget {
  const _PantryList();

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final l10n = context.l10n;
    final items = ref.watch(pantryListViewProvider);
    final threshold = ref.watch(appConfigProvider).nearExpiryDays;

    if (items.isEmpty) {
      final filtering = ref.watch(pantryFilterControllerProvider);
      final anyItems =
          (ref.watch(pantryListControllerProvider).asData?.value ?? [])
              .isNotEmpty;
      return EmptyState(
        title: anyItems ? l10n.pantryNoResults : l10n.pantryEmptyTitle,
        message: anyItems ? l10n.pantryNoResultsBody : l10n.pantryEmptyBody,
        icon: anyItems ? Icons.search_off_rounded : Icons.eco_outlined,
        actionLabel: filtering.tier == null && filtering.query.isEmpty
            ? l10n.pantryAddIngredient
            : null,
        onAction: () => showAddEntryChooser(context),
      );
    }

    final near = [
      for (final i in items)
        if (i.isNearExpiry(threshold: threshold)) i,
    ];
    final rest = [
      for (final i in items)
        if (!i.isNearExpiry(threshold: threshold)) i,
    ];

    return ListView(
      padding: const EdgeInsets.fromLTRB(Gap.lg, 0, Gap.lg, 96),
      children: [
        if (near.isNotEmpty) ...[
          Padding(
            padding: const EdgeInsets.symmetric(vertical: Gap.xs),
            child: SectionHeader(title: l10n.pantrySectionNear),
          ),
          for (final i in near) _row(context, i),
          Gap.gapMd,
        ],
        if (rest.isNotEmpty) ...[
          Padding(
            padding: const EdgeInsets.symmetric(vertical: Gap.xs),
            child: SectionHeader(
              title: near.isEmpty
                  ? l10n.pantrySectionAll
                  : l10n.pantrySectionRest,
            ),
          ),
          for (final i in rest) _row(context, i),
        ],
      ],
    );
  }

  Widget _row(BuildContext context, PantryItem item) => Padding(
    padding: const EdgeInsets.only(bottom: Gap.xs),
    child: PantryItemTile(
      item: item,
      onTap: () => context.push('${Routes.pantry}/item/${item.id}'),
    ),
  );
}
