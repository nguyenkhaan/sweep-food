/// One local file to attach to a multipart request.
typedef UploadFile = ({String field, String path, String? filename});

/// HTTP surface the repositories talk to. Two implementations:
/// [DioApiClient] (live) and `MockApiClient` (serves `assets/mock/*.json`).
///
/// Methods return the decoded JSON body (`Map`, `List`, scalar or `null`).
/// On a non-2xx response an implementation throws — repositories catch and map
/// via `error_mapper.dart`.
abstract interface class ApiClient {
  Future<dynamic> get(String path, {Map<String, dynamic>? query});

  Future<dynamic> post(
    String path, {
    Object? body,
    Map<String, dynamic>? query,
    Map<String, String>? headers,
  });

  Future<dynamic> put(String path, {Object? body});

  Future<dynamic> patch(
    String path, {
    Object? body,
    Map<String, String>? headers,
  });

  Future<dynamic> delete(
    String path, {
    Object? body,
    Map<String, String>? headers,
  });

  Future<dynamic> postMultipart(
    String path, {
    Map<String, dynamic> fields = const {},
    List<UploadFile> files = const [],
  });
}
