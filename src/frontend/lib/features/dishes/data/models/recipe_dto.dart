import 'package:freezed_annotation/freezed_annotation.dart';
import 'package:sweepfood/features/dishes/domain/entities/cooking_step.dart';
import 'package:sweepfood/features/dishes/domain/entities/dish.dart';
import 'package:sweepfood/features/dishes/domain/entities/dish_ingredient.dart';
import 'package:sweepfood/shared/domain/measurement_unit.dart';
import 'package:sweepfood/shared/domain/nutrition_info.dart';

part 'recipe_dto.freezed.dart';
part 'recipe_dto.g.dart';

/// Mirrors the backend seeded-recipe contract (`GET /recipes/{id}` — see
/// `src/backend/src/module/recipes`). Maps into the existing [Dish] entity so
/// the Dish detail screen, cooking, and shopping keep speaking one shape.
///
/// The backend has no cuisine / difficulty / prep-vs-cook split and does not
/// cross-reference the user's inventory, so those fields fall back to
/// empty / "not in pantry". `nutrition` arrives scaled to `servings` (a total,
/// not per-serving), so [toEntity] divides it back down.
@freezed
abstract class RecipeDto with _$RecipeDto {
  const RecipeDto._();

  const factory RecipeDto({
    required String id,
    required String name,
    @Default('') String description,
    @JsonKey(name: 'media_url') String? mediaUrl,
    @JsonKey(name: 'default_servings', fromJson: _asDouble) double? defaultServings,
    @JsonKey(name: 'estimated_cooking_minutes')
    @Default(0)
    int estimatedCookingMinutes,
    @JsonKey(name: 'estimated_cost', fromJson: _asDouble) double? estimatedCost,
    // Detail-only fields (absent on the list endpoint).
    @JsonKey(fromJson: _asDouble) double? servings,
    Map<String, dynamic>? instructions,
    RecipeNutritionDto? nutrition,
    @Default(<RecipeIngredientDto>[]) List<RecipeIngredientDto> ingredients,
  }) = _RecipeDto;

  factory RecipeDto.fromJson(Map<String, dynamic> json) =>
      _$RecipeDtoFromJson(json);

  Dish toEntity() {
    final raw = servings ?? defaultServings ?? 1;
    final servingCount = raw < 1 ? 1 : raw.round();
    return Dish(
      id: id,
      name: name,
      servings: servingCount,
      // The backend only reports a single cooking-time estimate.
      prepTimeMin: 0,
      cookTimeMin: estimatedCookingMinutes,
      cuisine: '',
      difficulty: '',
      imageUrl: mediaUrl,
      nutritionPerServing: _perServing(servingCount),
      ingredients: [for (final i in ingredients) i.toDishIngredient()],
      steps: _steps(),
    );
  }

  NutritionInfo _perServing(int servingCount) {
    final n = nutrition;
    if (n == null) return const NutritionInfo.zero();
    final divisor = servingCount <= 0 ? 1 : servingCount;
    return NutritionInfo(
      energyKcal: (n.calories ?? 0) / divisor,
      proteinG: (n.proteinG ?? 0) / divisor,
      carbG: (n.carbsG ?? 0) / divisor,
      lipidG: (n.fatG ?? 0) / divisor,
    );
  }

  List<CookingStep> _steps() {
    final raw = instructions?['steps'];
    if (raw is! List) return const [];
    final out = <CookingStep>[];
    var order = 1;
    for (final step in raw) {
      if (step is String && step.trim().isNotEmpty) {
        out.add(CookingStep(order: order++, text: step.trim()));
      } else if (step is Map && step['text'] is String) {
        out.add(
          CookingStep(
            order: (step['order'] as num?)?.toInt() ?? order++,
            text: (step['text'] as String).trim(),
            durationMin: (step['duration_min'] as num?)?.toInt(),
          ),
        );
      }
    }
    return out;
  }
}

@freezed
abstract class RecipeNutritionDto with _$RecipeNutritionDto {
  const factory RecipeNutritionDto({
    @JsonKey(fromJson: _asDouble) double? calories,
    @JsonKey(name: 'protein_g', fromJson: _asDouble) double? proteinG,
    @JsonKey(name: 'fat_g', fromJson: _asDouble) double? fatG,
    @JsonKey(name: 'carbs_g', fromJson: _asDouble) double? carbsG,
    @JsonKey(name: 'sugar_g', fromJson: _asDouble) double? sugarG,
  }) = _RecipeNutritionDto;

  factory RecipeNutritionDto.fromJson(Map<String, dynamic> json) =>
      _$RecipeNutritionDtoFromJson(json);
}

@freezed
abstract class RecipeIngredientDto with _$RecipeIngredientDto {
  const RecipeIngredientDto._();

  const factory RecipeIngredientDto({
    @JsonKey(name: 'recipe_ingredient_id') String? recipeIngredientId,
    @JsonKey(name: 'master_ingredient_id') String? masterIngredientId,
    @Default('') String name,
    @JsonKey(name: 'required_quantity', fromJson: _asDouble)
    double? requiredQuantity,
    @Default('GRAM') String unit,
    @JsonKey(name: 'is_optional') @Default(false) bool isOptional,
    @JsonKey(name: 'preparation_note') String? preparationNote,
  }) = _RecipeIngredientDto;

  factory RecipeIngredientDto.fromJson(Map<String, dynamic> json) =>
      _$RecipeIngredientDtoFromJson(json);

  /// The backend does not join inventory, so pantry availability is unknown
  /// here — every ingredient renders as "còn thiếu" until the inventory
  /// feature is wired. Optional ingredients render as seasoning chips.
  DishIngredient toDishIngredient() => DishIngredient(
        name: name,
        quantity: requiredQuantity ?? 0,
        unit: MeasurementUnit.fromWire(unit),
        isSeasoning: isOptional,
        availableInPantry: false,
        missingQty: 0,
        nearExpiry: false,
        pantryItemId: null,
      );
}

/// Tolerates numbers that arrive as JSON strings (pydantic `Decimal`).
double? _asDouble(Object? value) {
  if (value == null) return null;
  if (value is num) return value.toDouble();
  return double.tryParse(value.toString());
}
