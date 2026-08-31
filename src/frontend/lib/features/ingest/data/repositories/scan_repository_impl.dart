import 'package:frontend/core/network/api_result.dart';
import 'package:frontend/core/network/network_providers.dart';
import 'package:frontend/core/utils/result.dart';
import 'package:frontend/features/ingest/data/datasources/scan_remote_data_source.dart';
import 'package:frontend/features/ingest/domain/entities/scan_job.dart';
import 'package:frontend/features/ingest/domain/entities/scan_type.dart';
import 'package:frontend/features/ingest/domain/repositories/scan_repository.dart';
import 'package:riverpod_annotation/riverpod_annotation.dart';

part 'scan_repository_impl.g.dart';

@Riverpod(keepAlive: true)
ScanRepository scanRepository(Ref ref) => ScanRepositoryImpl(
      ScanRemoteDataSource(ref.watch(apiClientProvider)),
    );

class ScanRepositoryImpl implements ScanRepository {
  ScanRepositoryImpl(this._remote);

  final ScanRemoteDataSource _remote;

  @override
  Future<Result<ScanJob>> scanLabel(String imagePath) =>
      _submit(ScanType.label, mediaPath: imagePath);

  @override
  Future<Result<ScanJob>> scanReceipt(String imagePath) =>
      _submit(ScanType.receipt, mediaPath: imagePath);

  @override
  Future<Result<ScanJob>> scanVoice({String? audioPath, String? transcript}) =>
      _submit(ScanType.voice, mediaPath: audioPath, transcript: transcript);

  Future<Result<ScanJob>> _submit(
    ScanType type, {
    String? mediaPath,
    String? transcript,
  }) =>
      runGuarded(() async {
        final dto = await _remote.submit(
          type,
          mediaPath: mediaPath,
          transcript: transcript,
        );
        return dto.toEntity().copyWith(sourcePath: mediaPath);
      });
}
