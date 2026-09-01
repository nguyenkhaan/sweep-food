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

  Future<void> registerAndSignIn(String phone, String password) async {
    await repo.register(phone: phone, password: password, name: 'Acct Live');
    final session = await repo.verifyRegisterAndLogin(
      phone: phone,
      otp: '123456',
      password: password,
    );
    session.fold((f) => fail('verify+login failed: $f'), (_) {});
  }

  test('updateProfile renames the account and me() reflects it', () async {
    await registerAndSignIn(uniquePhone(), 'secret12345');

    final updated = await repo.updateProfile(name: 'Renamed Live');
    expect(
      updated.fold((f) => fail('updateProfile failed: $f'), (u) => u.name),
      'Renamed Live',
    );

    final me = await repo.me();
    expect(me.fold((f) => fail('me failed: $f'), (u) => u.name), 'Renamed Live');
  });

  test('email change: request OTP -> verify -> me() shows the new email',
      () async {
    await registerAndSignIn(uniquePhone(), 'secret12345');
    final tail = DateTime.now().microsecondsSinceEpoch.toString();
    final email = 'live_$tail@example.com';

    final requested = await repo.requestEmailChange(email);
    expect(requested.fold((f) => -1, (ttl) => ttl), greaterThan(0));

    final confirmed = await repo.confirmEmailChange('123456');
    expect(confirmed.isRight(), isTrue);

    final me = await repo.me();
    expect(me.fold((f) => fail('me failed: $f'), (u) => u.email), email);
  });

  test('phone change: request OTP -> confirm -> me() shows the new phone',
      () async {
    await registerAndSignIn(uniquePhone(), 'secret12345');
    final newPhone = uniquePhone();

    final requested = await repo.requestPhoneChange(newPhone);
    expect(requested.fold((f) => -1, (ttl) => ttl), greaterThan(0));

    final confirmed = await repo.confirmPhoneChange('123456');
    expect(confirmed.isRight(), isTrue);

    final me = await repo.me();
    expect(me.fold((f) => fail('me failed: $f'), (u) => u.phone), newPhone);
  });

  test('password change: request OTP -> verify -> sign in with new password',
      () async {
    final phone = uniquePhone();
    await registerAndSignIn(phone, 'secret12345');

    final requested = await repo.requestPasswordChange();
    expect(requested.fold((f) => -1, (ttl) => ttl), greaterThan(0));

    final confirmed = await repo.confirmPasswordChange(
      phone: phone,
      otp: '123456',
      newPassword: 'brandnew12345',
    );
    expect(confirmed.isRight(), isTrue);

    // Sessions are revoked server-side; the new password must work.
    final again = await repo.login(phone: phone, password: 'brandnew12345');
    expect(again.isRight(), isTrue);
  });
}
