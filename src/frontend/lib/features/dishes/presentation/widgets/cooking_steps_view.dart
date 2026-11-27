import 'package:flutter/material.dart';
import 'package:sweepfood/app/theme/app_icons.dart';
import 'package:sweepfood/app/theme/app_spacing.dart';
import 'package:sweepfood/core/utils/extensions/build_context_x.dart';
import 'package:sweepfood/features/dishes/domain/entities/cooking_step.dart';

/// Numbered recipe steps (D-01 "Cách làm").
class CookingStepsView extends StatelessWidget {
  const CookingStepsView({required this.steps, super.key});

  final List<CookingStep> steps;

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        for (final step in steps)
          Padding(
            padding: const EdgeInsets.symmetric(vertical: Gap.xs),
            child: Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Container(
                  width: 26,
                  height: 26,
                  alignment: Alignment.center,
                  decoration: BoxDecoration(
                    color: context.colors.primary,
                    shape: BoxShape.circle,
                  ),
                  child: Text(
                    '${step.order}',
                    style: context.text.labelSmall?.copyWith(
                      letterSpacing: 0,
                      color: context.colors.onPrimary,
                      fontWeight: FontWeight.w700,
                    ),
                  ),
                ),
                const SizedBox(width: Gap.sm),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        step.text,
                        style: context.text.bodyMedium?.copyWith(
                          color: context.sweep.textSecondary,
                          height: 1.5,
                        ),
                      ),
                      if (step.durationMin != null) ...[
                        const SizedBox(height: 4),
                        Container(
                          padding: const EdgeInsets.symmetric(
                            horizontal: Gap.xs,
                            vertical: 2,
                          ),
                          decoration: BoxDecoration(
                            color: context.sweep.culinaryAccentBg,
                            borderRadius: BorderRadius.circular(Radii.pill),
                          ),
                          child: Row(
                            mainAxisSize: MainAxisSize.min,
                            children: [
                              Icon(
                                AppIcons.timer,
                                size: 12,
                                color: context.sweep.onCulinaryAccentBg,
                              ),
                              const SizedBox(width: 4),
                              Text(
                                step.durationLabel(context.l10n),
                                style: context.text.labelSmall?.copyWith(
                                  letterSpacing: 0,
                                  color: context.sweep.onCulinaryAccentBg,
                                ),
                              ),
                            ],
                          ),
                        ),
                      ],
                    ],
                  ),
                ),
              ],
            ),
          ),
      ],
    );
  }
}
