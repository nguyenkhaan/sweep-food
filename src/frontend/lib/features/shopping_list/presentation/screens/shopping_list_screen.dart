import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:frontend/app/router/routes.dart';
import 'package:frontend/app/theme/app_spacing.dart';
import 'package:frontend/core/utils/extensions/build_context_x.dart';

import 'package:frontend/core/widgets/async_value_widget.dart';
import 'package:frontend/core/widgets/empty_state.dart';
import 'package:frontend/features/shopping_list/domain/entities/shopping_list.dart';
import 'package:frontend/features/shopping_list/presentation/controllers/shopping_list_controller.dart';
import 'package:frontend/features/shopping_list/presentation/widgets/add_shopping_item_sheet.dart';
import 'package:frontend/features/shopping_list/presentation/widgets/shopping_item_row.dart';
import 'package:go_router/go_router.dart';

/// B-01 Danh sách mua sắm — grouped by category, hide-in-stock toggle, check off,
/// estimated total.
class ShoppingListScreen extends ConsumerWidget {
  const ShoppingListScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final l10n = context.l10n;
    final async = ref.watch(shoppingListControllerProvider);
    final showInStock = ref.watch(shoppingListShowInStockProvider);

    return Scaffold(
      appBar: AppBar(title: Text(l10n.shoppingTitle)),
      floatingActionButton: async.hasValue
          ? FloatingActionButton.extended(
              // Unique tag — see note on the Pantry FAB (shared IndexedStack
              // subtree ⇒ default FAB hero tags collide).
              heroTag: 'shopping_fab',
              onPressed: () => AddShoppingItemSheet.show(context),
              icon: const Icon(Icons.add_rounded),
              label: Text(l10n.shoppingAddItem),
            )
          : null,
      body: RefreshIndicator(
        onRefresh: () =>
            ref.read(shoppingListControllerProvider.notifier).refresh(),
        child: AsyncValueWidget<ShoppingList>(
          value: async,
          onRetry: () => ref.invalidate(shoppingListControllerProvider),
          data: (list) {
            if (list.items.isEmpty) {
              return ListView(
                children: [
                  const SizedBox(height: 72),
                  EmptyState(
                    title: l10n.shoppingEmptyTitle,
                    message: l10n.shoppingEmptyBody,
                    icon: Icons.shopping_cart_outlined,
                    actionLabel: l10n.shoppingPlanWeek,
                    onAction: () => context.push(Routes.mealPlan),
                  ),
                ],
              );
            }
            final groups = list.grouped(showInStock: showInStock);
            return ListView(
              padding: const EdgeInsets.only(bottom: 96),
              children: [
                if (list.sourceLabel != null)
                  Padding(
                    padding: const EdgeInsets.fromLTRB(
                      Gap.lg,
                      Gap.sm,
                      Gap.lg,
                      0,
                    ),
                    child: Text(
                      list.sourceLabel!,
                      style: context.text.bodySmall?.copyWith(
                        color: context.sweep.textSecondary,
                      ),
                    ),
                  ),
                SwitchListTile(
                  value: showInStock,
                  onChanged: (_) => ref
                      .read(shoppingListShowInStockProvider.notifier)
                      .toggle(),
                  title: Text(l10n.shoppingShowInStock),
                  contentPadding: const EdgeInsets.symmetric(
                    horizontal: Gap.lg,
                  ),
                ),
                for (final entry in groups.entries) ...[
                  Padding(
                    padding: const EdgeInsets.fromLTRB(
                      Gap.lg,
                      Gap.md,
                      Gap.lg,
                      Gap.xs,
                    ),
                    child: Text(
                      entry.key.toUpperCase(),
                      style: context.text.labelSmall,
                    ),
                  ),
                  for (final item in entry.value)
                    ShoppingItemRow(
                      item: item,
                      onToggle: () => ref
                          .read(shoppingListControllerProvider.notifier)
                          .toggleChecked(item.id),
                      onDismissed: item.isManual
                          ? () => ref
                                .read(shoppingListControllerProvider.notifier)
                                .removeItem(item.id)
                          : null,
                    ),
                ],
                const Divider(height: 1),
                Padding(
                  padding: const EdgeInsets.all(Gap.lg),
                  child: Row(
                    children: [
                      Text(
                        l10n.shoppingEstimate,
                        style: context.text.titleSmall?.copyWith(
                          fontWeight: FontWeight.w700,
                        ),
                      ),
                      Gap.gapXs,
                      Text(
                        l10n.shoppingToBuyCount(list.toBuyCount),
                        style: context.text.bodySmall?.copyWith(
                          color: context.sweep.textTertiary,
                        ),
                      ),
                      const Spacer(),
                    ],
                  ),
                ),
              ],
            );
          },
        ),
      ),
    );
  }
}
