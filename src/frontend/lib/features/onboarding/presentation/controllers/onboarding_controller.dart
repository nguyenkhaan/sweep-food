import 'package:frontend/core/config/app_constants.dart';
import 'package:frontend/core/storage/prefs.dart';
import 'package:frontend/shared/domain/dietary_preference.dart';
import 'package:riverpod_annotation/riverpod_annotation.dart';

part 'onboarding_controller.g.dart';

/// Whether the user has finished (or skipped) onboarding. Persisted so it
/// survives a logout/login on the same device. Watched by `route_guards.dart`:
/// a signed-in user with `false` here is pinned to `/onboarding/diet`.
@Riverpod(keepAlive: true)
class OnboardingController extends _$OnboardingController {
  @override
  bool build() =>
      ref.watch(sharedPreferencesProvider).getBool(AppConstants.kOnboardingDone) ??
      false;

  Future<void> complete() async {
    state = true;
    await ref
        .read(sharedPreferencesProvider)
        .setBool(AppConstants.kOnboardingDone, true);
  }

  /// Only for tests / "đăng xuất rồi vào lại" flows that want the tour again.
  Future<void> reset() async {
    state = false;
    await ref
        .read(sharedPreferencesProvider)
        .remove(AppConstants.kOnboardingDone);
  }
}

/// The persisted meal-ranking preference (N-01). Chosen at onboarding (A-05),
/// later editable in Cài đặt → Tùy chọn. Feeds the `P` term of suggestion
/// scoring — `SuggestionFilterController` seeds its default from here.
@Riverpod(keepAlive: true)
class DietaryPreferenceController extends _$DietaryPreferenceController {
  @override
  DietaryPreference? build() {
    final raw =
        ref.watch(sharedPreferencesProvider).getString(AppConstants.kDietaryPreference);
    return raw == null ? null : DietaryPreference.fromWire(raw);
  }

  Future<void> set(DietaryPreference? preference) async {
    state = preference;
    final prefs = ref.read(sharedPreferencesProvider);
    if (preference == null) {
      await prefs.remove(AppConstants.kDietaryPreference);
    } else {
      await prefs.setString(AppConstants.kDietaryPreference, preference.wire);
    }
  }
}
