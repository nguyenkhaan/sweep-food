import 'package:freezed_annotation/freezed_annotation.dart';

part 'active_session.freezed.dart';

/// One active login session for the signed-in user, from `GET /auth/sessions`.
///
/// Distinct from [Session] (the live in-app auth state): this is a row in the
/// "devices signed into your account" list that the user can revoke one by one
/// via `DELETE /auth/sessions/{id}`.
@freezed
abstract class ActiveSession with _$ActiveSession {
  const ActiveSession._();

  const factory ActiveSession({
    required String id,
    String? ipAddress,
    String? userAgent,
    required DateTime expiresAt,
    required DateTime createdAt,
    DateTime? lastUsedAt,
  }) = _ActiveSession;

  /// A short human label for the device, derived from the raw [userAgent].
  /// Falls back to the IP address, then a generic string.
  String get deviceLabel {
    final ip = ipAddress?.trim() ?? '';
    final ua = userAgent?.trim() ?? '';
    if (ua.isEmpty) {
      return ip.isNotEmpty ? ip : 'Thiết bị không xác định';
    }

    final lower = ua.toLowerCase();
    final os = switch (lower) {
      _ when lower.contains('android') => 'Android',
      _ when lower.contains('iphone') || lower.contains('ios') => 'iPhone',
      _ when lower.contains('ipad') => 'iPad',
      _ when lower.contains('mac os') || lower.contains('macintosh') => 'macOS',
      _ when lower.contains('windows') => 'Windows',
      _ when lower.contains('linux') => 'Linux',
      _ => null,
    };
    final app = switch (lower) {
      _ when lower.contains('sweepfood') || lower.contains('dart') => 'Ứng dụng SweepFood',
      _ when lower.contains('chrome') => 'Chrome',
      _ when lower.contains('firefox') => 'Firefox',
      _ when lower.contains('safari') => 'Safari',
      _ => null,
    };
    if (os != null && app != null) return '$os · $app';
    if (os != null) return os;
    if (app != null) return app;
    // Unknown UA — show a trimmed version rather than the whole header.
    return ua.length > 40 ? '${ua.substring(0, 40)}…' : ua;
  }
}
