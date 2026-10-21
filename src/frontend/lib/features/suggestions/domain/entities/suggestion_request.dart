import 'package:sweepfood/core/config/app_constants.dart';
import 'package:sweepfood/l10n/app_localizations.dart';
import 'package:sweepfood/shared/domain/dietary_preference.dart';

/// Which meal the user is cooking (S-01 filter).
enum MealType {
  breakfast('breakfast'),
  lunch('lunch'),
  dinner('dinner');

  const MealType(this.wire);
  final String wire;

  String label(AppL10n l10n) => switch (this) {
    MealType.breakfast => l10n.mealTypeBreakfast,
    MealType.lunch => l10n.mealTypeLunch,
    MealType.dinner => l10n.mealTypeDinner,
  };
}

/// One pantry item sent to the AI Recommendation engine (BE RecommendationPantryItemDTO).
class RecommendationPantryItemDraft {
  const RecommendationPantryItemDraft({
    required this.name,
    this.code,
    this.quantityG = 200.0,
    this.hoursToExpire,
    this.isStaple = false,
  });

  final String name;
  final String? code;
  final double quantityG;
  final double? hoursToExpire;
  final bool isStaple;

  Map<String, dynamic> toJson() => {
        'name': name,
        if (code != null) 'code': code,
        'quantity_g': quantityG > 0 ? quantityG : 200.0,
        if (hoursToExpire != null) 'hours_to_expire': hoursToExpire,
        'is_staple': isStaple,
      };
}

/// Body for `POST /recommendations`. Aligned with backend `RecommendationRequestDTO` (AI v2).
class SuggestionRequest {
  const SuggestionRequest({
    this.pantryItems = const [],
    this.request,
    this.prompt,
    this.dietaryPreference,
    this.mealType,
    this.householdSize = 4.0,
    this.scenarioType,
    this.limit = AppConstants.maxSuggestions,
  });

  final List<RecommendationPantryItemDraft> pantryItems;

  /// Optional free-text query (preserved for backwards-compatibility).
  final String? request;

  /// Free-text search/filter prompt typed by the user.
  final String? prompt;

  final DietaryPreference? dietaryPreference;
  final MealType? mealType;
  final double householdSize;
  final String? scenarioType;
  final int limit;

  SuggestionRequest copyWith({
    List<RecommendationPantryItemDraft>? pantryItems,
    String? request,
    String? prompt,
    DietaryPreference? dietaryPreference,
    MealType? mealType,
    double? householdSize,
    String? scenarioType,
    int? limit,
    bool clearRequest = false,
    bool clearPrompt = false,
    bool clearDietaryPreference = false,
    bool clearMealType = false,
  }) {
    return SuggestionRequest(
      pantryItems: pantryItems ?? this.pantryItems,
      request: clearRequest ? null : request ?? this.request,
      prompt: clearPrompt ? null : prompt ?? this.prompt,
      dietaryPreference: clearDietaryPreference
          ? null
          : dietaryPreference ?? this.dietaryPreference,
      mealType: clearMealType ? null : mealType ?? this.mealType,
      householdSize: householdSize ?? this.householdSize,
      scenarioType: scenarioType ?? this.scenarioType,
      limit: limit ?? this.limit,
    );
  }

  /// Builds a payload strictly adhering to Backend `RecommendationRequestDTO`.
  Map<String, dynamic> toBody() {
    final restrictions = <String>[];
    if (dietaryPreference != null) {
      final tag = switch (dietaryPreference!) {
        DietaryPreference.balanced => 'balanced',
        DietaryPreference.moreVeg => 'vegetarian',
        DietaryPreference.highProtein => 'high_protein',
        DietaryPreference.lowCalorie => 'low_calorie',
      };
      restrictions.add(tag);
    }

    final effectiveScenario = scenarioType ??
        (mealType != null ? mealType!.wire : 'custom');

    return {
      'items': pantryItems.map((e) => e.toJson()).toList(),
      'household_size': householdSize > 0 ? householdSize : 4.0,
      'scenario_type': effectiveScenario,
      'dietary_restrictions': restrictions,
      'allergies': <String>[],
      'disliked_ingredients': <String>[],
      'preferred_cuisines': <String>[],
    };
  }

  String buildRequestText() {
    if (request != null && request!.trim().isNotEmpty) {
      final trimmed = request!.trim();
      return trimmed.length > 1000 ? trimmed.substring(0, 1000) : trimmed;
    }
    final parts = <String>[];
    if (prompt != null && prompt!.trim().isNotEmpty) {
      parts.add(prompt!.trim());
    }
    if (mealType != null) {
      parts.add(switch (mealType!) {
        MealType.breakfast => 'Bữa sáng',
        MealType.lunch => 'Bữa trưa',
        MealType.dinner => 'Bữa tối',
      });
    }
    if (dietaryPreference != null) {
      parts.add(switch (dietaryPreference!) {
        DietaryPreference.balanced => 'Cân bằng',
        DietaryPreference.moreVeg => 'Nhiều rau',
        DietaryPreference.highProtein => 'Giàu đạm',
        DietaryPreference.lowCalorie => 'Ít calo',
      });
    }
    if (parts.isEmpty) {
      return 'Gợi ý món ăn hôm nay';
    }
    final combined = parts.join(', ');
    return combined.length > 1000 ? combined.substring(0, 1000) : combined;
  }
}
