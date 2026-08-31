import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:frontend/app/theme/app_spacing.dart';
import 'package:frontend/core/utils/extensions/build_context_x.dart';
import 'package:frontend/core/widgets/async_value_widget.dart';
import 'package:frontend/core/widgets/empty_state.dart';
import 'package:frontend/features/reports/domain/entities/waste_reduction_summary.dart';
import 'package:frontend/features/reports/presentation/controllers/reports_controller.dart';
import 'package:frontend/features/reports/presentation/widgets/period_selector.dart';
import 'package:frontend/features/reports/presentation/widgets/report_bar_chart.dart';

/// R-01 Báo cáo chống lãng phí — ingredients used before expiry, kg avoided,
/// dishes cooked. No money (price data unavailable).
class ReportsScreen extends ConsumerWidget {
  const ReportsScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final period = ref.watch(reportPeriodControllerProvider);
    final async = ref.watch(reportsControllerProvider);

    return Scaffold(
      appBar: AppBar(
        title: const Text('Chống lãng phí'),
        actions: [
          PeriodSelector(
            value: period,
            onChanged: (p) =>
                ref.read(reportPeriodControllerProvider.notifier).set(p),
          ),
          const SizedBox(width: Gap.xs),
        ],
      ),
      body: AsyncValueWidget<WasteReductionSummary>(
        value: async,
        onRetry: () => ref.invalidate(reportsControllerProvider),
        data: (r) {
          if (r.isEmpty) {
            return ListView(
              children: const [
                SizedBox(height: 72),
                EmptyState(
                  title: 'Chưa có dữ liệu',
                  message:
                      'Nấu vài món dùng nguyên liệu cận hạn để xem bạn tiết kiệm được bao nhiêu.',
                  icon: Icons.insights_outlined,
                ),
              ],
            );
          }
          return ListView(
            padding: const EdgeInsets.fromLTRB(Gap.lg, Gap.md, Gap.lg, Gap.xxl),
            children: [
              _HeroCard(summary: r),
              Gap.gapMd,
              _Card(
                title: 'Nguyên liệu cứu được theo tuần',
                child: ReportBarChart(bars: r.weeklyBars),
              ),
              Gap.gapMd,
              _Card(
                title: 'Theo nhóm thực phẩm',
                child: Column(
                  children: [
                    for (final c in r.byCategory)
                      Padding(
                        padding: const EdgeInsets.symmetric(vertical: Gap.xs),
                        child: Row(
                          children: [
                            Container(
                              width: 8,
                              height: 8,
                              decoration: BoxDecoration(
                                color: Color(c.colorValue),
                                borderRadius: BorderRadius.circular(2),
                              ),
                            ),
                            Gap.gapSm,
                            Expanded(child: Text(c.category)),
                            Text(
                              '${c.count} nguyên liệu',
                              style: context.text.bodyMedium
                                  ?.copyWith(fontWeight: FontWeight.w700),
                            ),
                          ],
                        ),
                      ),
                  ],
                ),
              ),
            ],
          );
        },
      ),
    );
  }
}

class _HeroCard extends StatelessWidget {
  const _HeroCard({required this.summary});

  final WasteReductionSummary summary;

  @override
  Widget build(BuildContext context) {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(Gap.lg),
      decoration: BoxDecoration(
        color: context.colors.primaryContainer,
        borderRadius: Radii.brLg,
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            '${summary.periodLabel} · nguyên liệu dùng trước hạn',
            style: context.text.labelMedium?.copyWith(
              color: context.colors.onPrimaryContainer.withValues(alpha: 0.8),
            ),
          ),
          const SizedBox(height: 4),
          Text(
            '${summary.itemsUsedBeforeExpiry} nguyên liệu',
            style: context.text.headlineMedium?.copyWith(
              fontWeight: FontWeight.w700,
              color: context.colors.onPrimaryContainer,
            ),
          ),
          const SizedBox(height: 4),
          Text(
            '≈ ${summary.wasteAvoidedLabel} thực phẩm tránh bị bỏ phí · '
            '${summary.dishesCooked} món đã nấu',
            style: context.text.bodySmall?.copyWith(
              color: context.colors.onPrimaryContainer.withValues(alpha: 0.9),
            ),
          ),
        ],
      ),
    );
  }
}

class _Card extends StatelessWidget {
  const _Card({required this.title, required this.child});

  final String title;
  final Widget child;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(Gap.md),
      decoration: BoxDecoration(
        color: context.colors.surfaceContainerLowest,
        borderRadius: Radii.brLg,
        border: Border.all(color: context.sweep.hairline),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(title.toUpperCase(), style: context.text.labelSmall),
          Gap.gapSm,
          child,
        ],
      ),
    );
  }
}
