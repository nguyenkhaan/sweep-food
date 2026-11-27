import 'package:flutter/material.dart';
import 'package:sweepfood/app/theme/app_motion.dart';
import 'package:sweepfood/app/theme/app_spacing.dart';
import 'package:sweepfood/features/onboarding/domain/entities/onboarding_state.dart';

/// The segmented progress bar at the top of the onboarding screens (A-05, A-06).
class OnboardingProgress extends StatelessWidget {
  const OnboardingProgress({required this.step, super.key});

  final OnboardingStep step;

  @override
  Widget build(BuildContext context) {
    final scheme = Theme.of(context).colorScheme;
    return Row(
      children: [
        for (var i = 0; i < OnboardingStep.totalBars; i++) ...[
          if (i > 0) const SizedBox(width: Gap.xs),
          Expanded(
            child: AnimatedContainer(
              duration: AppMotion.resolve(
                context,
                AppMotion.of(context).medium,
              ),
              curve: AppMotion.resolveCurve(
                context,
                AppMotion.of(context).enterCurve,
              ),
              height: 5,
              decoration: BoxDecoration(
                color: i < step.stepNumber
                    ? scheme.primary
                    : scheme.outlineVariant,
                borderRadius: BorderRadius.circular(Radii.pill),
              ),
            ),
          ),
        ],
      ],
    );
  }
}
