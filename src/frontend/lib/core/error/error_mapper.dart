import 'dart:async';
import 'dart:io';

import 'package:dio/dio.dart';
import 'package:frontend/core/error/app_exception.dart';
import 'package:frontend/core/error/failure.dart';

/// Turns an exception thrown by a data source into a [Failure].
///
/// Usage in a repository:
/// ```dart
/// try {
///   final dto = await _remote.fetch();
///   return right(dto.toEntity());
/// } catch (e, st) {
///   return left(mapError(e, st));
/// }
/// ```
Failure mapError(Object error, [StackTrace? stackTrace]) {
  if (error is Failure) return error;

  if (error is DioException) return _fromDio(error, stackTrace);

  if (error is SocketException) {
    return NetworkFailure(cause: error, stackTrace: stackTrace);
  }
  if (error is TimeoutException) {
    return TimeoutFailure(cause: error, stackTrace: stackTrace);
  }
  if (error is FormatException || error is TypeError) {
    return ParseFailure(cause: error, stackTrace: stackTrace);
  }
  if (error is MockFixtureException) {
    return ServerFailure(message: error.message, cause: error);
  }
  if (error is AppException) {
    return _fromStatus(error.statusCode, error.message, error, stackTrace);
  }

  return UnknownFailure(cause: error, stackTrace: stackTrace);
}

Failure _fromDio(DioException e, StackTrace? st) {
  switch (e.type) {
    case DioExceptionType.connectionTimeout:
    case DioExceptionType.sendTimeout:
    case DioExceptionType.receiveTimeout:
      return TimeoutFailure(cause: e, stackTrace: st);
    case DioExceptionType.connectionError:
      return NetworkFailure(cause: e, stackTrace: st);
    case DioExceptionType.cancel:
      return UnknownFailure(cause: e, stackTrace: st);
    case DioExceptionType.badCertificate:
      return ServerFailure(cause: e, stackTrace: st);
    // ignore: no_default_cases
    default: // badResponse, unknown, transformTimeout, …
      final res = e.response;
      final data = res?.data;
      String? serverMsg;
      var fields = const <String, String>{};
      if (data is Map) {
        final err = data['error'];
        if (err is Map) {
          serverMsg = err['message']?.toString();
          final f = err['fields'];
          if (f is Map) {
            fields = f.map((k, v) => MapEntry(k.toString(), v.toString()));
          }
        } else {
          serverMsg = (data['message'] ?? data['detail'])?.toString();
        }
      }
      return _fromStatus(res?.statusCode, serverMsg, e, st, fields);
  }
}

Failure _fromStatus(
  int? status,
  String? serverMsg,
  Object cause,
  StackTrace? st, [
  Map<String, String> fields = const {},
]) {
  return switch (status) {
    401 => UnauthorizedFailure(cause: cause, stackTrace: st),
    402 => QuotaExceededFailure(cause: cause, stackTrace: st),
    403 => ForbiddenFailure(cause: cause, stackTrace: st),
    404 => NotFoundFailure(message: serverMsg, cause: cause, stackTrace: st),
    422 => ValidationFailure(
        message: serverMsg,
        fieldErrors: fields,
        cause: cause,
        stackTrace: st,
      ),
    final s when s != null && s >= 500 =>
      ServerFailure(message: serverMsg, cause: cause, stackTrace: st),
    _ => UnknownFailure(cause: cause, stackTrace: st),
  };
}
