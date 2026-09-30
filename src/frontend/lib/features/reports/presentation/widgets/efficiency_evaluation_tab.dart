import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:sweepfood/app/theme/app_colors.dart';
import 'package:sweepfood/app/theme/app_spacing.dart';
import 'package:sweepfood/core/utils/extensions/build_context_x.dart';
import 'package:sweepfood/core/widgets/async_value_widget.dart';
import 'package:sweepfood/features/reports/domain/entities/efficiency_evaluation.dart';
import 'package:sweepfood/features/reports/presentation/controllers/reports_controller.dart';

class EfficiencyEvaluationTab extends ConsumerWidget {
  const EfficiencyEvaluationTab({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final async = ref.watch(efficiencyEvaluationProvider);

    return RefreshIndicator(
      onRefresh: () => ref.refresh(efficiencyEvaluationProvider.future),
      child: AsyncValueWidget<EfficiencyEvaluation>(
        value: async,
        onRetry: () => ref.invalidate(efficiencyEvaluationProvider),
        data: (evaluation) {
          return ListView(
            padding: const EdgeInsets.fromLTRB(Gap.md, Gap.md, Gap.md, Gap.xxl),
            children: [
              _ScoreHeroCard(evaluation: evaluation),
              Gap.gapMd,
              _KpiRow(evaluation: evaluation),
              Gap.gapMd,
              _TrendCard(evaluation: evaluation),
              Gap.gapMd,
              Text(
                'LỜI KHUYÊN & ĐÁNH GIÁ THÔNG MINH',
                style: context.text.labelSmall?.copyWith(
                  color: context.sweep.textSecondary,
                  letterSpacing: 0.5,
                ),
              ),
              Gap.gapSm,
              for (final insight in evaluation.insights) ...[
                _InsightCard(insight: insight),
                const SizedBox(height: Gap.sm),
              ],
            ],
          );
        },
      ),
    );
  }
}

class _ScoreHeroCard extends StatelessWidget {
  const _ScoreHeroCard({required this.evaluation});

  final EfficiencyEvaluation evaluation;

  Color _scoreColor() {
    if (evaluation.efficiencyScore >= 85) return BrandPalette.green700;
    if (evaluation.efficiencyScore >= 70) return BrandPalette.warnSoon;
    return BrandPalette.brick500;
  }

  @override
  Widget build(BuildContext context) {
    final scoreColor = _scoreColor();

    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(Gap.lg),
      decoration: BoxDecoration(
        color: context.colors.surfaceContainerLowest,
        borderRadius: Radii.brLg,
        border: Border.all(color: context.sweep.hairline),
      ),
      child: Column(
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text(
                'ĐIỂM HIỆU QUẢ SỬ DỤNG BẾP',
                style: context.text.labelSmall?.copyWith(
                  color: context.sweep.textSecondary,
                  letterSpacing: 0.5,
                ),
              ),
              Container(
                padding: const EdgeInsets.symmetric(
                  horizontal: Gap.sm,
                  vertical: 3,
                ),
                decoration: BoxDecoration(
                  color: scoreColor.withValues(alpha: 0.12),
                  borderRadius: BorderRadius.circular(12),
                ),
                child: Row(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    Icon(Icons.workspace_premium_rounded, size: 14, color: scoreColor),
                    const SizedBox(width: 4),
                    Text(
                      evaluation.ratingLevel.label,
                      style: context.text.labelSmall?.copyWith(
                        color: scoreColor,
                        fontWeight: FontWeight.w700,
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ),
          const SizedBox(height: Gap.md),
          Text(
            '${evaluation.efficiencyScore}',
            style: context.text.displayMedium?.copyWith(
              fontWeight: FontWeight.w800,
              color: scoreColor,
            ),
          ),
          Text(
            'trên thang điểm 100',
            style: context.text.bodySmall?.copyWith(
              color: context.sweep.textTertiary,
            ),
          ),
          const SizedBox(height: Gap.md),
          ClipRRect(
            borderRadius: BorderRadius.circular(6),
            child: LinearProgressIndicator(
              value: (evaluation.efficiencyScore / 100).clamp(0.0, 1.0),
              minHeight: 10,
              backgroundColor: context.sweep.subtleFill,
              valueColor: AlwaysStoppedAnimation<Color>(scoreColor),
            ),
          ),
        ],
      ),
    );
  }
}

class _KpiRow extends StatelessWidget {
  const _KpiRow({required this.evaluation});

  final EfficiencyEvaluation evaluation;

