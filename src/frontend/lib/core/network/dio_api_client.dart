import 'package:dio/dio.dart';
import 'package:sweepfood/core/network/api_client.dart';

/// [ApiClient] backed by Dio. Used when `AppConfig.backend == Backend.live`.
/// Error handling is left to the caller (repositories catch `DioException`).
class DioApiClient implements ApiClient {
  DioApiClient(this._dio);

  final Dio _dio;

  @override
  Future<dynamic> get(String path, {Map<String, dynamic>? query}) async =>
      (await _dio.get<dynamic>(path, queryParameters: query)).data;

  @override
  Future<dynamic> post(
    String path, {
    Object? body,
    Map<String, dynamic>? query,
  }) async =>
      (await _dio.post<dynamic>(path, data: body, queryParameters: query)).data;

  @override
  Future<dynamic> put(String path, {Object? body}) async =>
      (await _dio.put<dynamic>(path, data: body)).data;

  @override
  Future<dynamic> patch(String path, {Object? body}) async =>
      (await _dio.patch<dynamic>(path, data: body)).data;

  @override
  Future<dynamic> delete(String path, {Object? body}) async =>
      (await _dio.delete<dynamic>(path, data: body)).data;

  @override
  Future<dynamic> postMultipart(
    String path, {
    Map<String, dynamic> fields = const {},
    List<UploadFile> files = const [],
  }) async {
    final form = FormData.fromMap({
      ...fields,
      for (final f in files)
        f.field: await MultipartFile.fromFile(f.path, filename: f.filename),
    });
    return (await _dio.post<dynamic>(path, data: form)).data;
  }
}
