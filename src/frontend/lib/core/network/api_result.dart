import 'package:sweepfood/core/error/error_mapper.dart';
import 'package:sweepfood/core/utils/result.dart';

/// Runs [body] (which calls a typed data source + maps DTO → entity) and wraps
/// the outcome in a [Result]. Keeps repositories to one line per method:
///
/// ```dart
/// Future<Result<PantrySummary>> summary() => runGuarded(() async {
///   final dto = await _remote.summary();
///   return dto.toEntity();
/// });
/// ```
Future<Result<T>> runGuarded<T>(Future<T> Function() body) async {
  try {
    return Right(await body());
  } catch (e, st) {
    return Left(mapError(e, st));
  }
}

/// Lower-level variant for callers that already have raw JSON in hand.
Future<Result<T>> guard<T>(
  Future<dynamic> Function() call,
  T Function(dynamic json) parse,
) async {
  try {
    return Right(parse(await call()));
  } catch (e, st) {
    return Left(mapError(e, st));
  }
}

/// [runGuarded] for a call whose result is discarded.
Future<Result<void>> guardVoid(Future<void> Function() call) async {
  try {
    await call();
    return const Right(null);
  } catch (e, st) {
    return Left(mapError(e, st));
  }
}
