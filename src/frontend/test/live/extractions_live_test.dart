@Tags(['live'])
library;

import 'dart:io';
import 'package:dio/dio.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:sweepfood/core/network/dio_api_client.dart';
import 'package:sweepfood/core/network/interceptors/auth_interceptor.dart';
import 'package:sweepfood/core/storage/secure_storage.dart';
import 'package:sweepfood/features/auth/data/datasources/auth_remote_data_source.dart';
import 'package:sweepfood/features/auth/data/repositories/auth_repository_impl.dart';
import 'package:sweepfood/features/ingest/data/datasources/scan_remote_data_source.dart';
import 'package:sweepfood/features/ingest/data/repositories/scan_repository_impl.dart';
import 'package:sweepfood/features/ingest/domain/entities/scan_type.dart';

const _baseUrl = String.fromEnvironment('LIVE_BASE_URL');

class _MemStore implements SecureStore {
  String? _access;
  String? _refresh;
  @override
  Future<String?> readAccessToken() async => _access;
  @override
  Future<String?> readRefreshToken() async => _refresh;
  @override
  Future<void> writeTokens({
    required String accessToken,
    required String refreshToken,
  }) async {
    _access = accessToken;
    _refresh = refreshToken;
  }

  @override
  Future<void> clear() async {
    _access = null;
    _refresh = null;
  }
}

void main() {
  if (_baseUrl.isEmpty) {
    test('live extractions (skipped: set --dart-define=LIVE_BASE_URL)', () {},
        skip: true);
    return;
  }

  late DioApiClient api;
  late ScanRepositoryImpl scanRepo;
  late Directory tempDir;
  late File samplePng;
  late File sampleMp3;

  setUpAll(() async {
    tempDir = await Directory.systemTemp.createTemp('extractions_live_');
    // Minimal valid 1x1 PNG
    samplePng = File('${tempDir.path}/label.png');
    await samplePng.writeAsBytes([
      0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a, 0x00, 0x00, 0x00, 0x0d,
      0x49, 0x48, 0x44, 0x52, 0x00, 0x00, 0x00, 0x01, 0x00, 0x00, 0x00, 0x01,
      0x08, 0x06, 0x00, 0x00, 0x00, 0x1f, 0x15, 0xc4, 0x89, 0x00, 0x00, 0x00,
      0x0a, 0x49, 0x44, 0x41, 0x54, 0x78, 0x9c, 0x63, 0x00, 0x01, 0x00, 0x00,
      0x05, 0x00, 0x01, 0x0d, 0x0a, 0x2d, 0xb4, 0x00, 0x00, 0x00, 0x00, 0x49,
      0x45, 0x4e, 0x44, 0xae, 0x42, 0x60, 0x82,
    ]);

    // Sample audio file
    sampleMp3 = File('${tempDir.path}/voice.mp3');
    await sampleMp3.writeAsBytes(List.filled(1024, 0));
  });

  tearDownAll(() async {
    if (await tempDir.exists()) {
      await tempDir.delete(recursive: true);
    }
  });

  setUp(() async {
    final store = _MemStore();
    final dio = Dio(BaseOptions(baseUrl: _baseUrl))
      ..interceptors.add(AuthInterceptor(store, baseUrl: _baseUrl));
    api = DioApiClient(dio);
    final auth = AuthRepositoryImpl(AuthRemoteDataSource(api), store);

    final tail = DateTime.now().microsecondsSinceEpoch.toString();
    final phone = '+8493${tail.substring(tail.length - 8)}';
    const password = 'secret12345';
    await auth.register(
      phone: phone,
      password: password,
      name: 'Extractions Live',
    );
    final session = await auth.verifyRegisterAndLogin(
      phone: phone,
      otp: '123456',
      password: password,
    );
    session.fold((f) => fail('sign-in failed: '), (_) {});

    scanRepo = ScanRepositoryImpl(ScanRemoteDataSource(api));
  });

  test('POST /extractions/ocr/label extracts label from uploaded image', () async {
    final result = await scanRepo.scanLabel(samplePng.path);
    final job = result.fold((f) => fail('scanLabel failed: '), (j) => j);

    expect(job.type, ScanType.label);
    expect(job.status, ScanStatus.completed);
    expect(job.sourcePath, samplePng.path);
    expect(job.hasItems, isTrue);
    expect(job.items.first.name, isNotEmpty);
    expect(job.items.first.quantity, greaterThan(0));
  });

  test('POST /extractions/ocr/invoice extracts invoice line items', () async {
    final result = await scanRepo.scanReceipt(samplePng.path);
    final job = result.fold((f) => fail('scanReceipt failed: '), (j) => j);

    expect(job.type, ScanType.receipt);
    expect(job.status, ScanStatus.completed);
    expect(job.sourcePath, samplePng.path);
    expect(job.hasItems, isTrue);
    expect(job.items.length, greaterThanOrEqualTo(1));
    for (final item in job.items) {
      expect(item.name, isNotEmpty);
      expect(item.quantity, greaterThan(0));
    }
  });

  test('POST /extractions/asr transcribes and extracts ingredient fields', () async {
    final result = await scanRepo.scanVoice(audioPath: sampleMp3.path);
    final job = result.fold((f) => fail('scanVoice failed: '), (j) => j);

    expect(job.type, ScanType.voice);
    expect(job.status, ScanStatus.completed);
    expect(job.hasItems, isTrue);
    expect(job.items.first.name, isNotEmpty);
  });

  test('POST /extractions/barcode looks up product by query param', () async {
    final result = await scanRepo.lookupBarcode('8934567890123');
    final job = result.fold((f) => fail('lookupBarcode failed: '), (j) => j);

    expect(job.status, ScanStatus.completed);
    expect(job.hasItems, isTrue);
    expect(job.items.first.name, isNotEmpty);
  });
}
