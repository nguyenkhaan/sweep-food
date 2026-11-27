import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:sweepfood/app/router/routes.dart';
import 'package:sweepfood/app/theme/app_icons.dart';
import 'package:sweepfood/app/theme/app_motion.dart';
import 'package:sweepfood/app/theme/app_spacing.dart';
import 'package:sweepfood/core/config/app_config_provider.dart';
import 'package:sweepfood/core/utils/extensions/build_context_x.dart';
import 'package:sweepfood/core/widgets/app_search_field.dart';
import 'package:sweepfood/core/widgets/app_snackbar.dart';
import 'package:sweepfood/core/widgets/async_value_widget.dart';
import 'package:sweepfood/core/widgets/empty_state.dart';
import 'package:sweepfood/features/ingest/presentation/screens/add_entry_chooser_sheet.dart';
import 'package:sweepfood/features/pantry/domain/entities/pantry_item.dart';
import 'package:sweepfood/features/pantry/domain/entities/pantry_item_draft.dart';
import 'package:sweepfood/features/pantry/domain/repositories/pantry_repository.dart';
import 'package:sweepfood/features/pantry/presentation/controllers/pantry_list_controller.dart';
import 'package:sweepfood/features/pantry/presentation/widgets/adjust_quantity_sheet.dart';
import 'package:sweepfood/features/pantry/presentation/widgets/pantry_item_tile.dart';
import 'package:sweepfood/features/pantry/presentation/widgets/tier_segmented_control.dart';

/// K-01 — Kho thực phẩm (Concept B Split Hero).
class PantryScreen extends ConsumerStatefulWidget {
  const PantryScreen({super.key});

  @override
  ConsumerState<PantryScreen> createState() => _PantryScreenState();
}

class _PantryScreenState extends ConsumerState<PantryScreen> {
  final Set<String> _selectedIds = {};
  bool _showPromptInput = false;
  late final TextEditingController _promptController;

  @override
  void initState() {
    super.initState();
    _promptController = TextEditingController();
  }

  @override
  void dispose() {
    _promptController.dispose();
    super.dispose();
  }

  void _toggleSelect(String id) {
    setState(() {
      if (_selectedIds.contains(id)) {
        _selectedIds.remove(id);
        if (_selectedIds.isEmpty) {
          _showPromptInput = false;
        }
      } else {
        _selectedIds.add(id);
      }
    });
  }

