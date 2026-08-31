import 'package:freezed_annotation/freezed_annotation.dart';
import 'package:frontend/features/dishes/domain/entities/cooking_step.dart';
import 'package:frontend/features/dishes/domain/entities/dish_ingredient.dart';
import 'package:frontend/l10n/app_localizations.dart';
import 'package:frontend/shared/domain/nutrition_info.dart';

part 'dish.freezed.dart';

/// A recipe (`GET /dishes/{id}`, and embedded in a `DishSuggestion`).
///
/// Quantities and nutrition are stored for [servings]; [scaledTo] returns a copy
/// re-scaled for a different serving count (D-01 khẩu phần stepper).
@freezed
abstract class Dish with _$Dish {
  const Dish._();

  const factory Dish({
    required String id,
    required String name,
    required int servings,
    required int prepTimeMin,
    required int cookTimeMin,
    required NutritionInfo nutritionPerServing,
    @Default('') String cuisine,
    @Default('') String difficulty,
    String? imageUrl,
    @Default(<DishIngredient>[]) List<DishIngredient> ingredients,
    @Default(<CookingStep>[]) List<CookingStep> steps,
  }) = _Dish;

  int get totalTimeMin => prepTimeMin + cookTimeMin;

  NutritionInfo get nutritionTotal =>
      nutritionPerServing.scale(servings.toDouble());

  /// Non-seasoning ingredients (the checklist); seasonings render as chips.
  List<DishIngredient> get mainIngredients => [
    for (final i in ingredients)
      if (!i.isSeasoning) i,
  ];

  List<DishIngredient> get seasonings => [
    for (final i in ingredients)
      if (i.isSeasoning) i,
  ];

  int get missingCount =>
      mainIngredients.where((i) => !i.availableInPantry).length;

  int get nearExpiryCount => mainIngredients.where((i) => i.nearExpiry).length;

  /// "15 phút chuẩn bị · Dễ · món trộn" — the detail subtitle.
  String metaLine(AppL10n l10n) {
    final parts = <String>[l10n.dishMetaPrep(prepTimeMin)];
    if (difficulty.isNotEmpty) parts.add(difficulty);
    if (cuisine.isNotEmpty) parts.add(cuisine);
    return parts.join(' · ');
  }

  /// "15 phút · Dễ · 320 kcal / khẩu phần" — the suggestion-card meta.
  String shortMeta(AppL10n l10n) {
    final parts = <String>[l10n.minutesLabel(totalTimeMin)];
    if (difficulty.isNotEmpty) parts.add(difficulty);
    parts.add(
      l10n.dishMetaKcalPerServing(nutritionPerServing.energyKcal.round()),
    );
    return parts.join(' · ');
  }

  /// A copy scaled from the base [servings] to [target] servings.
  Dish scaledTo(int target) {
    if (target <= 0 || target == servings) return this;
    final factor = target / servings;
    return copyWith(
      servings: target,
      ingredients: [
        for (final i in ingredients)
          i.copyWith(
            quantity: i.quantity * factor,
            missingQty: i.missingQty * factor,
          ),
      ],
    );
  }
}
