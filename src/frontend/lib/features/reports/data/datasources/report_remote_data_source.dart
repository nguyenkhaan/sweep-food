import 'package:frontend/core/network/api_client.dart';
import 'package:frontend/core/network/api_paths.dart';
import 'package:frontend/features/reports/data/models/report_dto.dart';
import 'package:frontend/features/reports/domain/entities/waste_reduction_summary.dart';

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
}
