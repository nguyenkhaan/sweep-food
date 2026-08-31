import 'package:flutter/material.dart';
import 'package:frontend/core/utils/extensions/build_context_x.dart';
import 'package:frontend/core/utils/formatters/expiry_text.dart';
import 'package:frontend/shared/domain/expiry_status.dart';

/// Pill showing expiry urgency + relative text ("Còn 1 ngày", "Quá hạn 2 ngày").
/// Colour comes from the theme's [SweepColors] extension — never colour-only,
/// always with text (a11y, spec 3.4).
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

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 9, vertical: 3),
      decoration: BoxDecoration(
        color: c.bg,
        borderRadius: BorderRadius.circular(999),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Container(
            width: 5,
            height: 5,
            decoration: BoxDecoration(color: c.fg, shape: BoxShape.circle),
          ),
          const SizedBox(width: 5),
          Text(
            label,
            style: context.text.labelMedium?.copyWith(
              color: c.fg,
              fontWeight: FontWeight.w600,
              fontSize: 11,
            ),
          ),
        ],
      ),
    );
  }
}
