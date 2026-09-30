import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:riverpod_annotation/riverpod_annotation.dart';
import 'package:sweepfood/features/reports/data/repositories/report_repository_impl.dart';
import 'package:sweepfood/features/reports/domain/entities/efficiency_evaluation.dart';
import 'package:sweepfood/features/reports/domain/entities/food_usage_history.dart';
import 'package:sweepfood/features/reports/domain/entities/waste_reduction_summary.dart';
import 'package:sweepfood/features/reports/domain/entities/waste_statistics.dart';

part 'reports_controller.g.dart';

/// R-01 period selector (Tuần này / Tháng này).
@riverpod
class ReportPeriodController extends _$ReportPeriodController {
  @override
  ReportPeriod build() => ReportPeriod.month;
  void set(ReportPeriod period) => state = period;
}

/// R-01 "Chống lãng phí" metrics for the selected period.
@riverpod
class ReportsController extends _$ReportsController {
  @override
  Future<WasteReductionSummary> build() async {
    final period = ref.watch(reportPeriodControllerProvider);
    final res = await ref.watch(reportRepositoryProvider).wasteReduction(period);
    return res.fold((f) => throw f, (s) => s);
  }
}

/// Provider cho Lịch sử sử dụng thực phẩm
final foodUsageHistoryProvider =
    FutureProvider.autoDispose<FoodUsageHistory>((ref) async {
  final period = ref.watch(reportPeriodControllerProvider);
  final res = await ref.watch(reportRepositoryProvider).usageHistory(period);
  return res.fold((f) => throw f, (s) => s);
});

/// Provider cho Thống kê thực phẩm lãng phí
final wasteStatisticsProvider =
    FutureProvider.autoDispose<WasteStatistics>((ref) async {
  final period = ref.watch(reportPeriodControllerProvider);
  final res = await ref.watch(reportRepositoryProvider).wasteStatistics(period);
  return res.fold((f) => throw f, (s) => s);
});

/// Provider cho Đánh giá hiệu quả sử dụng thực phẩm
final efficiencyEvaluationProvider =
    FutureProvider.autoDispose<EfficiencyEvaluation>((ref) async {
  final period = ref.watch(reportPeriodControllerProvider);
  final res =
      await ref.watch(reportRepositoryProvider).efficiencyEvaluation(period);
  return res.fold((f) => throw f, (s) => s);
});
