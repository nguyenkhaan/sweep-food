import 'package:flutter_test/flutter_test.dart';
import 'package:sweepfood/shared/domain/measurement_unit.dart';

void main() {
  group('MeasurementUnit.fromWire', () {
    test('accepts the frontend wire tokens', () {
      expect(MeasurementUnit.fromWire('g'), MeasurementUnit.gram);
      expect(MeasurementUnit.fromWire('kg'), MeasurementUnit.kilogram);
      expect(MeasurementUnit.fromWire('ml'), MeasurementUnit.milliliter);
      expect(MeasurementUnit.fromWire('cai'), MeasurementUnit.piece);
      expect(MeasurementUnit.fromWire('goi'), MeasurementUnit.pack);
    });

    test('accepts the backend enum tokens', () {
      expect(MeasurementUnit.fromWire('GRAM'), MeasurementUnit.gram);
      expect(MeasurementUnit.fromWire('KG'), MeasurementUnit.kilogram);
      expect(MeasurementUnit.fromWire('ML'), MeasurementUnit.milliliter);
      expect(MeasurementUnit.fromWire('LITER'), MeasurementUnit.liter);
      expect(MeasurementUnit.fromWire('PIECE'), MeasurementUnit.piece);
      expect(MeasurementUnit.fromWire('PACK'), MeasurementUnit.pack);
    });

    test('is case- and whitespace-tolerant for backend tokens', () {
      expect(MeasurementUnit.fromWire(' gram '), MeasurementUnit.gram);
      expect(MeasurementUnit.fromWire('Kg'), MeasurementUnit.kilogram);
    });

    test('maps OTHER to its own count-like unit, unknown falls back to gram', () {
      expect(MeasurementUnit.fromWire('OTHER'), MeasurementUnit.other);
      expect(MeasurementUnit.fromWire('parsec'), MeasurementUnit.gram);
      expect(MeasurementUnit.fromWire(''), MeasurementUnit.gram);
    });
  });
}
