import 'package:flutter/material.dart';
import 'package:frontend/app/theme/app_spacing.dart';
import 'package:frontend/core/utils/extensions/build_context_x.dart';
import 'package:frontend/features/dishes/domain/entities/cooking_step.dart';

/// Numbered recipe steps (D-01 "Cách làm"). The full-screen immersive mode
/// (D-02) is deferred past the MVP.
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
                  width: 24,
                  height: 24,
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
                      if (step.durationMin != null)
                        Text(
                          '⏱ ${step.durationLabel}',
                          style: context.text.labelSmall?.copyWith(
                            letterSpacing: 0,
                            color: context.sweep.textTertiary,
                          ),
                        ),
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