  @override
  Widget build(BuildContext context) {
    final l10n = context.l10n;
    final sweep = context.sweep;
    final cs = context.colors;
    final listAsync = ref.watch(pantryListControllerProvider);
    final filter = ref.watch(pantryFilterControllerProvider);
    final counts = ref.watch(pantryTierCountsProvider);
    final totalCount = counts[null] ?? 0;
    final threshold = ref.watch(appConfigProvider).nearExpiryDays;
    final allItems = listAsync.asData?.value ?? const <PantryItem>[];
    final nearCount = allItems
        .where((i) => i.isNearExpiry(threshold: threshold))
        .length;
    final subtitleText = nearCount > 0
        ? '${l10n.ingredientCount(totalCount)} · $nearCount cần dùng sớm'
        : l10n.ingredientCount(totalCount);

    return AnnotatedRegion<SystemUiOverlayStyle>(
      value: SystemUiOverlayStyle(
        statusBarColor: Colors.transparent,
        statusBarIconBrightness: Brightness.light,
        statusBarBrightness: Brightness.dark,
        systemNavigationBarColor: cs.surfaceContainerLowest,
        systemNavigationBarIconBrightness:
            Theme.of(context).brightness == Brightness.dark
            ? Brightness.light
            : Brightness.dark,
      ),
      child: Scaffold(
        backgroundColor: cs.surface,
        floatingActionButton: _selectedIds.isNotEmpty
            ? null
            : FloatingActionButton.extended(
                // Unique tag — all 5 shell branches stay mounted in the
                // StatefulShellRoute IndexedStack, so a default-tagged FAB here
                // collides with the one on the Shopping tab during route transitions.
                heroTag: 'pantry_fab',
                backgroundColor: sweep.ctaWarm,
                foregroundColor: sweep.onCtaWarm,
                elevation: 2,
                highlightElevation: 3,
                shape: const RoundedRectangleBorder(borderRadius: Radii.brLg),
                onPressed: () {
                  AppHaptics.light();
                  showAddEntryChooser(context);
                },
                icon: const Icon(AppIcons.add, size: 20),
                label: Text(
                  l10n.pantryAddIngredient,
                  style: context.text.labelLarge?.copyWith(
                    color: sweep.onCtaWarm,
                    fontWeight: FontWeight.w700,
                  ),
                ),
              ),
        bottomNavigationBar: _selectedIds.isEmpty
            ? null
            : SafeArea(
                top: false,
                child: AnimatedContainer(
                  duration: AppMotion.resolve(context, context.motion.fast),
                  curve: AppMotion.resolveCurve(
                    context,
                    context.motion.enterCurve,
                  ),
                  padding: const EdgeInsets.fromLTRB(
                    Gap.md,
                    Gap.sm,
                    Gap.md,
                    Gap.sm,
                  ),
                  decoration: BoxDecoration(
                    color: cs.surfaceContainerLowest,
                    border: Border(top: BorderSide(color: sweep.hairline)),
                    boxShadow: Shadows.e3,
                  ),
                  child: Column(
                    mainAxisSize: MainAxisSize.min,
                    crossAxisAlignment: CrossAxisAlignment.stretch,
                    children: [
                      if (_showPromptInput) ...[
                        Row(
                          children: [
                            Expanded(
                              child: TextField(
                                controller: _promptController,
                                style: context.text.bodyMedium,
                                decoration: InputDecoration(
                                  hintText:
                                      'Yêu cầu món (VD: ít dầu mỡ, món canh...)',
                                  hintStyle: context.text.bodySmall?.copyWith(
                                    color: sweep.textTertiary,
                                  ),
                                  prefixIcon: Icon(
                                    AppIcons.suggestions,
                                    size: 18,
                                    color: cs.primary,
                                  ),
                                  suffixIcon: _promptController.text.isNotEmpty
                                      ? IconButton(
                                          icon: const Icon(
                                            AppIcons.close,
                                            size: 16,
                                          ),
                                          onPressed: () {
                                            setState(
                                              () => _promptController.clear(),
                                            );
                                          },
                                        )
                                      : null,
                                  filled: true,
                                  fillColor: sweep.subtleFill,
                                  isDense: true,
                                  contentPadding: const EdgeInsets.symmetric(
                                    horizontal: Gap.sm,
                                    vertical: Gap.xs,
                                  ),
                                  border: OutlineInputBorder(
                                    borderRadius: Radii.brMd,
                                    borderSide: BorderSide(
                                      color: sweep.hairline,
                                    ),
                                  ),
                                  enabledBorder: OutlineInputBorder(
                                    borderRadius: Radii.brMd,
                                    borderSide: BorderSide(
                                      color: sweep.hairline,
                                    ),
                                  ),
                                ),
                                onChanged: (_) => setState(() {}),
                              ),
                            ),
                            const SizedBox(width: Gap.xs),
                            IconButton(
                              icon: const Icon(AppIcons.close, size: 18),
                              tooltip: 'Đóng',
                              onPressed: () =>
                                  setState(() => _showPromptInput = false),
                            ),
                          ],
                        ),
                        const Divider(height: Gap.md),
                      ],
                      Row(
                        children: [
                          Text(
                            'Đã chọn ${_selectedIds.length}',
                            style: context.text.titleSmall?.copyWith(
                              fontWeight: FontWeight.w700,
                            ),
                          ),
                          const SizedBox(width: Gap.xs),
                          TextButton(
                            onPressed: () {
                              setState(() {
                                _selectedIds.clear();
                                _showPromptInput = false;
                              });
                            },
                            child: const Text('Bỏ chọn'),
                          ),
                          const Spacer(),
                          OutlinedButton.icon(
                            style: OutlinedButton.styleFrom(
                              minimumSize: Size.zero,
                              padding: const EdgeInsets.symmetric(
                                horizontal: Gap.sm,
                                vertical: Gap.sm,
                              ),
                              side: BorderSide(
                                color:
                                    _showPromptInput ||
                                        _promptController.text.isNotEmpty
                                    ? cs.primary
                                    : sweep.hairline,
                              ),
                              backgroundColor:
                                  _showPromptInput ||
                                      _promptController.text.isNotEmpty
                                  ? cs.primaryContainer.withValues(alpha: 0.35)
                                  : null,
                            ),
                            onPressed: () {
                              setState(() {
                                _showPromptInput = !_showPromptInput;
                              });
                            },
                            icon: Icon(
                              AppIcons.suggestions,
                              size: 16,
                              color: cs.primary,
                            ),
                            label: Text(
                              'Yêu cầu AI',
                              style: context.text.labelMedium?.copyWith(
                                color: cs.primary,
                                fontWeight: FontWeight.w600,
                              ),
                            ),
                          ),
                        ],
                      ),
                      const SizedBox(height: Gap.xs),
                      SizedBox(
                        height: 48,
                        child: FilledButton.icon(
                          style: FilledButton.styleFrom(
                            backgroundColor: sweep.ctaWarm,
                            foregroundColor: sweep.onCtaWarm,
                            elevation: 0,
                            shadowColor: Colors.transparent,
                            shape: const RoundedRectangleBorder(
                              borderRadius: Radii.brLg,
                            ),
                          ),
                          onPressed: () {
                            final all =
                                ref
                                    .read(pantryListControllerProvider)
                                    .asData
                                    ?.value ??
                                [];
                            final selectedItems = all
                                .where((i) => _selectedIds.contains(i.id))
                                .toList();
                            final prompt = _promptController.text.trim();
                            context.push(
                              '${Routes.pantry}/${Routes.cookableRecipes}',
                              extra: (items: selectedItems, prompt: prompt),
                            );
                          },
                          icon: const Icon(AppIcons.cook, size: 18),
                          label: const Text('Xem công thức'),
                        ),
                      ),
                    ],
                  ),
                ),
              ),
        body: Column(
          children: [
            // ── Deep Forest Emerald Concept B Header ──────────────────────
            DecoratedBox(
              decoration: BoxDecoration(color: sweep.heroSurface),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  SafeArea(
                    bottom: false,
                    child: Padding(
                      padding: const EdgeInsets.fromLTRB(
                        Gap.lg,
                        Gap.sm,
                        Gap.lg,
                        Gap.md,
                      ),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Row(
                            children: [
                              Expanded(
                                child: Column(
                                  crossAxisAlignment: CrossAxisAlignment.start,
                                  children: [
                                    Text(
                                      l10n.pantryTitle,
                                      maxLines: 1,
                                      overflow: TextOverflow.ellipsis,
                                      style: context.text.headlineSmall
                                          ?.copyWith(
                                            color: sweep.onHeroSurface,
                                            fontWeight: FontWeight.w800,
                                          ),
                                    ),
                                    const SizedBox(height: 2),
                                    Text(
                                      subtitleText,
                                      maxLines: 1,
                                      overflow: TextOverflow.ellipsis,
                                      style: context.text.bodySmall?.copyWith(
                                        color: sweep.onHeroMuted,
                                      ),
                                    ),
                                  ],
                                ),
                              ),
                              if (_selectedIds.isNotEmpty) ...[
                                _HeroActionIconButton(
                                  icon: AppIcons.close,
                                  tooltip: 'Bỏ chọn',
                                  onPressed: () => setState(() {
                                    _selectedIds.clear();
                                    _showPromptInput = false;
                                  }),
                                ),
                                const SizedBox(width: Gap.xs),
                              ],
                              _HeroActionIconButton(
                                icon: AppIcons.history,
                                tooltip: 'Lịch sử biến động kho',
                                onPressed: () =>
                                    context.push(Routes.inventoryLedger),
                              ),
                              const SizedBox(width: Gap.xs),
                              _HeroSortButton(
                                currentSort: filter.sort,
                                onSelected: (s) => ref
                                    .read(
                                      pantryFilterControllerProvider.notifier,
                                    )
                                    .setSort(s),
                              ),
                            ],
                          ),
                          Gap.gapMd,
                          AppSearchField(
                            hintText: l10n.pantrySearchHint,
                            onChanged: (q) => ref
                                .read(pantryFilterControllerProvider.notifier)
                                .setQuery(q),
                          ),
                        ],
                      ),
                    ),
                  ),
                  // Curved transition into the rising crisp list surface
                  Container(
                    height: 20,
                    decoration: BoxDecoration(
                      color: cs.surface,
                      borderRadius: const BorderRadius.vertical(
                        top: Radius.circular(26),
                      ),
                    ),
                  ),
                ],
              ),
            ),

            // ── Tier Filters + Pantry List ────────────────────────────────
            TierSegmentedControl(
              selected: filter.tier,
              counts: counts,
              onSelected: (t) =>
                  ref.read(pantryFilterControllerProvider.notifier).setTier(t),
            ),
            Gap.gapXs,
            Expanded(
              child: RefreshIndicator(
                color: sweep.ctaWarm,
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
      ),
    );
  }
}

