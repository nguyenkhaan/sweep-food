/// Units used for pantry quantities and recipe amounts.
/// `wire` is the API/mock token; [label] is the Vietnamese display string.
enum MeasurementUnit {
  gram('g', 'g'),
  kilogram('kg', 'kg'),
  milliliter('ml', 'ml'),
  liter('l', 'lít'),
  piece('cai', 'cái'),
  fruit('qua', 'quả'),
  bunch('bo', 'bó'),
  box('hop', 'hộp'),
  pack('goi', 'gói'),
  bottle('chai', 'chai'),
  can('lon', 'lon'),
  slice('lat', 'lát'),
  spoon('thia', 'thìa');

  const MeasurementUnit(this.wire, this.label);
  final String wire;
  final String label;

  /// Backend `MeasurementUnit` enum tokens (`docs/DATABASE.txt`) mapped to the
  /// closest frontend unit. The backend only has these seven; the extras above
  /// (`qua`, `bo`, `chai`, …) come from mock fixtures and manual entry.
  static const Map<String, MeasurementUnit> _backendTokens = {
    'GRAM': MeasurementUnit.gram,
    'KG': MeasurementUnit.kilogram,
    'ML': MeasurementUnit.milliliter,
    'LITER': MeasurementUnit.liter,
    'PIECE': MeasurementUnit.piece,
    'PACK': MeasurementUnit.pack,
    // `OTHER` has no frontend equivalent; fall back to gram.
  };

  /// Accepts both the frontend `wire` tokens (`g`, `kg`, `cai`, …) and the
  /// backend enum tokens (`GRAM`, `KG`, `PIECE`, …). Unknown values fall back
  /// to [MeasurementUnit.gram].
  static MeasurementUnit fromWire(String value) {
    final trimmed = value.trim();
    for (final unit in MeasurementUnit.values) {
      if (unit.wire == trimmed) return unit;
    }
    return _backendTokens[trimmed.toUpperCase()] ?? MeasurementUnit.gram;
  }

  /// Weight units combine numerically; count units don't.
  bool get isWeight =>
      this == MeasurementUnit.gram || this == MeasurementUnit.kilogram;

  /// The backend `MeasurementUnit` enum token to send on writes. Units the
  /// backend has no equivalent for (`qua`, `bo`, `hop`, …) collapse to `OTHER`
  /// — a known display regression until the backend adds more units.
  String get backendWire => switch (this) {
    MeasurementUnit.gram => 'GRAM',
    MeasurementUnit.kilogram => 'KG',
    MeasurementUnit.milliliter => 'ML',
    MeasurementUnit.liter => 'LITER',
    MeasurementUnit.piece => 'PIECE',
    MeasurementUnit.pack => 'PACK',
    _ => 'OTHER',
  };
}
