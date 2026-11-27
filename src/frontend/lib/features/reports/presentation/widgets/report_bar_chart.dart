import 'package:fl_chart/fl_chart.dart';
import 'package:flutter/material.dart';
import 'package:sweepfood/core/utils/extensions/build_context_x.dart';
import 'package:sweepfood/features/reports/domain/entities/waste_reduction_summary.dart';

/// R-01 weekly bars — "nguyên liệu cứu được theo tuần".
class ReportBarChart extends StatelessWidget {
  const ReportBarChart({required this.bars, super.key});

  final List<WasteReductionBar> bars;

  @override
  Widget build(BuildContext context) {
    if (bars.isEmpty) {
      return const SizedBox(height: 8);
    }
    final maxY =
        bars.map((b) => b.value).fold<int>(1, (m, v) => v > m ? v : m) + 1;

    return SizedBox(
      height: 156,
      child: BarChart(
        BarChartData(
          alignment: BarChartAlignment.spaceAround,
          maxY: maxY.toDouble(),
          barTouchData: BarTouchData(
            enabled: true,
            touchTooltipData: BarTouchTooltipData(
              getTooltipColor: (_) => context.colors.surfaceContainerHighest,
              getTooltipItem: (group, groupIndex, rod, rodIndex) {
                final b = bars[groupIndex];
                return BarTooltipItem(
                  '${b.label}: ${b.value}',
                  context.text.labelMedium!.copyWith(
                    color: context.colors.onSurface,
                    fontWeight: FontWeight.w700,
                  ),
                );
              },
            ),
          ),
          gridData: const FlGridData(show: false),
          borderData: FlBorderData(show: false),
          titlesData: FlTitlesData(
            leftTitles: const AxisTitles(
              sideTitles: SideTitles(showTitles: false),
            ),
            rightTitles: const AxisTitles(
              sideTitles: SideTitles(showTitles: false),
            ),
            topTitles: const AxisTitles(
              sideTitles: SideTitles(showTitles: false),
            ),
            bottomTitles: AxisTitles(
              sideTitles: SideTitles(
                showTitles: true,
                reservedSize: 24,
                getTitlesWidget: (value, meta) {
                  final i = value.toInt();
                  if (i < 0 || i >= bars.length) return const SizedBox.shrink();
                  return Padding(
                    padding: const EdgeInsets.only(top: 6),
                    child: Text(
                      bars[i].label,
                      style: context.text.labelSmall?.copyWith(
                        letterSpacing: 0,
                        color: context.sweep.textTertiary,
                      ),
                    ),
                  );
                },
              ),
            ),
          ),
          barGroups: [
            for (var i = 0; i < bars.length; i++)
              BarChartGroupData(
                x: i,
                barRods: [
                  BarChartRodData(
                    toY: bars[i].value.toDouble(),
                    width: 24,
                    gradient: LinearGradient(
                      begin: Alignment.bottomCenter,
                      end: Alignment.topCenter,
                      colors: [
                        context.colors.primary,
                        context.colors.secondary,
                      ],
                    ),
                    borderRadius: const BorderRadius.vertical(
                      top: Radius.circular(8),
                    ),
                  ),
                ],
              ),
          ],
        ),
      ),
    );
  }
}
