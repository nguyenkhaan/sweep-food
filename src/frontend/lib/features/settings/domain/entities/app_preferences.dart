import 'package:flutter/foundation.dart';
import 'package:sweepfood/shared/domain/dietary_preference.dart';
import 'package:sweepfood/shared/domain/measurement_unit.dart';

/// User-tunable app preferences (P-03). Stored locally in SharedPreferences —
/// there's no server profile in the MVP. Theme mode lives in its own
/// `themeModeControllerProvider`; this covers the rest.
@immutable
class AppPreferences {
  const AppPreferences({
    this.dietaryPreference = DietaryPreference.balanced,
    this.defaultUnit = MeasurementUnit.gram,
    this.languageTag = 'vi',
  });

  final DietaryPreference dietaryPreference;

  /// The unit pre-selected in the add-ingredient form.
  final MeasurementUnit defaultUnit;

  /// BCP-47 tag. MVP ships `vi` only; the row is shown but fixed.
  final String languageTag;

  String get languageLabel => switch (languageTag) {
        'en' => 'English',
        _ => 'Tiếng Việt',
      };

  AppPreferences copyWith({
    DietaryPreference? dietaryPreference,
    MeasurementUnit? defaultUnit,
    String? languageTag,
  }) {
    return AppPreferences(
      dietaryPreference: dietaryPreference ?? this.dietaryPreference,
      defaultUnit: defaultUnit ?? this.defaultUnit,
      languageTag: languageTag ?? this.languageTag,
    );
  }
}
