import 'package:freezed_annotation/freezed_annotation.dart';
import 'package:sweepfood/features/auth/domain/entities/user.dart';

part 'session.freezed.dart';

/// A live authenticated session: the [user] plus the JWT pair.
///
/// The tokens also live in `SecureStore` (that's what the [AuthInterceptor]
/// reads); they're mirrored here so a freshly-restored session is self-contained
/// and controllers don't have to hit secure storage again.
@freezed
abstract class Session with _$Session {
  const Session._();

  const factory Session({
    required User user,
    required String accessToken,
    required String refreshToken,
  }) = _Session;

  bool get isAuthenticated => accessToken.isNotEmpty;
}
