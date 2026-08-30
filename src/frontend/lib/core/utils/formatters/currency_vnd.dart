import 'package:intl/intl.dart';

final _vnd = NumberFormat.decimalPattern('vi_VN');

/// Formats an amount in đồng, e.g. `39000` → `"39.000đ"`.
/// (Optional price displays only — SweepFood has no money-saved feature.)
String formatVnd(num amount) => '${_vnd.format(amount.round())}đ';

/// Rounded to the nearest thousand with a `~` prefix, e.g. `"~185.000đ"`.
String formatVndApprox(num amount) {
  final rounded = (amount / 1000).round() * 1000;
  return '~${_vnd.format(rounded)}đ';
}
