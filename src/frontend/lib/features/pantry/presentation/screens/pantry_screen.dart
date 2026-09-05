import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:sweepfood/app/router/routes.dart';
import 'package:sweepfood/app/theme/app_spacing.dart';
import 'package:sweepfood/core/config/app_config_provider.dart';
import 'package:sweepfood/core/utils/extensions/build_context_x.dart';
import 'package:sweepfood/core/widgets/app_search_field.dart';
import 'package:sweepfood/core/widgets/async_value_widget.dart';
import 'package:sweepfood/core/widgets/empty_state.dart';
import 'package:sweepfood/core/widgets/section_header.dart';
import 'package:sweepfood/features/ingest/presentation/screens/add_entry_chooser_sheet.dart';
import 'package:sweepfood/features/pantry/domain/entities/pantry_item.dart';
import 'package:sweepfood/features/pantry/domain/repositories/pantry_repository.dart';
import 'package:sweepfood/features/pantry/presentation/controllers/pantry_list_controller.dart';
import 'package:sweepfood/features/pantry/presentation/widgets/pantry_item_tile.dart';
import 'package:sweepfood/features/pantry/presentation/widgets/tier_segmented_control.dart';

/// K-01 — Kho thực phẩm.
class PantryScreen extends ConsumerStatefulWidget {
  const PantryScreen({super.key});

  @override
  ConsumerState<PantryScreen> createState() => _PantryScreenState();
}

class _PantryScreenState extends ConsumerState<PantryScreen> {
  final Set<String> _selectedIds = {};

  void _toggleSelect(String id) {
    setState(() {
      if (_selectedIds.contains(id)) {
        _selectedIds.remove(id);
      } else {
        _selectedIds.add(id);
      }
    });
  }

  @override
  Widget build(BuildContext context) {
    final l10n = context.l10n;
    final listAsync = ref.watch(pantryListControllerProvider);
    final filter = ref.watch(pantryFilterControllerProvider);
    final counts = ref.watch(pantryTierCountsProvider);

    return Scaffold(
      appBar: AppBar(
        title: Text(l10n.pantryTitle),
        actions: [
          if (_selectedIds.isNotEmpty)
            IconButton(
              icon: const Icon(Icons.close_rounded),
              tooltip: 'Bỏ chọn',
              onPressed: () => setState(() => _selectedIds.clear()),
            ),
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
      floatingActionButton: _selectedIds.isNotEmpty
          ? null
          : FloatingActionButton.extended(
              // Unique tag — all 5 shell branches stay mounted in the
              // StatefulShellRoute IndexedStack, so a default-tagged FAB here
              // collides with the one on the Shopping tab during route transitions.
              heroTag: 'pantry_fab',
              onPressed: () => showAddEntryChooser(context),
              icon: const Icon(Icons.add_rounded),
              label: Text(l10n.pantryAddIngredient),
            ),
      bottomNavigationBar: _selectedIds.isEmpty
          ? null
          : SafeArea(
              child: Container(
                padding: const EdgeInsets.symmetric(
                  horizontal: Gap.lg,
                  vertical: Gap.sm,
                ),
                decoration: BoxDecoration(
                  color: context.colors.surfaceContainerLowest,
                  border: Border(top: BorderSide(color: context.sweep.hairline)),
                  boxShadow: [
                    BoxShadow(
                      color: Colors.black.withValues(alpha: 0.06),
                      blurRadius: 10,
                      offset: const Offset(0, -4),
                    ),
                  ],
                ),
                child: Row(
                  children: [
                    Text(
                      'Đã chọn ${_selectedIds.length}',
                      style: context.text.titleSmall?.copyWith(
                        fontWeight: FontWeight.w600,
                      ),
                    ),
                    const SizedBox(width: Gap.xs),
                    TextButton(
                      onPressed: () => setState(() => _selectedIds.clear()),
                      child: const Text('Bỏ chọn'),
                    ),
                    const Spacer(),
                    FilledButton.icon(
                      style: FilledButton.styleFrom(
                        minimumSize: Size.zero,
                        padding: const EdgeInsets.symmetric(
                          horizontal: Gap.md,
                          vertical: Gap.sm,
                        ),
                      ),
                      onPressed: () {
                        final all = ref
                                .read(pantryListControllerProvider)
                                .asData
                                ?.value ??
                            [];
                        final selectedItems = all
                            .where((i) => _selectedIds.contains(i.id))
                            .toList();
                        context.push(
                          '${Routes.pantry}/${Routes.cookableRecipes}',
                          extra: selectedItems,
                        );
                      },
                      icon: const Icon(Icons.restaurant_menu_rounded, size: 18),
                      label: const Text('Xem công thức'),
                    ),
                  ],
                ),
              ),
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
                data: (_) => _PantryList(
                  selectedIds: _selectedIds,
                  onToggleSelect: _toggleSelect,
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }
}

class _PantryList extends ConsumerWidget {
  const _PantryList({
    required this.selectedIds,
    required this.onToggleSelect,
  });

  final Set<String> selectedIds;
  final ValueChanged<String> onToggleSelect;

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

  Widget _row(BuildContext context, PantryItem item) {
    final isSelected = selectedIds.contains(item.id);
    return Padding(
      padding: const EdgeInsets.only(bottom: Gap.xs),
      child: PantryItemTile(
        item: item,
        selected: isSelected,
        onSelectedChanged: (_) => onToggleSelect(item.id),
        onTap: selectedIds.isNotEmpty
            ? () => onToggleSelect(item.id)
            : () => context.push('${Routes.pantry}/item/${item.id}'),
      ),
    );
  }
}