class _HeroActionIconButton extends StatelessWidget {
  const _HeroActionIconButton({
    required this.icon,
    required this.tooltip,
    required this.onPressed,
  });

  final IconData icon;
  final String tooltip;
  final VoidCallback onPressed;

  @override
  Widget build(BuildContext context) {
    final sweep = context.sweep;
    return Tooltip(
      message: tooltip,
      child: Material(
        color: sweep.heroSurfaceElevated,
        shape: RoundedRectangleBorder(
          borderRadius: Radii.brMd,
          side: BorderSide(color: sweep.onHeroSurface.withValues(alpha: 0.14)),
        ),
        child: InkWell(
          borderRadius: Radii.brMd,
          onTap: () {
            AppHaptics.selection();
            onPressed();
          },
          child: SizedBox(
            width: 42,
            height: 42,
            child: Icon(icon, size: 19, color: sweep.onHeroSurface),
          ),
        ),
      ),
    );
  }
}

class _HeroSortButton extends StatelessWidget {
  const _HeroSortButton({required this.currentSort, required this.onSelected});

  final PantrySort currentSort;
  final ValueChanged<PantrySort> onSelected;

  @override
  Widget build(BuildContext context) {
    final l10n = context.l10n;
    final sweep = context.sweep;
    return Material(
      color: sweep.heroSurfaceElevated,
      shape: RoundedRectangleBorder(
        borderRadius: Radii.brMd,
        side: BorderSide(color: sweep.onHeroSurface.withValues(alpha: 0.14)),
      ),
      child: PopupMenuButton<PantrySort>(
        tooltip: 'Sắp xếp',
        initialValue: currentSort,
        onSelected: onSelected,
        shape: const RoundedRectangleBorder(borderRadius: Radii.brMd),
        child: SizedBox(
          width: 42,
          height: 42,
          child: Icon(AppIcons.sort, size: 19, color: sweep.onHeroSurface),
        ),
        itemBuilder: (_) => [
          for (final s in PantrySort.values)
            PopupMenuItem(
              value: s,
              child: Text(l10n.pantrySortPrefix(s.label(l10n))),
            ),
        ],
      ),
    );
  }
}

