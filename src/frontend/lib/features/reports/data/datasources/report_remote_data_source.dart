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
    final json = await _api.get(
      ApiPaths.reportsUsageHistory,
      query: {'period': period.wire},
    );
    return FoodUsageHistoryDto.fromJson(json as Map<String, dynamic>);
  }

  Future<WasteStatisticsDto> wasteStatistics(ReportPeriod period) async {
    final json = await _api.get(
      ApiPaths.reportsWasteStatistics,
      query: {'period': period.wire},
    );
    return WasteStatisticsDto.fromJson(json as Map<String, dynamic>);
  }

  Future<EfficiencyEvaluationDto> efficiencyEvaluation(ReportPeriod period) async {
    final json = await _api.get(
      ApiPaths.reportsEfficiency,
      query: {'period': period.wire},
    );
    return EfficiencyEvaluationDto.fromJson(json as Map<String, dynamic>);
  }
}
