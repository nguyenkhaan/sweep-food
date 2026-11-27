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
import 'package:sweepfood/core/utils/extensions/date_time_x.dart';
import 'package:sweepfood/core/widgets/async_value_widget.dart';
import 'package:sweepfood/core/widgets/recipe_image.dart';
import 'package:sweepfood/core/widgets/staggered_reveal.dart';
import 'package:sweepfood/core/widgets/tactile_card.dart';
import 'package:sweepfood/features/meal_plan/domain/entities/meal_plan.dart';
import 'package:sweepfood/features/meal_plan/domain/entities/meal_plan_entry.dart';
import 'package:sweepfood/features/meal_plan/presentation/controllers/meal_plan_controller.dart';
import 'package:sweepfood/features/meal_plan/presentation/widgets/dish_picker_sheet.dart';
import 'package:sweepfood/features/shopping_list/presentation/controllers/shopping_list_controller.dart';

/// M-01 Thực đơn tuần (Concept B · Format 2: Emerald Hero with Week Nav &
/// 7-Day Strip + Vertical Culinary Timeline Sáng → Trưa → Tối → Bữa phụ).
class MealPlanScreen extends ConsumerStatefulWidget {
  const MealPlanScreen({super.key});

  @override
  ConsumerState<MealPlanScreen> createState() => _MealPlanScreenState();
}

class _MealPlanScreenState extends ConsumerState<MealPlanScreen> {
  int _selectedDayIndex = (DateTime.now().weekday - 1).clamp(0, 6);

