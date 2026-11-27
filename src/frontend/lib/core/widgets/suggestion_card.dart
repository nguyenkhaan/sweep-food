import 'package:flutter/material.dart';
import 'package:sweepfood/app/theme/app_icons.dart';
import 'package:sweepfood/app/theme/app_motion.dart';
import 'package:sweepfood/app/theme/app_spacing.dart';
import 'package:sweepfood/app/theme/app_typography.dart';
import 'package:sweepfood/core/utils/extensions/build_context_x.dart';
import 'package:sweepfood/core/widgets/recipe_image.dart';
import 'package:sweepfood/core/widgets/tactile_card.dart';

/// A coloured chip under a suggestion ("Dùng 3 đồ cận hạn", "Đủ nấu ngay"…).
enum SuggestionChipTone { nearExpiry, available, toBuy }

typedef SuggestionChip = ({String label, SuggestionChipTone tone});

/// Editorial dish suggestion card (S-01, H-01 quick suggestions).
class SuggestionCard extends StatelessWidget {
  const SuggestionCard({
    required this.title,
    required this.score,
    required this.meta,
    required this.chips,
    this.fitReasons = const [],
    this.rank,
    this.imageUrl,
    this.heroTag,
    this.onTap,
    this.onScoreTap,
    super.key,
  });

  final String title;
  final int score;
  final int? rank;
  final String meta;
  final List<SuggestionChip> chips;
  final List<String> fitReasons;
  final String? imageUrl;
  final Object? heroTag;
  final VoidCallback? onTap;
  final VoidCallback? onScoreTap;

  @override
  Widget build(BuildContext context) {
    return TactileCard(
      boxShadow: Shadows.e1,
      onTap: onTap,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          SizedBox(
            height: 158,
            child: Stack(
              children: [
                Positioned.fill(
                  child: RecipeImage(
                    imageUrl: imageUrl,
                    fit: BoxFit.cover,
                    heroTag: heroTag,
                  ),
                ),
                // Bottom gradient scrim for image depth & badge legibility
                Positioned.fill(
                  child: IgnorePointer(
                    child: DecoratedBox(
                      decoration: BoxDecoration(
                        gradient: LinearGradient(
                          begin: Alignment.topCenter,
                          end: Alignment.bottomCenter,
                          colors: [
                            Colors.black.withValues(alpha: 0.14),
                            Colors.transparent,
                            Colors.black.withValues(alpha: 0.36),
                          ],
                          stops: const [0.0, 0.45, 1.0],
                        ),
                      ),
                    ),
                  ),
                ),
                if (rank != null)
                  Positioned(
                    top: Gap.sm,
                    left: Gap.sm,
                    child: Container(
                      padding: const EdgeInsets.symmetric(
                        horizontal: 10,
                        vertical: 5,
                      ),
                      decoration: BoxDecoration(
                        color: rank == 1
                            ? context.sweep.ctaWarm
                            : context.colors.surfaceContainerLowest.withValues(
                                alpha: 0.94,
                              ),
                        borderRadius: BorderRadius.circular(Radii.pill),
                        boxShadow: Shadows.e1,
                      ),
                      child: Text(
                        '#$rank',
                        style: AppTypography.tabular(
                          context.text.labelLarge?.copyWith(
                            color: rank == 1
                                ? context.sweep.onCtaWarm
                                : context.colors.primary,
                            fontWeight: FontWeight.w800,
                          ),
                        ),
                      ),
                    ),
                  ),
                Positioned(
                  top: Gap.sm,
                  right: Gap.sm,
                  child: _ScoreBadge(score: score, onTap: onScoreTap),
                ),
              ],
            ),
          ),
          Padding(
            padding: const EdgeInsets.all(Gap.md),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  title,
                  style: context.text.headlineSmall?.copyWith(
                    fontSize: 19,
                    height: 1.24,
                  ),
                ),
                const SizedBox(height: 4),
                Text(
                  meta,
                  style: context.text.bodySmall?.copyWith(
                    color: context.sweep.textTertiary,
                  ),
                ),
                const SizedBox(height: Gap.sm),
                Wrap(
                  spacing: 6,
                  runSpacing: 6,
                  children: [for (final c in chips) _Chip(chip: c)],
                ),
                if (fitReasons.isNotEmpty) ...[
                  const SizedBox(height: Gap.sm),
                  Divider(height: 1, color: context.sweep.hairline),
                  const SizedBox(height: Gap.xs + 2),
                  _FitReasonsPreview(reasons: fitReasons.take(3).toList()),
                ],
                if (onScoreTap != null) ...[
                  const SizedBox(height: Gap.xs),
                  Align(
                    alignment: AlignmentDirectional.centerEnd,
                    child: TextButton.icon(
                      style: TextButton.styleFrom(
                        visualDensity: VisualDensity.compact,
                        padding: const EdgeInsets.symmetric(
                          horizontal: Gap.xs,
                          vertical: 4,
                        ),
                      ),
                      onPressed: () {
                        AppHaptics.selection();
                        onScoreTap!();
                      },
                      icon: const Icon(AppIcons.info, size: 15),
                      label: Text(context.l10n.suggestionsWhyScore),
                    ),
                  ),
                ],
              ],
            ),
          ),
        ],
      ),
    );
  }
}

