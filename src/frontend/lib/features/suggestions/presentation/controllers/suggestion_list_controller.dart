import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:riverpod_annotation/riverpod_annotation.dart';
import 'package:sweepfood/core/config/app_constants.dart';
import 'package:sweepfood/core/network/network_providers.dart';
import 'package:sweepfood/features/pantry/domain/entities/pantry_item.dart';
import 'package:sweepfood/features/pantry/presentation/controllers/pantry_list_controller.dart';
import 'package:sweepfood/features/suggestions/data/datasources/suggestion_remote_data_source.dart';
import 'package:sweepfood/features/suggestions/data/repositories/suggestion_repository_impl.dart';
import 'package:sweepfood/features/suggestions/domain/entities/dish_suggestion.dart';
import 'package:sweepfood/features/suggestions/domain/entities/suggestion_request.dart';
import 'package:sweepfood/shared/domain/dietary_preference.dart';
import 'package:sweepfood/shared/domain/measurement_unit.dart';

part 'suggestion_list_controller.g.dart';

final aiServiceHealthProvider = FutureProvider.autoDispose(
  (ref) => SuggestionRemoteDataSource(
    ref.watch(apiClientProvider),
  ).health(),
);

/// UI filter state for S-01. Maps to a [SuggestionRequest] for the API.
class SuggestionFilter {
  const SuggestionFilter({
    this.mealType,
    this.dietaryPreference,
    this.prompt = '',
  });

  /// `null` = "Tất cả".
  final MealType? mealType;
  final DietaryPreference? dietaryPreference;
  final String prompt;

  SuggestionFilter copyWith({
    MealType? mealType,
    DietaryPreference? dietaryPreference,
    String? prompt,
    bool clearMealType = false,
    bool clearDietaryPreference = false,
  }) {
    return SuggestionFilter(
      mealType: clearMealType ? null : mealType ?? this.mealType,
      dietaryPreference: clearDietaryPreference
          ? null
          : dietaryPreference ?? this.dietaryPreference,
      prompt: prompt ?? this.prompt,
    );
  }

  SuggestionRequest toRequest({
    List<RecommendationPantryItemDraft> pantryDrafts = const [],
  }) =>
      SuggestionRequest(
        pantryItems: pantryDrafts,
        mealType: mealType,
        dietaryPreference: dietaryPreference,
        prompt: prompt.isNotEmpty ? prompt : null,
        limit: AppConstants.maxSuggestions,
      );
}

@riverpod
class SuggestionFilterController extends _$SuggestionFilterController {
  @override
  SuggestionFilter build() => const SuggestionFilter();

  void setPrompt(String prompt) => state = state.copyWith(prompt: prompt);

  void clearPrompt() => state = state.copyWith(prompt: '');

  void toggleMeal(MealType meal) => state = state.mealType == meal
      ? state.copyWith(clearMealType: true)
      : state.copyWith(mealType: meal);

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
    var drafts = const <RecommendationPantryItemDraft>[];
    try {
      final pantryAsync = ref.watch(pantryListControllerProvider);
      final pantryItems = pantryAsync.asData?.value ?? const <PantryItem>[];
      drafts = pantryItems
          .where((p) => p.status == PantryItemStatus.active)
          .map((p) {
        double? hours;
        if (p.expiryDate != null) {
          hours = p.expiryDate!.difference(DateTime.now()).inHours.toDouble();
        }
        final double qtyG = p.unit == MeasurementUnit.kilogram
            ? p.quantity * 1000.0
            : p.quantity;
        return RecommendationPantryItemDraft(
          name: p.name,
          code: p.ingredientId,
          quantityG: qtyG > 0 ? qtyG : 200.0,
          hoursToExpire: hours,
        );
      }).toList();
    } catch (_) {
      // In tests or isolated scopes where PantryListController is not wired
    }

    final res = await ref
        .watch(suggestionRepositoryProvider)
        .fetch(filter.toRequest(pantryDrafts: drafts));
    return res.fold(
      (f) => throw f,
      (list) {
        final q = filter.prompt.trim().toLowerCase();
        if (q.isEmpty) return list;
        final keywords =
            q.split(RegExp(r'\s+')).where((k) => k.isNotEmpty).toList();
        return list.where((item) {
          final text =
              '${item.dish.name} ${item.dish.cuisine} ${item.nearExpiryIngredients.join(" ")}'
                  .toLowerCase();
          return text.contains(q) || keywords.every((k) => text.contains(k));
        }).toList();
      },
    );
  }

  Future<void> refresh() async {
    ref.invalidateSelf();
    await future;
  }
}