  @override
  Widget build(BuildContext context) {
    final l10n = context.l10n;
    final sweep = context.sweep;
    final cs = context.colors;
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
    final currentPlan = async.asData?.value;
    final hasMeals = currentPlan?.entries.isNotEmpty ?? false;
    final weekLabel =
        '${weekStart.ddMM} – '
        '${weekStart.add(const Duration(days: 6)).ddMM}';

    String? daySummarySubtitle;
    if (currentPlan != null && currentPlan.days.isNotEmpty) {
      final safeIdx = _selectedDayIndex.clamp(0, currentPlan.days.length - 1);
      final day = currentPlan.days[safeIdx];
      final planned = MealSlot.values
          .where((s) => currentPlan.entryAt(day, s) != null)
          .length;
      daySummarySubtitle =
          '${dayLabels[safeIdx]}, ${day.ddMM} · $planned/${MealSlot.values.length} bữa';
    }

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
        body: Column(
          children: [
            _MealPlanEmeraldHeader(
              weekLabel: weekLabel,
              subtitle: daySummarySubtitle,
              dayLabels: dayLabels,
              selectedIndex: _selectedDayIndex,
              plan: currentPlan,
              onPrevWeek: () {
                AppHaptics.selection();
                ref.read(mealPlanWeekStartProvider.notifier).previous();
              },
              onNextWeek: () {
                AppHaptics.selection();
                ref.read(mealPlanWeekStartProvider.notifier).next();
              },
              onSelectDay: (idx) {
                AppHaptics.selection();
                setState(() => _selectedDayIndex = idx);
              },
            ),
            Expanded(
              child: AsyncValueWidget<MealPlan>(
                value: async,
                onRetry: () => ref.invalidate(mealPlanControllerProvider),
                data: (plan) {
                  final days = plan.days;
                  final safeIdx = _selectedDayIndex.clamp(0, days.length - 1);
                  final selectedDay = days[safeIdx];

                  return ListView(
                    padding: const EdgeInsets.fromLTRB(
                      Gap.lg,
                      Gap.xs,
                      Gap.lg,
                      Gap.xxl,
                    ),
                    children: [
                      for (var i = 0; i < MealSlot.values.length; i++)
                        StaggeredReveal(
                          index: i,
                          child: _TimelineMealRow(
                            slot: MealSlot.values[i],
                            entry: plan.entryAt(
                              selectedDay,
                              MealSlot.values[i],
                            ),
                            isFirst: i == 0,
                            isLast: i == MealSlot.values.length - 1,
                            onTap: () => _assign(
                              context,
                              ref,
                              selectedDay,
                              MealSlot.values[i],
                            ),
                            onClear: () {
                              AppHaptics.light();
                              ref
                                  .read(mealPlanControllerProvider.notifier)
                                  .clear(selectedDay, MealSlot.values[i]);
                            },
                          ),
                        ),
                    ],
                  );
                },
              ),
            ),
          ],
        ),
        bottomNavigationBar: async.hasValue
            ? DecoratedBox(
                decoration: BoxDecoration(
                  color: cs.surfaceContainerLowest,
                  border: Border(top: BorderSide(color: sweep.hairline)),
                ),
                child: SafeArea(
                  top: false,
                  minimum: const EdgeInsets.fromLTRB(
                    Gap.lg,
                    Gap.sm,
                    Gap.lg,
                    Gap.sm,
                  ),
                  child: SizedBox(
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
                      onPressed: hasMeals
                          ? () => _generateShoppingList(context, ref)
                          : null,
                      icon: const Icon(AppIcons.shopping, size: 18),
                      label: Text(l10n.mealPlanGenerateShopping),
                    ),
                  ),
                ),
              )
            : null,
      ),
    );
  }

  Future<void> _assign(
    BuildContext context,
    WidgetRef ref,
    DateTime day,
    MealSlot slot,
  ) async {
    final picked = await DishPickerSheet.show(context);
    if (picked == null) return;
    await ref
        .read(mealPlanControllerProvider.notifier)
        .assign(
          date: day,
          slot: slot,
          dishId: picked.dishId,
          servings: picked.servings,
          dishName: picked.name,
          dishImageUrl: picked.imageUrl,
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

class _MealPlanEmeraldHeader extends StatelessWidget {
  const _MealPlanEmeraldHeader({
    required this.weekLabel,
    required this.dayLabels,
    required this.selectedIndex,
    required this.onPrevWeek,
    required this.onNextWeek,
    required this.onSelectDay,
    this.subtitle,
    this.plan,
  });

  final String weekLabel;
  final String? subtitle;
  final List<String> dayLabels;
  final int selectedIndex;
  final MealPlan? plan;
  final VoidCallback onPrevWeek;
  final VoidCallback onNextWeek;
  final ValueChanged<int> onSelectDay;

  @override
  Widget build(BuildContext context) {
    final l10n = context.l10n;
    final sweep = context.sweep;
    final cs = context.colors;
    final canPop = Navigator.of(context).canPop();

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
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  Row(
                    crossAxisAlignment: CrossAxisAlignment.center,
                    children: [
                      if (canPop)
                        _HeaderIconBtn(
                          icon: AppIcons.arrowLeft,
                          tooltip: 'Quay lại',
                          onPressed: () => Navigator.of(context).maybePop(),
                        ),
                      const Spacer(),
                      // Compact week navigator capsule
                      Container(
                        decoration: BoxDecoration(
                          color: sweep.heroSurfaceElevated,
                          borderRadius: BorderRadius.circular(Radii.pill),
                          border: Border.all(
                            color: sweep.onHeroSurface.withValues(alpha: 0.14),
                          ),
                        ),
                        child: Row(
                          mainAxisSize: MainAxisSize.min,
                          children: [
                            InkWell(
                              borderRadius: BorderRadius.circular(Radii.pill),
                              onTap: onPrevWeek,
                              child: Padding(
                                padding: const EdgeInsets.all(7),
                                child: Icon(
                                  AppIcons.chevronLeft,
                                  size: 15,
                                  color: sweep.onHeroSurface,
                                ),
                              ),
                            ),
                            Text(
                              weekLabel,
                              style: AppTypography.tabular(
                                context.text.labelSmall?.copyWith(
                                  letterSpacing: 0,
                                  color: sweep.onHeroSurface,
                                  fontWeight: FontWeight.w700,
                                ),
                              ),
                            ),
                            InkWell(
                              borderRadius: BorderRadius.circular(Radii.pill),
                              onTap: onNextWeek,
                              child: Padding(
                                padding: const EdgeInsets.all(7),
                                child: Icon(
                                  AppIcons.chevronRight,
                                  size: 15,
                                  color: sweep.onHeroSurface,
                                ),
                              ),
                            ),
                          ],
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: Gap.sm + 2),
                  Row(
                    crossAxisAlignment: CrossAxisAlignment.baseline,
                    textBaseline: TextBaseline.alphabetic,
                    children: [
                      Expanded(
                        child: Text(
                          l10n.mealPlanTitle,
                          maxLines: 1,
                          overflow: TextOverflow.ellipsis,
                          style: context.text.headlineSmall?.copyWith(
                            color: sweep.onHeroSurface,
                            fontWeight: FontWeight.w800,
                          ),
                        ),
                      ),
                      if (subtitle != null) ...[
                        const SizedBox(width: Gap.sm),
                        Text(
                          subtitle!,
                          style: context.text.bodySmall?.copyWith(
                            color: sweep.onHeroMuted,
                            fontWeight: FontWeight.w600,
                          ),
                        ),
                      ],
                    ],
                  ),
                  if (plan != null) ...[
                    Gap.gapMd,
                    _HeroDayStrip(
                      days: plan!.days,
                      dayLabels: dayLabels,
                      selectedIndex: selectedIndex.clamp(
                        0,
                        plan!.days.length - 1,
                      ),
                      plan: plan!,
                      onSelected: onSelectDay,
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

class _HeaderIconBtn extends StatelessWidget {
  const _HeaderIconBtn({
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
          onTap: onPressed,
          child: SizedBox(
            width: 38,
            height: 38,
            child: Icon(icon, size: 18, color: sweep.onHeroSurface),
          ),
        ),
      ),
    );
  }
}

class _HeroDayStrip extends StatelessWidget {
  const _HeroDayStrip({
    required this.days,
    required this.dayLabels,
    required this.selectedIndex,
    required this.plan,
    required this.onSelected,
  });

  final List<DateTime> days;
  final List<String> dayLabels;
  final int selectedIndex;
  final MealPlan plan;
  final ValueChanged<int> onSelected;

  @override
  Widget build(BuildContext context) {
    final sweep = context.sweep;
    final now = DateTime.now();

    return Row(
      children: [
        for (var i = 0; i < days.length; i++)
          Expanded(
            child: Padding(
              padding: EdgeInsets.only(right: i == days.length - 1 ? 0 : 6),
              child: Builder(
                builder: (context) {
                  final d = days[i];
                  final selected = i == selectedIndex;
                  final isToday =
                      d.year == now.year &&
                      d.month == now.month &&
                      d.day == now.day;
                  final plannedCount = MealSlot.values
                      .where((s) => plan.entryAt(d, s) != null)
                      .length;

                  return InkWell(
                    borderRadius: Radii.brMd,
                    onTap: () => onSelected(i),
                    child: AnimatedContainer(
                      duration: AppMotion.resolve(context, context.motion.fast),
                      curve: AppMotion.resolveCurve(
                        context,
                        context.motion.enterCurve,
                      ),
                      padding: const EdgeInsets.symmetric(vertical: Gap.sm),
                      decoration: BoxDecoration(
                        color: selected
                            ? sweep.onHeroSurface
                            : sweep.heroSurfaceElevated,
                        borderRadius: Radii.brMd,
                        border: Border.all(
                          color: selected
                              ? sweep.onHeroSurface
                              : isToday
                              ? sweep.onHeroMuted.withValues(alpha: 0.7)
                              : sweep.onHeroSurface.withValues(alpha: 0.12),
                        ),
                      ),
                      child: Column(
                        mainAxisSize: MainAxisSize.min,
                        children: [
                          Text(
                            dayLabels[i],
                            style: context.text.labelSmall?.copyWith(
                              letterSpacing: 0,
                              color: selected
                                  ? sweep.heroSurface
                                  : sweep.onHeroMuted,
                              fontWeight: FontWeight.w600,
                            ),
                          ),
                          const SizedBox(height: 2),
                          Text(
                            '${d.day}',
                            style: AppTypography.tabular(
                              context.text.titleSmall?.copyWith(
                                color: selected
                                    ? sweep.heroSurface
                                    : sweep.onHeroSurface,
                                fontWeight: FontWeight.w800,
                              ),
                            ),
                          ),
                          const SizedBox(height: 5),
                          SizedBox(
                            height: 6,
                            child: Row(
                              mainAxisAlignment: MainAxisAlignment.center,
                              children: [
                                if (plannedCount == 0)
                                  Container(
                                    width: 4,
                                    height: 4,
                                    decoration: BoxDecoration(
                                      shape: BoxShape.circle,
                                      color:
                                          (selected
                                                  ? sweep.heroSurface
                                                  : sweep.onHeroSurface)
                                              .withValues(alpha: 0.25),
                                    ),
                                  )
                                else
                                  for (
                                    var dot = 0;
                                    dot < plannedCount.clamp(1, 3);
                                    dot++
                                  )
                                    Padding(
                                      padding: const EdgeInsets.symmetric(
                                        horizontal: 1,
                                      ),
                                      child: Container(
                                        width: 5,
                                        height: 5,
                                        decoration: BoxDecoration(
                                          shape: BoxShape.circle,
                                          color: sweep.ctaWarm,
                                        ),
                                      ),
                                    ),
                              ],
                            ),
                          ),
                        ],
                      ),
                    ),
                  );
                },
              ),
            ),
          ),
      ],
    );
  }
}

/// Format 2 — Vertical Culinary Timeline row connecting Sáng → Trưa → Tối → Phụ.
class _TimelineMealRow extends StatelessWidget {
  const _TimelineMealRow({
    required this.slot,
    required this.entry,
    required this.isFirst,
    required this.isLast,
    required this.onTap,
    required this.onClear,
  });

  final MealSlot slot;
  final MealPlanEntry? entry;
  final bool isFirst;
  final bool isLast;
  final VoidCallback onTap;
  final VoidCallback onClear;

  IconData _slotIcon(MealSlot slot) => switch (slot) {
    MealSlot.breakfast => AppIcons.sun,
    MealSlot.lunch => AppIcons.utensils,
    MealSlot.dinner => AppIcons.moon,
    MealSlot.snack => AppIcons.coffee,
  };

  String _slotTimeHint(MealSlot slot) => switch (slot) {
    MealSlot.breakfast => '07:00',
    MealSlot.lunch => '12:00',
    MealSlot.dinner => '18:30',
    MealSlot.snack => 'Phụ',
  };

  @override
  Widget build(BuildContext context) {
    final l10n = context.l10n;
    final sweep = context.sweep;
    final cs = context.colors;
    final filled = entry != null;
    final timeHint = _slotTimeHint(slot);
    final slotHeader = slot == MealSlot.snack
        ? slot.label(l10n).toUpperCase()
        : '${slot.label(l10n).toUpperCase()} · $timeHint';

    return IntrinsicHeight(
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          // Left vertical timeline rail + Lucide meal-slot node
          SizedBox(
            width: 34,
            child: Column(
              children: [
                SizedBox(
                  height: 16,
                  child: isFirst
                      ? null
                      : Center(
                          child: Container(width: 2, color: sweep.hairline),
                        ),
                ),
                Container(
                  width: 32,
                  height: 32,
                  decoration: BoxDecoration(
                    color: filled ? cs.primaryContainer : sweep.subtleFill,
                    shape: BoxShape.circle,
                    border: Border.all(
                      color: filled
                          ? cs.primary.withValues(alpha: 0.35)
                          : sweep.hairline,
                    ),
                  ),
                  child: Icon(
                    _slotIcon(slot),
                    size: 15,
                    color: filled ? cs.primary : sweep.textTertiary,
                  ),
                ),
                Expanded(
                  child: isLast
                      ? const SizedBox.shrink()
                      : Center(
                          child: Container(width: 2, color: sweep.hairline),
                        ),
                ),
              ],
            ),
          ),
          const SizedBox(width: Gap.sm + 2),

          // Right meal slot card
          Expanded(
            child: Padding(
              padding: EdgeInsets.only(bottom: isLast ? 0 : Gap.sm + 4),
              child: TactileCard(
                color: cs.surfaceContainerLowest,
                borderColor: filled
                    ? cs.primary.withValues(alpha: 0.28)
                    : sweep.hairline,
                boxShadow: filled ? Shadows.e1 : null,
                padding: const EdgeInsets.all(Gap.sm + 4),
                onTap: onTap,
                child: Row(
                  children: [
                    if (filled && entry!.dishImageUrl != null) ...[
                      ClipRRect(
                        borderRadius: Radii.brMd,
                        child: SizedBox(
                          width: 52,
                          height: 52,
                          child: RecipeImage(
                            imageUrl: entry!.dishImageUrl,
                            fit: BoxFit.cover,
                            iconSize: 20,
                          ),
                        ),
                      ),
                      const SizedBox(width: Gap.sm + 2),
                    ],
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        mainAxisAlignment: MainAxisAlignment.center,
                        children: [
                          Text(
                            slotHeader,
                            style: context.text.labelSmall?.copyWith(
                              letterSpacing: 0.6,
                              fontWeight: FontWeight.w800,
                              color: filled ? cs.primary : sweep.textTertiary,
                            ),
                          ),
                          const SizedBox(height: 3),
                          Text(
                            filled
                                ? (entry!.dishName ?? l10n.mealSlotChosen)
                                : l10n.mealPlanDayEmpty,
                            style: filled
                                ? context.text.titleSmall?.copyWith(
                                    fontWeight: FontWeight.w700,
                                  )
                                : context.text.bodyMedium?.copyWith(
                                    color: sweep.textTertiary,
                                  ),
                            maxLines: 2,
                            overflow: TextOverflow.ellipsis,
                          ),
                          if (filled) ...[
                            const SizedBox(height: 2),
                            Text(
                              l10n.servingsCount(entry!.servings.round()),
                              style: context.text.bodySmall?.copyWith(
                                color: sweep.textSecondary,
                              ),
                            ),
                          ],
                        ],
                      ),
                    ),
                    const SizedBox(width: Gap.xs),
                    if (filled)
                      IconButton(
                        tooltip: l10n.commonDelete,
                        icon: Icon(
                          AppIcons.close,
                          size: 18,
                          color: sweep.textTertiary,
                        ),
                        onPressed: onClear,
                      )
                    else
                      Container(
                        width: 34,
                        height: 34,
                        decoration: BoxDecoration(
                          color: cs.primaryContainer,
                          shape: BoxShape.circle,
                        ),
                        child: Icon(AppIcons.add, size: 16, color: cs.primary),
                      ),
                  ],
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }
}
