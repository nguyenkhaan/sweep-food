import 'package:flutter/material.dart';
import 'package:sweepfood/app/theme/app_icons.dart';
import 'package:sweepfood/app/theme/app_spacing.dart';
import 'package:sweepfood/app/theme/app_typography.dart';
import 'package:sweepfood/core/utils/extensions/build_context_x.dart';
import 'package:sweepfood/core/widgets/tactile_card.dart';

/// Home pill: "N nguyên liệu · đã dùng trước hạn tháng này".
///
/// Count-based — SweepFood has no money-saved figure. Optional
/// [wasteAvoidedKg] displays the kilograms line.
class WasteSavedPill extends StatelessWidget {
  const WasteSavedPill({
    required this.count,
    this.periodLabel,
    this.wasteAvoidedKg,
    this.onTap,
    super.key,
  });

  final int count;
  final String? periodLabel;
  final double? wasteAvoidedKg;
  final VoidCallback? onTap;

  @override
  Widget build(BuildContext context) {
    final l10n = context.l10n;
    final period = periodLabel ?? l10n.wastePillPeriodThisMonth;

    final inner = Row(
      children: [
        Container(
          width: 36,
          height: 36,
          decoration: BoxDecoration(
            color: context.colors.surface.withValues(alpha: 0.72),
            borderRadius: Radii.brMd,
          ),
          child: Icon(
            AppIcons.leaf,
            size: 18,
            color: context.colors.onPrimaryContainer,
          ),
        ),
        const SizedBox(width: Gap.sm),
        Expanded(
          child: Text.rich(
            TextSpan(
              style: context.text.bodyMedium?.copyWith(
                color: context.colors.onPrimaryContainer,
              ),
              children: [
                TextSpan(
                  text: l10n.wastePillCount(count),
                  style: AppTypography.tabular(
                    const TextStyle(fontWeight: FontWeight.w700),
                  ),
                ),
                TextSpan(
                  text: wasteAvoidedKg != null
                      ? l10n.wastePillUsedBeforeExpiryWithKg(
                          period,
                          wasteAvoidedKg!
                              .toStringAsFixed(1)
                              .replaceAll('.', ','),
                        )
                      : l10n.wastePillUsedBeforeExpiry(period),
                ),
              ],
            ),
          ),
        ),
        if (onTap != null) ...[
          const SizedBox(width: Gap.xs),
          Icon(
            AppIcons.chevronRight,
            size: 18,
            color: context.colors.onPrimaryContainer.withValues(alpha: 0.7),
          ),
        ],
      ],
    );

    if (onTap != null) {
      return TactileCard(
        color: context.colors.primaryContainer,
        borderColor: context.colors.primary.withValues(alpha: 0.16),
        padding: const EdgeInsets.symmetric(
          horizontal: Gap.md,
          vertical: Gap.sm + 2,
        ),
        onTap: onTap,
        child: inner,
      );
    }

    return Container(
      padding: const EdgeInsets.symmetric(
        horizontal: Gap.md,
        vertical: Gap.sm + 2,
      ),
      decoration: BoxDecoration(
        color: context.colors.primaryContainer,
        borderRadius: Radii.brLg,
      ),
      child: inner,
    );
  }
}
