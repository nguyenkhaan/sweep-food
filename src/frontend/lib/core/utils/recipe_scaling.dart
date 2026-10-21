import 'dart:math' as math;

import 'package:sweepfood/shared/domain/measurement_unit.dart';

/// Scales one recipe line by a serving multiplier. Mirrors the backend rule in
/// `src/service/recipe_quantity.py` so the dish screen and the cook preview
/// agree: seasonings scale sub-linearly (taste does not grow with portions) and
/// every line is rounded to a cookable step, never below one step.
double scaleRecipeQuantity(
  double quantity,
  MeasurementUnit unit,
  double factor, {
  required bool seasoning,
}) {
  if (quantity <= 0 || factor == 1) return quantity;
  final effective = seasoning ? math.pow(factor, 0.7).toDouble() : factor;
  final scaled = quantity * effective;
  final step = _stepFor(scaled, unit);
  return math.max((scaled / step).roundToDouble() * step, step);
}

double _stepFor(double value, MeasurementUnit unit) {
  if (!unit.isWeight && !unit.isVolume) return 0.5;
  if (unit == MeasurementUnit.kilogram || unit == MeasurementUnit.liter) {
    return 0.05;
  }
  if (value < 10) return 0.5;
  if (value < 50) return 1;
  if (value < 200) return 5;
  return 10;
}
