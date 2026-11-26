import 'package:flutter/material.dart';
import 'package:sweepfood/app/theme/app_spacing.dart';
import 'package:sweepfood/core/utils/extensions/build_context_x.dart';

/// Persistent medical/nutrition reference disclaimer required across nutrition
/// profile and suggestion surfaces.
class NutritionDisclaimerBanner extends StatelessWidget {
  const NutritionDisclaimerBanner({this.compact = false, super.key});

  final bool compact;

  @override
  Widget build(BuildContext context) {
    final textColor = context.sweep.textSecondary;
    return Semantics(
      container: true,
      child: Container(
        width: double.infinity,
        padding: EdgeInsets.symmetric(
          horizontal: compact ? Gap.sm : Gap.md,
          vertical: compact ? Gap.xs : Gap.sm,
        ),
        decoration: BoxDecoration(
          color: context.sweep.subtleFill,
          borderRadius: Radii.brMd,
          border: Border.all(color: context.sweep.hairline),
        ),
        child: Row(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Icon(
              Icons.info_outline_rounded,
              size: compact ? 15 : 17,
              color: textColor,
            ),
            const SizedBox(width: Gap.xs),
            Expanded(
              child: Text(
                context.l10n.nutritionDisclaimer,
                style:
                    (compact ? context.text.labelSmall : context.text.bodySmall)
                        ?.copyWith(
                          color: textColor,
                          letterSpacing: 0,
                          height: 1.35,
                        ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
