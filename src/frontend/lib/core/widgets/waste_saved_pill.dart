import 'package:flutter/material.dart';
import 'package:sweepfood/app/theme/app_spacing.dart';
import 'package:sweepfood/core/utils/extensions/build_context_x.dart';

/// Home pill: "N nguyên liệu · đã dùng trước hạn tháng này".
///
/// Count-based — SweepFood has **no money-saved figure** (OCR scanning doesn't
/// capture prices). Optional [wasteAvoidedKg] shows the kilograms line.
class WasteSavedPill extends StatelessWidget {
  const WasteSavedPill({
    required this.count,
    this.periodLabel,
    this.wasteAvoidedKg,
    super.key,
  });

  final int count;

  /// Defaults to the localized "this month" when null.
  final String? periodLabel;
  final double? wasteAvoidedKg;

  @override
  Widget build(BuildContext context) {
    final l10n = context.l10n;
    final period = periodLabel ?? l10n.wastePillPeriodThisMonth;
    return Container(
      padding: const EdgeInsets.all(Gap.sm + 2),
      decoration: BoxDecoration(
        color: context.colors.primaryContainer,
        borderRadius: Radii.brLg,
      ),
      child: Row(
        children: [
          Container(
            width: 30,
            height: 30,
            decoration: BoxDecoration(
              color: context.colors.surface.withValues(alpha: 0.5),
              borderRadius: Radii.brSm,
            ),
            child: Icon(
              Icons.eco_rounded,
              size: 16,
              color: context.colors.onPrimaryContainer,
            ),
          ),
          const SizedBox(width: Gap.xs),
          Expanded(
            child: Text.rich(
              TextSpan(
                style: context.text.bodyMedium?.copyWith(
                  color: context.colors.onPrimaryContainer,
                ),
                children: [
                  TextSpan(
                    text: l10n.wastePillCount(count),
                    style: const TextStyle(fontWeight: FontWeight.w700),
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
        ],
      ),
    );
  }
}
