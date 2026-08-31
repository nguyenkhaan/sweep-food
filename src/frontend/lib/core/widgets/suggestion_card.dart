import 'package:flutter/material.dart';
import 'package:frontend/app/theme/app_spacing.dart';
import 'package:frontend/core/utils/extensions/build_context_x.dart';

/// A coloured chip under a suggestion ("Dùng 3 đồ cận hạn", "Có sẵn 80%"…).
enum SuggestionChipTone { nearExpiry, available, toBuy }

typedef SuggestionChip = ({String label, SuggestionChipTone tone});

/// Dish suggestion card (S-01, H-01 quick suggestions).
///
/// Primitive params — M3 maps a `DishSuggestion` → these.
class SuggestionCard extends StatelessWidget {
  const SuggestionCard({
    required this.title,
    required this.score,
    required this.meta,
    required this.chips,
    this.imageUrl,
    this.onTap,
    super.key,
  });

  final String title;

  /// 0–100 match score.
  final int score;

  /// e.g. "15 phút · Dễ · 320 kcal / khẩu phần".
  final String meta;
  final List<SuggestionChip> chips;
  final String? imageUrl;
  final VoidCallback? onTap;

  @override
  Widget build(BuildContext context) {
    return Material(
      color: context.colors.surfaceContainerLowest,
      borderRadius: Radii.brLg,
      clipBehavior: Clip.antiAlias,
      child: InkWell(
        onTap: onTap,
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            SizedBox(
              height: 130,
              child: Stack(
                children: [
                  Positioned.fill(
                    child: ColoredBox(
                      color: context.sweep.subtleFill,
                      child: imageUrl == null
                          ? Icon(
                              Icons.restaurant_rounded,
                              size: 34,
                              color: context.sweep.textTertiary,
                            )
                          : Image.network(imageUrl!, fit: BoxFit.cover),
                    ),
                  ),
                  Positioned(
                    top: 12,
                    right: 12,
                    child: _ScoreBadge(score: score),
                  ),
                ],
              ),
            ),
            Padding(
              padding: const EdgeInsets.all(Gap.sm + 2),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(title, style: context.text.titleMedium),
                  const SizedBox(height: 3),
                  Text(
                    meta,
                    style: context.text.bodyMedium?.copyWith(
                      color: context.sweep.textTertiary,
                      fontSize: 12,
                    ),
                  ),
                  const SizedBox(height: Gap.xs),
                  Wrap(
                    spacing: 6,
                    runSpacing: 6,
                    children: [for (final c in chips) _Chip(chip: c)],
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _ScoreBadge extends StatelessWidget {
  const _ScoreBadge({required this.score});
  final int score;

  @override
  Widget build(BuildContext context) {
    return Container(
      width: 42,
      height: 42,
      alignment: Alignment.center,
      decoration: BoxDecoration(
        color: context.colors.primary,
        shape: BoxShape.circle,
        boxShadow: Shadows.e2,
      ),
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Text(
            '$score',
            style: context.text.titleSmall?.copyWith(
              color: context.colors.onPrimary,
              fontSize: 15,
              height: 1,
            ),
          ),
          Text(
            context.l10n.scoreBadgeLabel,
            style: TextStyle(
              color: context.colors.onPrimary.withValues(alpha: 0.85),
              fontSize: 7,
              fontWeight: FontWeight.w600,
              letterSpacing: 0.4,
            ),
          ),
        ],
      ),
    );
  }
}

class _Chip extends StatelessWidget {
  const _Chip({required this.chip});
  final SuggestionChip chip;

  @override
  Widget build(BuildContext context) {
    final (bg, fg) = switch (chip.tone) {
      SuggestionChipTone.nearExpiry => (
        context.sweep.expired.bg,
        context.sweep.expired.fg,
      ),
      SuggestionChipTone.available => (
        context.colors.primaryContainer,
        context.colors.onPrimaryContainer,
      ),
      SuggestionChipTone.toBuy => (
        context.sweep.subtleFill,
        context.sweep.textSecondary,
      ),
    };
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 9, vertical: 3),
      decoration: BoxDecoration(
        color: bg,
        borderRadius: BorderRadius.circular(999),
      ),
      child: Text(
        chip.label,
        style: context.text.labelSmall?.copyWith(letterSpacing: 0, color: fg),
      ),
    );
  }
}
