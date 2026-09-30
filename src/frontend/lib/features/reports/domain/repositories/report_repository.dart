import 'package:sweepfood/core/utils/result.dart';
import 'package:sweepfood/features/reports/domain/entities/efficiency_evaluation.dart';
import 'package:sweepfood/features/reports/domain/entities/food_usage_history.dart';
import 'package:sweepfood/features/reports/domain/entities/waste_reduction_summary.dart';
import 'package:sweepfood/features/reports/domain/entities/waste_statistics.dart';

abstract interface class ReportRepository {
  /// `GET /reports/waste-reduction?period=` (week | month).
  Future<Result<WasteReductionSummary>> wasteReduction(ReportPeriod period);

  /// `GET /reports/usage-history?period=` (week | month).
  Future<Result<FoodUsageHistory>> usageHistory(ReportPeriod period);

  /// `GET /reports/waste-statistics?period=` (week | month).
  Future<Result<WasteStatistics>> wasteStatistics(ReportPeriod period);

  /// `GET /reports/efficiency?period=` (week | month).
  Future<Result<EfficiencyEvaluation>> efficiencyEvaluation(ReportPeriod period);
}
