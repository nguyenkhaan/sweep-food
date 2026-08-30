import 'package:freezed_annotation/freezed_annotation.dart';
import 'package:frontend/shared/domain/measurement_unit.dart';
import 'package:frontend/shared/domain/nutrition_info.dart';

part 'ingredient.freezed.dart';

/// A reference ingredient from the catalog (`GET /ingredients?query=`).
/// Used for K-03 autocomplete and to seed a new [PantryItemDraft].
@freezed
abstract class Ingredient with _$Ingredient {
  const factory Ingredient({
    required String id,
    required String name,
    required String category,
    required MeasurementUnit defaultUnit,
    NutritionInfo? nutritionPer100g,

    /// Reference storage guidance when the product has no printed HSD (spec 6.3.2).
    int? referenceShelfLifeDays,
  }) = _Ingredient;
}
