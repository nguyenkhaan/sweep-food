import 'package:sweepfood/app/theme/app_colors.dart' show ExpiryLevel;

export 'package:sweepfood/app/theme/app_colors.dart' show ExpiryLevel;

/// Buckets days-until-expiry into the 4-level urgency scale used for badge
/// colours, sort order and the waste-reduction count.
///
/// "Near expiry" (used by suggestion scoring) = [ExpiryLevel.expired],
/// [ExpiryLevel.critical] or [ExpiryLevel.soon] — i.e. `daysUntil <= 5`, with
/// the configurable `NEAR_EXPIRY_DAYS` (default 3) as the tighter default that
/// counts toward the waste-reduction metric.
abstract final class Expiry {
  static ExpiryLevel levelFromDays(int? daysUntilExpiry) {
    if (daysUntilExpiry == null) return ExpiryLevel.ok;
    if (daysUntilExpiry <= 0) return ExpiryLevel.expired;
    if (daysUntilExpiry <= 2) return ExpiryLevel.critical;
    if (daysUntilExpiry <= 5) return ExpiryLevel.soon;
    return ExpiryLevel.ok;
  }

  static bool isNearExpiry(int? daysUntilExpiry, {int threshold = 3}) =>
      daysUntilExpiry != null && daysUntilExpiry <= threshold;

  /// Days between [now] (date-only) and [expiryDate] (date-only). Negative = past.
  static int? daysUntil(DateTime? expiryDate, {DateTime? now}) {
    if (expiryDate == null) return null;
    final today = _dateOnly(now ?? DateTime.now());
    final due = _dateOnly(expiryDate);
    return due.difference(today).inDays;
  }

  static DateTime _dateOnly(DateTime d) => DateTime(d.year, d.month, d.day);
}
