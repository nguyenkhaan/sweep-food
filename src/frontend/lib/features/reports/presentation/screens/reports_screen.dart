import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:sweepfood/app/theme/app_spacing.dart';
import 'package:sweepfood/core/utils/extensions/build_context_x.dart';
import 'package:sweepfood/features/reports/presentation/controllers/reports_controller.dart';
import 'package:sweepfood/features/reports/presentation/widgets/efficiency_evaluation_tab.dart';
import 'package:sweepfood/features/reports/presentation/widgets/food_usage_tab.dart';
import 'package:sweepfood/features/reports/presentation/widgets/period_selector.dart';
import 'package:sweepfood/features/reports/presentation/widgets/waste_statistics_tab.dart';

/// Màn hình Thống kê toàn diện:
/// - Tab 1: Xem lịch sử sử dụng thực phẩm (FoodUsageTab)
/// - Tab 2: Thống kê thực phẩm lãng phí (WasteStatisticsTab)
/// - Tab 3: Đánh giá hiệu quả sử dụng (EfficiencyEvaluationTab)
class ReportsScreen extends ConsumerWidget {
  const ReportsScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final l10n = context.l10n;
    final period = ref.watch(reportPeriodControllerProvider);

    return DefaultTabController(
      length: 3,
      child: Scaffold(
        appBar: AppBar(
          title: Text(l10n.reportsTitle),
          actions: [
            PeriodSelector(
              value: period,
              onChanged: (p) =>
                  ref.read(reportPeriodControllerProvider.notifier).set(p),
            ),
            const SizedBox(width: Gap.xs),
          ],
          bottom: TabBar(
            indicatorSize: TabBarIndicatorSize.tab,
            labelStyle: context.text.labelLarge?.copyWith(
              fontWeight: FontWeight.w700,
            ),
            unselectedLabelStyle: context.text.labelMedium,
            tabs: const [
              Tab(
                icon: Icon(Icons.history_rounded, size: 20),
                text: 'Lịch sử dùng',
              ),
              Tab(
                icon: Icon(Icons.delete_sweep_outlined, size: 20),
                text: 'Lãng phí',
              ),
              Tab(
                icon: Icon(Icons.insights_rounded, size: 20),
                text: 'Hiệu quả',
              ),
            ],
          ),
        ),
        body: const TabBarView(
          children: [
            FoodUsageTab(),
            WasteStatisticsTab(),
            EfficiencyEvaluationTab(),
          ],
        ),
      ),
    );
  }
}