class _FitReasonsPreview extends StatelessWidget {
  const _FitReasonsPreview({required this.reasons});

  final List<String> reasons;

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        for (var i = 0; i < reasons.length; i++) ...[
          if (i > 0) const SizedBox(height: Gap.xxs),
          Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Padding(
                padding: const EdgeInsets.only(top: 2),
                child: Icon(
                  AppIcons.checkCircle,
                  size: 14,
                  color: context.colors.primary,
                ),
              ),
              const SizedBox(width: 6),
              Expanded(
                child: Text(
                  reasons[i],
                  maxLines: 2,
                  overflow: TextOverflow.ellipsis,
                  style: context.text.bodySmall?.copyWith(
                    color: context.sweep.textSecondary,
                    height: 1.35,
                  ),
                ),
              ),
            ],
          ),
        ],
      ],
    );
  }
}

class _ScoreBadge extends StatelessWidget {
  const _ScoreBadge({required this.score, this.onTap});

  final int score;
  final VoidCallback? onTap;

  @override
  Widget build(BuildContext context) {
    final pill = Container(
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
      decoration: BoxDecoration(
        color: context.sweep.heroSurface,
        borderRadius: BorderRadius.circular(Radii.pill),
        boxShadow: Shadows.e1,
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Text(
            '$score',
            style: AppTypography.tabular(
              context.text.titleSmall?.copyWith(
                color: context.sweep.onHeroSurface,
                fontWeight: FontWeight.w800,
                height: 1,
              ),
            ),
          ),
          const SizedBox(width: 3),
          Text(
            context.l10n.scoreBadgeLabel,
            style: context.text.labelSmall?.copyWith(
              color: context.sweep.onHeroMuted,
              fontSize: 9,
              letterSpacing: 0.4,
            ),
          ),
        ],
      ),
    );

    if (onTap == null) return pill;
    return Semantics(
      button: true,
      label: context.l10n.suggestionsWhyScore,
      child: InkWell(
        onTap: () {
          AppHaptics.selection();
          onTap!();
        },
        borderRadius: BorderRadius.circular(Radii.pill),
        child: pill,
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
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
      decoration: BoxDecoration(
        color: bg,
        borderRadius: BorderRadius.circular(Radii.pill),
      ),
      child: Text(
        chip.label,
        style: context.text.labelSmall?.copyWith(
          letterSpacing: 0,
          color: fg,
          fontWeight: FontWeight.w600,
        ),
      ),
    );
  }
}
