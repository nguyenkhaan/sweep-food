import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:sweepfood/app/router/routes.dart';
import 'package:sweepfood/app/theme/app_icons.dart';
import 'package:sweepfood/app/theme/app_motion.dart';
import 'package:sweepfood/app/theme/app_spacing.dart';
import 'package:sweepfood/app/theme/app_typography.dart';
import 'package:sweepfood/core/utils/extensions/build_context_x.dart';
import 'package:sweepfood/core/widgets/app_snackbar.dart';
import 'package:sweepfood/core/widgets/async_value_widget.dart';
import 'package:sweepfood/core/widgets/empty_state.dart';
import 'package:sweepfood/features/shopping_list/domain/entities/shopping_list.dart';
import 'package:sweepfood/features/shopping_list/domain/entities/shopping_list_item.dart';
import 'package:sweepfood/features/shopping_list/presentation/controllers/shopping_list_controller.dart';
import 'package:sweepfood/features/shopping_list/presentation/widgets/add_shopping_item_sheet.dart';
import 'package:sweepfood/features/shopping_list/presentation/widgets/purchase_detail_sheet.dart';
import 'package:sweepfood/features/shopping_list/presentation/widgets/shopping_item_row.dart';

/// B-01 Danh sách mua sắm (Concept B Split Hero + Grouped Category Cards).
class ShoppingListScreen extends ConsumerWidget {
  const ShoppingListScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final l10n = context.l10n;
    final sweep = context.sweep;
    final cs = context.colors;
    final async = ref.watch(shoppingListControllerProvider);
    final showInStock = ref.watch(shoppingListShowInStockProvider);
    final currentList = async.asData?.value;
    final hasList = async.hasValue && currentList != null;

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
        floatingActionButton: hasList
            ? FloatingActionButton.extended(
                // Unique tag — all 5 shell branches stay mounted in the
                // StatefulShellRoute IndexedStack.
                heroTag: 'shopping_fab',
                backgroundColor: sweep.ctaWarm,
                foregroundColor: sweep.onCtaWarm,
                elevation: 2,
                highlightElevation: 3,
                shape: const RoundedRectangleBorder(borderRadius: Radii.brLg),
                onPressed: () {
                  AppHaptics.light();
                  AddShoppingItemSheet.show(context);
                },
                icon: const Icon(AppIcons.add, size: 20),
                label: Text(
                  l10n.shoppingAddItem,
                  style: context.text.labelLarge?.copyWith(
                    color: sweep.onCtaWarm,
                    fontWeight: FontWeight.w700,
                  ),
                ),
              )
            : null,
        body: Column(
          children: [
            _ShoppingEmeraldHeader(
              list: currentList,
              onOpenMealPlan: () => context.push(Routes.mealPlan),
            ),
            Expanded(
              child: RefreshIndicator(
                color: sweep.ctaWarm,
                onRefresh: () =>
                    ref.read(shoppingListControllerProvider.notifier).refresh(),
                child: AsyncValueWidget<ShoppingList?>(
                  value: async,
                  onRetry: () => ref.invalidate(shoppingListControllerProvider),
                  data: (list) {
                    if (list == null) {
                      return ListView(
                        padding: const EdgeInsets.fromLTRB(
                          Gap.lg,
                          Gap.xl,
                          Gap.lg,
                          Gap.xxl,
                        ),
                        children: [
                          EmptyState(
                            illustrationAsset:
                                'assets/illustrations/empty_shopping.svg',
                            title: l10n.shoppingEmptyTitle,
                            message: l10n.shoppingEmptyBody,
                            actionLabel: l10n.shoppingPlanWeek,
                            onAction: () => context.push(Routes.mealPlan),
                          ),
                        ],
                      );
                    }
                    if (list.items.isEmpty) {
                      return ListView(
                        padding: const EdgeInsets.fromLTRB(
                          Gap.lg,
                          Gap.xl,
                          Gap.lg,
                          Gap.xxl,
                        ),
                        children: const [
                          EmptyState(
                            illustrationAsset:
                                'assets/illustrations/empty_shopping.svg',
                            title: 'Danh sách đã sẵn sàng',
                            message:
                                'Thực đơn hiện không có nguyên liệu nào cần mua thêm. Dùng nút “Thêm món” để bổ sung thủ công.',
                          ),
                        ],
                      );
                    }

                    final groups = list.grouped(showInStock: showInStock);

                    return ListView(
                      padding: const EdgeInsets.fromLTRB(Gap.lg, 0, Gap.lg, 96),
                      children: [
                        // Clean rounded filter toggle card
                        Container(
                          padding: const EdgeInsets.symmetric(
                            horizontal: Gap.md,
                            vertical: Gap.xs,
                          ),
                          decoration: BoxDecoration(
                            color: cs.surfaceContainerLowest,
                            borderRadius: Radii.brLg,
                            border: Border.all(color: sweep.hairline),
                          ),
                          child: Row(
                            children: [
                              Icon(
                                AppIcons.pantry,
                                size: 17,
                                color: cs.primary,
                              ),
                              const SizedBox(width: Gap.sm),
                              Expanded(
                                child: Text(
                                  l10n.shoppingShowInStock,
                                  style: context.text.bodyMedium?.copyWith(
                                    fontWeight: FontWeight.w600,
                                  ),
                                ),
                              ),
                              Switch(
                                value: showInStock,
                                onChanged: (_) {
                                  AppHaptics.selection();
                                  ref
                                      .read(
                                        shoppingListShowInStockProvider
                                            .notifier,
                                      )
                                      .toggle();
                                },
                              ),
                            ],
                          ),
                        ),
                        if (groups.isEmpty) ...[
                          const SizedBox(height: 36),
                          EmptyState(
                            illustrationAsset: list.items.any((i) => i.checked)
                                ? 'assets/illustrations/shopping_all_done.svg'
                                : 'assets/illustrations/empty_shopping.svg',
                            title: list.items.any((i) => i.checked)
                                ? 'Đã mua hết nguyên liệu'
                                : 'Danh sách đã sẵn sàng',
                            message: list.items.any((i) => i.checked)
                                ? 'Tất cả nguyên liệu cần mua đã được mua xong và chuyển vào kho bếp. Dùng nút “Thêm món” nếu bạn muốn mua thêm.'
                                : 'Thực đơn hiện không có nguyên liệu nào cần mua thêm. Dùng nút “Thêm món” để bổ sung thủ công.',
                            icon: AppIcons.checkCircle,
                          ),
                        ] else ...[
                          for (final entry in groups.entries) ...[
                            Padding(
                              padding: const EdgeInsets.fromLTRB(
                                2,
                                Gap.md + 2,
                                2,
                                Gap.xs + 2,
                              ),
                              child: Row(
                                children: [
                                  Expanded(
                                    child: Text(
                                      entry.key.toUpperCase(),
                                      style: context.text.labelSmall?.copyWith(
                                        letterSpacing: 0.7,
                                        fontWeight: FontWeight.w800,
                                        color: sweep.textTertiary,
                                      ),
                                    ),
                                  ),
                                  Text(
                                    '${entry.value.length} món',
                                    style: context.text.labelSmall?.copyWith(
                                      letterSpacing: 0,
                                      color: sweep.textTertiary,
                                      fontWeight: FontWeight.w600,
                                    ),
                                  ),
                                ],
                              ),
                            ),
                            Material(
                              color: cs.surfaceContainerLowest,
                              shape: RoundedRectangleBorder(
                                borderRadius: Radii.brXl,
                                side: BorderSide(color: sweep.hairline),
                              ),
                              clipBehavior: Clip.antiAlias,
                              child: Column(
                                children: [
                                  for (
                                    var i = 0;
                                    i < entry.value.length;
                                    i++
                                  ) ...[
                                    if (i > 0)
                                      Divider(height: 1, color: sweep.hairline),
                                    ShoppingItemRow(
                                      item: entry.value[i],
                                      onToggle: () => _toggleItem(
                                        context,
                                        ref,
                                        entry.value[i],
                                      ),
                                      onDismissed: () => _removeItem(
                                        context,
                                        ref,
                                        entry.value[i],
                                      ),
                                    ),
                                  ],
                                ],
                              ),
                            ),
                          ],
                          Gap.gapMd,
                          // Compact summary footer pill
                          Container(
                            padding: const EdgeInsets.symmetric(
                              horizontal: Gap.md,
                              vertical: Gap.sm + 2,
                            ),
                            decoration: BoxDecoration(
                              color: sweep.subtleFill,
                              borderRadius: Radii.brLg,
                            ),
                            child: Row(
                              children: [
                                Icon(
                                  AppIcons.info,
                                  size: 15,
                                  color: sweep.textTertiary,
                                ),
                                const SizedBox(width: Gap.xs),
                                Text(
                                  l10n.shoppingEstimate,
                                  style: context.text.labelMedium?.copyWith(
                                    fontWeight: FontWeight.w700,
                                  ),
                                ),
                                const SizedBox(width: Gap.xs),
                                Expanded(
                                  child: Text(
                                    l10n.shoppingToBuyCount(list.toBuyCount),
                                    textAlign: TextAlign.right,
                                    style: context.text.bodySmall?.copyWith(
                                      color: sweep.textSecondary,
                                    ),
                                  ),
                                ),
                              ],
                            ),
                          ),
                        ],
                      ],
                    );
                  },
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  /// Checking an item (false→true) needs `purchase` details first — the
  /// backend uses them to create the resulting inventory batch. Un-checking
  /// needs none, so it's applied immediately.
  Future<void> _toggleItem(
    BuildContext context,
    WidgetRef ref,
    ShoppingListItem item,
  ) async {
    final notifier = ref.read(shoppingListControllerProvider.notifier);
    if (item.checked) {
      await notifier.toggleChecked(item.id);
      return;
    }
    final purchase = await PurchaseDetailSheet.show(context);
    if (purchase == null) return; // cancelled — stays unchecked
    final success = await notifier.toggleChecked(item.id, purchase: purchase);
    if (success && context.mounted) {
      AppSnack.show(context, 'Đã mua "${item.name}" và chuyển vào kho!');
    }
  }

  /// Swiping horizontally removes the ingredient from the shopping list.
  Future<void> _removeItem(
    BuildContext context,
    WidgetRef ref,
    ShoppingListItem item,
  ) async {
    final notifier = ref.read(shoppingListControllerProvider.notifier);
    final success = await notifier.removeItem(item.id);
    if (context.mounted) {
      if (success) {
        AppSnack.show(context, 'Đã xóa "${item.name}" khỏi danh sách');
      } else {
        AppSnack.show(context, 'Không thể xóa "${item.name}"');
      }
    }
  }
}

class _ShoppingEmeraldHeader extends StatelessWidget {
  const _ShoppingEmeraldHeader({required this.onOpenMealPlan, this.list});

  final ShoppingList? list;
  final VoidCallback onOpenMealPlan;

  @override
  Widget build(BuildContext context) {
    final l10n = context.l10n;
    final sweep = context.sweep;
    final cs = context.colors;

    final hasItems = list != null && list!.items.isNotEmpty;
    final totalItems = list?.items.length ?? 0;
    final boughtItems = list?.checkedCount ?? 0;
    final allDone = hasItems && boughtItems >= totalItems;
    final isVi = Localizations.localeOf(context).languageCode == 'vi';
    final progress = totalItems == 0
        ? 0.0
        : (boughtItems / totalItems).clamp(0.0, 1.0);

    return DecoratedBox(
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
                              l10n.shoppingTitle,
                              maxLines: 1,
                              overflow: TextOverflow.ellipsis,
                              style: context.text.headlineSmall?.copyWith(
                                color: sweep.onHeroSurface,
                                fontWeight: FontWeight.w800,
                              ),
                            ),
                            if (list?.sourceLabel != null) ...[
                              const SizedBox(height: 2),
                              Text(
                                list!.sourceLabel!,
                                maxLines: 1,
                                overflow: TextOverflow.ellipsis,
                                style: context.text.bodySmall?.copyWith(
                                  color: sweep.onHeroMuted,
                                ),
                              ),
                            ],
                          ],
                        ),
                      ),
                      const SizedBox(width: Gap.sm),
                      Tooltip(
                        message: l10n.mealPlanTitle,
                        child: Material(
                          color: sweep.heroSurfaceElevated,
                          shape: RoundedRectangleBorder(
                            borderRadius: Radii.brMd,
                            side: BorderSide(
                              color: sweep.onHeroSurface.withValues(
                                alpha: 0.14,
                              ),
                            ),
                          ),
                          child: InkWell(
                            borderRadius: Radii.brMd,
                            onTap: () {
                              AppHaptics.selection();
                              onOpenMealPlan();
                            },
                            child: Padding(
                              padding: const EdgeInsets.symmetric(
                                horizontal: Gap.sm + 2,
                                vertical: 9,
                              ),
                              child: Row(
                                mainAxisSize: MainAxisSize.min,
                                children: [
                                  Icon(
                                    AppIcons.calendar,
                                    size: 16,
                                    color: sweep.onHeroMuted,
                                  ),
                                  const SizedBox(width: 6),
                                  Text(
                                    'Thực đơn',
                                    style: context.text.labelSmall?.copyWith(
                                      letterSpacing: 0,
                                      color: sweep.onHeroSurface,
                                      fontWeight: FontWeight.w700,
                                    ),
                                  ),
                                ],
                              ),
                            ),
                          ),
                        ),
                      ),
                    ],
                  ),
                  if (hasItems) ...[
                    Gap.gapMd,
                    Container(
                      padding: const EdgeInsets.all(Gap.sm + 4),
                      decoration: BoxDecoration(
                        color: sweep.heroSurfaceElevated,
                        borderRadius: Radii.brLg,
                        border: Border.all(
                          color: sweep.onHeroSurface.withValues(alpha: 0.14),
                        ),
                      ),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Row(
                            children: [
                              Icon(
                                allDone
                                    ? AppIcons.badgeCheck
                                    : AppIcons.shopping,
                                size: 15,
                                color: allDone
                                    ? sweep.onHeroSurface
                                    : sweep.onHeroMuted,
                              ),
                              const SizedBox(width: 6),
                              Expanded(
                                child: Text(
                                  l10n.shoppingProgressLabel(
                                    boughtItems,
                                    totalItems,
                                  ),
                                  maxLines: 1,
                                  overflow: TextOverflow.ellipsis,
                                  style: AppTypography.tabular(
                                    context.text.labelMedium?.copyWith(
                                      color: sweep.onHeroSurface,
                                      fontWeight: FontWeight.w700,
                                    ),
                                  ),
                                ),
                              ),
                              const SizedBox(width: 6),
                              AnimatedSwitcher(
                                duration: AppMotion.resolve(
                                  context,
                                  context.motion.medium,
                                ),
                                transitionBuilder: (child, anim) =>
                                    ScaleTransition(
                                      scale: CurvedAnimation(
                                        parent: anim,
                                        curve: AppMotion.resolveCurve(
                                          context,
                                          Curves.easeOutBack,
                                        ),
                                      ),
                                      child: FadeTransition(
                                        opacity: anim,
                                        child: child,
                                      ),
                                    ),
                                child: allDone
                                    ? Container(
                                        key: const ValueKey('all-done-pill'),
                                        padding: const EdgeInsets.symmetric(
                                          horizontal: 8,
                                          vertical: 3,
                                        ),
                                        decoration: BoxDecoration(
                                          color: sweep.ctaWarm,
                                          borderRadius: BorderRadius.circular(
                                            Radii.pill,
                                          ),
                                        ),
                                        child: Text(
                                          isVi ? 'Hoàn tất!' : 'All done!',
                                          maxLines: 1,
                                          style: context.text.labelSmall
                                              ?.copyWith(
                                                letterSpacing: 0,
                                                color: sweep.onCtaWarm,
                                                fontWeight: FontWeight.w800,
                                              ),
                                        ),
                                      )
                                    : Text(
                                        l10n.shoppingRemainingLabel(
                                          list!.toBuyCount,
                                        ),
                                        key: const ValueKey('remaining-label'),
                                        maxLines: 1,
                                        style: context.text.labelSmall
                                            ?.copyWith(
                                              letterSpacing: 0,
                                              color: sweep.onHeroMuted,
                                              fontWeight: FontWeight.w700,
                                            ),
                                      ),
                              ),
                            ],
                          ),
                          const SizedBox(height: Gap.sm),
                          ClipRRect(
                            borderRadius: BorderRadius.circular(Radii.pill),
                            child: TweenAnimationBuilder<double>(
                              tween: Tween(begin: 0, end: progress),
                              duration: AppMotion.resolve(
                                context,
                                context.motion.medium,
                              ),
                              curve: AppMotion.resolveCurve(
                                context,
                                context.motion.enterCurve,
                              ),
                              builder: (_, val, __) => LinearProgressIndicator(
                                value: val,
                                minHeight: 6,
                                backgroundColor: sweep.onHeroSurface.withValues(
                                  alpha: 0.16,
                                ),
                                valueColor: AlwaysStoppedAnimation(
                                  sweep.ctaWarm,
                                ),
                              ),
                            ),
                          ),
                        ],
                      ),
                    ),
                  ],
                ],
              ),
            ),
          ),
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
    );
  }
}
