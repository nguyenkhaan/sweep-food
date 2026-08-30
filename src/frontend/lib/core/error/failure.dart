/// A user-facing failure. Repositories return `Either<Failure, T>`; controllers
/// turn a [Failure] into an [AsyncError] the UI renders via `AsyncValueWidget`.
///
/// Every subtype carries a Vietnamese [message] safe to show directly.
sealed class Failure {
  const Failure(this.message, {this.cause, this.stackTrace});

  final String message;
  final Object? cause;
  final StackTrace? stackTrace;

  @override
  String toString() => '$runtimeType($message)';
}

/// No connectivity / DNS / socket error.
class NetworkFailure extends Failure {
  const NetworkFailure({super.cause, super.stackTrace})
      : super('Không có kết nối mạng. Kiểm tra lại và thử lại.');
}

/// Request took too long.
class TimeoutFailure extends Failure {
  const TimeoutFailure({super.cause, super.stackTrace})
      : super('Máy chủ phản hồi quá lâu. Vui lòng thử lại.');
}

/// 401 — token missing / expired and refresh failed. Triggers logout.
class UnauthorizedFailure extends Failure {
  const UnauthorizedFailure({super.cause, super.stackTrace})
      : super('Phiên đăng nhập đã hết hạn. Đăng nhập lại nhé.');
}

/// 403 — authenticated but not allowed.
class ForbiddenFailure extends Failure {
  const ForbiddenFailure({super.cause, super.stackTrace})
      : super('Bạn không có quyền thực hiện thao tác này.');
}

/// 404.
class NotFoundFailure extends Failure {
  const NotFoundFailure({String? message, super.cause, super.stackTrace})
      : super(message ?? 'Không tìm thấy dữ liệu.');
}

/// 402 — freemium quota reached. Not expected in the MVP (all unlocked) but
/// kept so the type is complete for v2.
class QuotaExceededFailure extends Failure {
  const QuotaExceededFailure({super.cause, super.stackTrace})
      : super('Bạn đã dùng hết lượt cho tính năng này trong tháng.');
}

/// 422 — validation errors, keyed by field for form display.
class ValidationFailure extends Failure {
  const ValidationFailure({
    String? message,
    this.fieldErrors = const {},
    super.cause,
    super.stackTrace,
  }) : super(message ?? 'Dữ liệu chưa hợp lệ.');

  final Map<String, String> fieldErrors;
}

/// 5xx or an unexpected server payload.
class ServerFailure extends Failure {
  const ServerFailure({String? message, super.cause, super.stackTrace})
      : super(message ?? 'Máy chủ đang gặp sự cố. Thử lại sau ít phút.');
}

/// Response body could not be parsed into the expected shape.
class ParseFailure extends Failure {
  const ParseFailure({super.cause, super.stackTrace})
      : super('Dữ liệu trả về không đúng định dạng.');
}

/// Anything not matched above.
class UnknownFailure extends Failure {
  const UnknownFailure({super.cause, super.stackTrace})
      : super('Đã xảy ra lỗi không mong muốn.');
}
