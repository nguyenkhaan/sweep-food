import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:sweepfood/app/theme/app_icons.dart';
import 'package:sweepfood/app/theme/app_motion.dart';
import 'package:sweepfood/app/theme/app_spacing.dart';
import 'package:sweepfood/app/theme/app_typography.dart';
import 'package:sweepfood/core/utils/extensions/build_context_x.dart';
import 'package:sweepfood/core/widgets/animated_counter.dart';
import 'package:sweepfood/core/widgets/async_value_widget.dart';
import 'package:sweepfood/core/widgets/empty_state.dart';
import 'package:sweepfood/core/widgets/staggered_reveal.dart';
import 'package:sweepfood/core/widgets/tactile_card.dart';
import 'package:sweepfood/features/reports/domain/entities/waste_reduction_summary.dart';
import 'package:sweepfood/features/reports/presentation/controllers/reports_controller.dart';
import 'package:sweepfood/features/reports/presentation/widgets/period_selector.dart';
import 'package:sweepfood/features/reports/presentation/widgets/report_bar_chart.dart';

/// R-01 Báo cáo chống lãng phí (Concept B · Format 1: Big Emerald Hero Counter
/// + Clean Weekly Chart & Category Breakdown Cards).
class ReportsScreen extends ConsumerWidget {
  const ReportsScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final l10n = context.l10n;
    final sweep = context.sweep;
    final cs = context.colors;
    final period = ref.watch(reportPeriodControllerProvider);
    final async = ref.watch(reportsControllerProvider);
    final summary = async.asData?.value;

