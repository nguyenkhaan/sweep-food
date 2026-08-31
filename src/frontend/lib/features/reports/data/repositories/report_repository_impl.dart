import 'package:frontend/core/network/api_result.dart';
import 'package:frontend/core/network/network_providers.dart';
import 'package:frontend/core/utils/result.dart';
import 'package:frontend/features/reports/data/datasources/report_remote_data_source.dart';
import 'package:frontend/features/reports/domain/entities/waste_reduction_summary.dart';
import 'package:frontend/features/reports/domain/repositories/report_repository.dart';
import 'package:riverpod_annotation/riverpod_annotation.dart';

part 'report_repository_impl.g.dart';

@Riverpod(keepAlive: true)
ReportRepository reportRepository(Ref ref) => ReportRepositoryImpl(
      ReportRemoteDataSource(ref.watch(apiClientProvider)),
    );

class ReportRepositoryImpl implements ReportRepository {
  ReportRepositoryImpl(this._remote);

  final ReportRemoteDataSource _remote;

  @override
  Future<Result<WasteReductionSummary>> wasteReduction(ReportPeriod period) =>
      runGuarded(() async => (await _remote.wasteReduction(period)).toEntity());
}
