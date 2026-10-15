import 'package:riverpod_annotation/riverpod_annotation.dart';
import 'package:sweepfood/core/config/app_constants.dart';
import 'package:sweepfood/features/pantry/data/repositories/pantry_repository_impl.dart';
import 'package:sweepfood/features/pantry/domain/entities/pantry_item.dart';
import 'package:sweepfood/features/pantry/domain/repositories/pantry_repository.dart';
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
    this.prompt = '',
  });

  /// `null` = "Tất cả".
  final MealType? mealType;
  final bool quickCookOnly;
  final DietaryPreference? dietaryPreference;
  final String prompt;

  SuggestionFilter copyWith({
    MealType? mealType,
    bool? quickCookOnly,
    DietaryPreference? dietaryPreference,
    String? prompt,
    bool clearMealType = false,
    bool clearDietaryPreference = false,
  }) {
    return SuggestionFilter(
      mealType: clearMealType ? null : mealType ?? this.mealType,
      quickCookOnly: quickCookOnly ?? this.quickCookOnly,
      dietaryPreference: clearDietaryPreference
          ? null
          : dietaryPreference ?? this.dietaryPreference,
      prompt: prompt ?? this.prompt,
    );
  }

  SuggestionRequest toRequest({
    List<PantryItem> pantryItems = const <PantryItem>[],
    DateTime? now,
  }) => SuggestionRequest(
    items: [
      for (final item in pantryItems)
        if (RecommendationPantryItem.fromPantryItem(
              item,
              now: now ?? DateTime.now(),
            )
            case final recommendationItem?)
          recommendationItem,
    ],
    prompt: prompt,
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

  void setPrompt(String prompt) => state = state.copyWith(prompt: prompt);

  void clearPrompt() => state = state.copyWith(prompt: '');

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

/// S-01 list. Re-fetches whenever the filter changes; the server owns ranking.
@riverpod
class SuggestionListController extends _$SuggestionListController {
  @override
  Future<List<DishSuggestion>> build() async {
    final filter = ref.watch(suggestionFilterControllerProvider);
    // Capture watched dependencies before the async gap. Inventory updates
    // can invalidate this provider while the request is still in flight.
    final pantryRepository = ref.watch(pantryRepositoryProvider);
    final suggestionRepository = ref.watch(suggestionRepositoryProvider);
    final pantryResult = await pantryRepository.list(
      status: PantryItemStatus.active,
      sort: PantrySort.priority,
      page: 1,
    );
    final pantryItems = pantryResult.fold(
      (failure) => throw failure,
      (page) => page.items,
    );
    final res = await suggestionRepository.fetch(
      filter.toRequest(pantryItems: pantryItems),
    );
    return res.fold((f) => throw f, (list) {
      final q = filter.prompt.trim().toLowerCase();
      if (q.isEmpty) return list;
      final keywords = q
          .split(RegExp(r'\s+'))
          .where((k) => k.isNotEmpty)
          .toList();
      return list.where((item) {
        final text =
            '${item.dish.name} ${item.dish.cuisine} ${item.nearExpiryIngredients.join(" ")}'
                .toLowerCase();
        return text.contains(q) || keywords.every((k) => text.contains(k));
      }).toList();
    });
  }

  Future<void> refresh() =>
      ref.refresh(suggestionListControllerProvider.future);
}
