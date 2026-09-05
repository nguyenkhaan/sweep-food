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

  test(
      'scanLabel maps backend ExtractionResponse to a ScanJob and keeps image path',
      () async {
    when(
      () => api.postMultipart(
        ApiPaths.extractionOcrLabel,
        fields: any(named: 'fields'),
        files: any(named: 'files'),
      ),
    ).thenAnswer(
      (_) async => {
        'request_id': '00000000-0000-0000-0000-000000000001',
        'status': 'SUCCEEDED',
        'provider': 'MOCK_OCR',
        'raw_text': 'Mock OCR label output',
        'fields': {
          'ingredient_name': 'Whole Milk',
          'quantity': 1.0,
          'unit': 'LITER',
          'packaged_at': '2026-08-28',
          'expires_at': '2026-09-05',
          'price': 35000.0,
          'currency': 'VND',
          'barcode': null,
        },
        'confidence': {'ingredient_name': 0.95, 'expires_at': 0.75},
        'warnings': <String>[],
        'persisted': false,
      },
    );

    final job = rightOrFail(await repo.scanLabel('/tmp/label.jpg'));
    expect(job.type, ScanType.label);
    expect(job.sourcePath, '/tmp/label.jpg');
    expect(job.items, hasLength(1));
    expect(job.items.single.name, 'Whole Milk');
    expect(job.items.single.quantity, 1.0);
    expect(job.items.single.unit, MeasurementUnit.liter);
    expect(job.items.single.priceVnd, 35000);
    expect(job.items.single.isExpiryWarn, isTrue); // confidence < 0.8
  });

  test('scanReceipt maps backend InvoiceExtractionResponse with line items',
      () async {
    when(
      () => api.postMultipart(
        ApiPaths.extractionOcrInvoice,
        fields: any(named: 'fields'),
        files: any(named: 'files'),
      ),
    ).thenAnswer(
      (_) async => {
        'request_id': '00000000-0000-0000-0000-000000000002',
        'status': 'SUCCEEDED',
        'provider': 'MOCK_OCR',
        'raw_text': 'Mock OCR invoice output',
        'fields': {
          'line_items': [
            {
              'name': 'Whole Milk',
              'quantity': 2.0,
              'unit': 'LITER',
              'unit_price': 35000.0,
              'total_price': 70000.0,
            },
            {
              'name': 'Bread',
              'quantity': 1.0,
              'unit': 'PIECE',
              'unit_price': 15000.0,
              'total_price': 15000.0,
            },
          ],
          'total_amount': 85000.0,
          'currency': 'VND',
          'invoice_date': '2026-08-30',
          'vendor_name': 'Mock Grocery Store',
        },
        'confidence': {'line_items': 0.82},
        'warnings': <String>[],
        'persisted': false,
      },
    );

    final job = rightOrFail(await repo.scanReceipt('/tmp/r.jpg'));
    expect(job.type, ScanType.receipt);
    expect(job.storeName, 'Mock Grocery Store');
    expect(job.items, hasLength(2));
    expect(job.items.map((i) => i.name), ['Whole Milk', 'Bread']);
    expect(job.items.first.unit, MeasurementUnit.liter);
    expect(job.items.first.priceVnd, 35000);
    expect(job.items.last.unit, MeasurementUnit.piece);
  });

  test('lookupBarcode maps BarcodeExtractionResponse to ScanJob', () async {
    when(
      () => api.post(ApiPaths.extractionBarcode('8934567890123')),
    ).thenAnswer(
      (_) async => {
        'request_id': '00000000-0000-0000-0000-000000000003',
        'status': 'SUCCEEDED',
        'provider': 'MOCK_BARCODE',
        'raw_text': 'Product found for barcode 8934567890123',
        'fields': {
          'barcode': '8934567890123',
          'product_name': 'Whole Milk',
          'brand': 'Dairy Farm',
          'category': 'Dairy',
          'ingredient_name': 'Whole Milk',
          'quantity': 1.0,
          'unit': 'LITER',
          'expires_at': null,
          'price': 35000.0,
          'currency': 'VND',
        },
        'confidence': {'product_name': 0.90},
        'warnings': <String>[],
        'persisted': false,
      },
    );

    final job = rightOrFail(await repo.lookupBarcode('8934567890123'));
    expect(job.items, hasLength(1));
    expect(job.items.single.name, 'Whole Milk');
    expect(job.items.single.quantity, 1.0);
    expect(job.items.single.unit, MeasurementUnit.liter);
    expect(job.items.single.priceVnd, 35000);
  });

  test('scanVoice returns a Failure (Left) when the client throws', () async {
    when(
      () => api.postMultipart(
        ApiPaths.extractionAsr,
        fields: any(named: 'fields'),
        files: any(named: 'files'),
      ),
    ).thenThrow(Exception('boom'));

    final result = await repo.scanVoice(transcript: 'test');

    expect(result.isLeft(), isTrue);
    result.match((f) => expect(f, isA<Failure>()), (_) => fail('expected Left'));
  });
}
