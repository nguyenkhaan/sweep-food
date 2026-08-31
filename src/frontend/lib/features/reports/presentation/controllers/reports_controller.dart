import 'package:frontend/features/reports/data/repositories/report_repository_impl.dart';
import 'package:frontend/features/reports/domain/entities/waste_reduction_summary.dart';
import 'package:riverpod_annotation/riverpod_annotation.dart';

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
