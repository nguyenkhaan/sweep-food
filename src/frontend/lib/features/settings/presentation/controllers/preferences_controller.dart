import 'package:frontend/core/config/app_constants.dart';
import 'package:frontend/core/storage/prefs.dart';
import 'package:frontend/features/onboarding/presentation/controllers/onboarding_controller.dart';
import 'package:frontend/features/settings/domain/entities/app_preferences.dart';
import 'package:frontend/shared/domain/dietary_preference.dart';
import 'package:frontend/shared/domain/measurement_unit.dart';
import 'package:riverpod_annotation/riverpod_annotation.dart';

part 'preferences_controller.g.dart';

/// P-03 Tùy chọn. Reads/writes SharedPreferences. Dietary preference is
/// delegated to [DietaryPreferenceController] (shared with onboarding A-05 and
/// the suggestion scorer) so there's a single source of truth.
@Riverpod(keepAlive: true)
class PreferencesController extends _$PreferencesController {
  @override
  AppPreferences build() {
    final prefs = ref.watch(sharedPreferencesProvider);
    return AppPreferences(
      dietaryPreference: ref.watch(dietaryPreferenceControllerProvider) ??
          DietaryPreference.balanced,
      defaultUnit: MeasurementUnit.fromWire(
        prefs.getString(AppConstants.kDefaultUnit) ?? MeasurementUnit.gram.wire,
      ),
    );
  }

  Future<void> setDietaryPreference(DietaryPreference value) =>
      ref.read(dietaryPreferenceControllerProvider.notifier).set(value);

  Future<void> setDefaultUnit(MeasurementUnit unit) async {
    await ref
        .read(sharedPreferencesProvider)
        .setString(AppConstants.kDefaultUnit, unit.wire);
    ref.invalidateSelf();
  }
}
