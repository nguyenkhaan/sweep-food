import 'package:flutter/material.dart';
import 'package:frontend/app/theme/app_spacing.dart';
import 'package:frontend/features/onboarding/domain/entities/onboarding_state.dart';

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
            child: Container(
              height: 4,
              decoration: BoxDecoration(
                color: i < step.stepNumber
                    ? scheme.primary
                    : scheme.outlineVariant,
                borderRadius: Radii.brSm,
              ),
            ),
          ),
        ],
      ],
    );
  }
}
