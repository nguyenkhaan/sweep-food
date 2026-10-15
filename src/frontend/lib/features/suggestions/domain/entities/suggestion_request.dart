import 'package:sweepfood/core/config/app_constants.dart';
import 'package:sweepfood/features/pantry/domain/entities/pantry_item.dart';
import 'package:sweepfood/l10n/app_localizations.dart';
import 'package:sweepfood/shared/domain/dietary_preference.dart';
import 'package:sweepfood/shared/domain/measurement_unit.dart';

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

/// One pantry row in the recommendation v2 request.
class RecommendationPantryItem {
  const RecommendationPantryItem({
    required this.name,
    required this.quantityG,
    this.code,
    this.hoursToExpire,
    this.isStaple = false,
  });

  final String name;
  final String? code;
  final double quantityG;
  final double? hoursToExpire;
  final bool isStaple;

  /// The AI contract is gram-based. Count and volume units are deliberately
  /// omitted because converting them to grams without ingredient-specific
  /// density/weight data would fabricate inventory quantities.
  static RecommendationPantryItem? fromPantryItem(
    PantryItem item, {
    required DateTime now,
  }) {
    if (!item.unit.isWeight || item.quantity <= 0 || item.name.trim().isEmpty) {
      return null;
    }
    final quantityG = item.unit == MeasurementUnit.kilogram
        ? item.quantity * 1000
        : item.quantity;
    final expiry = item.expiryDate;
    final hoursToExpire = expiry == null
        ? null
        : expiry.difference(now).inMinutes / Duration.minutesPerHour;
    return RecommendationPantryItem(
      name: item.name.trim(),
      code: item.ingredientId,
      quantityG: quantityG,
      hoursToExpire: hoursToExpire,
    );
  }

  Map<String, dynamic> toJson() => {
    'name': name,
    if (code != null && code!.isNotEmpty) 'code': code,
    'quantity_g': quantityG,
    if (hoursToExpire != null) 'hours_to_expire': hoursToExpire,
    'is_staple': isStaple,
  };
}

/// Structured body for the backend/AI recommendation contract v2.
class SuggestionRequest {
  const SuggestionRequest({
    this.items = const <RecommendationPantryItem>[],
    this.householdSize = 4,
    this.request,
    this.prompt,
    this.dietaryPreference,
    this.maxCookTimeMin,
    this.mealType,
    this.scenarioType = 'custom',
    this.dietaryRestrictions = const <String>[],
    this.allergies = const <String>[],
    this.dislikedIngredients = const <String>[],
    this.preferredCuisines = const <String>[],
    this.limit = AppConstants.maxSuggestions,
  });

  final List<RecommendationPantryItem> items;
  final double householdSize;

  /// Legacy/local search inputs. They are intentionally not sent as unknown
  /// keys because the v2 backend request uses `extra="forbid"`.
  final String? request;
  final String? prompt;
  final DietaryPreference? dietaryPreference;
  final int? maxCookTimeMin;
  final MealType? mealType;
  final String scenarioType;
  final List<String> dietaryRestrictions;
  final List<String> allergies;
  final List<String> dislikedIngredients;
  final List<String> preferredCuisines;
  final int limit;

  SuggestionRequest copyWith({
    List<RecommendationPantryItem>? items,
    double? householdSize,
    String? request,
    String? prompt,
    DietaryPreference? dietaryPreference,
    int? maxCookTimeMin,
    MealType? mealType,
    String? scenarioType,
    List<String>? dietaryRestrictions,
    List<String>? allergies,
    List<String>? dislikedIngredients,
    List<String>? preferredCuisines,
    int? limit,
    bool clearRequest = false,
    bool clearPrompt = false,
    bool clearDietaryPreference = false,
    bool clearMaxCookTime = false,
    bool clearMealType = false,
  }) {
    return SuggestionRequest(
      items: items ?? this.items,
      householdSize: householdSize ?? this.householdSize,
      request: clearRequest ? null : request ?? this.request,
      prompt: clearPrompt ? null : prompt ?? this.prompt,
      dietaryPreference: clearDietaryPreference
          ? null
          : dietaryPreference ?? this.dietaryPreference,
      maxCookTimeMin: clearMaxCookTime
          ? null
          : maxCookTimeMin ?? this.maxCookTimeMin,
      mealType: clearMealType ? null : mealType ?? this.mealType,
      scenarioType: scenarioType ?? this.scenarioType,
      dietaryRestrictions: dietaryRestrictions ?? this.dietaryRestrictions,
      allergies: allergies ?? this.allergies,
      dislikedIngredients: dislikedIngredients ?? this.dislikedIngredients,
      preferredCuisines: preferredCuisines ?? this.preferredCuisines,
      limit: limit ?? this.limit,
    );
  }

  Map<String, dynamic> toBody() => {
    'items': [for (final item in items) item.toJson()],
    'household_size': householdSize,
    'max_cooking_time_min': (maxCookTimeMin ?? 45).toDouble(),
    'scenario_type': scenarioType,
    'dietary_restrictions': dietaryRestrictions,
    'allergies': allergies,
    'disliked_ingredients': dislikedIngredients,
    'preferred_cuisines': preferredCuisines,
  };
}
