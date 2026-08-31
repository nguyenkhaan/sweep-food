import 'package:riverpod_annotation/riverpod_annotation.dart';
import 'package:sweepfood/core/network/api_result.dart';
import 'package:sweepfood/core/network/network_providers.dart';
import 'package:sweepfood/core/storage/secure_storage.dart';
import 'package:sweepfood/core/storage/storage_providers.dart';
import 'package:sweepfood/core/utils/result.dart';
import 'package:sweepfood/features/auth/data/datasources/auth_remote_data_source.dart';
import 'package:sweepfood/features/auth/domain/entities/session.dart';
import 'package:sweepfood/features/auth/domain/entities/user.dart';
import 'package:sweepfood/features/auth/domain/repositories/auth_repository.dart';

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
  Future<Result<int>> register({
    required String phone,
    required String password,
    String? name,
    String? email,
  }) =>
      runGuarded(() async {
        final dto = await _remote.register(
          phone: phone,
          password: password,
          name: name,
          email: email,
        );
        return dto.expiresInSeconds;
      });

  @override
  Future<Result<int>> resendRegisterOtp(String phone) => runGuarded(
        () async => (await _remote.resendRegisterOtp(phone)).expiresInSeconds,
      );

  @override
  Future<Result<Session>> verifyRegisterAndLogin({
    required String phone,
    required String otp,
    required String password,
  }) =>
      runGuarded(() async {
        await _remote.verifyRegister(phone: phone, otp: otp);
        return _loginAndBuildSession(phone: phone, password: password);
      });

  @override
  Future<Result<Session>> login({
    required String phone,
    required String password,
  }) =>
      runGuarded(
        () => _loginAndBuildSession(phone: phone, password: password),
      );

  @override
  Future<Result<User>> me() =>
      runGuarded(() async => (await _remote.profile()).toEntity());

  @override
  Future<Result<int>> requestPasswordReset(String phone) => runGuarded(
        () async => (await _remote.requestPasswordReset(phone)).expiresInSeconds,
      );

  @override
  Future<Result<void>> confirmPasswordReset({
    required String phone,
    required String otp,
    required String newPassword,
  }) =>
      guardVoid(
        () => _remote.confirmPasswordReset(
          phone: phone,
          otp: otp,
          newPassword: newPassword,
        ),
      );

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

  /// Sign in, persist the token pair, then fetch the profile to build a
  /// self-contained [Session] (the login response carries no user block).
  Future<Session> _loginAndBuildSession({
    required String phone,
    required String password,
  }) async {
    final tokens = await _remote.login(phone: phone, password: password);
    await _store.writeTokens(
      accessToken: tokens.accessToken,
      refreshToken: tokens.refreshToken,
    );
    final user = (await _remote.profile()).toEntity();
    return Session(
      user: user,
      accessToken: tokens.accessToken,
      refreshToken: tokens.refreshToken,
    );
  }
}
