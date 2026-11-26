import 'package:riverpod_annotation/riverpod_annotation.dart';
import 'package:sweepfood/core/analytics/analytics_events.dart';
import 'package:sweepfood/core/analytics/analytics_provider.dart';
import 'package:sweepfood/core/config/app_constants.dart';
import 'package:sweepfood/core/storage/prefs.dart';
import 'package:sweepfood/core/utils/logger.dart';
import 'package:sweepfood/features/auth/data/repositories/auth_repository_impl.dart';
import 'package:sweepfood/features/auth/presentation/controllers/session_controller.dart';
import 'package:sweepfood/shared/domain/dietary_preference.dart';

part 'onboarding_controller.g.dart';

/// Whether the user has finished (or skipped) onboarding. Persisted so it
/// survives a logout/login on the same device. Watched by `route_guards.dart`:
/// a signed-in user with `false` here is pinned to `/onboarding/diet`.
@Riverpod(keepAlive: true)
class OnboardingController extends _$OnboardingController {
  @override
  bool build() =>
      ref
          .watch(sharedPreferencesProvider)
          .getBool(AppConstants.kOnboardingDone) ??
      false;

  Future<void> complete() async {
    state = true;
    ref.read(analyticsProvider).log(AnalyticsEvents.onboardingCompleted);
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

/// The persisted diet mode chosen at onboarding (A-05) and synced with
/// `users.preferences.diet` via `PATCH /users/profile`.
@Riverpod(keepAlive: true)
class DietaryPreferenceController extends _$DietaryPreferenceController {
  @override
  DietaryPreference? build() {
    final userDiet = ref
        .watch(sessionControllerProvider)
        .asData
        ?.value
        ?.user
        .nutritionProfile
        .diet;
    final raw = ref
        .watch(sharedPreferencesProvider)
        .getString(AppConstants.kDietaryPreference);
    if (userDiet != null) return userDiet;
    return raw == null ? null : DietaryPreference.fromWire(raw);
  }

  /// Updates local storage and optionally syncs `diet` to `PATCH /users/profile`.
  Future<void> set(
    DietaryPreference? preference, {
    bool syncRemote = true,
  }) async {
    state = preference;
    ref
        .read(analyticsProvider)
        .setUserProperty(
          AnalyticsUserProps.dietaryPreference,
          preference?.wire,
        );
    final prefs = ref.read(sharedPreferencesProvider);
    if (preference == null) {
      await prefs.remove(AppConstants.kDietaryPreference);
      return;
    }
    await prefs.setString(AppConstants.kDietaryPreference, preference.wire);

    if (!syncRemote) return;
    final session = ref.read(sessionControllerProvider).asData?.value;
    if (session == null) return;

    final result = await ref
        .read(authRepositoryProvider)
        .updateProfile(preferences: {'diet': preference.wire});
    if (!ref.mounted) return;
    result.fold(
      (failure) => log.w(
        'Onboarding diet sync failed (kept locally): ${failure.message}',
      ),
      (user) =>
          ref.read(sessionControllerProvider.notifier).applyUpdatedUser(user),
    );
  }
}
