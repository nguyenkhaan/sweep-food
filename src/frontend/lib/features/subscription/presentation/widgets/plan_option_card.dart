import 'package:flutter/material.dart';
import 'package:sweepfood/app/theme/app_spacing.dart';
import 'package:sweepfood/core/utils/extensions/build_context_x.dart';
import 'package:sweepfood/features/subscription/domain/entities/plan_option.dart';

/// A selectable plan row on the paywall (G-05). Disabled + faded when
/// `plan.comingSoon`.
class PlanOptionCard extends StatelessWidget {
  const PlanOptionCard({
    required this.plan,
    required this.selected,
    required this.onTap,
    super.key,
  });

  final PlanOption plan;
  final bool selected;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    final scheme = context.colors;
    final card = Container(
      padding: const EdgeInsets.all(Gap.md),
      decoration: BoxDecoration(
        color: selected ? scheme.primaryContainer : scheme.surface,
        borderRadius: Radii.brLg,
        border: Border.all(
          color: selected ? scheme.primary : context.sweep.hairline,
          width: selected ? 1.5 : 1,
        ),
      ),
      child: Row(
        children: [
          Icon(
            selected
                ? Icons.radio_button_checked_rounded
                : Icons.radio_button_unchecked_rounded,
            size: 20,
            color: selected ? scheme.primary : context.sweep.textTertiary,
          ),
          Gap.gapSm,
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  children: [
                    Flexible(
                      child: Text(
                        plan.name,
                        style: context.text.titleSmall
                            ?.copyWith(fontWeight: FontWeight.w700),
                      ),
                    ),
                    if (plan.savingLabel != null) ...[
                      Gap.gapXs,
                      Container(
                        padding: const EdgeInsets.symmetric(
                          horizontal: 6,
                          vertical: 1,
                        ),
                        decoration: BoxDecoration(
                          borderRadius: BorderRadius.circular(Radii.pill),
                          border: Border.all(color: scheme.tertiary),
                        ),
                        child: Text(
                          plan.savingLabel!,
                          style: context.text.labelSmall?.copyWith(
                            color: scheme.tertiary,
                            fontWeight: FontWeight.w700,
                          ),
                        ),
                      ),
                    ],
                  ],
                ),
                if (plan.subtitle != null)
                  Text(
                    plan.subtitle!,
                    style: context.text.bodySmall?.copyWith(
                      color: context.sweep.textTertiary,
                    ),
                  ),
              ],
            ),
          ),
          Gap.gapSm,
          Column(
            crossAxisAlignment: CrossAxisAlignment.end,
            children: [
              Text(
                plan.priceLabel,
                style: context.text.titleSmall
                    ?.copyWith(fontWeight: FontWeight.w700),
              ),
              if (plan.periodLabel.isNotEmpty)
                Text(
                  plan.periodLabel,
                  style: context.text.labelSmall?.copyWith(
                    color: context.sweep.textTertiary,
                  ),
                ),
            ],
          ),
        ],
      ),
    );

    if (plan.comingSoon) {
      return Opacity(opacity: 0.55, child: card);
    }
    return InkWell(onTap: onTap, borderRadius: Radii.brLg, child: card);
  }
}
