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
    test('maps the response and persists the token pair', () async {
      when(() => api.post(ApiPaths.login, body: any(named: 'body'))).thenAnswer(
        (_) async => {
          'user': {
            'id': 'u1',
            'name': 'Nguyễn Văn A',
            'email': 'ban@email.com',
            'dietary_preference': 'more_veg',
          },
          'access_token': 'at',
          'refresh_token': 'rt',
        },
      );

      final res = await repo.login(email: 'ban@email.com', password: 'secret123');

      final session = res.fold((f) => fail('expected Right, got $f'), (r) => r);
      expect(session.user.id, 'u1');
      expect(session.user.dietaryPreference, DietaryPreference.moreVeg);
      expect(session.accessToken, 'at');
      verify(() => store.writeTokens(accessToken: 'at', refreshToken: 'rt'))
          .called(1);
    });

    test('returns a Failure and does not persist when the client throws',
        () async {
      when(() => api.post(ApiPaths.login, body: any(named: 'body')))
          .thenThrow(Exception('boom'));

      final res = await repo.login(email: 'a@b.com', password: 'x');

      expect(res.isLeft(), isTrue);
      verifyNever(
        () => store.writeTokens(
          accessToken: any(named: 'accessToken'),
          refreshToken: any(named: 'refreshToken'),
        ),
      );
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
      when(() => api.get(ApiPaths.me)).thenThrow(
        const UnauthorizedFailure(),
      );
      final res = await repo.me();
      expect(res.isLeft(), isTrue);
      res.fold((f) => expect(f, isA<UnauthorizedFailure>()), (_) => fail('!'));
    });
  });
}
