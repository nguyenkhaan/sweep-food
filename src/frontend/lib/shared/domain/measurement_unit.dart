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

  static MeasurementUnit fromWire(String value) =>
      MeasurementUnit.values.firstWhere(
        (u) => u.wire == value,
        orElse: () => MeasurementUnit.gram,
      );

  /// Weight units combine numerically; count units don't.
  bool get isWeight =>
      this == MeasurementUnit.gram || this == MeasurementUnit.kilogram;
}
