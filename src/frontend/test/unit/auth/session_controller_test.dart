import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:mocktail/mocktail.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:sweepfood/core/error/failure.dart';
import 'package:sweepfood/core/storage/prefs.dart';
import 'package:sweepfood/core/storage/secure_storage.dart';
import 'package:sweepfood/core/storage/storage_providers.dart';
import 'package:sweepfood/core/utils/result.dart';
import 'package:sweepfood/features/auth/data/repositories/auth_repository_impl.dart';
import 'package:sweepfood/features/auth/domain/entities/session.dart';
import 'package:sweepfood/features/auth/domain/entities/user.dart';
import 'package:sweepfood/features/auth/domain/repositories/auth_repository.dart';
import 'package:sweepfood/features/auth/presentation/controllers/session_controller.dart';

class _MockAuthRepository extends Mock implements AuthRepository {}

class _MockSecureStore extends Mock implements SecureStore {}

class _MockPreferences extends Mock implements SharedPreferences {}

const _user = User(
  id: 'u1',
  phone: '+84901234567',
  name: 'A',
  email: 'a@b.com',
);
const _session = Session(user: _user, accessToken: 'at', refreshToken: 'rt');

void main() {
  late _MockAuthRepository repo;
  late _MockSecureStore store;
  late _MockPreferences preferences;

  ProviderContainer makeContainer() {
    final c = ProviderContainer(
      overrides: [
        authRepositoryProvider.overrideWithValue(repo),
        secureStoreProvider.overrideWithValue(store),
        sharedPreferencesProvider.overrideWithValue(preferences),
      ],
    );
    addTearDown(c.dispose);
    return c;
  }

  setUp(() {
    repo = _MockAuthRepository();
    store = _MockSecureStore();
    preferences = _MockPreferences();
    when(() => store.readAccessToken()).thenAnswer((_) async => 'at');
    when(() => store.readRefreshToken()).thenAnswer((_) async => 'rt');
    when(store.clear).thenAnswer((_) async {});
    when(() => preferences.getString(any())).thenReturn(null);
    when(
      () => preferences.setString(any(), any()),
    ).thenAnswer((_) async => true);
    when(() => preferences.remove(any())).thenAnswer((_) async => true);
  });

  test('cold start with no stored token resolves to signed-out', () async {
    when(repo.hasStoredSession).thenAnswer((_) async => false);
    final c = makeContainer();

    final result = await c.read(sessionControllerProvider.future);

    expect(result, isNull);
    verifyNever(repo.me);
  });

  test(
    'cold start with a valid token revives the session from the profile',
    () async {
      when(repo.hasStoredSession).thenAnswer((_) async => true);
      when(repo.me).thenAnswer((_) async => const Right<Failure, User>(_user));
      final c = makeContainer();

      final result = await c.read(sessionControllerProvider.future);

      expect(result?.user.id, 'u1');
      expect(result?.accessToken, 'at');
    },
  );

  test('a failing profile call resolves to signed-out (no throw)', () async {
    when(repo.hasStoredSession).thenAnswer((_) async => true);
    when(
      repo.me,
    ).thenAnswer((_) async => const Left<Failure, User>(ServerFailure()));
    final c = makeContainer();

    expect(await c.read(sessionControllerProvider.future), isNull);
  });

  test('logIn moves the notifier to AsyncData(session)', () async {
    when(repo.hasStoredSession).thenAnswer((_) async => false);
    when(
      () => repo.login(
        phone: any(named: 'phone'),
        password: any(named: 'password'),
      ),
    ).thenAnswer((_) async => const Right<Failure, Session>(_session));
    final c = makeContainer();
    await c.read(sessionControllerProvider.future);

    await c
        .read(sessionControllerProvider.notifier)
        .logIn(phone: '+84901234567', password: 'secret123');

    expect(c.read(sessionControllerProvider).asData?.value, _session);
  });

  test('logIn rethrows the Failure on bad credentials', () async {
    when(repo.hasStoredSession).thenAnswer((_) async => false);
    when(
      () => repo.login(
        phone: any(named: 'phone'),
        password: any(named: 'password'),
      ),
    ).thenAnswer(
      (_) async => const Left<Failure, Session>(UnauthorizedFailure()),
    );
    final c = makeContainer();
    await c.read(sessionControllerProvider.future);

    expect(
      () => c
          .read(sessionControllerProvider.notifier)
          .logIn(phone: '+84901234567', password: 'nope'),
      throwsA(isA<UnauthorizedFailure>()),
    );
  });

  test('logOut calls the repo and clears the session', () async {
    when(repo.hasStoredSession).thenAnswer((_) async => true);
    when(repo.me).thenAnswer((_) async => const Right<Failure, User>(_user));
    when(repo.logout).thenAnswer((_) async => const Right<Failure, void>(null));
    final c = makeContainer();
    await c.read(sessionControllerProvider.future);

    await c.read(sessionControllerProvider.notifier).logOut();

    expect(c.read(sessionControllerProvider).asData?.value, isNull);
    verify(repo.logout).called(1);
  });
}
