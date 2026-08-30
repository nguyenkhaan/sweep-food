import 'package:dio/dio.dart';
import 'package:frontend/core/storage/secure_storage.dart';

/// Attaches the Bearer access token to every request.
///
/// **M0:** attach-only. **M5:** on a 401, call `/auth/refresh` once, retry the
/// original request, and if refresh fails invalidate the session (logout).
class AuthInterceptor extends Interceptor {
  AuthInterceptor(this._store);

  final SecureStore _store;

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

  // TODO(M5): onError → 401 → refresh + retry, else clear session.
}
