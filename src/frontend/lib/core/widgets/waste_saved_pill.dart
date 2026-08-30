import 'package:flutter/material.dart';
import 'package:frontend/app/theme/app_spacing.dart';
import 'package:frontend/core/utils/extensions/build_context_x.dart';

/// Home pill: "N nguyên liệu · đã dùng trước hạn tháng này".
///
/// Count-based — SweepFood has **no money-saved figure** (OCR scanning doesn't
/// capture prices). Optional [wasteAvoidedKg] shows the kilograms line.
class WasteSavedPill extends StatelessWidget {
  const WasteSavedPill({
    required this.count,
    this.periodLabel = 'tháng này',
    this.wasteAvoidedKg,
    super.key,
  });

  final int count;
  final String periodLabel;
  final double? wasteAvoidedKg;

  @override
  Widget build(BuildContext context) {
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
                    text: '$count nguyên liệu',
                    style: const TextStyle(fontWeight: FontWeight.w700),
                  ),
                  TextSpan(
                    text: wasteAvoidedKg != null
                        ? '\nđã dùng trước hạn $periodLabel · '
                            '≈ ${wasteAvoidedKg!.toStringAsFixed(1).replaceAll('.', ',')} kg tránh bỏ phí'
                        : '\nđã dùng trước hạn $periodLabel',
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
