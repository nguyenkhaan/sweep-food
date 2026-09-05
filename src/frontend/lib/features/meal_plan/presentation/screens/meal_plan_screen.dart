import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:sweepfood/app/router/routes.dart';
import 'package:sweepfood/app/theme/app_spacing.dart';
import 'package:sweepfood/core/utils/extensions/build_context_x.dart';
import 'package:sweepfood/core/utils/extensions/date_time_x.dart';
import 'package:sweepfood/core/widgets/app_bottom_sheet.dart';
import 'package:sweepfood/core/widgets/async_value_widget.dart';
import 'package:sweepfood/core/widgets/primary_button.dart';
import 'package:sweepfood/features/meal_plan/domain/entities/meal_plan.dart';
import 'package:sweepfood/features/meal_plan/domain/entities/meal_plan_entry.dart';
import 'package:sweepfood/features/meal_plan/presentation/controllers/meal_plan_controller.dart';
import 'package:sweepfood/features/meal_plan/presentation/widgets/meal_slot_cell.dart';
import 'package:sweepfood/features/shopping_list/presentation/controllers/shopping_list_controller.dart';
import 'package:sweepfood/features/suggestions/domain/entities/dish_suggestion.dart';
import 'package:sweepfood/features/suggestions/presentation/controllers/suggestion_list_controller.dart';

/// M-01 Thực đơn tuần — 7 days × (Sáng/Trưa/Tối), week nav, and
/// "Tạo danh sách mua sắm".
class MealPlanScreen extends ConsumerWidget {
  const MealPlanScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final l10n = context.l10n;
    final dayLabels = [
      l10n.wdMon,
      l10n.wdTue,
      l10n.wdWed,
      l10n.wdThu,
      l10n.wdFri,
      l10n.wdSat,
      l10n.wdSun,
    ];
    final weekStart = ref.watch(mealPlanWeekStartProvider);
    final async = ref.watch(mealPlanControllerProvider);

    return Scaffold(
      appBar: AppBar(title: Text(l10n.mealPlanTitle)),
      body: Column(
        children: [
          _WeekNav(
            label:
                '${weekStart.ddMM} – '
                '${weekStart.add(const Duration(days: 6)).ddMM}',
            onPrev: () =>
                ref.read(mealPlanWeekStartProvider.notifier).previous(),
            onNext: () => ref.read(mealPlanWeekStartProvider.notifier).next(),
          ),
          const _ColumnHeader(),
          Expanded(
            child: AsyncValueWidget<MealPlan>(
              value: async,
              onRetry: () => ref.invalidate(mealPlanControllerProvider),
              data: (plan) => ListView.builder(
                padding: const EdgeInsets.fromLTRB(Gap.lg, 0, Gap.lg, 96),
                itemCount: 7,
                itemBuilder: (context, i) {
                  final day = plan.days[i];
                  return Padding(
                    padding: const EdgeInsets.only(bottom: Gap.xs),
                    child: Row(
                      children: [
                        SizedBox(
                          width: 28,
                          child: Text(
                            dayLabels[i],
                            style: context.text.labelMedium?.copyWith(
                              fontWeight: FontWeight.w700,
                              color: context.sweep.textSecondary,
                            ),
                          ),
                        ),
                        for (final slot in MealSlot.values)
                          Expanded(
                            child: Padding(
                              padding: const EdgeInsets.only(left: Gap.xxs),
                              child: MealSlotCell(
                                entry: plan.entryAt(day, slot),
                                onTap: () => _assign(context, ref, day, slot),
                                onClear: () => ref
                                    .read(mealPlanControllerProvider.notifier)
                                    .clear(day, slot),
                              ),
                            ),
                          ),
                      ],
                    ),
                  );
                },
              ),
            ),
          ),
        ],
      ),
      bottomNavigationBar: async.hasValue
          ? SafeArea(
              minimum: const EdgeInsets.fromLTRB(
                Gap.lg,
                Gap.xs,
                Gap.lg,
                Gap.md,
              ),
              child: PrimaryButton(
                label: l10n.mealPlanGenerateShopping,
                icon: Icons.shopping_cart_outlined,
                onPressed: () => _generateShoppingList(context, ref),
              ),
            )
          : null,
    );
  }

  Future<void> _assign(
    BuildContext context,
    WidgetRef ref,
    DateTime day,
    MealSlot slot,
  ) async {
    final picked = await showAppBottomSheet<DishSuggestion>(
      context,
      builder: (_) => const _AssignSheet(),
    );
    if (picked == null) return;
    await ref
        .read(mealPlanControllerProvider.notifier)
        .assign(
          date: day,
          slot: slot,
          dishId: picked.id,
          servings: picked.dish.servings.toDouble(),
          dishName: picked.dish.name,
          dishImageUrl: picked.dish.imageUrl,
        );
  }

  Future<void> _generateShoppingList(
    BuildContext context,
    WidgetRef ref,
  ) async {
    final messenger = ScaffoldMessenger.of(context);
    final l10n = context.l10n;
    final planId = ref.read(mealPlanControllerProvider).asData?.value.id;
    if (planId == null) return;
    final res = await ref
        .read(shoppingListControllerProvider.notifier)
        .generateFromWeek(planId);
    res.fold(
      (f) => messenger.showSnackBar(
        SnackBar(content: Text(f.localizedMessage(l10n))),
      ),
      (_) {
        if (context.mounted) context.go(Routes.shopping);
      },
    );
  }
}