  @override
  Widget build(BuildContext context) {
    return Row(
      children: [
        Expanded(
          child: Container(
            padding: const EdgeInsets.all(Gap.md),
            decoration: BoxDecoration(
              color: context.colors.primaryContainer.withValues(alpha: 0.5),
              borderRadius: Radii.brMd,
              border: Border.all(color: context.sweep.hairline),
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  children: [
                    const Icon(
                      Icons.trending_up_rounded,
                      size: 16,
                      color: BrandPalette.green700,
                    ),
                    const SizedBox(width: 4),
                    Text(
                      'Tận dụng kho',
                      style: context.text.labelSmall?.copyWith(
                        color: context.colors.onPrimaryContainer,
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 4),
                Text(
                  evaluation.utilizationRateLabel,
                  style: context.text.titleLarge?.copyWith(
                    fontWeight: FontWeight.w800,
                    color: context.colors.onPrimaryContainer,
                  ),
                ),
              ],
            ),
          ),
        ),
        const SizedBox(width: Gap.sm),
        Expanded(
          child: Container(
            padding: const EdgeInsets.all(Gap.md),
            decoration: BoxDecoration(
              color: BrandPalette.brick100.withValues(alpha: 0.5),
              borderRadius: Radii.brMd,
              border: Border.all(color: context.sweep.hairline),
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  children: [
                    const Icon(
                      Icons.trending_down_rounded,
                      size: 16,
                      color: BrandPalette.brick500,
                    ),
                    const SizedBox(width: 4),
                    Text(
                      'Tỷ lệ lãng phí',
                      style: context.text.labelSmall?.copyWith(
                        color: BrandPalette.brick500,
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 4),
                Text(
                  evaluation.wasteRateLabel,
                  style: context.text.titleLarge?.copyWith(
                    fontWeight: FontWeight.w800,
                    color: BrandPalette.brick500,
                  ),
                ),
              ],
            ),
          ),
        ),
      ],
    );
  }
}

class _TrendCard extends StatelessWidget {
  const _TrendCard({required this.evaluation});

  final EfficiencyEvaluation evaluation;

  @override
  Widget build(BuildContext context) {
    final trend = evaluation.trend;
    final isPos = trend.isPositive;

    return Container(
      padding: const EdgeInsets.all(Gap.md),
      decoration: BoxDecoration(
        color: context.colors.surfaceContainerLowest,
        borderRadius: Radii.brMd,
        border: Border.all(color: context.sweep.hairline),
      ),
      child: Row(
        children: [
          Container(
            width: 36,
            height: 36,
            decoration: BoxDecoration(
              color: isPos ? BrandPalette.green100 : BrandPalette.brick100,
              shape: BoxShape.circle,
            ),
            child: Icon(
              isPos ? Icons.arrow_upward_rounded : Icons.arrow_downward_rounded,
              size: 20,
              color: isPos ? BrandPalette.green700 : BrandPalette.brick500,
            ),
          ),
          const SizedBox(width: Gap.md),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  isPos
                    ? 'Tiến bộ hơn kỳ trước (+${trend.scoreDelta.toStringAsFixed(1)} điểm)'
                    : 'Giảm so với kỳ trước (${trend.scoreDelta.toStringAsFixed(1)} điểm)',
                  style: context.text.bodyMedium?.copyWith(
                    fontWeight: FontWeight.w600,
                  ),
                ),
                Text(
                  trend.wasteKgDelta <= 0
                    ? 'Giảm ${(trend.wasteKgDelta.abs()).toStringAsFixed(2)} kg thực phẩm bị lãng phí.'
                    : 'Tăng ${(trend.wasteKgDelta).toStringAsFixed(2)} kg thực phẩm bị lãng phí.',
                  style: context.text.bodySmall?.copyWith(
                    color: context.sweep.textSecondary,
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

class _InsightCard extends StatelessWidget {
  const _InsightCard({required this.insight});

  final SmartInsight insight;

  @override
  Widget build(BuildContext context) {
    final (icon, color, bg) = switch (insight.type) {
      InsightType.positive => (
          Icons.eco_rounded,
          BrandPalette.green700,
          BrandPalette.green100,
        ),
      InsightType.recommendation => (
          Icons.lightbulb_outline_rounded,
          BrandPalette.warnSoon,
          const Color(0xFFFFF3CD),
        ),
      InsightType.warning => (
          Icons.warning_amber_rounded,
          BrandPalette.brick500,
          BrandPalette.brick100,
        ),
    };

    return Container(
      padding: const EdgeInsets.all(Gap.md),
      decoration: BoxDecoration(
        color: context.colors.surfaceContainerLowest,
        borderRadius: Radii.brMd,
        border: Border.all(color: context.sweep.hairline),
      ),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Container(
            width: 36,
            height: 36,
            decoration: BoxDecoration(
              color: bg,
              borderRadius: Radii.brSm,
            ),
            child: Icon(icon, size: 20, color: color),
          ),
          const SizedBox(width: Gap.md),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  insight.title,
                  style: context.text.titleSmall?.copyWith(
                    fontWeight: FontWeight.w700,
                  ),
                ),
                const SizedBox(height: 3),
                Text(
                  insight.message,
                  style: context.text.bodySmall?.copyWith(
                    color: context.colors.onSurfaceVariant,
                    height: 1.35,
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}
