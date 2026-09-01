import 'package:freezed_annotation/freezed_annotation.dart';
import 'package:sweepfood/features/catalog/domain/entities/ingredient.dart';
import 'package:sweepfood/shared/domain/measurement_unit.dart';
import 'package:sweepfood/shared/domain/nutrition_info.dart';

part 'ingredient_dto.freezed.dart';
part 'ingredient_dto.g.dart';

/// Mirrors the backend catalog contract (`GET /ingredients`,
/// `GET /ingredients/{id}` — see `src/backend/src/module/catalog`).
///
/// The list endpoint returns `{id, name, category, default_unit,
/// default_storage_mode, aliases}`; the detail endpoint adds `description`,
/// `nutrition`, and `shelf_life_rules`. Both shapes decode into this one DTO —
/// list items simply leave the detail fields empty.
@freezed
abstract class IngredientDto with _$IngredientDto {
  const IngredientDto._();

  const factory IngredientDto({
    required String id,
    required String name,
    required IngredientCategoryDto category,
    @JsonKey(name: 'default_unit') @Default('GRAM') String defaultUnit,
    @JsonKey(name: 'default_storage_mode') String? defaultStorageMode,
    @Default(<String>[]) List<String> aliases,
    String? description,
    IngredientNutritionDto? nutrition,
    @JsonKey(name: 'shelf_life_rules')
    @Default(<ShelfLifeRuleDto>[]) List<ShelfLifeRuleDto> shelfLifeRules,
  }) = _IngredientDto;

  factory IngredientDto.fromJson(Map<String, dynamic> json) =>
      _$IngredientDtoFromJson(json);

  Ingredient toEntity() => Ingredient(
        id: id,
        name: name,
        category: category.name,
        defaultUnit: MeasurementUnit.fromWire(defaultUnit),
        nutritionPer100g: nutrition?.toEntityOrNull(),
        referenceShelfLifeDays: _flattenedShelfLifeDays(),
      );

  /// The backend models shelf life as one rule per storage mode. The frontend
  /// only needs a single hint, so prefer the rule that matches the ingredient's
  /// default storage mode, else fall back to the first rule.
  int? _flattenedShelfLifeDays() {
    if (shelfLifeRules.isEmpty) return null;
    final match = shelfLifeRules.firstWhere(
      (r) => defaultStorageMode != null && r.storageMode == defaultStorageMode,
      orElse: () => shelfLifeRules.first,
    );
    return match.defaultDays;
  }
}

@freezed
abstract class IngredientCategoryDto with _$IngredientCategoryDto {
  const factory IngredientCategoryDto({
    required String id,
    required String name,
  }) = _IngredientCategoryDto;

  factory IngredientCategoryDto.fromJson(Map<String, dynamic> json) =>
      _$IngredientCategoryDtoFromJson(json);
}

@freezed
abstract class IngredientNutritionDto with _$IngredientNutritionDto {
  const IngredientNutritionDto._();

  const factory IngredientNutritionDto({
    @JsonKey(fromJson: _asDouble) double? calories,
    @JsonKey(name: 'protein_g', fromJson: _asDouble) double? proteinG,
    @JsonKey(name: 'fat_g', fromJson: _asDouble) double? fatG,
    @JsonKey(name: 'carbs_g', fromJson: _asDouble) double? carbsG,
    @JsonKey(name: 'sugar_g', fromJson: _asDouble) double? sugarG,
    @JsonKey(name: 'sodium_mg', fromJson: _asDouble) double? sodiumMg,
  }) = _IngredientNutritionDto;

  factory IngredientNutritionDto.fromJson(Map<String, dynamic> json) =>
      _$IngredientNutritionDtoFromJson(json);

  /// `null` when the catalog carries no macro data. Sugar and sodium are kept on
  /// the DTO for future use but the app-wide [NutritionInfo] only tracks the
  /// four macros.
  NutritionInfo? toEntityOrNull() {
    if (calories == null &&
        proteinG == null &&
        carbsG == null &&
        fatG == null) {
      return null;
    }
    return NutritionInfo(
      energyKcal: calories ?? 0,
      proteinG: proteinG ?? 0,
      carbG: carbsG ?? 0,
      lipidG: fatG ?? 0,
    );
  }
}

@freezed
abstract class ShelfLifeRuleDto with _$ShelfLifeRuleDto {
  const factory ShelfLifeRuleDto({
    String? scope,
    @JsonKey(name: 'storage_mode') String? storageMode,
    @JsonKey(name: 'min_days') int? minDays,
    @JsonKey(name: 'max_days') int? maxDays,
    @JsonKey(name: 'default_days') @Default(0) int defaultDays,
  }) = _ShelfLifeRuleDto;

  factory ShelfLifeRuleDto.fromJson(Map<String, dynamic> json) =>
      _$ShelfLifeRuleDtoFromJson(json);
}

/// Tolerates numbers that arrive as JSON strings (pydantic `Decimal`).
double? _asDouble(Object? value) {
  if (value == null) return null;
  if (value is num) return value.toDouble();
  return double.tryParse(value.toString());
}
