import 'package:intl/intl.dart';

final _dmy = DateFormat('dd/MM/yyyy');
final _dm = DateFormat('dd/MM');

extension DateTimeX on DateTime {
  DateTime get dateOnly => DateTime(year, month, day);

  bool isSameDay(DateTime other) =>
      year == other.year && month == other.month && day == other.day;

  /// Whole days from `this` (date-only) to [other] (date-only). Negative = past.
  int daysUntil(DateTime other) =>
      other.dateOnly.difference(dateOnly).inDays;

  String get ddMMyyyy => _dmy.format(this);
  String get ddMM => _dm.format(this);
}

extension NullableDateTimeX on DateTime? {
  String get ddMMyyyyOrDash => this == null ? '—' : _dmy.format(this!);
}
