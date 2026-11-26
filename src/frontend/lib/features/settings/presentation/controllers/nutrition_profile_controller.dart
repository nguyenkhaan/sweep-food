import 'package:flutter/foundation.dart';
import 'package:riverpod_annotation/riverpod_annotation.dart';
import 'package:sweepfood/features/auth/data/repositories/auth_repository_impl.dart';
import 'package:sweepfood/features/auth/presentation/controllers/session_controller.dart';
import 'package:sweepfood/features/home/presentation/controllers/home_controller.dart';
import 'package:sweepfood/features/onboarding/presentation/controllers/onboarding_controller.dart';
import 'package:sweepfood/features/suggestions/presentation/controllers/suggestion_list_controller.dart';
import 'package:sweepfood/l10n/app_localizations.dart';
import 'package:sweepfood/shared/domain/dietary_preference.dart';
import 'package:sweepfood/shared/domain/nutrition_profile.dart';

part 'nutrition_profile_controller.g.dart';

@immutable
class NutritionProfileFormState {
  const NutritionProfileFormState({
    this.profile = const NutritionProfile(),
    this.isSaving = false,
    this.hasChanges = false,
    this.errorMessage,
  });

  final NutritionProfile profile;
  final bool isSaving;
  final bool hasChanges;
  final String? errorMessage;

  NutritionProfileFormState copyWith({
    NutritionProfile? profile,
    bool? isSaving,
    bool? hasChanges,
    String? errorMessage,
    bool clearError = false,
  }) {
    return NutritionProfileFormState(
      profile: profile ?? this.profile,
      isSaving: isSaving ?? this.isSaving,
      hasChanges: hasChanges ?? this.hasChanges,
      errorMessage: clearError ? null : errorMessage ?? this.errorMessage,
    );
  }
}

/// Manages editing & saving the 5-field Nutrition Profile via `PATCH /users/profile`.
@riverpod
class NutritionProfileController extends _$NutritionProfileController {
  @override
  NutritionProfileFormState build() {
    final userProfile =
        ref
            .watch(sessionControllerProvider)
            .asData
            ?.value
            ?.user
            .nutritionProfile ??
        const NutritionProfile();
    return NutritionProfileFormState(profile: userProfile);
  }

  void setHouseholdSize(int value) {
    final clamped = value.clamp(
      NutritionProfile.minHouseholdSize,
      NutritionProfile.maxHouseholdSize,
    );
    if (clamped == state.profile.householdSize) return;
    state = state.copyWith(
      profile: state.profile.copyWith(householdSize: clamped),
      hasChanges: true,
      clearError: true,
    );
  }

  void setDiet(DietaryPreference diet) {
    if (diet == state.profile.diet) return;
    state = state.copyWith(
      profile: state.profile.copyWith(diet: diet),
      hasChanges: true,
      clearError: true,
    );
  }

  void toggleHealthCondition(HealthCondition condition) {
    final current = List<HealthCondition>.from(state.profile.healthConditions);
    if (current.contains(condition)) {
      current.remove(condition);
    } else {
      current.add(condition);
    }
    state = state.copyWith(
      profile: state.profile.copyWith(healthConditions: current),
      hasChanges: true,
      clearError: true,
    );
  }

  void toggleAllergy(AllergyGroup allergy) {
    final current = List<AllergyGroup>.from(state.profile.allergies);
    if (current.contains(allergy)) {
      current.remove(allergy);
    } else {
      current.add(allergy);
    }
    state = state.copyWith(
      profile: state.profile.copyWith(allergies: current),
      hasChanges: true,
      clearError: true,
    );
  }

  bool addDislikedIngredient(String raw) {
    final cleaned = raw.trim();
    if (cleaned.isEmpty) return false;
    final current = state.profile.dislikedIngredients;
    if (current.length >= NutritionProfile.maxDislikedIngredients) {
      return false;
    }
    final exists = current.any(
      (item) => item.toLowerCase() == cleaned.toLowerCase(),
    );
    if (exists) return false;

    state = state.copyWith(
      profile: state.profile.copyWith(
        dislikedIngredients: [...current, cleaned],
      ),
      hasChanges: true,
      clearError: true,
    );
    return true;
  }

  void removeDislikedIngredient(String item) {
    final next = state.profile.dislikedIngredients
        .where((e) => e != item)
        .toList();
    state = state.copyWith(
      profile: state.profile.copyWith(dislikedIngredients: next),
      hasChanges: true,
      clearError: true,
    );
  }

  /// Persists the nutrition profile to `PATCH /users/profile`, refreshes the
  /// cached user, and invalidates suggestions so results reflect the changes.
  Future<bool> save(AppL10n l10n) async {
    if (state.isSaving) return false;
    state = state.copyWith(isSaving: true, clearError: true);

    final result = await ref
        .read(authRepositoryProvider)
        .updateProfile(preferences: state.profile.toPreferencesMap());
    if (!ref.mounted) return false;

    return result.fold(
      (failure) {
        state = state.copyWith(
          isSaving: false,
          errorMessage: failure.localizedMessage(l10n),
        );
        return false;
      },
      (user) async {
        ref.read(sessionControllerProvider.notifier).applyUpdatedUser(user);
        await ref
            .read(dietaryPreferenceControllerProvider.notifier)
            .set(user.nutritionProfile.diet, syncRemote: false);
        if (!ref.mounted) return true;

        ref
          ..invalidate(suggestionListControllerProvider)
          ..invalidate(homeDashboardProvider);

        state = state.copyWith(
          profile: user.nutritionProfile,
          isSaving: false,
          hasChanges: false,
          clearError: true,
        );
        return true;
      },
    );
  }
}
