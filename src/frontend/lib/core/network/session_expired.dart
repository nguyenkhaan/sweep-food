import 'package:riverpod_annotation/riverpod_annotation.dart';

part 'session_expired.g.dart';

/// A one-way "the session just died" signal.
///
/// [AuthInterceptor] can't reach the auth feature (that would cycle:
/// session → repo → apiClient → dio → session). Instead, when a token refresh
/// fails it bumps this counter; [SessionController] listens and tears the
/// session down, which flips the router back to `/welcome`.
@Riverpod(keepAlive: true)
class SessionExpired extends _$SessionExpired {
  @override
  int build() => 0;

  void fire() => state = state + 1;
}
