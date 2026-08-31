import 'package:flutter_test/flutter_test.dart';
import 'package:mocktail/mocktail.dart';
import 'package:sweepfood/core/error/failure.dart';
import 'package:sweepfood/core/network/api_paths.dart';
import 'package:sweepfood/core/utils/result.dart';
import 'package:sweepfood/features/ingest/data/datasources/scan_remote_data_source.dart';
import 'package:sweepfood/features/ingest/data/repositories/scan_repository_impl.dart';
import 'package:sweepfood/features/ingest/domain/entities/scan_job.dart';
import 'package:sweepfood/features/ingest/domain/entities/scan_type.dart';
import 'package:sweepfood/shared/domain/measurement_unit.dart';
import 'package:sweepfood/shared/domain/storage_tier.dart';

import '../../helpers/mocks.dart';

void main() {
  late MockApiClient api;
  late ScanRepositoryImpl repo;

  setUp(() {
    api = MockApiClient();
    repo = ScanRepositoryImpl(ScanRemoteDataSource(api));
  });

  ScanJob rightOrFail(Result<ScanJob> result) => result.fold(
        (f) => fail('expected Right, got $f'),
        (job) => job,
      );

  test('scanLabel maps the wire job to a ScanJob and keeps the image path',
      () async {
    when(
      () => api.postMultipart(
        ApiPaths.scanLabel,
        fields: any(named: 'fields'),
        files: any(named: 'files'),
      ),
    ).thenAnswer(
      (_) async => {
        'job_id': 'job_label_001',
        'type': 'label',
        'status': 'completed',
        'field_count': 5,
        'item': {
          'name': 'Cà chua bi',
          'category': 'Rau củ',
          'quantity': 500.0,
          'unit': 'g',
          'storage_tier': 'fridge',
          'price_vnd': 18000,
          'is_expiry_warn': true,
        },
      },
    );

    final job = rightOrFail(await repo.scanLabel('/tmp/label.jpg'));
    expect(job.type, ScanType.label);
    expect(job.fieldCount, 5);
    expect(job.sourcePath, '/tmp/label.jpg');
    expect(job.items, hasLength(1));
    expect(job.items.single.name, 'Cà chua bi');
    expect(job.items.single.unit, MeasurementUnit.gram);
    expect(job.items.single.storageTier, StorageTier.fridge);
    expect(job.items.single.isExpiryWarn, isTrue);
  });

  test('scanReceipt flattens the line-item array', () async {
    when(
      () => api.postMultipart(
        ApiPaths.scanReceipt,
        fields: any(named: 'fields'),
        files: any(named: 'files'),
      ),
    ).thenAnswer(
      (_) async => {
        'job_id': 'job_receipt_001',
        'type': 'receipt',
        'store_name': 'Bách Hóa Xanh',
        'items': [
          {'name': 'Trứng gà', 'quantity': 10.0, 'unit': 'qua'},
          {'name': 'Dầu ăn', 'quantity': 1.0, 'unit': 'chai'},
        ],
      },
    );

    final job = rightOrFail(await repo.scanReceipt('/tmp/r.jpg'));
    expect(job.storeName, 'Bách Hóa Xanh');
    expect(job.items.map((i) => i.name), ['Trứng gà', 'Dầu ăn']);
    expect(job.items.first.unit, MeasurementUnit.fruit);
  });

  test('scanVoice returns a Failure (Left) when the client throws', () async {
    when(
      () => api.postMultipart(
        ApiPaths.scanVoice,
        fields: any(named: 'fields'),
        files: any(named: 'files'),
      ),
    ).thenThrow(Exception('boom'));

    final result = await repo.scanVoice(transcript: 'test');

    expect(result.isLeft(), isTrue);
    result.match((f) => expect(f, isA<Failure>()), (_) => fail('expected Left'));
  });
}