class _WeekNav extends StatelessWidget {
  const _WeekNav({
    required this.label,
    required this.onPrev,
    required this.onNext,
  });

  final String label;
  final VoidCallback onPrev;
  final VoidCallback onNext;

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: Gap.lg, vertical: Gap.xs),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          IconButton(
            onPressed: onPrev,
            icon: const Icon(Icons.chevron_left_rounded),
          ),
          Text(
            label,
            style: context.text.titleSmall?.copyWith(
              fontWeight: FontWeight.w700,
            ),
          ),
          IconButton(
            onPressed: onNext,
            icon: const Icon(Icons.chevron_right_rounded),
          ),
        ],
      ),
    );
  }
}

class _ColumnHeader extends StatelessWidget {
  const _ColumnHeader();

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.fromLTRB(Gap.lg, 0, Gap.lg, Gap.xs),
      child: Row(
        children: [
          const SizedBox(width: 28),
          for (final s in MealSlot.values)
            Expanded(
              child: Padding(
                padding: const EdgeInsets.only(left: Gap.xxs),
                child: Text(
                  s.label(context.l10n),
                  textAlign: TextAlign.center,
                  style: context.text.labelSmall,
                ),
              ),
            ),
        ],
      ),
    );
  }
}

/// M-02 — pick a dish for a slot. MVP: choose from the current suggestions.
class _AssignSheet extends ConsumerWidget {
  const _AssignSheet();

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final async = ref.watch(suggestionListControllerProvider);
    return SheetBody(
      title: context.l10n.mealPlanPickDish,
      subtitle: context.l10n.mealPlanPickDishSub,
      child: SizedBox(
        height: 360,
        child: AsyncValueWidget<List<DishSuggestion>>(
          value: async,
          data: (list) => ListView.separated(
            shrinkWrap: true,
            itemCount: list.length,
            separatorBuilder: (_, __) => const Divider(height: 1),
            itemBuilder: (context, i) {
              final s = list[i];
              return ListTile(
                contentPadding: EdgeInsets.zero,
                leading: const Icon(Icons.restaurant_rounded),
                title: Text(s.dish.name),
                subtitle: Text(s.dish.shortMeta(context.l10n)),
                onTap: () => Navigator.of(context).pop(s),
              );
            },
          ),
        ),
      ),
    );
  }
}
