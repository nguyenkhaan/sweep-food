import 'package:dio/dio.dart';
import 'package:sweepfood/core/network/api_paths.dart';
import 'package:sweepfood/core/storage/secure_storage.dart';

/// Attaches the Bearer access token to every request and, on a 401, transparently
/// refreshes it once before retrying.
///
/// - `onRequest`: add `Authorization` unless the caller set `extra['skipAuth']`.
/// - `onError` + 401: call `/auth/refresh` once with the stored refresh token,
///   persist the new pair, replay the original request. If refresh fails (or
///   there's no refresh token), clear tokens and fire [onSessionExpired] so the
///   app logs out.
///
/// The refresh call goes through a bare [Dio] with no interceptors, so it can't
/// recurse back into this one.
class AuthInterceptor extends Interceptor {
  AuthInterceptor(
    this._store, {
    required String baseUrl,
    this.onSessionExpired,
  }) : _refresher = Dio(BaseOptions(baseUrl: baseUrl));

  final SecureStore _store;
  final Dio _refresher;
  final void Function()? onSessionExpired;

  static const _retriedKey = 'authRetried';

  @override
  Future<void> onRequest(
    RequestOptions options,
    RequestInterceptorHandler handler,
  ) async {
    if (options.extra['skipAuth'] != true) {
      final token = await _store.readAccessToken();
      if (token != null && token.isNotEmpty) {
        options.headers['Authorization'] = 'Bearer $token';
      }
    }
    handler.next(options);
  }

  @override
  Future<void> onError(
    DioException err,
    ErrorInterceptorHandler handler,
  ) async {
    final req = err.requestOptions;
    final isAuthFlow = req.path.startsWith('/auth/');
    final alreadyRetried = req.extra[_retriedKey] == true;

    if (err.response?.statusCode != 401 ||
        req.extra['skipAuth'] == true ||
        isAuthFlow ||
        alreadyRetried) {
      return handler.next(err);
    }

    final refreshed = await _tryRefresh();
    if (!refreshed) {
      await _store.clear();
      onSessionExpired?.call();
      return handler.next(err);
    }

    try {
      final token = await _store.readAccessToken();
      final retry = req
        ..extra[_retriedKey] = true
        ..headers['Authorization'] = 'Bearer $token';
      final response = await _refresher.fetch<dynamic>(retry);
      return handler.resolve(response);
    } on DioException catch (e) {
      return handler.next(e);
    }
  }

  Future<bool> _tryRefresh() async {
    final refreshToken = await _store.readRefreshToken();
    if (refreshToken == null || refreshToken.isEmpty) return false;
    try {
      final res = await _refresher.post<Map<String, dynamic>>(
        ApiPaths.refresh,
        data: {'refresh_token': refreshToken},
      );
      final data = res.data;
      if (data == null) return false;
      final access = data['access_token'] as String?;
      final refresh = (data['refresh_token'] as String?) ?? refreshToken;
      if (access == null || access.isEmpty) return false;
      await _store.writeTokens(accessToken: access, refreshToken: refresh);
      return true;
    } on DioException {
      return false;
    }
  }
}
