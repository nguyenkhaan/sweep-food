import 'package:sweepfood/l10n/app_localizations.dart';

/// A user-facing failure. Repositories return `Either<Failure, T>`; controllers
/// turn a [Failure] into an [AsyncError] the UI renders via `AsyncValueWidget`.
///
/// [message] is a plain fallback safe for logs and for surfaces without a
/// [BuildContext]; UI code should prefer [localizedMessage].
sealed class Failure {
  const Failure(this.message, {this.cause, this.stackTrace});

  final String message;
  final Object? cause;
  final StackTrace? stackTrace;

  /// The message localized for the current locale. Failures that can carry a
  /// server-supplied [message] (404 / 422 / 5xx) return it as-is.
  String localizedMessage(AppL10n l10n) => switch (this) {
    NetworkFailure() => l10n.failNetwork,
    TimeoutFailure() => l10n.failTimeout,
    UnauthorizedFailure() => l10n.failUnauthorized,
    ForbiddenFailure() => l10n.failForbidden,
    QuotaExceededFailure() => l10n.failQuota,
    ParseFailure() => l10n.failParse,
    UnknownFailure() => l10n.failUnknown,
    NotFoundFailure() || ValidationFailure() || ServerFailure() => message,
  };

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
