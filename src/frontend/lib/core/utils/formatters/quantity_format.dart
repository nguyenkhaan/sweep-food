import 'package:sweepfood/shared/domain/measurement_unit.dart';

/// "500 g", "1 bó", "3 quả", "1,5 kg". Drops a trailing `.0`, uses a comma
/// decimal separator (vi convention).
String formatQuantity(num value, MeasurementUnit unit) {
  final n = value == value.roundToDouble()
      ? value.round().toString()
      : value.toStringAsFixed(1).replaceAll('.', ',');
  return '$n ${unit.label}';
}
