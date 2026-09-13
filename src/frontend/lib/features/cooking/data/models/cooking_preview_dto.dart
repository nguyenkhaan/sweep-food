import 'package:freezed_annotation/freezed_annotation.dart';
import 'package:sweepfood/features/cooking/domain/entities/cooking_preview.dart';
import 'package:sweepfood/shared/domain/measurement_unit.dart';

part 'cooking_preview_dto.freezed.dart';
part 'cooking_preview_dto.g.dart';

@freezed
abstract class ProposedDeductionDto with _$ProposedDeductionDto {
  const ProposedDeductionDto._();

  const factory ProposedDeductionDto({
    @JsonKey(name: 'recipe_ingredient_id') required String recipeIngredientId,
    @JsonKey(name: 'batch_id') required String batchId,
    required double quantity,
    required String unit,
    @JsonKey(name: 'master_ingredient_id') String? masterIngredientId,
  }) = _ProposedDeductionDto;

  factory ProposedDeductionDto.fromJson(Map<String, dynamic> json) =>
      _$ProposedDeductionDtoFromJson(json);

  ProposedDeduction toEntity() => ProposedDeduction(
        recipeIngredientId: recipeIngredientId,
        batchId: batchId,
        quantity: quantity,
        unit: MeasurementUnit.fromWire(unit),
        masterIngredientId: masterIngredientId,
      );
}

@freezed
abstract class MissingIngredientPreviewDto with _$MissingIngredientPreviewDto {
  const MissingIngredientPreviewDto._();

  const factory MissingIngredientPreviewDto({
    @JsonKey(name: 'recipe_ingredient_id') required String recipeIngredientId,
    @JsonKey(name: 'ingredient_name') required String ingredientName,
    @JsonKey(name: 'missing_quantity') required double missingQuantity,
    required String unit,
  }) = _MissingIngredientPreviewDto;

  factory MissingIngredientPreviewDto.fromJson(Map<String, dynamic> json) =>
      _$MissingIngredientPreviewDtoFromJson(json);

  MissingIngredientPreview toEntity() => MissingIngredientPreview(
        recipeIngredientId: recipeIngredientId,
        ingredientName: ingredientName,
        missingQuantity: missingQuantity,
        unit: MeasurementUnit.fromWire(unit),
      );
}

/// `POST /cooking/preview` response. See `docs/api-contract.md` §6.
@freezed
abstract class CookingPreviewResponseDto with _$CookingPreviewResponseDto {
  const CookingPreviewResponseDto._();

  const factory CookingPreviewResponseDto({
    @JsonKey(name: 'recipe_id') required String recipeId,
    @JsonKey(name: 'recipe_name') required String recipeName,
    required double servings,
    @JsonKey(name: 'proposed_deductions')
    @Default(<ProposedDeductionDto>[])
    List<ProposedDeductionDto> proposedDeductions,
    @JsonKey(name: 'missing_ingredients')
    @Default(<MissingIngredientPreviewDto>[])
    List<MissingIngredientPreviewDto> missingIngredients,
  }) = _CookingPreviewResponseDto;

  factory CookingPreviewResponseDto.fromJson(Map<String, dynamic> json) =>
      _$CookingPreviewResponseDtoFromJson(json);

  CookingPreview toEntity(String mealPlanItemId) => CookingPreview(
        mealPlanItemId: mealPlanItemId,
        recipeId: recipeId,
        recipeName: recipeName,
        servings: servings,
        proposedDeductions: [
          for (final d in proposedDeductions) d.toEntity(),
        ],
        missingIngredients: [
          for (final m in missingIngredients) m.toEntity(),
        ],
      );
}
