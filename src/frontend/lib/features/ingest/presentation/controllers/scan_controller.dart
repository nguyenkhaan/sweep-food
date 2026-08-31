import 'package:frontend/core/utils/result.dart';
import 'package:frontend/features/ingest/data/repositories/scan_repository_impl.dart';
import 'package:frontend/features/ingest/domain/entities/scan_job.dart';
import 'package:frontend/features/ingest/domain/repositories/scan_repository.dart';
import 'package:riverpod_annotation/riverpod_annotation.dart';

part 'scan_controller.g.dart';

/// Drives one capture → upload → extract cycle. The camera / voice screens
/// `read` this to run a scan and watch it for the in-flight state; the review
/// screens receive the resulting [ScanJob] via router `extra`.
@riverpod
class ScanController extends _$ScanController {
  @override
  Future<ScanJob?> build() async => null;

  Future<ScanJob> scanLabel(String imagePath) =>
      _run((r) => r.scanLabel(imagePath));

  Future<ScanJob> scanReceipt(String imagePath) =>
      _run((r) => r.scanReceipt(imagePath));

  Future<ScanJob> scanVoice({String? audioPath, String? transcript}) =>
      _run((r) => r.scanVoice(audioPath: audioPath, transcript: transcript));

  Future<ScanJob> _run(
    Future<Result<ScanJob>> Function(ScanRepository repo) call,
  ) async {
    state = const AsyncValue<ScanJob?>.loading();
    final result = await call(ref.read(scanRepositoryProvider));
    return result.fold(
      (failure) {
        state = AsyncValue<ScanJob?>.error(failure, StackTrace.current);
        throw failure;
      },
      (job) {
        state = AsyncValue<ScanJob?>.data(job);
        return job;
      },
    );
  }
}