    return AnnotatedRegion<SystemUiOverlayStyle>(
      value: SystemUiOverlayStyle(
        statusBarColor: Colors.transparent,
        statusBarIconBrightness: Brightness.light,
        statusBarBrightness: Brightness.dark,
        systemNavigationBarColor: cs.surfaceContainerLowest,
        systemNavigationBarIconBrightness:
            Theme.of(context).brightness == Brightness.dark
            ? Brightness.light
            : Brightness.dark,
      ),
      child: Scaffold(
        backgroundColor: cs.surface,
        body: Column(
          children: [
            _ReportsEmeraldHero(
              title: l10n.reportsTitle,
              period: period,
              summary: summary != null && !summary.isEmpty ? summary : null,
              onPeriodChanged: (p) {
                AppHaptics.selection();
                ref.read(reportPeriodControllerProvider.notifier).set(p);
              },
            ),
            Expanded(
              child: AsyncValueWidget<WasteReductionSummary>(
                value: async,
                onRetry: () => ref.invalidate(reportsControllerProvider),
                data: (r) {
                  if (r.isEmpty) {
                    return ListView(
                      padding: const EdgeInsets.fromLTRB(
                        Gap.lg,
                        Gap.xl,
                        Gap.lg,
                        Gap.xxl,
                      ),
                      children: [
                        EmptyState(
                          illustrationAsset:
                              'assets/illustrations/welcome_zero_waste.svg',
                          title: l10n.reportsEmptyTitle,
                          message: l10n.reportsEmptyBody,
                        ),
                      ],
                    );
                  }

                  final maxCatCount = r.byCategory.fold<int>(
                    1,
                    (m, c) => c.count > m ? c.count : m,
                  );

                  return ListView(
                    padding: const EdgeInsets.fromLTRB(
                      Gap.lg,
                      Gap.xs,
                      Gap.lg,
                      Gap.xxl,
                    ),
                    children: [
                      StaggeredReveal(
                        index: 0,
                        child: _ReportSectionCard(
                          title: l10n.reportsWeeklyCard,
                          child: ReportBarChart(bars: r.weeklyBars),
                        ),
                      ),
                      Gap.gapMd,
                      if (r.byCategory.isNotEmpty)
                        StaggeredReveal(
                          index: 1,
                          child: _ReportSectionCard(
                            title: l10n.reportsByCategoryCard,
                            child: Column(
                              children: [
                                for (final c in r.byCategory)
                                  Padding(
                                    padding: const EdgeInsets.symmetric(
                                      vertical: Gap.xs,
                                    ),
                                    child: Column(
                                      crossAxisAlignment:
                                          CrossAxisAlignment.start,
                                      children: [
                                        Row(
                                          children: [
                                            Container(
                                              width: 10,
                                              height: 10,
                                              decoration: BoxDecoration(
                                                color: Color(c.colorValue),
                                                borderRadius:
                                                    BorderRadius.circular(3),
                                              ),
                                            ),
                                            const SizedBox(width: Gap.sm),
                                            Expanded(
                                              child: Text(
                                                c.category,
                                                style: context.text.bodyMedium,
                                              ),
                                            ),
                                            Text(
                                              l10n.ingredientCount(c.count),
                                              style: AppTypography.tabular(
                                                context.text.bodyMedium
                                                    ?.copyWith(
                                                      fontWeight:
                                                          FontWeight.w700,
                                                    ),
                                              ),
                                            ),
                                          ],
                                        ),
                                        const SizedBox(height: 6),
                                        ClipRRect(
                                          borderRadius: BorderRadius.circular(
                                            Radii.pill,
                                          ),
                                          child: TweenAnimationBuilder<double>(
                                            tween: Tween(
                                              begin: 0,
                                              end: (c.count / maxCatCount)
                                                  .clamp(0.08, 1.0),
                                            ),
                                            duration: AppMotion.resolve(
                                              context,
                                              context.motion.medium,
                                            ),
                                            curve: AppMotion.resolveCurve(
                                              context,
                                              context.motion.enterCurve,
                                            ),
                                            builder: (_, v, __) =>
                                                LinearProgressIndicator(
                                                  value: v,
                                                  minHeight: 6,
                                                  backgroundColor:
                                                      sweep.subtleFill,
                                                  valueColor:
                                                      AlwaysStoppedAnimation(
                                                        Color(c.colorValue),
                                                      ),
                                                ),
                                          ),
                                        ),
                                      ],
                                    ),
                                  ),
                              ],
                            ),
                          ),
                        ),
                    ],
                  );
                },
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _ReportsEmeraldHero extends StatelessWidget {
  const _ReportsEmeraldHero({
    required this.title,
    required this.period,
    required this.onPeriodChanged,
    this.summary,
  });

  final String title;
  final ReportPeriod period;
  final WasteReductionSummary? summary;
  final ValueChanged<ReportPeriod> onPeriodChanged;

  @override
  Widget build(BuildContext context) {
    final l10n = context.l10n;
    final sweep = context.sweep;
    final cs = context.colors;
    final canPop = Navigator.of(context).canPop();

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
                Gap.sm,
                Gap.lg,
                Gap.lg,
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    children: [
                      if (canPop) ...[
                        Material(
                          color: sweep.heroSurfaceElevated,
                          shape: RoundedRectangleBorder(
                            borderRadius: Radii.brMd,
                            side: BorderSide(
                              color: sweep.onHeroSurface.withValues(
                                alpha: 0.14,
                              ),
                            ),
                          ),
                          child: InkWell(
                            borderRadius: Radii.brMd,
                            onTap: () => Navigator.of(context).maybePop(),
                            child: SizedBox(
                              width: 44,
                              height: 44,
                              child: Icon(
                                AppIcons.arrowLeft,
                                size: 19,
                                color: sweep.onHeroSurface,
                              ),
                            ),
                          ),
                        ),
                        const SizedBox(width: Gap.sm + 2),
                      ],
                      Expanded(
                        child: Text(
                          title,
                          maxLines: 1,
                          overflow: TextOverflow.ellipsis,
                          style: context.text.titleLarge?.copyWith(
                            color: sweep.onHeroSurface,
                            fontWeight: FontWeight.w800,
                          ),
                        ),
                      ),
                      const SizedBox(width: Gap.xs),
                      Container(
                        decoration: BoxDecoration(
                          color: sweep.heroSurfaceElevated,
                          borderRadius: BorderRadius.circular(Radii.pill),
                          border: Border.all(
                            color: sweep.onHeroSurface.withValues(alpha: 0.18),
                          ),
                        ),
                        child: PeriodSelector(
                          value: period,
                          foregroundColor: sweep.onHeroSurface,
                          onChanged: onPeriodChanged,
                        ),
                      ),
                    ],
                  ),
                  if (summary != null) ...[
                    Gap.gapMd,
                    Row(
                      children: [
                        Icon(AppIcons.leaf, size: 15, color: sweep.onHeroMuted),
                        const SizedBox(width: 6),
                        Expanded(
                          child: Text(
                            l10n.reportsHeroPeriod(summary!.periodLabel),
                            style: context.text.labelMedium?.copyWith(
                              color: sweep.onHeroMuted,
                              fontWeight: FontWeight.w600,
                            ),
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 6),
                    AnimatedCounter(
                      value: summary!.wasteAvoidedKg,
                      formatter: (v) =>
                          '${v.toStringAsFixed(1).replaceAll('.', ',')} kg',
                      style: context.text.displayMedium?.copyWith(
                        color: sweep.onHeroSurface,
                        fontWeight: FontWeight.w800,
                        height: 1.05,
                      ),
                    ),
                    const SizedBox(height: 6),
                    Text(
                      l10n.reportsHeroDetail(
                        summary!.wasteAvoidedLabel,
                        summary!.dishesCooked,
                      ),
                      style: context.text.bodySmall?.copyWith(
                        color: sweep.onHeroMuted,
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

class _ReportSectionCard extends StatelessWidget {
  const _ReportSectionCard({required this.title, required this.child});

  final String title;
  final Widget child;

  @override
  Widget build(BuildContext context) {
    return TactileCard(
      color: context.colors.surfaceContainerLowest,
      borderColor: context.sweep.hairline,
      boxShadow: Shadows.e1,
      padding: const EdgeInsets.all(Gap.md),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            title.toUpperCase(),
            style: context.text.labelSmall?.copyWith(
              letterSpacing: 0.7,
              fontWeight: FontWeight.w800,
              color: context.sweep.textTertiary,
            ),
          ),
          Gap.gapSm,
          child,
        ],
      ),
    );
  }
}
