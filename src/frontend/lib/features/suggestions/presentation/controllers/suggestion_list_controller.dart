import 'package:riverpod_annotation/riverpod_annotation.dart';
import 'package:sweepfood/core/config/app_constants.dart';
import 'package:sweepfood/features/suggestions/data/repositories/suggestion_repository_impl.dart';
import 'package:sweepfood/features/suggestions/domain/entities/dish_suggestion.dart';
import 'package:sweepfood/features/suggestions/domain/entities/suggestion_request.dart';
import 'package:sweepfood/shared/domain/dietary_preference.dart';

part 'suggestion_list_controller.g.dart';

/// Fixed cook-time cap offered by the "≤ 30 phút" quick chip.
const _quickCookMinutes = 30;

/// UI filter state for S-01. Maps to a [SuggestionRequest] for the API.
class SuggestionFilter {
  const SuggestionFilter({
    this.mealType,
    this.quickCookOnly = false,
    this.dietaryPreference,
  });

  /// `null` = "Tất cả".
  final MealType? mealType;
  final bool quickCookOnly;
  final DietaryPreference? dietaryPreference;

  SuggestionFilter copyWith({
    MealType? mealType,
    bool? quickCookOnly,
    DietaryPreference? dietaryPreference,
    bool clearMealType = false,
    bool clearDietaryPreference = false,
  }) {
    return SuggestionFilter(
      mealType: clearMealType ? null : mealType ?? this.mealType,
      quickCookOnly: quickCookOnly ?? this.quickCookOnly,
      dietaryPreference: clearDietaryPreference
          ? null
          : dietaryPreference ?? this.dietaryPreference,
    );
  }

  SuggestionRequest toRequest() => SuggestionRequest(
        mealType: mealType,
        maxCookTimeMin: quickCookOnly ? _quickCookMinutes : null,
        dietaryPreference: dietaryPreference,
        limit: AppConstants.maxSuggestions,
      );
}

@riverpod
class SuggestionFilterController extends _$SuggestionFilterController {
  @override
  SuggestionFilter build() => const SuggestionFilter();
  // TODO(M5 settings slice): seed `dietaryPreference` from
  // `dietaryPreferenceControllerProvider` (onboarding A-05 / Cài đặt N-01).
  // Deferred so the suggestions test harness can add a SharedPreferences
  // override first.

  void toggleMeal(MealType meal) => state = state.mealType == meal
      ? state.copyWith(clearMealType: true)
      : state.copyWith(mealType: meal);

  void toggleQuickCook() =>
      state = state.copyWith(quickCookOnly: !state.quickCookOnly);

  void togglePreference(DietaryPreference pref) =>
      state = state.dietaryPreference == pref
          ? state.copyWith(clearDietaryPreference: true)
          : state.copyWith(dietaryPreference: pref);
}

/// S-01 list. Re-fetches whenever the filter changes; the server does the
/// `0.4E + 0.3A + 0.2P + 0.1U` scoring.
@riverpod
class SuggestionListController extends _$SuggestionListController {
  @override
  Future<List<DishSuggestion>> build() async {
    final filter = ref.watch(suggestionFilterControllerProvider);
    final res =
        await ref.watch(suggestionRepositoryProvider).fetch(filter.toRequest());
    return res.fold((f) => throw f, (list) => list);
  }

  Future<void> refresh() =>
      ref.refresh(suggestionListControllerProvider.future);
}
