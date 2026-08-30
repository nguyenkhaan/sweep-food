import 'package:frontend/core/error/error_mapper.dart';
import 'package:frontend/core/utils/result.dart';

/// Runs [call] (a data-source invocation), maps [json] → [T] with [parse], and
/// wraps everything in a [Result] so repositories stay tiny:
///
/// ```dart
/// Future<Result<PantrySummary>> summary() => guard(
///   () => _api.get(ApiPaths.pantrySummary),
///   (json) => PantrySummaryDto.fromJson(json as Map<String, dynamic>).toEntity(),
/// );
/// ```
Future<Result<T>> guard<T>(
  Future<dynamic> Function() call,
  T Function(dynamic json) parse,
) async {
  try {
    final json = await call();
    return Right(parse(json));
  } catch (e, st) {
    return Left(mapError(e, st));
  }
}

/// Like [guard] but for calls whose response body is ignored.
Future<Result<void>> guardVoid(Future<dynamic> Function() call) async {
  try {
    await call();
    return const Right(null);
  } catch (e, st) {
    return Left(mapError(e, st));
  }
}
