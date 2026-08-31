// lib/core/widgets/confidence_field.dart
// Read-only field card used on the OCR review screens (I-03 / I-05).

import 'package:flutter/material.dart';
import 'package:sweepfood/app/theme/app_colors.dart';
import 'package:sweepfood/app/theme/app_spacing.dart';
import 'package:sweepfood/core/utils/extensions/build_context_x.dart';

/// A labeled value the user taps to edit. When [needsReview] is set the border
/// turns amber and a "cần kiểm tra" chip appears next to the label — the signal
/// that the OCR / ASR filled this field with low confidence.
class ConfidenceField extends StatelessWidget {
  const ConfidenceField({
    required this.label,
    required this.value,
    this.onTap,
    this.needsReview = false,
    this.reviewLabel,
    this.trailingIcon = Icons.edit_outlined,
    super.key,
  });

  final String label;
  final String value;
  final VoidCallback? onTap;
  final bool needsReview;

  /// Defaults to the localized "check this" chip when null.
  final String? reviewLabel;
  final IconData trailingIcon;

  @override
  Widget build(BuildContext context) {
    final sweep = context.sweep;

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          children: [
            Text(
              label,
              style: context.text.labelMedium?.copyWith(
                fontWeight: FontWeight.w600,
                color: sweep.textSecondary,
              ),
            ),
            if (needsReview) ...[
              const SizedBox(width: Gap.xs),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 7, vertical: 2),
                decoration: BoxDecoration(
                  color: BrandPalette.warnSoon.withValues(alpha: 0.15),
                  borderRadius: BorderRadius.circular(999),
                ),
                child: Text(
                  reviewLabel ?? context.l10n.confidenceNeedsReview,
                  style: const TextStyle(
                    color: BrandPalette.warnSoon,
                    fontSize: 10,
                    fontWeight: FontWeight.w700,
                  ),
                ),
              ),
            ],
          ],
        ),
        const SizedBox(height: 6),
        Material(
          color: context.colors.surface,
          borderRadius: Radii.brMd,
          child: InkWell(
            onTap: onTap,
            borderRadius: Radii.brMd,
            child: Container(
              height: 46,
              padding: const EdgeInsets.symmetric(horizontal: Gap.md),
              decoration: BoxDecoration(
                borderRadius: Radii.brMd,
                border: Border.all(
                  color: needsReview ? BrandPalette.warnSoon : sweep.hairline,
                  width: needsReview ? 2 : 1,
                ),
              ),
              child: Row(
                children: [
                  Expanded(
                    child: Text(
                      value,
                      style: context.text.bodyMedium?.copyWith(
                        fontWeight: FontWeight.w500,
                      ),
                      maxLines: 1,
                      overflow: TextOverflow.ellipsis,
                    ),
                  ),
                  if (onTap != null)
                    Icon(trailingIcon, size: 16, color: sweep.textTertiary),
                ],
              ),
            ),
          ),
        ),
      ],
    );
  }
}
