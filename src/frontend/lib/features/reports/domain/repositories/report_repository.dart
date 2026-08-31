import 'package:sweepfood/core/utils/result.dart';
import 'package:sweepfood/features/reports/domain/entities/waste_reduction_summary.dart';

abstract interface class ReportRepository {
  /// `GET /reports/waste-reduction?period=` (week | month).
  Future<Result<WasteReductionSummary>> wasteReduction(ReportPeriod period);
}
