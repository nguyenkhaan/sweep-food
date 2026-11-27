import 'package:flutter/material.dart';
import 'package:flutter/physics.dart';
import 'package:go_router/go_router.dart';
import 'package:sweepfood/app/router/routes.dart';
import 'package:sweepfood/app/theme/app_icons.dart';
import 'package:sweepfood/app/theme/app_motion.dart';
import 'package:sweepfood/app/theme/app_spacing.dart';
import 'package:sweepfood/app/theme/app_typography.dart';
import 'package:sweepfood/core/utils/extensions/build_context_x.dart';
import 'package:sweepfood/core/widgets/emerald_split_header.dart';
import 'package:sweepfood/core/widgets/staggered_reveal.dart';
import 'package:sweepfood/features/cooking/domain/entities/cook_result.dart';
import 'package:sweepfood/features/cooking/presentation/widgets/leftover_save_sheet.dart';

/// D-05 / D-07 — "Đã cập nhật kho" (Concept B · Format 1: Emerald Celebration
/// Hero with spring checkmark, near-expiry rescue badge, cascaded stock diff
/// card, leftover shortcut, and sticky flat warm-orange Done CTA).
class CookResultScreen extends StatefulWidget {
  const CookResultScreen({required this.result, super.key});

  final CookResult result;

  @override
  State<CookResultScreen> createState() => _CookResultScreenState();
}

