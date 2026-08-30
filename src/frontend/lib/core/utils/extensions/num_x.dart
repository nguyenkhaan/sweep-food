extension NumX on num {
  /// Clamp to `[min, max]` and return as double.
  double clampd(double min, double max) => clamp(min, max).toDouble();
}

extension IntX on int {
  /// "1 nguyên liệu" / "3 nguyên liệu" — Vietnamese has no plural inflection,
  /// so this is just `"$this $noun"`; kept as a helper for intent + null-safety.
  String countLabel(String noun) => '$this $noun';
}
