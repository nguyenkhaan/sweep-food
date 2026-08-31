import 'package:flutter_test/flutter_test.dart';
import 'package:mocktail/mocktail.dart';
import 'package:sweepfood/core/error/failure.dart';
import 'package:sweepfood/core/network/api_client.dart';
import 'package:sweepfood/core/network/api_paths.dart';
import 'package:sweepfood/core/storage/secure_storage.dart';
import 'package:sweepfood/features/auth/data/datasources/auth_remote_data_source.dart';
import 'package:sweepfood/features/auth/data/repositories/auth_repository_impl.dart';
import 'package:sweepfood/shared/domain/dietary_preference.dart';

class _MockApiClient extends Mock implements ApiClient {}

class _MockSecureStore extends Mock implements SecureStore {}

Map<String, dynamic> _tokenPair() => {
      'access_token': 'at',
      'refresh_token': 'rt',
      'token_type': 'bearer',
      'access_expires_in_seconds': 900,
      'refresh_expires_in_seconds': 2592000,
      'session_id': 's1',
    };

Map<String, dynamic> _profile({String? diet}) => {
      'user_id': 'u1',
      'name': 'Nguyễn Văn A',
      'phone': '+84901234567',
      'phone_verified_at': null,
      'email': 'ban@email.com',
      'email_verified_at': null,
      'preferences': {if (diet != null) 'dietary_preference': diet},
    };

void main() {
  late _MockApiClient api;
  late _MockSecureStore store;
  late AuthRepositoryImpl repo;

  setUp(() {
    api = _MockApiClient();
    store = _MockSecureStore();
    repo = AuthRepositoryImpl(AuthRemoteDataSource(api), store);
    when(
      () => store.writeTokens(
        accessToken: any(named: 'accessToken'),
        refreshToken: any(named: 'refreshToken'),
      ),
    ).thenAnswer((_) async {});
    when(store.clear).thenAnswer((_) async {});
  });

  group('login()', () {
    test('signs in, persists the token pair, then loads the profile', () async {
      when(() => api.post(ApiPaths.login, body: any(named: 'body')))
          .thenAnswer((_) async => _tokenPair());
      when(() => api.get(ApiPaths.profile))
          .thenAnswer((_) async => _profile(diet: 'more_veg'));

      final res = await repo.login(phone: '+84901234567', password: 'secret123');

      final session = res.fold((f) => fail('expected Right, got $f'), (r) => r);
      expect(session.user.id, 'u1');
      expect(session.user.phone, '+84901234567');
      expect(session.user.dietaryPreference, DietaryPreference.moreVeg);
      expect(session.accessToken, 'at');
      verify(() => store.writeTokens(accessToken: 'at', refreshToken: 'rt'))
          .called(1);
    });

    test('returns a Failure and does not persist when login throws', () async {
      when(() => api.post(ApiPaths.login, body: any(named: 'body')))
          .thenThrow(Exception('boom'));

      final res = await repo.login(phone: '+84900000000', password: 'x');

      expect(res.isLeft(), isTrue);
      verifyNever(
        () => store.writeTokens(
          accessToken: any(named: 'accessToken'),
          refreshToken: any(named: 'refreshToken'),
        ),
      );
    });
  });

  group('register()', () {
    test('returns the OTP lifetime in seconds', () async {
      when(() => api.post(ApiPaths.register, body: any(named: 'body')))
          .thenAnswer((_) async => {'otp': '123456', 'expires_in_seconds': 300});

      final res = await repo.register(
        phone: '+84901234567',
        password: 'secret123',
        name: 'A',
      );

      expect(res.fold((f) => fail('$f'), (ttl) => ttl), 300);
    });
  });

  group('logout()', () {
    test('clears local tokens even if the network call fails', () async {
      when(() => store.readRefreshToken()).thenAnswer((_) async => 'rt');
      when(() => api.post(ApiPaths.logout, body: any(named: 'body')))
          .thenThrow(Exception('offline'));

      final res = await repo.logout();

      expect(res.isRight(), isTrue);
      verify(store.clear).called(1);
    });
  });

  group('hasStoredSession()', () {
    test('is false when no access token is stored', () async {
      when(() => store.readAccessToken()).thenAnswer((_) async => null);
      expect(await repo.hasStoredSession(), isFalse);
    });

    test('is true when an access token is stored', () async {
      when(() => store.readAccessToken()).thenAnswer((_) async => 'at');
      expect(await repo.hasStoredSession(), isTrue);
    });
  });

  group('me()', () {
    test('surfaces a 401 as an UnauthorizedFailure', () async {
      when(() => api.get(ApiPaths.profile)).thenThrow(
        const UnauthorizedFailure(),
      );
      final res = await repo.me();
      expect(res.isLeft(), isTrue);
      res.fold((f) => expect(f, isA<UnauthorizedFailure>()), (_) => fail('!'));
    });
  });
}
