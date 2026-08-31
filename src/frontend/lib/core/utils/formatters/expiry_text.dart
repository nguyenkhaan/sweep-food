import 'package:frontend/l10n/app_localizations.dart';

/// Relative expiry text for badges and list rows (spec: "còn 2 ngày" /
/// "quá hạn 1 ngày" / "Hôm nay").
String expiryText(int? daysUntilExpiry, AppL10n l10n) {
  if (daysUntilExpiry == null) return l10n.expiryNone;
  if (daysUntilExpiry < 0) return l10n.expiryOverdueDays(-daysUntilExpiry);
  if (daysUntilExpiry == 0) return l10n.expiryToday;
  if (daysUntilExpiry < 30) return l10n.expiryInDays(daysUntilExpiry);
  if (daysUntilExpiry < 365) {
    return l10n.expiryInMonths((daysUntilExpiry / 30).round());
  }
  return l10n.expiryInYears((daysUntilExpiry / 365).round());
}

/// "còn X ngày" lowercase form for inline sentences.
String expiryTextInline(int? daysUntilExpiry, AppL10n l10n) {
  final t = expiryText(daysUntilExpiry, l10n);
  return t.isEmpty ? t : t[0].toLowerCase() + t.substring(1);
}