class _CookResultScreenState extends State<CookResultScreen>
    with SingleTickerProviderStateMixin {
  late final AnimationController _badgeSpring;

  @override
  void initState() {
    super.initState();
    _badgeSpring = AnimationController.unbounded(vsync: this, value: 0.55);
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (!mounted) return;
      if (MediaQuery.disableAnimationsOf(context)) {
        _badgeSpring.value = 1.0;
        return;
      }
      AppHaptics.medium();
      _badgeSpring.animateWith(
        SpringSimulation(
          const SpringDescription(mass: 1.0, stiffness: 220.0, damping: 14.0),
          0.55,
          1.0,
          2.2,
        ),
      );
    });
  }

  @override
  void dispose() {
    _badgeSpring.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final l10n = context.l10n;
    final sweep = context.sweep;
    final cs = context.colors;
    final result = widget.result;

    return EmeraldSystemOverlay(
      child: Scaffold(
        backgroundColor: cs.surface,
        body: Column(
          children: [
            _CookResultEmeraldHero(
              result: result,
              badgeScale: _badgeSpring,
            ),
            Expanded(
              child: ListView(
                padding: const EdgeInsets.fromLTRB(
                  Gap.lg,
                  Gap.xs,
                  Gap.lg,
                  Gap.xxl,
                ),
                children: [
                  StaggeredReveal(index: 0, child: _ChangesCard(result: result)),
                  Gap.gapMd,
                  StaggeredReveal(
                    index: 1,
                    child: Material(
                      color: cs.primaryContainer.withValues(alpha: 0.45),
                      shape: RoundedRectangleBorder(
                        borderRadius: Radii.brLg,
                        side: BorderSide(
                          color: cs.primary.withValues(alpha: 0.35),
                        ),
                      ),
                      child: InkWell(
                        borderRadius: Radii.brLg,
                        onTap: () {
                          AppHaptics.selection();
                          LeftoverSaveSheet.show(
                            context,
                            sessionId: result.sessionId,
                            dishName: result.dishName,
                            initialServings: 1,
                          );
                        },
                        child: Padding(
                          padding: const EdgeInsets.symmetric(
                            horizontal: Gap.md,
                            vertical: Gap.sm + 4,
                          ),
                          child: Row(
                            mainAxisAlignment: MainAxisAlignment.center,
                            children: [
                              Icon(
                                AppIcons.packagePlus,
                                size: 18,
                                color: cs.primary,
                              ),
                              const SizedBox(width: Gap.sm),
                              Flexible(
                                child: Text(
                                  l10n.cookResultSaveLeftovers,
                                  maxLines: 1,
                                  overflow: TextOverflow.ellipsis,
                                  style: context.text.labelLarge?.copyWith(
                                    color: cs.primary,
                                    fontWeight: FontWeight.w700,
                                  ),
                                ),
                              ),
                            ],
                          ),
                        ),
                      ),
                    ),
                  ),
                ],
              ),
            ),
          ],
        ),
        bottomNavigationBar: SafeArea(
          child: Container(
            padding: const EdgeInsets.fromLTRB(Gap.lg, Gap.sm, Gap.lg, Gap.md),
            decoration: BoxDecoration(
              color: cs.surfaceContainerLowest,
              border: Border(top: BorderSide(color: sweep.hairline)),
            ),
            child: Row(
              children: [
                Expanded(
                  child: SizedBox(
                    height: 48,
                    child: OutlinedButton(
                      style: OutlinedButton.styleFrom(
                        side: BorderSide(color: sweep.hairline),
                        shape: const RoundedRectangleBorder(
                          borderRadius: Radii.brMd,
                        ),
                      ),
                      onPressed: () => context.go(Routes.pantry),
                      child: Text(
                        l10n.cookResultViewPantry,
                        maxLines: 1,
                        overflow: TextOverflow.ellipsis,
                      ),
                    ),
                  ),
                ),
                const SizedBox(width: Gap.sm),
                Expanded(
                  child: SizedBox(
                    height: 48,
                    child: FilledButton(
                      style: FilledButton.styleFrom(
                        backgroundColor: sweep.ctaWarm,
                        foregroundColor: sweep.onCtaWarm,
                        shape: const RoundedRectangleBorder(
                          borderRadius: Radii.brMd,
                        ),
                      ),
                      onPressed: () => context.go(Routes.suggestions),
                      child: Text(
                        l10n.commonDone,
                        maxLines: 1,
                        overflow: TextOverflow.ellipsis,
                        style: const TextStyle(fontWeight: FontWeight.w700),
                      ),
                    ),
                  ),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}

class _CookResultEmeraldHero extends StatelessWidget {
  const _CookResultEmeraldHero({
    required this.result,
    required this.badgeScale,
  });

  final CookResult result;
  final Animation<double> badgeScale;

  @override
  Widget build(BuildContext context) {
    final l10n = context.l10n;
    final sweep = context.sweep;
    final cs = context.colors;
    final kg = result.wasteAvoidedKg;
    final kgText = kg > 0
        ? l10n.cookResultWasteKgSuffix(
            kg.toStringAsFixed(1).replaceAll('.', ','),
          )
        : '';

    return DecoratedBox(
      decoration: BoxDecoration(color: sweep.heroSurface),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          SafeArea(
            bottom: false,
            child: Padding(
              padding: const EdgeInsets.fromLTRB(
                Gap.lg,
                Gap.lg,
                Gap.lg,
                Gap.md,
              ),
              child: Column(
                children: [
                  AnimatedBuilder(
                    animation: badgeScale,
                    builder: (_, child) => Transform.scale(
                      scale: badgeScale.value.clamp(0.4, 1.25),
                      child: child,
                    ),
                    child: Container(
                      width: 64,
                      height: 64,
                      decoration: BoxDecoration(
                        color: sweep.heroSurfaceElevated,
                        shape: BoxShape.circle,
                        border: Border.all(
                          color: sweep.onHeroSurface.withValues(alpha: 0.28),
                          width: 2,
                        ),
                      ),
                      child: Icon(
                        AppIcons.check,
                        size: 30,
                        color: sweep.onHeroSurface,
                      ),
                    ),
                  ),
                  const SizedBox(height: Gap.sm + 2),
                  Text(
                    l10n.cookResultTitle,
                    textAlign: TextAlign.center,
                    style: context.text.headlineSmall?.copyWith(
                      color: sweep.onHeroSurface,
                      fontWeight: FontWeight.w800,
                    ),
                  ),
                  if (result.dishName.trim().isNotEmpty) ...[
                    const SizedBox(height: 4),
                    Text(
                      result.dishName,
                      maxLines: 1,
                      overflow: TextOverflow.ellipsis,
                      textAlign: TextAlign.center,
                      style: context.text.bodySmall?.copyWith(
                        color: sweep.onHeroMuted,
                      ),
                    ),
                  ],
                  if (result.nearExpiryUsedCount > 0) ...[
                    const SizedBox(height: Gap.sm + 2),
                    Container(
                      padding: const EdgeInsets.symmetric(
                        horizontal: 12,
                        vertical: 6,
                      ),
                      decoration: BoxDecoration(
                        color: sweep.ctaWarm,
                        borderRadius: BorderRadius.circular(Radii.pill),
                      ),
                      child: Row(
                        mainAxisSize: MainAxisSize.min,
                        children: [
                          Icon(
                            AppIcons.trendingUp,
                            size: 14,
                            color: sweep.onCtaWarm,
                          ),
                          const SizedBox(width: 6),
                          Flexible(
                            child: Text(
                              '${l10n.cookResultUsedNearExpiryPrefix}'
                              '${l10n.cookResultUsedNearExpiryCount(result.nearExpiryUsedCount)}'
                              '$kgText',
                              maxLines: 2,
                              overflow: TextOverflow.ellipsis,
                              style: context.text.labelMedium?.copyWith(
                                color: sweep.onCtaWarm,
                                fontWeight: FontWeight.w700,
                              ),
                            ),
                          ),
                        ],
                      ),
                    ),
                  ],
                ],
              ),
            ),
          ),
          Container(
            height: 20,
            decoration: BoxDecoration(
              color: cs.surface,
              borderRadius: const BorderRadius.vertical(
                top: Radius.circular(26),
              ),
            ),
          ),
        ],
      ),
    );
  }
}

class _ChangesCard extends StatelessWidget {
  const _ChangesCard({required this.result});

  final CookResult result;

  @override
  Widget build(BuildContext context) {
    final l10n = context.l10n;
    final sweep = context.sweep;
    final cs = context.colors;

    return Container(
      decoration: BoxDecoration(
        color: cs.surfaceContainerLowest,
        borderRadius: Radii.brXl,
        border: Border.all(color: sweep.hairline),
        boxShadow: Shadows.e1,
      ),
      clipBehavior: Clip.antiAlias,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          Padding(
            padding: const EdgeInsets.fromLTRB(Gap.md, Gap.md, Gap.md, Gap.xs),
            child: Text(
              l10n.cookResultChangesHeader.toUpperCase(),
              style: context.text.labelSmall?.copyWith(
                letterSpacing: 0.7,
                fontWeight: FontWeight.w800,
                color: sweep.textTertiary,
              ),
            ),
          ),
          for (final (i, c) in result.changes.indexed) ...[
            StaggeredReveal(
              index: i + 1,
              child: Padding(
                padding: const EdgeInsets.symmetric(
                  horizontal: Gap.md,
                  vertical: Gap.sm + 2,
                ),
                child: Row(
                  children: [
                    Expanded(
                      child: Text(
                        c.name,
                        style: context.text.bodyMedium?.copyWith(
                          fontWeight: FontWeight.w700,
                        ),
                      ),
                    ),
                    Text(
                      c.beforeLabel,
                      style: AppTypography.tabular(
                        context.text.bodySmall?.copyWith(
                          color: sweep.textTertiary,
                          decoration: TextDecoration.lineThrough,
                        ),
                      ),
                    ),
                    Padding(
                      padding: const EdgeInsets.symmetric(horizontal: 6),
                      child: Icon(
                        AppIcons.arrowRight,
                        size: 13,
                        color: sweep.textTertiary,
                      ),
                    ),
                    Text(
                      c.afterLabel,
                      style: AppTypography.tabular(
                        context.text.bodyMedium?.copyWith(
                          fontWeight: FontWeight.w800,
                          color: c.afterLabel.startsWith('0')
                              ? sweep.ctaWarm
                              : cs.primary,
                        ),
                      ),
                    ),
                  ],
                ),
              ),
            ),
            if (i < result.changes.length - 1)
              Divider(height: 1, indent: Gap.md, color: sweep.hairline),
          ],
          if (result.lowStockNames.isNotEmpty)
            Padding(
              padding: const EdgeInsets.fromLTRB(
                Gap.md,
                Gap.xs,
                Gap.md,
                Gap.md,
              ),
              child: Container(
                padding: const EdgeInsets.symmetric(
                  horizontal: Gap.sm + 2,
                  vertical: Gap.xs + 2,
                ),
                decoration: BoxDecoration(
                  color: sweep.soon.bg,
                  borderRadius: Radii.brMd,
                  border: Border.all(
                    color: sweep.soon.fg.withValues(alpha: 0.25),
                  ),
                ),
                child: Row(
                  children: [
                    Icon(AppIcons.warning, size: 15, color: sweep.soon.fg),
                    const SizedBox(width: Gap.xs + 2),
                    Expanded(
                      child: Text(
                        l10n.cookResultLowStock(
                          result.lowStockNames.join(', '),
                        ),
                        style: context.text.labelMedium?.copyWith(
                          color: sweep.soon.fg,
                          fontWeight: FontWeight.w700,
                        ),
                      ),
                    ),
                    TextButton(
                      onPressed: () => context.go(Routes.shopping),
                      child: Text(l10n.commonBuyShort),
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
