import 'package:flutter_test/flutter_test.dart';
import 'package:frontend/core/error/failure.dart';
import 'package:frontend/core/utils/result.dart';
import 'package:frontend/features/ingest/data/repositories/scan_repository_impl.dart';
import 'package:frontend/features/ingest/presentation/controllers/scan_controller.dart';
import 'package:mocktail/mocktail.dart';

import '../../helpers/ingest_fixtures.dart';
import '../../helpers/mocks.dart';
import '../../helpers/test_providers.dart';

void main() {
  test('scanLabel returns the job from the repository and stores AsyncData',
      () async {
    final repo = MockScanRepository();
    final job = labelScanJob();
    when(() => repo.scanLabel(any())).thenAnswer((_) async => Right(job));

    final container = createContainer(
      overrides: [scanRepositoryProvider.overrideWithValue(repo)],
    );
    final notifier = container.read(scanControllerProvider.notifier);

    final result = await notifier.scanLabel('/tmp/x.jpg');

    expect(result.id, job.id);
    expect(container.read(scanControllerProvider).value, job);
    verify(() => repo.scanLabel('/tmp/x.jpg')).called(1);
  });

  test('a repository Failure is rethrown and stored as AsyncError', () async {
    final repo = MockScanRepository();
    const failure = ServerFailure(message: 'boom');
    when(() => repo.scanVoice(audioPath: any(named: 'audioPath')))
        .thenAnswer((_) async => const Left(failure));

    final container = createContainer(
      overrides: [scanRepositoryProvider.overrideWithValue(repo)],
    );
    final notifier = container.read(scanControllerProvider.notifier);

    await expectLater(
      notifier.scanVoice(audioPath: null),
      throwsA(isA<Failure>()),
    );
    expect(container.read(scanControllerProvider).error, isA<Failure>());
  });
}
