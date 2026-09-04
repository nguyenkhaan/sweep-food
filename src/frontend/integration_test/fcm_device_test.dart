// On-device FCM smoke test. Run on a physical Android device with the backend
// reachable (adb reverse tcp:4000 tcp:4000):
//
//   flutter test integration_test/fcm_device_test.dart -d <device-id> \
//     --dart-define=LIVE_BASE_URL=http://127.0.0.1:4000/api
//
// It obtains a real FCM registration token, registers it via
// POST /users/me/devices, then asks the backend to deliver a push through
// POST /api/send-notification and asserts Firebase accepted it. Background the
// app afterwards to see the notification land in the tray.
import 'package:dio/dio.dart';
import 'package:firebase_core/firebase_core.dart';
import 'package:firebase_messaging/firebase_messaging.dart';
import 'package:flutter/foundation.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:integration_test/integration_test.dart';
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
  IntegrationTestWidgetsFlutterBinding.ensureInitialized();

  testWidgets('FCM: token → register → backend push accepted', (tester) async {
    expect(_baseUrl, isNotEmpty, reason: 'pass --dart-define=LIVE_BASE_URL');

    await Firebase.initializeApp();
    await FirebaseMessaging.instance.requestPermission();
    final token = await FirebaseMessaging.instance.getToken();
    debugPrint('>>> FCM_TOKEN=$token');
    expect(token, isNotNull, reason: 'device produced no FCM token');
    expect(token!.length, greaterThan(20));

    final store = _MemStore();
    final dio = Dio(BaseOptions(baseUrl: _baseUrl))
      ..interceptors.add(AuthInterceptor(store, baseUrl: _baseUrl));
    final api = DioApiClient(dio);
    final auth = AuthRepositoryImpl(AuthRemoteDataSource(api), store);

    final tail = DateTime.now().microsecondsSinceEpoch.toString();
    final phone = '+8493${tail.substring(tail.length - 8)}';
    const password = 'secret12345';
    await auth.register(phone: phone, password: password, name: 'FCM Device');
    final session = await auth.verifyRegisterAndLogin(
      phone: phone,
      otp: '123456',
      password: password,
    );
    session.fold((f) => fail('sign-in failed: $f'), (_) {});

    final devices = DeviceRepositoryImpl(DeviceRemoteDataSource(api));
    final registered = await devices.register(token, platform: 'ANDROID');
    final deviceId =
        registered.fold((f) => fail('device register failed: $f'), (id) => id);
    debugPrint('>>> DEVICE_ID=$deviceId');

    // Ask the backend to deliver a real push to this token.
    final res = await api.post(
      '/send-notification',
      body: {
        'device_token': token,
        'title': 'SweepFood',
        'body': 'Push notification hoạt động 🎉',
        'data': {'notification_id': 'integration-test'},
      },
    );
    debugPrint('>>> SEND_NOTIFICATION_RESPONSE=$res');
    expect(
      (res as Map)['message_id'],
      isNotNull,
      reason: 'backend did not report a Firebase message id',
    );

    debugPrint('>>> Background the app now to see the notification in the tray.');
  });
}
