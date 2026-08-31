import 'package:flutter/material.dart';
import 'package:frontend/app/theme/app_spacing.dart';
import 'package:frontend/core/utils/extensions/build_context_x.dart';
import 'package:frontend/features/meal_plan/domain/entities/meal_plan_entry.dart';

/// One day×slot cell of the M-01 grid: empty "+ Thêm" or an assigned dish.
class MealSlotCell extends StatelessWidget {
  const MealSlotCell({
    required this.entry,
    required this.onTap,
    this.onClear,
    super.key,
  });

  final MealPlanEntry? entry;
  final VoidCallback onTap;
  final VoidCallback? onClear;

  @override
  Widget build(BuildContext context) {
    final filled = entry != null;
    return InkWell(
      onTap: onTap,
      onLongPress: filled ? onClear : null,
      borderRadius: Radii.brSm,
      child: Container(
        height: 52,
        padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 4),
        decoration: BoxDecoration(
          color: filled
              ? context.colors.primaryContainer
              : context.sweep.subtleFill,
          borderRadius: Radii.brSm,
          border: filled ? null : Border.all(color: context.sweep.hairline),
        ),
        child: Center(
          child: filled
              ? Text(
                  entry!.dishName ?? context.l10n.mealSlotChosen,
                  maxLines: 2,
                  overflow: TextOverflow.ellipsis,
                  textAlign: TextAlign.center,
                  style: context.text.labelSmall?.copyWith(
                    fontWeight: FontWeight.w600,
                    color: context.colors.onPrimaryContainer,
                  ),
                )
              : Text(
                  context.l10n.mealSlotAdd,
                  style: context.text.labelSmall?.copyWith(
                    color: context.sweep.textTertiary,
                  ),
                ),
        ),
      ),
    );
  }
}
