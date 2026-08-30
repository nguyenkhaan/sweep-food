/// Relative expiry text for badges and list rows (spec: "còn 2 ngày" /
/// "quá hạn 1 ngày" / "Hôm nay").
String expiryText(int? daysUntilExpiry) {
  if (daysUntilExpiry == null) return 'Không có hạn';
  if (daysUntilExpiry < 0) {
    final d = -daysUntilExpiry;
    return d == 1 ? 'Quá hạn 1 ngày' : 'Quá hạn $d ngày';
  }
  if (daysUntilExpiry == 0) return 'Hôm nay';
  if (daysUntilExpiry == 1) return 'Còn 1 ngày';
  if (daysUntilExpiry < 30) return 'Còn $daysUntilExpiry ngày';
  if (daysUntilExpiry < 365) {
    final months = (daysUntilExpiry / 30).round();
    return 'Còn $months tháng';
  }
  final years = (daysUntilExpiry / 365).round();
  return years == 1 ? 'Còn 1 năm' : 'Còn $years năm';
}

/// "còn X ngày" lowercase form for inline sentences.
String expiryTextInline(int? daysUntilExpiry) {
  final t = expiryText(daysUntilExpiry);
  return t.isEmpty ? t : t[0].toLowerCase() + t.substring(1);
}
