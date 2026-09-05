import 'package:freezed_annotation/freezed_annotation.dart';
import 'package:sweepfood/shared/domain/measurement_unit.dart';

part 'cooking_preview.freezed.dart';

/// One `proposed_deductions` line from `POST /cooking/preview` — the specific
/// inventory batch the backend would deduct from for one recipe ingredient.
/// Carries no ingredient name (the backend only gives `master_ingredient_id`)
/// — callers resolve a display name by looking up [batchId] in the loaded
/// pantry list.
@freezed
abstract class ProposedDeduction with _$ProposedDeduction {
  const factory ProposedDeduction({
    required String recipeIngredientId,
    required String batchId,
    required double quantity,
    required MeasurementUnit unit,
    String? masterIngredientId,
  }) = _ProposedDeduction;
}

/// One `missing_ingredients` line — nothing in stock matches this recipe
/// ingredient at all.
@freezed
abstract class MissingIngredientPreview with _$MissingIngredientPreview {
  const factory MissingIngredientPreview({
    required String recipeIngredientId,
    required String ingredientName,
    required double missingQuantity,
    required MeasurementUnit unit,
  }) = _MissingIngredientPreview;
}

/// `POST /cooking/preview` result. [mealPlanItemId] is the request's own
/// input, carried here since the backend doesn't echo it back but the next
/// steps (`sessions`, `complete`) need it.
@freezed
abstract class CookingPreview with _$CookingPreview {
  const CookingPreview._();

  const factory CookingPreview({
    required String mealPlanItemId,
    required String recipeId,
    required String recipeName,
    required double servings,
    @Default(<ProposedDeduction>[]) List<ProposedDeduction> proposedDeductions,
    @Default(<MissingIngredientPreview>[])
    List<MissingIngredientPreview> missingIngredients,
  }) = _CookingPreview;

  bool get hasMissingIngredients => missingIngredients.isNotEmpty;
}
