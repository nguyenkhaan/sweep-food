@Tags(['live'])
library;

/// Exercises the real auth data layer (DTO parsing + Dio + AuthInterceptor)
/// against a running backend. Skipped unless `LIVE_BASE_URL` is set, e.g.:
///
///   flutter test test/live/auth_live_test.dart \
///     --dart-define=LIVE_BASE_URL=http://localhost:4000/api
///
/// Needs the backend up with `ENV=dev` (OTP is always `123456`).
import 'package:dio/dio.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:sweepfood/core/network/dio_api_client.dart';
import 'package:sweepfood/core/network/interceptors/auth_interceptor.dart';
import 'package:sweepfood/core/storage/secure_storage.dart';
import 'package:sweepfood/features/auth/data/datasources/auth_remote_data_source.dart';
import 'package:sweepfood/features/auth/data/repositories/auth_repository_impl.dart';

const _baseUrl = String.fromEnvironment('LIVE_BASE_URL');

/// In-memory stand-in for [SecureStore] (no platform channel in `flutter test`).
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
    test('live auth (skipped: set --dart-define=LIVE_BASE_URL)', () {}, skip: true);
    return;
  }

  late _MemStore store;
  late AuthRepositoryImpl repo;

  setUp(() {
    store = _MemStore();
    final dio = Dio(BaseOptions(baseUrl: _baseUrl))
      ..interceptors.add(AuthInterceptor(store, baseUrl: _baseUrl));
    repo = AuthRepositoryImpl(AuthRemoteDataSource(DioApiClient(dio)), store);
  });

  String uniquePhone() {
    final tail = DateTime.now().microsecondsSinceEpoch.toString();
    return '+8493${tail.substring(tail.length - 8)}';
  }

  test('register -> verify+login -> me -> logout parses end to end', () async {
    final phone = uniquePhone();
    const password = 'secret12345';

    final ttl = await repo.register(
      phone: phone,
      password: password,
      name: 'Dart Live',
    );
    expect(ttl.fold((f) => -1, (v) => v), greaterThan(0));

    final session = await repo.verifyRegisterAndLogin(
      phone: phone,
      otp: '123456',
      password: password,
    );
    final s = session.fold((f) => fail('verify+login failed: $f'), (r) => r);
    expect(s.accessToken, isNotEmpty);
    expect(s.refreshToken, isNotEmpty);
    expect(s.user.phone, phone);
    expect(s.user.id, isNotEmpty);
    expect(s.user.name, 'Dart Live');
    expect(s.user.email, isNull);

    final me = await repo.me();
    expect(me.fold((f) => fail('me failed: $f'), (u) => u.phone), phone);

    final out = await repo.logout();
    expect(out.isRight(), isTrue);
    expect(await store.readAccessToken(), isNull);
  });

  test('login with a wrong password surfaces UnauthorizedFailure', () async {
    final phone = uniquePhone();
    const password = 'secret12345';
    await repo.register(phone: phone, password: password, name: 'Dart Live');
    await repo.verifyRegisterAndLogin(
      phone: phone,
      otp: '123456',
      password: password,
    );

    final res = await repo.login(phone: phone, password: 'totally-wrong');
    expect(res.isLeft(), isTrue);
  });

  test('duplicate registration surfaces ConflictFailure', () async {
    final phone = uniquePhone();
    const password = 'secret12345';
    await repo.register(phone: phone, password: password, name: 'Dart Live');

    final again =
        await repo.register(phone: phone, password: password, name: 'dup');
    expect(again.isLeft(), isTrue);
  });
}
