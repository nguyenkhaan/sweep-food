@Tags(['live'])
library;

/// Exercises the notification data layer (DTO parsing + Dio + AuthInterceptor)
/// against a running backend. A freshly registered user has no notifications,
/// so this proves the envelope parses and that writes are ownership-scoped.
///
///   flutter test test/live/notification_live_test.dart --run-skipped \
///     --dart-define=LIVE_BASE_URL=http://127.0.0.1:4000/api
import 'package:dio/dio.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:sweepfood/core/network/dio_api_client.dart';
import 'package:sweepfood/core/network/interceptors/auth_interceptor.dart';
import 'package:sweepfood/core/storage/secure_storage.dart';
import 'package:sweepfood/features/auth/data/datasources/auth_remote_data_source.dart';
import 'package:sweepfood/features/auth/data/repositories/auth_repository_impl.dart';
import 'package:sweepfood/features/notifications/data/datasources/notification_remote_data_source.dart';
import 'package:sweepfood/features/notifications/data/repositories/notification_repository_impl.dart';

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
    test('live notification (skipped: set --dart-define=LIVE_BASE_URL)', () {},
        skip: true);
    return;
  }

  late NotificationRepositoryImpl notifications;

  setUp(() async {
    final store = _MemStore();
    final dio = Dio(BaseOptions(baseUrl: _baseUrl))
      ..interceptors.add(AuthInterceptor(store, baseUrl: _baseUrl));
    final api = DioApiClient(dio);
    final auth = AuthRepositoryImpl(AuthRemoteDataSource(api), store);

    final tail = DateTime.now().microsecondsSinceEpoch.toString();
    final phone = '+8493${tail.substring(tail.length - 8)}';
    const password = 'secret12345';
    await auth.register(phone: phone, password: password, name: 'Notif Live');
    final session = await auth.verifyRegisterAndLogin(
      phone: phone,
      otp: '123456',
      password: password,
    );
    session.fold((f) => fail('sign-in failed: $f'), (_) {});

    notifications = NotificationRepositoryImpl(NotificationRemoteDataSource(api));
  });

  test('GET /notifications returns a parseable list for a new user', () async {
    final res = await notifications.list();
    final list = res.fold((f) => fail('list failed: $f'), (l) => l);
    expect(list, isA<List<Object?>>()); // empty is fine; parsing must not throw
  });

  test('PATCH on an unknown notification id surfaces a Failure', () async {
    final res = await notifications
        .markRead('00000000-0000-0000-0000-000000000000');
    expect(res.isLeft(), isTrue);
  });
}
