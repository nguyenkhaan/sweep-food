/// Thrown by data sources (not repositories). Repositories catch these and
/// map them to a [Failure] via `error_mapper.dart`.
class AppException implements Exception {
  const AppException(this.message, {this.statusCode, this.cause});
  final String message;
  final int? statusCode;
  final Object? cause;

  @override
  String toString() => 'AppException($statusCode, $message)';
}

/// A mock fixture is missing or malformed (dev-only, [MockApiClient]).
class MockFixtureException extends AppException {
  const MockFixtureException(super.message);
}
