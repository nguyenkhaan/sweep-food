import 'package:flutter/material.dart';
import 'package:sweepfood/app/theme/app_icons.dart';
import 'package:sweepfood/app/theme/app_spacing.dart';
import 'package:sweepfood/app/theme/app_typography.dart';
import 'package:sweepfood/core/utils/extensions/build_context_x.dart';
import 'package:sweepfood/core/utils/formatters/expiry_text.dart';
import 'package:sweepfood/shared/domain/expiry_status.dart';

/// Pill showing expiry urgency + relative text ("Còn 1 ngày", "Quá hạn 2 ngày").
/// Never color-only: always pairs semantic tint with urgency icon + text label.
class ExpiryBadge extends StatelessWidget {
  const ExpiryBadge({required this.daysUntilExpiry, super.key})
    : level = null,
      text = null;

  const ExpiryBadge.custom({
    required ExpiryLevel this.level,
    required String this.text,
    super.key,
  }) : daysUntilExpiry = null;

  final int? daysUntilExpiry;
  final ExpiryLevel? level;
  final String? text;

  @override
  Widget build(BuildContext context) {
    final lvl = level ?? Expiry.levelFromDays(daysUntilExpiry);
    final label = text ?? expiryText(daysUntilExpiry, context.l10n);
    final c = context.sweep.expiry(lvl);

    final icon = switch (lvl) {
      ExpiryLevel.expired => AppIcons.warning,
      ExpiryLevel.critical => AppIcons.flame,
      ExpiryLevel.soon => AppIcons.clock,
      ExpiryLevel.ok => AppIcons.checkCircle,
    };

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: Gap.xs + 2, vertical: 3),
      decoration: BoxDecoration(
        color: c.bg,
        borderRadius: BorderRadius.circular(Radii.pill),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(icon, size: 11, color: c.fg),
          const SizedBox(width: 4),
          Text(
            label,
            style: AppTypography.tabular(
              context.text.labelMedium?.copyWith(
                color: c.fg,
                fontWeight: FontWeight.w700,
                fontSize: 11,
              ),
            ),
          ),
        ],
      ),
    );
  }
}
