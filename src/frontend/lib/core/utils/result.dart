import 'package:fpdart/fpdart.dart';
import 'package:sweepfood/core/error/failure.dart';

export 'package:fpdart/fpdart.dart' show Either, Left, Right, Option, Some, None;

/// The repository return type: `Right(value)` on success, `Left(failure)` on error.
typedef Result<T> = Either<Failure, T>;

/// Async variant.
typedef FutureResult<T> = Future<Either<Failure, T>>;

extension ResultX<T> on Result<T> {
  /// Value or `null` (drops the failure). Use `fold` when you need the failure.
  T? get valueOrNull => fold((_) => null, (r) => r);

  bool get isSuccess => isRight();
  bool get isFailure => isLeft();
}
