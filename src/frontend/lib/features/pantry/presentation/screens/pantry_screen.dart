import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:frontend/app/router/routes.dart';
import 'package:frontend/app/theme/app_spacing.dart';
import 'package:frontend/core/config/app_config_provider.dart';
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
    final listAsync = ref.watch(pantryListControllerProvider);
    final filter = ref.watch(pantryFilterControllerProvider);
    final counts = ref.watch(pantryTierCountsProvider);

    return Scaffold(
      appBar: AppBar(
        title: const Text('Kho thực phẩm'),
        actions: [
          PopupMenuButton<PantrySort>(
            icon: const Icon(Icons.sort_rounded),
            initialValue: filter.sort,
            onSelected: (s) =>
                ref.read(pantryFilterControllerProvider.notifier).setSort(s),
            itemBuilder: (_) => [
              for (final s in PantrySort.values)
                PopupMenuItem(value: s, child: Text('Sắp xếp: ${s.label}')),
            ],
          ),
        ],
      ),
      floatingActionButton: FloatingActionButton.extended(
        onPressed: () => showAddEntryChooser(context),
        icon: const Icon(Icons.add_rounded),
        label: const Text('Thêm nguyên liệu'),
      ),
      body: Column(
        children: [
          Padding(
            padding: const EdgeInsets.fromLTRB(Gap.lg, Gap.xs, Gap.lg, Gap.xs),
            child: AppSearchField(
              hintText: 'Tìm trong tủ bếp…',
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
    final items = ref.watch(pantryListViewProvider);
    final threshold = ref.watch(appConfigProvider).nearExpiryDays;

    if (items.isEmpty) {
      final filtering = ref.watch(pantryFilterControllerProvider);
      final anyItems =
          (ref.watch(pantryListControllerProvider).asData?.value ?? [])
              .isNotEmpty;
      return EmptyState(
        title: anyItems ? 'Không có kết quả' : 'Tủ bếp đang trống',
        message: anyItems
            ? 'Thử đổi bộ lọc hoặc từ khóa khác.'
            : 'Thêm nguyên liệu đầu tiên để nhận gợi ý món.',
        icon: anyItems ? Icons.search_off_rounded : Icons.eco_outlined,
        actionLabel: filtering.tier == null && filtering.query.isEmpty
            ? 'Thêm nguyên liệu'
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
          const Padding(
            padding: EdgeInsets.symmetric(vertical: Gap.xs),
            child: SectionHeader(title: 'Cần dùng sớm'),
          ),
          for (final i in near) _row(context, i),
          Gap.gapMd,
        ],
        if (rest.isNotEmpty) ...[
          Padding(
            padding: const EdgeInsets.symmetric(vertical: Gap.xs),
            child: SectionHeader(title: near.isEmpty ? 'Tất cả' : 'Còn hạn'),
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
