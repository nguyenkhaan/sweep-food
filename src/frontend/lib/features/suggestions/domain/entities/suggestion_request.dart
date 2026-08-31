import 'package:frontend/core/config/app_constants.dart';
import 'package:frontend/l10n/app_localizations.dart';
import 'package:frontend/shared/domain/dietary_preference.dart';

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

/// Body for `POST /suggestions/dishes`. The server scores with
/// `0.4E + 0.3A + 0.2P + 0.1U`; every field is an optional narrowing filter.
class SuggestionRequest {
  const SuggestionRequest({
    this.dietaryPreference,
    this.maxCookTimeMin,
    this.mealType,
    this.limit = AppConstants.maxSuggestions,
  });

  final DietaryPreference? dietaryPreference;
  final int? maxCookTimeMin;
  final MealType? mealType;
  final int limit;

  SuggestionRequest copyWith({
    DietaryPreference? dietaryPreference,
    int? maxCookTimeMin,
    MealType? mealType,
    int? limit,
    bool clearDietaryPreference = false,
    bool clearMaxCookTime = false,
    bool clearMealType = false,
  }) {
    return SuggestionRequest(
      dietaryPreference: clearDietaryPreference
          ? null
          : dietaryPreference ?? this.dietaryPreference,
      maxCookTimeMin: clearMaxCookTime
          ? null
          : maxCookTimeMin ?? this.maxCookTimeMin,
      mealType: clearMealType ? null : mealType ?? this.mealType,
      limit: limit ?? this.limit,
    );
  }

  Map<String, dynamic> toBody() => {
    if (dietaryPreference != null)
      'dietary_preference': dietaryPreference!.wire,
    if (maxCookTimeMin != null) 'max_cook_time': maxCookTimeMin,
    if (mealType != null) 'meal_type': mealType!.wire,
    'limit': limit,
  };
}
