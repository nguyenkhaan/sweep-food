@Tags(['live'])
library;

/// Exercises the FCM device-registration REST surface (`/users/me/devices`)
/// against a running backend. No real Firebase token is needed — the backend
/// only validates length/shape.
///
///   flutter test test/live/device_live_test.dart --run-skipped \
///     --dart-define=LIVE_BASE_URL=http://127.0.0.1:4000/api
import 'package:dio/dio.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:sweepfood/core/network/dio_api_client.dart';
import 'package:sweepfood/core/network/interceptors/auth_interceptor.dart';
import 'package:sweepfood/core/storage/secure_storage.dart';
import 'package:sweepfood/features/auth/data/datasources/auth_remote_data_source.dart';
import 'package:sweepfood/features/auth/data/repositories/auth_repository_impl.dart';
import 'package:sweepfood/features/notifications/data/datasources/device_remote_data_source.dart';
import 'package:sweepfood/features/notifications/data/repositories/device_repository_impl.dart';

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
    test('live device (skipped: set --dart-define=LIVE_BASE_URL)', () {},
        skip: true);
    return;
  }

  late DeviceRepositoryImpl devices;

  setUp(() async {
    final store = _MemStore();
    final dio = Dio(BaseOptions(baseUrl: _baseUrl))
      ..interceptors.add(AuthInterceptor(store, baseUrl: _baseUrl));
    final api = DioApiClient(dio);
    final auth = AuthRepositoryImpl(AuthRemoteDataSource(api), store);

    final tail = DateTime.now().microsecondsSinceEpoch.toString();
    final phone = '+8493${tail.substring(tail.length - 8)}';
    const password = 'secret12345';
    await auth.register(phone: phone, password: password, name: 'Device Live');
    final session = await auth.verifyRegisterAndLogin(
      phone: phone,
      otp: '123456',
      password: password,
    );
    session.fold((f) => fail('sign-in failed: $f'), (_) {});

    devices = DeviceRepositoryImpl(DeviceRemoteDataSource(api));
  });

  test('register then unregister a device token round-trips', () async {
    final token = 'fake-fcm-token-${DateTime.now().microsecondsSinceEpoch}-abcdef';

    final registered = await devices.register(token, platform: 'ANDROID');
    final deviceId =
        registered.fold((f) => fail('register failed: $f'), (id) => id);
    expect(deviceId, isNotEmpty);

    final removed = await devices.unregister(deviceId);
    expect(removed.isRight(), isTrue);
  });

  test('unregister on an unknown device id surfaces a Failure', () async {
    final res =
        await devices.unregister('00000000-0000-0000-0000-000000000000');
    expect(res.isLeft(), isTrue);
  });
}
