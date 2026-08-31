import 'package:dio/dio.dart';
import 'package:riverpod_annotation/riverpod_annotation.dart';
import 'package:sweepfood/core/config/app_config_provider.dart';
import 'package:sweepfood/core/config/app_constants.dart';
import 'package:sweepfood/core/network/api_client.dart';
import 'package:sweepfood/core/network/dio_api_client.dart';
import 'package:sweepfood/core/network/interceptors/auth_interceptor.dart';
import 'package:sweepfood/core/network/interceptors/logging_interceptor.dart';
import 'package:sweepfood/core/network/mock_api_client.dart';
import 'package:sweepfood/core/network/session_expired.dart';
import 'package:sweepfood/core/storage/storage_providers.dart';

part 'network_providers.g.dart';

/// The live Dio instance (only actually hit when `backend == live`).
@Riverpod(keepAlive: true)
Dio dio(Ref ref) {
  final config = ref.watch(appConfigProvider);
  final d = Dio(
    BaseOptions(
      baseUrl: config.apiBaseUrl,
      connectTimeout: AppConstants.connectTimeout,
      receiveTimeout: AppConstants.receiveTimeout,
      headers: {'Accept': 'application/json'},
      contentType: Headers.jsonContentType,
    ),
  );
  d.interceptors.addAll([
    AuthInterceptor(
      ref.watch(secureStoreProvider),
      baseUrl: config.apiBaseUrl,
      onSessionExpired: () => ref.read(sessionExpiredProvider.notifier).fire(),
    ),
    LoggingInterceptor(),
  ]);
  return d;
}

/// The app's [ApiClient] — mock or live, chosen by `AppConfig.backend`.
/// All repositories depend on this, never on Dio directly.
@Riverpod(keepAlive: true)
ApiClient apiClient(Ref ref) {
  final config = ref.watch(appConfigProvider);
  return config.backend.isMock
      ? MockApiClient()
      : DioApiClient(ref.watch(dioProvider));
}
