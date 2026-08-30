import 'package:frontend/core/network/api_result.dart';
import 'package:frontend/core/network/network_providers.dart';
import 'package:frontend/core/storage/secure_storage.dart';
import 'package:frontend/core/storage/storage_providers.dart';
import 'package:frontend/core/utils/result.dart';
import 'package:frontend/features/auth/data/datasources/auth_remote_data_source.dart';
import 'package:frontend/features/auth/domain/entities/session.dart';
import 'package:frontend/features/auth/domain/entities/user.dart';
import 'package:frontend/features/auth/domain/repositories/auth_repository.dart';
import 'package:riverpod_annotation/riverpod_annotation.dart';

part 'auth_repository_impl.g.dart';

@Riverpod(keepAlive: true)
AuthRepository authRepository(Ref ref) => AuthRepositoryImpl(
      AuthRemoteDataSource(ref.watch(apiClientProvider)),
      ref.watch(secureStoreProvider),
    );

class AuthRepositoryImpl implements AuthRepository {
  AuthRepositoryImpl(this._remote, this._store);

  final AuthRemoteDataSource _remote;
  final SecureStore _store;

  @override
  Future<Result<Session>> register({
    required String name,
    required String email,
    required String password,
  }) =>
      runGuarded(() async {
        final dto = await _remote.register(
          name: name,
          email: email,
          password: password,
        );
        await _persist(dto.accessToken, dto.refreshToken);
        return dto.toEntity();
      });

  @override
  Future<Result<Session>> login({
    required String email,
    required String password,
  }) =>
      runGuarded(() async {
        final dto = await _remote.login(email: email, password: password);
        await _persist(dto.accessToken, dto.refreshToken);
        return dto.toEntity();
      });

  @override
  Future<Result<User>> me() =>
      runGuarded(() async => (await _remote.me()).toEntity());

  @override
  Future<Result<void>> requestPasswordReset(String email) =>
      guardVoid(() => _remote.requestPasswordReset(email));

  @override
  Future<Result<void>> logout() => guardVoid(() async {
        try {
          await _remote.logout(await _store.readRefreshToken());
        } catch (_) {
          // Best-effort: local sign-out proceeds even if the server call fails.
        }
        await _store.clear();
      });

  @override
  Future<bool> hasStoredSession() async {
    final token = await _store.readAccessToken();
    return token != null && token.isNotEmpty;
  }

  Future<void> _persist(String access, String refresh) =>
      _store.writeTokens(accessToken: access, refreshToken: refresh);
}
