import 'package:sweepfood/core/network/api_client.dart';
import 'package:sweepfood/core/network/api_paths.dart';
import 'package:sweepfood/features/reports/data/models/analytics_dto.dart';
import 'package:sweepfood/features/reports/data/models/report_dto.dart';
import 'package:sweepfood/features/reports/domain/entities/waste_reduction_summary.dart';

class ReportRemoteDataSource {
  ReportRemoteDataSource(this._api);

  final ApiClient _api;

  Future<WasteReductionSummaryDto> wasteReduction(ReportPeriod period) async {
    final json = await _api.get(
      ApiPaths.reportsWasteReduction,
      query: {'period': period.wire},
    );
    return WasteReductionSummaryDto.fromJson(json as Map<String, dynamic>);
  }

  Future<FoodUsageHistoryDto> usageHistory(ReportPeriod period) async {
    throw UnsupportedError(
      'Backend does not expose a food usage history report yet.',
    );
  }

  Future<WasteStatisticsDto> wasteStatistics(ReportPeriod period) async {
    throw UnsupportedError(
      'Backend does not expose aggregated waste statistics yet.',
    );
  }

  Future<EfficiencyEvaluationDto> efficiencyEvaluation(
    ReportPeriod period,
  ) async {
    throw UnsupportedError(
      'Backend does not expose an efficiency evaluation yet.',
    );
  }
}