class _PantryList extends ConsumerWidget {
  const _PantryList({required this.selectedIds, required this.onToggleSelect});

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
        illustrationAsset: anyItems
            ? 'assets/illustrations/empty_search.svg'
            : 'assets/illustrations/empty_pantry.svg',
        title: anyItems ? l10n.pantryNoResults : l10n.pantryEmptyTitle,
        message: anyItems ? l10n.pantryNoResultsBody : l10n.pantryEmptyBody,
        icon: anyItems ? AppIcons.search : AppIcons.leaf,
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
            child: _PantrySectionBar(
              title: l10n.pantrySectionNear,
              hint: selectedIds.isEmpty ? 'Chạm icon để chọn' : null,
            ),
          ),
          for (final i in near) _row(context, ref, i),
          Gap.gapMd,
        ],
        if (rest.isNotEmpty) ...[
          Padding(
            padding: const EdgeInsets.symmetric(vertical: Gap.xs),
            child: _PantrySectionBar(
              title: near.isEmpty
                  ? l10n.pantrySectionAll
                  : l10n.pantrySectionRest,
              hint: near.isEmpty && selectedIds.isEmpty
                  ? 'Chạm icon để chọn'
                  : null,
            ),
          ),
          for (final i in rest) _row(context, ref, i),
        ],
      ],
    );
  }

  Widget _row(BuildContext context, WidgetRef ref, PantryItem item) {
    final l10n = context.l10n;
    final sweep = context.sweep;
    final isSelected = selectedIds.contains(item.id);
    final multiSelectActive = selectedIds.isNotEmpty;

    return Padding(
      padding: const EdgeInsets.only(bottom: Gap.xs),
      child: Dismissible(
        key: ValueKey('pantry-row-${item.id}'),
        direction: multiSelectActive
            ? DismissDirection.none
            : DismissDirection.horizontal,
        background: Container(
          alignment: Alignment.centerLeft,
          padding: const EdgeInsets.symmetric(horizontal: Gap.md),
          decoration: BoxDecoration(
            color: context.colors.primaryContainer,
            borderRadius: Radii.brLg,
          ),
          child: Row(
            children: [
              Icon(
                AppIcons.filter,
                size: 18,
                color: context.colors.onPrimaryContainer,
              ),
              const SizedBox(width: Gap.xs),
              Text(
                l10n.pantrySwipeAdjust,
                style: context.text.labelMedium?.copyWith(
                  color: context.colors.onPrimaryContainer,
                  fontWeight: FontWeight.w700,
                ),
              ),
            ],
          ),
        ),
        secondaryBackground: Container(
          alignment: Alignment.centerRight,
          padding: const EdgeInsets.symmetric(horizontal: Gap.md),
          decoration: BoxDecoration(
            color: sweep.successBg,
            borderRadius: Radii.brLg,
          ),
          child: Row(
            mainAxisAlignment: MainAxisAlignment.end,
            children: [
              Text(
                l10n.pantrySwipeConsume,
                style: context.text.labelMedium?.copyWith(
                  color: sweep.successFg,
                  fontWeight: FontWeight.w700,
                ),
              ),
              const SizedBox(width: Gap.xs),
              Icon(AppIcons.check, size: 18, color: sweep.successFg),
            ],
          ),
        ),
        confirmDismiss: (direction) async {
          if (direction == DismissDirection.startToEnd) {
            AppHaptics.selection();
            if (context.mounted) {
              await AdjustQuantitySheet.show(context, item);
            }
            return false;
          }
          AppHaptics.medium();
          try {
            final notifier = ref.read(pantryListControllerProvider.notifier);
            await notifier.consume(item.id, quantityUsed: item.quantity);
            if (context.mounted) {
              AppSnack.undoable(
                context,
                l10n.pantryConsumedAll(item.name),
                onUndo: () {
                  notifier.add(
                    PantryItemDraft(
                      name: item.name,
                      category: item.category,
                      quantity: item.quantity,
                      unit: item.unit,
                      storageTier: item.storageTier,
                      source: item.source,
                      ingredientId: item.ingredientId,
                      packedDate: item.packedDate,
                      expiryDate: item.expiryDate,
                      referenceShelfLifeDays: item.referenceShelfLifeDays,
                      priceVnd: item.priceVnd,
                    ),
                  );
                },
              );
            }
            return true;
          } catch (_) {
            if (context.mounted) {
              AppSnack.show(context, l10n.pantryUpdateFailed);
            }
            return false;
          }
        },
        child: PantryItemTile(
          item: item,
          selected: isSelected,
          onSelectedChanged: (_) => onToggleSelect(item.id),
          onTap: multiSelectActive
              ? () => onToggleSelect(item.id)
              : () => context.push('${Routes.pantry}/item/${item.id}'),
        ),
      ),
    );
  }
}

class _PantrySectionBar extends StatelessWidget {
  const _PantrySectionBar({required this.title, this.hint});

  final String title;
  final String? hint;

  @override
  Widget build(BuildContext context) {
    final sweep = context.sweep;
    final cs = context.colors;
    return Row(
      children: [
        Expanded(
          child: Text(
            title.toUpperCase(),
            maxLines: 1,
            overflow: TextOverflow.ellipsis,
            style: context.text.labelSmall?.copyWith(
              letterSpacing: 0.7,
              fontWeight: FontWeight.w800,
              color: sweep.textTertiary,
            ),
          ),
        ),
        if (hint != null) ...[
          const SizedBox(width: Gap.xs),
          Text(
            hint!,
            style: context.text.labelSmall?.copyWith(
              letterSpacing: 0,
              color: cs.primary,
              fontWeight: FontWeight.w600,
            ),
          ),
        ],
      ],
    );
  }
}
